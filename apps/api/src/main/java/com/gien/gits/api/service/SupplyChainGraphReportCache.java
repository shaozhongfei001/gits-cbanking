package com.gien.gits.api.service;

import com.gien.gits.api.dto.SupplyChainGraphReport;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 供应链图谱报告进程内缓存。TTL 10 分钟，过期后视为不存在（对齐 DKWS 幂等缓存）。
 */
public class SupplyChainGraphReportCache {

    public static final Duration DEFAULT_TTL = Duration.ofMinutes(10);

    private final ConcurrentHashMap<String, Entry> store = new ConcurrentHashMap<>();
    private final Duration ttl;
    private final Clock clock;

    public SupplyChainGraphReportCache() {
        this(DEFAULT_TTL, Clock.systemUTC());
    }

    public SupplyChainGraphReportCache(Duration ttl, Clock clock) {
        this.ttl = ttl;
        this.clock = clock;
    }

    public void put(SupplyChainGraphReport report) {
        store.put(report.requestId(), new Entry(report, clock.instant().plus(ttl)));
    }

    public Optional<SupplyChainGraphReport> get(String requestId) {
        if (requestId == null || requestId.isBlank()) {
            return Optional.empty();
        }
        Entry entry = store.get(requestId);
        if (entry == null) {
            return Optional.empty();
        }
        if (clock.instant().isAfter(entry.expiresAt())) {
            store.remove(requestId, entry);
            return Optional.empty();
        }
        return Optional.of(entry.report());
    }

    private record Entry(SupplyChainGraphReport report, Instant expiresAt) {}
}
