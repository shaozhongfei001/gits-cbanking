package com.gien.gits.api.service.prompt;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class PromptTemplateTest {

    @Test
    void outreachAndMeetingSystemPromptsAreNotClones() {
        String outreach = PromptTemplate.outreachScriptSystemPrompt();
        String meeting = PromptTemplate.meetingScriptSystemPrompt();

        assertTrue(outreach.contains("约访") || outreach.contains("预约"));
        assertTrue(outreach.contains("2 分钟") || outreach.contains("2分钟"));
        assertTrue(outreach.contains("渠道"));
        assertFalse(outreach.contains("30–60 分钟") || outreach.contains("30-60 分钟"));

        assertTrue(meeting.contains("议程"));
        assertTrue(meeting.contains("KYC"));
        assertTrue(meeting.contains("产品"));
        assertTrue(meeting.contains("N分钟｜议题") || meeting.contains("分钟｜"));
        assertTrue(meeting.contains("约访") || meeting.contains("预约"));

        assertFalse(outreach.equals(meeting));
    }

    @Test
    void userPromptsDivergeByTaskAndChannelOrProducts() {
        String outreach = PromptTemplate.outreachScriptUserPrompt(
            "华东精工", "制造 | 大型", "股东结构", "进行中", "电话");
        String meeting = PromptTemplate.meetingScriptUserPrompt(
            "华东精工", "制造 | 大型", "股东结构", "进行中", "供应链融资");

        assertTrue(outreach.contains("电话"));
        assertTrue(outreach.contains("预约") || outreach.contains("约访"));
        assertTrue(outreach.contains("2分钟") || outreach.contains("2 分钟"));
        assertFalse(outreach.contains("候选产品"));

        assertTrue(meeting.contains("KYC"));
        assertTrue(meeting.contains("供应链融资"));
        assertTrue(meeting.contains("会面"));
        assertFalse(meeting.contains("2分钟内说完"));

        assertFalse(outreach.equals(meeting));
    }
}
