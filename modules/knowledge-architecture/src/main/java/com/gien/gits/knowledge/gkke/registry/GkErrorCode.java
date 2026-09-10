package com.gien.gits.knowledge.gkke.registry;

/**
 * GK-KE 稳定合同错误码（CR-02 §6.1）。
 *
 * <p>错误码字符串是跨版本稳定的机器可读合同，禁止随异常类名重构而变化；
 * 错误信息可变，错误码不可变。L1 落地注册中心/地图校验所需子集，
 * 路由/预算类错误码先定义常量供 L2+ 使用。</p>
 */
public enum GkErrorCode {

    /** 依赖引用断裂或引用版本未发布（验收 T06）。 */
    DEPENDENCY_UNRESOLVED("DEPENDENCY_UNRESOLVED"),

    /** 引用的能力未在能力注册表登记（验收 T06）。 */
    CAPABILITY_NOT_REGISTERED("CAPABILITY_NOT_REGISTERED"),

    /** 资产存在但当前不可用（未发布/已撤销）。 */
    ASSET_NOT_AVAILABLE("ASSET_NOT_AVAILABLE"),

    /** 同一资产版本重复登记。 */
    DUPLICATE_ASSET_VERSION("DUPLICATE_ASSET_VERSION"),

    /** 依赖闭包存在环。 */
    DEPENDENCY_CYCLE("DEPENDENCY_CYCLE"),

    /** 知识地图可执行依赖子图存在环（验收 T20）。 */
    MAP_CYCLE_DETECTED("MAP_CYCLE_DETECTED"),

    /** 知识地图结构非法（入口/端点缺失、relation 非枚举等）。 */
    MAP_VALIDATION_FAILED("MAP_VALIDATION_FAILED"),

    /** 路由命中多条策略（L2 使用，先定义常量）。 */
    ROUTE_AMBIGUOUS("ROUTE_AMBIGUOUS"),

    /** 超出预算约束（L2 使用，先定义常量）。 */
    BUDGET_EXCEEDED("BUDGET_EXCEEDED"),

    /** 主体无访问权限（L2+ 使用，先定义常量）。 */
    PERMISSION_DENIED("PERMISSION_DENIED");

    private final String wireValue;

    GkErrorCode(String wireValue) {
        this.wireValue = wireValue;
    }

    /** 合同错误码字符串（稳定，禁止变更）。 */
    public String wireValue() {
        return wireValue;
    }
}
