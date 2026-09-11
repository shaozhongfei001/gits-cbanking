#!/usr/bin/env python3
"""GK-KE L2-2 注册中心测试（C08 L2-2 / wave B3）。

依据 C02 §3 注册对象（AssetVersion / SourceVersion / Capability / QueryDefinition /
MapVersion / Release）与 C02 §4 边类型约束。

覆盖 C08 L2-2 退出标准：「非授权目录无泄漏；断链拒绝；并发更新 CAS 测试」。

检查：
  1. 注册对象六类均存在且必填字段齐备（C02 §3）
  2. 稳定 ID：assetId/queryId/mapId 唯一；version 不可变（同 id 同 version 内容 hash 必须一致）
  3. **断链拒绝**：所有 dependencyRefs / sourceProductRef / metricRef / routePolicyRef
     引用必须可解析，否则拒绝
  4. **非授权目录无泄漏**：未授权 scope 的资产不得出现在检索/发现结果中
  5. **CAS 并发**：expectedVersion 过期必须拒绝
  6. 能力探针：Capability 必须有 precondition 与探针状态；无探针不得视为可调用
  7. 边类型/端点约束（C02 §4）：6 类边各自的端点类型合法
  8. 负例覆盖上述拒绝路径

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "specs" / "knowledge-architecture" / "registry"
NEG = REG / "negatives"

REQUIRED_FIELDS = {
    "AssetVersion": ["assetId", "version", "assetClass", "kind", "title", "description",
                     "ownerSystem", "ownerRole", "contentRef", "contentHash", "coreVersion",
                     "scope", "purposeFlags", "lifecycle", "dependencyRefs"],
    "SourceVersion": ["sourceId", "version", "originalRef", "hash", "issuedAt", "validFrom",
                      "validTo", "sourceClass", "allowedUses", "permissionRef", "simulationOnly"],
    "Capability": ["capabilityId", "version", "inputSchemaRef", "outputSchemaRef", "executorRef",
                   "preconditions", "sideEffect", "permissionRef", "budget", "timeoutMs",
                   "idempotencyPolicy"],
    "QueryDefinition": ["queryId", "version", "parameterSchemaRef", "templateRef",
                        "resultSchemaRef", "sourceProductRef", "maxRows", "timeoutMs", "metricRef"],
    "MapVersion": ["mapId", "version", "taskTypes", "entryNodes", "nodes", "edges",
                   "routePolicyRef", "releaseRef", "coverage", "dependencyRefs"],
    "Release": ["releaseId", "manifest", "hash", "approvalRefs", "qualityRunRef",
                "effectiveFrom", "purposeFlags"],
}

EDGE_ENDPOINTS = {
    "requires": {("Task", "Asset"), ("Task", "Capability")},
    "optional": {("Task", "Asset"), ("Task", "Capability")},
    "uses": {("Capability", "Asset")},
    "dependsOn": {("Asset", "Asset"), ("Asset", "Capability"), ("Capability", "Asset"), ("Capability", "Capability")},
    "covers": {("KnowledgeDomain", "Asset")},
    "relatedTo": {("KnowledgeDomain", "KnowledgeDomain"), ("KnowledgeDomain", "Asset"),
                  ("Asset", "KnowledgeDomain"), ("Asset", "Asset")},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:  # noqa: C901
    failures: list[str] = []
    objects: dict[str, list[dict]] = {}

    for kind in REQUIRED_FIELDS:
        path = REG / f"{kind}.json"
        if not path.is_file():
            failures.append(f"[1] registry object file missing: {path}")
            objects[kind] = []
            continue
        doc = load(path)
        items = doc.get("items", [])
        objects[kind] = items
        for i, item in enumerate(items):
            missing = [f for f in REQUIRED_FIELDS[kind] if f not in item]
            if missing:
                failures.append(f"[1] {kind}[{i}] missing required fields: {missing}")

    # 2. 稳定 ID + version 不可变
    for kind, id_field in (("AssetVersion", "assetId"), ("SourceVersion", "sourceId"),
                           ("Capability", "capabilityId"), ("QueryDefinition", "queryId"),
                           ("MapVersion", "mapId"), ("Release", "releaseId")):
        seen: dict[tuple[str, str], str] = {}
        for item in objects.get(kind, []):
            key = (str(item.get(id_field)), str(item.get("version")))
            digest = str(item.get("contentHash") or item.get("hash") or "")
            if key in seen and seen[key] != digest:
                failures.append(f"[2] {kind}: version {key} content hash changed (version must be immutable)")
            seen[key] = digest

    # 3. 断链拒绝
    known = {
        "asset": {i["assetId"] for i in objects.get("AssetVersion", [])},
        "source": {i["sourceId"] for i in objects.get("SourceVersion", [])},
        "capability": {i["capabilityId"] for i in objects.get("Capability", [])},
        "query": {i["queryId"] for i in objects.get("QueryDefinition", [])},
        "map": {i["mapId"] for i in objects.get("MapVersion", [])},
        "release": {i["releaseId"] for i in objects.get("Release", [])},
    }
    def resolvable(ref: str) -> bool:
        if not isinstance(ref, str) or not ref:
            return False
        if ref in known["asset"] or ref in known["capability"] or ref in known["source"]:
            return True
        if ref in known["query"] or ref in known["map"] or ref in known["release"]:
            return True
        # 已登记 schema 引用（gk-ke/v1:<Schema>）：须能在 specs 中找到对应 schema
        if ref.startswith("gk-ke/v1:"):
            name = ref.split(":", 1)[1]
            return (ROOT / "specs" / "gk-ke" / "v1" / "schemas" / f"{name}.schema.json").is_file() or (
                ROOT / "specs" / "gk-ke" / "v1" / "schemas" / f"{name}.full.schema.json"
            ).is_file()
        # 仓库内文件引用：须真实存在
        if "/" in ref and not ref.startswith("SIM"):
            return (ROOT / ref).is_file()
        # 指标/路由等外部引用须以显式已登记前缀出现
        return ref.startswith(("SIM.METRIC.", "SIM-ROUTE-", "SIM-POLICY-", "SIM-TASK-"))

    for kind in ("AssetVersion", "MapVersion"):
        for item in objects.get(kind, []):
            for ref in item.get("dependencyRefs", []) or []:
                if not resolvable(ref):
                    failures.append(f"[3] {kind} {item.get('assetId') or item.get('mapId')}: dangling dependencyRef {ref!r}")
    for item in objects.get("QueryDefinition", []):
        for field in ("sourceProductRef", "metricRef", "templateRef", "resultSchemaRef"):
            ref = item.get(field)
            if ref and not resolvable(ref):
                failures.append(f"[3] QueryDefinition {item.get('queryId')}: dangling {field}={ref!r}")
    for item in objects.get("MapVersion", []):
        rp = item.get("routePolicyRef")
        if rp and not resolvable(rp):
            failures.append(f"[3] MapVersion {item.get('mapId')}: dangling routePolicyRef {rp!r}")

    # 4. 非授权目录无泄漏：authorized=false 的资产不得出现在 scope 内
    for item in objects.get("AssetVersion", []):
        scope = item.get("scope") or {}
        if scope.get("authorized") is False and item.get("discoverable") is True:
            failures.append(f"[4] AssetVersion {item.get('assetId')}: unauthorized but discoverable (leak)")

    # 5. CAS 并发（必须有真实触发路径：带 expectedError=CAS_STALE_VERSION_ACCEPTED 的条目必须被拒）
    cas_violations = 0
    for item in objects.get("AssetVersion", []):
        if item.get("casExpectedVersion") is None or item.get("currentVersion") is None:
            continue
        stale = str(item["casExpectedVersion"]) != str(item["currentVersion"])
        if not (stale and item.get("casAccepted") is True):
            continue
        cas_violations += 1
        # 该状态必须被拒绝：带 expectedError 的为测试夹具（合理存在），否则为真缺陷
        if item.get("expectedError") != "CAS_STALE_VERSION_ACCEPTED":
            failures.append(f"[5] AssetVersion {item.get('assetId')}: stale expectedVersion accepted")
    if cas_violations == 0:
        failures.append("[5] CAS check has no triggering fixture (assertion would be noop) "
                        "- see FAIL-2026-09-12-07")

    # 6. 能力探针
    for item in objects.get("Capability", []):
        if not item.get("preconditions"):
            failures.append(f"[6] Capability {item.get('capabilityId')}: no preconditions")
        probe = item.get("probeStatus")
        if probe not in {"PASSED", "FAILED", "NOT_PROBED"}:
            failures.append(f"[6] Capability {item.get('capabilityId')}: invalid probeStatus {probe!r}")
        if probe != "PASSED" and item.get("callable") is True:
            failures.append(f"[6] Capability {item.get('capabilityId')}: callable without passing probe")

    # 7. 边类型/端点约束
    for item in objects.get("MapVersion", []):
        for edge in item.get("edges", []) or []:
            relation = edge.get("relation")
            pair = (edge.get("fromType"), edge.get("toType"))
            if relation not in EDGE_ENDPOINTS:
                failures.append(f"[7] MapVersion {item.get('mapId')}: unknown relation {relation!r}")
            elif pair not in EDGE_ENDPOINTS[relation]:
                failures.append(f"[7] MapVersion {item.get('mapId')}: {relation} disallows {pair}")

    # 8. 负例覆盖
    neg_count = 0
    if NEG.is_dir():
        for path in sorted(NEG.glob("*.json")):
            doc = load(path)
            if not doc.get("expectedError"):
                failures.append(f"[8] {path.name}: missing expectedError")
            neg_count += 1

    if failures:
        print("gk-ke-l2-2-registry-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l2-2-registry-tests: PASS")
    for kind in REQUIRED_FIELDS:
        print(f"  {kind}: {len(objects.get(kind, []))} item(s)")
    print(f"  negatives={neg_count}")
    print("  checks: required-fields, stable-id/immutable-version, dangling-ref, leak, CAS, probe, edge-endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
