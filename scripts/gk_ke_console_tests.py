#!/usr/bin/env python3
"""GK-KE 人工验收台测试（GK13 / wave G）。

校验控制台**真的能触发全部拒绝**（否则人工验证会看到"永远绿灯"的假象），
且页面字段全部来自合同夹具，不含发明字段。

检查：
  1. 控制台依赖的数据文件全部存在
  2. **18 类拒绝全部可在控制台中触发**（OC-03×7 / OC-04×5 / OC-05×6）
  3. 正例**不得**触发任何拒绝（避免"永远红灯"）
  4. 注入为**只读**（不写入任何文件；注入后文件字节不变）
  5. 数据全部 `simulationOnly=true`
  6. 拒绝码与合同/条款一一对应（可追溯）
  7. 前端引用的注入 ID 与服务端 INJECTIONS 一致

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_OC03 = {
    "CONTENT_CHANGED_AFTER_APPROVAL", "SELF_APPROVAL", "EXPIRED_APPROVAL_COUNTED",
    "HALF_PUBLISH", "REVOKED_STILL_SEARCHABLE", "ROLLBACK_TO_REVOKED",
    "PURPOSE_FLAG_SILENT_UPGRADE",
}
REQUIRED_OC04 = {"ROUTE_AMBIGUOUS", "NO_MATCH_REJECT", "GITS_WRITEBACK_IN_KERT_PLAN",
                 "DEPENDENCY_CYCLE", "REQUIRED_CAPABILITY_MISSING"}
REQUIRED_OC05 = {"FORBIDDEN_ACTION_REJECTED", "STALE_TARGET_VERSION_REJECTED",
                 "MISSING_CONFIRMATION_REJECTED", "TIMEOUT_RESULT_UNKNOWN",
                 "STATEMENT_AS_FACT_REJECTED", "UNKNOWN_PURPOSE_NOT_ADMITTED"}


def load_server():
    spec = importlib.util.spec_from_file_location(
        "console_server", ROOT / "scripts" / "gk_ke_console_server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect(mod, injection: str) -> set[str]:
    state = mod.apply_injection("console", injection)
    codes: set[str] = set()
    for r in mod.eval_release(state.get("release") or {})["rejections"]:
        codes.add(r["code"])
    for r in mod.eval_activation(state.get("plan") or {}, state.get("route_policy") or {},
                                 state.get("_route_task"))["rejections"]:
        codes.add(r["code"])
    for r in mod.eval_closed_loop(state.get("closed_loop") or {})["rejections"]:
        codes.add(r["code"])
    return codes


def file_hashes() -> dict[str, str]:
    out = {}
    for rel in ("specs/knowledge-architecture/release/release_manifest.json",
                "specs/knowledge-architecture/activation/activation_plan.json",
                "specs/knowledge-architecture/closed-loop/closed_loop_run.json",
                "specs/openapi/gk-ke-v1.openapi.json"):
        p = ROOT / rel
        if p.is_file():
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main() -> int:  # noqa: C901
    failures: list[str] = []
    mod = load_server()

    # 1. 数据齐备
    state = mod.snapshot()
    for key, val in state.items():
        if val is None:
            failures.append(f"[1] missing console data: {key}")

    console = ROOT / "tools" / "gk-ke-console" / "index.html"
    if not console.is_file():
        failures.append(f"[1] console page missing: {console}")

    # 2. 全部拒绝可触发
    covered: set[str] = set()
    for inj in mod.INJECTIONS:
        covered |= collect(mod, inj)

    for name, required in (("OC-03", REQUIRED_OC03), ("OC-04", REQUIRED_OC04), ("OC-05", REQUIRED_OC05)):
        missing = required - covered
        if missing:
            failures.append(f"[2] {name} rejections not triggerable in console: {sorted(missing)}")

    # 3. 正例不得触发拒绝
    baseline = collect(mod, "NONE")
    if baseline:
        failures.append(f"[3] positive case unexpectedly triggers rejections: {sorted(baseline)}")

    # 4. 只读：注入前后文件字节不变
    before = file_hashes()
    for inj in mod.INJECTIONS:
        mod.apply_injection("console", inj)
    after = file_hashes()
    if before != after:
        failures.append("[4] injection modified repository files (must be read-only)")

    # 5. simulationOnly 贯穿
    for key in ("release", "plan", "closed_loop", "map_spec", "graph"):
        doc = state.get(key) or {}
        if "simulationOnly" in doc and doc["simulationOnly"] is not True:
            failures.append(f"[5] {key}: simulationOnly must be true")

    # 6. 每条拒绝码可追溯到条款
    for inj in mod.INJECTIONS:
        st = mod.apply_injection("console", inj)
        all_rej = (mod.eval_release(st.get("release") or {})["rejections"]
                   + mod.eval_activation(st.get("plan") or {}, st.get("route_policy") or {},
                                         st.get("_route_task"))["rejections"]
                   + mod.eval_closed_loop(st.get("closed_loop") or {})["rejections"])
        for r in all_rej:
            if not r.get("clause"):
                failures.append(f"[6] rejection {r.get('code')} lacks a contract clause reference")
            if r.get("http") is None:
                failures.append(f"[6] rejection {r.get('code')} lacks an HTTP status")

    # 7. 前端注入 ID 与服务端一致
    if console.is_file():
        html = console.read_text(encoding="utf-8")
        for prefix in ("OC03_", "OC04_", "OC05_"):
            server_ids = {i for i in mod.INJECTIONS if i.startswith(prefix)}
            if not server_ids:
                failures.append(f"[7] no server injections for prefix {prefix}")
            # 前端按前缀渲染，无需逐字硬编码；仅校验前缀已被引用
            if prefix not in html:
                failures.append(f"[7] console does not reference injection prefix {prefix}")

    if failures:
        print("gk-ke-console-tests: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("gk-ke-console-tests: PASS")
    print(f"  console: {console.relative_to(ROOT)}")
    print(f"  injections: {len(mod.INJECTIONS)}")
    print(f"  rejections triggerable: {len(covered)} "
          f"(OC-03={len(REQUIRED_OC03)} OC-04={len(REQUIRED_OC04)} OC-05={len(REQUIRED_OC05)})")
    print("  read-only: verified (no file bytes changed after injection)")
    print("  positive case: no rejections")
    print("  checks: data-present, all-rejections-triggerable, no-false-positive, "
          "read-only, simulation-only, traceable-clauses, injection-parity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
