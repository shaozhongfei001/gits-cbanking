package com.gien.gits.api.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.adapter.persistence.JdbcProductRecommendationRepository;
import com.gien.gits.api.service.ProductRecommendationApplicationService;
import com.gien.gits.api.service.ProductRecommendationHumanGateService;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.ontology.port.HumanGateRepository;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import com.gien.gits.customerjourney.recommendation.port.RecommendationAuthorizationPort;
import com.gien.gits.adapter.authorization.RoleBasedRecommendationAuthorizationAdapter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 产品推荐应用服务与 HG-D01 结构化决定服务的 Bean 装配（WP5-2，CANDIDATE）。
 *
 * <p>把此前仅单元测试可用的 {@code ProductRecommendationApplicationService} 提升为 Spring Bean，
 * 并装配其依赖（{@code ProductRecommendationRepository} / {@code SkillExecutionPort} /
 * {@code RecommendationAuthorizationPort}），供 {@code HumanGateController} 的 D01 结构化决定入口使用。</p>
 *
 * <p>F-4（2026-09-04）：{@code RecommendationAuthorizationPort} 已由「默认放行任意非空 actor」的
 * 占位 lambda 替换为 {@link RoleBasedRecommendationAuthorizationAdapter} 角色白名单实现，
 * 消除无条件越权。白名单通过 {@code gits.recommendation.authorization.allowed-roles} 配置，
 * 未配置时回退到内置默认角色集；配置为空则 fail-closed 拒绝一切决定。</p>
 */
@Configuration
public class ProductRecommendationConfig {

    /**
     * 未显式配置白名单时使用的默认允许角色。
     * 取自现有场景语义：客户经理及其主管可对产品推荐门禁作决定。
     */
    private static final Set<String> DEFAULT_ALLOWED_ROLES =
            Set.of("RM", "RELATIONSHIP_MANAGER", "RM_SUPERVISOR", "PRODUCT_OWNER");

    /**
     * HG-D01 操作者权限判定端口。
     *
     * <p>F-4 已落地角色白名单判定：actorId / gateId / actorRole 三者任一为空即拒绝，
     * actorRole 不在白名单内即拒绝（fail-closed）。RM 归属校验与企业 IAM 对接为剩余部分，
     * 见 {@link RoleBasedRecommendationAuthorizationAdapter} 类注释与 FAILURES.md。</p>
     */
    @Bean
    public RecommendationAuthorizationPort recommendationAuthorizationPort(
            @Value("${gits.recommendation.authorization.allowed-roles:}") String allowedRolesConfig) {
        Set<String> roles = parseAllowedRoles(allowedRolesConfig);
        return new RoleBasedRecommendationAuthorizationAdapter(roles);
    }

    /**
     * 解析逗号分隔的角色配置；未配置或全为空白时回退到内置默认角色集。
     */
    private static Set<String> parseAllowedRoles(String config) {
        if (config == null || config.isBlank()) {
            return DEFAULT_ALLOWED_ROLES;
        }
        Set<String> parsed = Arrays.stream(config.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .map(String::toUpperCase)
                .collect(Collectors.toUnmodifiableSet());
        return parsed.isEmpty() ? DEFAULT_ALLOWED_ROLES : parsed;
    }

    @Bean
    public ProductRecommendationRepository productRecommendationRepository(
            JdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        return new JdbcProductRecommendationRepository(jdbcTemplate, objectMapper);
    }

    @Bean
    public ProductRecommendationApplicationService productRecommendationApplicationService(
            ProductRecommendationRepository repository,
            SkillExecutionPort skillExecutionPort,
            RecommendationAuthorizationPort authorizationPort) {
        return new ProductRecommendationApplicationService(repository, skillExecutionPort, authorizationPort);
    }

    @Bean
    public ProductRecommendationHumanGateService productRecommendationHumanGateService(
            ProductRecommendationApplicationService applicationService,
            HumanGateRepository humanGateRepository,
            AuditLogPort auditLogPort) {
        return new ProductRecommendationHumanGateService(applicationService, humanGateRepository, auditLogPort);
    }
}
