#!/usr/bin/env python3
"""ONTO1｜TL 审计仪器：把「审核任务完成度」做成可复算的动作（AU-1 / AU-5 自动化）。

设计约束（安全）：
- **本脚本不执行 handoff 里声明的任何命令**。门禁复跑（AU-2）由 TL 人工审阅命令文本后手工执行——
  文件内容不得触发命令执行。
- 只做三件客观事：
    AU-1 交付物存在性 + sha256 校验（从 handoff 中解析 `<路径> @ <哈希前 8~64>` 形态）
    AU-5 红线扫描（写域外文件改动、KERT 仓改动）
    AU-6b 证据板一致性（调用 onto1_evidence_board_check）
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = ROOT.parent / "Leibniz-KERT"
LOOP = ROOT / "loops/ONTO1-ontology-split"
EVIDENCE_DIR = LOOP / "evidence"
HANDOFF_DIR = LOOP / "memory/handoffs"
GATES_JSON = LOOP / "EVIDENCE.json"

# 每个 PKG 的允许写域（glob）；SCOPE 之外的改动 ⇒ AU-5 报告（不自动判死，交 TL 裁决）
SCOPES: dict[str, list[str]] = {
    "PKG-A1": ["scripts/onto1_obligation_triage.py",
               "loops/ONTO1-ontology-split/evidence/obligation-*",
               "loops/ONTO1-ontology-split/evidence/PKG-A1-*",
               "loops/ONTO1-ontology-split/memory/waves/PKG-A1-*",
               "loops/ONTO1-ontology-split/memory/handoffs/PKG-A1-*"],
    "PKG-A2": ["scripts/onto1_wave0_readiness.py",
               "loops/ONTO1-ontology-split/evidence/wave0-readiness-*",
               "loops/ONTO1-ontology-split/evidence/PKG-A2-*",
               "loops/ONTO1-ontology-split/memory/waves/PKG-A2-*",
               "loops/ONTO1-ontology-split/memory/handoffs/PKG-A2-*"],
    "PKG-A3": ["scripts/onto1_namespace_collision_check.py",
               "scripts/onto1_reference_alignment_check.py",
               "loops/ONTO1-ontology-split/evidence/a3fix-*",
               "loops/ONTO1-ontology-split/evidence/PKG-A3-*",
               "loops/ONTO1-ontology-split/memory/waves/PKG-A3-*",
               "loops/ONTO1-ontology-split/memory/handoffs/PKG-A3-*"],
    "AUDIT": ["loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W15-*"],
}
# 红线：任何 PKG 都不得改（TL 单写者 + 受控制品）
TL_ONLY = ["loops/ONTO1-ontology-split/LOOP.yaml",
           "loops/ONTO1-ontology-split/EVIDENCE.json",
           "loops/ONTO1-ontology-split/EVIDENCE.md",
           "loops/ONTO1-ontology-split/STATE.json",
           "loops/ONTO1-ontology-split/FAILURES.md",
           "loops/ONTO1-ontology-split/memory/ROLE_BOARD.yaml",
           "loops/ONTO1-ontology-split/memory/NEXT_SESSION.md",
           "loops/ONTO1-ontology-split/memory/ORCHESTRATOR.md",
           "loops/ONTO1-ontology-split/memory/PLAN-NEXT.md",
           "loops/ONTO1-ontology-split/memory/INDEX_BASIS.md",
           "loops/ONTO1-ontology-split/memory/TL-DECISIONS-*",
           "loops/ONTO1-ontology-split/memory/DISPATCH-*",
           "loops/ONTO1-ontology-split/memory/W-1.5-ORCHESTRATION.md",
           "specs/*", "generated/*", "docs/dd/*"]
HASH_RE = re.compile(r"([\w\u4e00-\u9fff\-./]+\.(?:md|csv|json|py|jsonl))\s*@\s*`?([0-9a-f]{8,64})`?")
# 表格形态（PKG-A2/A1 等 handoff 常用）：| 1 | `path` | `hash` | ... |
TABLE_HASH_RE = re.compile(
    r"\|\s*\d+\s*\|\s*`([\w\u4e00-\u9fff\-./]+\.(?:md|csv|json|py|jsonl))`\s*\|\s*`([0-9a-f]{8,64})`\s*\|")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _match_any(path: str, patterns: list[str]) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def audit_handoff(pkg: str) -> list[str]:
    """AU-1：解析 handoff 中声明的交付物并校验存在性 + 哈希前缀。"""
    failures: list[str] = []
    candidates = sorted(HANDOFF_DIR.glob(f"{pkg}-HANDOFF.md")) or sorted(
        HANDOFF_DIR.glob(f"{pkg}*.md"))
    if not candidates:
        return [f"AU-1 handoff not found for {pkg} (looked for {pkg}-HANDOFF.md)"]
    handoff = candidates[0]
    text = handoff.read_text(encoding="utf-8")
    declared = HASH_RE.findall(text) or TABLE_HASH_RE.findall(text)
    if not declared:
        failures.append(f"AU-1 no hash declaration found in {handoff.name} "
                        f"（接受 `path @ hash` 或表格形态）⇒ 无法校验完成度（fail-closed）")
    seen = set()
    for raw_path, prefix in declared:
        if (raw_path, prefix) in seen:
            continue
        seen.add((raw_path, prefix))
        path = ROOT / raw_path
        if not path.is_file():
            failures.append(f"AU-1 declared artifact missing: {raw_path}")
            continue
        digest = sha256(path)
        if not digest.startswith(prefix.lower()):
            failures.append(f"AU-1 hash mismatch: {raw_path} actual={digest[:16]} declared={prefix}")

    # 写域检查（AU-5a）
    scope = SCOPES.get(pkg)
    if scope:
        for raw_path, _ in seen:
            if _match_any(raw_path, TL_ONLY):
                failures.append(f"AU-5 RED LINE: {pkg} wrote TL-only path: {raw_path}")
            elif not _match_any(raw_path, scope + TL_ONLY):
                failures.append(f"AU-5 out-of-scope artifact: {raw_path} (not in {pkg} write scope)")
    print(f"[AU-1] {pkg}: handoff={handoff.name} declared={len(seen)} "
          f"failures={len([f for f in failures if f.startswith('AU-1')])}")
    return failures


def redlines() -> list[str]:
    """AU-5：红线扫描 —— 受控制品与 KERT 仓是否被动。"""
    failures: list[str] = []
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                            capture_output=True, text=True, check=False).stdout
    touched = []
    for line in status.splitlines():
        parts = line[3:].strip().strip('"')
        if _match_any(parts, ["specs/*", "generated/*", "docs/dd/*", "**/specs/*", "**/generated/*"]):
            touched.append(parts)
    if touched:
        failures.append(f"AU-5 RED LINE: controlled artifacts touched: {touched[:5]}")
    if KERT.is_dir():
        kert_status = subprocess.run(["git", "status", "--porcelain"], cwd=KERT,
                                     capture_output=True, text=True, check=False).stdout
        recent = [l for l in kert_status.splitlines() if "ONTO" in l or "ONTOLOGY-SPLIT" in l]
        if recent:
            failures.append(f"AU-5 KERT writes related to ONTO1: {recent[:5]}")
    print(f"[AU-5] controlled/LERT redlines: {len(failures)} finding(s)")
    return failures


def board() -> list[str]:
    """AU-6b：证据板一致性（委派给既有门禁，避免重复实现）。"""
    result = subprocess.run([sys.executable, str(ROOT / "scripts/onto1_evidence_board_check.py"), "--gate"],
                            cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return [f"AU-6b evidence board inconsistency (exit={result.returncode}): "
                f"{result.stderr.strip().splitlines()[:2]}"]
    print("[AU-6b] evidence board: PASS")
    return []


# AU-1b：Loop 记录里的「声明哈希」vs 实测（F-2 类别；原 AU-1 会漏过）
DECLARED_HASH_RE = re.compile(
    r"`([^`\s]+\.(?:md|csv|json|jsonl|ttl|yaml|yml|txt|log|py|xml|sh))`"
    r"[^|\n]*?`?(?:sha256\s*)?([0-9a-f]{16})(?:[0-9a-f]{48})?`?")
RECORD_FILES = ["EVIDENCE.md", "EVIDENCE.json", "memory/INDEX_BASIS.md"]


def declared_hashes() -> list[str]:
    """解析 Loop 记录中声明的 `<文件名>` + 哈希，逐条比对实测。"""
    findings: list[str] = []
    info: list[tuple[str, str]] = []
    checked = 0
    for record in RECORD_FILES:
        path = LOOP / record
        if not path.is_file():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for name, prefix in DECLARED_HASH_RE.findall(line):
                digest = prefix.lower()
                candidate = None
                for base in (LOOP.parent.parent / name, EVIDENCE_DIR / name, LOOP / name,
                             ROOT / name):
                    if base.is_file():
                        candidate = base
                        break
                if candidate is None:
                    info.append((f"{record}:{lineno}", f"declared {name} not resolvable"))
                    continue
                checked += 1
                actual = sha256(candidate)
                if not actual.startswith(digest):
                    findings.append(
                        f"AU-1b declared hash mismatch: {record}:{lineno} declares {name}="
                        f"{digest} but actual={actual[:16]}")
    print(f"[AU-1b] declared-hash checks={checked} mismatch={len(findings)} "
          f"unresolvable={len(info)}")
    for where, note in info:
        print(f"        (info) {where}: {note}")
    return findings


def recent_changes(minutes: int) -> list[str]:
    """AU-5 兜底：loop 目录整体未跟踪 ⇒ git 看不见内部改动；用 mtime 列出近期被改文件。"""
    import datetime as dt
    cutoff = dt.datetime.now().timestamp() - minutes * 60
    touched: list[str] = []
    for base in (LOOP, ROOT / "scripts"):
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.stat().st_mtime >= cutoff and (
                    base == LOOP or path.name.startswith("onto1_")):
                touched.append(str(path.relative_to(ROOT)))
    print(f"[AU-5m] files modified in last {minutes} min: {len(touched)}")
    for item in sorted(touched)[:25]:
        print(f"        {item}")
    return []


def list_scopes() -> int:
    for pkg, patterns in SCOPES.items():
        print(f"{pkg}:")
        for pattern in patterns:
            print(f"  allow  {pattern}")
        print("  deny   " + ", ".join(TL_ONLY[:6]) + " ...")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pkg", choices=sorted(SCOPES) + ["ALL"], default=None)
    parser.add_argument("--redlines", action="store_true")
    parser.add_argument("--board", action="store_true")
    parser.add_argument("--declared", action="store_true",
                        help="AU-1b：比对 Loop 记录中声明的哈希与实测（F-2 类别）")
    parser.add_argument("--recent", type=int, default=None, metavar="MINUTES",
                        help="AU-5m：列出近 N 分钟内被改动的 loop/脚本文件（loop 目录未跟踪）")
    parser.add_argument("--list-scopes", action="store_true")
    args = parser.parse_args()

    if args.list_scopes:
        return list_scopes()

    failures: list[str] = []
    if args.redlines or args.pkg == "ALL":
        failures += redlines()
    if args.board or args.pkg == "ALL":
        failures += board()
    if args.declared or args.pkg == "ALL":
        failures += declared_hashes()
    if args.recent:
        recent_changes(args.recent)
    if args.pkg and args.pkg != "ALL":
        failures += audit_handoff(args.pkg)

    if failures:
        for item in failures:
            print(f"onto1-pkg-audit: FINDING: {item}", file=sys.stderr)
        print("onto1-pkg-audit: NOT_ACCEPTED（见上）", file=sys.stderr)
        return 2
    print("onto1-pkg-audit: ACCEPTED（自动部分；AU-2/AU-3/AU-4 仍需 TL 手工执行）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
