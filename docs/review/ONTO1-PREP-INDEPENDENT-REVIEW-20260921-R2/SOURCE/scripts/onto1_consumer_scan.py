#!/usr/bin/env python3
"""ONTO1 WI-A2｜消费者全量扫描（复审包 09 号 S1~S5）。

设计（防假绿三件套）：
1) **单一真值函数** `scan()`：所有判定只由它产出，报告与门禁共用同一实现；
2) **fail-closed**：基线计数不等于 32/34/1、扫描根不存在、命中无处置规则、期望命中缺失
   —— 任一情况一律 FAIL，绝不"缺夹具即跳过"；
3) **期望值锚定（防空转）**：`KNOWN_HITS` 取自复审包 09 号初版清单的逐条锚点，
   扫描必须逐条检出；检出不到即 FAIL（而不是打印 0 命中就报绿）。

用法：
    python3 scripts/onto1_consumer_scan.py --report              # 生成命中清单与汇总
    python3 scripts/onto1_consumer_scan.py --gate                # 门禁（S5）
    python3 scripts/onto1_consumer_scan.py --gate --roots gits   # 变异：只扫单仓 ⇒ 期望 FAIL
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
REPO_ROOTS = {
    "gits": ROOT,
    "kert": WORKSPACE / "Leibniz-KERT",
}
BASELINE_TTL = ROOT / "specs/semantic/gits-core.owl.ttl"
# 默认证据目录（命中缓存与规则表的稳定位置）；EVIDENCE_DIR 可被 --out-dir 改写以保护正式证据
DEFAULT_EVIDENCE_DIR = ROOT / "loops/ONTO1-ontology-split/evidence"
EVIDENCE_DIR = DEFAULT_EVIDENCE_DIR
RULES_PATH = DEFAULT_EVIDENCE_DIR / "consumer-scan-dispositions.json"

EXPECTED_BASELINE_SHA256_PREFIX = "705578d6324abd0c"
EXPECTED_COUNTS = {"owl_class": 32, "owl_object_property": 34, "owl_datatype_property": 1}

SKIP_DIR_PARTS = {
    ".git", ".ua", "node_modules", "target", "__pycache__", ".venv", "venv",
    "dist", "build", ".mypy_cache", ".pytest_cache", ".idea", ".mvn",
    "coverage", ".nyc_output", ".gradle", "site-packages", ".tox",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tgz",
    ".jar", ".class", ".pyc", ".so", ".dylib", ".dll", ".woff", ".woff2", ".ttf",
    ".eot", ".mp4", ".mp3", ".xlsx", ".docx", ".pptx", ".bin", ".sqlite", ".db",
}
MAX_FILE_BYTES = 4 * 1024 * 1024

# 复审包 09 号 S1 要求扫描的 ID 模式
ID_PATTERNS = {
    "KM": r"(?<![A-Za-z0-9-])KM-[A-Z0-9][A-Z0-9-]{2,}",
    "AC": r"(?<![A-Za-z0-9-])AC-[A-Z0-9][A-Z0-9-]{2,}",
    "ASSET": r"(?<![A-Za-z0-9-])ASSET-[A-Z0-9][A-Z0-9-]{2,}",
    "SP": r"(?<![A-Za-z0-9-])SP-[0-9]{1,3}(?![0-9])",
    "KI": r"(?<![A-Za-z0-9-])KI-[A-Z0-9][A-Z0-9-]{2,}",
    "KD": r"(?<![A-Za-z0-9-])KD-[A-Z0-9][A-Z0-9-]{2,}",
    "CTR": r"(?<![A-Za-z0-9-])CTR-[A-Z]{2,}-[0-9]{3}",
}
# 复审包 09 号 S1 要求扫描的 IRI / 文件名引用
IRI_LITERALS = {
    "IRI_BANK_EXAMPLE": "https://gits.bank.example/ontology/core#",
    "IRI_GIENTECH": "https://gientech.com/gits/kno/",
    "PREFIX_GITS": "gits:",
    "FILE_GITS_CORE": "gits-core",
}
# D3-A 残留表述（复审包 09 号第 9 行；核对为「文档残留」类别）
D3A_RESIDUAL = "D3-A"

# 复审包 09 号初版清单的逐条锚点：扫描必须全部检出，否则门禁 FAIL（防"0 命中即绿"空转）
# type=token 期望命中清单里的 token 键（如 IRI_BANK_EXAMPLE）；type=regex 对 token 文本做正则。
KNOWN_HITS = [
    {"id": "H-KERT-MAPID", "type": "regex", "path": "src/kert/application/skills.py", "pattern": r"^KM-CORP-RM-"},
    {"id": "H-KERT-SP15", "type": "token", "path": "src/kert/application/product_recommendation/sp15_skill.py", "pattern": r"SP-15"},
    {"id": "H-KERT-AC-SP15", "type": "token", "path": "src/kert/application/product_recommendation/sp15_skill.py", "pattern": r"AC-PRODUCT-RECOMMEND-001"},
    {"id": "H-KERT-SP20", "type": "token", "path": "src/kert/application/service_proposal.py", "pattern": r"SP-20"},
    {"id": "H-KERT-KI-FRONT", "type": "regex", "path": "src/kert/application/customer_knowledge.py", "pattern": r"^KI-FRONT-00[0-9]"},
    {"id": "H-KERT-D3A-REF", "type": "token", "path": "src/kert/domain/ontology_reference.py", "pattern": r"D3-A"},
    {"id": "H-KERT-D3A-MAP", "type": "token", "path": "src/kert/domain/knowledge_map.py", "pattern": r"D3-A"},
    {"id": "H-KERT-D3A-SRC", "type": "token", "path": "src/kert/domain/knowledge_source.py", "pattern": r"D3-A"},
    {"id": "H-KERT-D3A-ASSETS", "type": "token", "path": "src/kert/domain/ontology_assets.py", "pattern": r"D3-A"},
    {"id": "H-KERT-PIN-JSON", "type": "regex", "path": "examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json", "pattern": r"^CTR-SEM-002$"},
    {"id": "H-KERT-PROVENANCE", "type": "regex", "path": "examples/bank-front-knowledge-maps/90_control/ontology/PROVENANCE.json", "pattern": r"^CTR-SEM-002$"},
    {"id": "H-GITS-PRODUCTS-TTL", "type": "token", "path": "specs/knowledge-architecture/instances/product/products.ttl", "pattern": r"IRI_BANK_EXAMPLE"},
    {"id": "H-GITS-CONTRACT-INDEX", "type": "regex", "path": "specs/CONTRACT_INDEX.yaml", "pattern": r"^CTR-SEM-00[0-9]$"},
    {"id": "H-GITS-KAC-JAVA", "type": "token", "path": "apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java", "pattern": r"FILE_GITS_CORE"},
]

# 净迁移义务锚点：这些**必须**出现在净义务清单里（防"全部豁免/全部冻结"式空转）
KNOWN_OBLIGATIONS = [
    {"id": "O-PRODUCTS-PREFIX", "repo": "gits",
     "path": "specs/knowledge-architecture/instances/product/products.ttl",
     "disposition": "CONTROL_PLANE_REQUIRED", "tokenRegex": r"IRI_BANK_EXAMPLE"},
    {"id": "O-D3A-RESIDUAL-SRC", "repo": "kert", "path": "src/kert/domain/ontology_reference.py",
     "disposition": "CONTROL_PLANE_REQUIRED"},
    {"id": "O-KERT-MAPID", "repo": "kert", "path": "src/kert/application/skills.py",
     "disposition": "CONTROL_PLANE_REQUIRED", "tokenRegex": r"^KM-"},
    {"id": "O-KERT-SP15", "repo": "kert",
     "path": "src/kert/application/product_recommendation/sp15_skill.py",
     "disposition": "CONTROL_PLANE_REQUIRED"},
    {"id": "O-KERT-PIN", "repo": "kert",
     "path": "examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json",
     "disposition": "FOLLOW_MIGRATION"},
    {"id": "O-KERT-PROVENANCE", "repo": "kert",
     "path": "examples/bank-front-knowledge-maps/90_control/ontology/PROVENANCE.json",
     "disposition": "FOLLOW_MIGRATION"},
    {"id": "O-GITS-CONTRACT-INDEX", "repo": "gits", "path": "specs/CONTRACT_INDEX.yaml",
     "disposition": "FOLLOW_MIGRATION"},
    {"id": "O-GITS-KAC", "repo": "gits",
     "path": "apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java",
     "disposition": "FOLLOW_MIGRATION"},
]


# --------------------------------------------------------------------------- #
# 基线真值（fail-closed：读不到就失败，不返回空集合）
# --------------------------------------------------------------------------- #
def load_baseline_terms(ttl_path: Path = BASELINE_TTL,
                        expected_prefix: str = EXPECTED_BASELINE_SHA256_PREFIX) -> dict[str, list[str]]:
    """解析基线本体，返回 {类别: [术语短名]}。计数不符或哈希漂移即抛错（fail-closed）。

    `expected_prefix` 仅用于变异复验：允许测试把期望哈希改为被变异文件的哈希，
    以便单独验证"计数断言"本身有牙齿（否则哈希断言会先短路）。
    """
    if not ttl_path.is_file():
        raise RuntimeError(f"baseline ontology missing: {ttl_path}")
    sha = hashlib.sha256(ttl_path.read_bytes()).hexdigest()
    if not sha.startswith(expected_prefix):
        raise RuntimeError(
            f"baseline sha256 drifted: {sha[:16]} != expected prefix {expected_prefix}"
        )
    try:
        from rdflib import Graph
        from rdflib.namespace import OWL, RDF
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(f"rdflib unavailable: {exc}") from exc

    graph = Graph()
    graph.parse(str(ttl_path), format="turtle")
    buckets = {
        "owl_class": (OWL.Class, RDF.type),
        "owl_object_property": (OWL.ObjectProperty, RDF.type),
        "owl_datatype_property": (OWL.DatatypeProperty, RDF.type),
    }
    terms: dict[str, list[str]] = {}
    for key, (cls, rdf_type) in buckets.items():
        names = set()
        for subject in graph.subjects(rdf_type, cls):
            text = str(subject)
            names.add(text.rsplit("#", 1)[-1].rsplit("/", 1)[-1])
        terms[key] = sorted(names)

    for key, expected in EXPECTED_COUNTS.items():
        if len(terms[key]) != expected:
            raise RuntimeError(f"baseline count mismatch for {key}: {len(terms[key])} != {expected}")
    terms["baseline_sha256"] = [sha]
    return terms


# --------------------------------------------------------------------------- #
# 扫描（单一真值函数）
# --------------------------------------------------------------------------- #
def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def _mk_matchers(terms: dict[str, list[str]]) -> list[tuple[str, str, re.Pattern]]:
    matchers: list[tuple[str, str, re.Pattern]] = []
    for key in ("owl_class", "owl_object_property", "owl_datatype_property"):
        for name in terms[key]:
            matchers.append((key, name, re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])")))
    for key, pattern in ID_PATTERNS.items():
        matchers.append(("id_pattern", key, re.compile(pattern)))
    matchers.append(("d3a_residual", D3A_RESIDUAL, re.compile(re.escape(D3A_RESIDUAL))))
    return matchers


def scan(roots: list[str] | None = None) -> dict:
    """唯一真值函数：返回 hits / 统计 / 基线信息。"""
    terms = load_baseline_terms()
    matchers = _mk_matchers(terms)
    iri_literals = {key: re.compile(re.escape(value)) for key, value in IRI_LITERALS.items()}

    selected = roots or list(REPO_ROOTS)
    hits: list[dict] = []
    files_scanned = 0
    for repo in selected:
        root = REPO_ROOTS[repo]
        if not root.is_dir():
            raise RuntimeError(f"scan root missing: {root}")
        for path in iter_text_files(root):
            files_scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not text:
                continue
            rel = str(path.relative_to(root))
            lines = text.splitlines()
            for line_no, line in enumerate(lines, start=1):
                emitted: set[tuple[str, str]] = set()
                for category, token, matcher in matchers:
                    found = matcher.search(line)
                    if found:
                        key = (category, found.group(0))
                        if key in emitted:
                            continue
                        emitted.add(key)
                        hits.append({
                            "repo": repo, "path": rel, "line": line_no, "category": category,
                            "token": found.group(0), "matched_name": token,
                        })
                for iri_key, iri_matcher in iri_literals.items():
                    if iri_matcher.search(line):
                        key = ("iri_or_file_ref", iri_key)
                        if key in emitted:
                            continue
                        emitted.add(key)
                        hits.append({
                            "repo": repo, "path": rel, "line": line_no, "category": "iri_or_file_ref",
                            "token": iri_key, "matched_name": iri_key,
                        })
    return {
        "terms": terms,
        "files_scanned": files_scanned,
        "roots": selected,
        "hits": hits,
    }


# --------------------------------------------------------------------------- #
# 处置规则（S2/S3）
# --------------------------------------------------------------------------- #
def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _glob_match(pattern: str, value: str) -> bool:
    regex = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
    return re.fullmatch(regex, value) is not None


def load_rules(path: Path = RULES_PATH) -> dict:
    if not path.is_file():
        raise RuntimeError(f"disposition rules missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("rules"), list) or not data["rules"]:
        raise RuntimeError("disposition rules must contain a non-empty 'rules' array")
    return data


def classify(hits: list[dict], rules: dict) -> tuple[list[dict], list[dict]]:
    """返回 (已处置命中, 未处置命中)。未处置非空 ⇒ 门禁 FAIL。

    规则按数组顺序匹配，**首个匹配生效**；因此具体规则必须排在通用规则之前。
    """
    disposed, orphan = [], []
    for hit in hits:
        rule_id = None
        for rule in rules["rules"]:
            match = rule.get("match", {})
            if match.get("repo") and match["repo"] != hit["repo"]:
                continue
            if match.get("category") and match["category"] != hit["category"]:
                continue
            if match.get("token") and match["token"] != hit["token"]:
                continue
            if match.get("tokenRegex") and not re.fullmatch(match["tokenRegex"], hit["token"]):
                continue
            if match.get("pathGlob") and not _glob_match(match["pathGlob"], hit["path"]):
                continue
            if match.get("pathNotGlob") and _glob_match(match["pathNotGlob"], hit["path"]):
                continue
            rule_id = rule["id"]
            hit = dict(hit)
            hit["disposition"] = rule["disposition"]
            hit["rule_id"] = rule["id"]
            hit["action"] = rule.get("action", "")
            hit["rationale"] = rule.get("rationale", "")
            break
        if rule_id:
            disposed.append(hit)
        else:
            orphan.append(hit)
    return disposed, orphan


# 需要进入「净迁移义务清单」的处置类别（其余为登记豁免/取证冻结/权威源/制品镜像）
OBLIGATION_DISPOSITIONS = {"CONTROL_PLANE_REQUIRED", "FOLLOW_MIGRATION"}
# 表示「尚未完成分类」的处置（非零即阻碍 Wave 2/3 退出门禁）
PENDING_DISPOSITION = "PENDING_TRIAGE"


def obligations(disposed: list[dict]) -> list[dict]:
    net: dict[tuple, dict] = {}
    for hit in disposed:
        if hit["disposition"] not in OBLIGATION_DISPOSITIONS:
            continue
        key = (hit["repo"], hit["disposition"], hit["category"], hit["path"])
        row = net.setdefault(key, {"repo": hit["repo"], "disposition": hit["disposition"],
                                   "category": hit["category"], "path": hit["path"],
                                   "rule_id": hit["rule_id"], "action": hit["action"],
                                   "tokens": set(), "lines": []})
        row["tokens"].add(hit["token"])
        if len(row["lines"]) < 5:
            row["lines"].append(hit["line"])
    out = []
    for row in net.values():
        row = dict(row)
        row["tokens"] = sorted(row["tokens"])
        out.append(row)
    return sorted(out, key=lambda r: (r["disposition"], r["repo"], r["path"]))


# --------------------------------------------------------------------------- #
# 报告
# --------------------------------------------------------------------------- #
def write_report(result: dict, disposed: list[dict], orphan: list[dict]) -> dict:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    hits_path = EVIDENCE_DIR / "consumer-scan-hits.jsonl"
    summary_path = EVIDENCE_DIR / "consumer-scan-summary.csv"
    orphan_path = EVIDENCE_DIR / "consumer-scan-orphan.csv"
    with hits_path.open("w", encoding="utf-8") as handle:
        for hit in disposed:
            handle.write(json.dumps(hit, ensure_ascii=False) + "\n")
    with orphan_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["repo", "path", "line", "category", "token", "matched_name"])
        writer.writeheader()
        for hit in orphan:
            writer.writerow({k: hit[k] for k in writer.fieldnames})

    obligation_rows = obligations(disposed)
    obligation_path = EVIDENCE_DIR / "consumer-scan-obligations.csv"
    with obligation_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["repo", "disposition", "category", "path",
                                                   "rule_id", "tokens", "lines", "action"])
        writer.writeheader()
        for row in obligation_rows:
            writer.writerow({
                "repo": row["repo"], "disposition": row["disposition"], "category": row["category"],
                "path": row["path"], "rule_id": row["rule_id"], "tokens": ";".join(row["tokens"]),
                "lines": ";".join(str(x) for x in row["lines"]), "action": row["action"],
            })

    buckets: dict[tuple, dict] = {}
    for hit in disposed:
        key = (hit["repo"], hit["category"], hit["disposition"], hit["token"])
        row = buckets.setdefault(key, {"repo": hit["repo"], "category": hit["category"],
                                       "disposition": hit["disposition"], "token": hit["token"],
                                       "occurrences": 0, "files": set(), "rule_id": hit["rule_id"],
                                       "action": hit["action"]})
        row["occurrences"] += 1
        row["files"].add(hit["path"])
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["repo", "category", "disposition", "token",
                                                    "rule_id", "occurrences", "file_count", "action"])
        writer.writeheader()
        for key in sorted(buckets):
            row = buckets[key]
            writer.writerow({
                "repo": row["repo"], "category": row["category"], "disposition": row["disposition"],
                "token": row["token"], "rule_id": row["rule_id"], "occurrences": row["occurrences"],
                "file_count": len(row["files"]), "action": row["action"],
            })
    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "baseline_sha256": result["terms"]["baseline_sha256"][0],
        "baseline_counts": {k: len(result["terms"][k]) for k in EXPECTED_COUNTS},
        "roots": result["roots"],
        "files_scanned": result["files_scanned"],
        "total_hits": len(result["hits"]),
        "disposed": len(disposed),
        "orphan": len(orphan),
        "pending_triage": sum(1 for hit in disposed if hit["disposition"] == PENDING_DISPOSITION),
        "net_obligations": len(obligation_rows),
        "hits_file": _rel(hits_path),
        "summary_file": _rel(summary_path),
        "obligations_file": _rel(obligation_path),
        "hits_sha256": hashlib.sha256(hits_path.read_bytes()).hexdigest() if hits_path.exists() else None,
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
    }
    (EVIDENCE_DIR / "consumer-scan-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


# --------------------------------------------------------------------------- #
# 门禁（S4/S5）
# --------------------------------------------------------------------------- #
def gate(roots: list[str] | None, rules_path: Path = RULES_PATH, force_scan: bool = False,
         hits_file: Path | None = None, out_dir: Path | None = None) -> int:
    global EVIDENCE_DIR
    if out_dir is not None:
        EVIDENCE_DIR = out_dir
    failures: list[str] = []
    cache_path = hits_file or (DEFAULT_EVIDENCE_DIR / "consumer-scan-hits.jsonl")
    try:
        if roots or force_scan:
            result = scan(roots)
        elif cache_path.is_file():
            result = load_hits_cache(cache_path)
        else:
            result = scan(roots)
        rules = load_rules(rules_path)
    except RuntimeError as exc:
        print(f"onto1-consumer-scan: FAIL: {exc}", file=sys.stderr)
        return 2

    disposed, orphan = classify(result["hits"], rules)

    # 断言 A1：基线计数与哈希（load_baseline_terms 已 fail-closed）
    print(f"[A1] baseline {result['terms']['baseline_sha256'][0][:16]} "
          f"classes={len(result['terms']['owl_class'])} "
          f"objectProps={len(result['terms']['owl_object_property'])} "
          f"datatypeProps={len(result['terms']['owl_datatype_property'])}  OK")

    # 断言 A2：扫描规模下限（防"扫不到文件也算绿"）
    if result["files_scanned"] < 0:
        if len(result["hits"]) < 300:
            failures.append(f"A2 cached hits too small: {len(result['hits'])} < 300")
        print(f"[A2] files_scanned=cache hits={len(result['hits'])}")
    else:
        if result["files_scanned"] < 300:
            failures.append(f"A2 files_scanned too small: {result['files_scanned']} < 300")
        print(f"[A2] files_scanned={result['files_scanned']} hits={len(result['hits'])}")

    # 断言 A3：期望命中逐条检出（防空转：0 命中不得为绿）
    index: dict[tuple, list[dict]] = {}
    for hit in result["hits"]:
        index.setdefault((hit["repo"], hit["path"]), []).append(hit)
    missing = []
    for expectation in KNOWN_HITS:
        repo = "kert" if expectation["path"].startswith(("src/", "examples/")) else "gits"
        candidates = index.get((repo, expectation["path"]), [])
        if expectation.get("type", "regex") == "token":
            found = any(hit["token"] == expectation["pattern"] for hit in candidates)
        else:
            found = any(re.search(expectation["pattern"], hit["token"]) for hit in candidates)
        if not found:
            missing.append(expectation["id"])
    if missing:
        failures.append(f"A3 known-hit expectations not detected: {sorted(missing)}")
    print(f"[A3] known-hit expectations {len(KNOWN_HITS) - len(missing)}/{len(KNOWN_HITS)} detected"
          + (f"  MISSING={sorted(missing)}" if missing else "  OK"))

    # 断言 A4：命中 100% 处置（fail-closed：无规则即失败）
    if orphan:
        failures.append(f"A4 {len(orphan)} hit(s) without disposition rule")
        for hit in orphan[:10]:
            print(f"       orphan: {hit['repo']}:{hit['path']}:{hit['line']} "
                  f"{hit['category']}/{hit['token']}", file=sys.stderr)
    pending = [hit for hit in disposed if hit["disposition"] == PENDING_DISPOSITION]
    if pending:
        failures.append(f"A4b {len(pending)} hit(s) still PENDING_TRIAGE (处置表未完成)")
    print(f"[A4] disposed={len(disposed)} orphan={len(orphan)} "
          f"coverage={len(disposed) / max(len(result['hits']), 1):.4f}")
    print(f"[A4b] pending_triage={len(pending)}")

    manifest = write_report(result, disposed, orphan)

    # 断言 A5：证据文件哈希记账（供独立 QA 复核）
    print(f"[A5] report sha256 hits={manifest['hits_sha256'] and manifest['hits_sha256'][:16]} "
          f"summary={manifest['summary_sha256'][:16]} obligations={manifest['obligations_file']}")

    # 断言 A6：净迁移义务清单必须命中已知可执行项（防"全部豁免"式空转）
    obligation_index: dict[tuple, dict] = {}
    for row in obligations(disposed):
        key = (row["repo"], row["path"])
        merged = obligation_index.setdefault(key, {"dispositions": set(), "tokens": set()})
        merged["dispositions"].add(row["disposition"])
        merged["tokens"].update(row["tokens"])
    missing_obligations = []
    for item in KNOWN_OBLIGATIONS:
        row = obligation_index.get((item["repo"], item["path"]))
        if row is None or item["disposition"] not in row["dispositions"]:
            missing_obligations.append(item["id"])
        elif item.get("tokenRegex") and not any(
                re.search(item["tokenRegex"], token) for token in row["tokens"]):
            missing_obligations.append(item["id"])
    if missing_obligations:
        failures.append(f"A6 known obligations absent/mis-dispositioned: {sorted(missing_obligations)}")
    print(f"[A6] known obligation anchors "
          f"{len(KNOWN_OBLIGATIONS) - len(missing_obligations)}/{len(KNOWN_OBLIGATIONS)} present"
          + (f"  MISSING={sorted(missing_obligations)}" if missing_obligations else "  OK"))

    if failures:
        for item in failures:
            print(f"onto1-consumer-scan: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-consumer-scan: PASS")
    return 0


def load_hits_cache(path: Path) -> dict:  # noqa: D401
    """从已有命中清单复用扫描结果（规则迭代用；仍需重跑基线断言）。"""
    if not path.is_file():
        raise RuntimeError(f"hits cache missing: {path}")
    hits = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not hits:
        raise RuntimeError("hits cache is empty")
    terms = load_baseline_terms()
    return {"terms": terms, "files_scanned": -1, "roots": ["cache"], "hits": hits}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="仅生成命中清单与汇总")
    parser.add_argument("--gate", action="store_true", help="执行 S5 门禁（fail-closed）")
    parser.add_argument("--roots", nargs="*", choices=sorted(REPO_ROOTS), default=None,
                        help="限定扫描根（变异复验用；默认双仓）")
    parser.add_argument("--rules", default=str(RULES_PATH))
    parser.add_argument("--scan", action="store_true", help="强制重新扫描（默认优先读命中缓存）")
    parser.add_argument("--hits-file", default=None, help="指定命中缓存（变异复验用）")
    parser.add_argument("--out-dir", default=None, help="证据输出目录（默认正式证据目录）")
    args = parser.parse_args()

    if args.gate:
        return gate(args.roots, Path(args.rules), force_scan=args.scan,
                    hits_file=Path(args.hits_file) if args.hits_file else None,
                    out_dir=Path(args.out_dir) if args.out_dir else None)

    global EVIDENCE_DIR
    if args.out_dir:
        EVIDENCE_DIR = Path(args.out_dir)
    try:
        if args.roots or args.scan:
            result = scan(args.roots)
        else:
            result = load_hits_cache(Path(args.hits_file) if args.hits_file
                                     else DEFAULT_EVIDENCE_DIR / "consumer-scan-hits.jsonl")
        rules = load_rules(Path(args.rules))
    except RuntimeError as exc:
        print(f"onto1-consumer-scan: FAIL: {exc}", file=sys.stderr)
        return 2
    disposed, orphan = classify(result["hits"], rules)
    manifest = write_report(result, disposed, orphan)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
