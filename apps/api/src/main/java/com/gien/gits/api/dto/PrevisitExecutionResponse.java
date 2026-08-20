package com.gien.gits.api.dto;

import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.QuickBattleCard;

/**
 * 访前准备执行响应 — 返回访前报告、60秒作战卡与供应链图谱。
 *
 * @param previsitReport       访前报告（R1格式），包含客户概览、KYC缺口、产品方案等
 * @param battleCard           60秒作战卡（R2格式），移动端快速查看要点
 * @param supplyChainMarkdown  公司供应链图谱（KI-FRONT-001 上游/下游/位置解读，可空）
 */
public record PrevisitExecutionResponse(
        PrevisitReportContent previsitReport,
        QuickBattleCard battleCard,
        String supplyChainMarkdown) {

    /** 兼容旧 2 参构造（无供应链图谱）。 */
    public PrevisitExecutionResponse(PrevisitReportContent previsitReport,
                                     QuickBattleCard battleCard) {
        this(previsitReport, battleCard, null);
    }
}