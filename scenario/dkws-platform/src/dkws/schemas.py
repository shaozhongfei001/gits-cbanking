"""DKWS-SPEC-001 §9 契约化 Markdown Schema 注册（第一部分：核心文件类型）。"""

from __future__ import annotations

import re

from .contract import FieldRule as F
from .contract import SCHEMAS, Schema, register, validate_dsl  # noqa: F401

_T = "timestamp"
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_VER_RE = re.compile(r"^v?\d+(\.\d+)*$")

_ACTIVE = ["ACTIVE", "INACTIVE", "SUPERSEDED"]
_VALID_STATUS = ["CANDIDATE", "IN_REVIEW", "APPROVED", "REJECTED", "PUBLISHED", "PENDING"]


def _chk_hash(v, b, key):
    val = v.get(key)
    if isinstance(val, str) and not _HASH_RE.match(val):
        return [f"字段 {key} 非法 SHA-256（必须为 64 位十六进制）"]
    if isinstance(val, list):
        return [f"{key}[{i}] 非法 SHA-256" for i, x in enumerate(val) if not _HASH_RE.match(str(x))]
    return []


def _chk_version(v, _b):
    val = v.get("version")
    if val and not _VER_RE.match(str(val)):
        return [f"字段 version 非法（应匹配 {_VER_RE.pattern}）"]
    return []


_HEAD_MANIFEST = ["# 清单", "## 摘要", "## 文件列表", "## 校验信息"]
_HEAD_DOCUMENT = ["# 文档", "## 摘要", "## 内容范围", "## 版本记录"]
_HEAD_NORMALIZED = ["# 规范化文本", "## 规范化说明", "## 原文链接", "## 清理清单"]
_HEAD_SEGMENT = ["# 片段", "## 内容", "## 清洗记录", "## 来源"]
_HEAD_ENTITY = ["# 实体", "## 描述", "## 来源证据", "## 冲突与限定", "## 审核说明"]
_HEAD_RELATION = ["# 关系", "## 描述", "## 来源证据", "## 冲突与限定", "## 审核说明"]
_HEAD_STATEMENT = ["# 声明", "## 规范表达", "## 来源证据", "## 冲突与限定", "## 审核说明"]
_HEAD_RULE = ["# 规则", "## 业务解释", "## 输入与输出", "## 证据", "## 人工责任边界", "## 测试说明"]


def _chk_rule(v, _body):
    errs = []
    errs += _chk_version(v, _body)
    if not (0 <= int(v.get("priority", 0)) <= 1000):
        errs.append("rule.priority 必须在 0..1000")
    if not (isinstance(v.get("test_case_ids"), list) and len(v["test_case_ids"]) >= 2):
        errs.append("rule.test_case_ids 至少需正向、反向各一个")
    errs += validate_dsl(v.get("when", {}))
    errs += validate_dsl(v.get("then", {}))
    if v.get("else") is not None:
        errs += validate_dsl(v["else"])
    return errs


register(Schema(
    name="MANIFEST", contract="manifest/v1",
    path_regex=r"/01_raw/(nodes|payroll|knowledge)/[^/]+/MANIFEST\.md$",
    fields=[
        F("schema", "string", True), F("batch_id", "string", True),
        F("domain", "enum", True, enum=["nodes", "payroll", "knowledge"]),
        F("source_type", "enum", True, enum=["TEXT", "CSV", "JSON", "JSONL", "TABLE", "IMAGE", "AUDIO", "VIDEO"]),
        F("media_type", "string", True), F("file_count", "integer", True),
        F("total_bytes", "integer", True), F("content_sha256", "string", True),
        F("idempotency_key", "string", True), F("received_at", _T, True),
        F("status", "enum", False, enum=["OPEN", "CLOSED", "REJECTED"], default="OPEN"),
        F("size_bytes", "integer", False, default=0), F("version", "string", False),
    ],
    required_headings=_HEAD_MANIFEST,
    check=lambda v, b: _chk_hash(v, b, "content_sha256"),
))

register(Schema(
    name="DOCUMENT", contract="document/v1",
    path_regex=r"/01_raw/(nodes|payroll|knowledge)/D/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("document_id", "string", True), F("name", "string", True),
        F("source_file", "string", True),
        F("language", "enum", True, enum=["zh", "en", "pseudo"]),
        F("doc_type", "string", True),
        F("classification", "enum", True, enum=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]),
        F("owner", "string", True), F("tags", "list[string]", False),
        F("page_count", "integer", False), F("extracted_at", _T, True),
        F("source_document_id", "string", False), F("version", "string", False),
    ],
    required_headings=_HEAD_DOCUMENT,
))

register(Schema(
    name="NORMALIZED", contract="normalized_document/v1",
    path_regex=r"/02_work/U/[^/]+/NORMALIZED\.md$",
    fields=[
        F("schema", "string", True), F("normalized_id", "string", True),
        F("source_document_id", "string", True), F("normalized_at", _T, True),
        F("rules_used", "list[string]", True), F("textsha256", "string", True),
        F("token_count", "integer", False), F("version", "string", False),
    ],
    required_headings=_HEAD_NORMALIZED,
    check=lambda v, b: _chk_hash(v, b, "textsha256") + _chk_version(v, b),
))

register(Schema(
    name="SEGMENT", contract="segment/v1",
    path_regex=r"/02_work/U/[^/]+/segments/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("segment_id", "string", True),
        F("document_id", "string", True), F("normalized_id", "string", True),
        F("segment_type", "enum", True, enum=["HEADING", "PARAGRAPH", "TABLE", "LIST", "CODE", "FIGURE_CAPTION"]),
        F("heading_path", "string", True), F("page_from", "integer", True),
        F("page_to", "integer", True), F("sequence", "integer", True),
        F("content_sha256", "string", True), F("char_count", "integer", False, default=0),
        F("version", "string", False),
    ],
    required_headings=_HEAD_SEGMENT,
    check=lambda v, b: _chk_hash(v, b, "content_sha256"),
))

register(Schema(
    name="ENTITY", contract="entity/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/entities/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("entity_id", "string", True), F("entity_type", "string", True),
        F("name", "string", True), F("aliases", "list[string]", True), F("description", "string", False),
        F("domain", "string", True), F("canonical_id", "string", False), F("attributes", "map", False),
        F("source_document_ids", "list[string]", True), F("first_seen_at", _T, True),
        F("validation_status", "enum", True, enum=_VALID_STATUS),
        F("conflict_status", "enum", True, enum=["NONE", "POTENTIAL", "CONFIRMED", "RESOLVED"]),
        F("effective_from", "date", False), F("effective_to", "date", False),
        F("recorded_at", _T, True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True), F("source_segment_ids", "list[string]", False),
    ],
    required_headings=_HEAD_ENTITY,
    check=_chk_version,
))

register(Schema(
    name="RELATION", contract="relation/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/relations/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("relation_id", "string", True),
        F("source_id", "string", True), F("target_id", "string", True),
        F("relation_type", "string", True), F("direction", "enum", True, enum=["DIRECTED", "UNDIRECTED"]),
        F("statement_id", "string", True), F("aliases", "list[string]", False),
        F("validated", "boolean", True), F("source_entity_type", "string", False),
        F("target_entity_type", "string", False), F("source_document_ids", "list[string]", True),
        F("first_seen_at", _T, True), F("validation_status", "enum", True, enum=_VALID_STATUS),
        F("conflict_status", "enum", True, enum=["NONE", "POTENTIAL", "CONFIRMED", "RESOLVED"]),
        F("effective_from", "date", False), F("effective_to", "date", False),
        F("recorded_at", _T, True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_RELATION,
    check=_chk_version,
))

register(Schema(
    name="STATEMENT", contract="statement/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/statements/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("statement_id", "string", True), F("subject_id", "string", True),
        F("predicate", "string", True), F("object_value", "string", True),
        F("value_type", "enum", True, enum=["STRING", "NUMBER", "BOOLEAN", "DATE", "ENTITY_ID", "ENTITY_TYPE"]),
        F("object_entity_id", "string", False), F("object_unit", "string", False),
        F("derived", "enum", True, enum=["NATIVE", "DERIVED"]),
        F("derivation_rule_id", "string", False, condition="derived==DERIVED"),
        F("confidence", "number", False, condition="derived==DERIVED"),
        F("polarity", "enum", True, enum=["AFFIRMED", "NEGATED", "UNCERTAIN"]),
        F("validation_status", "enum", True, enum=_VALID_STATUS),
        F("conflict_status", "enum", True, enum=["NONE", "POTENTIAL", "CONFIRMED", "RESOLVED"]),
        F("effective_from", "date", False), F("effective_to", "date", False),
        F("recorded_at", _T, True), F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
        F("source_document_ids", "list[string]", False), F("source_segment_ids", "list[string]", False),
    ],
    required_headings=_HEAD_STATEMENT,
    check=_chk_version,
))

register(Schema(
    name="RULE", contract="rule/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/rules/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("rule_id", "string", True), F("name", "string", True),
        F("rule_type", "enum", True, enum=["VALIDATION", "ELIGIBILITY", "CALCULATION", "RECOMMENDATION", "ROUTING", "ALERT"]),
        F("priority", "integer", True),
        F("execution_mode", "enum", True, enum=["AUTOMATIC", "ADVISORY", "HUMAN_CONFIRM_REQUIRED"]),
        F("when", "expression", True), F("then", "object", True), F("else", "object", False),
        F("required_inputs", "list[string]", True),
        F("source_document_id", "string", False), F("source_segment_id", "string", False),
        F("test_case_ids", "list[string]", True),
        F("validation_status", "enum", True, enum=_VALID_STATUS),
        F("status", "enum", True, enum=_ACTIVE), F("effective_from", "date", False),
        F("effective_to", "date", False), F("version", "string", True),
    ],
    required_headings=_HEAD_RULE,
    check=_chk_rule,
))

# --------------------------------------------------------------- 控制层 / 服务层（§9.9-§9.25）

_HEAD_CATALOG = ["# 资产", "## 业务定义", "## 内容范围", "## 上下游", "## 使用限制", "## 变更记录"]
_HEAD_SCHEMA = ["# Schema", "## 目的", "## 字段定义", "## 交叉字段约束", "## 兼容策略", "## 合法示例", "## 非法示例"]
_HEAD_LINEAGE = ["# 血缘记录", "## 转换说明", "## 输入", "## 输出", "## 已知限制"]
_HEAD_RELEASE = ["# 发布记录", "## 摘要", "## 资产清单", "## 质量门禁结果", "## 回滚说明"]
_HEAD_CURRENT = ["# 当前活动版本", "## 切换说明", "## 回滚说明"]
_HEAD_REPORT = ["# 运行报告", "## 执行摘要", "## 输入与输出", "## 质量结果", "## 警告与错误", "## 可复现信息", "## 非声明事项"]
_HEAD_STATUS = ["# 任务状态", "## 当前摘要", "## 输入输出", "## 错误与恢复建议"]
_HEAD_VOCAB = ["# 术语", "## 定义", "## 使用约束", "## 示例", "## 变更记录"]
_HEAD_MAPPING = ["# 映射", "## 字段映射", "## 键策略", "## 空值与拒绝策略", "## 变更记录"]
_HEAD_POLICY = ["# 处理策略", "## 参数说明", "## 输入输出", "## 确定性与可重复性", "## 变更记录"]
_HEAD_PACK = ["# 知识包", "## 引用闭包", "## 使用说明", "## 变更记录"]
_HEAD_SERVICE = ["# 服务", "## 服务目的", "## 输入输出", "## 数据与知识范围", "## 限制和责任边界", "## 示例"]
_HEAD_DECISION = ["# 审核决定", "## 决定描述", "## 条件", "## 依据", "## 变更记录"]
_HEAD_PROJECTION = ["# 投影", "## 说明", "## 文件清单", "## 逻辑哈希", "## 校验信息"]


def _chk_lineage_io(v, _body):
    errs = []
    for io in ("inputs", "outputs"):
        for i, item in enumerate(v.get(io) or []):
            if not isinstance(item, dict):
                errs.append(f"{io}[{i}] 必须是对象")
                continue
            for fld in ("asset_id", "version", "path", "content_hash"):
                if fld not in item:
                    errs.append(f"{io}[{i}].{fld} 缺失")
            h = item.get("content_hash")
            if h and not _HASH_RE.match(str(h)):
                errs.append(f"{io}[{i}].content_hash 非法 SHA-256")
    return errs


def _chk_release(v, _body):
    errs = []
    for i, item in enumerate(v.get("asset_manifest") or []):
        if not isinstance(item, dict):
            errs.append(f"asset_manifest[{i}] 必须是对象")
            continue
        for fld in ("path", "schema", "business_id", "asset_version", "sha256"):
            if fld not in item:
                errs.append(f"asset_manifest[{i}].{fld} 缺失")
        if not _HASH_RE.match(str(item.get("sha256", ""))):
            errs.append(f"asset_manifest[{i}].sha256 非法 SHA-256")
    return errs


def _chk_decision(v, _body):
    errs = []
    if v.get("role") in ("OWNER", "INDEPENDENT_QA") and v.get("decided_by") == "_system_auto":
        errs.append("§9.19: 系统不得根据提交者身份自动生成 OWNER / INDEPENDENT_QA 批准决定")
    return errs


def _chk_job_status(v, _body):
    errs = []
    if not (0 <= int(v.get("progress", 0)) <= 100):
        errs.append("job_status.progress 必须在 0..100")
    if v.get("status") in ("COMPLETED", "FAILED", "CANCELLED", "BLOCKED") and not v.get("finished_at"):
        errs.append("job_status 终态必须填写 finished_at")
    return errs


register(Schema(
    name="CATALOG", contract="asset_catalog/v1",
    path_regex=r"/90_control/catalog/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("asset_id", "string", True),
        F("asset_type", "enum", True, enum=["DATASET", "DOCUMENT_COLLECTION", "ENTITY_SET", "RELATION_SET",
            "STATEMENT_SET", "RULE_SET", "KNOWLEDGE_PACK", "SERVICE", "PROJECTION"]),
        F("name", "string", True), F("domain", "string", True), F("owner", "string", True),
        F("classification", "enum", True, enum=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]),
        F("authoritative_layer", "string", True), F("current_version", "string", True),
        F("location", "string", True), F("upstream_ids", "list[string]", True),
        F("downstream_ids", "list[string]", True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_CATALOG,
    check=_chk_version,
))

register(Schema(
    name="SCHEMA_CONTRACT", contract="schema_contract/v1",
    path_regex=r"/90_control/schema/[^/]+/v\d+/SCHEMA\.md$",
    fields=[
        F("schema", "string", True), F("schema_id", "string", True), F("target_schema", "string", True),
        F("major_version", "integer", True),
        F("compatibility", "enum", True, enum=["BACKWARD_COMPATIBLE", "FORWARD_COMPATIBLE", "FULL", "NONE"]),
        F("primary_id_field", "string", True), F("required_fields", "list[string]", True),
        F("allowed_fields", "list[string]", True), F("enums", "map", False),
        F("reference_fields", "list[string]", False), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_SCHEMA,
    check=_chk_version,
))

register(Schema(
    name="LINEAGE", contract="lineage/v1",
    path_regex=r"/90_control/lineage/[^/]+/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("lineage_id", "string", True), F("process_id", "string", True),
        F("job_id", "string", True), F("inputs", "list[object]", True), F("outputs", "list[object]", True),
        F("transformation_id", "string", True), F("transformation_version", "string", True),
        F("code_version", "string", True), F("started_at", _T, True), F("finished_at", _T, True),
        F("status", "enum", True, enum=["SUCCEEDED", "FAILED", "PARTIAL"]), F("version", "string", True),
    ],
    required_headings=_HEAD_LINEAGE,
    check=lambda v, b: _chk_lineage_io(v, b) + _chk_version(v, b),
))

register(Schema(
    name="QUALITY_RULE", contract="quality_rule/v1",
    path_regex=r"/90_control/quality/rules/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("quality_rule_id", "string", True), F("name", "string", True),
        F("target_schema", "string", True), F("target_asset", "string", False),
        F("dimension", "enum", True, enum=["COMPLETENESS", "UNIQUENESS", "VALIDITY", "CONSISTENCY",
            "REFERENTIAL_INTEGRITY", "TRACEABILITY", "FRESHNESS", "SECURITY"]),
        F("severity", "enum", True, enum=["BLOCKER", "MAJOR", "MINOR", "NOTE"]),
        F("expression", "expression", True), F("threshold", "number", True),
        F("on_failure", "enum", True, enum=["BLOCK", "QUARANTINE", "WARN"]),
        F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    check=lambda v, b: _chk_version(v, b) + validate_dsl(v.get("expression", {})),
))

register(Schema(
    name="QUALITY_RESULT", contract="quality_result/v1",
    path_regex=r"/02_work/Q/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("quality_result_id", "string", True),
        F("quality_rule_id", "string", True), F("quality_rule_version", "string", True),
        F("job_id", "string", True), F("target_asset", "string", True),
        F("target_asset_version", "string", True), F("evaluated_count", "integer", True),
        F("failed_count", "integer", True), F("sample_failures", "list[string]", True),
        F("result", "enum", True, enum=["PASS", "WARN", "FAIL"]), F("executed_at", _T, True),
        F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    required_headings=["# 质量结果", "## 失败摘要", "## 修复责任"],
))

register(Schema(
    name="JOB_STATUS", contract="job_status/v1",
    path_regex=r"/90_control/jobs/[^/]+/STATUS\.md$",
    fields=[
        F("schema", "string", True), F("job_id", "string", True), F("job_type", "string", True),
        F("status", "enum", True, enum=["PENDING", "RUNNING", "VALIDATING", "COMPLETED", "FAILED",
            "CANCELLED", "CANCEL_REQUESTED", "RETRYING", "BLOCKED"]),
        F("requested_by", "string", True), F("idempotency_key", "string", True),
        F("input_refs", "list[object]", True), F("output_refs", "list[object]", True),
        F("started_at", _T, True), F("updated_at", _T, True), F("finished_at", "timestamp", False),
        F("progress", "integer", True), F("error_code", "string", False), F("error_message", "string", False),
        F("retry_of", "string", False),
        F("publish_status", "enum", True, enum=["NOT_APPLICABLE", "NOT_PUBLISHED", "PUBLISHED"]),
        F("version", "string", True),
    ],
    required_headings=_HEAD_STATUS,
    check=_chk_job_status,
))

register(Schema(
    name="RUN_REPORT", contract="run_report/v1",
    path_regex=r"/90_control/jobs/[^/]+/RUN_REPORT\.md$",
    fields=[
        F("schema", "string", True), F("job_id", "string", True),
        F("final_status", "enum", True, enum=["COMPLETED", "FAILED", "CANCELLED"]),
        F("started_at", _T, True), F("finished_at", _T, True), F("duration_ms", "integer", True),
        F("input_count", "integer", True), F("output_count", "integer", True),
        F("rejected_count", "integer", True), F("warning_count", "integer", True),
        F("error_count", "integer", True), F("quality_summary", "map", False),
        F("log_sha256", "string", True), F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    required_headings=_HEAD_REPORT,
    check=lambda v, b: _chk_hash(v, b, "log_sha256") + _chk_version(v, b),
))

register(Schema(
    name="RELEASE", contract="release/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/RELEASE\.md$",
    fields=[
        F("schema", "string", True), F("release_id", "string", True), F("domain", "string", True),
        F("release_version", "string", True), F("previous_version", "string", False),
        F("asset_manifest", "list[object]", True), F("quality_gate_results", "list[string]", True),
        F("approval_decision_ids", "list[string]", True),
        F("released_by", "string", True), F("released_at", _T, True),
        F("status", "enum", True, enum=["PUBLISHED", "REVOKED"]), F("version", "string", True),
    ],
    required_headings=_HEAD_RELEASE,
    check=lambda v, b: _chk_release(v, b) + _chk_version(v, b),
))

register(Schema(
    name="CURRENT", contract="current_pointer/v1",
    path_regex=r"/(03_core/[^/]+|04_serve/[^/]+)/CURRENT\.md$",
    fields=[
        F("schema", "string", True), F("scope_type", "enum", True, enum=["CORE_DOMAIN", "SERVICE"]),
        F("scope_id", "string", True), F("target_version", "string", True),
        F("target_release_id", "string", True), F("target_manifest_sha256", "string", True),
        F("switched_by", "string", True), F("switched_at", _T, True), F("reason", "string", True),
        F("status", "enum", True, enum=["ACTIVE"]), F("version", "string", True),
    ],
    required_headings=_HEAD_CURRENT,
    check=lambda v, b: _chk_hash(v, b, "target_manifest_sha256") + _chk_version(v, b),
))

register(Schema(
    name="PROJECTION", contract="projection/v1",
    path_regex=r"/04_serve/[^/]+/version=[^/]+/PROJECTION\.md$",
    fields=[
        F("schema", "string", True), F("projection_id", "string", True), F("service_id", "string", True),
        F("projection_version", "string", True), F("source_core_releases", "list[string]", True),
        F("builder_id", "string", True), F("builder_version", "string", True),
        F("configuration_hash", "string", True), F("files", "list[string]", True),
        F("logical_hashes", "list[object]", True), F("built_at", _T, True),
        F("verification_status", "enum", True, enum=["VERIFIED", "UNVERIFIED", "FAILED"]),
        F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    required_headings=_HEAD_PROJECTION,
    check=lambda v, b: _chk_hash(v, b, "configuration_hash"),
))

register(Schema(
    name="DECISION", contract="review_decision/v1",
    path_regex=r"/90_control/decisions/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("decision_id", "string", True),
        F("object_refs", "list[string]", True),
        F("decision", "enum", True, enum=["APPROVE", "REJECT", "REQUEST_CHANGES", "WAIVE"]),
        F("decided_by", "string", True),
        F("role", "enum", True, enum=["OWNER", "INDEPENDENT_QA", "TECH_LEAD", "FEATURE_PILOT", "E2E_OWNER", "DATA_OWNER"]),
        F("decided_at", _T, True), F("reason", "string", True),
        F("conditions", "list[string]", False), F("evidence_refs", "list[string]", False),
        F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    required_headings=_HEAD_DECISION,
    check=lambda v, b: _chk_decision(v, b) + _chk_version(v, b),
))

register(Schema(
    name="VOCABULARY", contract="vocabulary_term/v1",
    path_regex=r"/90_control/schema/vocabulary/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("term_id", "string", True),
        F("term_kind", "enum", True, enum=["ENTITY_TYPE", "RELATION_TYPE", "PREDICATE", "CODE", "UNIT"]),
        F("name", "string", True), F("definition", "string", True), F("domain", "string", True),
        F("parent_term_id", "string", False), F("aliases", "list[string]", False),
        F("allowed_source_types", "list[string]", False),
        F("source_entity_types", "list[string]", False, condition="term_kind==RELATION_TYPE"),
        F("target_entity_types", "list[string]", False, condition="term_kind==RELATION_TYPE"),
        F("symmetric", "boolean", False), F("transitive", "boolean", False),
        F("allow_self_loop", "boolean", False),
        F("value_types", "list[string]", False, condition="term_kind==PREDICATE"),
        F("cardinality", "string", False),
        F("unit_terms", "list[string]", False),
        F("status", "enum", True, enum=_ACTIVE), F("version", "string", True),
    ],
    required_headings=_HEAD_VOCAB,
    check=_chk_version,
))

register(Schema(
    name="DATA_MAPPING", contract="data_mapping/v1",
    path_regex=r"/90_control/schema/mappings/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("mapping_id", "string", True),
        F("source_schema", "string", True), F("target_schema", "string", True),
        F("field_mappings", "list[object]", True),
        F("key_policy", "string", True), F("null_policy", "string", True),
        F("reject_policy", "string", True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_MAPPING,
    check=_chk_version,
))

register(Schema(
    name="PROCESSING_POLICY", contract="processing_policy/v1",
    path_regex=r"/90_control/schema/policies/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("policy_id", "string", True),
        F("policy_kind", "enum", True, enum=["PARSE", "NORMALIZE", "CHUNK", "EXTRACT", "EMBED", "RANK"]),
        F("implementation_id", "string", True), F("implementation_version", "string", True),
        F("parameters", "object", False), F("input_schemas", "list[string]", True),
        F("output_schemas", "list[string]", True), F("deterministic", "boolean", True),
        F("provider_adapter", "string", False), F("model_id", "string", False),
        F("model_version", "string", False), F("prompt_template_id", "string", False),
        F("temperature", "number", False), F("seed", "integer", False),
        F("response_schema", "string", False), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_POLICY,
    check=_chk_version,
))

register(Schema(
    name="KNOWLEDGE_PACK", contract="knowledge_pack/v1",
    path_regex=r"/03_core/[^/]+/version=[^/]+/packs/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("knowledge_pack_id", "string", True), F("name", "string", True),
        F("domain", "string", True), F("intended_consumers", "list[string]", True),
        F("entity_ids", "list[string]", True), F("relation_ids", "list[string]", True),
        F("statement_ids", "list[string]", True), F("rule_ids", "list[string]", True),
        F("document_ids", "list[string]", True), F("scope_filters", "list[string]", False),
        F("source_release_ids", "list[string]", True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_PACK,
    check=_chk_version,
))

register(Schema(
    name="SERVICE_CATALOG", contract="service_catalog/v1",
    path_regex=r"/90_control/catalog/services/[^/]+\.md$",
    fields=[
        F("schema", "string", True), F("service_id", "string", True), F("name", "string", True),
        F("service_type", "enum", True, enum=["DATA_QUERY", "EXTRACTION", "SEARCH", "GRAPH", "RULE", "EVIDENCE", "CATALOG"]),
        F("input_contract", "string", True), F("output_contract", "string", True),
        F("source_projection_id", "string", True), F("authorization_policy", "string", True),
        F("limits", "object", False), F("sla_class", "string", False),
        F("current_version", "string", True), F("status", "enum", True, enum=_ACTIVE),
        F("version", "string", True),
    ],
    required_headings=_HEAD_SERVICE,
    check=_chk_version,
))