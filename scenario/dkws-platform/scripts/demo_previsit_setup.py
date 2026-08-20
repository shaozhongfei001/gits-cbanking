"""访前演示前置准备：注册 CUST-001 的访前所需业务资产并发布。

覆盖激活合同 AC-PREVISIT-001 需要的资产检索命中：
- ASSET-DATA-CUSTOMER-PROFILE     CUSTOMER (已在主演示发布)
- ASSET-KNOW-CUSTOMER-ONTOLOGY    ONTOLOGY_OBJECT (已发布)
- ASSET-DATA-CREDIT-FACILITY      CREDIT_FACILITY
- ASSET-DATA-INTERACTION-HISTORY  INTERACTION
- ASSET-KNOW-KYC-QUESTION-LIBRARY KYC_QUESTION
- ASSET-KNOW-PRODUCT-CARDS        PRODUCT_RULE_VERSION (已发布)
- ASSET-KNOW-VISIT-SOP            VISIT_SOP
将 CREDIT_FACILITY / INTERACTION / KYC_QUESTION / VISIT_SOP 作为 AA 级实体/声明注册并发布。

运行：PYTHONPATH=src python scripts/demo_previsit_setup.py --ws <ws>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws import schemas  # noqa: F401,E402
from dkws.knowledge import KnowledgeService  # noqa: E402
from dkws.publish import Publisher  # noqa: E402
from dkws.workspace import Workspace  # noqa: E402

CUST = "CUST-001"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default="/tmp/dkws-rm-demo")
    ap.add_argument("--extra-only", action="store_true",
                    help="只注册访前业务资产（假设 CUSTOMER/本体/产品已由主演示发布）")
    args = ap.parse_args()

    ws = Workspace.open(Path(args.ws))
    ksvc = KnowledgeService(ws)

    approved_refs = []

    # ---- 授信额度
    ksvc.register_entity_candidate(
        entity_id="FAC-001", entity_type="CREDIT_FACILITY", name="FAC-001",
        aliases=[CUST], domain="knowledge", source_document_ids=["RM-credit"])
    ksvc.register_statement_candidate(
        statement_id=f"ST-FAC-{CUST}-ammt", subject_id="FAC-001",
        predicate="facility_amount", object_value="120000000", value_type="NUMBER",
        source_document_ids=["RM-credit"])
    ksvc.register_statement_candidate(
        statement_id=f"ST-FAC-{CUST}-used", subject_id="FAC-001",
        predicate="utilized_amount", object_value="36000000", value_type="NUMBER",
        source_document_ids=["RM-credit"])
    approved_refs += ["ENT-FAC-001", f"STMT-ST-FAC-{CUST}-ammt", f"STMT-ST-FAC-{CUST}-used"]

    # ---- 互动历史
    ksvc.register_entity_candidate(
        entity_id="INT-001", entity_type="INTERACTION", name="INT-001",
        aliases=[CUST], domain="knowledge", source_document_ids=["RM-interaction"])
    ksvc.register_statement_candidate(
        statement_id=f"ST-INT-{CUST}-last", subject_id="INT-001",
        predicate="last_interaction", object_value="2026-07-02", value_type="DATE",
        source_document_ids=["RM-interaction"])
    approved_refs += ["ENT-INT-001", f"STMT-ST-INT-{CUST}-last"]

    # ---- KYC 问题库（面向 CFO 的访前问题）
    ksvc.register_entity_candidate(
        entity_id="KY-CFO-001", entity_type="KYC_QUESTION", name="KY-CFO-001",
        aliases=[CUST], domain="knowledge", source_document_ids=["RM-kyc"])
    ksvc.register_statement_candidate(
        statement_id=f"ST-KYC-{CUST}-role", subject_id="KY-CFO-001",
        predicate="target_role", object_value="CFO", value_type="STRING",
        source_document_ids=["RM-kyc"])
    approved_refs += ["ENT-KY-CFO-001", f"STMT-ST-KYC-{CUST}-role"]

    # ---- 访前 SOP
    ksvc.register_entity_candidate(
        entity_id="SOP-PRE-001", entity_type="VISIT_SOP", name="SOP-PRE-001",
        aliases=[CUST], domain="knowledge", source_document_ids=["RM-sop"])
    approved_refs += ["ENT-SOP-PRE-001"]

    # 人工审核决定
    ksvc.record_decision(decision_id="DC-PREVISIT-ASSETS", object_refs=approved_refs,
                         decision="APPROVE", decided_by="anonymous-human-owner",
                         role="OWNER", reason="previsit asset prepare")
    out = Publisher(ws).publish("knowledge", approved_decision_ids=["DC-PREVISIT-ASSETS"])
    print(f"已发布 {out.release_id} version={out.version}")
    print(f"新增可访问资产: {[r.removeprefix('ENT-') for r in approved_refs if r.startswith('ENT-')]}")


if __name__ == "__main__":
    main()