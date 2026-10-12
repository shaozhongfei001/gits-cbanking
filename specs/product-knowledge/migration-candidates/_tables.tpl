-- 1. 源文档（可变：allowed_claim_types 可由 Owner 调整）
CREATE TABLE pk_source_document (
    source_id            {vc}(64)   NOT NULL,
    zone                 {vc}(32)   NOT NULL,
    product_family       {vc}(32),
    allowed_claim_types  {vc}(255)  NOT NULL,
    authority_level      {vc}(32)   NOT NULL,
    registry_status      {vc}(32)   NOT NULL,
    created_at           {ts}       NOT NULL,
    updated_at           {ts}       NOT NULL,
    CONSTRAINT pk_source_document_pk PRIMARY KEY (source_id),
    CONSTRAINT pk_sd_zone_ck CHECK (zone IN ('_authoritative','_public_reference')),
    CONSTRAINT pk_sd_status_ck CHECK (registry_status IN
        ('REGISTERED','PENDING_SOURCE','AVAILABLE','PARSED','CLAUSE_VERIFIED','RETIRED'))
);

-- 2. 源版本（不可变）
CREATE TABLE pk_source_version (
    source_version_id  {vc}(128)  NOT NULL,
    source_id          {vc}(64)   NOT NULL,
    bytes_sha256       CHAR(64)   NOT NULL,
    byte_size          BIGINT     NOT NULL,
    page_count         INT,
    ingested_at        {ts}       NOT NULL,
    superseded_by      {vc}(128),
    provenance_url     {vc}(1024),
    provenance_state   {vc}(32)   NOT NULL DEFAULT 'UNVERIFIED',
    CONSTRAINT pk_source_version_pk PRIMARY KEY (source_version_id),
    CONSTRAINT pk_sv_source_fk FOREIGN KEY (source_id) REFERENCES pk_source_document(source_id),
    CONSTRAINT pk_sv_prov_ck CHECK (provenance_state IN
        ('VERIFIED','UNVERIFIED','CONFLICTING_EVIDENCE','DEMO'))
);
CREATE UNIQUE INDEX pk_sv_hash_uq ON pk_source_version(source_id, bytes_sha256);

-- 3. 片段（不可变）
CREATE TABLE pk_fragment (
    fragment_id        {vc}(128) NOT NULL,
    source_version_id  {vc}(128) NOT NULL,
    seq_no             INT       NOT NULL,
    page_no            INT,
    content_text       {txt}     NOT NULL,
    content_sha256     CHAR(64)  NOT NULL,
    CONSTRAINT pk_fragment_pk PRIMARY KEY (fragment_id),
    CONSTRAINT pk_frg_sv_fk FOREIGN KEY (source_version_id)
        REFERENCES pk_source_version(source_version_id)
);

-- 4. 证据跨度（不可变）— CTR-PK-EVS-002
CREATE TABLE pk_evidence_span (
    evidence_id        {vc}(128) NOT NULL,
    source_id          {vc}(64)  NOT NULL,
    source_version_id  {vc}(128) NOT NULL,
    fragment_id        {vc}(128) NOT NULL,
    locator_kind       {vc}(16)  NOT NULL,
    locator_json       {txt}     NOT NULL,
    quote              {txt}     NOT NULL,
    quote_sha256       CHAR(64)  NOT NULL,
    usage_type         {vc}(24)  NOT NULL,
    authority_level    {vc}(32)  NOT NULL,
    claim_type         {vc}(16)  NOT NULL,
    scope_json         {txt}     NOT NULL,
    extraction_run_id  {vc}(64)  NOT NULL,
    clause_verified    {bool}    NOT NULL DEFAULT {false},
    retrieved_at       {ts}      NOT NULL,
    source_path        {vc}(512) NOT NULL,
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
-- 8. 知识发布包（发布后不可变）— CTR-PK-RLS-001
CREATE TABLE pk_knowledge_release (
    release_id               {vc}(64) NOT NULL,
    taxonomy_version         {vc}(64) NOT NULL,
    lifecycle_state          {vc}(24) NOT NULL,
    interpretation_ready     {bool}   NOT NULL DEFAULT {false},
    recommendation_ready     {bool}   NOT NULL DEFAULT {false},
    assertion_manifest_hash  CHAR(64) NOT NULL,
    evidence_manifest_hash   CHAR(64) NOT NULL,
    card_projection_hash     CHAR(64) NOT NULL,
    rule_package_hash        CHAR(64) NOT NULL,
    bundle_hash              CHAR(64) NOT NULL,
    quality_run_id           {vc}(64) NOT NULL,
    is_stale                 {bool}   NOT NULL DEFAULT {false},
    stale_reason             {vc}(512),
    stale_since              {ts},
    gate_report_json         {txt},
    published_at             {ts},
    CONSTRAINT pk_knowledge_release_pk PRIMARY KEY (release_id),
    CONSTRAINT pk_rls_state_ck CHECK (lifecycle_state IN
        ('DRAFT','REVIEW_READY','APPROVED','PUBLISHED','RETIRED')),
    CONSTRAINT pk_rls_implies_ck CHECK (
        recommendation_ready = {false} OR interpretation_ready = {true}),
    CONSTRAINT pk_rls_stale_ck CHECK (is_stale = {false} OR stale_reason IS NOT NULL),
    CONSTRAINT pk_rls_prov_ck CHECK (provenance_state IN ('VERIFIED','DEMO')),
    CONSTRAINT pk_rls_demo_ck CHECK (
        provenance_state <> 'DEMO' OR recommendation_ready = {false})
);

CREATE TABLE pk_release_product (
    release_id {vc}(64) NOT NULL,
    product_id {vc}(32) NOT NULL,
    CONSTRAINT pk_release_product_pk PRIMARY KEY (release_id, product_id),
    CONSTRAINT pk_rp_rls_fk FOREIGN KEY (release_id)
        REFERENCES pk_knowledge_release(release_id)
);

-- 9. 变更事件（幂等去重）— CTR-PK-CHG-001
CREATE TABLE pk_change_event (
    event_id            {vc}(64)   NOT NULL,
    event_type          {vc}(32)   NOT NULL,
    previous_release_id {vc}(64),
    new_release_id      {vc}(64),
    impact_scope_json   {txt},
    reason              {vc}(1024) NOT NULL,
    occurred_at         {ts}       NOT NULL,
    applied_at          {ts},
    CONSTRAINT pk_change_event_pk PRIMARY KEY (event_id),
    CONSTRAINT pk_chg_type_ck CHECK (event_type IN
        ('RELEASE_PUBLISHED','RELEASE_RETIRED','RELEASE_STALED','SOURCE_VERSION_SUPERSEDED'))
);

-- 10. 字段策略 — CTR-PK-FLD-001
CREATE TABLE pk_field_policy (
    policy_id           {vc}(64)  NOT NULL,
    product_family      {vc}(32)  NOT NULL,
    policy_version      {vc}(32)  NOT NULL,
    owner_approved      {bool}    NOT NULL DEFAULT {false},
    owner_decision_id   {vc}(64),
    fields_json         {txt}     NOT NULL,
    created_at          {ts}      NOT NULL,
    CONSTRAINT pk_field_policy_pk PRIMARY KEY (policy_id),
    CONSTRAINT pk_fld_approved_ck CHECK (
        owner_approved = {false} OR owner_decision_id IS NOT NULL)
);
