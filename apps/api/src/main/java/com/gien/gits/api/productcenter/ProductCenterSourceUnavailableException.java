package com.gien.gits.api.productcenter;

/**
 * 产品知识源不可达 / 不可解析（fail-closed）。
 *
 * <p>对应 CTR-PKC-API-001 的 {@code SOURCES_UNAVAILABLE}：分类骨架或产品卡源
 * 不可读时，产品中心必须显式失败，<b>不得</b>本地兜底生成产品目录或结论。</p>
 */
public class ProductCenterSourceUnavailableException extends RuntimeException {

    private final String source;

    public ProductCenterSourceUnavailableException(String source, String reason) {
        super("产品中心知识源不可用: " + source + " (" + reason + ")");
        this.source = source;
    }

    public String source() {
        return source;
    }
}
