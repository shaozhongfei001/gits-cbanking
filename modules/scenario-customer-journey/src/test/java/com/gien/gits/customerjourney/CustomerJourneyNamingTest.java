package com.gien.gits.customerjourney;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.UUID;

import org.junit.jupiter.api.Test;

/**
 * 经营旅程名称派生规则测试（Owner 决议 2026-09-25 / Q3-1、Q3-2）。
 *
 * <p>注：本模块测试类路径仅含 JUnit 5（无 AssertJ），故沿用模块既有断言风格。</p>
 */
class CustomerJourneyNamingTest {

    private static final Instant BASE = Instant.parse("2026-09-25T06:00:00Z");

    private CustomerJourney journey(String customerId, String customerName, String name,
                                    Instant startedAt, JourneyPhase phase) {
        return new CustomerJourney(
                UUID.randomUUID(), UUID.randomUUID(), customerId, customerName,
                phase, startedAt, startedAt, name);
    }

    private List<String> names(List<CustomerJourney> journeys) {
        return journeys.stream().map(CustomerJourney::journeyName).toList();
    }

    private List<UUID> ids(List<CustomerJourney> journeys) {
        return journeys.stream().map(CustomerJourney::journeyId).toList();
    }

    @Test
    void defaultNameUsesCustomerNameAndOrdinal() {
        assertEquals("华东精工装备集团有限公司 经营旅程 #1",
                CustomerJourneyNaming.defaultName("华东精工装备集团有限公司", 1));
        assertEquals("华东精工装备集团有限公司 经营旅程 #3",
                CustomerJourneyNaming.defaultName("华东精工装备集团有限公司", 3));
    }

    @Test
    void defaultNameFallsBackForMissingCustomerNameAndClampsOrdinal() {
        assertEquals("客户 经营旅程 #1", CustomerJourneyNaming.defaultName(null, 1));
        assertEquals("客户 经营旅程 #1", CustomerJourneyNaming.defaultName("   ", 1));
        assertEquals("甲客户 经营旅程 #1", CustomerJourneyNaming.defaultName("甲客户", 0));
        assertEquals("甲客户 经营旅程 #2", CustomerJourneyNaming.defaultName("  甲客户  ", 2));
    }

    @Test
    void withResolvedNamesNumbersPerCustomerByStartedAtAscending() {
        CustomerJourney third = journey("CUST-001", "甲客户", null, BASE.plus(2, ChronoUnit.HOURS), JourneyPhase.PREVISIT_PREP);
        CustomerJourney second = journey("CUST-001", "甲客户", null, BASE.plus(1, ChronoUnit.HOURS), JourneyPhase.PRODUCT_MATCHING);
        CustomerJourney first = journey("CUST-001", "甲客户", null, BASE, JourneyPhase.KYC_COLLECT);

        // 入参顺序为倒序（模拟列表默认排序），输出顺序必须保持
        List<CustomerJourney> result = CustomerJourneyNaming.withResolvedNames(List.of(third, second, first));

        assertEquals(List.of(third.journeyId(), second.journeyId(), first.journeyId()), ids(result));
        assertEquals(List.of("甲客户 经营旅程 #3", "甲客户 经营旅程 #2", "甲客户 经营旅程 #1"), names(result));
    }

    @Test
    void withResolvedNamesKeepsManualNamesAndIsolatesOrdinalsPerCustomer() {
        CustomerJourney a1 = journey("CUST-001", "甲客户", null, BASE, JourneyPhase.KYC_COLLECT);
        CustomerJourney a2 = journey("CUST-001", "甲客户", "扩产融资专题旅程",
                BASE.plus(1, ChronoUnit.HOURS), JourneyPhase.PREVISIT_PREP);
        CustomerJourney b1 = journey("CUST-002", "乙客户", null, BASE, JourneyPhase.KYC_COLLECT);

        List<CustomerJourney> result = CustomerJourneyNaming.withResolvedNames(List.of(a1, a2, b1));

        // 客户内序号独立：乙客户从 #1 开始，不受甲客户条数影响；人工名称原样保留
        assertEquals(List.of("甲客户 经营旅程 #1", "扩产融资专题旅程", "乙客户 经营旅程 #1"), names(result));
    }

    @Test
    void withResolvedNamesPreservesOtherFieldsAndDerivesBlankNames() {
        CustomerJourney blank = journey("CUST-001", "甲客户", "   ", BASE, JourneyPhase.KYC_COLLECT);

        CustomerJourney resolved = CustomerJourneyNaming.withResolvedNames(List.of(blank)).get(0);

        assertEquals("甲客户 经营旅程 #1", resolved.journeyName());
        assertEquals(blank.journeyId(), resolved.journeyId());
        assertEquals(blank.operatingCaseId(), resolved.operatingCaseId());
        assertEquals(blank.customerId(), resolved.customerId());
        assertEquals(blank.customerName(), resolved.customerName());
        assertEquals(blank.phase(), resolved.phase());
        assertEquals(blank.startedAt(), resolved.startedAt());
    }

    @Test
    void withResolvedNamesReturnsEmptyListForNullOrEmptyInput() {
        assertTrue(CustomerJourneyNaming.withResolvedNames(null).isEmpty());
        assertTrue(CustomerJourneyNaming.withResolvedNames(List.of()).isEmpty());
    }

    @Test
    void legacyConstructorLeavesNameNullForReadSideDerivation() {
        CustomerJourney journey = new CustomerJourney(
                UUID.randomUUID(), UUID.randomUUID(), "CUST-001", "甲客户",
                JourneyPhase.KYC_COLLECT, BASE, BASE);

        assertNull(journey.journeyName());
        assertEquals("甲客户 经营旅程 #1",
                CustomerJourneyNaming.withResolvedNames(List.of(journey)).get(0).journeyName());
    }
}
