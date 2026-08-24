package com.gien.gits.api.security;

import com.gien.gits.action.port.AuditLogPort;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.core.context.SecurityContextHolder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ApiKeyAuthenticationFilterTest {

    @Mock
    private HttpServletRequest request;

    @Mock
    private HttpServletResponse response;

    @Mock
    private FilterChain filterChain;

    @Mock
    private AuditLogPort auditLog;

    @BeforeEach
    void clearContext() {
        SecurityContextHolder.clearContext();
    }

    private ApiKeyAuthenticationFilter createFilter(String apiKey) {
        return new ApiKeyAuthenticationFilter(apiKey, "", "", auditLog);
    }

    private ApiKeyAuthenticationFilter createFilterWithRotation(String apiKey, String rotationKey, String deadline) {
        return new ApiKeyAuthenticationFilter(apiKey, rotationKey, deadline, auditLog);
    }

    @Test
    void validApiKey_shouldAuthenticateAndProceed() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/api/v1/engagement/journey/start");
        when(request.getHeader("X-API-KEY")).thenReturn("test-secret-key");

        filter.doFilterInternal(request, response, filterChain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNotNull();
        assertThat(SecurityContextHolder.getContext().getAuthentication().isAuthenticated()).isTrue();
        verify(filterChain).doFilter(request, response);
        verify(auditLog).log(eq("API_KEY_AUTH"), anyString(), anyString(), eq("SUCCESS"), anyMap(), any(Instant.class));
    }

    @Test
    void invalidApiKey_shouldReturn401() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/api/v1/engagement/journey/start");
        when(request.getHeader("X-API-KEY")).thenReturn("wrong-key");
        when(response.getWriter()).thenReturn(new java.io.PrintWriter(new java.io.StringWriter()));

        filter.doFilterInternal(request, response, filterChain);

        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        verify(filterChain, never()).doFilter(request, response);
    }

    @Test
    void missingApiKey_shouldReturn401() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/api/v1/engagement/journey/start");
        when(request.getHeader("X-API-KEY")).thenReturn(null);
        when(response.getWriter()).thenReturn(new java.io.PrintWriter(new java.io.StringWriter()));

        filter.doFilterInternal(request, response, filterChain);

        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
    }

    @Test
    void blankApiKey_shouldReturn401() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/api/v1/engagement/journey/start");
        when(request.getHeader("X-API-KEY")).thenReturn("   ");
        when(response.getWriter()).thenReturn(new java.io.PrintWriter(new java.io.StringWriter()));

        filter.doFilterInternal(request, response, filterChain);

        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
    }

    @Test
    void emptyApiKey_shouldSkipAuthentication() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("");

        filter.doFilterInternal(request, response, filterChain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(filterChain).doFilter(request, response);
    }

    @Test
    void nullApiKey_shouldSkipAuthentication() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter(null);

        filter.doFilterInternal(request, response, filterChain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(filterChain).doFilter(request, response);
    }

    @Test
    void actuatorHealth_shouldBeAccessibleWithoutApiKey() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/actuator/health");

        filter.doFilterInternal(request, response, filterChain);

        verify(filterChain).doFilter(request, response);
        verify(response, never()).setStatus(anyInt());
    }

    @Test
    void actuatorInfo_shouldBeAccessibleWithoutApiKey() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilter("test-secret-key");

        when(request.getRequestURI()).thenReturn("/actuator/info");

        filter.doFilterInternal(request, response, filterChain);

        verify(filterChain).doFilter(request, response);
        verify(response, never()).setStatus(anyInt());
    }

    @Test
    void rotationKey_shouldAuthenticateBeforeDeadline() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilterWithRotation(
                "primary-key", "rotation-key", "2099-12-31");

        when(request.getRequestURI()).thenReturn("/api/v1/test");
        when(request.getHeader("X-API-KEY")).thenReturn("rotation-key");

        filter.doFilterInternal(request, response, filterChain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNotNull();
        verify(auditLog).log(eq("API_KEY_ROTATION_USED"), anyString(), anyString(), eq("SUCCESS"), anyMap(), any(Instant.class));
    }

    // P24 REM-P0-04: 负向测试 — 过期 rotation key 必须被拒绝
    @Test
    void rotationKey_shouldRejectAfterDeadline() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilterWithRotation(
                "primary-key", "rotation-key", "2020-01-01");

        when(request.getRequestURI()).thenReturn("/api/v1/test");
        when(request.getHeader("X-API-KEY")).thenReturn("rotation-key");
        when(response.getWriter()).thenReturn(new java.io.PrintWriter(new java.io.StringWriter()));

        filter.doFilterInternal(request, response, filterChain);

        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        verify(filterChain, never()).doFilter(request, response);
    }

    // P24 REM-P0-04: 负向测试 — 非法 deadline 格式必须 fail-closed（构造器抛异常）
    @Test
    void invalidDeadlineFormat_shouldFailClosed() {
        assertThatThrownBy(() -> createFilterWithRotation("primary-key", "rotation-key", "not-a-date"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Invalid api-key-rotation-deadline format");
    }

    // P24 REM-P0-04: 负向测试 — 空 deadline 应正常工作（无轮转 key）
    @Test
    void blankDeadline_shouldWorkWithoutRotation() throws Exception {
        ApiKeyAuthenticationFilter filter = createFilterWithRotation("primary-key", "", "");

        when(request.getRequestURI()).thenReturn("/api/v1/test");
        when(request.getHeader("X-API-KEY")).thenReturn("primary-key");

        filter.doFilterInternal(request, response, filterChain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNotNull();
    }
}
