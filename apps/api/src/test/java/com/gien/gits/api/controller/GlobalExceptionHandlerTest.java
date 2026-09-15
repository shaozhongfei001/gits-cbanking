package com.gien.gits.api.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import com.gien.gits.api.dto.ErrorResponse;

import static org.junit.jupiter.api.Assertions.*;

/**
 * P17: GlobalExceptionHandler单元测试
 */
class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

    @Test
    @DisplayName("IllegalArgumentException返回400")
    void handleIllegalArgument_returnsBadRequest() {
        ResponseEntity<ErrorResponse> response = handler.handleIllegalArgument(new IllegalArgumentException("bad input"));
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("INVALID_ARGUMENT", response.getBody().errorCode());
        assertEquals("bad input", response.getBody().message());
    }

    @Test
    @DisplayName("IllegalArgumentException空消息使用默认值")
    void handleIllegalArgument_nullMessage_usesDefault() {
        ResponseEntity<ErrorResponse> response = handler.handleIllegalArgument(new IllegalArgumentException());
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("Invalid argument", response.getBody().message());
    }

    @Test
    @DisplayName("IllegalStateException返回409")
    void handleIllegalState_returnsConflict() {
        ResponseEntity<ErrorResponse> response = handler.handleIllegalState(new IllegalStateException("conflict"));
        assertEquals(HttpStatus.CONFLICT, response.getStatusCode());
        assertEquals("STATE_CONFLICT", response.getBody().errorCode());
        assertEquals("conflict", response.getBody().message());
    }

    @Test
    @DisplayName("NoSuchElementException返回404")
    void handleNotFound_returnsNotFound() {
        ResponseEntity<ErrorResponse> response = handler.handleNotFound(new java.util.NoSuchElementException("not here"));
        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        assertEquals("NOT_FOUND", response.getBody().errorCode());
    }

    @Test
    @DisplayName("通用Exception返回500，消息为异常信息")
    void handleGeneral_returnsInternalServerError() {
        ResponseEntity<ErrorResponse> response = handler.handleGeneral(new RuntimeException("oops"));
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
        assertEquals("INTERNAL_ERROR", response.getBody().errorCode());
        assertEquals("oops", response.getBody().message());
    }

    @Test
    @DisplayName("NoResourceFoundException返回404而不是500")
    void handleNoResource_returnsNotFound() {
        ResponseEntity<ErrorResponse> response = handler.handleNoResource(
                new NoResourceFoundException(HttpMethod.GET, "/api/v1/interactions"));
        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        assertEquals("NOT_FOUND", response.getBody().errorCode());
    }
}
