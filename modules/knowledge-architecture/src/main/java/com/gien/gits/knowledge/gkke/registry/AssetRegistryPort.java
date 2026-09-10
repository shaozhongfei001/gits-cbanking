package com.gien.gits.knowledge.gkke.registry;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.ReleaseManifestRecord;
import java.util.List;
import java.util.Optional;

/**
 * GK-KE v1 知识资产注册中心端口（CR-02 §4.1，验收 T05）。
 *
 * <p>注册中心只追加、不可变：同一 {@code assetId + version} 只能登记一次；
 * 发布清单解析出的资产快照同样不可变。
 */
public interface AssetRegistryPort {

    /**
     * 登记一个资产版本；重复登记抛出 {@link DuplicateAssetVersionException}。
     *
     * @param asset 资产版本记录（不可为 {@code null}）
     */
    void register(AssetVersionRecord asset);

    /**
     * 按资产 ID 与精确版本解析。
     *
     * @param assetId 资产 ID
     * @param version 语义版本
     * @return 资产版本；不存在返回空
     */
    Optional<AssetVersionRecord> resolve(String assetId, String version);

    /**
     * 解析资产的最新已登记版本（语义版本比较）。
     *
     * @param assetId 资产 ID
     * @return 最高版本资产；无任何版本返回空
     */
    Optional<AssetVersionRecord> resolveLatest(String assetId);

    /** 按资产大类过滤（FOUNDATIONAL_DATA/KNOWLEDGE_RULE/PROCESS_TOOL/RUNTIME_FEEDBACK）。 */
    List<AssetVersionRecord> findByAssetClass(String assetClass);

    /** 按资产类型过滤（PRODUCT_CARD/POLICY/METRIC/SKILL 等）。 */
    List<AssetVersionRecord> findByKind(String kind);

    /** 列出所有已登记资产版本（目录发现全集；运行时权限过滤在调用方完成）。 */
    List<AssetVersionRecord> findAll();

    /** 按生命周期过滤（CANDIDATE/IN_REVIEW/APPROVED/PUBLISHED/REVOKED）。 */
    List<AssetVersionRecord> findByLifecycle(String lifecycle);

    /** 按所有系统过滤（KERT/SEMANTIC_SERVICE/GITS/SIMULATION_PLATFORM）。 */
    List<AssetVersionRecord> findByOwnerSystem(String ownerSystem);

    /** 查询所有已发布且声明该用途的资产（purposeFlags 包含该用途）。 */
    List<AssetVersionRecord> findPublishedByPurpose(String purpose);

    /**
     * 按发布清单解析不可变资产快照（CR-02 §4.3）。
     *
     * <p>清单引用的每个资产必须存在且为 {@code PUBLISHED}；快照返回后不随后续登记变化。
     *
     * @param manifest 发布清单
     * @return 不可变资产列表（顺序与清单引用一致，去重）
     * @throws AssetNotFoundException 引用资产不存在
     * @throws IllegalStateException  引用资产未发布
     */
    List<AssetVersionRecord> snapshotRelease(ReleaseManifestRecord manifest);

    /**
     * 计算资产的传递依赖闭包（CR-02 §4.1 dependencyRefs）。
     *
     * <p>深度优先遍历 {@code dependencyRefs}，返回拓扑序列表：被依赖者在前，根资产在最后；
     * 重复依赖只出现一次。依赖环抛出 {@link DependencyCycleException}，
     * 缺失依赖抛出 {@link AssetNotFoundException}。
     *
     * @param assetId 根资产 ID
     * @param version 根资产版本
     * @return 不可变依赖闭包列表（依赖在前，根资产在最后）
     */
    List<AssetVersionRecord> dependencyClosure(String assetId, String version);
}
