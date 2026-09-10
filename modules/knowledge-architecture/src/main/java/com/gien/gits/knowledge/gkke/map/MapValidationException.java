package com.gien.gits.knowledge.gkke.map;

import com.gien.gits.knowledge.gkke.registry.GkDomainException;
import com.gien.gits.knowledge.gkke.registry.GkErrorCode;

/**
 * 知识地图结构非法（入口/端点缺失、relation 非枚举、执行依赖成环等）。
 *
 * <p>Q3：携带稳定合同错误码（CR-02 §6.1）。结构非法用
 * {@link GkErrorCode#MAP_VALIDATION_FAILED}；执行依赖成环用
 * {@link GkErrorCode#MAP_CYCLE_DETECTED}（验收 T20）。</p>
 */
public class MapValidationException extends GkDomainException {

    private MapValidationException(GkErrorCode code, String message) {
        super(code, message);
    }

    public static MapValidationException invalid(String message) {
        return new MapValidationException(GkErrorCode.MAP_VALIDATION_FAILED, message);
    }

    public static MapValidationException cycle(String message) {
        return new MapValidationException(GkErrorCode.MAP_CYCLE_DETECTED, message);
    }
}
