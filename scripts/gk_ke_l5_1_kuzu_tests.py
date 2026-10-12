#!/usr/bin/env python3
"""GK-KE L5-1 Kuzu 图适配测试（C08 L5-1 / wave C3）。

依据 C05《RAG 与图适配合同》「图服务」路径与 C08 L5-1 退出标准：
「不覆盖源；边级权限/撤销；停止图服务的降级用例」。

检查：
  1. 锁版：Kuzu 版本固定（不得漂移）
  2. **图投影不覆盖源**：图是**可重建投影**，不得承载注册中心权威事务
  3. **有界 queryId**：只接受已登记 queryId，拒绝任意 Cypher
  4. **候选/发布隔离**：候选投影不得进入已发布检索
  5. **边级权限**：无权边不得返回
  6. **边级撤销**：撤销边立即不可见，且**不等待投影重建**
  7. **降级用例**：图服务停止时返回 503 语义明确，**不得返回 200 空结果**
  8. 重建/导出/恢复报告齐备（可重建性证据）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "specs" / "knowledge-architecture" / "graph"


def load(name: str):
    return json.loads((GRAPH / name).read_text(encoding="utf-8"))


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not GRAPH.is_dir():
        print(f"FAIL: graph dir missing: {GRAPH}", file=sys.stderr)
        return 2

    manifest = load("graph_manifest.json")
    queries = load("bounded_queries.json")
    violations = load("violations.json").get("violations", [])

    # 1. 锁版
    version = manifest.get("kuzuVersion")
    if not version or version == "latest" or str(version).startswith("^"):
        failures.append(f"[1] Kuzu version must be pinned, got {version!r}")
    if not manifest.get("versionLocked"):
        failures.append("[1] Kuzu version not marked locked")

    # 2. 投影不覆盖源
    if manifest.get("isRebuildableProjection") is not True:
        failures.append("[2] graph must be declared a rebuildable projection")
    if manifest.get("carriesAuthoritativeTransactions") is True:
        failures.append("[2] graph must NOT carry registry authoritative transactions")
    if manifest.get("sourceOfTruth") != "registry":
        failures.append(f"[2] sourceOfTruth must be registry, got {manifest.get('sourceOfTruth')!r}")

    # 3. 有界 queryId
    registered = {q["queryId"] for q in queries.get("queries", [])}
    for q in queries.get("queries", []):
        if not q.get("bounded") is True:
            failures.append(f"[3] query {q.get('queryId')}: not bounded")
        if "freeCypher" in q or "rawCypher" in q:
            failures.append(f"[3] query {q.get('queryId')}: free-form Cypher is not allowed")
    if manifest.get("acceptsArbitraryCypher") is True:
        failures.append("[3] adapter must not accept arbitrary Cypher")

    # 4. 候选/发布隔离
    if manifest.get("candidateProjectionSeparate") is not True:
        failures.append("[4] candidate projection must be separate from published")
    for n in manifest.get("nodes", []):
        if n.get("releaseState") == "CANDIDATE" and n.get("searchableInPublished") is True:
            failures.append(f"[4] node {n.get('nodeId')}: candidate node visible in published search")

    # 5. 边级权限
    for e in manifest.get("edges", []):
        if e.get("authorized") is False and e.get("visible") is True:
            failures.append(f"[5] edge {e.get('edgeId')}: unauthorized edge is visible")

    # 6. 边级撤销（立即生效，不等重建）
    for e in manifest.get("edges", []):
        if e.get("revoked") is True:
            if e.get("visible") is True:
                failures.append(f"[6] edge {e.get('edgeId')}: revoked but still visible")
            if e.get("awaitingRebuild") is True:
                failures.append(f"[6] edge {e.get('edgeId')}: revocation must not wait for projection rebuild")

    # 7. 降级用例
    degraded = manifest.get("degradedBehavior", {})
    if degraded.get("graphUnavailableStatus") != 503:
        failures.append(f"[7] graph unavailable must return 503, got {degraded.get('graphUnavailableStatus')!r}")
    if degraded.get("returnsEmptyResultWhenUnavailable") is True:
        failures.append("[7] must NOT return a 200 empty result when graph is unavailable")
    if degraded.get("fallbackPath") != "existing_rag_adapter":
        failures.append("[7] degraded path must fall back to the existing RAG adapter")

    # 8. 重建/导出/恢复报告
    for field in ("rebuildReportRef", "exportReportRef", "restoreReportRef"):
        if not manifest.get(field):
            failures.append(f"[8] missing {field}")

    # 负例（fail-closed）
    required = {"ARBITRARY_CYPHER_REJECTED", "UNAUTHORIZED_EDGE_HIDDEN", "REVOKED_EDGE_IMMEDIATE",
                "GRAPH_DOWN_503", "CANDIDATE_NOT_IN_PUBLISHED"}
    covered = {v.get("expectedError") for v in violations}
    uncovered = required - covered
    if uncovered:
        failures.append(f"[neg] rejection paths without fixtures: {sorted(uncovered)}")
    for v in violations:
        if v.get("detected") is not True:
            failures.append(f"[neg] {v.get('case')}: not detected")
            uncovered = True

    if failures:
        print("gk-ke-l5-1-kuzu-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l5-1-kuzu-tests: PASS")
    print(f"  kuzuVersion={version} locked={manifest.get('versionLocked')}")
    print(f"  registered_queries={sorted(registered)}")
    print(f"  nodes={len(manifest.get('nodes', []))} edges={len(manifest.get('edges', []))}")
    print(f"  degraded=503 fallback={degraded.get('fallbackPath')}")
    print("  checks: version-lock, projection-not-authority, bounded-query, candidate-isolation, "
          "edge-acl, edge-revoke-immediate, degrade-503, rebuild-reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
