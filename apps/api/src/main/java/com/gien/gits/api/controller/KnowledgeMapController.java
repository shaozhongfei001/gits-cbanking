package com.gien.gits.api.controller;

import com.gien.gits.knowledge.KnowledgeElement;
import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 知识控制面只读控制器（P22/P23，仓库内 KI/KE 快照）。
 *
 * <p>本控制器不是 P38 客户经营「知识卡与产品适用边界」页的数据源。
 * P38 必须走 {@code GET /api/v1/engagement/customer/{id}/knowledge-map}（DKWS Skill）。
 * 全部为只读 GET：不修改任何知识、不改变权威源（{@code specs/}），fail-closed（未知 ID 返回空）。
 * 返回集合一律为空数组而非 {@code null}。</p>
 */
@RestController
@RequestMapping("/api/v1/knowledge")
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
        name = "gits.knowledge.enabled",
        havingValue = "true",
        matchIfMissing = true)
public class KnowledgeMapController {

    private final KnowledgeElementPort elementPort;
    private final KnowledgeMapPort mapPort;

    public KnowledgeMapController(KnowledgeElementPort elementPort, KnowledgeMapPort mapPort) {
        this.elementPort = elementPort;
        this.mapPort = mapPort;
    }

    /**
     * 全部知识要素（扁平），前端可按 knowledgeItemId 分组渲染 KI→KE 树。
     */
    @GetMapping("/elements")
    public List<KnowledgeElement> allElements() {
        return elementPort.listAll();
    }

    /**
     * 指定知识条目（KI）下的全部知识要素。
     */
    @GetMapping("/items/{knowledgeItemId}")
    public List<KnowledgeElement> byKnowledgeItem(@PathVariable String knowledgeItemId) {
        return elementPort.listByKnowledgeItem(knowledgeItemId);
    }

    /**
     * 知识地图导航：按 KI 分组的要素映射（keyed by knowledgeItemId）。
     */
    @GetMapping("/map")
    public Map<String, List<KnowledgeElement>> map() {
        Map<String, List<KnowledgeElement>> byKi = new LinkedHashMap<>();
        List<KnowledgeElement> elements = elementPort.listAll();
        for (KnowledgeElement element : elements) {
            byKi.computeIfAbsent(element.knowledgeItemId(), k -> new java.util.ArrayList<>()).add(element);
        }
        // 保持 KI → KE 的确定性顺序
        byKi.replaceAll((k, v) -> v.stream()
                .sorted(Comparator.comparing(KnowledgeElement::elementId))
                .toList());
        return byKi;
    }

    /**
     * 知识条目（KI）清单及各自要素数量（供前端展示条目元数据）。
     */
    @GetMapping("/items")
    public List<Map<String, Object>> items() {
        Map<String, List<KnowledgeElement>> byKi = map();
        return byKi.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .map(entry -> {
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("knowledgeItemId", entry.getKey());
                    item.put("elementCount", entry.getValue().size());
                    item.put("firstElementName", entry.getValue().isEmpty()
                            ? "" : entry.getValue().get(0).name());
                    return item;
                })
                .toList();
    }
}
