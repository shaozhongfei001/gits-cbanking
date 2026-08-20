package com.gien.gits.hermes.knowledge;

import com.gien.gits.ontology.port.ScenarioDataProvider;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 模拟访问知识的数据提供者（scenario 影子/演示层）。
 *
 * <p>读取按《银行知识工程规范打样_fixed.xlsx》标准组织的演示知识资产
 * （{@code 05_knowledge/demo/}）{, 复现生产 P23 {@code KnowledgeAssembler} 的
 * "先读知识地图 → 按地图任务装配知识条目(KI→KE→RUL)" 语义，返回与生产同构的
 * {@link KnowledgeAssemblyResult}。生产使用受控 {@code specs/knowledge-architecture}，
 * 本提供者使用 {@code scenario/seed} 影子演示资产，供演示与影子环境。</p>
 */
public class SimulatedKnowledgeProvider {

    /** 演示知识资产根目录（相对 scenario seed root）。 */
    public static final String DEMO_ASSET_ROOT = "05_knowledge/demo";

    /** 激活合同路径（scope→task→KI 映射，JSON）。 */
    public static final String ACTIVATION_CONTRACT = DEMO_ASSET_ROOT + "/activation-contract.json";

    /** 知识地图路径（YAML）。 */
    public static final String KNOWLEDGE_MAP = DEMO_ASSET_ROOT + "/knowledge-map.yaml";

    /** 规则库路径（YAML）。 */
    public static final String RULES_FILE = DEMO_ASSET_ROOT + "/rules.yaml";

    /** 知识条目索引路径（YAML）。 */
    public static final String ELEMENTS_INDEX = DEMO_ASSET_ROOT + "/elements/_index.yaml";

    private final ScenarioDataProvider dataProvider;

    public SimulatedKnowledgeProvider(ScenarioDataProvider dataProvider) {
        this.dataProvider = Objects.requireNonNull(dataProvider, "dataProvider");
    }

    /**
     * 执行"先读图 → 按激活合同任务装配知识条目"，输出与 P23 同构的知识上下文。
     *
     * @param scope          知识地图（如 KM-CORP-RM-PREVISIT-DEMO）
     * @param businessContext 注入的业务上下文（客户/事件事实等）
     */
    public KnowledgeAssemblyResult assemble(String scope, String businessContext) {
        Objects.requireNonNull(scope, "scope");
        String context = businessContext == null ? "" : businessContext;

        List<String> kiIds = resolveKnowledgeItemIds();
        List<RuleRef> rules = readRules();
        List<String> sources = new ArrayList<>();
        List<AssemblyTraceStep> trace = new ArrayList<>();

        StringBuilder sb = new StringBuilder();
        sb.append("# 知识上下文：").append(scope).append("\n\n");

        if (!kiIds.isEmpty()) {
            sb.append("## 装配的知识条目\n\n");
            for (String kiId : kiIds) {
                trace.add(new AssemblyTraceStep(kiId, "READ_MAP", null, null, "OK",
                        "进入知识条目 " + kiId));
                appendKnowledgeItem(sb, kiId, sources, trace);
                appendBindingData(sb, kiId, sources, trace);
                trace.add(AssemblyTraceStep.done(kiId, "知识条目装配完成"));
            }
        }

        if (!rules.isEmpty()) {
            sb.append("## 规则约束\n\n");
            for (RuleRef rule : rules) {
                sb.append("- ").append(rule.display()).append('\n');
            }
        }

        if (!context.isBlank()) {
            sb.append("\n## 业务上下文\n\n").append(context).append('\n');
        }

        List<String> ruleIds = rules.stream().map(RuleRef::ruleId).toList();
        return new KnowledgeAssemblyResult(scope, kiIds, sb.toString(), ruleIds,
                List.copyOf(sources), List.copyOf(trace));
    }

    /** 从知识地图 knowledgeItemBindings / 索引 assetBinding 解析 KI→数据文件路径。 */
    private String bindingDataPath(String kiId) {
        String map = dataProvider.readText(KNOWLEDGE_MAP).orElse("");
        String idx = dataProvider.readText(ELEMENTS_INDEX).orElse("");
        for (String text : new String[]{idx, map}) {
            // 匹配 knowledgeItemId <kiId> 之后 <=300 字符内的 dataPath（兼容 YAML 缩进与引号）
            String pattern = "(?:knowledgeItemId|ki(?:I|i)d)\\s*[:=]\\s*[\"']?"
                    + java.util.regex.Pattern.quote(kiId)
                    + "[\"']?[\\s\\S]{0,300}?dataPath\\s*[:=]\\s*[\"']?([^\"',}\\s]+)";
            java.util.regex.Matcher m = java.util.regex.Pattern.compile(pattern).matcher(text);
            if (m.find()) {
                return m.group(1);
            }
        }
        return "";
    }

    /** 按 assetBinding 读取数据文件（如供应链图谱），把真实数据装配进上下文并记录轨迹。 */
    private void appendBindingData(StringBuilder sb, String kiId, List<String> sources,
                                   List<AssemblyTraceStep> trace) {
        String dataPath = bindingDataPath(kiId);
        if (dataPath.isBlank()) {
            trace.add(AssemblyTraceStep.skip(kiId, "无 assetBinding 数据映射，未取数"));
            return;
        }
        String full = DEMO_ASSET_ROOT + "/" + dataPath;
        trace.add(new AssemblyTraceStep(kiId, "RESOLVE_BINDING", null, dataPath, "OK",
                "解析数据绑定: " + dataPath));
        String text = dataProvider.readText(full).orElse(null);
        if (text == null || text.isBlank()) {
            trace.add(new AssemblyTraceStep(kiId, "LOAD_DATA", null, dataPath, "EMPTY",
                    "数据文件为空或不存在"));
            return;
        }
        sources.add(full);
        sb.append("\n### ").append(kiId).append(" · 数据资产\n\n");
        if (kiId.startsWith("KI-FRONT-001")) {
            sb.append(renderSupplyChain(text)).append('\n');
        } else {
            sb.append(text.lines().limit(8)
                    .map(l -> "- " + l)
                    .reduce((a, b) -> a + "\n" + b).orElse(""));
            sb.append('\n');
        }
        trace.add(AssemblyTraceStep.load(kiId, dataAssetOf(kiId), dataPath,
                "取数成功: " + full));
    }

    /** 渲染供应链图谱为人类可读陈述（上游/中游/下游 + 采购占比 + 付款偏好）。 */
    private String renderSupplyChain(String yaml) {
        StringBuilder out = new StringBuilder();
        out.append("### 上游供应商\n\n");
        appendSuppliers(out, yaml, "upstream_suppliers");
        out.append("\n### 中游集成商\n\n");
        appendSuppliers(out, yaml, "midstream_integrators");
        out.append("\n### 下游客户\n\n");
        appendSuppliers(out, yaml, "downstream_customers");
        return out.toString();
    }

    private void appendSuppliers(StringBuilder out, String yaml, String section) {
        boolean inSection = false;
        boolean first = true;
        String name = "", category = "", purchase = "", pct = "", trend = "", pref = "";
        for (String line : yaml.lines().toList()) {
            String t = line.trim();
            if (t.startsWith(section + ":")) {
                inSection = true;
                continue;
            }
            if (inSection && line.trim().isBlank()) {
                continue;
            }
            if (inSection && t.startsWith("- ")) {
                if (!first) {
                    emitSupplier(out, name, category, purchase, pct, trend, pref);
                }
                first = false;
                name = category = purchase = pct = trend = pref = "";
                continue;
            }
            if (inSection) {
                if (t.startsWith("name:") || t.startsWith("integrator_name:")
                        || t.startsWith("customer_id:")) {
                    name = val(t);
                } else if (t.startsWith("category:") || t.startsWith("service:")) {
                    category = val(t);
                } else if (t.startsWith("last12m_purchase_cny_wan:") || t.startsWith("contract_value_cny_wan:")) {
                    purchase = val(t);
                } else if (t.startsWith("pct_of_annual_purchase:")) {
                    pct = val(t);
                } else if (t.startsWith("price_trend:")) {
                    trend = val(t);
                } else if (t.startsWith("payment_preference:")) {
                    pref = val(t);
                }
            }
        }
        if (inSection && !first && !name.isBlank()) {
            emitSupplier(out, name, category, purchase, pct, trend, pref);
        }
    }

    private void emitSupplier(StringBuilder out, String name, String category, String purchase,
                              String pct, String trend, String pref) {
        StringBuilder line = new StringBuilder("- ");
        line.append(name);
        if (!category.isBlank()) {
            line.append("（").append(category).append('）');
        }
        if (!purchase.isBlank()) {
            line.append(" 近12月采购 ").append(purchase).append(" 万");
        }
        if (!pct.isBlank()) {
            line.append(" / 占比 ").append(pct).append('%');
        }
        if (!trend.isBlank()) {
            line.append(" / 价格").append(trend);
        }
        if (!pref.isBlank()) {
            line.append(" / 付款工具:").append(pref);
        }
        out.append(line).append('\n');
    }

    private String val(String line) {
        int c = line.indexOf(':');
        return c < 0 ? "" : line.substring(c + 1).trim().replaceAll("[\"']", "");
    }

    private String dataAssetOf(String kiId) {
        return "ASSET-KNOW-" + kiId + "-DEMO";
    }

    /** 从激活合同解析需装配的 knowledgeItemIds。 */
    public List<String> resolveKnowledgeItemIds() {
        String contract = dataProvider.readText(ACTIVATION_CONTRACT).orElse("");
        return parseKnowledgeItemIds(contract);
    }

    /** 从激活合同文本中提取 knowledgeItemIds 数组。 */
    private List<String> parseKnowledgeItemIds(String contract) {
        java.util.regex.Matcher m = java.util.regex.Pattern
                .compile("\"knowledgeItemIds\"\\s*:\\s*(\\[[^\\]]*\\])")
                .matcher(contract);
        if (!m.find()) {
            return List.of();
        }
        return parseStringArray(m.group(1));
    }

    /** 读取规则库引用（ruleId 与名称配对）。 */
    public List<RuleRef> readRules() {
        List<RuleRef> rules = new ArrayList<>();
        String currentId = null;
        for (String line : dataProvider.readLines(RULES_FILE)) {
            String trimmed = line.trim().replaceFirst("^-\\s*", "");
            if (trimmed.startsWith("ruleId:")) {
                currentId = trimmed.substring("ruleId:".length()).trim().replaceAll("[\"']", "");
            } else if (trimmed.startsWith("name:") && currentId != null) {
                String name = trimmed.substring("name:".length()).trim().replaceAll("[\"']", "");
                rules.add(new RuleRef(currentId, name));
                currentId = null;
            }
        }
        return List.copyOf(rules);
    }

    /** 规则引用（ruleId + 名称）。 */
    public record RuleRef(String ruleId, String name) {
        public String display() {
            return name.isBlank() ? ruleId : ruleId + " (" + name + ")";
        }
    }

    private void appendKnowledgeItem(StringBuilder sb, String kiId, List<String> sources,
                                 List<AssemblyTraceStep> trace) {
        sb.append("### ").append(kiId).append('\n');
        String dir = DEMO_ASSET_ROOT + "/elements/" + kiId;
        List<String> files = dataProvider.listFiles(dir);
        if (files.isEmpty()) {
            sb.append("- （无演示要素）\n");
            trace.add(AssemblyTraceStep.skip(kiId, "演示要素目录为空"));
            return;
        }
        for (String file : files) {
            if (!file.endsWith(".md")) {
                continue;
            }
            String path = dir + "/" + file;
            dataProvider.readText(path).ifPresent(text -> {
                Map<String, String> fm = parseFrontmatter(text);
                String elementId = fm.getOrDefault("elementId", file);
                String name = fm.getOrDefault("name", elementId);
                String content = fm.getOrDefault("content", "");
                sources.add(path);
                sb.append("- **").append(name).append("** (").append(elementId).append("): ")
                        .append(content).append('\n');
            });
        }
    }

    /** 解析 markdown 头部 JSON frontmatter（--- {...} --- 首块）。 */
    private Map<String, String> parseFrontmatter(String text) {
        String start = "json:";
        int open = text.indexOf('{');
        int close = text.indexOf('}', open + 1);
        if (open < 0 || close <= open) {
            return Map.of();
        }
        return parseJsonFields(text.substring(open, close + 1));
    }

    /** 解析单行 JSON object 的顶层字符串字段。 */
    private Map<String, String> parseJsonFields(String json) {
        Map<String, String> result = new LinkedHashMap<>();
        int i = 0;
        int n = json.length();
        while (i < n) {
            if (json.charAt(i) == '"') {
                int keyStart = i + 1;
                int keyEnd = json.indexOf('"', keyStart);
                if (keyEnd < 0) {
                    break;
                }
                String key = json.substring(keyStart, keyEnd);
                int colon = json.indexOf(':', keyEnd);
                if (colon < 0) {
                    i = keyEnd + 1;
                    continue;
                }
                int valueStart = json.indexOf('"', colon + 1);
                if (valueStart < 0) {
                    i = colon + 1;
                    continue;
                }
                int valueEnd = findUnescapedQuote(json, valueStart + 1);
                String value = decodeJson(json.substring(valueStart + 1, valueEnd));
                result.put(key, value);
                i = valueEnd + 1;
            } else {
                i++;
            }
        }
        return result;
    }

    /** 读取 JSON 文本并按顶层字段解析。 */
    private Map<String, String> readJsonText(String path) {
        return dataProvider.readText(path).map(this::parseJsonFields).orElseGet(Map::of);
    }

    /** 解析 JSON 字符串数组 ["a","b"]。 */
    private List<String> parseStringArray(String text) {
        if (text == null || !text.startsWith("[")) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        int from = 0;
        while (true) {
            int qs = text.indexOf('"', from);
            if (qs < 0) {
                break;
            }
            int qe = findUnescapedQuote(text, qs + 1);
            out.add(decodeJson(text.substring(qs + 1, qe)));
            from = qe + 1;
        }
        return List.copyOf(out);
    }

    private int findUnescapedQuote(String s, int from) {
        int i = from;
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == '\\') {
                i += 2;
                continue;
            }
            if (c == '"') {
                return i;
            }
            i++;
        }
        return s.length();
    }

    private String decodeJson(String raw) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < raw.length()) {
            char c = raw.charAt(i);
            if (c == '\\' && i + 1 < raw.length()) {
                char n = raw.charAt(i + 1);
                switch (n) {
                    case 'n' -> sb.append('\n');
                    case 't' -> sb.append('\t');
                    case 'r' -> sb.append('\r');
                    case '"', '\\', '/' -> sb.append(n);
                    case 'u' -> {
                        if (i + 5 < raw.length()) {
                            sb.append((char) Integer.parseInt(raw.substring(i + 2, i + 6), 16));
                            i += 5;
                        }
                    }
                    default -> sb.append(n);
                }
                i += 2;
            } else {
                sb.append(c);
                i++;
            }
        }
        return sb.toString();
    }
}