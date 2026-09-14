-- 5. 字段断言（不可变，值变更走 supersedes）— CTR-PK-ASM-001
CREATE TABLE pk_field_assertion (
    assertion_id          {vc}(128) NOT NULL,
    product_id            {vc}(32)  NOT NULL,
    product_version_scope {vc}(64)  NOT NULL,
    field_path            {vc}(128) NOT NULL,
    raw_value             {txt},
    normalized_value      {txt},
    value_type            {vc}(16)  NOT NULL,
    knowledge_state       {vc}(24)  NOT NULL,
    scope_json            {txt}     NOT NULL,
    conflict_id           {vc}(128),
    review_decision_id    {vc}(64),
    supersedes            {vc}(128),
    created_by_run_id     {vc}(64)  NOT NULL,
    created_at            {ts}      NOT NULL,
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
    assertion_id {vc}(128) NOT NULL,
    evidence_id  {vc}(128) NOT NULL,
    CONSTRAINT pk_assertion_evidence_pk PRIMARY KEY (assertion_id, evidence_id),
    CONSTRAINT pk_ae_asm_fk FOREIGN KEY (assertion_id)
        REFERENCES pk_field_assertion(assertion_id),
    CONSTRAINT pk_ae_evs_fk FOREIGN KEY (evidence_id)
        REFERENCES pk_evidence_span(evidence_id)
);

-- 6. 冲突案例 — CTR-PK-CNF-001
CREATE TABLE pk_conflict_case (
    conflict_id         {vc}(128)  NOT NULL,
    product_id          {vc}(32)   NOT NULL,
    field_path          {vc}(128)  NOT NULL,
    conflict_type       {vc}(32)   NOT NULL,
    status              {vc}(16)   NOT NULL,
    resolution_json     {txt},
    detected_by_run_id  {vc}(64)   NOT NULL,
    detected_at         {ts}       NOT NULL,
    CONSTRAINT pk_conflict_case_pk PRIMARY KEY (conflict_id),
    CONSTRAINT pk_cnf_status_ck CHECK (status IN
        ('OPEN','UNDER_REVIEW','RESOLVED','DEFERRED')),
    CONSTRAINT pk_cnf_type_ck CHECK (conflict_type IN
        ('VALUE_MISMATCH','SCOPE_OVERLAP','AUTHORITY_TIE','TEMPORAL_AMBIGUITY','UNIT_MISMATCH')),
    CONSTRAINT pk_cnf_resolved_ck CHECK (status <> 'RESOLVED' OR resolution_json IS NOT NULL)
);

-- 7. 审核决议（不可变，只追加）
CREATE TABLE pk_review_decision (
    decision_id     {vc}(64)  NOT NULL,
    subject_kind    {vc}(32)  NOT NULL,
    subject_id      {vc}(128) NOT NULL,
    decision        {vc}(24)  NOT NULL,
    rationale       {txt}     NOT NULL,
    decided_by      {vc}(128) NOT NULL,
    decided_by_role {vc}(32)  NOT NULL,
    decided_at      {ts}      NOT NULL,
    CONSTRAINT pk_review_decision_pk PRIMARY KEY (decision_id),
    CONSTRAINT pk_dec_role_ck CHECK (decided_by_role IN
        ('PRODUCT_OWNER','RISK_OWNER','COMPLIANCE_OWNER'))
);
