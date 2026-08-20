package com.gien.gits.api.dto;

import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.QuickBattleCard;

/**
 * 一键访前自动准备响应（P23/G6，知识地图任务映射驱动）。
 *
 * @param outreachScript        外联脚本
 * @param meetingScript         会面脚本
 * @param previsitReport        访前报告（R1）
 * @param battleCard            速战卡（R2）
 * @param supplyChainMarkdown   公司供应链图谱（KI-FRONT-001，可空）
 */
public record PreparedPrevisitResponse(
        OutreachScript outreachScript,
        MeetingScript meetingScript,
        PrevisitReportContent previsitReport,
        QuickBattleCard battleCard,
        String supplyChainMarkdown) {

    /** 兼容旧 4 参构造（无供应链图谱）。 */
    public PreparedPrevisitResponse(
            OutreachScript outreachScript,
            MeetingScript meetingScript,
            PrevisitReportContent previsitReport,
            QuickBattleCard battleCard) {
        this(outreachScript, meetingScript, previsitReport, battleCard, null);
    }
}