"""P1 契约化 Markdown 框架测试：frontmatter、schema、DSL、非法样例拒绝。"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dkws.contract import (  # noqa: E402
    Schema, FieldRule as F, parse_frontmatter, validate_headings, validate_dsl,
    resolve_by_contract, validate_text,
)
from dkws.errors import ContractError
from dkws import schemas  # noqa: F401,E402  触发注册


class TestParseFrontmatter(unittest.TestCase):
    def test_parse_valid(self):
        text = "---\nschema: foo/v1\nbatch_id: B1\n---\nbody"
        data, body = parse_frontmatter(text)
        self.assertEqual(data["batch_id"], "B1")
        self.assertEqual(body, "body")

    def test_missing_delimiter(self):
        with self.assertRaises(ContractError):
            parse_frontmatter("no delimiter")

    def test_unclosed(self):
        with self.assertRaises(ContractError):
            parse_frontmatter("---\nschema: x\n")

    def test_non_dict_frontmatter(self):
        with self.assertRaises(ContractError):
            parse_frontmatter("---\n- a\n- b\n---\nbody")

    def test_bom_handling(self):
        text = "\ufeff---\nfoo: 1\n---\nbody"
        data, _ = parse_frontmatter(text)
        self.assertEqual(data["foo"], 1)


class TestSchemaValidation(unittest.TestCase):
    def test_manifest_legal_sample(self):
        s = resolve_by_contract("manifest/v1")
        text = (
            "---\nschema: manifest/v1\nbatch_id: B1\ndomain: nodes\n"
            "source_type: CSV\nmedia_type: text/csv\nfile_count: 2\n"
            "total_bytes: 100\ncontent_sha256: " + "a" * 64 + "\n"
            "idempotency_key: k1\nreceived_at: 2026-01-01T00:00:00Z\n"
            "status: OPEN\n---\n# 清单\n## 摘要\nx\n## 文件列表\nx\n## 校验信息\nx\n"
        )
        values = validate_text(text, s)
        self.assertEqual(values["domain"], "nodes")
        self.assertEqual(values["status"], "OPEN")

    def test_manifest_missing_required(self):
        s = resolve_by_contract("manifest/v1")
        text = "---\nschema: manifest/v1\n---\n"
        with self.assertRaises(ContractError):
            validate_text(text, s)

    def test_manifest_bad_hash(self):
        s = resolve_by_contract("manifest/v1")
        text = (
            "---\nschema: manifest/v1\nbatch_id: B1\ndomain: nodes\n"
            "source_type: CSV\nmedia_type: text/csv\nfile_count: 2\n"
            "total_bytes: 100\ncontent_sha256: notahash\n"
            "idempotency_key: k1\nreceived_at: 2026-01-01T00:00:00Z\n---\n"
        )
        with self.assertRaises(ContractError):
            validate_text(text, s)

    def test_manifest_bad_domain_enum(self):
        s = resolve_by_contract("manifest/v1")
        text = (
            "---\nschema: manifest/v1\nbatch_id: B1\ndomain: bogus\n"
            "source_type: CSV\nmedia_type: text/csv\nfile_count: 1\n"
            "total_bytes: 10\ncontent_sha256: " + "a" * 64 + "\n"
            "idempotency_key: k\nreceived_at: t\n---\n"
        )
        with self.assertRaises(ContractError):
            validate_text(text, s)

    def test_missing_headings(self):
        s = resolve_by_contract("manifest/v1")
        text = (
            "---\nschema: manifest/v1\nbatch_id: B1\ndomain: nodes\n"
            "source_type: CSV\nmedia_type: text/csv\nfile_count: 1\n"
            "total_bytes: 10\ncontent_sha256: " + "a" * 64 + "\n"
            "idempotency_key: k\nreceived_at: t\n---\n# 清单\nno subsections\n"
        )
        with self.assertRaises(ContractError):
            validate_text(text, s)

    def test_statement_derived_condition(self):
        s = resolve_by_contract("statement/v1")
        text = (
            "---\nschema: statement/v1\nstatement_id: S1\nsubject_id: E1\npredicate: owns\n"
            "object_value: x\nvalue_type: STRING\nobject_entity_id: ''\nobject_unit: ''\n"
            "derived: DERIVED\npolarity: AFFIRMED\nvalidation_status: CANDIDATE\n"
            "conflict_status: NONE\nrecorded_at: t\nstatus: ACTIVE\nversion: 1.0\n"
            "source_document_ids: []\n---\n"
        )
        # derived==DERIVED 但缺 derivation_rule_id/confidence -> 条件必填报错
        with self.assertRaises(ContractError):
            validate_text(text, s)


class TestHeadingValidation(unittest.TestCase):
    def test_headings_order(self):
        body = "## 摘要\ntext\n## 文件列表\nx\n## 校验信息\nx\n"
        self.assertEqual(validate_headings(body, ["摘要", "文件列表", "校验信息"]), [])

    def test_missing(self):
        body = "## 摘要\nx\n"
        self.assertEqual(validate_headings(body, ["摘要", "文件列表"]), ["文件列表"])


class TestDslValidation(unittest.TestCase):
    def test_safe_dsl(self):
        errs = validate_dsl(["all", ["eq", "input.amount", 100], ["exists", "input.x"]])
        self.assertEqual(errs, [])

    def test_dangerous_shell(self):
        errs = validate_dsl(["then", {"action": "$(rm -rf /)"}])
        self.assertTrue(any("禁止" in e for e in errs))

    def test_unknown_keyword(self):
        errs = validate_dsl(["all", ["printf", 1]])
        self.assertTrue(any("未知 DSL" in e for e in errs))


class TestSchemaVarieties(unittest.TestCase):
    def test_all_registered(self):
        expected = ["MANIFEST", "DOCUMENT", "NORMALIZED", "SEGMENT", "ENTITY",
                    "RELATION", "STATEMENT", "RULE", "CATALOG", "SCHEMA_CONTRACT",
                    "LINEAGE", "QUALITY_RULE", "QUALITY_RESULT", "JOB_STATUS",
                    "RUN_REPORT", "RELEASE", "CURRENT", "PROJECTION", "DECISION",
                    "VOCABULARY", "KNOWLEDGE_PACK", "SERVICE_CATALOG"]
        import dkws.schemas as sc
        for name in expected:
            self.assertIn(name, sc.SCHEMAS, f"schema {name} 未注册")


if __name__ == "__main__":
    unittest.main()