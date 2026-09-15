package com.gien.gits.ontology.port;

import com.gien.gits.ontology.Interaction;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * 交互仓储端口 — 只读操作。
 *
 * <p>定义对 {@link Interaction} 聚合的查询契约，由适配器层实现。
 * 写操作见 {@link WritableInteractionRepository}。</p>
 */
public interface InteractionRepository {

    /**
     * 根据交互ID查找交互。
     *
     * @param interactionId 交互唯一标识
     * @return 找到的交互，若不存在则返回空
     */
    Optional<Interaction> findById(UUID interactionId);

    /**
     * 根据运营案例ID查找其关联的所有交互。
     *
     * @param caseId 运营案例唯一标识
     * @return 关联的交互列表
     */
    List<Interaction> findByCaseId(UUID caseId);

    /**
     * 根据客户旅程ID查找其关联的所有交互。
     *
     * @param journeyId 旅程唯一标识
     * @return 关联的交互列表
     */
    List<Interaction> findByJourneyId(UUID journeyId);

    /**
     * 列出全部交互，按发生时间倒序。
     *
     * <p>无记录时返回空列表，不得抛出。</p>
     *
     * @return 交互列表，可能为空
     */
    List<Interaction> findAll();
}
