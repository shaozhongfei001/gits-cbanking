#!/usr/bin/env python3
"""GK17 / WP3.1 -- 产品卡 front matter -> RDF（确定性投影，fail-closed）

裁定依据：docs/architecture/GK17-WP1.3-产品关系权威归属裁定-V1.0.md
  - 关系**类型**权威 = 本体（gits:requiresProduct / mutuallyExclusiveWith / complementsProduct）
  - 关系**实例**权威 = 产品卡（本脚本的输入）
  - 投影**单向**：产品卡 -> 本体个体（本脚本的输出，本体侧只读）

本脚本**不得**承载"关系类型"的定义，只做投影；也**不得**静默丢弃任何关系实例。

用法：
  python3 scripts/gk17_prodcard_to_rdf.py --root . --cards-dir <路径> [--out-dir <路径>]
      [--id-map <文件>] [--allow-unresolved] [--verify-determinism] [--json]

退出码：
  0 = 投影完成且所有引用可解析（或已显式 --allow-unresolved）
  2 = 存在无法解析的引用（strict 默认，fail-closed）
  3 = 输入缺失 / 解析失败
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

# ── 版本化投影配置（命名空间 / 关系字段 / 别名映射）───────────────────────────
# 2026-09-21 Owner 授权整改（c-2 生成器根因）：**命名空间分离**——
#   `gits:` → 本体术语命名空间（类 / 属性）；`prod:` → SIM 产品实例命名空间。
# 命名空间与关系字段**一律从配置读取**，不在此硬编码（见 projection-config.json）。
DEFAULT_CONFIG = "specs/knowledge-architecture/instances/product/projection-config.json"
DEFAULT_RELATION_FIELDS = {
    "prerequisite_product_ids": "requiresProduct",
    "mutex_product_ids": "mutuallyExclusiveWith",
    "complementary_products": "complementsProduct",
}


def load_config(path: Path) -> dict:
    """载入版本化配置；缺文件即 fail-closed（绝不静默沿用旧口径）。"""
    if not path.is_file():
        raise ValueError(f"投影配置缺失：{path}")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    ns = cfg["namespaces"]
    terms, inst = ns["terms"], ns["instances"]
    cfg["_terms_prefix"] = terms["prefix"]
    cfg["_inst_prefix"] = inst["prefix"]
    cfg["_prefixes"] = (
        f"@prefix {terms['prefix']}: <{terms['iri']}> .\n"
        f"@prefix {inst['prefix']}: <{inst['iri']}> .\n"
        '@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n'
        '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
        '@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .\n'
    )
    cfg.setdefault("relationFields", dict(DEFAULT_RELATION_FIELDS))
    return cfg


# ── front matter 极简解析（纯 stdlib；只取顶层标量与行内列表，块状嵌套一律跳过）──
def split_front_matter(text: str) -> str:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        raise ValueError("front matter 缺失（文件未以 --- 开头）")
    return m.group(1)


def top_level_scalar(fm: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    return m.group(1).strip()


def scalar(v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    if v in ("", "null", "~"):
        return None
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def inline_list(v: str | None) -> list[str]:
    if v is None:
        return []
    v = v.strip()
    if not v.startswith("["):
        return []
    inner = v[1:-1].strip()
    if not inner:
        return []
    return [scalar(x) or "" for x in inner.split(",") if x.strip()]


def read_card(path: Path, relation_fields: dict[str, str] | None = None) -> dict:
    fields = relation_fields or DEFAULT_RELATION_FIELDS
    fm = split_front_matter(path.read_text(encoding="utf-8"))
    return {
        "file": path.name,
        "product_id": scalar(top_level_scalar(fm, "product_id")),
        "name": scalar(top_level_scalar(fm, "name")),
        "product_family": scalar(top_level_scalar(fm, "product_family")),
        "version": scalar(top_level_scalar(fm, "version")),
        "status": scalar(top_level_scalar(fm, "status")),
        "relations": {
            field: sorted({x for x in inline_list(top_level_scalar(fm, field)) if x})
            for field in fields
        },
    }


def load_id_map(path: Path | None) -> dict[str, str]:
    """显式身份映射：符名 -> PROD-* ID。仅接受指向真实存在卡片的映射。"""
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping = data.get("mappings", data)
    if not isinstance(mapping, dict):
        raise ValueError("id-map 必须是 {符名: PROD-ID} 或 {\"mappings\": {...}}")
    return mapping


def collect_cards(cards_dirs: list[Path], relation_fields: dict[str, str] | None = None) -> list[dict]:
    found: list[Path] = []
    for d in cards_dirs:
        if not d.exists():
            continue
        found.extend(sorted(d.rglob("product-cards/*.md")))
    cards = [read_card(p, relation_fields) for p in found]
    for c in cards:
        if not c["product_id"]:
            raise ValueError(f"{c['file']}: product_id 缺失")
    return sorted(cards, key=lambda c: c["product_id"])


def ttl_literal(s: str | None) -> str | None:
    if s is None:
        return None
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(cards: list[dict], id_map: dict[str, str], cfg: dict) -> tuple[str, list[dict]]:
    """返回 (turtle, unresolved)。unresolved 逐条记录来源卡与字段，绝不静默丢弃。

    命名空间来自**版本化配置**：实例 `prod:`（SIM 产品实例），术语 `gits:`（类 / 属性）。
    """
    known = {c["product_id"]: c for c in cards}
    inst = cfg["_inst_prefix"]
    term = cfg["_terms_prefix"]
    ptype = cfg.get("productType") or f"{term}:Product"
    lines: list[str] = [cfg["_prefixes"].rstrip(), ""]
    unresolved: list[dict] = []

    lines.append("# W3.1 投影产物：产品个体（身份空间 PROD-*）。")
    lines.append(f"# 命名空间：{term}: = 本体术语（类/属性）；{inst}: = SIM 产品实例；"
                 f"配置版本 {cfg.get('version', 'n/a')}。")
    lines.append("# 关系实例源自产品卡 front matter；关系类型定义在本体，本文件不复述。")
    lines.append("")

    for c in cards:
        subj = f"{inst}:{c['product_id'].lower().replace('-', '_')}"
        lines.append(f"{subj}")
        lines.append(f"  a {ptype} ;")
        label = ttl_literal(c["name"])
        if label:
            lines.append(f"  rdfs:label {label} ;")
        lines.append(f"  rdfs:comment \"source card: {c['file']}\" .")
        lines.append("")

    # 关系：只有目标解析到已存在的产品个体才可写；否则逐条记入 unresolved
    for c in cards:
        subj = f"{inst}:{c['product_id'].lower().replace('-', '_')}"
        for field, prop in cfg["relationFields"].items():
            for target in c["relations"][field]:
                resolved = id_map.get(target, target)
                if resolved not in known:
                    unresolved.append({
                        "card": c["file"],
                        "card_product_id": c["product_id"],
                        "field": field,
                        "ontology_property": prop,
                        "referenced_symbol": target,
                        "resolved_to": resolved,
                        "reason": "referenced product has no product card in the supplied card set",
                    })
                    continue
                obj = f"{inst}:{resolved.lower().replace('-', '_')}"
                lines.append(f"{subj} {term}:{prop} {obj} .")

    if unresolved:
        lines.append("")
        lines.append("# 以下引用无法解析，未写入 A-Box（逐条见 UNRESOLVED.json），按裁定 fail-closed 处理。")
        for u in sorted(unresolved, key=lambda x: (x["card"], x["field"], x["referenced_symbol"])):
            lines.append(f"#   {u['card']} [{u['field']}] -> {u['referenced_symbol']}")

    text = "\n".join(lines).rstrip() + "\n"
    return text, unresolved


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--cards-dir", action="append", default=[])
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--id-map", default=None)
    ap.add_argument("--config", default=None,
                    help=f"版本化投影配置路径（默认 {DEFAULT_CONFIG}，相对 --root）")
    ap.add_argument("--allow-unresolved", action="store_true")
    ap.add_argument("--verify-determinism", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir) if args.out_dir else root / "specs/knowledge-architecture/instances/product"

    cfg_path = Path(args.config) if args.config else Path(DEFAULT_CONFIG)
    if not cfg_path.is_absolute():
        cfg_path = root / cfg_path
    try:
        cfg = load_config(cfg_path)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 3

    cards_dirs = [Path(d) for d in args.cards_dir]
    if not cards_dirs:
        default = root / "examples/product-recommendation-assets/03_core"
        cards_dirs = [default]
    # 允许把相对路径按 --root 解析
    cards_dirs = [d if d.is_absolute() else (root / d) for d in cards_dirs]

    try:
        cards = collect_cards(cards_dirs, cfg["relationFields"])
    except (ValueError, OSError) as exc:
        print(f"INPUT ERROR: {exc}", file=sys.stderr)
        return 3
    if not cards:
        print(f"INPUT ERROR: 在 {[str(d) for d in cards_dirs]} 下未找到任何 product-cards/*.md", file=sys.stderr)
        return 3

    id_map = load_id_map(Path(args.id_map)) if args.id_map else {}
    unknown_map = sorted(set(id_map.values()) - {c["product_id"] for c in cards})
    if unknown_map:
        print(f"INPUT ERROR: id-map 目标不是本卡集中的产品: {unknown_map}", file=sys.stderr)
        return 3

    ttl, unresolved = render(cards, id_map, cfg)

    products_ttl = ttl
    relation_count = sum(
        len([t for t in c["relations"][f] if id_map.get(t, t) in {x["product_id"] for x in cards}])
        for c in cards for f in cfg["relationFields"]
    )

    if args.verify_determinism:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.ttl"
            b = Path(tmp) / "b.ttl"
            write_atomic(a, ttl)
            # 重跑一次完整流程（含解析）以证明逐字节一致
            again, _ = render(collect_cards(cards_dirs, cfg["relationFields"]), id_map, cfg)
            write_atomic(b, again)
            same = a.read_bytes() == b.read_bytes()
            sha = hashlib.sha256(a.read_bytes()).hexdigest()
            print(f"determinism: {'IDENTICAL' if same else 'DIFFERENT'} sha256={sha}")
            if not same:
                return 2

    write_atomic(out_dir / "products.ttl", products_ttl)
    report = {
        "projectionConfig": {
            "file": str(cfg_path),
            "version": cfg.get("version"),
            "sha256": hashlib.sha256(cfg_path.read_bytes()).hexdigest(),
            "namespaces": cfg["namespaces"],
            "simulationOnly": cfg.get("simulationOnly", False),
        },
        "cardFiles": [c["file"] for c in cards],
        "productIndividuals": len(cards),
        "productIds": [c["product_id"] for c in cards],
        "relationInstances": relation_count,
        "unresolvedReferenceCount": len(unresolved),
        "unresolved": sorted(unresolved, key=lambda x: (x["card"], x["field"], x["referenced_symbol"])),
        "relationTypeAuthority": "ontology (gits-core.owl.ttl)",
        "relationInstanceAuthority": "product cards (this projection's input)",
    }
    write_atomic(out_dir / "UNRESOLVED.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"产品个体 = {len(cards)}；关系实例 = {relation_count}；无法解析的引用 = {len(unresolved)}")
        for u in report["unresolved"]:
            print(f"  UNRESOLVED {u['card']} [{u['field']}] -> {u['referenced_symbol']}")

    if unresolved and not args.allow_unresolved:
        print(
            f"FAIL-CLOSED: {len(unresolved)} 条引用无法解析到产品个体；"
            "按 WP1.3 裁定不予静默丢弃。请补 --id-map 或由产品 Owner 补齐卡片。",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
