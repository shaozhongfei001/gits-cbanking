-- 1. 源文档（可变：allowed_claim_types 可由 Owner 调整）
CREATE TABLE pk_source_document (
    source_id            VARCHAR(64)   NOT NULL,
    zone                 VARCHAR(32)   NOT NULL,
    product_family       VARCHAR(32),
    allowed_claim_types  VARCHAR(255)  NOT NULL,
    authority_level      VARCHAR(32)   NOT NULL,
    registry_status      VARCHAR(32)   NOT NULL,
    created_at           DATETIME(6)       NOT NULL,
    updated_at           DATETIME(6)       NOT NULL,
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
    ingested_at        DATETIME(6)       NOT NULL,
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
    content_text       LONGTEXT     NOT NULL,
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
    locator_json       LONGTEXT     NOT NULL,
    quote              LONGTEXT     NOT NULL,
    quote_sha256       CHAR(64)  NOT NULL,
    usage_type         VARCHAR(24)  NOT NULL,
    authority_level    VARCHAR(32)  NOT NULL,
    claim_type         VARCHAR(16)  NOT NULL,
    scope_json         LONGTEXT     NOT NULL,
    extraction_run_id  VARCHAR(64)  NOT NULL,
    clause_verified    TINYINT(1)    NOT NULL DEFAULT 0,
    retrieved_at       DATETIME(6)      NOT NULL,
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
    raw_value             LONGTEXT,
    normalized_value      LONGTEXT,
    value_type            VARCHAR(16)  NOT NULL,
    knowledge_state       VARCHAR(24)  NOT NULL,
    scope_json            LONGTEXT     NOT NULL,
    conflict_id           VARCHAR(128),
    review_decision_id    VARCHAR(64),
    supersedes            VARCHAR(128),
    created_by_run_id     VARCHAR(64)  NOT NULL,
    created_at            DATETIME(6)      NOT NULL,
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
    resolution_json     LONGTEXT,
    detected_by_run_id  VARCHAR(64)   NOT NULL,
    detected_at         DATETIME(6)       NOT NULL,
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
    rationale       LONGTEXT     NOT NULL,
    decided_by      VARCHAR(128) NOT NULL,
    decided_by_role VARCHAR(32)  NOT NULL,
    decided_at      DATETIME(6)      NOT NULL,
    CONSTRAINT pk_review_decision_pk PRIMARY KEY (decision_id),
    CONSTRAINT pk_dec_role_ck CHECK (decided_by_role IN
        ('PRODUCT_OWNER','RISK_OWNER','COMPLIANCE_OWNER'))
);
-- 8. 知识发布包（发布后不可变）— CTR-PK-RLS-001
CREATE TABLE pk_knowledge_release (
    release_id               VARCHAR(64) NOT NULL,
    taxonomy_version         VARCHAR(64) NOT NULL,
    lifecycle_state          VARCHAR(24) NOT NULL,
    interpretation_ready     TINYINT(1)   NOT NULL DEFAULT 0,
    recommendation_ready     TINYINT(1)   NOT NULL DEFAULT 0,
    assertion_manifest_hash  CHAR(64) NOT NULL,
    evidence_manifest_hash   CHAR(64) NOT NULL,
    card_projection_hash     CHAR(64) NOT NULL,
    rule_package_hash        CHAR(64) NOT NULL,
    bundle_hash              CHAR(64) NOT NULL,
    quality_run_id           VARCHAR(64) NOT NULL,
    is_stale                 TINYINT(1)   NOT NULL DEFAULT 0,
    stale_reason             VARCHAR(512),
    stale_since              DATETIME(6),
    gate_report_json         LONGTEXT,
    published_at             DATETIME(6),
    CONSTRAINT pk_knowledge_release_pk PRIMARY KEY (release_id),
    CONSTRAINT pk_rls_state_ck CHECK (lifecycle_state IN
        ('DRAFT','REVIEW_READY','APPROVED','PUBLISHED','RETIRED')),
    CONSTRAINT pk_rls_implies_ck CHECK (
        recommendation_ready = 0 OR interpretation_ready = 1),
    CONSTRAINT pk_rls_stale_ck CHECK (is_stale = 0 OR stale_reason IS NOT NULL),
    CONSTRAINT pk_rls_prov_ck CHECK (provenance_state IN ('VERIFIED','DEMO')),
    CONSTRAINT pk_rls_demo_ck CHECK (
        provenance_state <> 'DEMO' OR recommendation_ready = 0)
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
    impact_scope_json   LONGTEXT,
    reason              VARCHAR(1024) NOT NULL,
    occurred_at         DATETIME(6)       NOT NULL,
    applied_at          DATETIME(6),
    CONSTRAINT pk_change_event_pk PRIMARY KEY (event_id),
    CONSTRAINT pk_chg_type_ck CHECK (event_type IN
        ('RELEASE_PUBLISHED','RELEASE_RETIRED','RELEASE_STALED','SOURCE_VERSION_SUPERSEDED'))
);

-- 10. 字段策略 — CTR-PK-FLD-001
CREATE TABLE pk_field_policy (
    policy_id           VARCHAR(64)  NOT NULL,
    product_family      VARCHAR(32)  NOT NULL,
    policy_version      VARCHAR(32)  NOT NULL,
    owner_approved      TINYINT(1)    NOT NULL DEFAULT 0,
    owner_decision_id   VARCHAR(64),
    fields_json         LONGTEXT     NOT NULL,
    created_at          DATETIME(6)      NOT NULL,
    CONSTRAINT pk_field_policy_pk PRIMARY KEY (policy_id),
    CONSTRAINT pk_fld_approved_ck CHECK (
        owner_approved = 0 OR owner_decision_id IS NOT NULL)
);

-- ============================================================
-- 不可变性保障（MySQL）：BEFORE UPDATE 触发器直接报错
-- ============================================================
DELIMITER $$

CREATE TRIGGER pk_evidence_span_no_update BEFORE UPDATE ON pk_evidence_span
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_evidence_span is immutable (CTR-PK-EVS-002)';
END$$

CREATE TRIGGER pk_fragment_no_update BEFORE UPDATE ON pk_fragment
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_fragment is immutable';
END$$

CREATE TRIGGER pk_field_assertion_no_update BEFORE UPDATE ON pk_field_assertion
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_field_assertion is immutable; use supersedes chain (INV-ASM-06)';
END$$

CREATE TRIGGER pk_review_decision_no_update BEFORE UPDATE ON pk_review_decision
FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'pk_review_decision is append-only (INV-CNF-05)';
END$$

CREATE TRIGGER pk_knowledge_release_published_immutable BEFORE UPDATE ON pk_knowledge_release
FOR EACH ROW BEGIN
    IF OLD.lifecycle_state = 'PUBLISHED'
       AND NOT (NEW.bundle_hash <=> OLD.bundle_hash) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'published release is immutable; create new releaseId (INV-RLS-05)';
    END IF;
END$$

DELIMITER ;
