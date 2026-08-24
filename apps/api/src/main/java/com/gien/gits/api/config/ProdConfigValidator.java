package com.gien.gits.api.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

/**
 * P21: Production profile fail-closed validator.
 *
 * <p>在 prod profile 启动时校验关键凭据，缺失必需凭据即抛异常导致启动失败（fail-closed），
 * 避免因缺省空值而静默降级到不安全状态。</p>
 *
 * <p>校验规则（按 {@code engagement.llm.mode} / {@code engagement.crm.mode} / {@code engagement.security.api-key}）：</p>
 * <ul>
 *   <li>API 认证密钥（{@code engagement.security.api-key}）必须非空，否则 API 认证可被绕过。</li>
 *   <li>LLM 为 {@code real} 模式时 {@code engagement.llm.api-key} 必须非空。</li>
 *   <li>CRM 为 {@code http} 模式时 {@code engagement.crm.writeback-url} 必须非空（auth-token 由远端策略决定）。</li>
 * </ul>
 */
@Component
@Profile("prod")
public class ProdConfigValidator implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(ProdConfigValidator.class);

    private final Environment env;

    public ProdConfigValidator(Environment env) {
        this.env = env;
    }

    @Override
    public void run(ApplicationArguments args) {
        log.info("prod-config-validator: validating required production credentials (fail-closed)");

        String apiKey = env.getProperty("engagement.security.api-key", "");
        if (apiKey.isBlank()) {
            throw new IllegalStateException(
                    "prod-config-validator: FAIL: engagement.security.api-key is required in production (fail-closed). "
                    + "Set API_KEY env var.");
        }

        String llmMode = env.getProperty("engagement.llm.mode", "mock");
        if ("real".equalsIgnoreCase(llmMode)) {
            String llmKey = env.getProperty("engagement.llm.api-key", "");
            if (llmKey.isBlank()) {
                throw new IllegalStateException(
                        "prod-config-validator: FAIL: engagement.llm.api-key is required when LLM_MODE=real (fail-closed).");
            }
            log.info("prod-config-validator: OK llm.mode=real with api-key");
        }

        String crmMode = env.getProperty("engagement.crm.mode", "logging");
        if ("http".equalsIgnoreCase(crmMode)) {
            String writebackUrl = env.getProperty("engagement.crm.writeback-url", "");
            if (writebackUrl.isBlank()) {
                throw new IllegalStateException(
                        "prod-config-validator: FAIL: engagement.crm.writeback-url is required when CRM_MODE=http (fail-closed).");
            }
            log.info("prod-config-validator: OK crm.mode=http with writeback-url");
        }

        log.info("prod-config-validator: PASS — required production credentials present");
    }
}
