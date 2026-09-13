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
# 放宽为允许**大写与连字符**（2026-09-13，修复 schema 问题 4）。
# 依据（外部执行者实测）：历史 actor 名 `AI-Agent`（P18）被原模式拒绝，
# 唯一的"合法"做法是**把历史执行者改名** —— 那是**改写历史**，
# 与"记录如实"直接冲突。
# 本模式的**目的**是排除占位符/空白/空值，**不是**规范命名风格。
# 故保留"以字母开头、长度 3–64、仅字母数字下划线连字符"，
# 但不再强制小写。
ACTOR_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{2,63}$")
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


MANUAL_PREFIX = "manual:"


def validate_command(command: object, location: str, loop: Path | None = None) -> None:
    if not isinstance(command, str) or not command.strip():
        raise ValueError(f"{location}: non-empty executable command required")
    normalized = command.strip()

    # **人工/文档 gate**（2026-09-13，修复 schema 问题 6）。
    # 依据（外部执行者实测）：GKC 的 `impact_assessment`（产出文档盘点）无命令，
    # 被"non-empty executable command"拒绝，执行者只能填 `manual: ...` ——
    # **而该占位恰好绕过了 `FORBIDDEN_COMMAND_PARTS`，成为一个"看起来合规"的逃生口**。
    #
    # 处置：**把隐式逃生口变成显式受约束形式**。
    # `manual: <相对路径>` 必须指向**该 loop `evidence/` 目录内真实存在**的制品；
    # 若无法校验（如模板检查，无 loop 上下文），则要求路径形态合法。
    if normalized.startswith(MANUAL_PREFIX):
        # **人工 gate 的约束加在"声称"上，不加在文本上**（2026-09-13）。
        #
        # 演进（记录之，因为它是一次"修到根"）：
        #   ① 旧规则：只看非空 ⇒ `manual: <任意描述>` 可长期通过 = 隐式逃生口；
        #   ② 第二版：要求路径 token ⇒ 实测发现这些 manual 命令**根本不是文档，
        #      而是工作项**（"delete port, model, adapters/…"、"verify KERT …"），
        #      且 `evidence/` 是空的 ⇒ **对 pending 的工作项过严**；
        #   ③ 本版：认识到**根因是概念错误** —— `manual:` **不是命令**，
        #      「人工执行的工作」不构成门禁（不可执行、不可复现、无法自动核验）。
        #
        # 故：**文本不限形态**（pending 的工作项本就该写清要做什么），
        #     但**该 gate 永远不得声称 `pass`** —— 由 `validate_evidence` 强制。
        # 后果（正是我们想要的）：只要存在人工 gate，
        # `all_pass` 就永不为真 ⇒ `ready_for_independent_qa`/`qa_pass`/`closed` **不可达**。
        # **你不能执行它，就不能用它关闭 loop。**
        if not normalized[len(MANUAL_PREFIX):].strip():
            raise ValueError(f"{location}: manual gate must describe the work item")
        return

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
    _manual_gate_ids: list[str] = []
    for gate in gates:
        gate_id = gate["id"]
        if str(gate.get("command", "")).strip().startswith(MANUAL_PREFIX):
            _manual_gate_ids.append(gate_id)
        validate_command(gate.get("command"), f"gate {gate_id}", loop=loop)
        row = evidence["gates"][gate_id]
        if row.get("command") != gate["command"]:
            raise ValueError(f"{gate_id}: evidence command differs from LOOP")
        status = row.get("status")
        if status not in ALLOWED_EVIDENCE:
            raise ValueError(f"{gate_id}: invalid evidence status {status}")
        all_pass = all_pass and status == "pass"
        if status == "pass":
            # **反向/负例 gate**（2026-09-13，修复 schema 问题 1）。
            # 依据（外部执行者实测）：GKB 的 `repro_baseline` gate 的
            # `pass_condition` 是"复现 4 errors" —— 即**期望命令 exit≠0**；
            # 而原 schema 规定 `pass ⟺ exit_code=0` ⇒
            # **红测无法表达，只能记 fail** ⇒ 进而 `ready_for_independent_qa`
            # （要求全 pass）**永远无法成立**，本可 QA 就绪的 loop 被迫降级。
            #
            # 故允许显式声明 `expected_exit_code`（正整数，缺省 0）。
            #
            # **防滥用（重要）**：该字段可被用来把"失败"洗成"通过"。
            # 缓解办法是**可见性**而非隐藏：任何非零 `expected_exit_code`
            # 都会在门禁输出中**显式打印**，使读者必然看到该 gate 的
            # 通过条件是"命令失败"。**残余风险如实登记**：
            # 若有人滥用此字段，唯一能发现的是读输出的人的审视 ——
            # 本仓的纪律是"不隐藏"，不是"不可能滥用"。
            expected = row.get("expected_exit_code", 0)
            if not isinstance(expected, int) or expected < 0:
                raise ValueError(
                    f"{gate_id}: expected_exit_code must be a non-negative integer")
            if row.get("exit_code") != expected:
                if expected == 0:
                    raise ValueError(f"{gate_id}: pass requires exit_code=0")
                raise ValueError(
                    f"{gate_id}: pass requires exit_code={expected}"
                    f"（反向 gate），实际 {row.get('exit_code')}")
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
            # **人工 gate 永远不得声称 `pass`**（2026-09-13，修复 schema 问题 6 的**根**）。
            #
            # 演进过程（值得记录，因为它是一次"修到根"）：
            #   第一版：允许 `manual: <描述>` —— 因为旧规则只看非空。
            #   第二版：要求 `<路径 token>` 且真实存在 —— 但实测发现
            #     GKC/P38 的 manual 命令**根本不是文档，而是工作项**
            #     （"delete port, model, adapters/…"、"set migration_status=…"、
            #      "verify KERT endpoint is callable"），
            #     而且它们的 `evidence/` 目录**是空的**。
            #   第三版（本版）：认识到**根因是概念错误** ——
            #     **`manual:` 不是命令。** 「人工执行的工作」不构成"门禁"，
            #     因为它**不可执行、不可复现、无法自动化核验**。
            #
            # 故规则简化为：**`manual:` gate 的状态只能是 `pending`/`blocked`/`fail`。**
            # **你不能执行它，就不能声称它通过了。**
            # 若该工作确实完成，正确做法有二：
            #   ① 改为**可执行检查**（如 `! grep -r OracleSourcePort …`）；或
            #   ② 走 `independent_qa` block 的独立证据（即由他人核验）。
            cmd = str(gate.get("command", "")).strip()
            if cmd.startswith(MANUAL_PREFIX):
                raise ValueError(
                    f"{gate_id}: **人工 gate 不得声称 pass** —— `manual:` 不是命令。"
                    f"请改为可执行检查，或将该工作登记为 pending/blocked 并走独立 QA 证据。"
                    f"（原命令：{cmd[:80]}）")
    # **可见性**：任何"通过条件是命令失败"的 gate 必须被打印出来。
    # 这是 `expected_exit_code` 唯一的防滥用机制 —— 不靠隐藏，靠**必然被看到**。
    reverse_gates = [
        f"{gid}(expected_exit_code={evidence['gates'][gid].get('expected_exit_code')})"
        for gid in evidence.get("gates", {})
        if evidence["gates"][gid].get("expected_exit_code")
        not in (None, 0)
    ]
    manual_gates = sorted(_manual_gate_ids)
    if manual_gates:
        print(f"  [MANUAL-GATE] **{len(manual_gates)} 个 gate 为人工工作项**"
              f"（不可执行 ⇒ 不得声称 pass ⇒ **阻碍 loop 关闭**）：{manual_gates}")
    if reverse_gates:
        print(f"  [REVERSE-GATE] **{len(reverse_gates)} 个 gate 的通过条件是『命令失败』**"
              f"（负例/红测）：{reverse_gates}")
        print("  [REVERSE-GATE] 请核对其 pass_condition 与证据输出确实构成负例验证，"
              "而非把失败记为通过。")

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
