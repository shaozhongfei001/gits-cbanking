package com.gien.gits.adapter.persistence;

import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import com.gien.gits.ontology.port.WritableCustomerRepository;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

public class JdbcCustomerRepository implements WritableCustomerRepository {

    private static final String INSERT_SQL = """
        INSERT INTO customer (customer_id, customer_name, customer_short_name,
            unified_social_credit_code, established_date, registered_capital_cny,
            industry, region, enterprise_scale, customer_tier, relationship_since,
            rm_id, rm_name, managing_branch, group_flag, listed_status, risk_level,
            main_products, core_tags, relationship_summary, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """;

    private static final String UPDATE_SQL = """
        UPDATE customer SET
            customer_name = ?, customer_short_name = ?,
            unified_social_credit_code = ?, established_date = ?, registered_capital_cny = ?,
            industry = ?, region = ?, enterprise_scale = ?, customer_tier = ?, relationship_since = ?,
            rm_id = ?, rm_name = ?, managing_branch = ?,
            group_flag = ?, listed_status = ?, risk_level = ?,
            main_products = ?, core_tags = ?, relationship_summary = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE customer_id = ?
        """;

    private static final String FIND_BY_ID_SQL = """
        SELECT customer_id, customer_name, customer_short_name,
            unified_social_credit_code, established_date, registered_capital_cny,
            industry, region, enterprise_scale, customer_tier, relationship_since,
            rm_id, rm_name, managing_branch, group_flag, listed_status, risk_level,
            main_products, core_tags, relationship_summary, created_at, updated_at
        FROM customer WHERE customer_id = ?
        """;

    private static final String FIND_BY_RM_SQL = FIND_BY_ID_SQL.replace("WHERE customer_id = ?", "WHERE rm_id = ?");

    private static final String FIND_ALL_SQL = FIND_BY_ID_SQL.replace("WHERE customer_id = ?", "");

    private final JdbcTemplate jdbcTemplate;

    public JdbcCustomerRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = Objects.requireNonNull(jdbcTemplate, "jdbcTemplate");
    }

    @Override
    public void save(Customer customer) {
        jdbcTemplate.update(INSERT_SQL,
            customer.customerId(), customer.customerName(), customer.customerShortName(),
            customer.unifiedSocialCreditCode(), customer.establishedDate(), customer.registeredCapitalCny(),
            enumName(customer.industry()), customer.region(), enumName(customer.enterpriseScale()),
            enumName(customer.customerTier()),
            customer.relationshipSince(), customer.rmId(), customer.rmName(), customer.managingBranch(),
            customer.groupFlag(), enumName(customer.listedStatus()), enumName(customer.riskLevel()),
            JsonHelper.toJsonArray(customer.mainProducts()), JsonHelper.toJsonArray(customer.coreTags()),
            customer.relationshipSummary());
    }

    @Override
    public void update(Customer customer) {
        jdbcTemplate.update(UPDATE_SQL,
            customer.customerName(), customer.customerShortName(),
            customer.unifiedSocialCreditCode(), customer.establishedDate(), customer.registeredCapitalCny(),
            enumName(customer.industry()), customer.region(), enumName(customer.enterpriseScale()),
            enumName(customer.customerTier()),
            customer.relationshipSince(), customer.rmId(), customer.rmName(), customer.managingBranch(),
            customer.groupFlag(), enumName(customer.listedStatus()), enumName(customer.riskLevel()),
            JsonHelper.toJsonArray(customer.mainProducts()), JsonHelper.toJsonArray(customer.coreTags()),
            customer.relationshipSummary(),
            customer.customerId());
    }

    public Optional<Customer> findById(String customerId) {
        List<Customer> results = jdbcTemplate.query(FIND_BY_ID_SQL, new CustomerRowMapper(), customerId);
        return results.stream().findFirst();
    }

    public List<Customer> findByRmId(String rmId) {
        return jdbcTemplate.query(FIND_BY_RM_SQL, new CustomerRowMapper(), rmId);
    }

    @Override
    public List<Customer> findAll() {
        return jdbcTemplate.query(FIND_ALL_SQL, new CustomerRowMapper());
    }

    private static String enumName(Enum<?> value) {
        return value == null ? null : value.name();
    }

    private static Customer toCustomer(ResultSet rs) throws SQLException {
        return new Customer(
            rs.getString("customer_id"), rs.getString("customer_name"),
            rs.getString("customer_short_name"), rs.getString("unified_social_credit_code"),
            rs.getObject("established_date", LocalDate.class), rs.getLong("registered_capital_cny"),
            Industry.valueOf(rs.getString("industry")), rs.getString("region"),
            EnterpriseScale.valueOf(rs.getString("enterprise_scale")),
            CustomerTier.valueOf(rs.getString("customer_tier")),
            rs.getObject("relationship_since", LocalDate.class),
            rs.getString("rm_id"), rs.getString("rm_name"), rs.getString("managing_branch"),
            rs.getBoolean("group_flag"),
            ListedStatus.valueOf(rs.getString("listed_status")),
            RiskLevel.valueOf(rs.getString("risk_level")),
            JsonHelper.parseStringList(rs.getString("main_products")),
            JsonHelper.parseStringList(rs.getString("core_tags")),
            rs.getString("relationship_summary"),
            rs.getTimestamp("created_at") != null ? rs.getTimestamp("created_at").toInstant() : Instant.now(),
            rs.getTimestamp("updated_at") != null ? rs.getTimestamp("updated_at").toInstant() : Instant.now());
    }

    private static final class CustomerRowMapper implements RowMapper<Customer> {
        @Override
        public Customer mapRow(ResultSet rs, int rowNum) throws SQLException {
            return toCustomer(rs);
        }
    }
}
