package com.gien.gits.api.productknowledge;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * 适配器级集成测试（L13 · 修复 F-L13-02）。
 *
 * <p>此前 503 用例只在控制器层 stub Port 抛异常，结构性覆盖不到
 * 「目录缺失」分支，导致 E2E S8 漏网。本类直接打真实文件系统，
 * 区分「源不可达 → 503」与「产品无投影 → 404」。</p>
 */
class KertReleaseSnapshotAdapterTest {

    private static final String PRODUCT_ID = "PROD-CM-001";
    private static final String SNAPSHOT = """
            {
              "productId": "PROD-CM-001",
              "releaseId": "RLS-2026.09.06.1",
              "bundleHash": "%s",
              "lifecycleState": "PUBLISHED",
              "isStale": false,
              "provenanceState": "DEMO",
              "purposeAllowed": {"INTERPRETATION": true, "RECOMMENDATION": false},
              "views": {"OVERVIEW": []},
              "generatedAt": "2026-09-06T12:00:00+08:00"
            }
            """.formatted("a".repeat(64));

    private KertReleaseSnapshotAdapter adapter(String dir) {
        return new KertReleaseSnapshotAdapter(dir, new ObjectMapper());
    }

    @Test
    void missingSnapshotDirIsFailedClosed(@TempDir Path tmp) throws Exception {
        Path absent = tmp.resolve("does-not-exist");
        assertThatThrownBy(() -> adapter(absent.toString()).load(PRODUCT_ID))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("不可达");
    }

    @Test
    void unconfiguredSnapshotDirIsFailedClosed() {
        assertThatThrownBy(() -> adapter("").load(PRODUCT_ID))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("未配置");
    }

    @Test
    void dirExistsButProductMissingReturnsEmpty(@TempDir Path tmp) {
        Optional<InterpretationProjection> loaded = adapter(tmp.toString()).load(PRODUCT_ID);
        assertThat(loaded).isEmpty();
    }

    @Test
    void corruptedProjectionIsFailedClosed(@TempDir Path tmp) throws Exception {
        Files.writeString(tmp.resolve(PRODUCT_ID + ".json"), "{ truncated");
        assertThatThrownBy(() -> adapter(tmp.toString()).load(PRODUCT_ID))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("不可解析");
    }

    @Test
    void readableProjectionIsLoaded(@TempDir Path tmp) throws Exception {
        Files.writeString(tmp.resolve(PRODUCT_ID + ".json"), SNAPSHOT);
        InterpretationProjection loaded = adapter(tmp.toString()).load(PRODUCT_ID).orElseThrow();
        assertThat(loaded.getReleaseId()).isEqualTo("RLS-2026.09.06.1");
        assertThat(loaded.getLifecycleState()).isEqualTo("PUBLISHED");
        assertThat(loaded.getIsStale()).isFalse();
        assertThat(loaded.getPurposeAllowed()).containsEntry("INTERPRETATION", true);
    }
}
