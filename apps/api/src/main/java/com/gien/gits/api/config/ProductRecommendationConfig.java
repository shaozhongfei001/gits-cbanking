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
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

/**
 * 产品推荐应用服务与 HG-D01 结构化决定服务的 Bean 装配（WP5-2，CANDIDATE）。
 *
 * <p>把此前仅单元测试可用的 {@code ProductRecommendationApplicationService} 提升为 Spring Bean，
 * 并装配其依赖（{@code ProductRecommendationRepository} / {@code SkillExecutionPort} /
 * {@code RecommendationAuthorizationPort}），供 {@code HumanGateController} 的 D01 结构化决定入口使用。</p>
 *
 * <p>{@code RecommendationAuthorizationPort} 当前以默认放行的 CANDIDATE 占位实现注册；真实鉴权
 * 接入后替换。</p>
 */
@Configuration
public class ProductRecommendationConfig {

    /**
     * HG-D01 操作者权限判定端口占位实现。
     * 状态 CANDIDATE：默认放行任意非空 actor；真实鉴权（RM 归属/角色）接入前不改判。
     */
    @Bean
    public RecommendationAuthorizationPort recommendationAuthorizationPort() {
        return (actorId, actorRole, gateId) -> actorId != null && !actorId.isBlank();
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
