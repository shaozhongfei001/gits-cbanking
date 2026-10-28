package com.gien.gits.api.productknowledge;

import java.util.List;

/**
 * 产品卡详情（含原始产品文档全文，供「深度解读」与「原始材料」展示）。
 *
 * @param productId     产品ID
 * @param name          产品名称
 * @param family        产品族代码
 * @param familyName    产品族中文名
 * @param owner         产品 owner
 * @param summary       产品摘要（「产品概览与客户价值」正文）
 * @param sections      产品卡正文各章节（标题 + 内容），供分段「深度解读」展示
 * @param sourceFile    原始产品卡文件路径
 * @param rawMarkdown   原始产品卡全文（Markdown）
 */
public record ProductCardDetail(
        String productId,
        String name,
        String family,
        String familyName,
        String owner,
        String summary,
        List<CardSection> sections,
        String sourceFile,
        String rawMarkdown) {

    /** 产品卡正文章节。 */
    public record CardSection(String title, String content) {
    }
}
