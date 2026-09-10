package com.gien.gits.knowledge.gkke.map;

/**
 * 知识地图结构校验失败（CR-02 §4.2：入口存在、边端点存在、禁止有环）。
 */
public class MapValidationException extends RuntimeException {

    public MapValidationException(String message) {
        super(message);
    }
}
