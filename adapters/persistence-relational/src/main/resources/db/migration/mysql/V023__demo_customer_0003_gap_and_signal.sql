-- ═══════════════════════════════════════════════════════════════════
-- V023: 演示主客户 CUST-CORP-0003（北京绿源环保集团）数据补全
-- MySQL version
-- 目的：让「客户经营旅程」主链（P04 客户经营总览）数据完整，保证人类演示畅通。
-- ═══════════════════════════════════════════════════════════════════

-- ── 经营案例：北京绿源环保集团经营旅程 ──
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('a1b2c3d4-e5f6-7890-abcd-100000000003', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '北京绿源环保集团经营旅程',
        '2026-06-20 08:30:00', NULL, '2026-06-20 08:30:00', 0, 'RM-ZW-001');

INSERT INTO customer_journey (journey_id, case_id, customer_id, customer_name, phase, started_at, updated_at)
VALUES ('a1b2c3d4-e5f6-7890-abcd-000000000003', 'a1b2c3d4-e5f6-7890-abcd-100000000003',
        'CUST-CORP-0003', '北京绿源环保集团', 'POSTVISIT_REVIEW',
        '2026-06-20 08:30:00', '2026-08-15 11:00:00');

-- ── KYC 缺口画像：北京绿源环保集团 ──
INSERT INTO kyc_gap_profile (profile_id, customer_id, as_of, known_items, partial_known_items, stale_items, conflicting_or_ambiguous_items, unknown_items, priority_questions, created_at, updated_at)
VALUES ('kgp-0003-lvyuan', 'CUST-CORP-0003', '2026-08-15',
        '["公司基本信息","主营业务","实控人信息","信用评级","上市状态"]',
        '["旗下5家子公司经营状况","PPP项目合同台账"]',
        '["财务数据(2024年报)","环保资质证书有效期"]',
        '["PPP项目投资总额 — 客户口径8亿与公开备案5亿存在差异"]',
        '["海外环保项目布局","碳中和技改资金缺口","政府回款账期"]',
        '["核实PPP项目投资总额口径","获取最新财务报表","确认碳中和技改资金来源"]',
        '2026-08-15T09:00:00Z', '2026-08-15T09:00:00Z');

-- ── 机会信号：北京绿源环保集团 ──
INSERT INTO opportunity_signal (signal_id, operating_case_id, journey_id, signal_type, content, source_type, source_ref, confidence, status, evidence_ref, detected_at, confirmed_at, created_at, updated_at)
VALUES ('c47ac10b-58cc-4372-a567-0e02b2c3d301', 'a1b2c3d4-e5f6-7890-abcd-100000000003', 'a1b2c3d4-e5f6-7890-abcd-000000000003', 'FINANCING_NEED',
        '客户正在推进3个大型污水处理PPP项目，总投资约8亿元，有绿色债券发行融资需求',
        'INTERACTION', 'INT-YDMY-001', 0.88, 'DETECTED', 'evidence-0003-001',
        '2026-07-20T10:00:00Z', NULL, '2026-07-20T10:00:00Z', NULL);

INSERT INTO opportunity_signal (signal_id, operating_case_id, journey_id, signal_type, content, source_type, source_ref, confidence, status, evidence_ref, detected_at, confirmed_at, created_at, updated_at)
VALUES ('c47ac10b-58cc-4372-a567-0e02b2c3d302', 'a1b2c3d4-e5f6-7890-abcd-100000000003', 'a1b2c3d4-e5f6-7890-abcd-000000000003', 'PRODUCT_OPPORTUNITY',
        '客户未来3年计划投入5亿元用于碳中和技术改造，可推荐绿色信贷专项方案',
        'ANALYSIS', 'kyc-report-0003-001', 0.76, 'CONFIRMED', 'kyc-report-0003-001',
        '2026-07-22T14:00:00Z', '2026-07-22T16:00:00Z', '2026-07-22T14:00:00Z', '2026-07-22T16:00:00Z');

INSERT INTO opportunity_signal (signal_id, operating_case_id, journey_id, signal_type, content, source_type, source_ref, confidence, status, evidence_ref, detected_at, confirmed_at, created_at, updated_at)
VALUES ('c47ac10b-58cc-4372-a567-0e02b2c3d303', 'a1b2c3d4-e5f6-7890-abcd-100000000003', 'a1b2c3d4-e5f6-7890-abcd-000000000003', 'RELATIONSHIP_CHANGE',
        '客户与政府合作方的关系调整，可能影响PPP项目回款节奏，需持续跟踪',
        'EXTERNAL_EVENT', 'event-0003-001', 0.52, 'DETECTED', 'event-0003-001',
        '2026-08-10T09:00:00Z', NULL, '2026-08-10T09:00:00Z', NULL);
