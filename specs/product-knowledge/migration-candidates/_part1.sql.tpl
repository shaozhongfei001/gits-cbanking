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
