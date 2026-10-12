package com.gien.gits.api.productknowledge;

/**
 * KERT 知识源不可达 / 投影不可解析。
 *
 * <p>按红线必须受控失败：绝不退化为本地种子或模型生成的产品结论。</p>
 */
public class KnowledgeSourceUnavailableException extends RuntimeException {

    public KnowledgeSourceUnavailableException(String message) {
        super(message);
    }
}
