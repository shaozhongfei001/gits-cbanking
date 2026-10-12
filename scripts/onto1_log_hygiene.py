#!/usr/bin/env python3
"""证据日志卫生：干跑 → 白名单 → 备份 → 删除（D-14；Owner 决议 六）

**背景**：`FAIL-2026-09-21-W15TL-16` —— TL 曾因**误读白名单键名**（用 `path`，实为 `file`）
导致白名单未生效、一次性误删 53 件在案证据。本工具把"删除证据"变成**四道闸**的流程：

  1. `--plan`（**干跑**）：只产出删除计划，**不删任何文件**；
  2. **白名单**：`non-gate-log-allowlist.json` 的 `allow[].file` 为受保护键；schema 不符即**报错拒绝**（防再次误读）；
  3. **备份**：`--apply` 必须提供 `--backup-dir`，逐件 `cp` 并校验 sha256 后才删除；
  4. **已登记**：`EVIDENCE.json` 中的 `evidence_file` 一律受保护（REFUSED）。

用法：
  python3 scripts/onto1_log_hygiene.py --plan [--out /tmp/plan.json]
  python3 scripts/onto1_log_hygiene.py --apply /tmp/plan.json --backup-dir /tmp/logbak
  python3 scripts/onto1_log_hygiene.py --gate | --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOOP = ROOT / "loops/ONTO1-ontology-split"
EVID = LOOP / "EVIDENCE.json"
EV_DIR = LOOP / "evidence"
ALLOWLIST = EV_DIR / "non-gate-log-allowlist.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_registered(evidence: Path | None = None) -> set[str]:
    evidence = evidence or EVID
    d = json.loads(evidence.read_text(encoding="utf-8"))
    return {Path(v["evidence_file"]).name for v in d.get("gates", {}).values() if v.get("evidence_file")}


def load_allowlist(path: Path | None = None) -> set[str]:
    """白名单条目结构固定为 {"file": ..., "reason": ...}；**键名不符即拒绝**（D-14 第 2 条）。"""
    path = path or ALLOWLIST
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("allow", data.get("entries", data)) if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError("白名单结构非法：allow 必须是数组")
    bad = [i for i in items if not isinstance(i, dict) or "file" not in i]
    if bad:
        raise ValueError(f"白名单 schema 错误：{len(bad)} 条缺少 `file` 键（禁止按其他键名匹配）")
    return {i["file"] for i in items}


def classify(ev_dir: Path | None = None, evidence: Path | None = None,
             allowlist: Path | None = None) -> list[dict]:
    ev_dir = ev_dir or EV_DIR
    reg, allow = load_registered(evidence), load_allowlist(allowlist)
    out: list[dict] = []
    for p in sorted(ev_dir.glob("*.log")):
        if p.name in reg:
            out.append({"file": p.name, "decision": "REFUSED_REGISTERED", "reason": "EVIDENCE.json 已登记的门禁日志"})
        elif p.name in allow:
            out.append({"file": p.name, "decision": "REFUSED_ALLOWLISTED", "reason": "白名单在案保留（allow[].file）"})
        else:
            out.append({"file": p.name, "decision": "DELETE_CANDIDATE",
                        "reason": "既未登记也不在白名单：确认为一次性调试残留后方可删除",
                        "sha256": sha256(p)})
    return out


def cmd_plan(out: Path | None) -> int:
    rows = classify()
    cand = [r for r in rows if r["decision"] == "DELETE_CANDIDATE"]
    print("# 干跑（未删除任何文件）")
    print(f"# 受保护（登记）={sum(1 for r in rows if r['decision'] == 'REFUSED_REGISTERED')} "
          f"受保护（白名单）={sum(1 for r in rows if r['decision'] == 'REFUSED_ALLOWLISTED')} "
          f"删除候选={len(cand)}")
    for r in cand:
        print(f"  CANDIDATE {r['file']}  sha256={r['sha256'][:16]}")
    plan = {"schema": "ONTO1-LOG-CLEANUP-PLAN/1.0", "dry_run": True, "entries": rows}
    if out:
        out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"# 计划已写入 {out}")
    return 0


def cmd_apply(plan_path: Path, backup: Path | None, evidence: Path | None = None,
              allowlist: Path | None = None, ev_dir: Path | None = None) -> int:
    ev_dir = ev_dir or EV_DIR
    if not plan_path.is_file():
        print("REFUSED: 未提供干跑计划（禁止先删后审）；请先运行 --plan", file=sys.stderr)
        return 2
    if backup is None:
        print("REFUSED: 缺少 --backup-dir（禁止无备份删除）", file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    cand = [e for e in plan["entries"] if e["decision"] == "DELETE_CANDIDATE"]
    protected = [e for e in plan["entries"] if e["decision"].startswith("REFUSED")]
    # 计划里若把受保护件标成候选 ⇒ 拒绝
    reg, allow = load_registered(evidence), load_allowlist(allowlist)
    bad = [e["file"] for e in cand if e["file"] in reg or e["file"] in allow]
    if bad:
        print(f"REFUSED: 计划含受保护文件 {bad}", file=sys.stderr)
        return 2
    backup.mkdir(parents=True, exist_ok=True)
    done = 0
    for e in cand:
        src = ev_dir / e["file"]
        if not src.is_file():
            continue
        dst = backup / e["file"]
        shutil.copy2(src, dst)
        if sha256(src) != sha256(dst):
            print(f"REFUSED: 备份校验失败 {e['file']}", file=sys.stderr)
            return 2
        src.unlink()
        done += 1
    print(f"已删除 {done} 件（全部先备份至 {backup} 并校验 sha256）；受保护跳过 {len(protected)} 件")
    return 0


def cmd_gate() -> int:
    rows = classify()
    cand = [r for r in rows if r["decision"] == "DELETE_CANDIDATE"]
    reg, allow = load_registered(), load_allowlist()
    checks = [
        ("H1 白名单按 `file` 键可读", len(allow) > 0),
        ("H2 无任何已登记文件被标为删除候选", not [r for r in cand if r["file"] in reg]),
        ("H3 无任何白名单文件被标为删除候选", not [r for r in cand if r["file"] in allow]),
        ("H4 白名单在案文件确实存在且白名单非空（QA-W3R2 N-1 修复：原 `or True` 恒真）",
         len(allow) > 0 and all((EV_DIR / f).is_file() for f in allow)),
    ]
    missing = [f for f in allow if not (EV_DIR / f).is_file()]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} [{name}]")
    print(f"  白名单在案 {len(allow)} 件；缺件 {len(missing)}{('：' + str(missing[:3])) if missing else ''}")
    print(f"CANDIDATES={len(cand)}（须经 --plan 干跑 + --backup-dir 才可删除）")
    bad = [n for n, ok in checks if not ok]
    print(f"log-hygiene: {'PASS' if not bad else 'FAIL'}")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ev, al, reg = td / "EVIDENCE.json", td / "allow.json", td / "logs"
        logs = td / "logs"
        logs.mkdir()
        (logs / "registered.log").write_text("r", encoding="utf-8")
        (logs / "allowlisted.log").write_text("a", encoding="utf-8")
        (logs / "stray.log").write_text("s", encoding="utf-8")
        ev.write_text(json.dumps({"gates": {"g": {"evidence_file": "logs/registered.log"}}}), encoding="utf-8")
        al.write_text(json.dumps({"allow": [{"file": "allowlisted.log", "reason": "在案保留"}]}), encoding="utf-8")

        # M1 白名单键名误读（用 path 而非 file）⇒ 必须报错拒绝
        bad_al = td / "allow_bad.json"
        bad_al.write_text(json.dumps({"allow": [{"path": "allowlisted.log", "reason": "键名写错"}]}), encoding="utf-8")
        try:
            load_allowlist(bad_al)
            print("FAIL [M1 白名单键名误读] 未被检出（漏检！）")
            fails += 1
        except ValueError as exc:
            print(f"PASS [M1 白名单键名误读] 被拦下：{str(exc)[:60]}")

        rows = classify(logs, ev, al)
        refus = {r["file"] for r in rows if r["decision"].startswith("REFUSED")}
        cand = {r["file"] for r in rows if r["decision"] == "DELETE_CANDIDATE"}
        ok2 = refus == {"registered.log", "allowlisted.log"} and cand == {"stray.log"}
        print(f"{'PASS' if ok2 else 'FAIL'} [M2 分类正确] REFUSED={sorted(refus)} CANDIDATE={sorted(cand)}")
        fails += 0 if ok2 else 1

        # M3 计划中把受保护件当候选 ⇒ apply 必须拒绝
        bad_plan = td / "bad_plan.json"
        bad_plan.write_text(json.dumps({"entries": [
            {"file": "registered.log", "decision": "DELETE_CANDIDATE"},
            {"file": "stray.log", "decision": "DELETE_CANDIDATE"}]}), encoding="utf-8")
        bak = td / "bak"
        rc = _apply_with(ev, al, logs, bad_plan, bak)
        print(f"{'PASS' if rc == 2 else 'FAIL'} [M3 计划含受保护件] apply 拒绝 = {rc == 2}（exit={rc}）")
        fails += 0 if rc == 2 else 1

        # M4 无备份 ⇒ 拒绝
        good_plan = td / "good_plan.json"
        good_plan.write_text(json.dumps({"entries": [{"file": "stray.log", "decision": "DELETE_CANDIDATE"}]}),
                             encoding="utf-8")
        rc4 = _apply_with(ev, al, logs, good_plan, None)
        print(f"{'PASS' if rc4 == 2 else 'FAIL'} [M4 无 --backup-dir] apply 拒绝 = {rc4 == 2}（exit={rc4}）")
        fails += 0 if rc4 == 2 else 1

        # M5 合规删除：备份哈希一致且文件被删
        orig_stray = sha256(logs / "stray.log")
        bak5 = td / "bak5"
        rc5 = _apply_with(ev, al, logs, good_plan, bak5)
        ok5 = rc5 == 0 and (bak5 / "stray.log").is_file() and not (logs / "stray.log").is_file() \
            and sha256(bak5 / "stray.log") == orig_stray
        print(f"{'PASS' if ok5 else 'FAIL'} [M5 合规删除+备份校验] = {ok5}（exit={rc5}）")
        fails += 0 if ok5 else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{5 - fails}/5）")
    return 0 if fails == 0 else 2


def _apply_with(evidence: Path, allowlist: Path, ev_dir: Path, plan: Path, backup: Path | None) -> int:
    """测试用：显式传参执行 apply（**不**依赖默认参数/全局，避免"读错来源"同族缺陷）。"""
    return cmd_apply(plan, backup, evidence=evidence, allowlist=allowlist, ev_dir=ev_dir)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--apply", default=None)
    ap.add_argument("--backup-dir", default=None)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    if ns.apply:
        return cmd_apply(Path(ns.apply), Path(ns.backup_dir) if ns.backup_dir else None)
    if ns.plan:
        return cmd_plan(Path(ns.out) if ns.out else None)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
