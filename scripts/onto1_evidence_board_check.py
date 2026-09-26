#!/usr/bin/env python3
"""ONTO1｜证据板一致性门禁（固化 G-1 盲区）。

背景（本轮真实踩到）：4 组检查（8 个门禁名）**执行过并留下 17 份日志**，但从未登记进
`EVIDENCE.json` ⇒ `loop-guard` 只比对 `LOOP.yaml.gates` ↔ `EVIDENCE.json.gates` **两个集合**，
看不见集合外的日志，于是板面显示"15/15 全绿"，而其中一组实为 **FAIL**。

本门禁补上"集合外"这一维：
    E1 目录/文件齐备（fail-closed：缺 `evidence/` 或缺 `EVIDENCE.json` 即失败）
    E2 **孤儿检查**：`evidence/*.log` 中形如门禁日志者（前缀 `wi_`/`contract_`/`security_`/`index_`）
       必须要么是某个已登记门禁的 `evidence_file`，要么在**非门禁日志白名单**中列出（带理由）
    E3 反向检查：每个已登记门禁的 `evidence_file` 必须真实存在
    E4 白名单自身不得只剩空壳（有白名单文件就必须有 `reason`；缺文件则视为"无白名单"，此时
       任何孤儿一律 FAIL —— 缺夹具即失败）
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "loops/ONTO1-ontology-split"
EVIDENCE_DIR = LOOP / "evidence"
EVIDENCE_JSON = LOOP / "EVIDENCE.json"
ALLOWLIST = EVIDENCE_DIR / "non-gate-log-allowlist.json"
GATE_LOG_RE = re.compile(r"^(wi_|contract_|security_|index_)")


def load_state() -> dict:
    if not EVIDENCE_JSON.is_file():
        raise RuntimeError(f"EVIDENCE.json missing: {EVIDENCE_JSON}")
    return json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))


def load_allowlist(path: Path = ALLOWLIST) -> dict[str, str]:
    """返回 {文件名或 glob: 理由}；文件不存在 ⇒ 空表（此时孤儿一律 FAIL）。"""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("allow")
    if not isinstance(entries, list):
        raise RuntimeError("allowlist must contain an 'allow' array")
    out: dict[str, str] = {}
    for item in entries:
        name, reason = item.get("file"), item.get("reason")
        if not name or not reason:
            raise RuntimeError(f"allowlist entry lacks file/reason: {item}")
        out[name] = reason
    return out


def allowlisted(name: str, allow: dict[str, str]) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(name, pattern) for pattern in allow)


def check(evidence_dir: Path = EVIDENCE_DIR, evidence_json: Path = EVIDENCE_JSON,
          allowlist_path: Path = ALLOWLIST) -> list[str]:
    failures: list[str] = []
    if not evidence_dir.is_dir():
        return [f"E1 evidence dir missing: {evidence_dir}"]
    if not evidence_json.is_file():
        return [f"E1 EVIDENCE.json missing: {evidence_json}"]
    state = json.loads(evidence_json.read_text(encoding="utf-8"))
    registered = {Path(v["evidence_file"]).name for v in state.get("gates", {}).values()
                  if v.get("evidence_file")}
    allow = load_allowlist(allowlist_path)
    if allowlist_path.is_file() and not allow and evidence_dir == EVIDENCE_DIR:
        failures.append("E4 allowlist file exists but contains no entry")

    logs = sorted(p.name for p in evidence_dir.glob("*.log"))
    # **FIX-2026-09-21（QA 第三轮 U-6）**：原先 `gate_like` 只认**文件名前缀**（`wi_`/`contract_` 等），
    # 因此 `a3fix-after-*.log`、`wave0-readiness-*.log`、`review-submission-zip-dryrun-*.log` 这类
    # **已执行但命名不含前缀**的证据日志**对 E2 不可见** ⇒ 理论上可藏一个 FAIL 而不被发现。
    # 现改为：**evidence/ 下所有 `*.log` 一律纳入**（未登记且未白名单即 FAIL）。
    # 代价是每新增一个非门禁日志都必须显式登记或白名单（可见的逃生口）——这正是本门禁的目的。
    gate_like = logs

    orphans = [name for name in gate_like
               if name not in registered and not allowlisted(name, allow)]
    for name in orphans:
        failures.append(f"E2 orphan evidence log (executed but unregistered): {name}")

    for name in sorted(registered):
        if not (evidence_dir / name).is_file():
            failures.append(f"E3 registered evidence file missing: {name}")

    # **FIX-2026-09-21（QA 第三轮 U-7）**：白名单是"逃生口"，**通配**不得覆盖已登记的证据文件——
    # 否则 E2 的统计会自相矛盾（实测曾出现 31+25−1 的重叠），且会掩盖"证据被白名单吞掉"。
    # **收窄理由（TL 复核）**：E5 只对**含通配符**的条目生效。**精确名**条目与"当前登记文件"重合
    # 是**重记自检型门禁时的必然瞬态**（旧日志在记录更新前仍是登记证据；若不允许白名单覆盖，
    # E2 与 E5 将同时不可满足 ⇒ 门禁无法重记）。精确名是无歧义的显式声明，不构成"吞掉"。
    for name in sorted(registered):
        if any(allowlisted(name, {pat: ""}) and any(ch in pat for ch in "*?[")
               for pat in allow):
            failures.append(f"E5 allowlist glob swallows registered evidence file: {name}")

    print(f"[E1] evidence dir ok; gates={len(state.get('gates', {}))}")
    print(f"[E2] evidence logs={len(gate_like)} registered={len(registered & set(gate_like))} "
          f"allowlisted={len([n for n in gate_like if allowlisted(n, allow)])} orphan={len(orphans)}")
    print(f"[E3] registered evidence files present="
          f"{len([n for n in registered if (evidence_dir / n).is_file()])}/{len(registered)}")
    return failures


def gate() -> int:
    try:
        failures = check()
    except RuntimeError as exc:
        print(f"onto1-evidence-board: FAIL: {exc}", file=sys.stderr)
        return 2
    if failures:
        for item in failures:
            print(f"onto1-evidence-board: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-evidence-board: PASS")
    return 0


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="onto1-evidence-board-selftest-"))
    failures: list[str] = []
    try:
        ev = tmp / "evidence"
        ev.mkdir(parents=True)
        state = {"gates": {"g1": {"evidence_file": "loops/ONTO1-ontology-split/evidence/wi_g1-1.log"}}}
        (tmp / "EVIDENCE.json").write_text(json.dumps(state), encoding="utf-8")
        (ev / "wi_g1-1.log").write_text("ok\n", encoding="utf-8")

        ok0 = check(ev, tmp / "EVIDENCE.json") == []
        print(f"{'PASS' if ok0 else 'FAIL'}  M0 对照：无孤儿 ⇒ PASS")
        if not ok0:
            failures.append("M0")

        (ev / "wi_ghost-1.log").write_text("executed but never registered\n", encoding="utf-8")
        problems = check(ev, tmp / "EVIDENCE.json")
        ok1 = any("E2" in item and "wi_ghost-1.log" in item for item in problems)
        print(f"{'PASS' if ok1 else 'FAIL'}  M1 注入未登记门禁日志 ⇒ 被拦下  {problems[:1]}")
        if not ok1:
            failures.append("M1")

        (ev / "wi_g1-1.log").unlink()
        problems = check(ev, tmp / "EVIDENCE.json")
        ok2 = any("E3" in item for item in problems)
        print(f"{'PASS' if ok2 else 'FAIL'}  M2 删除已登记证据文件 ⇒ 被拦下  {problems[:1]}")
        if not ok2:
            failures.append("M2")

        # ---- M4 **前缀制盲区回归**（QA 第三轮 U-6）----
        # 注入一个**命名不含门禁前缀**的已执行日志；旧逻辑（`GATE_LOG_RE` 前缀制）看不见它，
        # 现逻辑（全部 `*.log`）必须拦下。同时断言旧正则确实匹配不到该名 —— 证明本用例有区分度。
        (ev / "wi_g1-1.log").write_text("ok\n", encoding="utf-8")
        (ev / "a3fix-after-x.log").write_text("executed, unprefixed name\n", encoding="utf-8")
        legacy_blind = GATE_LOG_RE.match("a3fix-after-x.log") is None
        problems = check(ev, tmp / "EVIDENCE.json")
        ok4 = legacy_blind and any("E2" in item and "a3fix-after-x.log" in item for item in problems)
        print(f"{'PASS' if ok4 else 'FAIL'}  M4 无前缀的已执行日志 ⇒ 必须被 E2 拦下"
              f"（旧前缀逻辑不可见={legacy_blind}）  {problems[:1]}")
        if not ok4:
            failures.append("M4")
        (ev / "a3fix-after-x.log").unlink()

        # ---- M5 **白名单通配不得吞掉已登记证据**（QA 第三轮 U-7）----
        bad_allow = tmp / "bad-allowlist.json"
        bad_allow.write_text(json.dumps({"allow": [
            {"file": "wi_g1-*.log", "reason": "夹具：故意用**通配**覆盖已登记证据文件"}]},
            ensure_ascii=False), encoding="utf-8")
        problems = check(ev, tmp / "EVIDENCE.json", bad_allow)
        ok5 = any("E5" in item and "wi_g1-1.log" in item for item in problems)
        print(f"{'PASS' if ok5 else 'FAIL'}  M5 白名单**通配**覆盖已登记证据文件 ⇒ E5 必须 FAIL  {problems[:1]}")
        if not ok5:
            failures.append("M5")

        # ---- M5b **反例的边界**：精确名条目与登记文件重合属"重记自检型门禁的必然瞬态"，**不得**判 E5 ----
        exact_allow = tmp / "exact-allowlist.json"
        exact_allow.write_text(json.dumps({"allow": [
            {"file": "wi_g1-1.log", "reason": "夹具：精确名（重记瞬态，应被容忍）"}]},
            ensure_ascii=False), encoding="utf-8")
        problems = check(ev, tmp / "EVIDENCE.json", exact_allow)
        ok5b = not any("E5" in item for item in problems)
        print(f"{'PASS' if ok5b else 'FAIL'}  M5b 精确名与登记文件重合 ⇒ 容忍（否则重记无法进行）  {problems[:1]}")
        if not ok5b:
            failures.append("M5b")

        code = gate()
        print(f"{'PASS' if code == 0 else 'FAIL'}  M3 对照：真实 Loop ⇒ PASS  exit={code}")
        if code != 0:
            failures.append("M3")

        if failures:
            print(f"onto1-evidence-board-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-evidence-board-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return gate()


if __name__ == "__main__":
    raise SystemExit(main())
