package com.gien.gits.api.dto;

import java.util.List;

/**
 * CRM 主档 fixture 重载结果。
 */
public record CrmCustomerMasterReloadResponse(
        int upsertedCount,
        List<String> customerIds) {}
