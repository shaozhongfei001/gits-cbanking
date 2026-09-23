#!/usr/bin/env python3
"""代码事实索引红线门禁（GOV-CFI-001）。

定位：TL / 架构角色使用的"代码事实索引与检索底座"（Understand-Anything 派生视图）
      的**红线可判定项**门禁。它不是"理解是否到位"的证明——那件事机器判不了。

判定原则（沿用本仓 fail-closed 惯例）：
- 可判定的红线 → 缺输入即失败，不默认放行；
- 不可判定的项（"索引有没有被真正使用"）不假装判定，只输出证据；
- 新鲜度属 advisory（WARN），仅在 --require 下阻塞。

红线（FAIL，exit 2）：
  R1 派生视图不得入库      .ua/ 必须被 git 忽略，且不得被 git 跟踪
  R2 采集边界不得放开凭据  .understandignore 的凭据/二进制排除项必须处于生效态
  R3 索引不得无声升格      .ua/ 产物必须自带"非权威"标记；流程文档与规则必须仍在
  R4 产物必须可解析        索引 JSON 结构自洽（nodes/edges/layers）
  R5 流程与规则必须落盘    docs/governance/CODE-FACT-INDEX-PROCESS.md + 规则文件

Advisory（WARN）：
  F1 索引新鲜度            .ua/merge-meta.json 与 .ua/meta.json 记录的 commit 相对 HEAD 的漂移
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

PROCESS_DOC = "docs/governance/CODE-FACT-INDEX-PROCESS.md"
RULE_FILE = ".codebuddy/rules/code-fact-index/RULE.mdc"
GRAPH = ".ua/knowledge-graph.json"
MERGE_META = ".ua/merge-meta.json"
SCAN_META = ".ua/meta.json"
IGNORE_FILE = ".understandignore"

# §B 凭据与二进制：数据出域防护，任何放开都必须是一条显式 Owner 裁决
REQUIRED_IGNORE_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.jks",
    "*.keystore",
    "*.class",
    "*.jar",
    "*.war",
    "*.xlsx",
    "*.docx",
)
# §C 自我递归防护
REQUIRED_SELF_PATTERNS = (".ua/",)

DOC_MARKERS = ("回源", "DERIVED", "index-status")
RULE_MARKERS = ("回源", "DERIVED")

DEFAULT_MAX_DRIFT = 50
DEFAULT_MAX_AGE_DAYS = 14


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def active_patterns(text: str) -> set:
    patterns = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.add(line)
    return patterns


def git_head(root: Path) -> str | None:
    result = run_git(root, "rev-parse", "HEAD")
    value = result.stdout.strip()
    return value if result.returncode == 0 and len(value) == 40 else None


def is_ignored(root: Path, rel: str) -> bool:
    result = run_git(root, "check-ignore", "-q", "--no-index", rel)
    return result.returncode == 0


def is_tracked(root: Path, rel: str) -> bool:
    result = run_git(root, "ls-files", "--error-unmatch", "--", rel)
    return result.returncode == 0


def count_commits_between(root: Path, older: str) -> int | None:
    result = run_git(root, "rev-list", "--count", f"{older}..HEAD")
    value = result.stdout.strip()
    if result.returncode != 0 or not value.isdigit():
        return None
    return int(value)


def has_authority_marker(graph: dict) -> bool:
    human = graph.get("humanView")
    if isinstance(human, dict) and human.get("derived") is True and human.get("notAuthoritative") is True:
        return True
    project = graph.get("project")
    if isinstance(project, dict) and "DERIVED" in str(project.get("description", "")):
        return True
    return False


def check_redlines(root: Path, failures: list, warnings: list) -> dict:
    evidence = {}

    # R5 流程与规则必须落盘（先判，因为它是"约束存在"本身）
    doc_path = root / PROCESS_DOC
    rule_path = root / RULE_FILE
    if not doc_path.is_file():
        failures.append(f"R5 缺失流程文档：{PROCESS_DOC}")
    else:
        text = doc_path.read_text(encoding="utf-8")
        missing = [m for m in DOC_MARKERS if m not in text]
        if missing:
            failures.append(f"R5 流程文档缺少红线标记 {missing}（被改写即视为约束失效，需显式修订）")
    if not rule_path.is_file():
        failures.append(f"R5 缺失角色规则：{RULE_FILE}")
    else:
        text = rule_path.read_text(encoding="utf-8")
        missing = [m for m in RULE_MARKERS if m not in text]
        if missing:
            failures.append(f"R5 角色规则缺少红线标记 {missing}")

    # R2 采集边界（凭据/二进制硬排除必须生效）
    ignore_path = root / IGNORE_FILE
    if not ignore_path.is_file():
        failures.append(f"R2 缺失采集边界文件：{IGNORE_FILE}（缺输入不得默认放行）")
    else:
        patterns = active_patterns(ignore_path.read_text(encoding="utf-8"))
        opened = [p for p in REQUIRED_IGNORE_PATTERNS + REQUIRED_SELF_PATTERNS if p not in patterns]
        if opened:
            failures.append(f"R2 凭据/自我递归排除被放开：{opened}")
        evidence["ignore_active_patterns"] = len(patterns)

    # R1 派生视图不得入库
    if is_tracked(root, GRAPH):
        failures.append(f"R1 派生视图被 git 跟踪：{GRAPH}（必须保持 gitignore）")
    elif not is_ignored(root, GRAPH):
        failures.append(f"R1 派生视图未被 git 忽略：{GRAPH}")

    # R3 + R4 产物必须自带非权威标记且结构自洽
    graph_path = root / GRAPH
    graph = None
    if not graph_path.is_file():
        warnings.append(f"F1 索引产物缺失：{GRAPH}（本机尚未建立索引，检索协议不可用）")
    else:
        graph = read_json(graph_path)
        if graph is None:
            failures.append(f"R4 索引产物无法解析：{GRAPH}")
        else:
            if not has_authority_marker(graph):
                failures.append(
                    "R3 索引产物缺少非权威标记（humanView.notAuthoritative / project.description 中的 DERIVED）"
                    "——重新生成后必须补回，禁止无声升格为权威事实"
                )
            nodes = graph.get("nodes") or []
            edges = graph.get("edges") or []
            layers = graph.get("layers") or []
            if not nodes or not layers:
                failures.append(f"R4 索引产物结构异常：nodes={len(nodes)} layers={len(layers)}")
            evidence["graph_nodes"] = len(nodes)
            evidence["graph_edges"] = len(edges)
            evidence["graph_layers"] = len(layers)

    return evidence


def check_freshness(root: Path, require: bool, max_drift: int, max_age_days: int, failures: list, warnings: list) -> dict:
    evidence = {"head": None, "recorded_commits": {}, "drift": {}}
    head = git_head(root)
    evidence["head"] = head

    # 严格模式的核心承诺：索引必须可用。缺输入不得默认放行（FAIL-2026-09-15-01）。
    graph_present = (root / GRAPH).is_file()
    if not graph_present and require:
        failures.append(f"F1 严格模式（--require）要求索引可用，但缺失：{GRAPH}")

    if head is None:
        warnings.append("F1 无法读取 HEAD（非 git 仓库或首次提交前），新鲜度不可判定")
        if require:
            failures.append("F1 严格模式（--require）下新鲜度不可判定即失败")
        return evidence

    sources = {"merge-meta.json": (MERGE_META, "gitsCommit"), "meta.json": (SCAN_META, "gitCommitHash")}
    graph_existed = graph_present
    for label, (rel, key) in sources.items():
        path = root / rel
        if not path.is_file():
            if graph_existed:
                warnings.append(f"F1 缺少新鲜度来源 {rel}，无法判定索引相对 HEAD 的漂移")
            continue
        payload = read_json(path)
        recorded = (payload or {}).get(key)
        if not recorded:
            warnings.append(f"F1 {rel} 未记录 {key}，无法判定漂移")
            continue
        evidence["recorded_commits"][label] = recorded
        if recorded == head:
            evidence["drift"][label] = 0
            continue
        drift = count_commits_between(root, recorded)
        if drift is None:
            warnings.append(f"F1 {rel} 记录的 commit {recorded[:8]} 不在当前历史中（已变基或跨仓）")
            evidence["drift"][label] = None
            continue
        evidence["drift"][label] = drift
        if drift > max_drift:
            message = f"F1 索引已过期：{label} 落后 HEAD {drift} 个提交（阈值 {max_drift}），需按 SOP 刷新"
            (failures if require else warnings).append(message)
        elif drift > 0:
            warnings.append(f"F1 索引轻微漂移：{label} 落后 HEAD {drift} 个提交（阈值内，收工声明 STALE({drift})）")

    for rel in (MERGE_META, SCAN_META):
        path = root / rel
        payload = read_json(path) if path.is_file() else None
        stamp = (payload or {}).get("mergedAt") or (payload or {}).get("lastAnalyzedAt")
        if not stamp:
            continue
        try:
            when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        age = (dt.datetime.now(dt.timezone.utc) - when).days
        evidence[f"age_days:{rel}"] = age
        if age > max_age_days:
            message = f"F1 索引已过期：{rel} 生成于 {age} 天前（阈值 {max_age_days} 天），需按 SOP 刷新"
            (failures if require else warnings).append(message)

    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="代码事实索引红线门禁（GOV-CFI-001）")
    parser.add_argument("--root", default=None, help="门禁根目录，默认仓库根（供变异测试注入用）")
    parser.add_argument("--require", action="store_true", help="严格模式：索引缺失/过期亦判失败")
    parser.add_argument("--max-drift", type=int, default=DEFAULT_MAX_DRIFT)
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    parser.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    failures: list = []
    warnings: list = []

    evidence = check_redlines(root, failures, warnings)
    evidence.update(check_freshness(root, args.require, args.max_drift, args.max_age_days, failures, warnings))

    result = {
        "gate": "ua_index_gate",
        "process": "GOV-CFI-001",
        "root": str(root),
        "require": args.require,
        "status": "FAIL" if failures else ("WARN" if warnings else "PASS"),
        "failures": failures,
        "warnings": warnings,
        "evidence": evidence,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in failures:
            print(f"FAIL: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        print(f"ua_index_gate: {result['status']} (nodes={evidence.get('graph_nodes')}, drift={evidence.get('drift')})")

    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
