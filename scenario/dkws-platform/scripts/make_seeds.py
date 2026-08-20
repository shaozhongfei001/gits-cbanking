"""生成 DKWS 权威演示样例与非法样例，用于 P1 合同校验测试与文档。
输出到 seeds/（合法 + 非法各若干）。

运行：python scripts/make_seeds.py <out_dir>
"""

from __future__ import annotations

import sys
from pathlib import Path

H = "a" * 64


def legal_samples():
    manifest_body = "# 清单\n\n## 摘要\n\n## 文件列表\n\n## 校验信息\n"
    manifest = (
        f"---\nschema: manifest/v1\nbatch_id: batch-demo-001\ndomain: nodes\n"
        f"source_type: CSV\nmedia_type: text/csv\nfile_count: 2\ntotal_bytes: 1280\n"
        f"content_sha256: {H}\nidempotency_key: demo-key-1\n"
        f"received_at: 2026-01-01T00:00:00Z\nstatus: CLOSED\nsize_bytes: 1280\n"
        f"version: 1.0\n---\n{manifest_body}"
    )

    entity_body = "# 实体\n\n## 描述\n\n## 来源证据\n\n## 冲突与限定\n\n## 审核说明\n"
    entity = (
        f"---\nschema: entity/v1\nentity_id: ENT-001\nentity_type: CORPORATE_ENTITY\n"
        f"name: 示例公司\naliases: []\ndescription: 演示\ndomain: nodes\ncanonical_id: ENT-001\n"
        f"attributes: {{}}\nsource_document_ids: [D-001]\nfirst_seen_at: 2026-01-01T00:00:00Z\n"
        f"validation_status: APPROVED\nconflict_status: NONE\neffective_from: null\n"
        f"effective_to: null\nrecorded_at: 2026-01-01T00:00:00Z\nstatus: ACTIVE\n"
        f"version: 1.0\n---\n{entity_body}"
    )

    statement_body = "# 声明\n\n## 规范表达\n\n## 来源证据\n\n## 冲突与限定\n\n## 审核说明\n"
    statement = (
        f"---\nschema: statement/v1\nstatement_id: STMT-001\nsubject_id: ENT-001\n"
        f"predicate: net_worth\nobject_value: 500000\nvalue_type: NUMBER\n"
        f"object_entity_id: null\nobject_unit: null\nderived: NATIVE\npolarity: AFFIRMED\n"
        f"validation_status: APPROVED\nconflict_status: NONE\neffective_from: null\n"
        f"effective_to: null\nrecorded_at: 2026-01-01T00:00:00Z\nstatus: ACTIVE\n"
        f"version: 1.0\nsource_document_ids: [D-001]\nsource_segment_ids: []\n"
        f"---\n{statement_body}"
    )

    current_body = "# 当前活动版本\n\n## 切换说明\n\n## 回滚说明\n"
    current = (
        f"---\nschema: current_pointer/v1\nscope_type: CORE_DOMAIN\nscope_id: nodes\n"
        f"target_version: 1.0.0\ntarget_release_id: REL-nodes-1.0.0\n"
        f"target_manifest_sha256: {H}\nswitched_by: dkws.cli\n"
        f"switched_at: 2026-01-01T00:00:00Z\nreason: demo\nstatus: ACTIVE\nversion: 2.0\n"
        f"---\n{current_body}"
    )
    return {
        "manifest-legal.md": manifest,
        "entity-legal.md": entity,
        "statement-legal.md": statement,
        "current-legal.md": current,
    }


def illegal_samples():
    # 非法1：schema 版本不匹配
    bad_schema = (
        f"---\nschema: manifest/v2\nbatch_id: b\ndomain: nodes\nsource_type: CSV\n"
        f"media_type: text/csv\nfile_count: 1\ntotal_bytes: 1\ncontent_sha256: {H}\n"
        f"idempotency_key: k\nreceived_at: t\n---\n"
    )
    # 非法2：缺必填字段（rule 无 test_case_ids 或 test_case 仅1）
    rule_body = "# 规则\n\n## 业务解释\n\n## 输入与输出\n\n## 证据\n\n## 人工责任边界\n\n## 测试说明\n"
    bad_rule = (
        f"---\nschema: rule/v1\nrule_id: RUL-001\nname: demo\nrule_type: VALIDATION\n"
        f"priority: 500\nexecution_mode: AUTOMATIC\nwhen: [all]\nthen: {{}}\n"
        f"required_inputs: [x]\ntest_case_ids: [only-one]\nvalidation_status: CANDIDATE\n"
        f"status: ACTIVE\nversion: 1.0\n---\n{rule_body}"
    )
    # 非法3：DSL 含危险操作
    bad_dsl = (
        f"---\nschema: rule/v1\nrule_id: RUL-002\nname: evil\nrule_type: ALERT\n"
        f"priority: 10\nexecution_mode: AUTOMATIC\n"
        f"when: [all]\nthen: {{action: \"$(rm -rf /)\"}}\n"
        f"required_inputs: [x]\ntest_case_ids: [a, b]\nvalidation_status: CANDIDATE\n"
        f"status: ACTIVE\nversion: 1.0\n---\n{rule_body}"
    )
    # 非法4：Decision 由系统以 OWNER 自动批准
    bad_decision = (
        f"---\nschema: review_decision/v1\ndecision_id: DC-BAD\ndecision: APPROVE\n"
        f"object_refs: [ENT-001]\ndecided_by: _system_auto\nrole: OWNER\n"
        f"decided_at: 2026-01-01T00:00:00Z\nreason: auto\nconditions: []\n"
        f"evidence_refs: []\nstatus: ACTIVE\nversion: 1.0\n"
        f"---\n# 审核决定\n\n## 决定描述\n\n## 条件\n\n## 依据\n\n## 变更记录\n"
    )
    return {
        "schema-mismatch.md": bad_schema,
        "rule-missing-tests.md": bad_rule,
        "rule-dangerous-dsl.md": bad_dsl,
        "auto-owner-decision.md": bad_decision,
    }


def main(out: str):
    out_dir = Path(out)
    legal = out_dir / "legal"
    illegal = out_dir / "illegal"
    legal.mkdir(parents=True, exist_ok=True)
    illegal.mkdir(parents=True, exist_ok=True)
    for name, text in legal_samples().items():
        (legal / name).write_text(text, encoding="utf-8")
    for name, text in illegal_samples().items():
        (illegal / name).write_text(text, encoding="utf-8")
    index = f"# Seeds\n\n合法 {len(legal_samples())} 个，非法 {len(illegal_samples())} 个。\n"
    (out_dir / "README.md").write_text(index, encoding="utf-8")
    print(f"generated {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "seeds")