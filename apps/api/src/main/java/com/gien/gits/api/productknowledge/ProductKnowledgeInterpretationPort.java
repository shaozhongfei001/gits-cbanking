package com.gien.gits.api.productknowledge;

import java.util.Optional;

/**
 * 产品解读投影端口（GITS 侧只读消费 KERT 已发布 Release）。
 *
 * <p>GITS 不得成为第二套产品规则系统：本端口只返回 KERT 侧投影的只读快照，
 * 不提供任何写操作，也不得在本地生成产品结论。KERT 不可达时实现必须
 * 抛出 {@link KnowledgeSourceUnavailableException}，由上层转为 503 受控失败。</p>
 */
public interface ProductKnowledgeInterpretationPort {

    /**
     * 加载指定产品的解读投影。
     *
     * @param productId 产品 ID（{@code PROD-XX-NNN}）
     * @return 投影；未找到返回空
     */
    Optional<InterpretationProjection> load(String productId);
}
