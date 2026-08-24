package com.gien.gits.api.service;

import com.gien.gits.ontology.*;
import com.gien.gits.ontology.port.ScenarioDataProvider;
import com.gien.gits.ontology.port.WritableBankRelationshipSnapshotRepository;
import com.gien.gits.ontology.port.WritableCreditFacilityRepository;
import com.gien.gits.ontology.port.WritableCustomerRepository;
import com.gien.gits.ontology.port.WritableExternalEventRepository;
import com.gien.gits.ontology.port.WritableGroupRelationshipRepository;
import com.gien.gits.ontology.port.WritableInteractionRepository;
import com.gien.gits.ontology.port.WritableKycGapProfileRepository;
import com.gien.gits.ontology.port.WritableLegalEntityRepository;
import com.gien.gits.ontology.port.WritablePolicyRuleRepository;
import com.gien.gits.ontology.port.WritableProductCatalogRepository;
import com.gien.gits.ontology.port.WritableTransactionRecordRepository;
import com.gien.gits.ontology.port.WritableTransactionRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;

import jakarta.annotation.PostConstruct;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.*;

/**
 * 场景种子数据加载器 — 华东精工经营闭环场景数据
 * <p>
 * V1.1升级：支持SCENARIO_DATA_ROOT外部数据源
 * - filesystem provider: 从V1.1外部目录加载 (JSON/CSV/JSONL/YAML)
 * - classpath provider: 使用V1.0内嵌硬编码数据 (兼容fallback)
 * <p>
 * 加载: 客户主档 + 法人实体 + 集团关系 + 银行关系 + 授信 + 产品 + 政策 + 外部事件 + KYC缺口
 */
public class ScenarioSeedDataService {

    private static final Logger log = LoggerFactory.getLogger(ScenarioSeedDataService.class);

    private final WritableCustomerRepository customerRepo;
    private final WritableLegalEntityRepository legalEntityRepo;
    private final WritableGroupRelationshipRepository groupRelRepo;
    private final WritableBankRelationshipSnapshotRepository bankRelRepo;
    private final WritableCreditFacilityRepository creditFacilityRepo;
    private final WritableTransactionRecordRepository transactionRepo;
    private final WritableTransactionRepository transactionFlowRepo;
    private final WritableProductCatalogRepository productCatalogRepo;
    private final WritablePolicyRuleRepository policyRuleRepo;
    private final WritableExternalEventRepository externalEventRepo;
    private final WritableKycGapProfileRepository kycGapRepo;
    private final WritableInteractionRepository interactionRepo;
    private final JdbcTemplate jdbcTemplate;
    private final ScenarioDataProvider dataProvider;

    public ScenarioSeedDataService(
            WritableCustomerRepository customerRepo,
            WritableLegalEntityRepository legalEntityRepo,
            WritableGroupRelationshipRepository groupRelRepo,
            WritableBankRelationshipSnapshotRepository bankRelRepo,
            WritableCreditFacilityRepository creditFacilityRepo,
            WritableTransactionRecordRepository transactionRepo,
            WritableTransactionRepository transactionFlowRepo,
            WritableProductCatalogRepository productCatalogRepo,
            WritablePolicyRuleRepository policyRuleRepo,
            WritableExternalEventRepository externalEventRepo,
            WritableKycGapProfileRepository kycGapRepo,
            WritableInteractionRepository interactionRepo,
            JdbcTemplate jdbcTemplate,
            ScenarioDataProvider dataProvider) {
        this.customerRepo = customerRepo;
        this.legalEntityRepo = legalEntityRepo;
        this.groupRelRepo = groupRelRepo;
        this.bankRelRepo = bankRelRepo;
        this.creditFacilityRepo = creditFacilityRepo;
        this.transactionRepo = transactionRepo;
        this.transactionFlowRepo = transactionFlowRepo;
        this.productCatalogRepo = productCatalogRepo;
        this.policyRuleRepo = policyRuleRepo;
        this.externalEventRepo = externalEventRepo;
        this.kycGapRepo = kycGapRepo;
        this.interactionRepo = interactionRepo;
        this.jdbcTemplate = jdbcTemplate;
        this.dataProvider = dataProvider;
    }

    @PostConstruct
    @Transactional
    public void init() {
        if (isLoaded()) {
            log.info("Seed data already loaded, skipping auto-load");
            return;
        }
        try {
            loadAll();
        } catch (Exception e) {
            log.warn("Seed data auto-load skipped (may already exist): {}", e.getMessage());
        }
    }

    /**
     * 加载全部场景种子数据
     * <p>
     * V1.1升级：根据ScenarioDataProvider类型自动选择数据源
     * - filesystem: 从V1.1外部目录加载
     * - classpath: 使用V1.0内嵌硬编码数据
     */
    @Transactional
    public void loadAll() {
        log.info("=== Loading scenario seed data (provider={}) ===", dataProvider.getProviderType());

        if ("filesystem".equals(dataProvider.getProviderType())) {
            loadFromV11Data();
        } else {
            loadFromV10Hardcoded();
        }

        log.info("=== Scenario seed data loaded successfully (provider={}) ===", dataProvider.getProviderType());
    }

    /**
     * V1.1数据加载路径 — 从外部文件系统读取
     * <p>
     * 每个步骤独立容错，避免单步主键冲突导致后续步骤全部跳过
     */
    private void loadFromV11Data() {
        V11ScenarioDataLoader loader = new V11ScenarioDataLoader(
            new V11ScenarioDataReader(dataProvider));

        loadSafely("v11-customers", () -> loader.loadCustomers().forEach(customerRepo::save));
        loadSafely("v11-legalEntities", () -> loader.loadLegalEntities().forEach(legalEntityRepo::save));
        loadSafely("v11-groupRelationships", () -> loader.loadGroupRelationships().forEach(groupRelRepo::save));
        loadSafely("v11-bankRelationship", () -> loader.loadBankRelationshipSnapshot().ifPresent(bankRelRepo::save));
        loadSafely("v11-creditFacilities", () -> loader.loadCreditFacilities().forEach(creditFacilityRepo::save));
        loadSafely("v11-productCatalog", () -> loader.loadProductKnowledgeCards().forEach(productCatalogRepo::save));
        loadSafely("policyRules", this::loadPolicyRules);  // 政策规则暂保留硬编码（V1.1无对应数据文件）
        loadSafely("v11-externalEvents", () -> loader.loadExternalEvents().forEach(this::saveExternalEventSafely));
        loadSafely("v11-kycGapProfile", () -> loader.loadKycGapProfile().ifPresent(kycGapRepo::save));
        loadSafely("v11-transactions", () -> loader.loadTransactions().forEach(transactionFlowRepo::save));
        loadSafely("v11-historicalInteractions", () -> loader.loadHistoricalInteractions().forEach(interactionRepo::save));

        log.info("[V11] Loaded data from external source: {}", dataProvider.getRootDescription());
    }

    /**
     * V1.0数据加载路径 — 使用硬编码数据（classpath fallback）
     * <p>
     * 每个步骤独立容错，避免单步主键冲突导致后续步骤全部跳过
     */
    private void loadFromV10Hardcoded() {
        loadSafely("customerMaster", this::loadCustomerMaster);
        loadSafely("legalEntities", this::loadLegalEntities);
        loadSafely("groupRelationships", this::loadGroupRelationships);
        loadSafely("bankRelationship", this::loadBankRelationship);
        loadSafely("creditFacilities", this::loadCreditFacilities);
        loadSafely("productCatalog", this::loadProductCatalog);
        loadSafely("policyRules", this::loadPolicyRules);
        loadSafely("externalEvents", this::loadExternalEvents);
        loadSafely("kycGapProfile", this::loadKycGapProfile);
        loadSafely("transactions", this::loadTransactions);
    }

    /**
     * 安全加载：捕获单步异常，不阻断后续步骤
     */
    private void loadSafely(String stepName, Runnable loader) {
        try {
            loader.run();
        } catch (Exception e) {
            log.warn("Seed data step '{}' skipped (may already exist): {}", stepName, e.getMessage());
        }
    }

    /**
     * 检查种子数据是否已加载
     * <p>
     * 同时检查客户主档和外部事件，避免部分加载时跳过重试
     */
    public boolean isLoaded() {
        // 主客户ID因数据版本而异（V1.0: CUST-CORP-0001, V1.1: CUST-001），按 provider 归属判断
        String primaryCustomerId = "filesystem".equals(dataProvider.getProviderType())
            ? "CUST-001"
            : "CUST-CORP-0001";
        Integer customerCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM customer WHERE customer_id = ?", Integer.class, primaryCustomerId);
        Integer eventCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM external_event", Integer.class);
        boolean customerLoaded = customerCount != null && customerCount > 0;
        boolean eventsLoaded = eventCount != null && eventCount > 0;
        if (customerLoaded && !eventsLoaded) {
            log.warn("Customer data loaded but external events missing — will retry full load");
            return false;
        }
        return customerLoaded && eventsLoaded;
    }

    private void loadCustomerMaster() {
        // 集团本部
        customerRepo.save(new Customer(
            "CUST-CORP-0001", "华东精工装备集团有限公司", "华东精工集团",
            "91330000MA27DEMO", LocalDate.of(2005, 3, 15),  // TODO: DEMO placeholder — replace with real credit code before production
            500_000_000L, Industry.MANUFACTURING, "浙江省杭州市",
            EnterpriseScale.LARGE, CustomerTier.STRATEGIC, LocalDate.of(2018, 6, 1),
            "RM-ZW-001", "张伟", "杭州城西支行",
            true, ListedStatus.UNLISTED, RiskLevel.MEDIUM,
            List.of("高端数控机床", "智能装配线", "工业机器人"),
            List.of("制造业龙头", "集团客户", "设备付款激增"),
            "集团客户，下属3家子公司，授信1.5亿，存款8200万，流水2.8亿。近期设备付款+32%，智能制造二期项目备案中。",
            null, null));

        log.info("Loaded customer master: 1 record");
    }

    private void loadLegalEntities() {
        legalEntityRepo.save(new LegalEntity("ENT-GRP-0001", "CUST-CORP-0001",
            "华东精工装备集团有限公司", "集团本部/母公司", "100%", "CUST-CORP-0001", "ACTIVE", "EV-MASTER-001"));
        legalEntityRepo.save(new LegalEntity("ENT-SUB-0001", "CUST-CORP-0001",
            "华东精工智能制造有限公司", "核心子公司", "60%", "CUST-CORP-0002", "ACTIVE", "EV-MASTER-001"));
        legalEntityRepo.save(new LegalEntity("ENT-SUB-0002", "CUST-CORP-0001",
            "华东精工自动化设备有限公司", "控股子公司", "45%", "CUST-CORP-0003", "ACTIVE", "EV-MASTER-001"));

        log.info("Loaded legal entities: 3 records");
    }

    private void loadGroupRelationships() {
        groupRelRepo.save(new GroupRelationship(UUID.randomUUID(), "CUST-CORP-0001",
            "ENT-GRP-0001", "ENT-SUB-0001", "OWNS", 60));
        groupRelRepo.save(new GroupRelationship(UUID.randomUUID(), "CUST-CORP-0001",
            "ENT-GRP-0001", "ENT-SUB-0002", "OWNS", 45));

        log.info("Loaded group relationships: 2 records");
    }

    private void loadBankRelationship() {
        bankRelRepo.save(new BankRelationshipSnapshot(
            UUID.randomUUID(), "CUST-CORP-0001", "2026-06",
            82_000_000L, 280_000_000L, 150_000_000L,
            150_000_000L, 68_000_000L, 82_000_000L,
            20_000_000L, 5_000_000L, 1200,
            true, false, 0L,
            4, "A", "存款下降趋势;设备付款激增+32%"));

        log.info("Loaded bank relationship snapshot: 1 record");
    }

    private void loadCreditFacilities() {
        creditFacilityRepo.save(new CreditFacility(
            "FAC-HDEG-GRP-2026", "CUST-CORP-0001", "华东精工装备集团有限公司",
            LocalDate.of(2025, 12, 1), LocalDate.of(2026, 12, 1),
            80_000_000L, 55_000_000L, 25_000_000L,
            55_000_000L, 0L, 0L,
            "集团本部信用担保", List.of("流动资金贷款", "银行承兑汇票"),
            List.of("不得用于股权投资"), List.of("季度财务报表", "重大事项及时报告"),
            "集团本部授信，可用额度2500万", "EV-CREDIT-001"));

        creditFacilityRepo.save(new CreditFacility(
            "FAC-HDEG-SUB1-2026", "CUST-CORP-0001", "华东精工智能制造有限公司",
            LocalDate.of(2026, 1, 15), LocalDate.of(2027, 1, 15),
            50_000_000L, 32_000_000L, 18_000_000L,
            32_000_000L, 0L, 0L,
            "母公司担保+设备抵押", List.of("流动资金贷款", "项目贷款"),
            List.of("不得用于房地产"), List.of("季度财务报表", "项目进度报告"),
            "智能制造子公司授信，可用额度1800万", "EV-CREDIT-001"));

        creditFacilityRepo.save(new CreditFacility(
            "FAC-HDEG-SUB2-2026", "CUST-CORP-0001", "华东精工自动化设备有限公司",
            LocalDate.of(2026, 3, 1), LocalDate.of(2027, 3, 1),
            20_000_000L, 13_000_000L, 7_000_000L,
            13_000_000L, 0L, 0L,
            "母公司担保", List.of("流动资金贷款"),
            List.of("不得用于股权投资", "不得用于房地产"),
            List.of("季度财务报表"),
            "自动化子公司授信，可用额度700万", "EV-CREDIT-001"));

        log.info("Loaded credit facilities: 3 records");
    }

    private void loadProductCatalog() {
        productCatalogRepo.save(new ProductKnowledgeCard(
            "PROD-WORKING-CAPITAL", "流动资金贷款",
            "满足企业日常经营周转资金需求",
            List.of("经营满2年", "信用评级BBB-以上", "无不良信用记录"),
            List.of("营业执照", "近2年财务报表", "纳税证明", "购销合同"),
            List.of("资金用途监控", "关联交易风险", "过度融资风险"),
            "客户有日常经营周转需求，或流水/订单增长但资金紧张",
            List.of("保证通过", "利率最低", "额度可以随时增加"),
            "EV-PRODUCT-001"));

        productCatalogRepo.save(new ProductKnowledgeCard(
            "PROD-PROJECT-LOAN", "项目贷款",
            "支持企业固定资产投资项目",
            List.of("项目已备案/核准", "自有资金比例≥30%", "项目可行性研究报告"),
            List.of("项目备案文件", "可行性研究报告", "环评批复", "自有资金证明", "工程预算"),
            List.of("项目延期风险", "成本超支风险", "市场变化风险"),
            "客户有新建/扩建项目，已取得备案文件",
            List.of("项目一定盈利", "资金可以挪用"),
            "EV-PRODUCT-001"));

        productCatalogRepo.save(new ProductKnowledgeCard(
            "PROD-BANK-ACCEPTANCE", "银行承兑汇票",
            "为企业商品交易提供支付便利",
            List.of("真实贸易背景", "交易对手资信良好", "保证金比例≥30%"),
            List.of("购销合同", "增值税发票", "交易对手资料"),
            List.of("贸易背景真实性", "保证金不足风险", "到期兑付风险"),
            "客户有设备采购、材料采购等大额支付需求",
            List.of("可以用于融资套利", "不需要真实贸易背景"),
            "EV-PRODUCT-001"));

        log.info("Loaded product catalog: 3 records");
    }

    private void loadPolicyRules() {
        policyRuleRepo.save(new PolicyRule(
            "RULE-CREDIT-001", "授信额度确认规则",
            PolicyRule.Severity.CRITICAL,
            "任何授信额度讨论必须基于:(1)可用额度核实;(2)项目主体确认;(3)客户表达语义消歧;(4)事实来源校验",
            "输出必须包含:可用额度→项目主体→客户表达→事实来源 四维校验结果"));

        policyRuleRepo.save(new PolicyRule(
            "RULE-CREDIT-002", "授信承诺禁止",
            PolicyRule.Severity.CRITICAL,
            "RM不得对客户做出任何授信额度承诺，包括暗示性承诺",
            "所有授信相关输出必须包含免责声明: '最终额度以审批结果为准'"));

        policyRuleRepo.save(new PolicyRule(
            "RULE-SIGNAL-001", "机会信号识别规则",
            PolicyRule.Severity.HIGH,
            "客户模糊表达(如'希望增加支持')必须识别为OpportunitySignal(FINANCING_NEED)，不得直接转为授信申请",
            "输出类型必须为OpportunitySignal，状态为DETECTED，需人工确认后才能转为InsightClaim"));

        policyRuleRepo.save(new PolicyRule(
            "RULE-FACT-001", "事实对账规则",
            PolicyRule.Severity.HIGH,
            "所有客户口头表达必须经过事实对账，不得直接作为事实记录",
            "输出必须标记notFact=true，并创建FactReconciliationCase"));

        policyRuleRepo.save(new PolicyRule(
            "RULE-CRM-001", "CRM回写确认规则",
            PolicyRule.Severity.CRITICAL,
            "所有CRM回写操作必须require_human_confirm=true",
            "每个CRM回写命令的requiresHumanConfirm字段必须为true"));

        log.info("Loaded policy rules: 5 records");
    }

    private void loadExternalEvents() {
        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-001", LocalDate.of(2026, 6, 20),
            ExternalEvent.SourceType.OFFICIAL_ANNOUNCEMENT,
            "浙江省发改委项目备案公示", "华东精工智能制造有限公司",
            "华东精工智能制造二期项目备案",
            "华东精工智能制造有限公司'智能制造二期产线扩建项目'于2026年6月20日完成备案，项目总投资1.2亿元。",
            ExternalEvent.Confidence.HIGH, ExternalEvent.Reliability.VERIFIED, true,
            List.of("产能扩张", "项目融资", "设备采购"),
            "可能产生项目融资需求和设备采购需求",
            "不得将项目备案等同于授信需求，需进一步确认客户实际意愿",
            "EV-EXT-001"));

        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-002", LocalDate.of(2026, 6, 25),
            ExternalEvent.SourceType.INDUSTRY,
            "中国机械工业联合会", "专用设备制造业",
            "2026年Q2专用设备制造业景气指数上升",
            "2026年Q2专用设备制造业景气指数为112.5，环比上升3.2个百分点，行业整体向好。",
            ExternalEvent.Confidence.MEDIUM, ExternalEvent.Reliability.VERIFIED, true,
            List.of("行业景气", "设备需求"),
            "行业景气可能带动客户业务增长",
            "行业景气不等于个体企业景气，需结合客户具体情况",
            "EV-EXT-002"));

        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-003", LocalDate.of(2026, 7, 1),
            ExternalEvent.SourceType.NEWS,
            "企查查", "浙江恒远钢材贸易有限公司",
            "浙江恒远钢材贸易有限公司涉及合同纠纷",
            "华东精工主要原材料供应商之一涉及合同纠纷，可能影响供应链稳定性。",
            ExternalEvent.Confidence.MEDIUM, ExternalEvent.Reliability.UNVERIFIED, true,
            List.of("供应链风险", "原材料供应"),
            "可能影响客户原材料供应稳定性",
            "供应商风险不直接等于客户风险，需评估替代供应商",
            "EV-EXT-003"));

        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-004", LocalDate.of(2026, 7, 5),
            ExternalEvent.SourceType.NEWS,
            "杭州日报", "华东精工装备集团有限公司",
            "华东精工集团获评省级专精特新企业",
            "华东精工装备集团有限公司获评2026年度浙江省专精特新中小企业。",
            ExternalEvent.Confidence.HIGH, ExternalEvent.Reliability.VERIFIED, true,
            List.of("品牌提升", "政策优惠", "融资便利"),
            "专精特新认定可能带来政策性融资渠道",
            "政策优惠不等于实际融资，需确认客户是否了解相关政策",
            "EV-EXT-004"));

        // V1.1新增：监管动态事件
        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-005", LocalDate.of(2026, 7, 8),
            ExternalEvent.SourceType.REGULATORY,
            "银保监会", "制造业企业",
            "银保监会发布制造业中长期贷款支持政策",
            "银保监会发布通知，鼓励银行加大对制造业中长期贷款投放，对专精特新企业给予优惠利率支持。",
            ExternalEvent.Confidence.HIGH, ExternalEvent.Reliability.VERIFIED, true,
            List.of("政策利好", "融资便利", "利率优惠"),
            "政策利好可能降低客户融资成本",
            "政策支持不等于自动获批，需按正常流程申请",
            "EV-EXT-005"));

        // V1.1新增：社交媒体舆情事件
        saveExternalEventSafely(new ExternalEvent(
            "E-EXT-006", LocalDate.of(2026, 7, 10),
            ExternalEvent.SourceType.SOCIAL_MEDIA,
            "微博财经", "华东精工装备集团有限公司",
            "华东精工集团智能制造二期项目引发行业关注",
            "多家财经自媒体关注华东精工智能制造二期项目，认为其可能成为行业标杆。",
            ExternalEvent.Confidence.LOW, ExternalEvent.Reliability.UNVERIFIED, false,
            List.of("品牌曝光", "行业关注"),
            "舆情关注可能提升客户品牌影响力",
            "社交媒体信息未经核实，不得作为业务决策依据",
            "EV-EXT-006"));

        log.info("Loaded external events: 6 records (V1.0: 4 + V1.1: 2)");
    }

    /**
     * 安全保存外部事件，忽略重复键冲突
     */
    private void saveExternalEventSafely(ExternalEvent event) {
        try {
            externalEventRepo.save(event);
        } catch (Exception e) {
            log.debug("External event already exists, skipping: eventId={}, error={}",
                event.eventId(), e.getMessage());
        }
    }

    private void loadKycGapProfile() {
        kycGapRepo.save(new KycGapProfile(
            "KYC-GAP-HDEG-20260705", "CUST-CORP-0001",
            LocalDate.of(2026, 7, 5),
            List.of("集团股权结构(3家子公司)", "现有授信1.5亿(3笔)", "日均存款8200万", "月均结算2.8亿"),
            List.of("智能制造二期项目(已备案，投资额待确认)", "设备采购计划(金额/时间待确认)"),
            List.of("3000万需求的具体含义(上次提及但未明确)"),
            List.of("客户说'希望增加支持' — 是授信? 流贷? 项目贷?"),
            List.of("二期项目实际投资额", "设备采购具体清单和时间表", "3000万需求的精确含义", "是否有其他银行介入"),
            List.of("二期项目总投资和资金安排?", "3000万支持的具体用途?", "设备采购计划和时间表?", "是否有其他银行在接触?")));

        log.info("Loaded KYC gap profile: 1 record");
    }

    private void loadTransactions() {
        String customerId = "CUST-CORP-0001";
        String accountId = "ACC-HDEG-001";
        Instant baseTime = LocalDate.of(2025, 8, 1).atStartOfDay(ZoneOffset.UTC).toInstant();

        // 2025年8月 - 日常经营
        saveTransaction(customerId, accountId, "TXN-20250801", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("15000000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "货款回笼-数控机床订单", LocalDate.of(2025, 8, 3));
        saveTransaction(customerId, accountId, "TXN-20250802", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("8500000"), "CNY", "苏州精密模具有限公司", "模具制造",
            "贸易结算-设备配件销售", LocalDate.of(2025, 8, 7));
        saveTransaction(customerId, accountId, "TXN-20250803", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3200000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-特种钢材", LocalDate.of(2025, 8, 12));
        saveTransaction(customerId, accountId, "TXN-20250804", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2025, 8, 20));
        saveTransaction(customerId, accountId, "TXN-20250805", Transaction.TransactionType.FEE,
            new BigDecimal("45000"), "CNY", "本行-城西支行", "银行",
            "账户管理费及手续费", LocalDate.of(2025, 8, 25));

        // 2025年9月 - 季度末回款
        saveTransaction(customerId, accountId, "TXN-20250901", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("22000000"), "CNY", "上海汽车集团股份有限公司", "汽车制造",
            "货款回笼-智能装配线项目尾款", LocalDate.of(2025, 9, 2));
        saveTransaction(customerId, accountId, "TXN-20250902", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("12000000"), "CNY", "广州南方重工机械有限公司", "重型机械",
            "贸易结算-大型设备出口结算", LocalDate.of(2025, 9, 8));
        saveTransaction(customerId, accountId, "TXN-20250903", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("5800000"), "CNY", "华东精工智能制造有限公司", "智能制造",
            "集团内部调拨-子公司运营资金", LocalDate.of(2025, 9, 10));
        saveTransaction(customerId, accountId, "TXN-20250904", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("1500000"), "CNY", "杭州人力资源服务有限公司", "人力资源",
            "员工工资代发", LocalDate.of(2025, 9, 15));
        saveTransaction(customerId, accountId, "TXN-20250905", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("6800000"), "CNY", "宁波海天塑机集团有限公司", "塑料机械",
            "设备销售回款", LocalDate.of(2025, 9, 18));
        saveTransaction(customerId, accountId, "TXN-20250906", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2025, 9, 20));
        saveTransaction(customerId, accountId, "TXN-20250907", Transaction.TransactionType.WITHDRAWAL,
            new BigDecimal("5000000"), "CNY", null, null,
            "大额提现-供应商现金结算", LocalDate.of(2025, 9, 25));

        // 2025年10月 - 日常经营
        saveTransaction(customerId, accountId, "TXN-20251001", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("9500000"), "CNY", "比亚迪股份有限公司", "新能源汽车",
            "工业机器人订单回款", LocalDate.of(2025, 10, 5));
        saveTransaction(customerId, accountId, "TXN-20251002", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("15000000"), "CNY", "三一重工股份有限公司", "工程机械",
            "贸易结算-成套设备销售", LocalDate.of(2025, 10, 10));
        saveTransaction(customerId, accountId, "TXN-20251003", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("4200000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-合金钢材", LocalDate.of(2025, 10, 15));
        saveTransaction(customerId, accountId, "TXN-20251004", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("800000"), "CNY", "浙江省税务局", "政府",
            "增值税及附加税缴纳", LocalDate.of(2025, 10, 20));
        saveTransaction(customerId, accountId, "TXN-20251005", Transaction.TransactionType.TRANSFER_IN,
            new BigDecimal("3000000"), "CNY", "华东精工自动化设备有限公司", "自动化设备",
            "子公司利润上缴", LocalDate.of(2025, 10, 28));

        // 2025年11月 - 季度末+研发投入
        saveTransaction(customerId, accountId, "TXN-20251101", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("18000000"), "CNY", "中联重科股份有限公司", "工程机械",
            "大型设备订单回款", LocalDate.of(2025, 11, 3));
        saveTransaction(customerId, accountId, "TXN-20251102", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("22000000"), "CNY", "徐工集团工程机械有限公司", "工程机械",
            "贸易结算-出口东南亚设备结算", LocalDate.of(2025, 11, 8));
        saveTransaction(customerId, accountId, "TXN-20251103", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("6500000"), "CNY", "德国西门子有限公司", "工业自动化",
            "进口数控系统采购", LocalDate.of(2025, 11, 12));
        saveTransaction(customerId, accountId, "TXN-20251104", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("2000000"), "CNY", "浙江大学工业技术研究院", "科研院所",
            "智能制造研发合作经费", LocalDate.of(2025, 11, 15));
        saveTransaction(customerId, accountId, "TXN-20251105", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2025, 11, 20));
        saveTransaction(customerId, accountId, "TXN-20251106", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("7500000"), "CNY", "合肥国轩高科动力能源有限公司", "新能源",
            "设备销售回款", LocalDate.of(2025, 11, 25));

        // 2025年12月 - 年末大额结算
        saveTransaction(customerId, accountId, "TXN-20251201", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("25000000"), "CNY", "上海汽车集团股份有限公司", "汽车制造",
            "年度框架协议结算-智能产线", LocalDate.of(2025, 12, 2));
        saveTransaction(customerId, accountId, "TXN-20251202", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("30000000"), "CNY", "印度塔塔钢铁有限公司", "钢铁",
            "出口贸易结算-成套设备出口印度", LocalDate.of(2025, 12, 5));
        saveTransaction(customerId, accountId, "TXN-20251203", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("8500000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "年末原材料集中采购", LocalDate.of(2025, 12, 10));
        saveTransaction(customerId, accountId, "TXN-20251204", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("5500000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款+年末提前还款", LocalDate.of(2025, 12, 15));
        saveTransaction(customerId, accountId, "TXN-20251205", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("1200000"), "CNY", "杭州人力资源服务有限公司", "人力资源",
            "年终奖及工资代发", LocalDate.of(2025, 12, 20));
        saveTransaction(customerId, accountId, "TXN-20251206", Transaction.TransactionType.FEE,
            new BigDecimal("68000"), "CNY", "本行-城西支行", "银行",
            "年度账户管理费及手续费", LocalDate.of(2025, 12, 28));
        saveTransaction(customerId, accountId, "TXN-20251207", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3500000"), "CNY", "浙江省税务局", "政府",
            "企业所得税年度汇算清缴", LocalDate.of(2025, 12, 30));

        // 2026年1月 - 新年开局
        saveTransaction(customerId, accountId, "TXN-20260101", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("12000000"), "CNY", "苏州精密模具有限公司", "模具制造",
            "新年度订单预付款", LocalDate.of(2026, 1, 5));
        saveTransaction(customerId, accountId, "TXN-20260102", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("18000000"), "CNY", "广州南方重工机械有限公司", "重型机械",
            "贸易结算-设备交付结算", LocalDate.of(2026, 1, 10));
        saveTransaction(customerId, accountId, "TXN-20260103", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("4500000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-一季度备货", LocalDate.of(2026, 1, 15));
        saveTransaction(customerId, accountId, "TXN-20260104", Transaction.TransactionType.LOAN_DISBURSE,
            new BigDecimal("10000000"), "CNY", "本行-城西支行", "银行",
            "新年度流动资金贷款放款", LocalDate.of(2026, 1, 18));
        saveTransaction(customerId, accountId, "TXN-20260105", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("1500000"), "CNY", "杭州人力资源服务有限公司", "人力资源",
            "员工工资代发", LocalDate.of(2026, 1, 20));
        saveTransaction(customerId, accountId, "TXN-20260106", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("5800000"), "CNY", "宁波海天塑机集团有限公司", "塑料机械",
            "设备销售回款", LocalDate.of(2026, 1, 28));

        // 2026年2月 - 春节前后
        saveTransaction(customerId, accountId, "TXN-20260201", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("8000000"), "CNY", "比亚迪股份有限公司", "新能源汽车",
            "工业机器人订单回款", LocalDate.of(2026, 2, 5));
        saveTransaction(customerId, accountId, "TXN-20260202", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("16000000"), "CNY", "三一重工股份有限公司", "工程机械",
            "贸易结算-设备销售结算", LocalDate.of(2026, 2, 10));
        saveTransaction(customerId, accountId, "TXN-20260203", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("2800000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购", LocalDate.of(2026, 2, 15));
        saveTransaction(customerId, accountId, "TXN-20260204", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2026, 2, 20));
        saveTransaction(customerId, accountId, "TXN-20260205", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3500000"), "CNY", "华东精工智能制造有限公司", "智能制造",
            "集团内部调拨-子公司运营资金", LocalDate.of(2026, 2, 25));

        // 2026年3月 - 季度末+项目启动
        saveTransaction(customerId, accountId, "TXN-20260301", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("20000000"), "CNY", "上海汽车集团股份有限公司", "汽车制造",
            "智能产线二期预付款", LocalDate.of(2026, 3, 2));
        saveTransaction(customerId, accountId, "TXN-20260302", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("25000000"), "CNY", "印度塔塔钢铁有限公司", "钢铁",
            "出口贸易结算-二期设备出口", LocalDate.of(2026, 3, 8));
        saveTransaction(customerId, accountId, "TXN-20260303", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("9000000"), "CNY", "德国西门子有限公司", "工业自动化",
            "智能制造二期设备采购-进口数控系统", LocalDate.of(2026, 3, 12));
        saveTransaction(customerId, accountId, "TXN-20260304", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3000000"), "CNY", "浙江大学工业技术研究院", "科研院所",
            "智能制造二期研发合作经费", LocalDate.of(2026, 3, 15));
        saveTransaction(customerId, accountId, "TXN-20260305", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2026, 3, 20));
        saveTransaction(customerId, accountId, "TXN-20260306", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("11000000"), "CNY", "中联重科股份有限公司", "工程机械",
            "设备销售回款", LocalDate.of(2026, 3, 25));
        saveTransaction(customerId, accountId, "TXN-20260307", Transaction.TransactionType.FEE,
            new BigDecimal("52000"), "CNY", "本行-城西支行", "银行",
            "账户管理费及手续费", LocalDate.of(2026, 3, 28));

        // 2026年4月 - 日常经营
        saveTransaction(customerId, accountId, "TXN-20260401", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("13500000"), "CNY", "合肥国轩高科动力能源有限公司", "新能源",
            "设备销售回款", LocalDate.of(2026, 4, 3));
        saveTransaction(customerId, accountId, "TXN-20260402", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("19000000"), "CNY", "广州南方重工机械有限公司", "重型机械",
            "贸易结算-大型设备销售结算", LocalDate.of(2026, 4, 8));
        saveTransaction(customerId, accountId, "TXN-20260403", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("5500000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-特种钢材", LocalDate.of(2026, 4, 12));
        saveTransaction(customerId, accountId, "TXN-20260404", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("1500000"), "CNY", "杭州人力资源服务有限公司", "人力资源",
            "员工工资代发", LocalDate.of(2026, 4, 15));
        saveTransaction(customerId, accountId, "TXN-20260405", Transaction.TransactionType.TRANSFER_IN,
            new BigDecimal("4000000"), "CNY", "华东精工自动化设备有限公司", "自动化设备",
            "子公司利润上缴", LocalDate.of(2026, 4, 20));
        saveTransaction(customerId, accountId, "TXN-20260406", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("7200000"), "CNY", "苏州精密模具有限公司", "模具制造",
            "设备配件销售回款", LocalDate.of(2026, 4, 25));

        // 2026年5月 - 扩产信号增强
        saveTransaction(customerId, accountId, "TXN-20260501", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("16000000"), "CNY", "比亚迪股份有限公司", "新能源汽车",
            "工业机器人批量订单回款", LocalDate.of(2026, 5, 2));
        saveTransaction(customerId, accountId, "TXN-20260502", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("28000000"), "CNY", "徐工集团工程机械有限公司", "工程机械",
            "贸易结算-出口中东设备大额结算", LocalDate.of(2026, 5, 8));
        saveTransaction(customerId, accountId, "TXN-20260503", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("12000000"), "CNY", "德国西门子有限公司", "工业自动化",
            "智能制造二期设备采购-第二批", LocalDate.of(2026, 5, 12));
        saveTransaction(customerId, accountId, "TXN-20260504", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3500000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-二期项目备料", LocalDate.of(2026, 5, 15));
        saveTransaction(customerId, accountId, "TXN-20260505", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2026, 5, 20));
        saveTransaction(customerId, accountId, "TXN-20260506", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("2500000"), "CNY", "浙江大学工业技术研究院", "科研院所",
            "智能制造二期研发合作经费-第二期", LocalDate.of(2026, 5, 22));
        saveTransaction(customerId, accountId, "TXN-20260507", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("9000000"), "CNY", "宁波海天塑机集团有限公司", "塑料机械",
            "设备销售回款", LocalDate.of(2026, 5, 28));

        // 2026年6月 - 近期大额贸易结算增加（扩展意向信号）
        saveTransaction(customerId, accountId, "TXN-20260601", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("22000000"), "CNY", "上海汽车集团股份有限公司", "汽车制造",
            "智能产线二期进度款", LocalDate.of(2026, 6, 2));
        saveTransaction(customerId, accountId, "TXN-20260602", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("30000000"), "CNY", "印度塔塔钢铁有限公司", "钢铁",
            "出口贸易结算-成套设备出口大额结算", LocalDate.of(2026, 6, 5));
        saveTransaction(customerId, accountId, "TXN-20260603", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("15000000"), "CNY", "泰国暹罗水泥集团", "建材",
            "出口贸易结算-海外设备出口泰国", LocalDate.of(2026, 6, 8));
        saveTransaction(customerId, accountId, "TXN-20260604", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("15000000"), "CNY", "德国西门子有限公司", "工业自动化",
            "智能制造二期设备采购-第三批（核心设备）", LocalDate.of(2026, 6, 10));
        saveTransaction(customerId, accountId, "TXN-20260605", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("6800000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购-二期项目大宗采购", LocalDate.of(2026, 6, 12));
        saveTransaction(customerId, accountId, "TXN-20260606", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2026, 6, 20));
        saveTransaction(customerId, accountId, "TXN-20260607", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("1800000"), "CNY", "杭州人力资源服务有限公司", "人力资源",
            "员工工资代发+项目组人员扩招", LocalDate.of(2026, 6, 22));
        saveTransaction(customerId, accountId, "TXN-20260608", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("11000000"), "CNY", "中联重科股份有限公司", "工程机械",
            "设备销售回款", LocalDate.of(2026, 6, 25));
        saveTransaction(customerId, accountId, "TXN-20260609", Transaction.TransactionType.FEE,
            new BigDecimal("55000"), "CNY", "本行-城西支行", "银行",
            "账户管理费及手续费", LocalDate.of(2026, 6, 28));

        // 2026年7月 - 最新月份（扩展意向信号持续增强）
        saveTransaction(customerId, accountId, "TXN-20260701", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("18000000"), "CNY", "三一重工股份有限公司", "工程机械",
            "大型设备订单回款", LocalDate.of(2026, 7, 2));
        saveTransaction(customerId, accountId, "TXN-20260702", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("25000000"), "CNY", "越南VIN集团", "综合集团",
            "出口贸易结算-东南亚市场拓展大额结算", LocalDate.of(2026, 7, 5));
        saveTransaction(customerId, accountId, "TXN-20260703", Transaction.TransactionType.TRADE_SETTLEMENT,
            new BigDecimal("18000000"), "CNY", "广州南方重工机械有限公司", "重型机械",
            "贸易结算-国内设备大额结算", LocalDate.of(2026, 7, 8));
        saveTransaction(customerId, accountId, "TXN-20260704", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("8000000"), "CNY", "德国西门子有限公司", "工业自动化",
            "智能制造二期设备采购-尾款", LocalDate.of(2026, 7, 10));
        saveTransaction(customerId, accountId, "TXN-20260705", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("3500000"), "CNY", "浙江恒远钢材贸易有限公司", "钢铁",
            "原材料采购", LocalDate.of(2026, 7, 12));
        saveTransaction(customerId, accountId, "TXN-20260706", Transaction.TransactionType.TRANSFER_OUT,
            new BigDecimal("2000000"), "CNY", "浙江大学工业技术研究院", "科研院所",
            "智能制造二期研发合作经费-第三期", LocalDate.of(2026, 7, 15));
        saveTransaction(customerId, accountId, "TXN-20260707", Transaction.TransactionType.LOAN_REPAY,
            new BigDecimal("2800000"), "CNY", "本行-城西支行", "银行",
            "流动资金贷款季度还款", LocalDate.of(2026, 7, 20));
        saveTransaction(customerId, accountId, "TXN-20260708", Transaction.TransactionType.DEPOSIT,
            new BigDecimal("9500000"), "CNY", "合肥国轩高科动力能源有限公司", "新能源",
            "设备销售回款", LocalDate.of(2026, 7, 25));

        log.info("Loaded transactions: 85 records (12 months for CUST-CORP-0001)");
    }

    private void saveTransaction(String customerId, String accountId, String txnId,
                                  Transaction.TransactionType type, BigDecimal amount,
                                  String currency, String counterparty,
                                  String counterpartyIndustry, String description,
                                  LocalDate txnDate) {
        transactionFlowRepo.save(new Transaction(
            UUID.randomUUID(), txnId, customerId, accountId,
            type, amount, currency, counterparty, counterpartyIndustry,
            description, txnDate, Instant.now()));
    }
}
