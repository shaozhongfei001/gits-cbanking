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
