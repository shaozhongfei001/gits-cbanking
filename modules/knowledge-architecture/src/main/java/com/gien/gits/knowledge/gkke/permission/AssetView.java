package com.gien.gits.knowledge.gkke.permission;

import java.util.List;

/**
 * 资产的运行时安全投影（CR-02 §4.1/§7）。
 *
 * <p>仅暴露交付所需元数据，不携带内部存储位置 {@code contentRef} 等受控字段；
 * 内容必须经受控交付通道获取，运行时不直接访问存储。
 *
 * @param assetId      资产 ID
 * @param version      版本
 * @param assetClass   资产大类
 * @param kind         资产类型
 * @param title        标题
 * @param lifecycle    生命周期（投影只可能为 PUBLISHED）
 * @param purposeFlags 声明用途
 * @param coreVersion  公共核心版本
 */
public record AssetView(String assetId, String version, String assetClass, String kind,
                        String title, String lifecycle, List<String> purposeFlags,
                        String coreVersion) {

    public AssetView {
        purposeFlags = purposeFlags == null ? List.of() : List.copyOf(purposeFlags);
    }
}
