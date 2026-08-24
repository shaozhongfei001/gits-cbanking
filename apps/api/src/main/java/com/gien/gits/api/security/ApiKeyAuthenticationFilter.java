package com.gien.gits.api.security;

import com.gien.gits.action.port.AuditLogPort;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * API Key 认证过滤器 — 校验 X-API-KEY 请求头
 * <p>
 * 当 engagement.security.api-key 为空时跳过认证（开发模式）；
 * 配置后，除 actuator/health 和 actuator/info 外的所有请求必须携带匹配的 X-API-KEY。
 * <p>
 * P16 G10: 支持 API Key 轮转 — 主 Key + 轮转 Key 并行生效，
 * 轮转 Key 在 api-key-rotation-deadline 后自动失效。
 */
@Component
public class ApiKeyAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyAuthenticationFilter.class);
    private static final String API_KEY_HEADER = "X-API-KEY";

    private final String configuredApiKey;
    private final String rotationApiKey;
    private final LocalDate rotationDeadline;
    private final AuditLogPort auditLog;

    public ApiKeyAuthenticationFilter(
            @Value("${engagement.security.api-key:}") String configuredApiKey,
            @Value("${engagement.security.api-key-rotation:}") String rotationApiKey,
            @Value("${engagement.security.api-key-rotation-deadline:}") String rotationDeadline,
            AuditLogPort auditLog) {
        this.configuredApiKey = configuredApiKey;
        this.rotationApiKey = (rotationApiKey != null && rotationApiKey.isBlank()) ? null : rotationApiKey;
        this.rotationDeadline = parseDeadline(rotationDeadline);
        this.auditLog = auditLog;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        // 开发模式: api-key 为空则跳过认证
        if (!isAuthenticationEnabled()) {
            filterChain.doFilter(request, response);
            return;
        }

        String requestPath = request.getRequestURI();

        // actuator/health 和 actuator/info 公开访问
        if (isActuatorPublicEndpoint(requestPath)) {
            filterChain.doFilter(request, response);
            return;
        }

        String providedApiKey = request.getHeader(API_KEY_HEADER);

        if (providedApiKey == null || providedApiKey.isBlank()) {
            auditLog.log("API_KEY_AUTH", "anonymous", requestPath, "FAILURE",
                    Map.of("reason", "Missing X-API-KEY header"), Instant.now());
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("{\"error\":\"Missing X-API-KEY header\"}");
            return;
        }

        // 主 Key 匹配
        if (configuredApiKey.equals(providedApiKey)) {
            auditLog.log("API_KEY_AUTH", maskKey(providedApiKey), requestPath, "SUCCESS",
                    Map.of("keyType", "primary"), Instant.now());
            SecurityContextHolder.getContext().setAuthentication(new ApiKeyAuthenticationToken(providedApiKey));
            filterChain.doFilter(request, response);
            return;
        }

        // 轮转 Key 匹配
        if (isRotationKeyValid(providedApiKey)) {
            auditLog.log("API_KEY_ROTATION_USED", maskKey(providedApiKey), requestPath, "SUCCESS",
                    Map.of("keyType", "rotation", "deadline", String.valueOf(rotationDeadline)), Instant.now());
            log.warn("API Key rotation key used for path={} — ensure client migrates before deadline={}",
                    requestPath, rotationDeadline);
            SecurityContextHolder.getContext().setAuthentication(new ApiKeyAuthenticationToken(providedApiKey));
            filterChain.doFilter(request, response);
            return;
        }

        // 认证失败
        auditLog.log("API_KEY_AUTH", maskKey(providedApiKey), requestPath, "FAILURE",
                Map.of("reason", "Invalid API key"), Instant.now());
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.getWriter().write("{\"error\":\"Invalid API key\"}");
    }

    private boolean isAuthenticationEnabled() {
        return configuredApiKey != null && !configuredApiKey.isBlank();
    }

    private boolean isActuatorPublicEndpoint(String path) {
        return path.endsWith("/actuator/health") || path.endsWith("/actuator/info");
    }

    private boolean isRotationKeyValid(String providedKey) {
        if (rotationApiKey == null || rotationApiKey.isBlank()) {
            return false;
        }
        if (!rotationApiKey.equals(providedKey)) {
            return false;
        }
        // 检查轮转截止时间
        if (rotationDeadline != null && LocalDate.now().isAfter(rotationDeadline)) {
            log.warn("Rotation key used after deadline={} — rejecting", rotationDeadline);
            return false;
        }
        return true;
    }

    private static LocalDate parseDeadline(String deadline) {
        if (deadline == null || deadline.isBlank()) {
            return null;
        }
        try {
            return LocalDate.parse(deadline, DateTimeFormatter.ISO_DATE_TIME);
        } catch (DateTimeParseException e1) {
            try {
                return LocalDate.parse(deadline, DateTimeFormatter.ISO_DATE);
            } catch (DateTimeParseException e2) {
                // P24 REM-P0-04: fail-closed — 非法 deadline 格式视为配置错误，拒绝启动
                throw new IllegalArgumentException(
                        "Invalid api-key-rotation-deadline format: '" + deadline
                        + "'. Expected ISO date (e.g. 2026-09-01) or ISO datetime. Refusing to start with ambiguous key rotation config.");
            }
        }
    }

    private static String maskKey(String key) {
        if (key == null || key.length() <= 8) {
            return "***";
        }
        return key.substring(0, 4) + "***" + key.substring(key.length() - 4);
    }
}
