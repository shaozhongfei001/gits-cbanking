-- ═══════════════════════════════════════════════════════════════════
-- V020: Product Recommendation Run (三段式产品推荐) tables
-- H2-compatible version (MySQL compatibility mode)
-- 状态 CANDIDATE / FROZEN=NO：仅在域模型/合同获批后启用
-- ═══════════════════════════════════════════════════════════════════

-- 产品推荐业务运行表（GITS 主责业务状态机）
CREATE TABLE IF NOT EXISTS product_recommendation_run (
    run_id CHAR(36) PRIMARY KEY,
    customer_id CHAR(36) NOT NULL,
    journey_id CHAR(36) NULL,
    operating_case_id CHAR(36) NULL,
    need_version_ids JSON NULL,
    recommendation_objective VARCHAR(512) NOT NULL,
    requested_product_domains JSON NULL,
    as_of TIMESTAMP(6) NOT NULL,
    idempotency_key VARCHAR(256) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'REQUESTED',
    current_version_id CHAR(36) NULL,
    kert_job_ref VARCHAR(128) NULL,
    snapshot_refs JSON NULL,
    created_at TIMESTAMP(6) NOT NULL,
    updated_at TIMESTAMP(6) NOT NULL
);

-- 产品推荐 attempt 表（每次调 KERT 的 attempt，不覆盖旧轨迹）
CREATE TABLE IF NOT EXISTS product_recommendation_attempt (
    attempt_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    kert_request_id VARCHAR(128) NOT NULL,
    started_at TIMESTAMP(6) NOT NULL,
    finished_at TIMESTAMP(6) NULL,
    status VARCHAR(32) NOT NULL,
    error_code VARCHAR(64) NULL,
    retryable BOOLEAN NOT NULL DEFAULT FALSE
);

-- 不可变方案版本表（含哈希，支持重放与过期判断）
CREATE TABLE IF NOT EXISTS recommendation_proposal_version (
    version_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    result_ref VARCHAR(128) NULL,
    evidence_bundle_id VARCHAR(128) NULL,
    content_hash VARCHAR(128) NOT NULL,
    payload JSON NOT NULL,
    superseded_by CHAR(36) NULL,
    created_at TIMESTAMP(6) NOT NULL
);

-- 人工决定表（结构化 HG-D01 决策；decision 指向 proposal_version_id）
CREATE TABLE IF NOT EXISTS recommendation_human_decision (
    decision_id CHAR(36) PRIMARY KEY,
    gate_id CHAR(36) NOT NULL,
    run_id CHAR(36) NOT NULL,
    proposal_version_id CHAR(36) NOT NULL,
    decision VARCHAR(32) NOT NULL,
    modifications JSON NULL,
    reason TEXT NULL,
    actor_id VARCHAR(128) NOT NULL,
    actor_role VARCHAR(64) NULL,
    decided_at TIMESTAMP(6) NOT NULL
);

-- 反馈表（供评测；不直接改正式规则）
CREATE TABLE IF NOT EXISTS recommendation_feedback (
    feedback_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    adopted BOOLEAN NULL,
    rejection_reason VARCHAR(256) NULL,
    modified_fields JSON NULL,
    outcome_ref VARCHAR(128) NULL,
    created_at TIMESTAMP(6) NOT NULL
);

-- 索引
-- 幂等键唯一约束：与 mysql/V020 的 UNIQUE KEY uk_prr_idem 对齐，
-- 保证并发同键在 createRun.saveRun 命中 DuplicateKeyException 后回读既有 run。
CREATE UNIQUE INDEX IF NOT EXISTS uk_prr_idem ON product_recommendation_run (idempotency_key);
CREATE INDEX IF NOT EXISTS idx_prr_customer ON product_recommendation_run (customer_id);
CREATE INDEX IF NOT EXISTS idx_prr_journey ON product_recommendation_run (journey_id);
CREATE INDEX IF NOT EXISTS idx_prr_status ON product_recommendation_run (status);
CREATE INDEX IF NOT EXISTS idx_pra_run ON product_recommendation_attempt (run_id);
CREATE INDEX IF NOT EXISTS idx_pra_status ON product_recommendation_attempt (status);
CREATE INDEX IF NOT EXISTS idx_rpv_run ON recommendation_proposal_version (run_id);
CREATE INDEX IF NOT EXISTS idx_rpv_hash ON recommendation_proposal_version (content_hash);
CREATE INDEX IF NOT EXISTS idx_rhd_run ON recommendation_human_decision (run_id);
CREATE INDEX IF NOT EXISTS idx_rhd_gate ON recommendation_human_decision (gate_id);
CREATE INDEX IF NOT EXISTS idx_rhd_version ON recommendation_human_decision (proposal_version_id);
CREATE INDEX IF NOT EXISTS idx_rf_run ON recommendation_feedback (run_id);
