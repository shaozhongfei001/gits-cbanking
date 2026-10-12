#!/usr/bin/env python3
"""ONTO1｜复审包完整性门禁。

存在两个真实风险，本门禁各堵一个：

    R1「包内容被静默改动」：01~12 是提交给委员会的**已定稿证据**。若有人改了其中任何一份
       又顺手更新 MANIFEST 哈希，门禁会"自证清白"地通过 ⇒ 委员会拿到的结论建立在漂移证据上。
       对策：把 V1.0 的 12 份哈希**硬编码为冻结值**，任何改动一律 FAIL（须显式走"重发快照 +
       重算哈希 + 在 MANIFEST 记版本沿革"的流程，不允许静默）。
    R2「缺可签署载体」：复审轮若缺少 13（送审函）/ 14（决议签署页），委员会**无法出具结论**
       （旧送审包两件已随 RETURN_TO_HLD 归档且裁定项已被推翻）⇒ 门禁 FAIL 并指明。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package"

# V1.0 冻结值（2026-09-20 核对：12/12 与 MANIFEST 逐字一致）
FROZEN_01_12 = {
    "01-主设计-V2.0-复审快照.md": "d2c16784182517e0dde48222a4c3abbd9ab0cdd2b3ea5d9afcdfeff5381de908",
    "02-整改处置报告-V2.0.md": "3a25af6f5dc9c79679546995aa3a4e9ef3e0080b7de53e2a9a44d4097db0f70c",
    "03-逐术语权威矩阵-22字段.csv": "6ace07b87e693a7eccb15a0ff7c7d9ae2547856567e77d0e22b4e195dc2a5ff3",
    "04-基线32项映射表.md": "c4f00811701216acf4bbe15a598f7c18c7be006b92391729675d18aad3e6d505",
    "05-六列权威与发布依赖表.md": "eb751a2d514f2411f3fc638e1a858cca8b5b73cfad4622229e89226c0c9211bc",
    "06-验证状态模型与状态跃迁表.md": "00808bcb40c0d134c0889da8010b6a3711044a55b20d0c35bafe8d170c61d2e5",
    "07-兼容性矩阵-major-minor-patch.md": "808efbe76f4e5eb6155f57de42d724e67475cc0c796847600811ff553b869de0",
    "08-CQ语义验收矩阵.md": "ff7faac5a17c9bbd4098531442cdfc4a9e096d5871d8ab6e00798fd9349cc4ef",
    "09-消费者影响清单-状态修正版.md": "a2afdbc6fd8daf21d0d3968ea16918da5d4b4a48142ce79cb3040eba5ed2a0ed",
    "10-国标参照对齐与批准范围说明.md": "68eeaa1b775a39dde621d85dfb11314e1ad5402a422624186ecd1798992cc879",
    "11-外部依赖登记表.md": "580dab650c4beafa8abca7a8d68bfba1afeaa52c2bd8e46f4caa89e6c40e441f",
    "12-证据账本.md": "f284e9fd082faaefa9a4ada8a54f2f78784fa70d96fe43b58b60bc6da6560bbf",
}
# 复审轮必须具备的"可签署载体"
REQUIRED_SUBMISSION_FILES = ["13-送审函-书面复审.md", "14-书面复审决议签署页.md"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(text: str) -> dict[str, str]:
    rows = re.findall(r"\|\s*`([0-9A-Za-z\u4e00-\u9fff\-\._]+)`\s*\|[^|]*\|[^|]*\|\s*`([0-9a-f]{64})`", text)
    return {name: digest for name, digest in rows}


def gate() -> int:
    failures: list[str] = []
    if not PACKAGE.is_dir():
        print(f"onto1-review-package: FAIL: package dir missing: {PACKAGE}", file=sys.stderr)
        return 2

    # R1 冻结校验
    for name, expected in FROZEN_01_12.items():
        path = PACKAGE / name
        if not path.is_file():
            failures.append(f"R1 frozen file missing: {name}")
            continue
        got = sha256(path)
        if got != expected:
            failures.append(f"R1 frozen file DRIFTED: {name} ({got[:16]} != {expected[:16]})")
    print(f"[R1] frozen 01~12 一致 {len(FROZEN_01_12) - len([f for f in failures if f.startswith('R1 frozen file')])}"
          f"/{len(FROZEN_01_12)}")

    # R2 可签署载体
    for name in REQUIRED_SUBMISSION_FILES:
        if not (PACKAGE / name).is_file():
            failures.append(f"R2 missing signable carrier: {name}")
    print(f"[R2] signable carriers {[n for n in REQUIRED_SUBMISSION_FILES if (PACKAGE / n).is_file()]}")

    # R3 MANIFEST 自洽（登记项存在且哈希一致）
    manifest_path = PACKAGE / "MANIFEST.md"
    if not manifest_path.is_file():
        failures.append("R3 MANIFEST.md missing")
    else:
        registered = parse_manifest(manifest_path.read_text(encoding="utf-8"))
        if len(registered) < 14:
            failures.append(f"R3 MANIFEST registers only {len(registered)} files (expect >= 14)")
        for name, digest in registered.items():
            path = PACKAGE / name
            if not path.is_file():
                failures.append(f"R3 manifest entry has no file: {name}")
            elif sha256(path) != digest:
                failures.append(f"R3 manifest hash mismatch: {name}")
        print(f"[R3] MANIFEST 登记 {len(registered)} 件；自洽校验完毕")

    if failures:
        for item in failures:
            print(f"onto1-review-package: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-review-package: PASS")
    return 0


def selftest() -> int:
    import shutil
    import tempfile
    original = PACKAGE
    tmp_root = Path(tempfile.mkdtemp(prefix="onto1-pkg-selftest-"))
    failures: list[str] = []
    try:
        globals()["PACKAGE"] = tmp_root / "pkg"
        shutil.copytree(original, PACKAGE)

        # M1 改动 01 ⇒ R1 必须 FAIL
        target = PACKAGE / "01-主设计-V2.0-复审快照.md"
        target.write_text(target.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
        code = gate()
        ok1 = code == 2
        print(f"{'PASS' if ok1 else 'FAIL'}  M1 静默改动 01 ⇒ 门禁 FAIL  exit={code}")
        if not ok1:
            failures.append("M1")

        # 恢复后再测 M2：删除 14 ⇒ R2 必须 FAIL
        globals()["PACKAGE"] = tmp_root / "pkg2"
        shutil.copytree(original, PACKAGE)
        (PACKAGE / "14-书面复审决议签署页.md").unlink()
        code = gate()
        ok2 = code == 2
        print(f"{'PASS' if ok2 else 'FAIL'}  M2 删除决议签署页 ⇒ 门禁 FAIL  exit={code}")
        if not ok2:
            failures.append("M2")

        # M0 对照
        globals()["PACKAGE"] = tmp_root / "pkg3"
        shutil.copytree(original, PACKAGE)
        code = gate()
        print(f"{'PASS' if code == 0 else 'FAIL'}  M0 对照：原样包 ⇒ PASS  exit={code}")
        if code != 0:
            failures.append("M0")

        if failures:
            print(f"onto1-review-package-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-review-package-selftest: PASS")
        return 0
    finally:
        globals()["PACKAGE"] = original
        shutil.rmtree(tmp_root, ignore_errors=True)


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
