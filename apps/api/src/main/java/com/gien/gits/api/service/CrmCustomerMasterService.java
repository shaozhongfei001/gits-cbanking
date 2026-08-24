package com.gien.gits.api.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.dto.CrmCustomerMaster;
import com.gien.gits.api.dto.CrmCustomerMasterReloadResponse;
import com.gien.gits.api.dto.CrmCustomerUpsertResponse;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import com.gien.gits.ontology.port.WritableCustomerRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.transaction.annotation.Transactional;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * CRM 客户主档写入 — 只写 H2 {@code customer} 表，不摄入 KYC/产品/交易/图谱。
 */
public class CrmCustomerMasterService {

    private static final Logger log = LoggerFactory.getLogger(CrmCustomerMasterService.class);

    static final String STATUS_CREATED = "CREATED";
    static final String STATUS_UPDATED = "UPDATED";

    private final WritableCustomerRepository customerRepo;
    private final ObjectMapper objectMapper;
    private final ResourceLoader resourceLoader;
    private final String fixturePath;

    public CrmCustomerMasterService(
            WritableCustomerRepository customerRepo,
            ObjectMapper objectMapper,
            ResourceLoader resourceLoader,
            String fixturePath) {
        this.customerRepo = Objects.requireNonNull(customerRepo, "customerRepo");
        this.objectMapper = Objects.requireNonNull(objectMapper, "objectMapper");
        this.resourceLoader = Objects.requireNonNull(resourceLoader, "resourceLoader");
        this.fixturePath = fixturePath != null && !fixturePath.isBlank()
                ? fixturePath
                : "docs/dd/fixtures/gits-crm-customer-master.json";
    }

    @Transactional
    public CrmCustomerUpsertResponse upsert(String pathCustomerId, CrmCustomerMaster body) {
        if (body == null) {
            throw new IllegalArgumentException("CRM customer body is required");
        }
        if (pathCustomerId == null || pathCustomerId.isBlank()
                || !pathCustomerId.equals(body.customerId())) {
            throw new IllegalArgumentException("path customerId must equal body.customerId");
        }

        Customer incoming = toCustomer(body, Instant.now(), Instant.now());
        Optional<Customer> existing = customerRepo.findById(pathCustomerId);
        if (existing.isEmpty()) {
            customerRepo.save(incoming);
            return new CrmCustomerUpsertResponse(incoming.customerId(), incoming.customerName(), STATUS_CREATED);
        }

        Customer current = existing.get();
        if (bothNonBlankAndDiffer(current.unifiedSocialCreditCode(), incoming.unifiedSocialCreditCode())) {
            throw new IllegalStateException(
                    "unifiedSocialCreditCode conflict for customerId " + pathCustomerId);
        }

        Customer updated = toCustomer(body, current.createdAt(), Instant.now());
        customerRepo.update(updated);
        return new CrmCustomerUpsertResponse(updated.customerId(), updated.customerName(), STATUS_UPDATED);
    }

    /**
     * 读取 fixture JSON {@code {customers:[...]}}，对每条做幂等 upsert。
     * 忽略 schemaVersion / purpose 以外的未知顶层键；不写 KYC/产品/交易/图谱表。
     */
    @Transactional
    public CrmCustomerMasterReloadResponse reloadFromFixture() {
        byte[] bytes = readFixtureBytes();
        if (bytes == null) {
            return new CrmCustomerMasterReloadResponse(0, List.of());
        }

        JsonNode root;
        try {
            root = objectMapper.readTree(bytes);
        } catch (Exception ex) {
            throw new IllegalArgumentException("CRM master fixture is not readable JSON", ex);
        }

        JsonNode customersNode = root.path("customers");
        if (!customersNode.isArray()) {
            log.warn("CRM master fixture has no customers array: {}", fixturePath);
            return new CrmCustomerMasterReloadResponse(0, List.of());
        }

        List<String> ids = new ArrayList<>();
        for (JsonNode node : customersNode) {
            CrmCustomerMaster master;
            try {
                master = objectMapper.treeToValue(node, CrmCustomerMaster.class);
            } catch (Exception ex) {
                throw new IllegalArgumentException("Invalid CRM customer in fixture: " + ex.getMessage(), ex);
            }
            if (master == null || master.customerId() == null || master.customerId().isBlank()) {
                throw new IllegalArgumentException("Fixture customer is missing customerId");
            }
            upsert(master.customerId(), master);
            ids.add(master.customerId());
        }
        log.info("CRM master fixture upserted {} customers from {}", ids.size(), fixturePath);
        return new CrmCustomerMasterReloadResponse(ids.size(), List.copyOf(ids));
    }

    Customer toCustomer(CrmCustomerMaster body, Instant createdAt, Instant updatedAt) {
        return new Customer(
                body.customerId(),
                body.customerName(),
                body.customerShortName(),
                body.unifiedSocialCreditCode(),
                body.establishedDate(),
                body.registeredCapitalCny() != null ? body.registeredCapitalCny() : 0L,
                parseEnum(Industry.class, body.industry()),
                body.region(),
                parseEnum(EnterpriseScale.class, body.enterpriseScale()),
                parseEnum(CustomerTier.class, body.customerTier()),
                body.relationshipSince(),
                body.rmId(),
                body.rmName(),
                body.managingBranch(),
                body.groupFlag() != null && body.groupFlag(),
                parseEnum(ListedStatus.class, body.listedStatus()),
                parseEnum(RiskLevel.class, body.riskLevel()),
                body.mainProducts(),
                body.coreTags(),
                body.relationshipSummary(),
                createdAt,
                updatedAt);
    }

    private static <E extends Enum<E>> E parseEnum(Class<E> type, String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return Enum.valueOf(type, value);
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Invalid " + type.getSimpleName() + ": " + value);
        }
    }

    private static boolean bothNonBlankAndDiffer(String existing, String incoming) {
        return isNonBlank(existing) && isNonBlank(incoming) && !existing.equals(incoming);
    }

    private static boolean isNonBlank(String value) {
        return value != null && !value.isBlank();
    }

    private byte[] readFixtureBytes() {
        Path file = resolveFixtureFile();
        if (file != null) {
            try {
                return Files.readAllBytes(file);
            } catch (Exception ex) {
                log.warn("CRM master fixture unreadable at {}: {}", file, ex.getMessage());
                return null;
            }
        }

        Resource resource = resourceLoader.getResource("classpath:" + fixturePath);
        if (resource.exists()) {
            try (InputStream in = resource.getInputStream()) {
                return in.readAllBytes();
            } catch (Exception ex) {
                log.warn("CRM master fixture classpath unreadable {}: {}", fixturePath, ex.getMessage());
                return null;
            }
        }

        log.warn("CRM master fixture not found: {}", fixturePath);
        return null;
    }

    Path resolveFixtureFile() {
        Path configured = Path.of(fixturePath);
        if (configured.isAbsolute() && Files.isRegularFile(configured)) {
            return configured;
        }

        Path cursor = Path.of(System.getProperty("user.dir", ".")).toAbsolutePath().normalize();
        while (cursor != null) {
            Path candidate = cursor.resolve(fixturePath).normalize();
            if (Files.isRegularFile(candidate)) {
                return candidate;
            }
            cursor = cursor.getParent();
        }
        return null;
    }
}
