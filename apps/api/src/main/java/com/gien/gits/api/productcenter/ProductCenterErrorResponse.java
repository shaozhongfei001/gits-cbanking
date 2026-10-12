package com.gien.gits.api.productcenter;

/**
 * 产品中心端点的统一错误响应（CTR-PKC-API-001 · PkcError）。
 *
 * <p>字段与 {@code specs/product-center/product-center-api.openapi.json} 的
 * {@code PkcError} 逐项一致。本类为产品中心自有类型，不复用 P38 包内类型，
 * 以避免产品中心与冻结的 P38 实现产生耦合（OD-PI-01）。</p>
 */
public record ProductCenterErrorResponse(
        int status,
        String error,
        String code,
        String message,
        String path,
        String timestamp) {
}
