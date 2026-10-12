#!/usr/bin/env python3
"""GK-KE 能力探针的变异测试 v2.0.0。

【为什么重写】
v1.0.0 的变异测试只覆盖了旧探针的"条件齐备性"判定，
而旧探针的 **PASSED 实际由样例文件里的静态 `dryRunVerified: true` 决定**，
从未真实调用 KERT。独立 QA 指出该缺陷，经核验属实。

【v2 新增的核心断言（直接针对该缺陷）】
  M0: 样例里 `dryRunVerified: true`，但**没有可用服务** → **绝不能 PASSED**。
      这条断言的存在，就是为了防止"静态标志冒充真实调用"复现。
  M9: 真实调用成功但输出**不符合该技能语义契约** → 必须是
      `CALLED_CONTRACT_UNMET` 而**不是** PASSED。

每个变异体构造受控输入，调用探针核心 `probe_one`，
若探针给出错误的"通过"判定，则该断言是空转或失效的。

用法：
  python3 scripts/gk_ke_capability_probe_tests.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "probe", ROOT / "scripts" / "gk_ke_capability_probe.py")
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)

BASE_ITEM = {
    "capabilityId": "SIM-CAP-TEST",
    "executorRef": "bank-front-fact-reconciliation",
    "inputSchemaRef": "gk-ke/v1:Req",
    "outputSchemaRef": "gk-ke/v1:Res",
    "probeStatus": "NOT_PROBED",
    "callable": False,
}

BASE_SAMPLE = {
    "capabilityId": "SIM-CAP-TEST",
    "input": {"customerId": "SIM-C001"},
    "mustFail": [{"caseId": "N1", "expectedError": "X"}],
    "dryRunVerified": True,
}


class FakeService:
    """受控假服务：镜像真实 SkillExecutionService 的接口。

    关键：必须提供 `_packages`，因为探针的契约期望**取自 provider 自身声明的
    schema_keys**（而非 GK-KE 侧硬编码）。若假服务不提供该结构，
    探针会判 NOT_PROBED，测试即失去意义。
    """

    def __init__(self, schema_keys=None, result_keys=None, status="ok",
                 raise_exc=False):
        # provider 声明的 schema 顶层键
        self._packages = {
            "bank-front-fact-reconciliation": {
                "schema_keys": schema_keys if schema_keys is not None
                else ["schemaVersion", "skillId", "customerId",
                      "indicators", "conflicts"]
            }
        }
        # 实际返回的 result 内层键
        self.result_keys = result_keys
        self.status = status
        self.raise_exc = raise_exc
        self.called = 0

    def execute(self, skill_id, request_id, request):  # noqa: D401,WPS110
        self.called += 1
        if self.raise_exc:
            raise RuntimeError("simulated executor failure")

        declared = (self._packages.get(skill_id) or {}).get("schema_keys") or []
        keys = self.result_keys if self.result_keys is not None else declared

        class R:
            pass

        r = R()
        r.status = self.status
        # 真实外壳：{"skillId":..., "result": {...技能语义结构...}}
        r.data = {"skillId": skill_id, "result": {k: [] for k in keys}}
        return r


def run_case(item, samples, mapping_index, svc, svc_err=""):
    return probe.probe_one(item, samples, mapping_index, svc, svc_err)


def main() -> int:
    fails: list[str] = []
    passed = 0
    good_keys = ["schemaVersion", "skillId", "customerId", "indicators", "conflicts"]
    good_svc = FakeService(schema_keys=good_keys)

    # 基线：真实调用成功且结构符合 → PASSED
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, good_svc)
    if r["verdict"] != "PASSED" or r["callable"] is not True:
        fails.append(f"base: 期望 PASSED，实为 {r['verdict']}")
    else:
        passed += 1

    # --- M0：**核心断言** — 静态 dryRunVerified=true 但无服务，绝不能 PASSED ---
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, None,
                 "服务不可用")
    if r["verdict"] == "PASSED" or r["callable"]:
        fails.append("M0: 无真实调用却判 PASSED —— 静态标志冒充真实调用（禁止）")
    else:
        passed += 1

    # 确认 M0 的输入里确实带着 dryRunVerified=true（否则该用例无意义）
    if BASE_SAMPLE.get("dryRunVerified") is not True:
        fails.append("M0 前置失效：样例未含 dryRunVerified=true，该断言无意义")

    # M1: 无语义样例 → 不得 PASSED
    r = run_case(dict(BASE_ITEM), {}, {}, good_svc)
    if r["verdict"] == "PASSED":
        fails.append("M1: 无语义样例却判 PASSED")
    else:
        passed += 1

    # M2: 样例缺 mustFail 负例 → 不得 PASSED
    s = dict(BASE_SAMPLE); s.pop("mustFail", None)
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": s}, {}, good_svc)
    if r["verdict"] == "PASSED":
        fails.append("M2: 无 mustFail 负例却判 PASSED")
    else:
        passed += 1

    # M3: provider 未解析 → 不得 PASSED
    it = dict(BASE_ITEM); it["executorRef"] = "PENDING_NAMING_MAPPING"
    r = run_case(it, {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, good_svc)
    if r["verdict"] == "PASSED":
        fails.append("M3: provider 未解析却判 PASSED")
    else:
        passed += 1

    # --- M9：**核心断言** — 调用成功但输出不符合语义契约 → 不得 PASSED ---
    bad_svc = FakeService(schema_keys=good_keys, result_keys=["skillId", "result"])
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, bad_svc)
    if r["verdict"] != "CALLED_CONTRACT_UNMET":
        fails.append(
            f"M9: 输出不符契约时应判 CALLED_CONTRACT_UNMET，实为 {r['verdict']}")
    else:
        passed += 1

    # M10: 调用抛异常 → CALL_FAILED，不得 PASSED
    exc_svc = FakeService(raise_exc=True)
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, exc_svc)
    if r["verdict"] == "PASSED" or r["callable"]:
        fails.append(f"M10: 调用异常却判 {r['verdict']}")
    else:
        passed += 1

    # M11: 调用返回非 ok → 不得 PASSED
    err_svc = FakeService(schema_keys=good_keys, status="skill_error")
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, err_svc)
    if r["verdict"] == "PASSED" or r["callable"]:
        fails.append(f"M11: status!=ok 却判 {r['verdict']}")
    else:
        passed += 1

    # M12: 无独立 output-schema 的 provider，即使调用成功也不得声称契约满足
    it = dict(BASE_ITEM); it["executorRef"] = "skill-customer-outreach-script"
    r = run_case(it, {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, good_svc)
    if r["verdict"] == "PASSED":
        fails.append("M12: 无 output-schema 的 provider 却判 PASSED")
    else:
        passed += 1

    # M13: 假服务必须真的被调用过（证明"真实调用"确实发生）
    svc = FakeService(schema_keys=good_keys)
    run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {}, svc)
    if svc.called == 0:
        fails.append("M13: 判 PASSED 但服务从未被调用 —— 探针未真实调用")
    else:
        passed += 1

    total = passed + len(fails)
    if fails:
        print("gk-ke-capability-probe-tests: FAIL", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"gk-ke-capability-probe-tests: PASS ({passed}/{total} 变异被捕获)")
    print("  含两条核心断言：M0 静态标志不得冒充真实调用；"
          "M9 输出不符契约不得判通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
