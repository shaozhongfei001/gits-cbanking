package com.gien.gits.api.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.gien.gits.ontology.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * V1.1场景数据加载器 — 将V1.1外部数据文件映射到领域对象
 * <p>
 * 数据映射关系：
 * <pre>
 * V1.1 文件                                → 领域对象
 * ──────────────────────────────────────────────────────────────
 * 02_master_data/customer_master.json       → Customer
 * 02_master_data/legal_entities.csv         → LegalEntity
 * 02_master_data/group_relationships.csv    → GroupRelationship
 * 03_bank_data/credit_facilities.csv        → CreditFacility
 * 03_bank_data/bank_relationship_monthly.csv → BankRelationshipSnapshot
 * 04_external_data/external_events.jsonl    → ExternalEvent
 * 05_knowledge/product_knowledge_cards.yaml → ProductKnowledgeCard
 * 05_knowledge/kyc_question_library.jsonl   → KycGapProfile (聚合)
 * 06_interactions/historical_interactions.jsonl → Interaction
 * </pre>
 * <p>
 * 关键业务不变量：
 * - 3000万≠自动新增授信 (Claim≠Fact)
 * - 可用额度≠新额度需求
 * - 项目主体≠授信主体
 * - 他行授信(PENDING_VERIFICATION)≠本行事实
 */
public class V11ScenarioDataLoader {

    private static final Logger log = LoggerFactory.getLogger(V11ScenarioDataLoader.class);
    private static final DateTimeFormatter DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private final V11ScenarioDataReader reader;

    public V11ScenarioDataLoader(V11ScenarioDataReader reader) {
        this.reader = reader;
    }

    // ========== Customer ==========

    public List<Customer> loadCustomers() {
        List<Customer> result = new ArrayList<>();
        reader.readJson("02_master_data/customer_master.json").ifPresent(node -> {
            if (node.isArray()) {
                for (JsonNode n : node) {
                    Customer c = mapCustomer(n);
                    if (c != null) result.add(c);
                }
            } else {
                Customer c = mapCustomer(node);
                if (c != null) result.add(c);
            }
        });
        log.info("[V11Loader] Loaded customers: {} records", result.size());
        return result;
    }

    private Customer mapCustomer(JsonNode n) {
        try {
            return new Customer(
                text(n, "customer_id"),
                text(n, "canonical_name"),
                text(n, "canonical_name"),  // shortName — V1.1无short_name字段
                null,                       // creditCode — V1.1不提供
                parseDate(text(n, "established_date")),
                longVal(n, "registered_capital_cny"),
                mapIndustryStr(text(n, "industry")),        // String for compatible constructor
                text(n, "region"),
                mapScale(text(n, "registered_capital_cny")), // String for compatible constructor
                mapTier(text(n, "customer_tier")),           // String for compatible constructor
                parseDate(text(n, "relationship_since")),
                text(n, "rm_id"),
                text(n, "rm_name"),
                text(n, "branch"),
                true,                       // groupCustomer
                n.path("listed").asBoolean(false) ? "LISTED" : "UNLISTED",  // String for compatible constructor
                mapRiskLevel(text(n, "risk_level")),        // String for compatible constructor
                toStringList(n.path("main_products")),
                toStringList(n.path("tags")),
                text(n, "relationship_summary")
            );
        } catch (Exception e) {
            log.warn("[V11Loader] Failed to map customer: {}", e.getMessage());
            return null;
        }
    }

    // ========== LegalEntity ==========

    public List<LegalEntity> loadLegalEntities() {
        List<LegalEntity> result = new ArrayList<>();
        V11ScenarioDataReader.CsvData csv = reader.readCsv("02_master_data/legal_entities.csv");
        for (Map<String, String> row : csv.rows()) {
            LegalEntity le = new LegalEntity(
                row.get("entity_id"),
                row.getOrDefault("bank_customer_id", ""),
                row.get("name"),
                row.get("role"),
                row.getOrDefault("ownership_pct", "") + "%",
                row.getOrDefault("ownership_parent", ""),
                row.getOrDefault("status", "ACTIVE"),
                "EV-MASTER-V11"
            );
            result.add(le);
        }
        log.info("[V11Loader] Loaded legal entities: {} records", result.size());
        return result;
    }

    // ========== GroupRelationship ==========

    public List<GroupRelationship> loadGroupRelationships() {
        List<GroupRelationship> result = new ArrayList<>();
        V11ScenarioDataReader.CsvData csv = reader.readCsv("02_master_data/group_relationships.csv");
        for (Map<String, String> row : csv.rows()) {
            int pct = parseIntSafe(row.getOrDefault("ownership_pct", "0"));
            result.add(new GroupRelationship(
                UUID.randomUUID(),
                "CUST-001",  // customerId — 从customer_master.json获取
                row.get("from_entity"),
                row.get("to_entity"),
                row.getOrDefault("relation_type", "OWNS"),
                pct
            ));
        }
        log.info("[V11Loader] Loaded group relationships: {} records", result.size());
        return result;
    }

    // ========== CreditFacility ==========

    public List<CreditFacility> loadCreditFacilities() {
        List<CreditFacility> result = new ArrayList<>();
        V11ScenarioDataReader.CsvData csv = reader.readCsv("03_bank_data/credit_facilities.csv");
        for (Map<String, String> row : csv.rows()) {
            CreditFacility cf = new CreditFacility(
                row.get("facility_id"),
                row.getOrDefault("borrower_entity_id", ""),
                row.getOrDefault("facility_type", ""),
                parseDate(row.getOrDefault("approval_date", "")),
                parseDate(row.getOrDefault("expiry_date", "")),
                parseLongSafe(row.getOrDefault("approved_amount_cny", "0")),
                parseLongSafe(row.getOrDefault("used_amount_cny", "0")),
                parseLongSafe(row.getOrDefault("available_amount_cny", "0")),
                parseLongSafe(row.getOrDefault("used_amount_cny", "0")),  // currentLoanBalanceCny
                0L,  // bankAcceptanceBillBalanceCny
                0L,  // guaranteeBalanceCny
                row.getOrDefault("allowed_purpose", ""),
                parseListField(row.getOrDefault("allowed_purpose", "")),
                parseListField(row.getOrDefault("restriction", "")),
                List.of("季度财务报表"),
                row.getOrDefault("restriction", ""),
                "EV-CREDIT-V11"
            );
            result.add(cf);
        }
        log.info("[V11Loader] Loaded credit facilities: {} records", result.size());
        return result;
    }

    // ========== BankRelationshipSnapshot ==========

    public Optional<BankRelationshipSnapshot> loadBankRelationshipSnapshot() {
        V11ScenarioDataReader.CsvData csv = reader.readCsv("03_bank_data/bank_relationship_monthly.csv");
        if (csv.isEmpty()) return Optional.empty();

        // 取最新月份
        Map<String, String> latest = csv.rows().get(csv.rowCount() - 1);
        return Optional.of(new BankRelationshipSnapshot(
            UUID.randomUUID(),
            "CUST-001",
            latest.getOrDefault("month", "2026-07"),
            parseLongSafe(latest.getOrDefault("deposit_balance_cny", "0")),
            parseLongSafe(latest.getOrDefault("deposit_balance_cny", "0")) * 3,  // monthlySettlementCny (估算)
            parseLongSafe(latest.getOrDefault("credit_used_cny", "0")),
            parseLongSafe(latest.getOrDefault("credit_approved_cny", "0")),
            parseLongSafe(latest.getOrDefault("credit_used_cny", "0")),
            parseLongSafe(latest.getOrDefault("credit_available_cny", "0")),
            0L,  // bankAcceptanceBillBalanceCny
            0L,  // guaranteeBalanceCny
            0,   // payrollEmployees
            true, false, 0L,
            4, "A", "V1.1数据加载"
        ));
    }

    // ========== ExternalEvent ==========

    public List<ExternalEvent> loadExternalEvents() {
        List<ExternalEvent> result = new ArrayList<>();
        List<JsonNode> events = reader.readJsonl("04_external_data/external_events.jsonl");
        for (JsonNode n : events) {
            ExternalEvent ee = mapExternalEvent(n);
            if (ee != null) result.add(ee);
        }
        log.info("[V11Loader] Loaded external events: {} records", result.size());
        return result;
    }

    private ExternalEvent mapExternalEvent(JsonNode n) {
        try {
            // 使用String兼容构造器
            return new ExternalEvent(
                text(n, "event_id"),
                parseDate(text(n, "date")),
                mapSourceTypeStr(text(n, "category")),
                text(n, "source_name"),
                text(n, "entity"),
                text(n, "title"),
                text(n, "content"),
                mapConfidenceStr(text(n, "relevance")),
                mapReliabilityStr(text(n, "reliability")),
                true,
                toStringList(n.path("tags")),
                text(n, "opportunity_hint"),
                text(n, "no_go"),
                "EV-EXT-V11"
            );
        } catch (Exception e) {
            log.warn("[V11Loader] Failed to map external event: {}", e.getMessage());
            return null;
        }
    }

    // ========== ProductKnowledgeCard ==========

    public List<ProductKnowledgeCard> loadProductKnowledgeCards() {
        List<ProductKnowledgeCard> result = new ArrayList<>();
        reader.readYaml("05_knowledge/product_knowledge_cards.yaml").ifPresent(root -> {
            JsonNode products = root.path("products");
            if (products.isArray()) {
                for (JsonNode p : products) {
                    if (!"ACTIVE".equals(text(p, "status"))) continue;
                    ProductKnowledgeCard card = new ProductKnowledgeCard(
                        text(p, "product_id"),
                        text(p, "name"),
                        text(p, "business_problem"),
                        toStringList(p.path("key_conditions")),
                        toStringList(p.path("required_materials")),
                        toStringList(p.path("not_suitable")),
                        text(p, "scenario_fit"),
                        toStringList(p.path("prohibited")),
                        "EV-PRODUCT-V11"
                    );
                    result.add(card);
                }
            }
        });
        log.info("[V11Loader] Loaded product knowledge cards: {} records", result.size());
        return result;
    }

    // ========== KycGapProfile ==========

    public Optional<KycGapProfile> loadKycGapProfile() {
        // V1.1 KYC gap从kyc_question_library.jsonl聚合
        List<JsonNode> questions = reader.readJsonl("05_knowledge/kyc_question_library.jsonl");
        if (questions.isEmpty()) return Optional.empty();

        List<String> openQuestions = new ArrayList<>();
        for (JsonNode q : questions) {
            if ("ACTIVE".equals(text(q, "status"))) {
                openQuestions.add(text(q, "question"));
            }
        }

        return Optional.of(new KycGapProfile(
            "KYC-GAP-V11-001",
            "CUST-001",
            LocalDate.now(),
            List.of("集团5家法人实体", "综合授信1.5亿", "他行授信待核实"),
            List.of("智能制造二期项目(已备案)", "设备采购计划待确认"),
            List.of("3000万需求的具体含义(上次提及但未明确)"),
            List.of("客户说'希望增加支持' — 是授信? 流贷? 项目贷?"),
            List.of("二期项目实际投资额", "设备采购具体清单和时间表", "3000万需求的精确含义", "是否有其他银行介入"),
            openQuestions
        ));
    }

    // ========== Interaction (historical) ==========

    public List<Interaction> loadHistoricalInteractions() {
        List<Interaction> result = new ArrayList<>();
        List<JsonNode> interactions = reader.readJsonl("06_interactions/historical_interactions.jsonl");
        for (JsonNode n : interactions) {
            Interaction i = mapInteraction(n);
            if (i != null) result.add(i);
        }
        log.info("[V11Loader] Loaded historical interactions: {} records", result.size());
        return result;
    }

    private Interaction mapInteraction(JsonNode n) {
        try {
            UUID interactionId = UUID.randomUUID();
            List<Interaction.Participant> participants = mapParticipants(n);
            Interaction.Participant initiator = participants.isEmpty()
                ? new Interaction.Participant("RM-001", Interaction.Participant.Role.RELATIONSHIP_MANAGER, "RM")
                : participants.get(0);

            return new Interaction(
                interactionId,
                UUID.randomUUID(),  // caseId — V1.1无此字段
                UUID.randomUUID(),  // journeyId — V1.1无此字段
                mapInteractionType(text(n, "channel")),
                Interaction.Direction.OUTBOUND,
                mapChannel(text(n, "channel")),
                initiator,
                participants,
                text(n, "raw_summary"),
                List.of(),
                Interaction.InteractionOutcome.COMPLETED,
                parseInstant(text(n, "date")),
                parseInstant(text(n, "date")).plusSeconds(3600),
                "EV-INTERACTION-V11-" + interactionId.toString().substring(0, 8)
            );
        } catch (Exception e) {
            log.warn("[V11Loader] Failed to map interaction: {}", e.getMessage());
            return null;
        }
    }

    private List<Interaction.Participant> mapParticipants(JsonNode n) {
        List<Interaction.Participant> result = new ArrayList<>();
        JsonNode participantsNode = n.path("participants");
        if (participantsNode.isArray()) {
            for (JsonNode p : participantsNode) {
                String pid = p.isTextual() ? p.asText() : p.path("id").asText("");
                String name = p.isTextual() ? p.asText() : p.path("name").asText("");
                result.add(new Interaction.Participant(
                    pid,
                    pid.startsWith("RM") || pid.startsWith("P-RM")
                        ? Interaction.Participant.Role.RELATIONSHIP_MANAGER
                        : Interaction.Participant.Role.CUSTOMER,
                    name
                ));
            }
        }
        return result;
    }

    // ========== Transaction (交易流水) ==========

    public List<Transaction> loadTransactions() {
        List<Transaction> result = new ArrayList<>();
        V11ScenarioDataReader.CsvData csv = reader.readCsv("03_bank_data/transactions_20260101_20260708.csv");
        for (Map<String, String> row : csv.rows()) {
            Transaction tx = mapTransaction(row);
            if (tx != null) result.add(tx);
        }
        log.info("[V11Loader] Loaded transactions: {} records", result.size());
        return result;
    }

    private Transaction mapTransaction(Map<String, String> row) {
        try {
            String purpose = row.getOrDefault("purpose", "");
            String direction = row.getOrDefault("direction", "");
            return new Transaction(
                UUID.randomUUID(),
                row.getOrDefault("transaction_id", ""),
                "CUST-001",  // V1.1 客户主档ID
                row.getOrDefault("account_id", ""),
                mapTransactionType(direction, purpose),
                BigDecimal.valueOf(parseDoubleSafe(row.getOrDefault("amount_cny", "0"))),
                "CNY",
                row.getOrDefault("counterparty_name", ""),
                row.getOrDefault("counterparty_type", ""),
                purpose,
                parseDate(row.getOrDefault("date", "")),
                Instant.now()
            );
        } catch (Exception e) {
            log.warn("[V11Loader] Failed to map transaction: {}", e.getMessage());
            return null;
        }
    }

    private Transaction.TransactionType mapTransactionType(String direction, String purpose) {
        if (purpose == null || purpose.isBlank()) {
            return "IN".equalsIgnoreCase(direction)
                ? Transaction.TransactionType.TRANSFER_IN
                : Transaction.TransactionType.TRANSFER_OUT;
        }
        if (purpose.contains("还款")) return Transaction.TransactionType.LOAN_REPAY;
        if (purpose.contains("放款") || purpose.contains("贷款到账")) return Transaction.TransactionType.LOAN_DISBURSE;
        if (purpose.contains("手续费") || purpose.contains("账户管理费")) return Transaction.TransactionType.FEE;
        if (purpose.contains("结算")) return Transaction.TransactionType.TRADE_SETTLEMENT;
        if ("IN".equalsIgnoreCase(direction)) return Transaction.TransactionType.TRANSFER_IN;
        return Transaction.TransactionType.TRANSFER_OUT;
    }

    private double parseDoubleSafe(String val) {
        if (val == null || val.isBlank()) return 0.0;
        try {
            return Double.parseDouble(val.trim().replace(",", ""));
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    // ========== Helper Methods ==========

    private String text(JsonNode n, String field) {
        JsonNode child = n.path(field);
        return child.isMissingNode() || child.isNull() ? "" : child.asText("");
    }

    private long longVal(JsonNode n, String field) {
        return n.path(field).asLong(0);
    }

    private LocalDate parseDate(String dateStr) {
        if (dateStr == null || dateStr.isBlank()) return null;
        try {
            return LocalDate.parse(dateStr.trim(), DATE_FMT);
        } catch (Exception e) {
            return null;
        }
    }

    private Instant parseInstant(String dateStr) {
        LocalDate ld = parseDate(dateStr);
        return ld != null ? ld.atStartOfDay().toInstant(java.time.ZoneOffset.UTC) : Instant.now();
    }

    private long parseLongSafe(String val) {
        if (val == null || val.isBlank()) return 0L;
        try {
            return Long.parseLong(val.trim().replace(",", ""));
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    private int parseIntSafe(String val) {
        if (val == null || val.isBlank()) return 0;
        try {
            return Integer.parseInt(val.trim());
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private List<String> toStringList(JsonNode node) {
        if (node == null || !node.isArray()) return List.of();
        List<String> result = new ArrayList<>();
        for (JsonNode item : node) {
            result.add(item.asText(""));
        }
        return result;
    }

    private List<String> parseListField(String val) {
        if (val == null || val.isBlank()) return List.of();
        return Arrays.stream(val.split("[、，,;]"))
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .toList();
    }

    // ========== Enum Mapping ==========

    private String mapIndustryStr(String industryStr) {
        if (industryStr == null || industryStr.isBlank()) return "MANUFACTURING";
        if (industryStr.contains("制造")) return "MANUFACTURING";
        if (industryStr.contains("科技") || industryStr.contains("信息")) return "TECHNOLOGY";
        if (industryStr.contains("贸易") || industryStr.contains("批发")) return "RETAIL";
        if (industryStr.contains("建筑") || industryStr.contains("房地产")) return "REAL_ESTATE";
        if (industryStr.contains("金融")) return "FINANCE";
        if (industryStr.contains("能源")) return "ENERGY";
        if (industryStr.contains("医疗") || industryStr.contains("医药")) return "HEALTHCARE";
        if (industryStr.contains("农业")) return "AGRICULTURE";
        if (industryStr.contains("物流") || industryStr.contains("运输")) return "LOGISTICS";
        return "OTHER";
    }

    private String mapScale(String capitalStr) {
        long capital = parseLongSafe(capitalStr);
        if (capital >= 400_000_000L) return "LARGE";       // ≥4亿
        if (capital >= 80_000_000L) return "MEDIUM";        // ≥8000万
        if (capital >= 3_000_000L) return "SMALL";          // ≥300万
        return "MICRO";
    }

    private String mapTier(String tierStr) {
        if (tierStr == null || tierStr.isBlank()) return "KEY";
        if (tierStr.contains("战略")) return "STRATEGIC";
        if (tierStr.contains("重点")) return "KEY";
        if (tierStr.contains("成长")) return "GROWTH";
        if (tierStr.contains("一般")) return "GENERAL";
        return "KEY";
    }

    private String mapRiskLevel(String riskStr) {
        if (riskStr == null || riskStr.isBlank()) return "MEDIUM";
        if (riskStr.contains("正常")) return "LOW";
        if (riskStr.contains("关注")) return "MEDIUM";
        if (riskStr.contains("次级") || riskStr.contains("可疑") || riskStr.contains("损失")) return "HIGH";
        return "MEDIUM";
    }

    private String mapSourceTypeStr(String category) {
        if (category == null) return "NEWS";
        return switch (category) {
            case "PROJECT_FILING" -> "OFFICIAL_ANNOUNCEMENT";
            case "TENDER" -> "INDUSTRY";
            case "INDUSTRY_NEWS" -> "INDUSTRY";
            case "COMPETITOR" -> "NEWS";
            case "SUPPLY_CHAIN" -> "NEWS";
            case "REGIONAL_ECONOMY" -> "INDUSTRY";
            case "REGULATORY" -> "REGULATORY";
            default -> "NEWS";
        };
    }

    private String mapConfidenceStr(String relevance) {
        if (relevance == null) return "MEDIUM";
        return switch (relevance) {
            case "HIGH" -> "HIGH";
            case "MEDIUM" -> "MEDIUM";
            case "LOW" -> "LOW";
            default -> "MEDIUM";
        };
    }

    private String mapReliabilityStr(String reliability) {
        if (reliability == null) return "UNVERIFIED";
        return switch (reliability) {
            case "VERIFIED", "HIGH" -> "VERIFIED";
            case "MEDIUM", "LOW" -> "UNVERIFIED";
            default -> "UNVERIFIED";
        };
    }

    private Interaction.InteractionType mapInteractionType(String channel) {
        if (channel == null) return Interaction.InteractionType.PHONE_CALL;
        return switch (channel.toUpperCase()) {
            case "PHONE", "PHONE_CALL" -> Interaction.InteractionType.PHONE_CALL;
            case "IN_PERSON", "FACE_TO_FACE", "VISIT" -> Interaction.InteractionType.FACE_TO_FACE_VISIT;
            case "VIDEO", "VIDEO_CONFERENCE" -> Interaction.InteractionType.VIDEO_CONFERENCE;
            case "WECHAT", "INSTANT_MESSAGE" -> Interaction.InteractionType.INSTANT_MESSAGE;
            case "EMAIL" -> Interaction.InteractionType.EMAIL;
            default -> Interaction.InteractionType.PHONE_CALL;
        };
    }

    private Channel mapChannel(String channel) {
        if (channel == null) return Channel.PHONE;
        return switch (channel.toUpperCase()) {
            case "PHONE", "PHONE_CALL" -> Channel.PHONE;
            case "IN_PERSON", "FACE_TO_FACE", "VISIT" -> Channel.FACE_TO_FACE;
            case "VIDEO", "VIDEO_CONFERENCE" -> Channel.VIDEO_CONFERENCE;
            case "WECHAT", "INSTANT_MESSAGE" -> Channel.INSTANT_MESSAGE;
            case "EMAIL" -> Channel.EMAIL;
            default -> Channel.PHONE;
        };
    }
}
