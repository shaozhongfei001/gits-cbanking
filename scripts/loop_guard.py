#!/usr/bin/env python3
"""Strict validation for Loop state, Baton and cryptographic gate evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ACTOR_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_STATES = {"planned", "in_progress", "blocked", "ready_for_independent_qa", "qa_pass", "closed"}
# `inconclusive` 于 2026-09-13 加入（终结 T-08）。
# 依据：本仓判据体系已确立「**INCONCLUSIVE ≠ 通过**」为核心纪律
# （见 GK-KE-语义级消费验证方案-V1.2.1.md 与 GK16 的注入测试门禁）；
# 而 loop 协议原先只有 {pending, pass, fail, blocked}，**无该态**，
# 迫使使用者用 `blocked` 或 `fail` 代替 —— **两者都丢失「未产生结论」的语义**。
# 实测受迫场景：`gate-injection-tests` 与 `capability-probe` 均判 INCONCLUSIVE，
# 只能有损映射为 `blocked`（GK16 的 EVIDENCE.json 中曾显式标注该有损）。
ALLOWED_EVIDENCE = {"pending", "pass", "fail", "blocked", "inconclusive"}
FORBIDDEN_COMMANDS = {"true", ":", "exit 0"}
FORBIDDEN_COMMAND_PARTS = ("Replace with", "TODO", "TEMPLATE", "echo ", "printf ")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON/YAML-JSON {path}: {exc}") from exc


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_command(command: object, location: str) -> None:
    if not isinstance(command, str) or not command.strip():
        raise ValueError(f"{location}: non-empty executable command required")
    normalized = command.strip()
    if normalized in FORBIDDEN_COMMANDS or any(token in normalized for token in FORBIDDEN_COMMAND_PARTS):
        raise ValueError(f"{location}: dummy command prohibited: {command}")


def reject_placeholders(loop: Path) -> None:
    bad = []
    for path in loop.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "{{" in text or "TEMPLATE-" in text or "Replace with" in text:
            bad.append(path.relative_to(ROOT).as_posix())
    if bad:
        raise ValueError(f"unresolved placeholders: {bad}")


def validate_memory(loop: Path, state: dict) -> None:
    required = [
        loop / "SHARED_MEMORY.md",
        loop / "memory/PROTOCOL.md",
        loop / "memory/ROLE_BOARD.yaml",
        loop / "memory/NEXT_SESSION.md",
        loop / "memory/ORCHESTRATOR.md",
    ]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"missing shared memory files: {missing}")
    board = load_json(loop / "memory/ROLE_BOARD.yaml")
    holder = board.get("baton", {}).get("holder")
    if not isinstance(holder, str) or not ACTOR_PATTERN.fullmatch(holder):
        raise ValueError("ROLE_BOARD baton.holder is absent or invalid")
    next_text = (loop / "memory/NEXT_SESSION.md").read_text(encoding="utf-8")
    match = re.search(r"\| \*\*holder\*\* \| `([^`]+)` \|", next_text)
    if not match or match.group(1) != holder:
        raise ValueError("NEXT_SESSION holder and ROLE_BOARD baton.holder disagree")
    if state.get("status") in {"ready_for_independent_qa", "qa_pass", "closed"}:
        if holder not in {"independent_qa", "owner_review"} and holder != state.get("qa_actor"):
            raise ValueError("review state requires an independent QA or owner-review Baton holder")
    elif state.get("implementation_actor") != holder:
        raise ValueError("STATE implementation_actor and Baton holder disagree")


def validate_evidence(loop: Path, loop_spec: dict, state: dict) -> None:
    evidence = load_json(loop / "EVIDENCE.json")
    gates = loop_spec.get("gates")
    if not isinstance(gates, list) or not gates:
        raise ValueError("LOOP gates must be a non-empty array")
    gate_ids = [gate.get("id") for gate in gates]
    if None in gate_ids or len(gate_ids) != len(set(gate_ids)):
        raise ValueError("LOOP gate IDs are missing or duplicated")
    if set(gate_ids) != set(evidence.get("gates", {})):
        raise ValueError("EVIDENCE gate set must exactly match LOOP gates")
    all_pass = True
    for gate in gates:
        gate_id = gate["id"]
        validate_command(gate.get("command"), f"gate {gate_id}")
        row = evidence["gates"][gate_id]
        if row.get("command") != gate["command"]:
            raise ValueError(f"{gate_id}: evidence command differs from LOOP")
        status = row.get("status")
        if status not in ALLOWED_EVIDENCE:
            raise ValueError(f"{gate_id}: invalid evidence status {status}")
        all_pass = all_pass and status == "pass"
        if status == "pass":
            if row.get("exit_code") != 0:
                raise ValueError(f"{gate_id}: pass requires exit_code=0")
            if not row.get("actor") or not row.get("actor_role") or not row.get("executed_at"):
                raise ValueError(f"{gate_id}: pass requires actor, role and timestamp")
            evidence_file = row.get("evidence_file")
            if not isinstance(evidence_file, str):
                raise ValueError(f"{gate_id}: evidence file required")
            evidence_path = ROOT / evidence_file
            try:
                evidence_path.relative_to(loop / "evidence")
            except ValueError as exc:
                raise ValueError(f"{gate_id}: evidence must be inside the loop evidence directory") from exc
            if not evidence_path.is_file() or row.get("output_sha256") != file_hash(evidence_path):
                raise ValueError(f"{gate_id}: evidence file missing or hash mismatch")
    if state.get("status") in {"ready_for_independent_qa", "qa_pass", "closed"} and not all_pass:
        raise ValueError(f"state {state['status']} requires all implementation gates to pass")
    qa = evidence.get("independent_qa", {})
    if state.get("status") in {"qa_pass", "closed"}:
        if qa.get("status") != "pass" or qa.get("actor") == state.get("implementation_actor") or not qa.get("session"):
            raise ValueError("qa_pass requires a distinct independent QA actor and session")
        qa_file = ROOT / str(qa.get("evidence_file"))
        if not qa_file.is_file() or qa.get("evidence_sha256") != file_hash(qa_file):
            raise ValueError("independent QA evidence file is missing or its hash differs")


def validate_loop(loop_id: str, memory_only: bool, evidence_only: bool) -> None:
    loop = ROOT / "loops" / loop_id
    if not loop.is_dir() or loop.name == "_template":
        raise ValueError(f"loop not found: {loop_id}")
    reject_placeholders(loop)
    required = [loop / name for name in ("LOOP.yaml", "STATE.json", "EVIDENCE.json", "EVIDENCE.md", "FAILURES.md", "HANDOFF.md")]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"missing loop files: {missing}")
    state = load_json(loop / "STATE.json")
    if state.get("loop_id") != loop_id or state.get("status") not in ALLOWED_STATES:
        raise ValueError("STATE loop_id or status is invalid")
    baseline = state.get("baseline_commit")
    if baseline == "PENDING_FIRST_COMMIT" and state["status"] != "planned":
        raise ValueError("PENDING_FIRST_COMMIT is allowed only while planned")
    if baseline != "PENDING_FIRST_COMMIT" and (not isinstance(baseline, str) or not SHA_PATTERN.fullmatch(baseline)):
        raise ValueError("baseline_commit must be a full Git SHA")
    loop_spec = load_json(loop / "LOOP.yaml")
    if loop_spec.get("loop_id") != loop_id:
        raise ValueError("LOOP loop_id mismatch")
    if not evidence_only:
        validate_memory(loop, state)
    if not memory_only:
        validate_evidence(loop, loop_spec, state)


def check_instances_ratchet() -> int:
    """**实例合规棘轮**（终结 T-06）。

    问题：`--template-check` **只验模板、从不验实例**；实测 58 个实例中
    **30 个不合规**（历史欠账），而门禁全绿 —— 门禁名 `loop-guard`
    会让读者以为它在守 loop。

    **为何不直接对全部实例判 FAIL**：那 30 个是**已完成的历史工作**，
    一次性改判会阻断整个门禁链，且**不改变任何事实**。

    **棘轮策略**（工程上闭合该缺口的正确做法）：
      · 基线 `loops/_instance_baseline.json` **冻结**已知不合规实例；
      · **不在基线中的实例必须合规** —— 否则 FAIL（**新违规立即拦截**）；
      · 基线中的实例若已转为合规 → 报告进展；
      · 基线中的实例**已消失** → 报告陈旧条目；
      · **基线条目数不得增长** —— 任何新增都必须走正常修复，不得塞进基线。

    > **豁免 ≠ 放过**：历史欠账被**计数、列名、冻结**，
    > 新增违规无处可藏。这才是"如实登记"与"实际闭合"的区别。
    """
    baseline_path = ROOT / "loops" / "_instance_baseline.json"
    loops = sorted(p for p in (ROOT / "loops").iterdir()
                   if p.is_dir() and p.name != "_template")
    bad: list[str] = []
    for lp in loops:
        try:
            validate_loop(lp.name, memory_only=False, evidence_only=False)
        except (OSError, ValueError, json.JSONDecodeError):
            bad.append(lp.name)
    names = {lp.name for lp in loops}

    if not baseline_path.is_file():
        print(f"loop-guard: FAIL: 实例基线缺失 {baseline_path}", file=sys.stderr)
        return 2
    baseline = load_json(baseline_path)
    known = set(baseline.get("knownNonCompliant", []))

    new_violations = sorted(set(bad) - known)
    improved = sorted(known - set(bad) - (known - names))
    vanished = sorted(known - names)

    print(f"  [RATCHET] loop 实例 {len(loops)} 个：合规 {len(loops) - len(bad)}，"
          f"不合规 {len(bad)}（其中 **{len(set(bad) & known)} 个为基线冻结**）")
    if improved:
        print(f"  [RATCHET] 已由不合规转为合规 {len(improved)} 个：{improved}")
    if vanished:
        print(f"  [RATCHET] 基线中的陈旧条目（实例已不存在）{len(vanished)} 个：{vanished}")

    if new_violations:
        print(f"loop-guard: FAIL: **{len(new_violations)} 个新增不合规实例**"
              f"（不在基线中 ⇒ 不得豁免）：", file=sys.stderr)
        for n in new_violations:
            print(f"  - {n}", file=sys.stderr)
        print("  **新增/改动的 loop 实例必须合规；历史欠账冻结在基线中，不得新增。**",
              file=sys.stderr)
        return 2
    print(f"  [RATCHET] **无新增违规**；基线冻结 {len(known)} 条历史欠账。")
    return 0


def report_instance_compliance() -> None:
    """如实报告：`--template-check` **只验模板，不验任何实例**。

    依据（2026-09-13 反角色攻击命中 T-06）：
    我新建 GK16 loop 后，`loop_guard.py --loop GK16-trust-hardening` **连续 7 次 FAIL**
    （占位符未解析 / baseline 非完整 SHA / holder 不一致 / EVIDENCE gate 集合不匹配 /
    evidence 缺 status、exit_code、actor、actor_role、executed_at、evidence_file、output_sha256），
    **而门禁链全绿** —— 因为门禁跑的是 `--template-check`，它**从不校验实例**。
    → **门禁名 `loop-guard` 会让读者以为它在守 loop；实际它只守模板。**

    **本函数只增加可见性，不改变判定**：把 58 个实例的合规数与不合规清单**打印出来**，
    使该缺口**不可隐藏**。
    **是否把不合规实例改判为 FAIL，属纪律变更，不由本脚本单方面决定。**
    """
    loops = sorted(p for p in (ROOT / "loops").iterdir()
                   if p.is_dir() and p.name != "_template")
    bad: list[str] = []
    for lp in loops:
        try:
            validate_loop(lp.name, memory_only=False, evidence_only=False)
        except (OSError, ValueError, json.JSONDecodeError):
            bad.append(lp.name)
    print(f"  [SCOPE] 本次**只校验模板**（loops/_template），"
          f"**未校验任何实例**。")
    print(f"  [INFO] loop 实例合规：{len(loops) - len(bad)}/{len(loops)} 通过"
          f"（{len(bad)} 个不合规 —— 历史欠账，**本门禁不判定它们**）")
    if bad:
        print(f"  [INFO] 不合规实例（前 10）：{bad[:10]}")


def validate_template() -> None:
    template = ROOT / "loops/_template"
    required_tokens = {"{{LOOP_ID}}", "{{HOLDER}}", "{{BASELINE_COMMIT}}", "{{ISO_TIME}}"}
    all_text = "\n".join(path.read_text(encoding="utf-8") for path in template.rglob("*") if path.is_file())
    missing = sorted(token for token in required_tokens if token not in all_text)
    if missing:
        raise ValueError(f"template missing required tokens: {missing}")
    loop_spec = load_json(template / "LOOP.yaml")
    for gate in loop_spec.get("gates", []):
        validate_command(gate.get("command"), f"template gate {gate.get('id')}")
    evidence = load_json(template / "EVIDENCE.json")
    if set(evidence.get("gates", {})) != {gate["id"] for gate in loop_spec["gates"]}:
        raise ValueError("template LOOP and EVIDENCE gates disagree")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-check", action="store_true")
    parser.add_argument("--instances-check", action="store_true")
    parser.add_argument("--loop")
    parser.add_argument("--memory-only", action="store_true")
    parser.add_argument("--evidence-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.instances_check:
            return check_instances_ratchet()
        if args.template_check:
            validate_template()
            report_instance_compliance()
        elif args.loop:
            validate_loop(args.loop, args.memory_only, args.evidence_only)
        else:
            raise ValueError("--template-check or --loop is required")
        print("loop-guard: PASS")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"loop-guard: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
