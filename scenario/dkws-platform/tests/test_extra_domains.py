"""关键人物/行业分层/产品规则/Skill-Product 接入测试。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

STK_CSV = (
    "stakeholder_id,person_id,entity_id,role,influence,attitude,bank_relationship,"
    "decision_topics,preferred_channel,last_contact\n"
    "STK-001,C-CFO-001,ENT-001,CFO,HIGH,NEUTRAL_POSITIVE,STRONG,融资,电话,2026-07-02\n"
)
TAX_CSV = (
    "industry_code,industry_name,parent_code,level\n"
    "I-100,高端装备制造,,1\nI-110,工业自动化装备,I-100,2\n"
)
PROD_JSONL = (
    '{"product_id": "PROD-WCL", "version": "3.4", "effective_from": "2026-06-15", '
    '"effective_to": null, "status": "ACTIVE", "owner": "产品部"}\n'
    '{"product_id": "PROD-SCF", "version": "4.0", "effective_from": "2026-05-10", '
    '"effective_to": null, "status": "ACTIVE", "owner": "交易银行部"}\n'
)
SKILL_JSON = '[{"skill_product_id": "SP-01", "name": "客户组合与经营触发", "version": "1.1.0", "human_gate_required": "CONDITIONAL", "status": "ACTIVE"}]'


class _Ctx:
    """容纳推导出的 CSV 解析器（复用 demo 的 _csv_rows 逻辑）。"""

    @staticmethod
    def rows(text: str):
        import csv as _csv
        from io import StringIO
        text = "".join(line.removeprefix("\ufeff") for line in text.splitlines(keepends=True))
        return _csv.DictReader(StringIO(text))


class TestExtraDomains(unittest.TestCase):
    def test_stakeholder(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = KnowledgeService(ws)
            for row in _Ctx.rows(STK_CSV):
                ksvc.register_entity_candidate(
                    entity_id=row["stakeholder_id"], entity_type="STAKEHOLDER",
                    name=row.get("person_id"), aliases=[], domain="knowledge",
                    source_document_ids=["D"])
                ksvc.register_statement_candidate(
                    statement_id=f"ST-{row['stakeholder_id']}-role", subject_id=row["stakeholder_id"],
                    predicate="has_role", object_value=row["role"], value_type="STRING",
                    source_document_ids=["D"])
            self.assertIsNotNone(ksvc._find_candidate("ENT-STK-001"))
            self.assertIsNotNone(ksvc._find_candidate("STMT-ST-STK-001-role"))

    def test_industry_taxonomy(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = KnowledgeService(ws)
            for row in _Ctx.rows(TAX_CSV):
                ksvc.register_entity_candidate(
                    entity_id=row["industry_code"], entity_type="INDUSTRY_TAXONOMY_NODE",
                    name=row["industry_name"], aliases=[], domain="knowledge",
                    source_document_ids=["D"])
                if row.get("parent_code"):
                    ksvc.register_statement_candidate(
                        statement_id=f"ST-{row['industry_code']}-parent", subject_id=row["industry_code"],
                        predicate="parent_industry", object_value=row["parent_code"],
                        value_type="ENTITY_ID", source_document_ids=["D"])
            ent = ksvc._find_candidate("ENT-I-100")
            self.assertEqual(ent["values"]["name"], "高端装备制造")

    def test_product_rules_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = KnowledgeService(ws)
            import json
            for line in PROD_JSONL.splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                pid = rec["product_id"]
                ksvc.register_entity_candidate(
                    entity_id=f"{pid}-{rec['version']}", entity_type="PRODUCT_RULE_VERSION",
                    name=f"{pid}@{rec['version']}", aliases=[pid], domain="knowledge",
                    source_document_ids=["D"])
                ksvc.register_statement_candidate(
                    statement_id=f"ST-{pid}-{rec['version']}-st", subject_id=f"{pid}-{rec['version']}",
                    predicate="product_status", object_value=rec["status"], value_type="STRING",
                    source_document_ids=["D"])
            self.assertIsNotNone(ksvc._find_candidate("ENT-PROD-WCL-3.4"))
            self.assertIsNotNone(ksvc._find_candidate("ENT-PROD-SCF-4.0"))

    def test_skill_products(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = KnowledgeService(ws)
            import json
            for rec in json.loads(SKILL_JSON):
                ksvc.register_entity_candidate(
                    entity_id=rec["skill_product_id"], entity_type="SKILL_PRODUCT",
                    name=rec["name"], aliases=[], domain="knowledge", source_document_ids=["D"])
                ksvc.register_statement_candidate(
                    statement_id=f"ST-{rec['skill_product_id']}-gate",
                    subject_id=rec["skill_product_id"], predicate="human_gate_required",
                    object_value=rec["human_gate_required"], value_type="STRING",
                    source_document_ids=["D"])
            self.assertIsNotNone(ksvc._find_candidate("ENT-SP-01"))


if __name__ == "__main__":
    unittest.main()