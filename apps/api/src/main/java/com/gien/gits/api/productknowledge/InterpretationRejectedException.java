package com.gien.gits.api.productknowledge;

import org.springframework.http.HttpStatus;

/**
 * 解读请求被门禁拒绝（404 / 409 / 422 / 400），携带合同定义的错误码。
 */
public class InterpretationRejectedException extends RuntimeException {

    private final HttpStatus status;
    private final String code;

    public InterpretationRejectedException(HttpStatus status, String code, String message) {
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
