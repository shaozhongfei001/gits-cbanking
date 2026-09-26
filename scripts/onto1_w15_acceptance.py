#!/usr/bin/env python3
"""ONTO1 W-1.5｜T-4 验收仪器（A3 复交后的四个反例 + 一个对照）。

背景：PKG-A3 的两处门禁脚本存在**已实证的缺口**（见 `FAILURES.md`）——
`W15A3-02` 必需钉值 allow-list 只查"声明"不查"**文件存在**"；
`W15A3-03` 缺受控钉值**文件**时抛 `KeyError` 崩溃（非 fail-closed）；
`W15A3-04`（QA Q-1）`rule_statement` 放行被**含主题词的真实标准对齐声称**利用；
R-1（QA Q-4）`section_heading_negation` 用**子串**匹配，标题含"禁"即放行其下全部声称。

本仪器把上述四类反例 + 一个对照**固化为可复算用例**，供 TL 在 A3 复交后一键复验。
**仪器只写临时目录**（`tempfile.mkdtemp`），绝不改动被检仓库。

用法：
    python3 scripts/onto1_w15_acceptance.py            # 全部用例（默认）
    python3 scripts/onto1_w15_acceptance.py --only c4  # 只跑 C-4 组
    python3 scripts/onto1_w15_acceptance.py --only d3  # 只跑 D-3 组

退出码：0 = 全部用例符合预期；2 = 有用例不符（**未修复的缺口会被如实报为 NG，不是本仪器故障**）。
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
COLLISION = ROOT / "scripts/onto1_namespace_collision_check.py"
REFALIGN = ROOT / "scripts/onto1_reference_alignment_check.py"

# 沙箱内必须复制的真实制品（碰撞检查的输入面）
COLLISION_SOURCES = (
    "specs/semantic",
    "specs/CONTRACT_INDEX.yaml",
    "specs/knowledge-architecture/instances/product/products.ttl",
    "specs/data/customer-source-mapping.r2rml.ttl",
    "loops/ONTO1-ontology-split",
)
CONTROLLED_PIN = "specs/semantic/gits-core.owl.ttl"
UNCONTROLLED_PIN = "loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv"

# D-3 组：真实标准对齐声称（QA 第二轮 X2/X3）与标题语境（QA X4/X5）
#
# **书写约束（重要，`FAIL-2026-09-20-W15TL-08`）**：本文件会被参照对齐守卫扫描，而
# "符合" + 空格 + "GB/T" 属**声称构造**（`CLAIM_CONSTRUCTION_RE`）⇒ 逐字写出该句会让
# **本仪器自身**变成违规源。故此处**在运行期拼接**，源码内不出现可匹配的连续形态；
# 夹具文本只写入临时目录（`tempfile.mkdtemp`），不进入被扫仓库。
_STANDARD = "GB/T 48000.3-2026"
_CLAIM_PREFIX = "本设计" + "符合" + " "
CLAIM_X2 = _CLAIM_PREFIX + _STANDARD + " 的全部要求。"
CLAIM_X3 = _CLAIM_PREFIX + _STANDARD + " 的全部要求，术语按词表统一。"


class Case:
    def __init__(self, cid: str, group: str, what: str, expected: str) -> None:
        self.cid, self.group, self.what, self.expected = cid, group, what, expected
        self.ok: bool | None = None
        self.detail = ""


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout + proc.stderr


def build_collision_root(tmp: pathlib.Path) -> pathlib.Path | None:
    sandbox = tmp / "collision"
    for relative in COLLISION_SOURCES:
        src = ROOT / relative
        dst = sandbox / relative
        if not src.exists():
            print(f"[sandbox] 缺少输入：{relative}", file=sys.stderr)
            return None
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    (sandbox / "scripts").mkdir(exist_ok=True)
    shutil.copy2(COLLISION, sandbox / "scripts" / COLLISION.name)
    shutil.copy2(REFALIGN, sandbox / "scripts" / REFALIGN.name)
    docs = ROOT / "docs/architecture"
    if docs.is_dir():
        (sandbox / "docs/architecture").mkdir(parents=True, exist_ok=True)
        for adr in docs.glob("ADR-ONTO1-*.md"):
            shutil.copy2(adr, sandbox / "docs/architecture" / adr.name)
    # 侧车日志不参与判定，避免复制噪声
    for log in (sandbox / "loops/ONTO1-ontology-split/evidence").glob("*.log"):
        log.unlink()
    return sandbox


def collision_run(sandbox: pathlib.Path) -> tuple[int, str]:
    return run([sys.executable, str(sandbox / "scripts" / COLLISION.name), "--gate",
                "--root", str(sandbox)], cwd=sandbox)


def check_c4_group(tmp: pathlib.Path) -> list[Case]:
    cases: list[Case] = []
    sandbox = build_collision_root(tmp)
    if sandbox is None:
        case = Case("A0", "c4", "沙箱构建", "可构建")
        case.ok, case.detail = False, "输入缺失"
        return [case]

    # A 对照（**2026-09-21 更新**，Owner 授权 C-2 修复已落地）：真实副本 ⇒ **C-2 实测 0 处** + C-1b 未判定
    # ⇒ 整体 **INCOMPLETE（exit 3）**，而 C-4 必须 PASS。断言强度**不降**：
    #   ① 仍须"绝不是 PASS"（若变 exit 0 即 FAIL）；② C-2 必须为 PASS（冲突若回归立即 FAIL）；③ 不得 crash。
    code, out = collision_run(sandbox)
    case = Case("A", "c4", "对照：真实副本（C-2 已修）",
                "exit=3 INCOMPLETE 且 C-2 PASS（0 处）且 C-4 PASS 且不得 crash")
    case.ok = (code == 3 and "[C-2] PASS" in out and "[C-4] PASS" in out
               and "INCOMPLETE" in out and "Traceback" not in out)
    case.detail = (f"exit={code} C-2_PASS={'[C-2] PASS' in out} C-4_PASS={'[C-4] PASS' in out} "
                   f"INCOMPLETE={'INCOMPLETE' in out} crash={'Traceback' in out}")
    cases.append(case)

    # B 反例：删【受控】必需钉值**文件** ⇒ 具名 C-4_REQUIRED_PIN_MISSING，且**不得崩溃**
    target = sandbox / CONTROLLED_PIN
    backup = target.read_bytes()
    target.unlink()
    code, out = collision_run(sandbox)
    case = Case("B", "c4", f"删受控钉值文件 {CONTROLLED_PIN}",
                "具名 C-4_REQUIRED_PIN_MISSING（fail-closed，不得 Traceback）")
    case.ok = ("C-4_REQUIRED_PIN_MISSING" in out) and ("Traceback" not in out)
    case.detail = f"exit={code} 具名FAIL={'C-4_REQUIRED_PIN_MISSING' in out} crash={'Traceback' in out}"
    cases.append(case)
    target.write_bytes(backup)

    # C 反例：删【范围外】必需钉值**文件** ⇒ 同样须具名 FAIL（这是 QA E3 的原意）
    target = sandbox / UNCONTROLLED_PIN
    backup = target.read_bytes()
    target.unlink()
    code, out = collision_run(sandbox)
    case = Case("C", "c4", f"删范围外钉值文件 {UNCONTROLLED_PIN}",
                "具名 C-4_REQUIRED_PIN_MISSING（file 存在性断言）")
    case.ok = ("C-4_REQUIRED_PIN_MISSING" in out) and ("Traceback" not in out)
    case.detail = f"exit={code} 具名FAIL={'C-4_REQUIRED_PIN_MISSING' in out} C-4={'[C-4] PASS' if '[C-4] PASS' in out else 'FAIL'}"
    cases.append(case)
    target.write_bytes(backup)

    # D 还原对照：恢复后 C-4 必须回到 PASS（证明 B/C 不是"永久红"）
    code, out = collision_run(sandbox)
    case = Case("D", "c4", "还原对照", "C-4 回到 PASS（非永久红）")
    case.ok = "[C-4] PASS" in out
    case.detail = f"exit={code} C-4_PASS={'[C-4] PASS' in out}"
    cases.append(case)
    return cases


def check_d3_group(tmp: pathlib.Path) -> list[Case]:
    fixtures = {
        # 文件级 gb_scope 由声称行自身携带的 "GB/T" 满足
        "x2-plain-claim.md": f"# 规则说明\n\n{CLAIM_X2}\n",
        "x3-claim-with-topicword.md": f"# 规则说明\n\n{CLAIM_X3}\n",
        "x4-heading-with-negchar.md": f"# 门禁规则说明\n\n{CLAIM_X2}\n",
        "x5-heading-control.md": f"# 规则说明\n\n{CLAIM_X2}\n",
    }
    root = tmp / "refalign"
    root.mkdir(parents=True, exist_ok=True)
    for name, body in fixtures.items():
        (root / name).write_text(body, encoding="utf-8")

    code, out = run([sys.executable, str(REFALIGN), "--gate", "--root", str(root),
                     "--min-files", "4", "--min-candidates", "4"])
    cases: list[Case] = []

    def violated(name: str) -> bool:
        """该夹具文件是否被判为违规（输出中出现其路径即为命中，而非放行）。"""
        return name in out

    case = Case("Q1a", "d3", "对照（不含关键词的真实声称 X2）", "必须 FAIL（判违规）")
    case.ok = violated("x2-plain-claim.md")
    case.detail = f"exit={code} 判违规={case.ok}"
    cases.append(case)

    case = Case("Q1b", "d3", "**含主题词的真实声称 X3**（QA Q-1）", "必须 FAIL（不得被 rule_statement 放行）")
    case.ok = violated("x3-claim-with-topicword.md")
    case.detail = f"exit={code} 判违规={case.ok}"
    cases.append(case)

    case = Case("R1a", "d3", "标题含「门禁」+ 其下真实声称 X4（QA Q-4/R-1）", "必须 FAIL（不得整节放行）")
    case.ok = violated("x4-heading-with-negchar.md")
    case.detail = f"exit={code} 判违规={case.ok}"
    cases.append(case)

    case = Case("R1b", "d3", "对照：普通标题 + 同一声称 X5", "必须 FAIL（对照）")
    case.ok = violated("x5-heading-control.md")
    case.detail = f"exit={code} 判违规={case.ok}"
    cases.append(case)

    allowed = re.search(r"allowed_by_reason: (\{.*?\})", out)
    if allowed:
        print(f"[d3] {allowed.group(0)}")
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="ONTO1 W-1.5 T-4 验收仪器")
    parser.add_argument("--only", choices=("c4", "d3"), default=None)
    args = parser.parse_args()

    for script in (COLLISION, REFALIGN):
        if not script.is_file():
            print(f"onto1-w15-acceptance: FAIL: 被测脚本缺失 {script}", file=sys.stderr)
            return 2

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="onto1-w15-acc-"))
    cases: list[Case] = []
    try:
        if args.only in (None, "c4"):
            cases += check_c4_group(tmp)
        if args.only in (None, "d3"):
            cases += check_d3_group(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n[T-4 验收矩阵]")
    for case in cases:
        mark = "OK" if case.ok else "NG"
        print(f"  {mark}  {case.cid:4s} {case.what}\n        期望={case.expected}\n        实测={case.detail}")

    bad = [case.cid for case in cases if not case.ok]
    print(f"\nonto1-w15-acceptance: {'PASS' if not bad else 'FAIL'}（{len(cases) - len(bad)}/{len(cases)} 符合预期"
          + (f"；未达: {bad}" if bad else "") + "）")
    print("  说明：NG 表示**被检脚本的缺口仍未修复**，不是仪器故障；请对照 FAILURES.md W15A3-02/03/04 与 QA Q-1/Q-4。")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
