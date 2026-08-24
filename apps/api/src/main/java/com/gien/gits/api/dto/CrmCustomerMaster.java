package com.gien.gits.api.dto;

import java.time.LocalDate;
import java.util.List;

/**
 * CRM 客户主档（身份字段 only）。不包含 KYC / 产品 / 图谱。
 */
public record CrmCustomerMaster(
        String customerId,
        String customerName,
        String customerShortName,
        String unifiedSocialCreditCode,
        LocalDate establishedDate,
        Long registeredCapitalCny,
        String industry,
        String region,
        String enterpriseScale,
        String customerTier,
        LocalDate relationshipSince,
        String rmId,
        String rmName,
        String managingBranch,
        Boolean groupFlag,
        String listedStatus,
        String riskLevel,
        List<String> mainProducts,
        List<String> coreTags,
        String relationshipSummary) {}
