package com.gien.gits.api.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.adapter.skill.ServiceProposalMapper;
import com.gien.gits.engagement.port.ServiceProposal;
import com.gien.gits.engagement.port.ServiceProposalCommand;
import com.gien.gits.engagement.port.ServiceProposalPort;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.ontology.CreditFacility;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.Industry;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SP-20 服务建议书消费服务 — 组合 {@link SkillExecutionPort}（async）+ {@link ServiceProposalMapper}。
 *
 * <p>SP-20 长任务一律 async（契约 v1.4 §2.1）；BLOCKING 规则违规时 DKWS 回 PARTIAL，
 * 本服务透出 {@link ServiceProposal} 供闸门/前端消费。</p>
 *
 * <p>调用方 context 可能不是完整 ContextPackage（前端仅传 customerId）。
 * 本服务在调用 DKWS 前，依据客户主数据补齐 SP-20 最小必填集
 * （customerId/customerName/industry/enterpriseData）；调用方已提供完整必填集时透传。
 * 客户不存在时无法补齐，原样透传交由 DKWS 校验报错。</p>
 */
public class ServiceProposalService implements ServiceProposalPort {

    private static final Logger log = LoggerFactory.getLogger(ServiceProposalService.class);
    private static final String SKILL_ID = "SP-20";
    private static final String CONTEXT_SCHEMA_VERSION = "1.0.0";
    private static final String DEFAULT_ENGAGEMENT_PHASE = "FIRST_CONTACT";

    /** SP-20 ContextPackage 最小必填集（DKWS v1.4 validate），缺任一键视为不完整需补齐 */
    private static final List<String> REQUIRED_CONTEXT_KEYS =
        List.of("customerId", "customerName", "industry", "enterpriseData");

    private final SkillExecutionPort skillExecutionPort;
    private final ServiceProposalMapper mapper;
    private final ObjectMapper objectMapper;
    private final CustomerContextService customerContextService;

    public ServiceProposalService(SkillExecutionPort skillExecutionPort,
                                  ServiceProposalMapper mapper,
                                  ObjectMapper objectMapper,
                                  CustomerContextService customerContextService) {
        this.skillExecutionPort = skillExecutionPort;
        this.mapper = mapper;
        this.objectMapper = objectMapper;
        this.customerContextService = customerContextService;
    }

    @Override
    public ServiceProposal generate(ServiceProposalCommand command) {
        log.info("[SP-20] generate customerId={} requestId={}", command.customerId(), command.requestId());
        SkillExecutionCommand skillCmd = new SkillExecutionCommand(
            SKILL_ID, command.requestId(), command.customerId(),
            Map.of("task", "generate-service-proposal"),
            true, buildContext(command));
        SkillExecutionResult result = skillExecutionPort.execute(skillCmd);
        return mapResult(result);
    }

    /**
     * 组装 SP-20 ContextPackage：调用方已提供完整必填集则透传；
     * 否则仅凭 customerId 从客户主数据补齐最小必填集（DKWS v1.4 校验）。
     */
    private Map<String, Object> buildContext(ServiceProposalCommand command) {
        Map<String, Object> ctx = new LinkedHashMap<>(
            command.context() != null ? command.context() : Map.of());
        if (isCompleteContextPackage(ctx)) {
            return ctx;
        }
        Optional<Customer> customer = customerContextService.findCustomer(command.customerId());
        if (customer.isEmpty()) {
            log.warn("[SP-20] 客户不存在，无法补齐 ContextPackage: customerId={}", command.customerId());
            return ctx;
        }
        enrichContext(ctx, customerContextService.buildOperatingView(command.customerId()));
        return ctx;
    }

    private boolean isCompleteContextPackage(Map<String, Object> ctx) {
        return REQUIRED_CONTEXT_KEYS.stream()
            .allMatch(k -> ctx.get(k) != null && !String.valueOf(ctx.get(k)).isBlank());
    }

    private void enrichContext(Map<String, Object> ctx,
                               CustomerContextService.CustomerOperatingView view) {
        Customer customer = view.customer();
        ctx.putIfAbsent("schemaVersion", CONTEXT_SCHEMA_VERSION);
        ctx.putIfAbsent("customerId", customer.customerId());
        ctx.putIfAbsent("customerName", customer.customerName());
        ctx.putIfAbsent("industry", industryLabel(customer.industry()));
        ctx.putIfAbsent("engagementPhase", DEFAULT_ENGAGEMENT_PHASE);
        ctx.putIfAbsent("enterpriseData", buildEnterpriseData(view));
        ctx.putIfAbsent("proposalContext",
            Map.of("proposalType", "INITIAL",
                   "gateState", Map.of("passed", List.of("G0"), "current", "G1")));
    }

    private Map<String, Object> buildEnterpriseData(CustomerContextService.CustomerOperatingView view) {
        Customer customer = view.customer();
        Map<String, Object> basicInfo = new LinkedHashMap<>();
        basicInfo.put("registeredCapital", formatCny(customer.registeredCapitalCny()));
        basicInfo.put("establishedDate", customer.establishedDate() != null
            ? customer.establishedDate().toString() : null);
        basicInfo.put("registeredAddress", customer.region());
        basicInfo.put("businessScope", customer.mainProducts() != null
            ? String.join("、", customer.mainProducts()) : null);

        Map<String, Object> enterpriseData = new LinkedHashMap<>();
        enterpriseData.put("basicInfo", basicInfo);
        enterpriseData.put("creditFacility", buildCreditFacility(view.creditFacilities()));
        view.bankRelationship().ifPresent(b ->
            enterpriseData.put("transactionSummary",
                Map.of("monthlyAvgVolume", b.monthlySettlementCny())));
        return enterpriseData;
    }

    private Map<String, Object> buildCreditFacility(List<CreditFacility> facilities) {
        if (facilities == null || facilities.isEmpty()) {
            return Map.of();
        }
        long totalApproved = facilities.stream().mapToLong(CreditFacility::creditTotalCny).sum();
        long totalUsed = facilities.stream().mapToLong(CreditFacility::usedCreditCny).sum();
        return Map.of("totalApproved", totalApproved, "totalUsed", totalUsed);
    }

    private String industryLabel(Industry industry) {
        if (industry == null) {
            return null;
        }
        return switch (industry) {
            case MANUFACTURING -> "制造业";
            case FINANCE -> "金融业";
            case TECHNOLOGY -> "科技业";
            case REAL_ESTATE -> "房地产业";
            case ENERGY -> "能源业";
            case HEALTHCARE -> "医疗健康";
            case AGRICULTURE -> "农业";
            case LOGISTICS -> "物流业";
            case RETAIL -> "零售业";
            default -> "其他";
        };
    }

    private String formatCny(long yuan) {
        if (yuan >= 100_000_000L) {
            return (yuan / 100_000_000L) + "亿";
        }
        if (yuan >= 10_000L) {
            return (yuan / 10_000L) + "万";
        }
        return String.valueOf(yuan);
    }

    private ServiceProposal mapResult(SkillExecutionResult result) {
        if (result == null || !result.isOk() || result.data() == null) {
            log.warn("[SP-20] execute 未成功，返回空 ServiceProposal (ok={})",
                     result != null ? result.isOk() : "null");
            return ServiceProposal.empty();
        }
        try {
            JsonNode root = objectMapper.valueToTree(result.data());
            JsonNode resultNode = root.path("result");
            return mapper.fromResult(resultNode);
        } catch (Exception e) {
            log.error("[SP-20] data 映射失败，返回空 ServiceProposal: {}", e.getMessage());
            return ServiceProposal.empty();
        }
    }
}
