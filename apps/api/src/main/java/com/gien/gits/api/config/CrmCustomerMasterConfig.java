package com.gien.gits.api.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.service.CrmCustomerMasterService;
import com.gien.gits.ontology.port.WritableCustomerRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ResourceLoader;

/**
 * CRM 客户目录服务与启动加载（Flyway 之后）。只写 customer 表。
 */
@Configuration
public class CrmCustomerMasterConfig {

    private static final Logger log = LoggerFactory.getLogger(CrmCustomerMasterConfig.class);

    @Bean
    public CrmCustomerMasterService crmCustomerMasterService(
            WritableCustomerRepository customerRepo,
            ObjectMapper objectMapper,
            ResourceLoader resourceLoader,
            @Value("${gits.crm-master.fixture-path:docs/dd/fixtures/gits-crm-customer-master.json}")
            String fixturePath) {
        return new CrmCustomerMasterService(customerRepo, objectMapper, resourceLoader, fixturePath);
    }

    @Bean
    @ConditionalOnProperty(name = "gits.crm-master.load-on-startup", havingValue = "true", matchIfMissing = true)
    public ApplicationRunner crmCustomerMasterStartupLoader(CrmCustomerMasterService crmCustomerMasterService) {
        return args -> {
            try {
                var result = crmCustomerMasterService.reloadFromFixture();
                log.info("CRM master startup load upserted {} customers", result.upsertedCount());
            } catch (Exception ex) {
                log.warn("CRM master startup load skipped: {}", ex.getMessage());
            }
        };
    }
}
