package com.gien.gits.adapter.persistence.foundation.ontology.mapper;

import com.gien.gits.adapter.persistence.foundation.ontology.dto.CustomerRow;
import com.gien.gits.ontology.Customer;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Optional;

/**
 * 客户 Mapper — foundation/ontology 层
 */
@Mapper
public interface CustomerMapper {

    void insert(Customer customer);

    void update(Customer customer);

    Optional<CustomerRow> findRowById(@Param("customerId") String customerId);

    List<CustomerRow> findRowsByRmId(@Param("rmId") String rmId);

    List<CustomerRow> findAllRows();
}
