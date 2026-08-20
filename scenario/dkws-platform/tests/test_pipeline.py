"""P0/P2/P4/P5/P6/P7/P8 全链路测试（标准库 unittest）。

场景：init 工作区 -> ingest raw -> docs 切片 -> 知识候选/冲突/决定 -> publish -> 投影 -> 查询服务。
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.errors import ConflictError, ValidationError  # noqa: E402
from dkws.state import JOB_SM, ASSET_SM, RELEASE_SM  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402
from dkws.ingest import IngestionService  # noqa: E402
from dkws.docs import DocumentPipeline  # noqa: E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.service import KnowledgeService as ServiceApi, _eval_rule  # noqa: E402


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


# ---------------------------------------------------------------- P0 工作区
class TestWorkspace(PipelineTestCase):
    def test_init_inspect(self):
        ws = Workspace.init(self.root / "ws")
        for layer in ("01_raw", "02_work", "03_core", "04_serve", "90_control"):
            self.assertTrue((self.root / "ws" / layer).is_dir(), layer)
        self.assertTrue((self.root / "ws" / "dkws.meta.yaml").exists())
        info = Workspace.open(self.root / "ws").inspect()
        self.assertEqual(info["schema"], "dkws/0.1")

    def test_path_escape_blocked(self):
        ws = Workspace.init(self.root / "ws")
        with self.assertRaises(Exception):
            ws.resolve("../escape")


# ---------------------------------------------------------------- 状态机
class TestStateMachines(unittest.TestCase):
    def test_job_transitions(self):
        self.assertEqual(JOB_SM.transition("PENDING", "RUNNING"), "RUNNING")
        with self.assertRaises(Exception):
            JOB_SM.transition("PENDING", "COMPLETED")

    def test_asset_state_machine(self):
        self.assertEqual(ASSET_SM.transition("CANDIDATE", "IN_REVIEW"), "IN_REVIEW")
        self.assertEqual(ASSET_SM.transition("IN_REVIEW", "APPROVED"), "APPROVED")
        self.assertEqual(ASSET_SM.transition("APPROVED", "PUBLISHED"), "PUBLISHED")
        with self.assertRaises(Exception):
            ASSET_SM.transition("CANDIDATE", "REJECTED")

    def test_release_state_machine(self):
        s = "DRAFT_RELEASE"
        s = RELEASE_SM.transition(s, "VALIDATING")
        s = RELEASE_SM.transition(s, "READY_TO_PUBLISH")
        s = RELEASE_SM.transition(s, "PUBLISHING")
        s = RELEASE_SM.transition(s, "PUBLISHED")
        self.assertEqual(s, "PUBLISHED")


# ---------------------------------------------------------------- P2 接入
class TestIngest(PipelineTestCase):
    def test_ingest_flow(self):
        ws = Workspace.init(self.root / "ws")
        src = self.root / "src"
        src.mkdir()
        (src / "a.csv").write_text("id,name\n1,x\n", encoding="utf-8")
        svc = IngestionService(ws)
        res = svc.ingest(src, domain="nodes", idempotency_key="key-123")
        self.assertTrue(res.manifest_path)
        self.assertEqual(res.file_count, 1)
        self.assertIsNotNone(res.content_sha256)
        # 幂等重复
        with self.assertRaises(ConflictError):
            svc.ingest(src, domain="nodes", idempotency_key="key-123")
        # 非法 domain
        with self.assertRaises(ValidationError):
            svc.ingest(src, domain="bad", idempotency_key="k-2")

    def test_ingest_large_file_rejected(self):
        ws = Workspace.init(self.root / "ws")
        src = self.root / "big.txt"
        src.write_text("x" * 10_000_000, encoding="utf-8")
        svc = IngestionService(ws)
        with self.assertRaises(ValidationError):
            svc.ingest(src, domain="knowledge", idempotency_key="k-big")


# ---------------------------------------------------------------- P4 文档
class TestDocs(PipelineTestCase):
    def test_normalize_slice(self):
        ws = Workspace.init(self.root / "ws")
        pipe = DocumentPipeline(ws)
        source = "# 标题\n\n第一段。\n\n| 列A | 列B |\n|---|---|\n| 1 | 2 |\n"
        pipe.register("DOC-1", name="Doc", source_file="doc.md", domain="knowledge")
        out = pipe.normalize_and_slice("DOC-1", "knowledge", source)
        self.assertGreaterEqual(out.segment_count, 3)
        self.assertEqual(out.document_id, "DOC-1")
        # 幂等：重跑同输入同输出（segment 数量一致）
        out2 = pipe.normalize_and_slice("DOC-1", "knowledge", source)
        self.assertEqual(out.segment_count, out2.segment_count)


# ---------------------------------------------------------------- P5 知识
class TestKnowledge(PipelineTestCase):
    def test_candidate_and_decision(self):
        ws = Workspace.init(self.root / "ws")
        svc = KnowledgeService(ws)
        svc.register_entity_candidate(entity_id="E1", entity_type="COMPANY", name="A",
                                      aliases=[], domain="nodes", source_document_ids=["D1"])
        svc.register_statement_candidate(statement_id="S1", subject_id="E1", predicate="net_worth",
                                         object_value="100", value_type="NUMBER",
                                         source_document_ids=["D1"])
        # 系统自动 OWNER 决定被拒
        with self.assertRaises(ConflictError):
            svc.record_decision(decision_id="DC-1", object_refs=["ENT-E1"], decision="APPROVE",
                                decided_by="_system_auto", role="OWNER", reason="auto")
        # 人工批准
        rel = svc.record_decision(decision_id="DC-2", object_refs=["ENT-E1", "STMT-S1"],
                                  decision="APPROVE", decided_by="alice", role="OWNER",
                                  reason="manual")
        self.assertTrue(rel)

    def test_conflict_detection(self):
        ws = Workspace.init(self.root / "ws")
        svc = KnowledgeService(ws)
        svc.register_entity_candidate(entity_id="E1", entity_type="COMPANY", name="A",
                                      aliases=[], domain="nodes", source_document_ids=["D1"])
        svc.register_statement_candidate(statement_id="S1", subject_id="E1", predicate="net_worth",
                                         object_value="100", value_type="NUMBER",
                                         source_document_ids=["D1"])
        svc.register_statement_candidate(statement_id="S2", subject_id="E1", predicate="net_worth",
                                         object_value="999", value_type="NUMBER",
                                         source_document_ids=["D1"])
        n = svc.detect_conflicts()
        self.assertGreaterEqual(n, 1)


# ---------------------------------------------------------------- P6 发布
class TestPublish(PipelineTestCase):
    def _seed(self, ws, with_decision=True):
        ksvc = KnowledgeService(ws)
        ksvc.register_entity_candidate(entity_id="E1", entity_type="COMPANY", name="A",
                                       aliases=[], domain="knowledge", source_document_ids=["D1"])
        ksvc.register_statement_candidate(statement_id="S1", subject_id="E1", predicate="net_worth",
                                          object_value="1000000", value_type="NUMBER",
                                          source_document_ids=["D1"])
        ksvc.register_relation_candidate(relation_id="R1", source_id="E1", target_id="E1",
                                         relation_type="SELF", direction="UNDIRECTED",
                                         statement_id="S1", source_document_ids=["D1"])
        if with_decision:
            ksvc.record_decision(decision_id="DC-PUB", object_refs=["ENT-E1", "STMT-S1", "REL-R1"],
                                 decision="APPROVE", decided_by="bob", role="OWNER", reason="ok")

    def test_publish_requires_approval(self):
        ws = Workspace.init(self.root / "ws")
        self._seed(ws, with_decision=False)
        pub = Publisher(ws)
        with self.assertRaises(ValidationError):
            pub.publish("knowledge", approved_decision_ids=[])

    def test_publish_and_query(self):
        ws = Workspace.init(self.root / "ws")
        self._seed(ws)
        pub = Publisher(ws)
        out = pub.publish("knowledge", approved_decision_ids=["DC-PUB"])
        self.assertTrue(out.version)
        current = ws.root / "03_core" / "knowledge" / "CURRENT.md"
        self.assertTrue(current.exists())
        # 查询
        api = ServiceApi(ws)
        resp = api.query(domain="knowledge")
        self.assertEqual(resp.status, "ok")
        self.assertGreaterEqual(resp.data["entity_count"], 1)

    def test_rollback_missing_version(self):
        ws = Workspace.init(self.root / "ws")
        pub = Publisher(ws)
        with self.assertRaises(Exception):
            pub.rollback("knowledge", "99.0.0")


# ---------------------------------------------------------------- 规则执行
class TestRuleExec(unittest.TestCase):
    def test_eval_rule_eligibility(self):
        rule = {"rule_type": "ELIGIBILITY", "execution_mode": "AUTOMATIC",
                "when": ["all", ["gte", "input.net_worth", 1000000]],
                "then": {"action": "flag", "set": {"eligible": True}, "message": "high net worth"}}
        r = _eval_rule(rule, {"net_worth": 2000000})
        self.assertTrue(r["fired"])
        self.assertTrue(r["set"]["eligible"])

    def test_eval_rule_not_fired(self):
        rule = {"rule_type": "ALERT", "execution_mode": "AUTOMATIC",
                "when": ["lt", "input.amount", 0], "then": {"action": "alert"}}
        r = _eval_rule(rule, {"amount": 50})
        self.assertFalse(r["fired"])


# ---------------------------------------------------------------- 需求矩阵
class TestTraceMatrix(PipelineTestCase):
    def test_trace_matrix_exists(self):
        from dkws.trace import trace_matrix
        self.assertTrue(len(trace_matrix()) >= 18)


if __name__ == "__main__":
    unittest.main()