package com.gien.gits.api.dto;

/**
 * CRM 客户 upsert 结果。status 为 CREATED 或 UPDATED。
 */
public record CrmCustomerUpsertResponse(
        String customerId,
        String customerName,
        String status) {}
