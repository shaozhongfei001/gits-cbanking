package com.gien.gits.api.controller;

import static org.junit.jupiter.api.Assertions.*;

import java.util.NoSuchElementException;

import com.gien.gits.api.dto.ErrorResponse;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.mock.http.MockHttpInputMessage;
import org.springframework.web.bind.MissingServletRequestParameterException;

class GlobalExceptionHandlerTest {

    private GlobalExceptionHandler handler;

    @BeforeEach
    void setUp() {
        handler = new GlobalExceptionHandler();
    }

    @Test
    void illegalArgument_returns400WithCode() {
        ResponseEntity<ErrorResponse> resp =
                handler.handleIllegalArgument(new IllegalArgumentException("bad"));
        assertEquals(HttpStatus.BAD_REQUEST, resp.getStatusCode());
        ErrorResponse body = resp.getBody();
        assertEquals("INVALID_ARGUMENT", body.errorCode());
        assertEquals("bad", body.message());
        assertNotNull(body.timestamp());
    }

    @Test
    void illegalArgument_nullMessage_fallsBack() {
        ResponseEntity<ErrorResponse> resp = handler.handleIllegalArgument(new IllegalArgumentException());
        assertEquals("Invalid argument", resp.getBody().message());
    }

    @Test
    void illegalState_returns409WithCode() {
        ResponseEntity<ErrorResponse> resp =
                handler.handleIllegalState(new IllegalStateException("conflict"));
        assertEquals(HttpStatus.CONFLICT, resp.getStatusCode());
        assertEquals("STATE_CONFLICT", resp.getBody().errorCode());
    }

    @Test
    void notFound_returns404() {
        ResponseEntity<ErrorResponse> resp =
                handler.handleNotFound(new NoSuchElementException("missing"));
        assertEquals(HttpStatus.NOT_FOUND, resp.getStatusCode());
        assertEquals("NOT_FOUND", resp.getBody().errorCode());
    }

    @Test
    void missingParam_returns400() throws Exception {
        ResponseEntity<ErrorResponse> resp = handler.handleMissingParam(
                new MissingServletRequestParameterException("customerId", "string"));
        assertEquals(HttpStatus.BAD_REQUEST, resp.getStatusCode());
        assertEquals("INVALID_ARGUMENT", resp.getBody().errorCode());
        assertNotNull(resp.getBody().message());
    }

    @Test
    void notReadable_returns400() {
        HttpMessageNotReadableException ex =
                new HttpMessageNotReadableException("bad body", new MockHttpInputMessage(new byte[0]));
        ResponseEntity<ErrorResponse> resp = handler.handleNotReadable(ex);
        assertEquals(HttpStatus.BAD_REQUEST, resp.getStatusCode());
        assertEquals("INVALID_ARGUMENT", resp.getBody().errorCode());
    }

    @Test
    void general_returns500() {
        ResponseEntity<ErrorResponse> resp = handler.handleGeneral(new RuntimeException("boom"));
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, resp.getStatusCode());
        assertEquals("INTERNAL_ERROR", resp.getBody().errorCode());
        assertEquals("boom", resp.getBody().message());
    }
}