"""访前报告数据组装链路测试：客户 ID → 读图 → 激活合同 → 检索 → 访前报告（READY）。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

SRC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC / "scripts"))


def _mini_ws(root: Path):
    ws = Workspace.init(root / "ws")
    ksvc = KnowledgeService(ws)
    # CUSTOMER
    ksvc.register_entity_candidate(entity_id="CUST-001", entity_type="CUSTOMER",
                                   name="华东精工装备集团有限公司", aliases=[],
                                   domain="knowledge", source_document_ids=["D"])
    # CREDIT
    ksvc.register_entity_candidate(entity_id="FAC-001", entity_type="CREDIT_FACILITY",
                                   name="FAC-001", aliases=[], domain="knowledge",
                                   source_document_ids=["D"])
    ksvc.register_entity_candidate(entity_id="KY-CFO-001", entity_type="KYC_QUESTION",
                                   name="KY-CFO-001", aliases=[], domain="knowledge",
                                   source_document_ids=["D"])
    # INTERACTION（AC-PREVISIT-001 必需资产）
    ksvc.register_entity_candidate(entity_id="INT-001", entity_type="INTERACTION",
                                   name="INT-001", aliases=[], domain="knowledge",
                                   source_document_ids=["D"])
    # 本体对象
    ksvc.register_entity_candidate(entity_id="OBJ-Party", entity_type="ONTOLOGY_OBJECT",
                                   name="Party", aliases=[], domain="knowledge",
                                   source_document_ids=["D"])
    # 产品
    ksvc.register_entity_candidate(entity_id="PROD-WCL-3.4", entity_type="PRODUCT_RULE_VERSION",
                                   name="PROD-WCL@3.4", aliases=[], domain="knowledge",
                                   source_document_ids=["D"])
    refs = ["ENT-CUST-001", "ENT-FAC-001", "ENT-KY-CFO-001", "ENT-INT-001",
            "ENT-OBJ-Party", "ENT-PROD-WCL-3.4"]
    ksvc.record_decision(decision_id="DC-PV", object_refs=refs, decision="APPROVE",
                         decided_by="anon", role="OWNER", reason="previsit")
    Publisher(ws).publish("knowledge", approved_decision_ids=["DC-PV"])
    return ws


class TestRealLlmComposeNormalization(unittest.TestCase):
    def test_compose_public_shape_without_network(self):
        """不触发真实网络：直接构造 RealLlm 实例跳过 __init__，验证 compose() 的规整/去重。"""
        from dkws.llm import RealLlm
        llm = RealLlm.__new__(RealLlm)  # 跳过 __init__（不检查 key、不调网络）
        llm._calls = []
        # 用 lambda 注入伪模型返回，模拟真实 chat/completions 输出 markdown 围栏 JSON
        fake_model = "deepseek-fake"
        import json as _json
        sections_payload = [
            {"assetId": "ASSET-DATA-CUSTOMER-PROFILE", "sequence": 1, "required": True,
             "items": ["华东精工装备集团有限公司"], "purpose": "客户事实"},
            {"assetId": "ASSET-KNOW-PRODUCT-CARDS", "sequence": 8, "required": False,
             "items": ["PROD-WCL@3.4", "PROD-WCL@3.4"]},
        ]
        seen = {}

        def fake_converse(system, user, temperature=0.2, max_tokens=2048):
            seen["prompt"] = user
            fence = "```json\n" + _json.dumps(sections_payload, ensure_ascii=False) + "\n```"
            return fence

        llm.converse = fake_converse
        llm.compose_json = lambda s, u, **kw: _json.loads(
            fake_converse(s, u).removeprefix("```json").removesuffix("```"))

        activation = {"contractId": "AC-PREVISIT-001", "routeMode": "ONTOLOGY_THEN_MAP",
                      "activations": [
                          {"assetId": "ASSET-DATA-CUSTOMER-PROFILE", "sequence": 1,
                           "required": True, "purpose": "客户事实"},
                          {"assetId": "ASSET-KNOW-PRODUCT-CARDS", "sequence": 8,
                           "required": False, "purpose": "定向产品知识"},
                      ]}
        retrieved = {
            "ASSET-DATA-CUSTOMER-PROFILE": [{"entity_id": "CUST-001", "name": "华东精工装备集团有限公司"}],
            "ASSET-KNOW-PRODUCT-CARDS": [
                {"entity_id": "P1", "name": "PROD-WCL@3.4"},
                {"entity_id": "P2", "name": "PROD-FAL@2.2"},
            ],
        }
        out = llm.compose(activation, retrieved)
        by_id = {s["assetId"]: s for s in out}
        self.assertEqual(len(out), 2)
        # 产品卡片：模型 items + DKWS 回填，保序去重
        prod = by_id["ASSET-KNOW-PRODUCT-CARDS"]["items"]
        self.assertEqual(prod, ["PROD-WCL@3.4", "PROD-FAL@2.2"])
        self.assertEqual(prod.count("PROD-WCL@3.4"), 1)
        # 客户画像：应以 DKWS 命中的名称为准（模型未给时回填）
        cust = by_id["ASSET-DATA-CUSTOMER-PROFILE"]["items"]
        self.assertEqual(cust, ["华东精工装备集团有限公司"])
        # prompt 应包含 retrieved 数据（确保真实模型有数据读）
        self.assertIn("PROD-WCL@3.4", seen["prompt"])


class TestPrevisitReport(unittest.TestCase):
    def test_assembly_ready(self):
        from demo_previsit_report import PrevisitAssembler
        with tempfile.TemporaryDirectory() as td:
            ws = _mini_ws(Path(td))
            a = PrevisitAssembler(ws.root)
            report = a.run("P-VISIT-001")
            self.assertEqual(report["customerId"], "CUST-001")
            self.assertEqual(report["status"], "READY")
            self.assertTrue(report["dataAssembly"]["readyToReport"])
            self.assertEqual(report["dataAssembly"]["missingRequiredAssets"], [])
            # 必需资产应命中
            seq = {s["assetId"]: s for s in report["dataAssembly"]["activationSequenced"]}
            self.assertTrue(seq["ASSET-DATA-CUSTOMER-PROFILE"]["items"])
            self.assertTrue(seq["ASSET-DATA-CREDIT-FACILITY"]["items"])
            self.assertTrue(seq["ASSET-KNOW-KYC-QUESTION-LIBRARY"]["items"])
            # 读图路径
            self.assertIn("KM-GITS-ROOT", report["knowledgePath"]["rootMap"])
            self.assertIn("AC-PREVISIT-001", report["knowledgePath"]["activationContract"])

    def test_markdown_render(self):
        from demo_previsit_report import PrevisitAssembler
        with tempfile.TemporaryDirectory() as td:
            ws = _mini_ws(Path(td))
            a = PrevisitAssembler(ws.root)
            report = a.run("P-VISIT-001")
            md = a.render_markdown(report)
            self.assertIn("# 访前报告", md)
            self.assertIn("CUST-001", md)
            self.assertIn("AC-PREVISIT-001", md)
            self.assertIn("就绪度", md)


if __name__ == "__main__":
    unittest.main()