package com.gien.gits.customerjourney;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

public record CustomerJourney(
        UUID journeyId,
        UUID operatingCaseId,
        String customerId,
        String customerName,
        JourneyPhase phase,
        Instant startedAt,
        Instant updatedAt,
        String journeyName) {

    public CustomerJourney {
        Objects.requireNonNull(journeyId, "journeyId");
        Objects.requireNonNull(operatingCaseId, "operatingCaseId");
        customerId = requireText(customerId, "customerId");
        Objects.requireNonNull(phase, "phase");
        Objects.requireNonNull(startedAt, "startedAt");
    }

    /**
     * 兼容构造器：不提供 journeyName 的历史调用点保持编译与行为不变（名称置 null）。
     *
     * <p>名称缺失时，读取侧按 {@link CustomerJourneyNaming#defaultName} 统一派生，
     * 不在构造期伪造值。</p>
     */
    public CustomerJourney(UUID journeyId,
                           UUID operatingCaseId,
                           String customerId,
                           String customerName,
                           JourneyPhase phase,
                           Instant startedAt,
                           Instant updatedAt) {
        this(journeyId, operatingCaseId, customerId, customerName, phase, startedAt, updatedAt, null);
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " must not be blank");
        }
        return value;
    }
}
