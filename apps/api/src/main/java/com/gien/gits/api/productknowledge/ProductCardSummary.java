package com.gien.gits.api.productknowledge;

import java.util.List;

/**
 * 产品卡摘要（产品全景列表项）。
 *
 * <p>来源为 KERT 侧 {@code 03_core/*&#47;product-cards/PROD-*.md} 产品卡文件，
 * 仅承载人类可读的元数据与摘要，不承载制度结论（制度结论由解读投影承载）。</p>
 *
 * @param productId     产品ID
 * @param name          产品名称
 * @param family        产品族代码
 * @param familyName    产品族中文名
 * @param summary       产品摘要（「产品概览与客户价值」正文）
 * @param capabilities  产品能力
 * @param scenarios     适用场景
 * @param riskNotes     风险提示
 * @param sourceFile    原始产品卡文件路径（相对 KERT 资产包根）
 */
public record ProductCardSummary(
        String productId,
        String name,
        String family,
        String familyName,
        String summary,
        List<String> capabilities,
        List<String> scenarios,
        List<String> riskNotes,
        String sourceFile) {
}
