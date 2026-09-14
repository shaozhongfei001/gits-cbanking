-- V022: 为其他客户添加经营案例和商机种子数据
-- 用途：为「产品推荐三段式工作区」的「经营案例」和「需求候选」选择器提供真实可选项。
-- 现有数据：CUST-CORP-0001 已有经营案例 a1b2c3d4-e5f6-7890-abcd-ef0123456789 及 3 条商机（V014）。
-- 本脚本：为 CUST-CORP-0002~0006 各添加 1 个经营案例 + 2~3 条商机。

-- ═══════════════════════════════════════════════════════════════════
-- 经营案例
-- ═══════════════════════════════════════════════════════════════════

-- CUST-CORP-0002 深圳创新科技 — 科创板上市前融资规划
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('b2a1c3d4-e5f6-7890-abcd-ef0123456001', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '深圳创新科技科创板上市前融资规划 — 营运资金及研发投入',
        '2026-08-01 09:00:00', NULL, '2026-08-01 09:00:00', 0, 'RM-002');

-- CUST-CORP-0003 北京绿源环保 — PPP项目配套融资
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('b2a1c3d4-e5f6-7890-abcd-ef0123456002', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '北京绿源环保PPP项目配套融资 — 污水处理厂三期建设',
        '2026-07-15 09:00:00', NULL, '2026-07-15 09:00:00', 0, 'RM-001');

-- CUST-CORP-0004 绿能新能源 — 光伏电站建设融资
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('b2a1c3d4-e5f6-7890-abcd-ef0123456003', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '绿能新能源光伏电站建设融资 — 200MW分布式光伏项目',
        '2026-08-10 09:00:00', NULL, '2026-08-10 09:00:00', 0, 'RM-ZW-001');

-- CUST-CORP-0005 华创医药 — 研发中心建设及并购融资
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('b2a1c3d4-e5f6-7890-abcd-ef0123456004', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '华创医药研发中心建设及并购融资 — 创新药管线扩张',
        '2026-06-20 09:00:00', NULL, '2026-06-20 09:00:00', 0, 'RM-ZW-001');

-- CUST-CORP-0006 长江物流 — 冷链物流网络扩建融资
INSERT INTO operating_case (case_id, case_type, status, purpose, valid_from, valid_to, recorded_at, record_version, created_by)
VALUES ('b2a1c3d4-e5f6-7890-abcd-ef0123456005', 'CONTINUOUS_ENGAGEMENT', 'ACTIVE', '长江物流冷链物流网络扩建融资 — 华中冷链枢纽建设',
        '2026-07-01 09:00:00', NULL, '2026-07-01 09:00:00', 0, 'RM-ZW-001');

-- ═══════════════════════════════════════════════════════════════════
-- 商机
-- ═══════════════════════════════════════════════════════════════════

-- CUST-CORP-0002 深圳创新科技
INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456001', 'CUST-CORP-0002', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456001', 'WORKING_CAPITAL', 'PROD-WORKING-CAPITAL', '流动资金贷款', '科创板上市前营运资金补充 — 研发及市场推广投入', 'QUALIFIED', '5000万', '65%', 'RM-002', 'TRANSACTION_ANALYSIS', '["确认上市时间表","评估营运资金缺口","准备授信审批材料"]', '2026-10-31', '2026-08-01 10:00:00', '2026-08-01 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456002', 'CUST-CORP-0002', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456001', 'EQUIPMENT_FINANCING', 'PROD-FACTORING', '国内保理', '应收账款保理 — 大客户回款周期长', 'DETECTED', '3000万', '50%', 'RM-002', 'EXTERNAL_EVENT', '["确认应收账款规模","评估保理额度需求"]', '2026-09-30', '2026-08-01 10:00:00', '2026-08-01 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456003', 'CUST-CORP-0002', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456001', 'SETTLEMENT', 'PROD-CASH-MANAGEMENT', '现金管理', '集团资金集中管理 — 多银行账户归集', 'PROPOSAL', '2000万', '70%', 'RM-002', 'INTERACTION', '["确认资金归集需求","设计现金管理方案"]', '2026-09-15', '2026-08-01 10:00:00', '2026-08-01 10:00:00');

-- CUST-CORP-0003 北京绿源环保
INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456004', 'CUST-CORP-0003', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456002', 'PROJECT_FINANCING', 'PROD-PROJECT-LOAN', '项目贷款', '污水处理厂三期项目融资 — 总投资2.5亿元', 'QUALIFIED', '25000万', '55%', 'RM-001', 'EXTERNAL_EVENT', '["确认项目投资额","准备环评及备案文件","安排项目评审"]', '2026-12-31', '2026-07-15 10:00:00', '2026-07-15 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456005', 'CUST-CORP-0003', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456002', 'TRADE_FINANCE', 'PROD-LC', '信用证', '进口设备信用证 — 德国污水处理设备采购', 'DETECTED', '8000万', '45%', 'RM-001', 'TRANSACTION_ANALYSIS', '["确认设备采购合同","评估信用证额度需求"]', '2026-11-30', '2026-07-15 10:00:00', '2026-07-15 10:00:00');

-- CUST-CORP-0004 绿能新能源
INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456006', 'CUST-CORP-0004', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456003', 'PROJECT_FINANCING', 'PROD-GREEN-LOAN', '绿色贷款', '200MW分布式光伏项目绿色融资 — 总投资4亿元', 'QUALIFIED', '40000万', '50%', 'RM-ZW-001', 'EXTERNAL_EVENT', '["确认项目备案","准备绿色认证材料","安排项目评审"]', '2027-03-31', '2026-08-10 10:00:00', '2026-08-10 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456007', 'CUST-CORP-0004', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456003', 'WORKING_CAPITAL', 'PROD-WORKING-CAPITAL', '流动资金贷款', '光伏组件采购周转资金 — 硅片及逆变器采购', 'DETECTED', '6000万', '40%', 'RM-ZW-001', 'TRANSACTION_ANALYSIS', '["确认采购计划","评估周转资金需求"]', '2026-12-31', '2026-08-10 10:00:00', '2026-08-10 10:00:00');

-- CUST-CORP-0005 华创医药
INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456008', 'CUST-CORP-0005', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456004', 'PROJECT_FINANCING', 'PROD-PROJECT-LOAN', '项目贷款', '创新药研发中心建设融资 — 总投资1.8亿元', 'QUALIFIED', '18000万', '60%', 'RM-ZW-001', 'EXTERNAL_EVENT', '["确认研发中心建设计划","准备立项审批材料","安排项目评审"]', '2027-06-30', '2026-06-20 10:00:00', '2026-06-20 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456009', 'CUST-CORP-0005', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456004', 'MERGER_ACQUISITION', 'PROD-M-A-LOAN', '并购贷款', '生物科技公司并购融资 — 标的公司估值3亿元', 'DETECTED', '15000万', '35%', 'RM-ZW-001', 'INTERACTION', '["确认并购标的","评估并购贷款额度","准备并购方案"]', '2027-09-30', '2026-06-20 10:00:00', '2026-06-20 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456010', 'CUST-CORP-0005', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456004', 'SETTLEMENT', 'PROD-CASH-MANAGEMENT', '现金管理', '集团资金池管理 — 多子公司资金归集', 'PROPOSAL', '8000万', '75%', 'RM-ZW-001', 'TRANSACTION_ANALYSIS', '["确认资金归集需求","设计资金池方案"]', '2026-10-31', '2026-06-20 10:00:00', '2026-06-20 10:00:00');

-- CUST-CORP-0006 长江物流
INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456011', 'CUST-CORP-0006', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456005', 'PROJECT_FINANCING', 'PROD-PROJECT-LOAN', '项目贷款', '华中冷链枢纽建设融资 — 总投资1.5亿元', 'QUALIFIED', '15000万', '55%', 'RM-ZW-001', 'EXTERNAL_EVENT', '["确认枢纽建设计划","准备立项审批材料","安排项目评审"]', '2027-03-31', '2026-07-01 10:00:00', '2026-07-01 10:00:00');

INSERT INTO opportunity (opportunity_id, customer_id, interaction_id, operating_case_id, opportunity_type, product_id, product_name, description, status, estimated_amount, probability, assigned_to, source, next_steps, expected_close_date, created_at, updated_at)
VALUES ('e2a1c3d4-e5f6-7890-abcd-ef0123456012', 'CUST-CORP-0006', NULL, 'b2a1c3d4-e5f6-7890-abcd-ef0123456005', 'WORKING_CAPITAL', 'PROD-WORKING-CAPITAL', '流动资金贷款', '冷链运输车队购置周转资金 — 新能源冷藏车采购', 'DETECTED', '4000万', '45%', 'RM-ZW-001', 'TRANSACTION_ANALYSIS', '["确认车队采购计划","评估周转资金需求"]', '2026-12-31', '2026-07-01 10:00:00', '2026-07-01 10:00:00');
