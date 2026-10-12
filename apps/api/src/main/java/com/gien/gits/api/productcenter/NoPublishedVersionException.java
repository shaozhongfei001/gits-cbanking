package com.gien.gits.api.productcenter;

/**
 * 产品已登记但不存在可呈现的知识内容（CTR-PKC-API-001 · {@code NO_PUBLISHED_VERSION}）。
 *
 * <p>语义与 {@code PRODUCT_NOT_FOUND} 严格区分：产品确实存在于受控分类法中，
 * 只是尚无产品卡/受控知识版本可供呈现 —— 页面必须给出「暂无有效版本」与责任人入口，
 * 不得展示草稿或示意内容（AT-009）。</p>
 */
public class NoPublishedVersionException extends RuntimeException {

    public NoPublishedVersionException(String productId, String reason) {
        super("产品无有效发布版本: " + productId + " (" + reason + ")");
    }
}
