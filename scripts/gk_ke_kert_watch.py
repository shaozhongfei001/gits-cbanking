#!/usr/bin/env python3
"""GK-KE：KERT 回函与进度被动监控（只读）。

背景：函件 GK-KE-KERT-LETTER-001 已发出（受控文档留档），但对方无回执通道。
本脚本提供**被动轮询**：只读比对 KERT 侧四个可观测信号，发现变化即报告。

**核心纪律**：
  1. 只读，**不写入 KERT 仓**
  2. **"无变化"不等于"未在处理"** —— 对方可能在内部分析或在独立分支工作
  3. **"沉默"不等于"同意"** —— 无回函则 REPORT-ASSEMBLE 的 callable 保持 false
  4. 不把本脚本的结论当作 KERT 的进度声明

信号：
  - KERT HEAD 提交
  - 未提交改动计数（U-D 重命名推进指标）
  - R-3 涉及文件（skills.py）的 sha256 与 hash 变化
  - 回函/回复类文件是否出现

用法：
  python3 scripts/gk_ke_kert_watch.py                 # 与基线比对
  python3 scripts/gk_ke_kert_watch.py --snapshot      # 记录当前为新基线
  python3 scripts/gk_ke_kert_watch.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")
SNAPSHOT = ROOT / "loops" / "GK14-l4-0-capability-closure" / "kert-watch-baseline.json"

# R-3 涉及文件（决定 REPORT-ASSEMBLE 能否转 callable）
R3_FILES = [
    "src/kert/application/skills.py",
]
# 回函可能的落点（只读探测）
LETTER_PATHS = [
    "docs/inbox",
    "docs/architecture",
]


def run(cmd: list[str], cwd: Path) -> str:
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                             timeout=30, check=False)
        return out.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"__ERROR__ {exc}"


def file_hash(p: Path) -> str | None:
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect() -> dict:
    if not KERT.is_dir():
        return {"available": False, "reason": f"KERT 路径不存在: {KERT}"}

    head = run(["git", "log", "-1", "--format=%H"], KERT)
    head_msg = run(["git", "log", "-1", "--format=%s"], KERT)
    changed = run(["git", "status", "--porcelain"], KERT)
    changed_count = len([l for l in changed.splitlines() if l.strip()])

    # U-D 指标：src/dkws 是否仍处于未提交删除状态
    dkws_deleted_uncommitted = any(
        l.strip().startswith("D") and "src/dkws" in l for l in changed.splitlines())

    r3 = {}
    for rel in R3_FILES:
        p = KERT / rel
        r3[rel] = {
            "exists": p.is_file(),
            "sha256": file_hash(p),
            "mtime": (datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                      .isoformat() if p.is_file() else None),
        }

    # 回函探测
    replies = []
    for rel in LETTER_PATHS:
        d = KERT / rel
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file() and any(
                        k in f.name.lower() for k in ("gk-ke", "回函", "letter", "inbox")):
                    replies.append(str(f.relative_to(KERT)))

    return {
        "available": True,
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "kertHead": head,
        "kertHeadSubject": head_msg,
        "uncommittedChangeCount": changed_count,
        "dkwsRenameStillUncommitted": dkws_deleted_uncommitted,
        "r3Files": r3,
        "replyFiles": sorted(replies),
    }


def load_snapshot() -> dict:
    if SNAPSHOT.is_file():
        return json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return {}


def diff(prev: dict, cur: dict) -> list[str]:
    changes: list[str] = []
    if not prev:
        return ["（无基线，首次观测）"]
    if prev.get("kertHead") != cur.get("kertHead"):
        changes.append(f"KERT HEAD 变化: {prev.get('kertHead','')[:8]} → "
                       f"{cur.get('kertHead','')[:8]}")
    pc = prev.get("uncommittedChangeCount")
    cc = cur.get("uncommittedChangeCount")
    if pc != cc:
        changes.append(f"未提交改动数变化: {pc} → {cc}")
    if prev.get("dkwsRenameStillUncommitted") and not cur.get("dkwsRenameStillUncommitted"):
        changes.append("U-D 进展：src/dkws 未提交删除状态已消失（可能已提交）")
    for rel, info in cur.get("r3Files", {}).items():
        prev_hash = (prev.get("r3Files", {}).get(rel) or {}).get("sha256")
        if prev_hash != info.get("sha256"):
            changes.append(f"R-3 涉及文件变化: {rel}")
    new_replies = set(cur.get("replyFiles", [])) - set(prev.get("replyFiles", []))
    if new_replies:
        changes.append(f"**发现疑似回函文件**: {sorted(new_replies)}")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true", help="记录当前为基线")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cur = collect()
    prev = load_snapshot()

    if not cur.get("available"):
        print(f"gk-ke-kert-watch: UNAVAILABLE — {cur.get('reason')}", file=sys.stderr)
        return 1

    changes = diff(prev, cur)

    if args.snapshot:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print(f"gk-ke-kert-watch: 基线已记录 → {SNAPSHOT.relative_to(ROOT)}")

    if args.json:
        print(json.dumps({"current": cur, "changes": changes},
                         ensure_ascii=False, indent=2))
    else:
        print("gk-ke-kert-watch: 只读观测")
        print(f"  KERT HEAD: {cur['kertHead'][:12]} ({cur['kertHeadSubject'][:40]})")
        print(f"  未提交改动: {cur['uncommittedChangeCount']} 项")
        print(f"  U-D 重命名仍未提交: {cur['dkwsRenameStillUncommitted']}")
        for rel, info in cur["r3Files"].items():
            print(f"  {rel}: {(info['sha256'] or 'MISSING')[:16]}... "
                  f"(mtime {info['mtime']})")
        print(f"  疑似回函文件: {cur['replyFiles'] or '无'}")
        print()
        if changes:
            print("  变化:")
            for c in changes:
                print(f"    - {c}")
        else:
            print("  变化: 无")
        print()
        print("  纪律提醒:")
        print("    - 『无变化』不等于『未在处理』：对方可能在内部分析或独立分支工作")
        print("    - 『沉默』不等于『同意』：无回函则 REPORT-ASSEMBLE 的 callable 保持 false")
        print("    - 本脚本结论不构成 KERT 的进度声明")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
