package com.gien.gits.api.productknowledge;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 读取 KERT 产品卡目录（{@code 03_core/*&#47;product-cards/PROD-*.md}）的目录服务。
 *
 * <p>产品卡文件是产品原始材料的权威来源，本服务仅做只读解析与呈现，
 * 不生成、不改写任何制度结论。卡片目录未配置或不可读时返回空列表（非受控失败，
 * 产品解读投影的受控失败语义由 {@link KertReleaseSnapshotAdapter} 单独负责）。</p>
 */
@Component
public class ProductCardCatalogService {

    private static final Logger log = LoggerFactory.getLogger(ProductCardCatalogService.class);

    private final Path cardDir;
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

    public ProductCardCatalogService(
            @Value("${gits.product-knowledge.card-dir:}") String cardDir) {
        this.cardDir = cardDir == null || cardDir.isBlank() ? null : Path.of(cardDir);
    }

    /** 产品卡根目录（03_core）。未配置时返回 null。 */
    public boolean isConfigured() {
        return cardDir != null && Files.isDirectory(cardDir) && Files.isReadable(cardDir);
    }

    /** 扫描全部产品卡文件，返回按产品族/产品ID排序的摘要列表。 */
    public List<ProductCardSummary> listSummaries() {
        if (!isConfigured()) {
            log.warn("[PK-CATALOG] card-dir 未配置或不可读，返回空列表");
            return List.of();
        }
        List<CardFile> files = scanCardFiles();
        return files.stream()
                .map(this::toSummary)
                .filter(Optional::isPresent)
                .map(Optional::get)
                .sorted(Comparator.comparing(ProductCardSummary::familyName)
                        .thenComparing(ProductCardSummary::productId))
                .toList();
    }

    /** 按产品ID读取单个产品卡详情（含全文）。 */
    public Optional<ProductCardDetail> loadDetail(String productId) {
        if (!isConfigured() || productId == null || productId.isBlank()) {
            return Optional.empty();
        }
        return scanCardFiles().stream()
                .filter(f -> productId.equals(f.productId()))
                .findFirst()
                .flatMap(this::toDetail);
    }

    /** 单个产品卡是否具备解读投影（由 KertReleaseSnapshotAdapter 判定）。 */
    private boolean isInterpretable(String productId) {
        // 仅现金池 PROD-CM-001 具备已发布 Release；其余产品卡的解读投影待 KERT 侧发布。
        return "PROD-CM-001".equals(productId);
    }

    private Optional<ProductCardSummary> toSummary(CardFile f) {
        try {
            CardMeta meta = parse(f);
            return Optional.of(new ProductCardSummary(
                    f.productId(), meta.name(), meta.family(), meta.familyName(),
                    meta.summary(), meta.capabilities(), meta.scenarios(), meta.riskNotes(),
                    f.relativePath(), isInterpretable(f.productId())));
        } catch (Exception ex) {
            log.warn("[PK-CATALOG] 产品卡解析失败，跳过: {} ({})", f.path(), ex.getMessage());
            return Optional.empty();
        }
    }

    private Optional<ProductCardDetail> toDetail(CardFile f) {
        try {
            CardMeta meta = parse(f);
            String raw = Files.readString(f.path());
            return Optional.of(new ProductCardDetail(
                    f.productId(), meta.name(), meta.family(), meta.familyName(),
                    meta.owner(), meta.summary(), parseSections(raw),
                    f.relativePath(), raw, isInterpretable(f.productId())));
        } catch (Exception ex) {
            log.warn("[PK-CATALOG] 产品卡详情解析失败: {} ({})", f.path(), ex.getMessage());
            return Optional.empty();
        }
    }

    /** 解析产品卡 front matter + 摘要 + 关键字段。 */
    private CardMeta parse(CardFile f) throws IOException {
        String raw = Files.readString(f.path());
        String[] parts = raw.split("---", 3);
        JsonNode fm = parts.length >= 3 ? yamlMapper.readTree(parts[1]) : yamlMapper.createObjectNode();
        String body = parts.length >= 3 ? parts[2] : raw;

        String name = text(fm, "name", f.productId());
        String family = text(fm, "product_family", "");
        String familyName = text(fm, "product_family_name", family);
        String owner = text(fm, "owner", "");
        List<String> capabilities = textList(fm.get("capabilities"));
        List<String> scenarios = textList(fm.get("applicable_scenarios"));
        List<String> riskNotes = textList(fm.get("risk_notes"));
        String summary = extractSummary(body);
        return new CardMeta(name, family, familyName, owner, summary,
                capabilities, scenarios, riskNotes);
    }

    /** 提取「产品概览与客户价值」节作为摘要；缺失时取正文首段。 */
    private String extractSummary(String body) {
        String[] lines = body.split("\\R");
        StringBuilder summary = new StringBuilder();
        boolean inOverview = false;
        for (String line : lines) {
            String t = line.trim();
            if (t.matches("^#+\\s*.*")) {
                if (t.contains("产品概览")) {
                    inOverview = true;
                    continue;
                } else if (inOverview) {
                    break; // 进入下一个章节，停止
                }
                continue;
            }
            if (inOverview && !t.isEmpty() && !t.startsWith(">")) {
                summary.append(t).append('\n');
            }
        }
        String result = summary.toString().trim();
        if (result.isEmpty()) {
            // 兜底：取正文第一个非空、非标题、非引用段落
            for (String line : lines) {
                String t = line.trim();
                if (!t.isEmpty() && !t.startsWith("#") && !t.startsWith(">") && !t.startsWith("-")) {
                    result = t;
                    break;
                }
            }
        }
        return result;
    }

    /** 解析正文各章节（## 标题 + 内容），供分段「深度解读」。跳过 H1 与引用块。 */
    private List<ProductCardDetail.CardSection> parseSections(String raw) {
        String[] parts = raw.split("---", 3);
        String body = parts.length >= 3 ? parts[2] : raw;
        List<ProductCardDetail.CardSection> sections = new ArrayList<>();
        String[] lines = body.split("\\R");
        String currentTitle = null;
        StringBuilder currentContent = new StringBuilder();
        for (String line : lines) {
            String t = line.trim();
            if (t.matches("^##\\s+.*")) {
                // 仅 ## 作为章节标题；# H1 跳过（是产品卡文件名标题）
                if (currentTitle != null && currentContent.length() > 0) {
                    sections.add(new ProductCardDetail.CardSection(currentTitle, currentContent.toString().trim()));
                }
                currentTitle = t.replaceFirst("^##\\s+", "");
                currentContent = new StringBuilder();
            } else if (t.matches("^#\\s+.*")) {
                // H1 忽略
                continue;
            } else if (currentTitle != null && !t.isEmpty() && !t.startsWith(">")) {
                currentContent.append(line).append('\n');
            }
        }
        if (currentTitle != null && currentContent.length() > 0) {
            sections.add(new ProductCardDetail.CardSection(currentTitle, currentContent.toString().trim()));
        }
        return sections;
    }

    private List<CardFile> scanCardFiles() {
        List<CardFile> files = new ArrayList<>();
        try (Stream<Path> stream = Files.walk(cardDir)) {
            stream.filter(p -> p.getFileName() != null
                            && p.getFileName().toString().startsWith("PROD-")
                            && p.getFileName().toString().endsWith(".md"))
                    .forEach(p -> {
                        String productId = p.getFileName().toString().replace(".md", "");
                        files.add(new CardFile(productId, p, cardDir.relativize(p).toString()));
                    });
        } catch (IOException ex) {
            log.error("[PK-CATALOG] 扫描产品卡目录失败: {}", cardDir, ex);
        }
        return files;
    }

    private static String text(JsonNode fm, String key, String def) {
        JsonNode n = fm.get(key);
        return n != null && n.isTextual() ? n.asText() : def;
    }

    private static List<String> textList(JsonNode n) {
        if (n == null || !n.isArray()) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        n.forEach(e -> out.add(e.asText()));
        return out;
    }

    private record CardFile(String productId, Path path, String relativePath) {
    }

    private record CardMeta(String name, String family, String familyName, String owner,
                            String summary, List<String> capabilities, List<String> scenarios,
                            List<String> riskNotes) {
    }
}
