package com.gien.gits.api.service;

import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.OutreachScript.OutreachChannel;
import com.gien.gits.engagement.OutreachScript.TalkingPoint;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.WritableOutreachScriptRepository;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 外联脚本：只调用 DKWS Skill，request 仅 customerId + 可选 channel。
 * GITS 不组装 KYC / 画像 / 产品，也不用本地 LLM 补话术。
 */
public class OutreachScriptService {

    static final String OUTREACH_SKILL_ID = "skill-customer-outreach-script";

    private static final Logger log = LoggerFactory.getLogger(OutreachScriptService.class);

    private final CustomerContextService customerContextService;
    private final WritableOutreachScriptRepository scriptRepository;
    private final SkillExecutionPort skillExecutionPort;

    public OutreachScriptService(
            CustomerContextService customerContextService,
            WritableOutreachScriptRepository scriptRepository,
            SkillExecutionPort skillExecutionPort) {
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.scriptRepository = Objects.requireNonNull(scriptRepository);
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort);
    }

    public OutreachScript generateScript(String customerId, String rmId,
                                          String operatingCaseId, String journeyId,
                                          OutreachChannel channel) {
        if (customerContextService.findCustomer(customerId).isEmpty()) {
            throw new IllegalArgumentException("Customer not found: " + customerId);
        }

        OutreachScript script;
        try {
            SkillExecutionResult result = skillExecutionPort.execute(
                    skillCommand(customerId, channel));
            if (!result.isOk() || result.data().isEmpty()) {
                log.warn("[OUTREACH-SKILL] dsh status={} empty={}, 不回填本地种子",
                        result.status(), result.data().isEmpty());
                script = emptyScript(customerId, rmId, operatingCaseId, journeyId, channel);
            } else {
                script = mapFromSkill(customerId, rmId, operatingCaseId, journeyId, channel, result.data());
            }
        } catch (SkillExecutionException ex) {
            log.warn("[OUTREACH-SKILL] DKWS 不可达，不使用本地种子: {}", ex.getMessage());
            script = emptyScript(customerId, rmId, operatingCaseId, journeyId, channel);
        }
        scriptRepository.save(script);
        return script;
    }

    private SkillExecutionCommand skillCommand(String customerId, OutreachChannel channel) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("customerId", customerId);
        if (channel != null) {
            request.put("channel", channel.name());
        }
        return new SkillExecutionCommand(
                OUTREACH_SKILL_ID, "REQ-OUTREACH-" + UUID.randomUUID(), customerId, request);
    }

    private static OutreachScript mapFromSkill(
            String customerId, String rmId, String operatingCaseId, String journeyId,
            OutreachChannel channel, Map<String, Object> data) {
        String objective = joinStrings(stringList(data.get("callObjectives")));
        if (objective.isBlank()) {
            objective = stringValue(data.get("scriptTitle"));
        }

        List<String> keyMessages = stringList(data.get("keyMessages"));
        String openingLine = keyMessages.isEmpty() ? "" : keyMessages.get(0);

        List<Map<String, Object>> sections = mapList(data.get("sections"));
        if (openingLine.isBlank() && !sections.isEmpty()) {
            openingLine = stringValue(sections.get(0).get("content"));
        }

        List<TalkingPoint> talkingPoints = new ArrayList<>();
        List<String> riskReminders = new ArrayList<>();
        String closingLine = "";
        String followUpAction = "";
        int priority = 1;
        for (Map<String, Object> section : sections) {
            String heading = stringValue(section.get("heading"));
            String content = stringValue(section.get("content"));
            talkingPoints.add(new TalkingPoint(heading, content, "", priority++));
            if (heading.contains("风险") && !content.isBlank()) {
                riskReminders.add(content);
            } else if (heading.contains("收口") && closingLine.isBlank()) {
                closingLine = content;
            } else if (heading.contains("后续") && followUpAction.isBlank()) {
                followUpAction = content;
            }
        }

        return new OutreachScript(
                newId("OS-"), customerId, resolveRmId(rmId), operatingCaseId, journeyId,
                channel, objective, openingLine, talkingPoints,
                riskReminders, closingLine, followUpAction, Instant.now());
    }

    private static OutreachScript emptyScript(
            String customerId, String rmId, String operatingCaseId, String journeyId,
            OutreachChannel channel) {
        return new OutreachScript(
                newId("OS-"), customerId, resolveRmId(rmId), operatingCaseId, journeyId,
                channel, "", "", List.of(), List.of(), "", "", Instant.now());
    }

    static String resolveRmId(String rmId) {
        return (rmId == null || rmId.isBlank()) ? "UNSET" : rmId;
    }

    private static String newId(String prefix) {
        return prefix + UUID.randomUUID().toString().substring(0, 8);
    }

    private static String joinStrings(List<String> values) {
        return values.isEmpty() ? "" : String.join("；", values);
    }

    private static List<String> stringList(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        for (Object item : list) {
            if (item instanceof String s && !s.isBlank()) {
                out.add(s);
            }
        }
        return out;
    }

    private static List<Map<String, Object>> mapList(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<Map<String, Object>> out = new ArrayList<>();
        for (Object item : list) {
            if (item instanceof Map<?, ?> map) {
                Map<String, Object> converted = new LinkedHashMap<>();
                map.forEach((k, v) -> converted.put(String.valueOf(k), v));
                out.add(converted);
            }
        }
        return out;
    }

    private static String stringValue(Object value) {
        return value instanceof String s ? s : "";
    }
}
