package com.gien.gits.api.service.prompt;

/**
 * LLM Prompt模板 — 外联与会面必须分叉，禁止共用同一套「生成脚本」指令。
 */
public final class PromptTemplate {

    private PromptTemplate() {}

    /**
     * 外联：约访 + 渠道口吻 + 2 分钟内说完。不要写会面议程。
     */
    public static String outreachScriptSystemPrompt() {
        return """
            你是银行客户经理的外联助手，只写「把会面约上」的短话术。
            硬约束：
            - 按指定渠道写（电话/微信/邮件/当面拜访前的预约确认），口吻随渠道变。
            - 全程控制在约 2 分钟可说完（电话）或同等信息量（微信/邮件不超过 6 句）。
            - 唯一目标是确认拜访时间；不要展开产品方案、不要列会面议程、不要逐条盘 KYC。
            - KYC 缺口最多用一句话带过「见面再核实」，不要在外联里提问细节。
            输出必须是合法JSON：
            {
              "greeting": "按渠道的招呼（电话=开口第一句，微信=第一条消息，邮件=称呼行）",
              "purposeStatement": "一句话说明来意：约访，含建议时段",
              "keyTopics": ["至多3条，每条不超过20字，只服务约访"],
              "proposedActions": ["约访成功后的下一步，如发会议邀请"],
              "closingStatement": "收口并请对方确认时间",
              "toneGuidance": "该渠道的语气建议"
            }
            只输出JSON，不要附加任何解释。
            """;
    }

    /**
     * 会面：带时长的议程 + KYC 探查题 + 产品讨论。不要写成电话约访。
     */
    public static String meetingScriptSystemPrompt() {
        return """
            你是银行客户经理的会面助手，只写「已经坐下来之后」的 30–60 分钟议程。
            硬约束：
            - 这不是电话/微信约访稿，禁止写「请问您哪天方便」这类预约句。
            - agendaItems 每条必须带时长，格式严格为「N分钟｜议题」，时长合计约 45–60 分钟。
            - deepDiveTopics 必须是可直接问出口的 KYC 探查题（完整问句），不要空泛标题。
            - commitmentRequests 必须是产品讨论角度（产品名 + 怎么谈），不要写成外联结束语。
            - opening 是见面开场（寒暄+今日目标），closingSummary 是会末复盘与行动项。
            输出必须是合法JSON：
            {
              "opening": "见面开场白（今日目标，非约访）",
              "agendaItems": ["5分钟｜开场与经营近况", "15分钟｜KYC核实", "20分钟｜产品方案", "10分钟｜下一步"],
              "deepDiveTopics": ["KYC探查完整问句1", "问句2"],
              "commitmentRequests": ["产品名：讨论角度"],
              "nextSteps": ["会后行动1", "会后行动2"],
              "closingSummary": "会末总结与双方行动"
            }
            只输出JSON，不要附加任何解释。
            """;
    }

    /**
     * 报告生成的系统提示
     * @param reportType 报告类型描述
     */
    public static String reportSystemPrompt(String reportType) {
        return String.format("""
            你是一位资深银行关系报告分析师，擅长撰写%s。
            根据提供的客户关系数据，生成专业的分析报告。
            输出必须是合法JSON，格式如下：
            {
              "summary": "报告摘要",
              "keyFindings": ["发现1", "发现2"],
              "riskIndicators": ["风险1", "风险2"],
              "opportunityIndicators": ["机会1", "机会2"],
              "recommendations": ["建议1", "建议2"],
              "actionItems": ["行动项1", "行动项2"]
            }
            只输出JSON，不要附加任何解释。
            """, reportType);
    }

    /**
     * 外联 user prompt：必须带渠道，任务是约访而非会面。
     */
    public static String outreachScriptUserPrompt(String customerName, String customerContext,
                                                   String kycGaps, String journeyStage,
                                                   String channelLabel) {
        return String.format("""
            任务：用【%s】渠道预约一次拜访，2分钟内说完。
            客户姓名: %s
            客户上下文: %s
            KYC缺口（见面再核实，外联不要展开）: %s
            旅程阶段: %s

            请只生成预约话术，不要生成会面议程或产品讲解。
            """, channelLabel, customerName, customerContext, kycGaps, journeyStage);
    }

    /**
     * 会面 user prompt：议程时长 + KYC 题 + 产品讨论。
     */
    public static String meetingScriptUserPrompt(String customerName, String customerContext,
                                                  String kycGaps, String journeyStage,
                                                  String productHints) {
        return String.format("""
            任务：生成已预约上门后的会面脚本（带时长议程）。
            客户姓名: %s
            客户上下文: %s
            须在会上核实的 KYC 缺口: %s
            候选产品（按此写讨论角度）: %s
            旅程阶段: %s

            请只生成会面议程、KYC 问句和产品讨论，不要生成电话/微信约访稿。
            """, customerName, customerContext, kycGaps, productHints, journeyStage);
    }

    /**
     * 构建报告生成的user prompt
     */
    public static String reportUserPrompt(String reportType, String operatingCaseId,
                                           String customerId, String contextSummary) {
        return String.format("""
            报告类型: %s
            经营案例ID: %s
            客户ID: %s
            上下文摘要: %s

            请根据以上信息生成%s。
            """, reportType, operatingCaseId, customerId, contextSummary, reportType);
    }
}
