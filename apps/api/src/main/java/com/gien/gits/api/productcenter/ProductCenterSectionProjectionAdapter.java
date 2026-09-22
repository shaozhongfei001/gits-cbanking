package com.gien.gits.api.productcenter;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * 读取 KERT 产品中心「章节投影」（{@code 04_serve/product-center/PROD-*.json}）的适配器。
 *
 * <p><b>分域口径</b>（{@code ONTOLOGY-SPLIT-DESIGN-V2.0} · Owner 裁定 O-1）：产品知识 8 章内容
 * <b>归 KERT（L2）</b>；GITS 作为 L3 <b>只读消费</b>，<b>不得</b>本地兜底生成内容。投影由 KERT 侧
 * {@code examples/product-recommendation-assets/tools/l40_build_product_center_sections.py}
 * 从产品卡<b>确定性派生</b>，每个对象的 {@code evidenceRefs} 可回译到卡片小节（{@code #S<节号>}）。</p>
 *
 * <p><b>受控失败（fail-closed）</b>：目录未配置 / 不可读 / 解析失败 ⇒ 抛
 * {@link ProductCenterSourceUnavailableException}（控制器转 503 {@code SOURCES_UNAVAILABLE}）；
 * 目录可用但该产品无投影 ⇒ 返回 {@link Optional#empty()}（前端显示明确的「未接入」状态，
 * <b>不</b>以示意数据填充）。</p>
 */
@Component
@ConditionalOnProperty(name = "gits.product-center.enabled", havingValue = "true", matchIfMissing = true)
public class ProductCenterSectionProjectionAdapter {

    private static final Logger log = LoggerFactory.getLogger(ProductCenterSectionProjectionAdapter.class);
    private static final TypeReference<Map<String, Object>> MAP_TYPE = new TypeReference<>() {
    };

    private final Path sectionDir;
    private final ObjectMapper objectMapper;

    public ProductCenterSectionProjectionAdapter(
            @Value("${gits.product-center.section-dir:}") String sectionDir,
            ObjectMapper objectMapper) {
        this.sectionDir = sectionDir == null || sectionDir.isBlank() ? null : Path.of(sectionDir);
        this.objectMapper = objectMapper;
    }

    /** 章节投影目录是否已配置（未配置即 fail-closed；调用方据此给出确切错误）。 */
    public boolean configured() {
        return sectionDir != null;
    }

    /**
     * 读取某产品的章节投影。
     *
     * @param productId 产品标识（{@code PROD-XXX-NNN}）
     * @return 投影内容；该产品无投影时为空 Optional
     */
    public Optional<Map<String, Object>> load(String productId) {
        if (sectionDir == null) {
            log.warn("[PC-SECTIONS] section-dir 未配置，受控失败: productId={}", productId);
            throw new ProductCenterSourceUnavailableException(
                    "gits.product-center.section-dir", "未配置（KERT 章节投影目录为空）");
        }
        if (!Files.isDirectory(sectionDir) || !Files.isReadable(sectionDir)) {
            log.error("[PC-SECTIONS] 章节投影目录不可达，受控失败: productId={} dir={}", productId, sectionDir);
            throw new ProductCenterSourceUnavailableException(
                    sectionDir.toString(), "KERT 章节投影目录不可达");
        }
        Path file = sectionDir.resolve(productId + ".json");
        if (!Files.isRegularFile(file)) {
            log.info("[PC-SECTIONS] 该产品无章节投影（前端须显示未接入）: productId={} path={}", productId, file);
            return Optional.empty();
        }
        try {
            Map<String, Object> doc = objectMapper.readValue(Files.readAllBytes(file), MAP_TYPE);
            log.info("[PC-SECTIONS] 章节投影加载成功: productId={} version={} 章节键={}",
                    productId, doc.get("versionId"), doc.keySet().size());
            return Optional.of(doc);
        } catch (Exception ex) {
            log.error("[PC-SECTIONS] 章节投影解析失败，受控失败: productId={} file={}", productId, file, ex);
            throw new ProductCenterSourceUnavailableException(
                    file.toString(), "KERT 章节投影不可解析");
        }
    }

    // ── 投影取值助手（**只做搬运与展示拼接，不生成内容**） ──────────────────────

    /** 取列表型章节；缺失 ⇒ 空列表（前端显示未接入）。 */
    @SuppressWarnings("unchecked")
    public static List<Object> list(Map<String, Object> doc, String key) {
        Object v = doc.get(key);
        return v instanceof List<?> l ? (List<Object>) l : List.of();
    }

    /** 取对象型章节（如 comparison）；缺失 ⇒ null。 */
    @SuppressWarnings("unchecked")
    public static Map<String, Object> map(Map<String, Object> doc, String key) {
        Object v = doc.get(key);
        return v instanceof Map<?, ?> m ? (Map<String, Object>) m : Map.of();
    }

    /**
     * 列表 → 展示用字符串（{@code ；} 连接）。
     *
     * <p>契约 {@code ProductCenterSummary.solves/isNot} 为 {@code String}，而投影中是 {@code List}；
     * 此处**仅做展示拼接**，不新增、不改写任何条目。</p>
     */
    public static String joinForDisplay(Object v) {
        if (v instanceof List<?> l) {
            StringBuilder sb = new StringBuilder();
            for (Object o : l) {
                if (o == null || String.valueOf(o).isBlank()) {
                    continue;
                }
                if (sb.length() > 0) {
                    sb.append("；");
                }
                sb.append(o);
            }
            return sb.length() == 0 ? null : sb.toString();
        }
        return v == null ? null : String.valueOf(v);
    }
}
