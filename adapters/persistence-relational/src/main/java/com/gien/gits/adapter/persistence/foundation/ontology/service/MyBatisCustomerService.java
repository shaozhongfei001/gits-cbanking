package com.gien.gits.adapter.persistence.foundation.ontology.service;

import com.gien.gits.adapter.persistence.foundation.ontology.dto.CustomerRow;
import com.gien.gits.adapter.persistence.foundation.ontology.mapper.CustomerMapper;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.port.WritableCustomerRepository;

import java.util.List;
import java.util.Optional;

/**
 * MyBatis 客户仓储实现 — foundation/ontology 层
 */
public class MyBatisCustomerService implements WritableCustomerRepository {

    private final CustomerMapper mapper;

    public MyBatisCustomerService(CustomerMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public void save(Customer customer) {
        mapper.insert(customer);
    }

    @Override
    public void update(Customer customer) {
        mapper.update(customer);
    }

    @Override
    public Optional<Customer> findById(String customerId) {
        return mapper.findRowById(customerId).map(CustomerRow::toCustomer);
    }

    @Override
    public List<Customer> findByRmId(String rmId) {
        return mapper.findRowsByRmId(rmId).stream().map(CustomerRow::toCustomer).toList();
    }

    @Override
    public List<Customer> findAll() {
        return mapper.findAllRows().stream().map(CustomerRow::toCustomer).toList();
    }
}
