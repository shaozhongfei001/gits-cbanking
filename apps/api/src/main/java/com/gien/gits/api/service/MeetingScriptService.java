package com.gien.gits.api.service;

import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.MeetingScript.AgendaItem;
import com.gien.gits.engagement.MeetingScript.KycQuestionItem;
import com.gien.gits.engagement.MeetingScript.ProductDiscussionItem;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.WritableMeetingScriptRepository;

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
 * 会面脚本：只调用 DKWS Skill，request 仅 customerId。
 * GITS 不组装 KYC / 画像 / 产品，也不用本地 LLM 补议程。
 */
public class MeetingScriptService {

    static final String MEETING_SKILL_ID = "skill-customer-meeting-script";

    private static final Logger log = LoggerFactory.getLogger(MeetingScriptService.class);

    private final CustomerContextService customerContextService;
    private final WritableMeetingScriptRepository scriptRepository;
    private final SkillExecutionPort skillExecutionPort;

    public MeetingScriptService(
            CustomerContextService customerContextService,
            WritableMeetingScriptRepository scriptRepository,
            SkillExecutionPort skillExecutionPort) {
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.scriptRepository = Objects.requireNonNull(scriptRepository);
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort);
    }

    public MeetingScript generateScript(String customerId, String rmId,
                                         String operatingCaseId, String journeyId) {
        if (customerContextService.findCustomer(customerId).isEmpty()) {
            throw new IllegalArgumentException("Customer not found: " + customerId);
        }

        MeetingScript script;
        try {
            SkillExecutionResult result = skillExecutionPort.execute(skillCommand(customerId));
            if (!result.isOk() || result.data().isEmpty()) {
                log.warn("[MEETING-SKILL] dsh status={} empty={}, 不回填本地种子",
                        result.status(), result.data().isEmpty());
                script = emptyScript(customerId, rmId, operatingCaseId, journeyId);
            } else {
                script = mapFromSkill(customerId, rmId, operatingCaseId, journeyId, result.data());
            }
        } catch (SkillExecutionException ex) {
            log.warn("[MEETING-SKILL] DKWS 不可达，不使用本地种子: {}", ex.getMessage());
            script = emptyScript(customerId, rmId, operatingCaseId, journeyId);
        }
        scriptRepository.save(script);
        return script;
    }

    private SkillExecutionCommand skillCommand(String customerId) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("customerId", customerId);
        return new SkillExecutionCommand(
                MEETING_SKILL_ID, "REQ-MEETING-" + UUID.randomUUID(), customerId, request);
    }

    private static MeetingScript mapFromSkill(
            String customerId, String rmId, String operatingCaseId, String journeyId,
            Map<String, Object> data) {
        List<Map<String, Object>> talkingPoints = mapList(data.get("talkingPoints"));
        List<Map<String, Object>> agendaRaw = mapList(data.get("agenda"));

        String meetingObjective = "";
        if (!talkingPoints.isEmpty()) {
            meetingObjective = stringValue(talkingPoints.get(0).get("title"));
        }
        if (meetingObjective.isBlank() && !agendaRaw.isEmpty()) {
            meetingObjective = stringValue(agendaRaw.get(0).get("topic"));
        }

        List<AgendaItem> agendaItems = new ArrayList<>();
        for (Map<String, Object> item : agendaRaw) {
            agendaItems.add(new AgendaItem(
                    stringValue(item.get("topic")),
                    0,
                    stringValue(item.get("time")),
                    ""));
        }

        List<KycQuestionItem> kycQuestions = new ArrayList<>();
        List<ProductDiscussionItem> productDiscussions = new ArrayList<>();
        for (Map<String, Object> point : talkingPoints) {
            String title = stringValue(point.get("title"));
            String detail = stringValue(point.get("detail"));
            if (title.contains("KYC") || title.contains("尽调")) {
                kycQuestions.add(new KycQuestionItem(title, detail, "", "TEXT"));
            } else if (title.contains("产品")) {
                productDiscussions.add(new ProductDiscussionItem("", title, detail, List.of()));
            }
        }

        return new MeetingScript(
                newId("MS-"), customerId, resolveRmId(rmId), operatingCaseId, journeyId,
                meetingObjective, "", agendaItems,
                kycQuestions, productDiscussions, stringList(data.get("sensitivePoints")),
                joinStrings(stringList(data.get("actionItems"))), Instant.now());
    }

    private static MeetingScript emptyScript(
            String customerId, String rmId, String operatingCaseId, String journeyId) {
        return new MeetingScript(
                newId("MS-"), customerId, resolveRmId(rmId), operatingCaseId, journeyId,
                "", "", List.of(), List.of(), List.of(), List.of(), "", Instant.now());
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
