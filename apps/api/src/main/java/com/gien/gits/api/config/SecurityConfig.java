package com.gien.gits.api.config;

import com.gien.gits.api.security.ApiKeyAuthenticationFilter;
import org.springframework.beans.factory.BeanCreationException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

/**
 * 安全基线配置 — API Key 认证 + CORS + 无状态会话
 * <p>
 * 开发模式下 (engagement.security.api-key 为空) 自动跳过认证；
 * 生产模式配置 api-key 后，除 actuator/health 和 actuator/info 外的请求必须携带 X-API-KEY。
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final ApiKeyAuthenticationFilter apiKeyFilter;
    private final String allowedOrigins;

    public SecurityConfig(ApiKeyAuthenticationFilter apiKeyFilter,
                          @Value("${engagement.security.cors.allowed-origins:http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080}") String allowedOrigins) {
        this.apiKeyFilter = apiKeyFilter;
        this.allowedOrigins = allowedOrigins;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/actuator/info").permitAll()
                .anyRequest().permitAll()
            )
            .addFilterBefore(apiKeyFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of(allowedOrigins.split(",")));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }

    @Bean
    @Profile("prod")
    public ApiKeyValidator prodApiKeyValidator(@Value("${engagement.security.api-key:}") String apiKey) {
        if (apiKey == null || apiKey.isBlank()) {
            throw new BeanCreationException(
                "engagement.security.api-key must be set and non-blank in production profile");
        }
        return new ApiKeyValidator(apiKey);
    }

    record ApiKeyValidator(String apiKey) {}
}
