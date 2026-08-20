"""P9 E2E 黄金场景：接入 -> 切片 -> 候选/决定 -> 发布 -> 投影 -> 服务返回全链。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.workspace import Workspace  # noqa: E402
from dkws.ingest import IngestionService  # noqa: E402
from dkws.docs import DocumentPipeline  # noqa: E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.service import KnowledgeService as ServiceApi  # noqa: E402


class EndToEndTestCase(unittest.TestCase):
    def test_golden_scenario(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ws = Workspace.init(root / "ws")

            # 1. 接入 raw
            src = root / "src"
            src.mkdir()
            (src / "corp.csv").write_text("id,name\nC1,ACME\n", encoding="utf-8")
            IngestionService(ws).ingest(src, domain="knowledge", idempotency_key="e2e-1")

            # 2. 文档切片
            pipe = DocumentPipeline(ws)
            text = "# 示例公司\n\nACME 净资产五百万。\n"
            pipe.register("DOC-E2E", name="sample", source_file="sample.md", domain="knowledge")
            slice_out = pipe.normalize_and_slice("DOC-E2E", "knowledge", text)
            self.assertGreaterEqual(slice_out.segment_count, 2)

            # 3. 知识候选 + 决定
            ksvc = KnowledgeService(ws)
            ksvc.register_entity_candidate(entity_id="C1", entity_type="COMPANY",
                                           name="ACME", aliases=[], domain="knowledge",
                                           source_document_ids=["DOC-E2E"])
            ksvc.register_statement_candidate(statement_id="S1", subject_id="C1",
                                              predicate="net_worth", object_value="500000",
                                              value_type="NUMBER", source_document_ids=["DOC-E2E"])
            ksvc.record_decision(decision_id="DC-E2E", object_refs=["ENT-C1", "STMT-S1"],
                                 decision="APPROVE", decided_by="alice", role="OWNER",
                                 reason="qa pass")

            # 4. 发布 + CURRENT
            out = Publisher(ws).publish("knowledge", approved_decision_ids=["DC-E2E"])
            current = ws.root / "03_core" / "knowledge" / "CURRENT.md"
            self.assertTrue(current.exists())
            self.assertIn(out.version, current.read_text(encoding="utf-8"))

            # 5. 投影
            api = ServiceApi(ws)
            resp = api.build_projection(service_id="svc-e2e", domain="knowledge",
                                        version=out.version)
            self.assertEqual(resp.status, "ok")

            # 6. 服务返回合同化 JSON
            q = api.query(domain="knowledge", request_id="req-1")
            self.assertEqual(q.status, "ok")
            self.assertEqual(q.request_id, "req-1")
            self.assertGreaterEqual(q.data["entity_count"], 1)
            self.assertIn("meta", q.as_dict("e2e", out.version))
            # 数据路径不含宿主绝对路径
            s = api.search(query="net_worth", domain="knowledge")
            for hit in s.data["hits"]:
                self.assertNotIn(str(root), hit["path"])


if __name__ == "__main__":
    unittest.main()