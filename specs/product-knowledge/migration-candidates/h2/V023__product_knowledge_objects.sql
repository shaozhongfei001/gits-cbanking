-- 1. 源文档（可变：allowed_claim_types 可由 Owner 调整）
CREATE TABLE pk_source_document (
    source_id            VARCHAR(64)   NOT NULL,
    zone                 VARCHAR(32)   NOT NULL,
    product_family       VARCHAR(32),
    allowed_claim_types  VARCHAR(255)  NOT NULL,
    authority_level      VARCHAR(32)   NOT NULL,
    registry_status      VARCHAR(32)   NOT NULL,
    created_at           TIMESTAMP WITH TIME ZONE       NOT NULL,
    updated_at           TIMESTAMP WITH TIME ZONE       NOT NULL,
    CONSTRAINT pk_source_document_pk PRIMARY KEY (source_id),
    CONSTRAINT pk_sd_zone_ck CHECK (zone IN ('_authoritative','_public_reference')),
    CONSTRAINT pk_sd_status_ck CHECK (registry_status IN
        ('REGISTERED','PENDING_SOURCE','AVAILABLE','PARSED','CLAUSE_VERIFIED','RETIRED'))
);

-- 2. 源版本（不可变）
CREATE TABLE pk_source_version (
    source_version_id  VARCHAR(128)  NOT NULL,
    source_id          VARCHAR(64)   NOT NULL,
    bytes_sha256       CHAR(64)   NOT NULL,
    byte_size          BIGINT     NOT NULL,
    page_count         INT,
    ingested_at        TIMESTAMP WITH TIME ZONE       NOT NULL,
    superseded_by      VARCHAR(128),
    provenance_url     VARCHAR(1024),
    provenance_state   VARCHAR(32)   NOT NULL DEFAULT 'UNVERIFIED',
    CONSTRAINT pk_source_version_pk PRIMARY KEY (source_version_id),
    CONSTRAINT pk_sv_source_fk FOREIGN KEY (source_id) REFERENCES pk_source_document(source_id),
    CONSTRAINT pk_sv_prov_ck CHECK (provenance_state IN
        ('VERIFIED','UNVERIFIED','CONFLICTING_EVIDENCE','DEMO'))
);
CREATE UNIQUE INDEX pk_sv_hash_uq ON pk_source_version(source_id, bytes_sha256);

-- 3. 片段（不可变）
CREATE TABLE pk_fragment (
    fragment_id        VARCHAR(128) NOT NULL,
    source_version_id  VARCHAR(128) NOT NULL,
    seq_no             INT       NOT NULL,
    page_no            INT,
    content_text       CLOB     NOT NULL,
    content_sha256     CHAR(64)  NOT NULL,
    CONSTRAINT pk_fragment_pk PRIMARY KEY (fragment_id),
    CONSTRAINT pk_frg_sv_fk FOREIGN KEY (source_version_id)
        REFERENCES pk_source_version(source_version_id)
);

-- 4. 证据跨度（不可变）— CTR-PK-EVS-002
CREATE TABLE pk_evidence_span (
    evidence_id        VARCHAR(128) NOT NULL,
    source_id          VARCHAR(64)  NOT NULL,
    source_version_id  VARCHAR(128) NOT NULL,
    fragment_id        VARCHAR(128) NOT NULL,
    locator_kind       VARCHAR(16)  NOT NULL,
    locator_json       CLOB     NOT NULL,
    quote              CLOB     NOT NULL,
    quote_sha256       CHAR(64)  NOT NULL,
    usage_type         VARCHAR(24)  NOT NULL,
    authority_level    VARCHAR(32)  NOT NULL,
    claim_type         VARCHAR(16)  NOT NULL,
    scope_json         CLOB     NOT NULL,
    extraction_run_id  VARCHAR(64)  NOT NULL,
    clause_verified    BOOLEAN    NOT NULL DEFAULT FALSE,
    retrieved_at       TIMESTAMP WITH TIME ZONE      NOT NULL,
    source_path        VARCHAR(512) NOT NULL,
    CONSTRAINT pk_evidence_span_pk PRIMARY KEY (evidence_id),
    CONSTRAINT pk_evs_frg_fk FOREIGN KEY (fragment_id) REFERENCES pk_fragment(fragment_id),
    CONSTRAINT pk_evs_usage_ck CHECK (usage_type IN ('AUTHORITATIVE','VERIFICATION_ONLY')),
    CONSTRAINT pk_evs_claim_ck CHECK (claim_type IN
        ('PRICE','ELIGIBILITY','PROCESS','RISK','REGULATORY')),
    CONSTRAINT pk_evs_locator_ck CHECK (locator_kind IN ('PAGE_BBOX','CLAUSE','CHAR_RANGE')),
    CONSTRAINT pk_evs_zone_usage_ck CHECK (
        (source_path LIKE '01_raw/_public_reference/%' AND usage_type = 'VERIFICATION_ONLY')
     OR (source_path LIKE '01_raw/_authoritative/%'    AND usage_type = 'AUTHORITATIVE')),
    CONSTRAINT pk_evs_id_fmt_ck CHECK (evidence_id LIKE 'EVS-%')
);
CREATE INDEX pk_evs_source_idx ON pk_evidence_span(source_id);
CREATE INDEX pk_evs_usage_idx  ON pk_evidence_span(usage_type);
-- 5. 字段断言（不可变，值变更走 supersedes）— CTR-PK-ASM-001
CREATE TABLE pk_field_assertion (
    assertion_id          VARCHAR(128) NOT NULL,
    product_id            VARCHAR(32)  NOT NULL,
    product_version_scope VARCHAR(64)  NOT NULL,
    field_path            VARCHAR(128) NOT NULL,
    raw_value             CLOB,
    normalized_value      CLOB,
    value_type            VARCHAR(16)  NOT NULL,
    knowledge_state       VARCHAR(24)  NOT NULL,
    scope_json            CLOB     NOT NULL,
    conflict_id           VARCHAR(128),
    review_decision_id    VARCHAR(64),
    supersedes            VARCHAR(128),
    created_by_run_id     VARCHAR(64)  NOT NULL,
    created_at            TIMESTAMP WITH TIME ZONE      NOT NULL,
    CONSTRAINT pk_field_assertion_pk PRIMARY KEY (assertion_id),
    CONSTRAINT pk_asm_state_ck CHECK (knowledge_state IN
        ('CANDIDATE','EVIDENCE_VERIFIED','REVIEWED','SUPPORTED','REJECTED',
         'UNKNOWN','CONFLICT','NOT_APPLICABLE','STALE')),
    CONSTRAINT pk_asm_unknown_ck CHECK (
        knowledge_state <> 'UNKNOWN'
        OR (raw_value IS NULL AND normalized_value IS NULL)),
    CONSTRAINT pk_asm_conflict_val_ck CHECK (
        knowledge_state <> 'CONFLICT' OR normalized_value IS NULL),
    CONSTRAINT pk_asm_conflict_ref_ck CHECK (
        knowledge_state <> 'CONFLICT' OR conflict_id IS NOT NULL),
    CONSTRAINT pk_asm_na_ck CHECK (
        knowledge_state <> 'NOT_APPLICABLE' OR review_decision_id IS NOT NULL)
);
CREATE INDEX pk_asm_product_idx ON pk_field_assertion(product_id, field_path);
CREATE INDEX pk_asm_state_idx   ON pk_field_assertion(knowledge_state);

-- 5b. 断言 x 证据（多对多，不可变）
CREATE TABLE pk_assertion_evidence (
    assertion_id VARCHAR(128) NOT NULL,
    evidence_id  VARCHAR(128) NOT NULL,
    CONSTRAINT pk_assertion_evidence_pk PRIMARY KEY (assertion_id, evidence_id),
    CONSTRAINT pk_ae_asm_fk FOREIGN KEY (assertion_id)
        REFERENCES pk_field_assertion(assertion_id),
    CONSTRAINT pk_ae_evs_fk FOREIGN KEY (evidence_id)
        REFERENCES pk_evidence_span(evidence_id)
);

-- 6. 冲突案例 — CTR-PK-CNF-001
CREATE TABLE pk_conflict_case (
    conflict_id         VARCHAR(128)  NOT NULL,
    product_id          VARCHAR(32)   NOT NULL,
    field_path          VARCHAR(128)  NOT NULL,
    conflict_type       VARCHAR(32)   NOT NULL,
    status              VARCHAR(16)   NOT NULL,
    resolution_json     CLOB,
    detected_by_run_id  VARCHAR(64)   NOT NULL,
    detected_at         TIMESTAMP WITH TIME ZONE       NOT NULL,
    CONSTRAINT pk_conflict_case_pk PRIMARY KEY (conflict_id),
    CONSTRAINT pk_cnf_status_ck CHECK (status IN
        ('OPEN','UNDER_REVIEW','RESOLVED','DEFERRED')),
    CONSTRAINT pk_cnf_type_ck CHECK (conflict_type IN
        ('VALUE_MISMATCH','SCOPE_OVERLAP','AUTHORITY_TIE','TEMPORAL_AMBIGUITY','UNIT_MISMATCH')),
    CONSTRAINT pk_cnf_resolved_ck CHECK (status <> 'RESOLVED' OR resolution_json IS NOT NULL)
);

-- 7. 审核决议（不可变，只追加）
CREATE TABLE pk_review_decision (
    decision_id     VARCHAR(64)  NOT NULL,
    subject_kind    VARCHAR(32)  NOT NULL,
    subject_id      VARCHAR(128) NOT NULL,
    decision        VARCHAR(24)  NOT NULL,
    rationale       CLOB     NOT NULL,
    decided_by      VARCHAR(128) NOT NULL,
    decided_by_role VARCHAR(32)  NOT NULL,
    decided_at      TIMESTAMP WITH TIME ZONE      NOT NULL,
    CONSTRAINT pk_review_decision_pk PRIMARY KEY (decision_id),
    CONSTRAINT pk_dec_role_ck CHECK (decided_by_role IN
        ('PRODUCT_OWNER','RISK_OWNER','COMPLIANCE_OWNER'))
);
-- 8. 知识发布包（发布后不可变）— CTR-PK-RLS-001
CREATE TABLE pk_knowledge_release (
    release_id               VARCHAR(64) NOT NULL,
    taxonomy_version         VARCHAR(64) NOT NULL,
    lifecycle_state          VARCHAR(24) NOT NULL,
    interpretation_ready     BOOLEAN   NOT NULL DEFAULT FALSE,
    recommendation_ready     BOOLEAN   NOT NULL DEFAULT FALSE,
    assertion_manifest_hash  CHAR(64) NOT NULL,
    evidence_manifest_hash   CHAR(64) NOT NULL,
    card_projection_hash     CHAR(64) NOT NULL,
    rule_package_hash        CHAR(64) NOT NULL,
    bundle_hash              CHAR(64) NOT NULL,
    quality_run_id           VARCHAR(64) NOT NULL,
    is_stale                 BOOLEAN   NOT NULL DEFAULT FALSE,
    stale_reason             VARCHAR(512),
    stale_since              TIMESTAMP WITH TIME ZONE,
    gate_report_json         CLOB,
    published_at             TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_knowledge_release_pk PRIMARY KEY (release_id),
    CONSTRAINT pk_rls_state_ck CHECK (lifecycle_state IN
        ('DRAFT','REVIEW_READY','APPROVED','PUBLISHED','RETIRED')),
    CONSTRAINT pk_rls_implies_ck CHECK (
        recommendation_ready = FALSE OR interpretation_ready = TRUE),
    CONSTRAINT pk_rls_stale_ck CHECK (is_stale = FALSE OR stale_reason IS NOT NULL),
    CONSTRAINT pk_rls_prov_ck CHECK (provenance_state IN ('VERIFIED','DEMO')),
    CONSTRAINT pk_rls_demo_ck CHECK (
        provenance_state <> 'DEMO' OR recommendation_ready = FALSE)
);

CREATE TABLE pk_release_product (
    release_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    CONSTRAINT pk_release_product_pk PRIMARY KEY (release_id, product_id),
    CONSTRAINT pk_rp_rls_fk FOREIGN KEY (release_id)
        REFERENCES pk_knowledge_release(release_id)
);

-- 9. 变更事件（幂等去重）— CTR-PK-CHG-001
CREATE TABLE pk_change_event (
    event_id            VARCHAR(64)   NOT NULL,
    event_type          VARCHAR(32)   NOT NULL,
    previous_release_id VARCHAR(64),
    new_release_id      VARCHAR(64),
    impact_scope_json   CLOB,
    reason              VARCHAR(1024) NOT NULL,
    occurred_at         TIMESTAMP WITH TIME ZONE       NOT NULL,
    applied_at          TIMESTAMP WITH TIME ZONE,
    CONSTRAINT pk_change_event_pk PRIMARY KEY (event_id),
    CONSTRAINT pk_chg_type_ck CHECK (event_type IN
        ('RELEASE_PUBLISHED','RELEASE_RETIRED','RELEASE_STALED','SOURCE_VERSION_SUPERSEDED'))
);

-- 10. 字段策略 — CTR-PK-FLD-001
CREATE TABLE pk_field_policy (
    policy_id           VARCHAR(64)  NOT NULL,
    product_family      VARCHAR(32)  NOT NULL,
    policy_version      VARCHAR(32)  NOT NULL,
    owner_approved      BOOLEAN    NOT NULL DEFAULT FALSE,
    owner_decision_id   VARCHAR(64),
    fields_json         CLOB     NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE      NOT NULL,
    CONSTRAINT pk_field_policy_pk PRIMARY KEY (policy_id),
    CONSTRAINT pk_fld_approved_ck CHECK (
        owner_approved = FALSE OR owner_decision_id IS NOT NULL)
);

-- ============================================================
-- 不可变性保障（H2）
-- ============================================================
-- H2 的 BEFORE UPDATE 触发器需 Java 触发器类，无法在纯 SQL 迁移中声明。
-- 本候选以显式声明记录约束意图，实际由三层保障：
--   1. 应用层：Repository 不暴露 update 方法（仅 insert）
--   2. 集成测试 IT：尝试 UPDATE 必须失败
--   3. Gate A2 时确认是否引入 Java 触发器类
--
-- 涉及的不可变表：
--   pk_source_version      （仅 superseded_by 可后置设置）
--   pk_fragment            （完全不可变）
--   pk_evidence_span       （完全不可变，CTR-PK-EVS-002）
--   pk_field_assertion     （完全不可变，值变更走 supersedes，INV-ASM-06）
--   pk_review_decision     （只追加，INV-CNF-05）
--   pk_knowledge_release   （PUBLISHED 后不可变，INV-RLS-05）
