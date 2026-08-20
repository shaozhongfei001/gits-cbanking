package com.gien.gits.api.service;

import com.gien.gits.knowledge.KnowledgeElement;
import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeWikiPort;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

/**
 * 知识装配器（P23：知识地图驱动报告生成）。
 *
 * <p>按任务从知识地图组装 LLM 上下文：知识地图导航（锁定知识领域）+ 任务关联的知识条目
 * （KI）及其知识要素（KE）内容 + 业务数据。输出为 LLM 可读的 Markdown，供
 * {@code LlmClient} 作为 systemPrompt 注入，实现"大模型优先读知识地图再生成报告"。</p>
 *
 * <p>fail-closed：任何 KI/KE 拉取为空时跳过该条目，不抛异常；返回上下文可能为空（调用方决定）。</p>
 */
public final class KnowledgeAssembler {

    private final KnowledgeElementPort elementPort;
    private final KnowledgeWikiPort wikiPort;

    public KnowledgeAssembler(KnowledgeElementPort elementPort, KnowledgeWikiPort wikiPort) {
        this.elementPort = Objects.requireNonNull(elementPort);
        this.wikiPort = Objects.requireNonNull(wikiPort);
    }

    /**
     * 组装知识上下文。
     *
     * @param scope         知识地图/域范围（锁定知识领域）
     * @param knowledgeItemIds 任务关联的知识条目（KI）列表（来自激活合同 knowledgeItemIds）
     * @param businessContext  业务数据（客户/事件/KYC 等组装好的文本）
     * @return LLM 可读知识上下文 Markdown
     */
    public String assemble(String scope, List<String> knowledgeItemIds, String businessContext) {
        StringBuilder sb = new StringBuilder(512);
        sb.append("### 知识地图导航（权威受控）\n");
        String mapNav = wikiPort.renderMap(scope);
        if (!mapNav.isBlank()) {
            sb.append(mapNav).append('\n');
        }

        sb.append("\n### 任务关联知识条目（KI→KE）\n");
        if (knowledgeItemIds != null && !knowledgeItemIds.isEmpty()) {
            for (String kiId : knowledgeItemIds) {
                List<KnowledgeElement> elements = elementPort.listByKnowledgeItem(kiId);
                if (elements.isEmpty()) {
                    continue;
                }
                sb.append("#### ").append(kiId).append('\n');
                for (KnowledgeElement element : elements) {
                    sb.append("- [").append(element.kind()).append("] ")
                            .append(element.name()).append("：")
                            .append(element.content()).append('\n');
                }
            }
        }

        if (businessContext != null && !businessContext.isBlank()) {
            sb.append("\n### 业务数据\n").append(businessContext).append('\n');
        }
        return sb.toString();
    }

    /**
     * 抽取指定 KI 的供应链图谱数据（校 KI-FRONT 上游/下游/解读 KE 内嵌 JSON）。
     *
     * <p>KE content 在 specs/knowledge-architecture/elements 中为结构化字符串；
     * 本方法对其做防御性解析，返回供前端渲染图谱的可读段落。任一 KE 缺失则跳过，
     * 不抛异常（fail-closed）。</p>
     *
     * @param supplyChainKiIds 供应链知识条目（通常为 KI-FRONT-001）
     * @return 图谱 Markdown 段（空字符串表示无数据）
     */
    public String supplyChainMarkdown(List<String> supplyChainKiIds) {
        StringBuilder sb = new StringBuilder();
        if (supplyChainKiIds == null) {
            return sb.toString();
        }
        for (String kiId : supplyChainKiIds) {
            List<KnowledgeElement> elements = elementPort.listByKnowledgeItem(kiId);
            for (KnowledgeElement el : elements) {
                String name = el.name();
                String content = el.content();
                if (content == null || content.isBlank()) {
                    continue;
                }
                if (content.startsWith("[")) {
                    sb.append("- ").append(renderStructured(content)).append('\n');
                } else if (name != null && (name.contains("解读") || name.contains("位置"))) {
                    sb.append(content).append('\n');
                } else {
                    sb.append("- ").append(name).append("：")
                            .append(content.lines().findFirst().orElse("")).append('\n');
                }
            }
        }
        return sb.toString().strip();
    }

    /** 把 KE content 里嵌的 JSON 数组（供应商/下游/解读）转成人类可读行。 */
    private String renderStructured(String content) {
        // content 是含中文的 JSON 数组字符串；提取 [ ] 子串并防御性解析
        int start = content.indexOf('[');
        int end = content.lastIndexOf(']');
        String json = (start >= 0 && end > start) ? content.substring(start, end + 1) : content;
        java.util.List<String> items = new java.util.ArrayList<>();
        try {
            com.fasterxml.jackson.databind.ObjectMapper om = new com.fasterxml.jackson.databind.ObjectMapper();
            com.fasterxml.jackson.databind.JsonNode arr = om.readTree(json);
            if (arr.isArray()) {
                for (com.fasterxml.jackson.databind.JsonNode n : arr) {
                    items.add(renderNode(n));
                }
            }
        } catch (Exception ignore) {
            return content.lines().findFirst().orElse(content);
        }
        return items.isEmpty() ? content.lines().findFirst().orElse(content) : String.join("；", items);
    }

    /** 渲染 JSON 对象节点为一行：{name or integrator_name}【品类/行业】(数值字段)。 */
    private String renderNode(com.fasterxml.jackson.databind.JsonNode n) {
        StringBuilder line = new StringBuilder();
        String name = n.has("name") ? n.get("name").asText()
                : n.has("integrator_name") ? n.get("integrator_name").asText()
                : n.has("customerId") ? n.get("customerId").asText() : "";
        if (!name.isBlank()) {
            line.append(name);
        }
        line.append(nodeFields(n,
                "category", "industry", "customerType",
                "last12mPurchaseCnyWan", "last12mSalesCnyWan", "contract_value_cny_wan",
                "pctOfAnnualPurchase", "pctOfAnnualSales", "orderGrowthPct",
                "priceTrend", "paymentPreference", "paymentTerms",
                "role", "bargainingPower", "stabilityRiskLevel"));
        return line.toString().trim();
    }

    private String nodeFields(com.fasterxml.jackson.databind.JsonNode n, String... keys) {
        java.util.List<String> parts = new java.util.ArrayList<>();
        for (String k : keys) {
            if (n.has(k) && !n.get(k).isNull() && !n.get(k).asText().isBlank()) {
                parts.add(keyToLabel(k) + " " + n.get(k).asText());
            }
        }
        return parts.isEmpty() ? "" : "：" + String.join(" / ", parts);
    }

    private String keyToLabel(String key) {
        return switch (key) {
            case "category" -> "品类";
            case "industry" -> "行业";
            case "customerType" -> "客户类型";
            case "last12mPurchaseCnyWan" -> "近12月采购(万)";
            case "last12mSalesCnyWan" -> "近12月销售(万)";
            case "contract_value_cny_wan" -> "合同(万)";
            case "pctOfAnnualPurchase" -> "采购占比%";
            case "pctOfAnnualSales" -> "销售占比%";
            case "orderGrowthPct" -> "订单同比%";
            case "priceTrend" -> "价格";
            case "paymentPreference" -> "付款工具";
            case "paymentTerms" -> "付款条件";
            case "role" -> "角色";
            case "bargainingPower" -> "议价";
            case "stabilityRiskLevel" -> "稳定性";
            default -> key;
        };
    }
}
