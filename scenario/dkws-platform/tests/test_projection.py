"""P7 投影建与可重建性测试（标准库 unittest）。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.workspace import Workspace  # noqa: E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.service import KnowledgeService as ServiceApi  # noqa: E402
from dkws.projection import ProjectionBuilder  # noqa: E402
from dkws.errors import NotFoundError  # noqa: E402


class ProjectionTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._seed()

    def tearDown(self):
        self._tmp.cleanup()

    def _seed(self):
        ws = Workspace.init(self.root / "ws")
        ksvc = KnowledgeService(ws)
        ksvc.register_entity_candidate(entity_id="E1", entity_type="COMPANY", name="ACME",
                                       aliases=["A"], domain="knowledge",
                                       source_document_ids=["D1"])
        ksvc.register_statement_candidate(statement_id="S1", subject_id="E1",
                                          predicate="net_worth", object_value="500000",
                                          value_type="NUMBER", source_document_ids=["D1"])
        ksvc.record_decision(decision_id="DC-1", object_refs=["ENT-E1", "STMT-S1"],
                             decision="APPROVE", decided_by="bob", role="OWNER", reason="ok")
        Publisher(ws).publish("knowledge", approved_decision_ids=["DC-1"])
        self.ws = ws

    def test_build_projection(self):
        svc = ServiceApi(self.ws)
        resp = svc.build_projection(service_id="svc", domain="knowledge", version="1.0.0")
        self.assertEqual(resp.status, "ok")
        proj_dir = self.ws.root / "04_serve" / "svc" / "version=1.0.0"
        self.assertTrue(proj_dir.is_dir())
        self.assertTrue((proj_dir / "PROJECTION.md").exists())
        # 必须不含宿主绝对路径
        for f in proj_dir.rglob("*.csv"):
            self.assertNotIn(str(self.root), f.read_text(encoding="utf-8"))

    def test_rebuild_idempotent(self):
        svc = ServiceApi(self.ws)
        svc.build_projection(service_id="svc", domain="knowledge", version="1.0.0")
        proj_dir = self.ws.root / "04_serve" / "svc" / "version=1.0.0"
        first = sorted(p.stat().st_size for p in proj_dir.rglob("*") if p.is_file())
        svc.build_projection(service_id="svc", domain="knowledge", version="1.0.0")
        second = sorted(p.stat().st_size for p in proj_dir.rglob("*") if p.is_file())
        self.assertEqual(first, second, "投影重建应幂等（同输入同输出）")

    def test_missing_source_version(self):
        svc = ServiceApi(self.ws)
        resp = svc.build_projection(service_id="svc2", domain="knowledge", version="9.0.0")
        self.assertEqual(resp.status, "error")


if __name__ == "__main__":
    unittest.main()