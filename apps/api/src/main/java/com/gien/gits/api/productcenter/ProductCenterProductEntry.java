package com.gien.gits.api.productcenter;

import java.util.List;

/**
 * 产品目录条目（CTR-PKC-DOM-001 · PkcProductCatalogEntry）。
 *
 * @param productId              稳定产品标识（OD-PI-05：括号内不携带环境语义）
 * @param productCode            银行产品代码；DEMO 数据使用 DEMO-* 前缀
 * @param productName            产品中文名（以 taxonomy name_zh 为权威）
 * @param aliases                别名（产品卡 front matter 提供，用于搜索）
 * @param familyId               所属族 ID
 * @param familyName             所属族中文名
 * @param lifecycleStatus        生命周期状态（taxonomy_registration_status 映射）
 * @param currentPublishedVersionId 当前已发布知识版本；无已发布版本时为 null
 * @param hasPublishedVersion    是否存在已发布受控知识版本（false ⇒ 目录显示「无有效版本」）
 * @param environment            DEMO / UAT / PROD
 * @param isDemo                 DEMO 数据标记（不得计入生产口径）
 */
public record ProductCenterProductEntry(
        String productId,
        String productCode,
        String productName,
        List<String> aliases,
        String familyId,
        String familyName,
        String lifecycleStatus,
        String currentPublishedVersionId,
        boolean hasPublishedVersion,
        String environment,
        boolean isDemo) {
}
