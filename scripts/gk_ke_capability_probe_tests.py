#!/usr/bin/env python3
"""GK-KE 能力探针的变异测试（证明探针断言非空转）。

本项目有"假绿"前科（6 个模块首报门禁全绿但断言实际为空转），
故对探针本身也做变异测试：**故意破坏条件，探针必须转为失败**。

每个变异体构造一份被篡改的输入，调用探针核心判定，
若探针仍判 PASSED，则说明该断言是空转的。

用法：
  python3 scripts/gk_ke_capability_probe_tests.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "probe", ROOT / "scripts" / "gk_ke_capability_probe.py")
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


BASE_ITEM = {
    "capabilityId": "SIM-CAP-TEST",
    "version": "1.0.0",
    "executorRef": "SIM-EXEC-TEST",
    "inputSchemaRef": "gk-ke/v1:Req",
    "outputSchemaRef": "gk-ke/v1:Res",
    "probeStatus": "NOT_PROBED",
    "callable": False,
}

BASE_SAMPLE = {
    "capabilityId": "SIM-CAP-TEST",
    "input": {"a": 1},
    "expected": {"status": "SUCCESS", "evidenceRefsRequired": True},
    "mustFail": [{"caseId": "N1", "expectedError": "X"}],
    "dryRunVerified": True,
}


def run_case(item: dict, samples: dict, mapping_index: dict) -> dict:
    return probe.probe_capability(item, samples, mapping_index)


def main() -> int:
    fails: list[str] = []
    passed = 0

    # 基线：条件齐备 → 应 PASSED
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {})
    if r["verdict"] != "PASSED" or r["callable"] is not True:
        fails.append(f"base case should PASS, got {r['verdict']}")
    else:
        passed += 1

    # 变异 M1：去掉语义样例 → 必须 NOT_PROBED（不得因端点存在而通过）
    r = run_case(dict(BASE_ITEM), {}, {})
    if r["verdict"] == "PASSED":
        fails.append("M1: 无语义样例却判 PASSED（空转）")
    else:
        passed += 1

    # 变异 M2：样例缺 evidenceRefs 要求 → 必须非 PASSED
    s = dict(BASE_SAMPLE); s["expected"] = {"status": "SUCCESS"}
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": s}, {})
    if r["verdict"] == "PASSED":
        fails.append("M2: 未要求证据引用却判 PASSED")
    else:
        passed += 1

    # 变异 M3：无失败负例 → 必须非 PASSED（无法验证失败行为）
    s = dict(BASE_SAMPLE); s["mustFail"] = []
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": s}, {})
    if r["verdict"] == "PASSED":
        fails.append("M3: 无 mustFail 负例却判 PASSED")
    else:
        passed += 1

    # 变异 M4：executorRef 未解析 → 必须 NOT_PROBED
    it = dict(BASE_ITEM); it["executorRef"] = "PENDING_NAMING_MAPPING"
    r = run_case(it, {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {})
    if r["verdict"] == "PASSED":
        fails.append("M4: provider 未解析却判 PASSED")
    else:
        passed += 1

    # 变异 M5：schema 未固定 → 必须非 PASSED
    it = dict(BASE_ITEM); it["inputSchemaRef"] = "PENDING"
    r = run_case(it, {"SIM-CAP-TEST": dict(BASE_SAMPLE)}, {})
    if r["verdict"] == "PASSED":
        fails.append("M5: schema 未固定却判 PASSED")
    else:
        passed += 1

    # 变异 M6：映射 verdict 非 PROVEN_COMPATIBLE → 必须非 PASSED
    r = run_case(
        dict(BASE_ITEM),
        {"SIM-CAP-TEST": dict(BASE_SAMPLE)},
        {"SIM-CAP-TEST": {"verdict": "PENDING"}},
    )
    if r["verdict"] == "PASSED":
        fails.append("M6: 映射未证实兼容却判 PASSED（违反建议书 §9.2）")
    else:
        passed += 1

    # 变异 M7：dryRunVerified=false → 必须 FAILED（不是 PASSED）
    s = dict(BASE_SAMPLE); s["dryRunVerified"] = False
    r = run_case(dict(BASE_ITEM), {"SIM-CAP-TEST": s}, {})
    if r["verdict"] == "PASSED":
        fails.append("M7: dryRunVerified=false 却判 PASSED")
    else:
        passed += 1

    # 变异 M8：NOT_PROBED 的能力若 callable 被置 true → 探针须给出 callable=false
    it = dict(BASE_ITEM); it["callable"] = True
    r = run_case(it, {}, {})
    if r["callable"] is True:
        fails.append("M8: 未探针能力仍返回 callable=true")
    else:
        passed += 1

    total = passed + len(fails)
    if fails:
        print("gk-ke-capability-probe-tests: FAIL", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"gk-ke-capability-probe-tests: PASS ({passed}/{total} 变异被捕获)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
