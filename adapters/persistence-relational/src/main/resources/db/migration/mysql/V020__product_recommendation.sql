-- ═══════════════════════════════════════════════════════════════════
-- V020: Product Recommendation Run (三段式产品推荐) tables
-- MySQL version
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
    updated_at TIMESTAMP(6) NOT NULL,
    UNIQUE KEY uk_prr_idem (idempotency_key),
    INDEX idx_prr_customer (customer_id),
    INDEX idx_prr_journey (journey_id),
    INDEX idx_prr_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 产品推荐 attempt 表（每次调 KERT 的 attempt，不覆盖旧轨迹）
CREATE TABLE IF NOT EXISTS product_recommendation_attempt (
    attempt_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    kert_request_id VARCHAR(128) NOT NULL,
    started_at TIMESTAMP(6) NOT NULL,
    finished_at TIMESTAMP(6) NULL,
    status VARCHAR(32) NOT NULL,
    error_code VARCHAR(64) NULL,
    retryable BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_pra_run (run_id),
    INDEX idx_pra_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 不可变方案版本表（含哈希，支持重放与过期判断）
CREATE TABLE IF NOT EXISTS recommendation_proposal_version (
    version_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    result_ref VARCHAR(128) NULL,
    evidence_bundle_id VARCHAR(128) NULL,
    content_hash VARCHAR(128) NOT NULL,
    payload JSON NOT NULL,
    superseded_by CHAR(36) NULL,
    created_at TIMESTAMP(6) NOT NULL,
    INDEX idx_rpv_run (run_id),
    INDEX idx_rpv_hash (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
    decided_at TIMESTAMP(6) NOT NULL,
    INDEX idx_rhd_run (run_id),
    INDEX idx_rhd_gate (gate_id),
    INDEX idx_rhd_version (proposal_version_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 反馈表（供评测；不直接改正式规则）
CREATE TABLE IF NOT EXISTS recommendation_feedback (
    feedback_id CHAR(36) PRIMARY KEY,
    run_id CHAR(36) NOT NULL,
    adopted BOOLEAN NULL,
    rejection_reason VARCHAR(256) NULL,
    modified_fields JSON NULL,
    outcome_ref VARCHAR(128) NULL,
    created_at TIMESTAMP(6) NOT NULL,
    INDEX idx_rf_run (run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
