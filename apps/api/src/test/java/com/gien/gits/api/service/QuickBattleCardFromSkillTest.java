package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.gien.gits.api.dto.SkillReportSection;
import com.gien.gits.engagement.QuickBattleCard;
import java.util.List;
import org.junit.jupiter.api.Test;

class QuickBattleCardFromSkillTest {

    @Test
    void mapsKiSectionsToListsWithoutInventingSeedProducts() {
        List<SkillReportSection> sections = List.of(
                new SkillReportSection("KI-009 企业客户基本信息", "行业：精密制造，年营收约 18 亿"),
                new SkillReportSection("产业链八维研判", "中游集成，议价能力偏弱"),
                new SkillReportSection("KI-FRONT-006 产品候选", "供应链票据贴现方案，核对应收账期"),
                new SkillReportSection("KI-FRONT-005 KYC", "补齐实控人及关联担保口径"));

        QuickBattleCard card = QuickBattleCardFromSkill.map(
                sections, "华东精工装备集团有限公司", "了解二期项目资金需求", "STRATEGIC", "MEDIUM");

        assertEquals("华东精工装备集团有限公司", card.customerName());
        assertEquals("了解二期项目资金需求", card.visitObjective());
        assertEquals("STRATEGIC", card.customerTier());
        assertEquals("MEDIUM", card.riskLevel());
        assertTrue(card.keyPoints().stream().anyMatch(p -> p.contains("精密制造")));
        assertTrue(card.keyPoints().stream().anyMatch(p -> p.contains("中游集成")));
        assertTrue(card.productHints().stream().anyMatch(p -> p.contains("供应链票据贴现方案")));
        assertTrue(card.dontForget().stream().anyMatch(p -> p.contains("实控人")));
        assertFalse(card.productHints().stream().anyMatch(p -> p.contains("流动资金贷款")));
        assertEquals("", card.bottomLine());
    }

    @Test
    void emptySectionsYieldEmptyListsAndBlankBottomLine() {
        QuickBattleCard card = QuickBattleCardFromSkill.map(
                List.of(), "华东精工", "访前沟通", "CORE", "LOW");

        assertTrue(card.keyPoints().isEmpty());
        assertTrue(card.productHints().isEmpty());
        assertTrue(card.dontForget().isEmpty());
        assertEquals("", card.bottomLine());
        assertEquals("华东精工", card.customerName());
        assertEquals("访前沟通", card.visitObjective());
    }

    @Test
    void bottomLineOnlyWhenHeadingContainsBottomLineKeyword() {
        List<SkillReportSection> sections = List.of(
                new SkillReportSection("风险底线", "不得承诺授信额度"),
                new SkillReportSection("KI-009 客户概况", "客户基本面稳健"));

        QuickBattleCard card = QuickBattleCardFromSkill.map(sections, "A", "B", "", "");

        assertEquals("不得承诺授信额度", card.bottomLine());
        assertTrue(card.keyPoints().contains("客户基本面稳健"));
    }

    @Test
    void nullSectionsYieldEmptyListsAndBlankBottomLine() {
        QuickBattleCard card = QuickBattleCardFromSkill.map(null, "华东精工", "访前沟通", "CORE", "LOW");

        assertTrue(card.keyPoints().isEmpty());
        assertTrue(card.productHints().isEmpty());
        assertTrue(card.dontForget().isEmpty());
        assertEquals("", card.bottomLine());
        assertEquals("华东精工", card.customerName());
        assertEquals("访前沟通", card.visitObjective());
    }

    @Test
    void blankContentSectionsAreSkipped() {
        List<SkillReportSection> sections = List.of(
                new SkillReportSection("KI-009 企业客户基本信息", "   "),
                new SkillReportSection("KI-FRONT-006 产品候选", null));

        QuickBattleCard card = QuickBattleCardFromSkill.map(sections, "A", "B", "CORE", "LOW");

        assertTrue(card.keyPoints().isEmpty());
        assertTrue(card.productHints().isEmpty());
        assertEquals("", card.bottomLine());
    }

    @Test
    void contentLongerThanMaxCharsIsTruncated() {
        String longContent = "长".repeat(300);
        List<SkillReportSection> sections = List.of(
                new SkillReportSection("KI-009 企业客户基本信息", longContent));

        QuickBattleCard card = QuickBattleCardFromSkill.map(sections, "A", "B", "CORE", "LOW");

        assertEquals(1, card.keyPoints().size());
        assertEquals(QuickBattleCardFromSkill.CONTENT_MAX_CHARS, card.keyPoints().get(0).length());
    }

    @Test
    void nullFieldValuesAreNormalized() {
        List<SkillReportSection> sections = List.of(
                new SkillReportSection(null, null),
                new SkillReportSection("风险底线", " 不得越过权限  "));

        QuickBattleCard card = QuickBattleCardFromSkill.map(sections, null, null, null, null);

        assertEquals("", card.customerName());
        assertEquals("", card.visitObjective());
        assertEquals("", card.customerTier());
        assertEquals("", card.riskLevel());
        assertEquals("不得越过权限", card.bottomLine());
        assertTrue(card.keyPoints().isEmpty());
    }
}
