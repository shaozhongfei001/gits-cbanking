package com.gien.gits.customerjourney;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 经营旅程名称派生规则（单一事实来源）。
 *
 * <p>口径（Owner 决议 2026-09-25 / Q3-1、Q3-2）：</p>
 * <ul>
 *   <li>启动旅程时可人工提供名称；</li>
 *   <li>未提供（或缺省/空白）时派生 {@code {客户名称} 经营旅程 #{N}}，
 *       {@code N} 为该客户已有旅程按 {@code startedAt} 正序的序号；</li>
 *   <li>历史行 {@code journeyName} 为空时，读取侧用同一规则兜底显示，
 *       <b>不写入库、不伪造人工值</b>。</li>
 * </ul>
 */
public final class CustomerJourneyNaming {

    private static final String FALLBACK_CUSTOMER = "客户";

    private CustomerJourneyNaming() {
    }

    /** 派生缺省名称：{@code {客户名称} 经营旅程 #{N}}。ordinal 小于 1 时按 1 处理。 */
    public static String defaultName(String customerName, int ordinal) {
        String base = (customerName == null || customerName.isBlank())
                ? FALLBACK_CUSTOMER
                : customerName.trim();
        return base + " 经营旅程 #" + Math.max(ordinal, 1);
    }

    /**
     * 为一批旅程补齐名称（不改写入参，返回新实例列表）。
     *
     * <p>按 {@code customerId} 分组、组内按 {@code startedAt} 正序编号；
     * 已有非空名称的行保持原值不动。输出顺序与入参一致。</p>
     */
    public static List<CustomerJourney> withResolvedNames(List<CustomerJourney> journeys) {
        if (journeys == null || journeys.isEmpty()) {
            return List.of();
        }

        Map<String, List<CustomerJourney>> byCustomer = new HashMap<>();
        for (CustomerJourney journey : journeys) {
            byCustomer.computeIfAbsent(journey.customerId(), key -> new ArrayList<>()).add(journey);
        }

        Map<CustomerJourney, String> resolved = new HashMap<>();
        for (List<CustomerJourney> group : byCustomer.values()) {
            group.sort(Comparator.comparing(CustomerJourney::startedAt));
            for (int index = 0; index < group.size(); index++) {
                CustomerJourney journey = group.get(index);
                String name = (journey.journeyName() == null || journey.journeyName().isBlank())
                        ? defaultName(journey.customerName(), index + 1)
                        : journey.journeyName();
                resolved.put(journey, name);
            }
        }

        List<CustomerJourney> result = new ArrayList<>(journeys.size());
        for (CustomerJourney journey : journeys) {
            String name = resolved.getOrDefault(journey, journey.journeyName());
            if (name != null && name.equals(journey.journeyName())) {
                result.add(journey);
            } else {
                result.add(new CustomerJourney(
                        journey.journeyId(), journey.operatingCaseId(), journey.customerId(),
                        journey.customerName(), journey.phase(), journey.startedAt(),
                        journey.updatedAt(), name));
            }
        }
        return result;
    }
}
