package com.gien.gits.api.service;

import com.gien.gits.api.dto.SkillReportSection;
import com.gien.gits.engagement.QuickBattleCard;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Maps DKWS R1 {@code data.sections} onto the existing R2 {@link QuickBattleCard} shape.
 * Heading aliases match {@code frontend/src/utils/kiSection.ts}. Does not read H2 KYC/product seed.
 */
public final class QuickBattleCardFromSkill {

    static final int CONTENT_MAX_CHARS = 240;

    private static final Map<String, List<String>> ALIASES = Map.of(
            "KI-009", List.of("KI-009", "企业客户基本信息", "客户概况", "客户基本信息"),
            "KI-FRONT-002", List.of("KI-FRONT-002", "八维", "产业链八维"),
            "KI-FRONT-004", List.of("KI-FRONT-004", "事实承诺", "沟通话术", "承诺事项"),
            "KI-FRONT-005", List.of("KI-FRONT-005", "KYC"),
            "KI-FRONT-006", List.of("KI-FRONT-006", "产品候选", "产品组合"));

    private QuickBattleCardFromSkill() {
    }

    public static QuickBattleCard map(
            List<SkillReportSection> sections,
            String customerName,
            String visitObjective,
            String customerTier,
            String riskLevel) {
        List<SkillReportSection> safe = sections == null ? List.of() : sections;
        List<String> keyPoints = new ArrayList<>();
        addIfPresent(keyPoints, contentOf(safe, "KI-009"));
        addIfPresent(keyPoints, contentOf(safe, "KI-FRONT-002"));
        List<String> productHints = new ArrayList<>();
        addIfPresent(productHints, contentOf(safe, "KI-FRONT-006"));
        List<String> dontForget = new ArrayList<>();
        addIfPresent(dontForget, contentOf(safe, "KI-FRONT-004"));
        addIfPresent(dontForget, contentOf(safe, "KI-FRONT-005"));
        return new QuickBattleCard(
                "R2-" + UUID.randomUUID().toString().substring(0, 8),
                nullToEmpty(customerName),
                nullToEmpty(visitObjective),
                nullToEmpty(customerTier),
                nullToEmpty(riskLevel),
                keyPoints,
                productHints,
                dontForget,
                bottomLineOf(safe));
    }

    static String contentOf(List<SkillReportSection> sections, String kiId) {
        List<String> aliases = ALIASES.getOrDefault(kiId, List.of(kiId));
        for (SkillReportSection section : sections) {
            String heading = section.heading() == null ? "" : section.heading();
            String content = section.content() == null ? "" : section.content().trim();
            if (content.isEmpty()) {
                continue;
            }
            for (String alias : aliases) {
                if (heading.contains(alias)) {
                    return truncate(content);
                }
            }
        }
        return "";
    }

    private static String bottomLineOf(List<SkillReportSection> sections) {
        for (SkillReportSection section : sections) {
            String heading = section.heading() == null ? "" : section.heading();
            if (!heading.contains("底线")) {
                continue;
            }
            String content = section.content() == null ? "" : section.content().trim();
            return truncate(content);
        }
        return "";
    }

    private static void addIfPresent(List<String> target, String value) {
        if (!value.isEmpty()) {
            target.add(value);
        }
    }

    private static String truncate(String value) {
        if (value.length() <= CONTENT_MAX_CHARS) {
            return value;
        }
        return value.substring(0, CONTENT_MAX_CHARS);
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }
}
