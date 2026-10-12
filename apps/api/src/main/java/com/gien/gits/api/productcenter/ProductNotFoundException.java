package com.gien.gits.api.productcenter;

/**
 * 产品未在受控分类法中登记（CTR-PKC-API-001 · {@code PRODUCT_NOT_FOUND}）。
 */
public class ProductNotFoundException extends RuntimeException {

    public ProductNotFoundException(String productId) {
        super("产品未登记: " + productId);
    }
}
