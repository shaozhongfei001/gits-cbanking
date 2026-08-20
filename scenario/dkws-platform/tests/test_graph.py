"""企业知识图谱接入测试：CSV(BOM) 解析、法人实体、股权关系、产业链节点，发布后可查。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.errors import ConflictError  # noqa: E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

LEGAL_CSV = (
    "entity_id,name,short_name,entity_type,role,ownership_parent,ownership_pct,"
    "bank_customer_id,status\n"
    "ENT-001,华东精工集团有限公司,华东精工,LEGAL_ENTITY,本部,,,CUST-001,ACTIVE\n"
    "ENT-002,华东精工智能制造有限公司,智能制造,LEGAL_ENTITY,项目主体,ENT-001,100,CUST-002,ACTIVE\n"
)
GRAPH_CSV = (
    "relation_id,from_entity,to_entity,relation_type,ownership_pct,effective_from,source_ref\n"
    "REL-ENT-002,ENT-001,ENT-002,OWNS,100,2023-01-01,SYNTH_GROUP_REGISTRY\n"
)
CHAIN_CSV = (
    "node_id,industry_code,role,node_name,typical_financial_need\n"
    "CHAIN-01,I-121,上游,伺服系统供应,预付款\n"
)


class TestGraphIngest(unittest.TestCase):
    def _seed_graph(self, ws, *, with_bom=True):
        import csv
        ksvc = KnowledgeService(ws)
        text = LEGAL_CSV
        if with_bom:
            text = "\ufeff" + text
        # BOM 必须逐行剥离：csv.DictReader 不会去掉首行 BOM，导致首列 key 变 \ufeffentity_id
        text = "".join(line.removeprefix("\ufeff") for line in text.splitlines(keepends=True))
        for row in csv.DictReader(text.splitlines()):
            ksvc.register_entity_candidate(
                entity_id=row["entity_id"], entity_type="LEGAL_ENTITY",
                name=row.get("name"), aliases=[row.get("short_name")] if row.get("short_name") else [],
                domain="knowledge", source_document_ids=["RM-graph"])
            parent = row.get("ownership_parent")
            if parent:
                ksvc.register_relation_candidate(
                    relation_id=f"OWNS-{row['entity_id']}-{parent}", source_id=parent,
                    target_id=row["entity_id"], relation_type="OWNS", direction="DIRECTED",
                    statement_id=f"ST-OWN-{row['entity_id']}", source_document_ids=["RM-graph"])
        for row in csv.DictReader(CHAIN_CSV.splitlines()):
            ksvc.register_entity_candidate(
                entity_id=row["node_id"], entity_type="INDUSTRY_CHAIN_NODE",
                name=row["node_name"], aliases=[], domain="knowledge",
                source_document_ids=["RM-graph"])
        return ksvc

    def test_parse_bom_csv_and_relations(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = self._seed_graph(ws, with_bom=True)
            # BOM 不应影响首列键
            cand = ksvc._find_candidate("ENT-ENT-001")
            self.assertIsNotNone(cand, "法人实体 ENT-001 应已注册")
            self.assertIsNotNone(ksvc._find_candidate("ENT-ENT-002"))
            # 股权关系（ref = REL-<relation_id>）
            rel = ksvc._find_candidate("REL-OWNS-ENT-002-ENT-001")
            self.assertIsNotNone(rel)
            self.assertEqual(rel["values"]["relation_type"], "OWNS")
            # 产业链节点
            self.assertIsNotNone(ksvc._find_candidate("ENT-CHAIN-01"))

    def test_graph_relation_referential_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = KnowledgeService(ws)
            ksvc.register_entity_candidate(entity_id="A", entity_type="LEGAL_ENTITY",
                                           name="A", aliases=[], domain="knowledge",
                                           source_document_ids=["D"])
            # 引用不存在的目标实体应被拒（防悬空边）
            with self.assertRaises(ConflictError):
                ksvc.register_relation_candidate(
                    relation_id="REL-BAD", source_id="A", target_id="NOPE",
                    relation_type="OWNS", direction="DIRECTED",
                    statement_id="ST-BAD", source_document_ids=["D"])

    def test_publish_graph_and_query(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Workspace.init(Path(td) / "ws")
            ksvc = self._seed_graph(ws)
            ksvc.record_decision(decision_id="DC-G", object_refs=[
                "ENT-ENT-001", "ENT-ENT-002", "REL-OWNS-ENT-002-ENT-001", "ENT-CHAIN-01"],
                decision="APPROVE", decided_by="anon-human", role="OWNER", reason="demo")
            out = Publisher(ws).publish("knowledge", approved_decision_ids=["DC-G"])
            from dkws.service import KnowledgeService as ServiceApi
            resp = ServiceApi(ws).query(domain="knowledge")
            self.assertEqual(resp.status, "ok")
            self.assertGreaterEqual(resp.data["entity_count"], 3)
            # 实体为 LEGAL_ENTITY —— 可进一步按类型过滤
            resp2 = ServiceApi(ws).query(domain="knowledge", entity_type="LEGAL_ENTITY")
            self.assertEqual(resp2.status, "ok")
            self.assertEqual(resp2.data["entity_count"], 2)
            # 股权关系已发布到 03_core relations
            rel_dir = ws.root / "03_core" / "knowledge" / f"version={out.version}" / "relations"
            self.assertTrue(rel_dir.is_dir())
            self.assertGreaterEqual(len(list(rel_dir.glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()