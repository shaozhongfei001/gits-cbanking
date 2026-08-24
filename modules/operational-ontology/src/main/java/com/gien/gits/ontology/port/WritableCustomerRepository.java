package com.gien.gits.ontology.port;

import com.gien.gits.ontology.Customer;

/**
 * 可写客户仓储端口 — 在 {@link CustomerRepository} 只读契约基础上增加写操作。
 *
 * <p>适配器层的 JDBC 实现类应实现此接口，从而同时满足读/写契约。</p>
 */
public interface WritableCustomerRepository extends CustomerRepository {

    /**
     * 保存客户聚合。
     *
     * @param customer 待保存的客户
     */
    void save(Customer customer);

    /**
     * 按 customer_id 更新 CRM 主档列（不改 created_at）。
     *
     * @param customer 待更新的客户
     */
    void update(Customer customer);
}
