"""演示：基于 DKWS 平台访问「客户经理持续经营」场景的知识领域数据。

场景来源：scenario/seed（华东精工客户经理持续经营闭环，RM-CONTINUOUS-ENGAGEMENT）。
本脚本用 DKWS 平台把代表性知识数据接入工作区，并通过 service.query / search
演示数据访问，逐项说明：访问的知识领域 / 存储位置 / 输出格式。

运行：
    PYTHONPATH=src python scripts/demo_rm_data_access.py [--ws <dir>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import csv as _csv
from io import StringIO


def _csv_rows(text: str):
    """把 CSV 文本（可能含首行 BOM）安全解析为 dict 行。
    csv.DictReader 不会剥离 BOM，首列 key 会带 \\ufeff；先逐行去除。"""
    text = "".join(line.removeprefix("\ufeff") for line in text.splitlines(keepends=True))
    return _csv.DictReader(StringIO(text))

from dkws import schemas  # noqa: E402,F401
from dkws.docs import DocumentPipeline  # noqa: E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.service import KnowledgeService as ServiceApi  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

SEED = REPO / "scenario" / "seed"

# 客户经理持续经营场景中将要「演示访问」的知识领域文件（原文所在位置）
SOURCE_FILES = [
    # (显示名, 知识领域, 原文相对路径, DKWS 接入方式)
    ("customer-master", "客户主数据/客户基础信息",
     "02_master_data/customer_master.json", "json-entity"),
    ("product-cards", "产品知识/产品准入(产品画像)",
     "05_knowledge/product_knowledge_cards.yaml", "doc-extract"),
    ("visit-sop", "运营规范/访前访中访后SOP",
     "05_knowledge/visit_sop.yaml", "doc-extract"),
    ("kyc-library", "KYC/问题库(按角色/主题)",
     "05_knowledge/kyc_question_library.jsonl", "doc-extract"),
    ("ontology", "本体/对象与关键区分",
     "05_knowledge/ontology_seed.json", "json-entity"),
    ("graph-entities", "企业知识图谱/法人实体",
     "02_master_data/legal_entities.csv", "graph-entities"),
    ("graph-ownership", "企业知识图谱/股权关系",
     "02_master_data/group_relationships.csv", "graph-relations"),
    ("graph-chain", "企业知识图谱/产业链节点",
     "02_master_data/industry_chain_nodes.csv", "graph-chain"),
    ("stakeholders", "企业知识图谱/关键人物影响",
     "02_master_data/stakeholder_directory.csv", "stakeholders"),
    ("industry-taxonomy", "企业知识图谱/行业分层",
     "02_master_data/industry_taxonomy.csv", "industry-tax"),
    ("product-rules", "产品规则版本/对象模型",
     "05_knowledge/product_rule_versions.jsonl", "product-rules"),
    ("skill-products", "对象模型/Skill-Product 注册",
     "05_knowledge/skill_product_registry.json", "skill-products"),
]


def demo(args) -> None:
    root = Path(args.ws)
    if (root / "dkws.meta.yaml").exists():
        Workspace.open(root)
        ws = Workspace.open(root)
        print(f"[复用工作区] {root.resolve()}")
    else:
        ws = Workspace.init(root, by="demo_rm_data_access")
        print(f"[初始化工作区] {root.resolve()}")

    print("\n=== 第 1 步：把客户经理持续经营的知识领域数据接入 DKWS 工作区 ===")
    pipe = DocumentPipeline(ws)
    api = ServiceApi(ws)
    ksvc = KnowledgeService(ws)

    for name, domain, rel, how in SOURCE_FILES:
        src = SEED / rel
        if not src.exists():
            print(f"  - 跳过(不存在): {rel}")
            continue
        text = src.read_text(encoding="utf-8").lstrip("\ufeff")
        doc_id = f"RM-{name}"
        if how in ("doc-extract",):
            # 文本/YAML -> 文档登记 + 规范化切片
            pipe.register(doc_id, name=name, source_file=src.name,
                          domain="knowledge", classification="INTERNAL", owner="RM-Front")
            out = pipe.normalize_and_slice(doc_id, "knowledge", text)
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} "
                  f"切片 {out.segment_count} 段 (NORMALIZED+segments)")
        elif name == "customer-master":
            data = json.loads(text)
            cid = data.get("customer_id", "CUST-001")
            # 把原文关键字段完整落入 attributes，使产物承载真实语义（非占位）
            attr_fields = ("industry", "region", "established_date", "registered_capital_cny",
                           "relationship_since", "customer_tier", "rm_id", "managing_org",
                           "group_id", "listed", "risk_level", "employees_group",
                           "payroll_bank_employees", "main_products")
            attributes = {k: data[k] for k in attr_fields if k in data}
            desc = (data.get("relationship_summary")
                    or f"{data.get('canonical_name')} 客户，行业 {data.get('industry')}，"
                       f"地区 {data.get('region')}，层级 {data.get('customer_tier')}。")
            ksvc.register_entity_candidate(
                entity_id=cid, entity_type="CUSTOMER", name=data.get("canonical_name", cid),
                aliases=[data.get("canonical_name", "")], domain="knowledge",
                source_document_ids=[doc_id], description=desc, attributes=attributes)
            ksvc.register_statement_candidate(
                statement_id=f"ST-{cid}-tier", subject_id=cid, predicate="customer_tier",
                object_value=data.get("customer_tier", ""), value_type="ENTITY_TYPE",
                source_document_ids=[doc_id])
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} (客户实体/声明候选)")
        elif name == "ontology":
            data = json.loads(text)
            objects = data.get("objects", [])
            distinctions = data.get("critical_distinctions", [])
            # 每个本体对象都带描述；最后用一个"本体关键区分"实体承载 critical_distinctions（真实语义）
            for obj in objects:
                ksvc.register_entity_candidate(
                    entity_id=f"OBJ-{obj}", entity_type="ONTOLOGY_OBJECT",
                    name=obj, aliases=[], domain="knowledge",
                    source_document_ids=[doc_id],
                    description=f"对公持续经营本体对象: {obj}（银行客户经理场景领域模型）。")
            if distinctions:
                ksvc.register_entity_candidate(
                    entity_id="OBJ-CRITICAL-DISTINCTIONS", entity_type="ONTOLOGY_OBJECT",
                    name="本体关键区分", aliases=[], domain="knowledge",
                    source_document_ids=[doc_id],
                    description="对公持续经营对象的关键区分（Claim≠Fact 等）。",
                    attributes={"critical_distinctions": distinctions})
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} "
                  f"({len(objects)} 本体对象 + {len(distinctions)} 关键区分)")
        elif how == "graph-entities":
            # 企业知识图谱：法人实体（完整落属性：持股/归属/角色）
            n = 0
            for row in _csv_rows(text):
                attr = {k: v for k, v in row.items()
                        if k not in ("entity_id", "name", "short_name") and v}
                desc = (f"法人主体 {row.get('name', row.get('entity_id'))}"
                        + (f"（{row.get('short_name')}）" if row.get("short_name") else "")
                        + (f"，类型 {row.get('entity_type')}" if row.get("entity_type") else "")
                        + (f"，角色 {row.get('role')}" if row.get("role") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=row["entity_id"], entity_type="LEGAL_ENTITY",
                    name=row.get("name", row["entity_id"]),
                    aliases=[row.get("short_name", "")] if row.get("short_name") else [],
                    domain="knowledge", source_document_ids=[doc_id],
                    description=desc, attributes=attr)
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} ({n} 个法人实体，含持股/角色属性)")
        elif how == "graph-relations":
            n = 0
            for row in _csv_rows(text):
                rel_id = row["relation_id"]
                # 关系两端实体已在 graph-entities 注册
                ksvc.register_relation_candidate(
                    relation_id=rel_id, source_id=row["from_entity"], target_id=row["to_entity"],
                    relation_type=row["relation_type"], direction="DIRECTED",
                    statement_id=f"ST-{rel_id}", source_document_ids=[doc_id])
                # 持股比例作为关系语义落成声明（真实业务字段）
                if row.get("ownership_pct"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{rel_id}-pct", subject_id=row["from_entity"],
                        predicate="ownership_pct", object_value=row["ownership_pct"],
                        value_type="NUMBER", source_document_ids=[doc_id])
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} ({n} 条股权关系，含持股比例)")
        elif how == "graph-chain":
            n = 0
            seen = set()
            for row in _csv_rows(text):
                node_id = row["node_id"]
                if node_id in seen:
                    continue
                seen.add(node_id)
                attr = {k: v for k, v in row.items()
                        if k not in ("node_id", "node_name") and v}
                desc = (f"产业链节点 {row.get('node_name', node_id)}"
                        + (f"（{row.get('role')}）" if row.get("role") else "")
                        + (f"，行业代码 {row.get('industry_code')}" if row.get("industry_code") else "")
                        + (f"，典型金融需求: {row.get('typical_financial_need')}"
                           if row.get("typical_financial_need") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=node_id, entity_type="INDUSTRY_CHAIN_NODE",
                    name=row.get("node_name", node_id), aliases=[], domain="knowledge",
                    source_document_ids=[doc_id], description=desc, attributes=attr)
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} "
                  f"({n} 个产业链节点，含角色/行业/金融需求)")
        elif how == "stakeholders":
            n = 0
            for row in _csv_rows(text):
                skey = row.get("stakeholder_id")
                if not skey:
                    continue
                # 关键人物完整属性：角色/影响力/态度/银行关系/决策议题/渠道/最近联系
                attr = {k: v for k, v in row.items()
                        if k not in ("stakeholder_id", "person_id", "entity_id", "role") and v}
                desc = (f"关键人物 {row.get('person_id', skey)}"
                        + (f"，角色 {row.get('role')}" if row.get("role") else "")
                        + (f"，影响力 {row.get('influence')}" if row.get("influence") else "")
                        + (f"，态度 {row.get('attitude')}" if row.get("attitude") else "")
                        + (f"，银行关系 {row.get('bank_relationship')}"
                           if row.get("bank_relationship") else "")
                        + (f"，决策议题 {row.get('decision_topics')}"
                           if row.get("decision_topics") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=skey, entity_type="STAKEHOLDER",
                    name=row.get("person_id", skey), aliases=[], domain="knowledge",
                    source_document_ids=[doc_id], description=desc, attributes=attr)
                if row.get("role"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{skey}-role", subject_id=skey, predicate="has_role",
                        object_value=row["role"], value_type="STRING",
                        source_document_ids=[doc_id])
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} "
                  f"({n} 位关键人物，含角色/影响力/决策议题)")
        elif how == "industry-tax":
            n = 0
            for row in _csv_rows(text):
                code = row.get("industry_code")
                if not code:
                    continue
                attr = {k: v for k, v in row.items()
                        if k not in ("industry_code", "industry_name") and v}
                desc = (f"行业节点 {row.get('industry_name', code)}"
                        + (f"（代码 {code}）" if code else "")
                        + (f"，层级 {row.get('level')}" if row.get("level") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=code, entity_type="INDUSTRY_TAXONOMY_NODE",
                    name=row.get("industry_name", code), aliases=[], domain="knowledge",
                    source_document_ids=[doc_id], description=desc, attributes=attr)
                if row.get("parent_code"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{code}-parent", subject_id=code,
                        predicate="parent_industry", object_value=row["parent_code"],
                        value_type="ENTITY_ID", source_document_ids=[doc_id])
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} ({n} 个行业节点，含层级/父级)")
        elif how == "product-rules":
            n = 0
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                pid = rec.get("product_id")
                if not pid:
                    continue
                attr = {k: v for k, v in rec.items()
                        if k not in ("product_id", "version") and v is not None}
                desc = (f"产品规则产品 {pid} 版本 {rec.get('version')}"
                        + (f"，状态 {rec.get('status')}" if rec.get("status") else "")
                        + (f"，生效 {rec.get('effective_from')}" if rec.get("effective_from") else "")
                        + (f"，所有者 {rec.get('owner')}" if rec.get("owner") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=f"{pid}-{rec.get('version')}", entity_type="PRODUCT_RULE_VERSION",
                    name=f"{pid}@{rec.get('version')}", aliases=[pid], domain="knowledge",
                    source_document_ids=[doc_id], description=desc, attributes=attr)
                if rec.get("status"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{pid}-{rec.get('version')}-st", subject_id=f"{pid}-{rec.get('version')}",
                        predicate="product_status", object_value=rec["status"],
                        value_type="STRING", source_document_ids=[doc_id])
                if rec.get("effective_from"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{pid}-{rec.get('version')}-ef", subject_id=f"{pid}-{rec.get('version')}",
                        predicate="effective_from", object_value=rec["effective_from"],
                        value_type="DATE", source_document_ids=[doc_id])
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} ({n} 条产品规则版本)")
        elif how == "skill-products":
            data = json.loads(text)
            n = 0
            for rec in data:
                sid = rec.get("skill_product_id")
                if not sid:
                    continue
                attr = {k: v for k, v in rec.items()
                        if k not in ("skill_product_id", "name") and v is not None}
                desc = (f"技能产品 {rec.get('name', sid)}"
                        + (f"（版本 {rec.get('version')}" if rec.get("version") else "（版本 ?")
                        + (f"，{rec.get('status')}" if rec.get("status") else "")
                        + (f"，human_gate={rec.get('human_gate_required')}"
                           if rec.get("human_gate_required") else "") + "）"
                        + (f"。输入: {rec.get('input_contract')}" if rec.get("input_contract") else "")
                        + (f"。输出: {rec.get('output_contract')}" if rec.get("output_contract") else "")
                        + (f"。所有者: {rec.get('owner')}" if rec.get("owner") else "") + "。")
                ksvc.register_entity_candidate(
                    entity_id=sid, entity_type="SKILL_PRODUCT",
                    name=rec.get("name", sid), aliases=[], domain="knowledge",
                    source_document_ids=[doc_id], description=desc, attributes=attr)
                if rec.get("human_gate_required"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{sid}-gate", subject_id=sid,
                        predicate="human_gate_required", object_value=rec["human_gate_required"],
                        value_type="STRING", source_document_ids=[doc_id])
                n += 1
            print(f"  - 接入 {name:16s} [{domain}]  <- {rel:48s} ({n} 个 Skill-Product)")

    print("\n=== 第 2 步：人工审核决定 + 发布（生成 CURRENT 核心知识） ===")
    try:
        ksvc.record_decision(decision_id="DC-RM-DEMO",
                             object_refs=[
                                 "ENT-CUST-001", "ENT-OBJ-Party", "ENT-OBJ-Need",
                                 "ENT-OBJ-Commitment", "ST-ST-CUST-001-tier",
                                 "ENT-ENT-001", "ENT-ENT-002", "ENT-ENT-003",
"ENT-ENT-004", "ENT-ENT-005",
                                "REL-REL-ENT-002", "ENT-CHAIN-01",
                                "ENT-STK-001", "ENT-STK-002",
                                "STMT-ST-STK-001-role", "STMT-ST-STK-001-infl",
                                "STMT-ST-STK-002-role",
                                "ENT-I-100", "ENT-I-110",
                                "STMT-ST-I-110-parent",
                                "ENT-PROD-WCL-3.4", "ENT-PROD-FAL-2.2",
                                "STMT-ST-PROD-WCL-3.4-st",
                                "ENT-SP-01",
                            ],
                            decision="APPROVE", decided_by="anonymous-human-owner",
                            role="OWNER", reason="demo review")
        out = Publisher(ws).publish("knowledge", approved_decision_ids=["DC-RM-DEMO"])
        print(f"  - 已发布 {out.release_id} version={out.version}")
    except Exception as exc:  # noqa: BLE001
        print(f"  - 发布跳过(用于只读演示): {type(exc).__name__}: {exc}")

    print("\n=== 第 2.5 步：构建服务投影（04_serve 实体化产物） ===")
    core_dir = ws.root / "03_core" / "knowledge"
    if core_dir.is_dir():
        for vdir in sorted(core_dir.glob("version=*")):
            v = vdir.name.split("=")[1]
            resp = api.build_projection(service_id="svc-demo", domain="knowledge", version=v)
            if resp.status == "ok":
                print(f"  - 投影 {resp.data['projection_id']} 已构建（04_serve/svc-demo/version={v}）")
            else:
                print(f"  - 投影构建失败 version={v}: {resp.errors}")

    print("\n=== 第 3 步：通过 DKWS 服务访问数据 ===")
    q = api.query(domain="knowledge")
    print("  service.query  ->", json.dumps(q.data, ensure_ascii=False)[:240])
    q_legal = api.query(domain="knowledge", entity_type="LEGAL_ENTITY")
    print("  query LEGAL_ENTITY ->", json.dumps(q_legal.data, ensure_ascii=False)[:240])
    q_stk = api.query(domain="knowledge", entity_type="STAKEHOLDER")
    print("  query STAKEHOLDER ->", json.dumps(q_stk.data, ensure_ascii=False)[:240])
    q_ind = api.query(domain="knowledge", entity_type="INDUSTRY_TAXONOMY_NODE")
    print("  query INDUSTRY  ->", json.dumps(q_ind.data, ensure_ascii=False)[:240])
    q_prod = api.query(domain="knowledge", entity_type="PRODUCT_RULE_VERSION")
    print("  query PRODUCT   ->", json.dumps(q_prod.data, ensure_ascii=False)[:240])
    s = api.search(query="Commitment", domain="knowledge")
    print("  service.search  ->", json.dumps(s.data, ensure_ascii=False)[:200])

    print("\n=== 第 4 步：工作区落点预览 ===")
    for sub in ("02_work/U", "02_work/C", "03_core/knowledge", "90_control/decisions"):
        d = ws.root / sub
        n = 0
        if d.is_dir():
            files = sorted({p.name for p in d.rglob("*") if p.is_file() and p.suffix != ".lock" and ".DS_Store" not in str(p)})
            n = len(files)
        print(f"  {sub}: {n} 个文件")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default="/tmp/dkws-rm-demo", help="DKWS 工作区目录")
    args = ap.parse_args()
    demo(args)


if __name__ == "__main__":
    main()