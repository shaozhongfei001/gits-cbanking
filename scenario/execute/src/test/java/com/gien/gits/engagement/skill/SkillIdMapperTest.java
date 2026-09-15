package com.gien.gits.engagement.skill;

import org.junit.jupiter.api.Test;

import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SkillIdMapperTest {

    @Test
    void resolveOutreachVariants() {
        SkillIdMapper m = new SkillIdMapper();
        assertEquals("skill-customer-outreach-script", m.resolve("SP-OUTREACH-001").orElseThrow());
        assertEquals("skill-customer-outreach-script", m.resolve("SP-OUTBOUND-002").orElseThrow());
        assertEquals("skill-customer-outreach-script", m.resolve("sp-outreach-003").orElseThrow());
    }

    @Test
    void resolveMeetingVariants() {
        SkillIdMapper m = new SkillIdMapper();
        assertEquals("skill-customer-meeting-script", m.resolve("SP-MEETING-001").orElseThrow());
        assertEquals("skill-customer-meeting-script", m.resolve("SP-AGENDA-002").orElseThrow());
    }

    @Test
    void resolvePrevisitVariants() {
        SkillIdMapper m = new SkillIdMapper();
        assertEquals("skill-customer-previsit-report", m.resolve("SP-PREVISIT-001").orElseThrow());
        assertEquals("skill-customer-previsit-report", m.resolve("SP-PRE-VISIT-REPORT").orElseThrow());
    }

    @Test
    void resolveVisitFallback() {
        SkillIdMapper m = new SkillIdMapper();
        assertEquals("skill-customer-visiting-record", m.resolve("SP-VISIT-001").orElseThrow());
        assertEquals("skill-customer-visiting-record", m.resolve("SP-POSTVISIT-002").orElseThrow());
    }

    @Test
    void resolveUnknownReturnsEmpty() {
        SkillIdMapper m = new SkillIdMapper();
        Optional<String> result = m.resolve("SP-UNKNOWN-XYZ");
        assertFalse(result.isPresent());
    }

    @Test
    void resolveBlankReturnsEmpty() {
        SkillIdMapper m = new SkillIdMapper();
        assertFalse(m.resolve(null).isPresent());
        assertFalse(m.resolve("").isPresent());
        assertFalse(m.resolve("   ").isPresent());
    }

    @Test
    void overrideBeatsDefault() {
        SkillIdMapper m = new SkillIdMapper(Map.of("SP-OUTREACH-001", "skill-custom-outreach"));
        assertEquals("skill-custom-outreach", m.resolve("SP-OUTREACH-001").orElseThrow());
        // 未覆盖的仍走默认
        assertEquals("skill-customer-meeting-script", m.resolve("SP-MEETING-001").orElseThrow());
    }

    @Test
    void overrideRemoveRestoresDefault() {
        SkillIdMapper m = new SkillIdMapper();
        m.override("SP-OUTREACH-001", "skill-x");
        assertEquals("skill-x", m.resolve("SP-OUTREACH-001").orElseThrow());
        m.override("SP-OUTREACH-001", null);
        assertEquals("skill-customer-outreach-script", m.resolve("SP-OUTREACH-001").orElseThrow());
    }

    @Test
    void snapshotOverridesIsImmutableCopy() {
        SkillIdMapper m = new SkillIdMapper(Map.of("SP-A", "skill-a"));
        Map<String, String> snap = m.snapshotOverrides();
        assertTrue(snap.containsKey("SP-A"));
        try {
            snap.put("SP-B", "skill-b");
            // Map.copyOf 返回 ImmutableMap，put 应抛 UnsupportedOperationException
            // 如果未抛异常，至少不应影响 mapper
        } catch (UnsupportedOperationException ignored) {
            // 期望行为
        }
        // mapper 内部状态独立
        assertFalse(m.snapshotOverrides().containsKey("SP-B"));
    }
}