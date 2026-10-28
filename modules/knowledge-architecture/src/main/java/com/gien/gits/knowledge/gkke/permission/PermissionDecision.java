package com.gien.gits.knowledge.gkke.permission;

/**
 * 单资产访问决议（CR-02 §4.1 scope 匹配，C06 权限决议可追溯）。
 *
 * @param allowed 是否允许
 * @param reason  拒绝原因码（ALLOW 时为 "ALLOW"）
 */
public record PermissionDecision(boolean allowed, String reason) {

    public static final String ALLOW = "ALLOW";
    public static final String NOT_PUBLISHED = "NOT_PUBLISHED";
    public static final String TENANT_MISMATCH = "TENANT_MISMATCH";
    public static final String ORG_NOT_AUTHORIZED = "ORG_NOT_AUTHORIZED";
    public static final String CUSTOMER_NOT_AUTHORIZED = "CUSTOMER_NOT_AUTHORIZED";
    public static final String PURPOSE_NOT_DECLARED = "PURPOSE_NOT_DECLARED";

    public static PermissionDecision allow() {
        return new PermissionDecision(true, ALLOW);
    }

    public static PermissionDecision deny(String reason) {
        return new PermissionDecision(false, reason);
    }
}
