#!/usr/bin/env python3
"""门禁注入测试：**对每个门禁注入一个真实缺陷，要求它失败**。

动因（Owner 要求：逐个给 18 个门禁建负例测试）：
    实测 **18 个门禁 0 个**有可复现的负例测试。
    一个从不失败的检查器，与没有检查器等价，但更危险 —— 它提供虚假的安心。

方法（同一个方法，逐门禁执行）：
    1. 找到该门禁**主要校验的制品**；
    2. 把它**破坏**（JSON 置为非法语法 / 非 JSON 追加垃圾）；
    3. 运行该门禁；
    4. **无论结果如何，立即用原始字节还原**（`finally` + 结束时校验仓库干净）；
    5. 门禁**失败** ⇒ 该门禁对该缺陷**有判别力**（OK）；
       门禁**通过** ⇒ **注入未被检出**（BAD，该门禁在此缺陷上无判别力）。

**安全**：只改一个文件、只改一次、`finally` 还原、结束时 `git status` 必须为空。
**诚实**：无法确定注入目标的门禁列入 UNCOVERED 并给出原因，
**不得**读作"已测通过"。
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("rg", ROOT / "scripts" / "run_gates.py")
rg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rg)

# gate 名 → (注入目标 glob, 说明)。取**第一个**匹配文件。
# glob 为空或未设计 ⇒ UNCOVERED（如实报告，不静默跳过）。
INJECTIONS: dict[str, tuple[str, str]] = {
    "contract-examples": (
        "specs/gk-ke/v1/examples/positive/*.json",
        "破坏一个**正例**样例 → 它应无法通过对应 schema"),
    "contract-coverage": (
        "specs/knowledge-architecture/contracts/*.json",
        "破坏一个合同文件 → 覆盖核对应报错"),
    "metric-definitions": (
        "specs/gk-ke/v1/definitions/_metric_registry.json",
        "破坏指标注册表 → 指标定义核验应失败"),
    "product-card": (
        "specs/product-knowledge/cards/*.json",
        "破坏一张产品卡 → 必填字段核验应失败"),
    "registry-contract": (
        "specs/knowledge-architecture/registry/*.json",
        "破坏一个注册对象 → 注册中心约束测试应失败"),
    "plan-compiler": (
        "specs/gk-ke/v1/definitions/_metric_registry.json",
        "破坏指标注册表 → 计划编译应报错"),
    "semantic-rule-gate": (
        "generated/semantic/*.json",
        "破坏生成的语义制品 → 语义契约门禁应失败"),
    # 注入点经实测（Round7）：`--verify` **不比文件哈希**，做的是语义检查
    # （禁止署名 / 时间泄漏）。故必须植入**它真正检查的语义违规**。
    "dataset-v2": (
        "scenario/seed/18_gk_ke_dataset_v2/world_truth/world_truth.json",
        "植入禁止署名 → 语义校验应失败"),
    "acceptance-pack": (
        "scenario/seed/18_gk_ke_dataset_v2/world_truth/world_truth.json",
        "植入禁止署名 → 验收包应报错"),
    # 注入点经**逐一实测**确定（Round6）：原目标 ROLE_BOARD.yaml（实例）**无效** ——
    # `--template-check` 校验的是 `loops/_template`，且要求
    # `EVIDENCE.json` 的 gates 与 `LOOP.yaml` 的 gate id 集合**一致**。
    # 改注入 `_template/EVIDENCE.json` 为 `{}` → 集合不一致 → FAIL（实测确认）。
    "loop-guard": (
        "loops/_template/EVIDENCE.json",
        "破坏模板 EVIDENCE.json 使 gates 与 LOOP.yaml 不一致 → 模板检查应失败"),
    "secret-scan": (
        "__TEMP_SECRET__",
        "在临时目录放置伪造凭据 → 扫描应检出（用 --root，不动本仓）"),
    "criteria-key-audit": (
        "docs/architecture/GK-KE-语义级消费验证方案-V1.2.2.md",
        "把白名单键改为合同中不存在的键 → 审计应失败"),
    "criteria-line-audit": (
        "docs/architecture/GK-KE-语义级消费验证方案-V1.2.2.md",
        "把一条出处行号改错 → 审计应失败"),
    # 以下为**尚未设计注入**者，如实列入 UNCOVERED（附原因）
}
UNCOVERED_REASONS = {
    "contract-check": "未确定主制品（shell 脚本，需先读其校验逻辑）",
    "enum-consistency": "需构造三层（Java 枚举/seed/schema）漂移场景，尚未设计",
    "probe-mutation-tests": "该门禁**自身即变异测试**；对其再注入需改被测探针脚本，风险高，尚未设计",
    "capability-probe": "readiness 类；需构造能力不可调用场景，尚未设计",
    "counterfactual-test": "readiness 类；需构造反事实失效场景，尚未设计",
    "chain-trace": "需 KERT 服务在跑；尚未设计",
    "semantic-consumption": "注入点为其判定汇总逻辑，尚未设计（其结论已由 NOT_MET 实测覆盖）",
}

# **语法合法、语义违规**的 JSON。
# 依据（Round2/3 反角色攻击）：原先注入**语法非法**的 JSON →
# 6 个门禁**直接崩溃（Traceback）**，那只证明"无输入防御"，**不证明"能校验"**。
# 改为注入**合法但为空**的对象：schema 校验类门禁应给出**受控的校验失败**。
CORRUPT_JSON = "{}"


# --- 精确注入器：对"追加垃圾改不到校验点"的制品，必须**按语义改** ---
# 教训（FAIL-49）：对 .md 判据文档追加文本**改不到白名单键**，
# 审计当然仍通过 —— 那是**测试无效**，不是门禁弱。
def _inj_nonexistent_key(text: str) -> tuple[str, bool]:
    """在判据白名单里插入一个合同中**不存在**的键。key audit 必须失败。"""
    anchor = "| `indicators[].source` | string | 例 `T-CORE-001` |"
    if anchor not in text:
        return text, False
    add = anchor + "\n| `indicators[].__inj__` | string | — |"
    return text.replace(anchor, add, 1), True


def _inj_wrong_lineno(text: str) -> tuple[str, bool]:
    """把一条出处行号改错。line audit 必须失败。"""
    import re as _re
    m = _re.search(r"\(`output-schema\.md:(\d+)`\)", text) or \
        _re.search(r"\| `output-schema\.md:(\d+)` \|", text)
    if not m:
        return text, False
    good = m.group(1)
    bad = str(int(good) + 7)          # 偏移到一个必然不含该字段的行
    return text.replace(f"output-schema.md:{good}", f"output-schema.md:{bad}", 1), True


def run_semantic_injections() -> tuple[int, list[str]]:
    """**语义级注入**：证明门禁有"语义校验能力"，而非只会做哈希/结构比对。

    依据（2026-09-13 反角色攻击命中，第 3 代）：
    `metric-definitions` 在 `{}` 注入下报的是
    `registry fileSha256 不一致` —— **那是完整性比对，不是语义校验**。
    空文件会**首先撞上哈希检查**，把后面的语义检查**遮住**。
    → 这类证据"弱"：它不能排除"门禁只会比哈希"。

    **语义注入**须同时满足：① 违反某条**语义**规则；② **同步**哈希，
    使完整性检查**通过**；③ 门禁**仍**因语义规则失败。
    这才证明校验能力。
    """
    import json as _json
    import hashlib as _hashlib
    import shutil, tempfile

    n_ok, notes = 0, []
    spec = SEMANTIC_INJECTIONS["metric-definitions"]
    tgt = ROOT / spec["target"]
    reg = ROOT / spec["registry"]
    if not tgt.is_file() or not reg.is_file():
        notes.append("目标或登记表缺失，跳过")
        return 0, notes
    snap = Path(tempfile.mkdtemp(prefix="sem-inj-"))
    shutil.copy2(tgt, snap / tgt.name)
    shutil.copy2(reg, snap / reg.name)
    try:
        obj = _json.loads(tgt.read_text(encoding="utf-8"))
        obj[spec["mutate_field"]] = spec["mutate_value"]
        tgt.write_text(_json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        # ② 同步哈希：让完整性检查通过
        subprocess.run([str(c) for c in spec["sync"]], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
        r = subprocess.run([str(c) for c in _gate_cmd(spec["gate"])], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        blob = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 and spec["expect"] in blob:
            n_ok += 1
            print(f"  OK  {spec['gate']:22s} **语义注入**被检出（{spec['expect']}）"
                  f" —— **哈希已同步，仍被抓住 ⇒ 确有语义校验能力**")
        else:
            notes.append(f"{spec['gate']}: 语义注入未被检出（exit={r.returncode}）"
                         f" ⇒ **该门禁可能只会比对哈希**")
            print(f"  **  {spec['gate']:22s} 语义注入**未被检出** ⇒ 校验能力存疑")
    finally:
        shutil.copy2(snap / tgt.name, tgt)
        shutil.copy2(snap / reg.name, reg)
        shutil.rmtree(snap, ignore_errors=True)
    return n_ok, notes


SEMANTIC_INJECTIONS = {
    "metric-definitions": {
        "gate": "metric-definitions",
        "target": "specs/gk-ke/v1/definitions/SIM.METRIC.DEBT_ASSET_RATIO.json",
        "registry": "specs/gk-ke/v1/definitions/_metric_registry.json",
        "mutate_field": "simulationOnly",
        "mutate_value": False,
        "sync": ["python3", "scripts/gk_ke_metric_definitions_check.py", "--write"],
        "expect": "simulationOnly 必须为 true",
    },
}


def _inj_forbidden_signature(text: str) -> tuple[str, bool]:
    """在数据集 JSON 中植入**禁止署名**（真实监管机构名）。

    dataset/acceptance 门禁做的是**语义检查**（`verify_no_forbidden_signatures`
    / `verify_time_leakage`），**不比文件哈希** ——
    故 `{}` 或破坏哈希**都不会**让它失败（Round6/7 实测）。
    必须植入它**真正检查的语义违规**。
    """
    import json as _json
    try:
        obj = _json.loads(text)
    except Exception:                                   # noqa: BLE001
        return text, False
    if not isinstance(obj, dict):
        return text, False
    obj["__injected_source__"] = "国家统计局"
    return _json.dumps(obj, ensure_ascii=False, indent=2), True


PRECISE = {
    "criteria-key-audit": _inj_nonexistent_key,
    "criteria-line-audit": _inj_wrong_lineno,
    "dataset-v2": _inj_forbidden_signature,
    "acceptance-pack": _inj_forbidden_signature,
}


def _target(glob: str) -> Path | None:
    if glob == "__TEMP_SECRET__":
        return None
    matches = sorted(ROOT.glob(glob))
    return matches[0] if matches else None


def _gate_cmd(name: str):
    for g in rg.GATES:
        if g[0] == name:
            return g[1]
    return None


def main() -> int:
    st0 = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True)
    before_status = st0.stdout

    # **覆盖盘点：每个门禁必须被"认领"**（Round9 反角色攻击命中）。
    # 否则后人在 run_gates 新增一个门禁，它会**自动落进盲区**且无人察觉 ——
    # 这是"静默跳过"在**元层面**的重现。故：未被认领者 → 直接失败。
    all_gates = [g[0] for g in rg.GATES]
    # `gate-selftest` 与 `gate-injection-tests` **自身**不作注入对象：
    # 前者已由 10 条分类用例覆盖；后者对自己注入无意义（自指）。
    # 二者**显式认领**，避免落入"未被认领"的误报。
    SELF_EXEMPT = {
        "gate-selftest": "由 10 条分类器用例覆盖（见 gate_selftest.py）",
        "gate-injection-tests": "自指，不作注入对象",
    }
    claimed = set(INJECTIONS) | set(UNCOVERED_REASONS) | set(SELF_EXEMPT)
    unclaimed = [g for g in all_gates if g not in claimed]
    if unclaimed:
        print(f"gate-injection-tests: FAIL —— 下列门禁**既无注入设计、也未登记为未覆盖**："
              f"{unclaimed}。\n  → 新增门禁必须显式认领（设计注入或登记原因），"
              f"否则会静默落入盲区。", file=sys.stderr)
        print("__GATE_VERDICT__=FAIL")
        return 1

    print(f"gate-injection-tests（逐门禁注入真实缺陷）—— 门禁认领 {len(claimed)}/"
          f"{len(all_gates)}")
    print("\n  —— 语义级注入（证明门禁有**语义校验能力**，而非只会比哈希）——")
    sem_ok, sem_notes = run_semantic_injections()
    if sem_notes:
        for n in sem_notes:
            print(f"  !!  {n}")

    ok = bad = uncovered = unproven = 0
    skip_readonly = 0
    crashed_gates: list[str] = []
    details: list[str] = []
    restore_failures: list[str] = []
    original_hash = ""
    for gate, (glob, why) in INJECTIONS.items():
        cmd = _gate_cmd(gate)
        if cmd is None:
            print(f"  SKIP {gate:22s} 不在 GATES 中")
            uncovered += 1
            continue
        target = _target(glob)
        if target is None and glob != "__TEMP_SECRET__":
            print(f"  SKIP {gate:22s} 注入目标不存在: {glob}")
            uncovered += 1
            details.append(f"{gate}: 目标缺失({glob})")
            continue

        original: bytes | None = None
        injected = False
        orig_mode = None          # 只有**注入确实成功**时才需要还原；
        try:                      # 注入本身失败（如只读）则无需还原 ——
                                  # 否则会误报"还原失败"（实测发生过）
            if glob == "__TEMP_SECRET__":
                import tempfile
                tmp = Path(tempfile.mkdtemp())
                # 载荷选择（第 2 项）：原先用 AWS **文档示例**键
                # `AKIAIOSFODNN7EXAMPLE` —— 那是公开示例值，扫描器**常刻意放行**，
                # 故"未检出"可能是**载荷无效**而非门禁弱。
                # 改用结构确定会被判为凭据的形态：私钥头 + 非示例形态的键串。
                # 载荷经**逐种实测**确定（2026-09-13）：
                #   AWS 文档示例键  → 未检出（扫描器刻意放行公开示例值）—— 我原来的载荷即此类
                #   私钥头(短假体)   → 未检出（**可疑，见下**）
                #   `sk-live-…`     → **检出（exit=2）** ← 采用此载荷
                # 私钥头未检出已作为**独立疑点**登记：
                # 可能是扫描器要求合法密钥体，也可能是我构造的假体太短；
                # **未查清之前不得据此断言门禁有漏洞**。
                (tmp / "creds.txt").write_text(
                    "api_key = sk-live-9f2b7c41d8e35a60b4c7f1e29d3a58c6\n",
                    encoding="utf-8")
                cmd = [cmd[0], cmd[1], "--root", str(tmp), "--quiet"]
            else:
                original = target.read_bytes()
                original_hash = hashlib.sha256(original).hexdigest()
                # **注入前先确认可写**：只读制品（如 generated/ 下的产物）
                # 注入会失败，且失败时 `finally` 的还原也会失败 —— 实测曾因此使脚本崩溃。
                # 只读是**保护机制**，不是缺陷；应如实报 SKIP 而非硬闯。
                # **只读制品：一律跳过，不再尝试放开写位。**
                #
                # 依据（2026-09-13 实测事故）：曾用"chmod +w → 注入 → finally 还原内容+权限"，
                # 但 `finally` 中**先还原权限、后还原内容** → 内容还原被拒 →
                # **受保护制品 `generated/semantic/gits-core.schema.json` 被写坏**
                # （7805→45 字节、JSON 非法），且**只读保护被我取消**（git 不跟踪只读位）。
                # 事后经 `git checkout` + `chmod 444` 完全恢复并校验。
                #
                # 结论：**只读是保护机制。绕过它去测试别的机制，是拿受保护制品做赌注。**
                # 该做法已废弃；只读目标如实报 SKIP，**不得**为"覆盖率好看"而重试。
                if not os.access(target, os.W_OK):
                    print(f"  SKIP {gate:22s} 目标只读（受保护制品，按纪律不放开写位）: "
                          f"{target.name}")
                    skip_readonly += 1
                    details.append(f"{gate}: 目标只读，按纪律跳过（{target.name}）")
                    continue
                if gate in PRECISE:
                    new_text, did = PRECISE[gate](original.decode("utf-8"))
                    if not did:
                        print(f"  ?? {gate:22s} 精确注入锚点未命中 —— 测试无效")
                        unproven += 1
                        details.append(f"{gate}: 精确注入锚点未命中（测试无效）")
                        continue
                    target.write_text(new_text, encoding="utf-8")
                elif target.suffix == ".json":
                    target.write_text(CORRUPT_JSON, encoding="utf-8")
                elif target.suffix in (".yaml", ".yml"):
                    target.write_text("__injected_defect__: [unclosed\n", encoding="utf-8")
                else:
                    target.write_bytes(original + b"\n__INJECTED_DEFECT__\n")
                injected = True
            r = subprocess.run([str(c) for c in cmd], cwd=ROOT,
                               capture_output=True, text=True, timeout=300)
            blob = (r.stdout or "") + (r.stderr or "")
            verdict = rg.classify(r.returncode, blob)
            # **"崩溃" ≠ "检出"**（Round2 反角色攻击命中）：
            # 门禁收到非法制品后**抛栈退出**，只证明它**没有输入防御**，
            # **不证明它的校验逻辑发现了缺陷**。真实场景下它同样会崩溃而非给出判定。
            # 故：含 Traceback 的非零退出**不计为检出**，单列 crash。
            crashed = "Traceback" in blob or "JSONDecodeError" in blob
            if crashed:
                crashed_gates.append(gate)
                print(f"  **  {gate:22s} 注入后**崩溃**（Traceback）—— "
                      f"**不算检出**：只证明无输入防御，不证明能校验")
                details.append(f"{gate}: 注入后崩溃（非受控失败）⇒ 检出证据无效")
                continue
            caught = verdict != "PASS"
            if caught:
                ok += 1
                print(f"  OK  {gate:22s} 注入被检出（{verdict}，受控失败）")
            else:
                # **区分两种 BAD**（FAIL-23 教训：负例测试本身可能无效）：
                #   · 注入有效但门禁未检出 → 门禁无判别力（对门禁不利的证据）
                #   · 注入无效（如对 .md 追加垃圾、对模板检查注入实例文件）→ **测试无效**
                # 二者不可混同；后者**不构成**门禁弱的证据。
                if glob == "__TEMP_SECRET__":
                    bad += 1
                    print(f"  BAD {gate:22s} **注入未被检出**（门禁仍 PASS）")
                    details.append(f"{gate}: 注入后仍 PASS ⇒ 对该缺陷无判别力")
                else:
                    unproven += 1
                    print(f"  ?? {gate:22s} 注入**有效性未确立**（门禁仍 PASS）"
                          f" —— 不能据此判定门禁弱")
                    details.append(f"{gate}: **注入可能无效**（{why}）⇒ 测试无效，"
                                   "不得作为门禁无判别力的证据")
        except Exception as exc:                       # noqa: BLE001
            print(f"  ERR {gate:22s} {exc}")
            bad += 1
            details.append(f"{gate}: 执行异常 {exc}")
        finally:
            # 还原**不得抛异常**：否则一处失败会中断整轮（实测发生过）。
            # 且必须**校验哈希**证明真的还原了 —— "我写了还原代码" 不等于 "文件已还原"。
            if orig_mode is not None and target is not None:
                try:
                    # **权限也必须还原**：否则"只读保护"被我悄悄取消了。
                    os.chmod(target, orig_mode)
                    if target.stat().st_mode != orig_mode:
                        raise RuntimeError("权限未还原")
                except Exception as exc:                # noqa: BLE001
                    print(f"  **ERR {gate:20s} 权限还原失败: {exc}**", file=sys.stderr)
                    restore_failures.append(gate)
            if injected and original is not None and target is not None:
                try:
                    target.write_bytes(original)
                    now = hashlib.sha256(target.read_bytes()).hexdigest()
                    if now != original_hash:
                        raise RuntimeError("还原后哈希不符")
                except Exception as exc:                # noqa: BLE001
                    print(f"  **ERR {gate:20s} 还原失败: {exc}**", file=sys.stderr)
                    restore_failures.append(gate)

    print(f"\n  注入测试: {ok} 项**受控失败被检出** / {len(crashed_gates)} 项**崩溃(不算检出)**"
          f" / {bad} 项注入有效但未被检出 / {unproven} 项**注入有效性未确立**")
    print(f"  语义级注入: {sem_ok} 项通过（**哈希已同步，仍被检出 ⇒ 确有语义校验能力**）")
    if crashed_gates:
        print(f"  [CRASHED] 注入后崩溃（只证明无输入防御，**不证明能校验**）：")
        for g in crashed_gates:
            print(f"      - {g}")
    if UNCOVERED_REASONS:
        print("  [UNCOVERED] **尚未设计注入的门禁**（其 PASS 不予采信）：")
        for name, reason in UNCOVERED_REASONS.items():
            print(f"      - {name:24s} {reason}")
        uncovered = len(UNCOVERED_REASONS)
    if details:
        print("\n  详情：")
        for d in details:
            print(f"      · {d}")

    # 注入测试**不得留痕**：与**运行前**快照对比（而非要求仓库为空 ——
    # 原实现把本轮自己的未提交改动误报为"残留"，属**测试自身的假阳性**）。
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True)
    if st.stdout != before_status:
        print("\n  **FAIL: 注入测试留下了改动，仓库不干净：**", file=sys.stderr)
        print(st.stdout[:800], file=sys.stderr)
        return 1

    if restore_failures:
        print(f"\n  **FAIL: {len(restore_failures)} 个目标未成功还原: {restore_failures}**",
              file=sys.stderr)
        return 1

    if bad:
        print(f"\ngate-injection-tests: FAIL ({bad} 项未被检出) —— "
              "上述门禁对该类缺陷无判别力。", file=sys.stderr)
        print("__GATE_VERDICT__=FAIL")
        return 1
    # **覆盖不完整 ⇒ INCONCLUSIVE，不得判 PASS。**
    # 反思（Round1 反角色攻击命中）：本脚本原先在任何"无 bad"情况下 exit=0 →
    # 被门禁链记为 PASS。但当时有 3 项注入有效性未确立 + 7 项未设计 + 1 项跳过
    # = **11/18 个门禁未验证**。读汇总的人看到 `gate-injection-tests PASS`，
    # 会以为"注入测试已完成" —— **这是误导性通过**。
    # 本门禁要证明的是"各门禁有判别力"；**只验了一半就不能算通过**。
    pending = unproven + len(UNCOVERED_REASONS) + skip_readonly + len(crashed_gates)
    if pending:
        print(f"\n__GATE_VERDICT__=INCONCLUSIVE")
        print(f"gate-injection-tests: INCONCLUSIVE —— 已设计 {ok} 项全部被检出，"
              f"但**仍有 {pending} 个门禁未取得负例证据**"
              f"（未确立 {unproven} / 未设计 {len(UNCOVERED_REASONS)} / 只读跳过 "
              f"{skip_readonly} / 崩溃 {len(crashed_gates)}）。**本门禁未完成，不得计为通过。**",
              file=sys.stderr)
        return 0
    print(f"\ngate-injection-tests: 全部 {ok} 项被检出，且无未覆盖门禁。")
    print("__GATE_VERDICT__=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
