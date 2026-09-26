package com.gien.gits.api.productknowledge;

import org.springframework.http.HttpStatus;

/**
 * LightRAG / KERT 上游检索失败（502 / 504）。绝不降级为本地结果（fail-closed）。
 */
public class RetrievalUpstreamException extends RuntimeException {

    private final HttpStatus status;
    private final String code;

    public RetrievalUpstreamException(HttpStatus status, String code, String message) {
        super(message);
        this.status = status;
        this.code = code;
    }

    public HttpStatus status() {
        return status;
    }

    public String code() {
        return code;
    }
}
