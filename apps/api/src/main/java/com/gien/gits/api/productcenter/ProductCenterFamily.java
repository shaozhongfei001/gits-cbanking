package com.gien.gits.api.productcenter;

/**
 * 产品族（CTR-PKC-DOM-001 · PkcProductFamily）。
 *
 * <p>分类骨架权威源为 {@code CTR-PK-TAX-001}（owner 已裁定 OQ-B / OD-PI-04），
 * 本服务只读呈现，不生成、不改写族定义。</p>
 *
 * @param familyId          族 ID（taxonomy families[].id）
 * @param familyName        族中文名（taxonomy name_zh，族名唯一权威）
 * @param parentFamilyId    父族（当前基线无层级，恒为 null）
 * @param domainId          产品域 ID（taxonomy families[].domain）
 * @param domainName        产品域中文名
 * @param displayOrder      目录显示顺序（按 taxonomy 文件顺序）
 * @param visibilityScope   可见范围（当前基线为 ALL_RM）
 * @param activeProductCount 已登记并可呈现的产品数（本族内、且产品卡存在）
 * @param unclassifiedCount 待归类产品数（族内无产品卡或族缺失，不静默丢失）
 */
public record ProductCenterFamily(
        String familyId,
        String familyName,
        String parentFamilyId,
        String domainId,
        String domainName,
        int displayOrder,
        String visibilityScope,
        int activeProductCount,
        int unclassifiedCount) {
}
