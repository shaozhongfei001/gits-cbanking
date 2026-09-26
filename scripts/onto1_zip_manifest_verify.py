#!/usr/bin/env python3
"""ONTO1｜送审包「发出的包 == 受检的包」可执行证明。

问题：委员会拿到的是 **zip**，而项目侧冻结的是**仓内文件哈希**。若中间有人重打包、改文件、
或 zip 与仓内不一致，"受检对象"就与"冻结对象"脱钩，而双方都不会察觉。

本脚本把两者绑死：
    读 MANIFEST 登记的 (文件名 → sha256)
    读 zip 内每个条目的实际内容哈希
    逐项比对：缺件 / 多件 / 哈希不符 ⇒ FAIL

用法：
    python3 scripts/onto1_zip_manifest_verify.py --zip <path/to/pkg.zip>
    python3 scripts/onto1_zip_manifest_verify.py --dryrun     # 在 /tmp 造包 + 自证（含变异复验）

`--dryrun` 会额外做一次**变异复验**：复制 zip、篡改其中一个成员，要求验证器判 FAIL
（证明"该证明有牙齿"，而不是恒真）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package"
MANIFEST = PKG_DIR / "MANIFEST.md"


def parse_manifest_names() -> set[str]:
    """从 MANIFEST 中提取被登记的文件名（形如 `NN-名称.md` / `MANIFEST.md`）。"""
    import re
    text = MANIFEST.read_text(encoding="utf-8")
    names = set(re.findall(r"\|\s*`([0-9A-Za-z\u4e00-\u9fff\-\._]+)`\s*\|", text))
    names.add("MANIFEST.md")
    return {n for n in names if n.endswith((".md", ".csv", ".json"))}


def expected_hashes() -> dict[str, str]:
    """期望哈希以**仓内文件**为准（MANIFEST 只是登记面，实体在仓库里）。"""
    out: dict[str, str] = {}
    for name in parse_manifest_names():
        path = PKG_DIR / name
        if path.is_file():
            out[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def verify_zip(zip_path: Path) -> list[str]:
    failures: list[str] = []
    if not zip_path.is_file():
        return [f"zip missing: {zip_path}"]
    expected = expected_hashes()
    if not expected:
        return ["no expected files resolved from repo (fail-closed)"]

    seen: dict[str, str] = {}
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            base = Path(info.filename).name
            seen[base] = hashlib.sha256(archive.read(info)).hexdigest()

    missing = sorted(set(expected) - set(seen))
    extra = sorted(set(seen) - set(expected))
    mismatch = sorted(name for name in set(expected) & set(seen) if expected[name] != seen[name])
    for name in missing:
        failures.append(f"missing in zip: {name}")
    for name in extra:
        failures.append(f"unexpected extra member in zip: {name}")
    for name in mismatch:
        failures.append(f"hash mismatch: {name} (zip={seen[name][:16]} repo={expected[name][:16]})")

    print(f"[V] zip members={len(seen)} repo expected={len(expected)} "
          f"missing={len(missing)} extra={len(extra)} mismatch={len(mismatch)}")
    return failures


def build_dryrun_zip(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    subprocess.run(
        ["zip", "-r", "-X", "-q", str(target), PKG_DIR.name, "-x", "*.DS_Store"],
        cwd=str(PKG_DIR.parent), check=True,
    )
    return target


def dryrun() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="onto1-submit-verify-"))
    failures: list[str] = []
    try:
        good = build_dryrun_zip(tmp / "submit.zip")
        problems = verify_zip(good)
        print(f"{'PASS' if not problems else 'FAIL'}  M0 对照：预演包对仓内文件逐件一致  {problems[:2]}")
        if problems:
            failures.append("M0")

        # 变异：篡改一个成员内容，验证器必须判 FAIL
        bad = tmp / "submit-tampered.zip"
        with zipfile.ZipFile(good) as src, zipfile.ZipFile(bad, "w") as dst:
            for info in src.infolist():
                data = src.read(info)
                if info.filename.endswith("13-送审函-书面复审.md"):
                    data += "\n<!-- tampered -->\n".encode("utf-8")
                dst.writestr(info, data)
        problems = verify_zip(bad)
        ok = any("hash mismatch" in item for item in problems)
        print(f"{'PASS' if ok else 'FAIL'}  M1 篡改包内成员 ⇒ 必须被判 FAIL  {problems[:2]}")
        if not ok:
            failures.append("M1")

        if failures:
            print(f"onto1-zip-manifest-verify: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-zip-manifest-verify: PASS（预演包与仓内冻结件逐件一致；篡改可被检出）")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", default=None)
    parser.add_argument("--dryrun", action="store_true")
    args = parser.parse_args()
    if args.dryrun:
        return dryrun()
    if not args.zip:
        parser.error("either --zip or --dryrun is required")
    failures = verify_zip(Path(args.zip))
    if failures:
        for item in failures:
            print(f"onto1-zip-manifest-verify: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-zip-manifest-verify: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
