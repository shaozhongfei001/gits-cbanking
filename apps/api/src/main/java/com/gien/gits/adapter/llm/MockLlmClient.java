package com.gien.gits.adapter.llm;

import com.gien.gits.api.metrics.BusinessMetrics;
import com.gien.gits.engagement.port.LlmClient;
import com.gien.gits.engagement.port.LlmClientException;

import java.util.UUID;

/**
 * Mock LLM客户端 — 根据systemPrompt关键词返回预定义的结构化JSON。
 * 用于开发和测试环境，模拟50-200ms延迟。
 * P11 G5/G6: 增加外联脚本、会面脚本、报告生成的场景识别
 */
public class MockLlmClient implements LlmClient {

    private final BusinessMetrics businessMetrics;

    public MockLlmClient(BusinessMetrics businessMetrics) {
        this.businessMetrics = businessMetrics;
    }

    @Override
    public String complete(String systemPrompt, String userPrompt) {
        // 模拟网络延迟 50-200ms
        try {
            Thread.sleep(50 + (long) (Math.random() * 150));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new LlmClientException("Mock LLM interrupted", e);
        }

        if (systemPrompt == null || userPrompt == null) {
            throw new LlmClientException("systemPrompt and userPrompt must not be null");
        }

        String promptLower = systemPrompt.toLowerCase();
        String response;

        // 语义提取场景: 返回包含patterns数组的JSON
        if (promptLower.contains("语义") || promptLower.contains("pattern")
                || promptLower.contains("提取") || promptLower.contains("extract")) {
            response = buildSemanticExtractionResponse(userPrompt);
        }
        // 外联脚本场景: 返回外联脚本结构化JSON
        else if (promptLower.contains("外联") || promptLower.contains("outreach")) {
            response = buildOutreachScriptResponse();
        }
        // 会面脚本场景: 返回会面脚本结构化JSON
        else if (promptLower.contains("会面") || promptLower.contains("meeting")) {
            response = buildMeetingScriptResponse();
        }
        // 报告生成场景: 返回报告结构化JSON
        else if (promptLower.contains("报告") || promptLower.contains("report")
                || promptLower.contains("分析师")) {
            response = buildReportResponse();
        }
        // 知识地图驱动访前场景 (P23): systemPrompt 含"知识地图/访前分析"，返回知识驱动 JSON
        else if (promptLower.contains("知识地图") || promptLower.contains("knowledge map")
                || promptLower.contains("访前分析") || promptLower.contains("previsit")) {
            response = buildKnowledgeDrivenPrevisitResponse(userPrompt);
        }
        // 脚本生成场景(通用): 返回包含content字段的JSON
        else if (promptLower.contains("脚本") || promptLower.contains("script")
                || promptLower.contains("生成") || promptLower.contains("generate")) {
            response = buildScriptGenerationResponse(userPrompt);
        }
        // 通用场景: 返回简单确认
        else {
            response = buildGenericResponse(userPrompt);
        }

        businessMetrics.recordLlmCall("mock", "success");
        return response;
    }

    private String buildSemanticExtractionResponse(String userPrompt) {
        String id1 = "EXT-" + UUID.randomUUID().toString().substring(0, 8);
        String id2 = "EXT-" + UUID.randomUUID().toString().substring(0, 8);
        return """
                {
                  "patterns": [
                    {
                      "objectId": "%s",
                      "type": "OPPORTUNITY_SIGNAL",
                      "claimType": "FINANCING_NEED",
                      "content": "客户提及融资需求",
                      "speaker": "客户方",
                      "evidenceRef": "TR-RAW",
                      "status": "DETECTED",
                      "confidence": 0.75,
                      "notFact": true,
                      "requiresReconciliation": true,
                      "conflictWith": null,
                      "nextQuestion": "确认融资需求的具体金额和用途"
                    },
                    {
                      "objectId": "%s",
                      "type": "CUSTOMER_COMMITMENT",
                      "claimType": "MATERIAL_PROVIDE",
                      "content": "客户表示将提供相关材料",
                      "speaker": "客户方",
                      "evidenceRef": "TR-RAW",
                      "status": "DETECTED",
                      "confidence": 0.80,
                      "notFact": false,
                      "requiresReconciliation": false,
                      "conflictWith": null,
                      "nextQuestion": "确认材料清单和提交时间"
                    }
                  ]
                }""".formatted(id1, id2);
    }

    private String buildOutreachScriptResponse() {
        return """
                {
                  "greeting": "张总您好，我是杭州分行客户经理张伟，打扰您两分钟。",
                  "purposeStatement": "想预约本周四下午到贵司当面沟通智能制造二期，大约四十分钟。",
                  "keyTopics": ["确认周四或周五下午是否方便", "到访只需财务或经营负责人一位"],
                  "proposedActions": ["对方确认时段后发日历邀请"],
                  "closingStatement": "您看周四还是周五更合适？我按您的时间上门。",
                  "toneGuidance": "电话：短、敬、只约时间"
                }""";
    }

    private String buildMeetingScriptResponse() {
        return """
                {
                  "opening": "张总您好，今天按约定来当面过三件事：经营近况、KYC缺口、供应链融资方案。",
                  "agendaItems": ["5分钟｜开场与经营近况", "15分钟｜KYC信息核实", "25分钟｜供应链融资方案", "10分钟｜下一步与材料清单"],
                  "deepDiveTopics": ["实际控制人近12个月是否变更？", "近两季营收与订单能提供哪些可核验材料？"],
                  "commitmentRequests": ["供应链融资：从应付账期与上游集中度切入，先问需求再谈产品"],
                  "nextSteps": ["会后整理纪要", "按缺口清单补材料"],
                  "closingSummary": "确认融资意向与KYC补件清单，一周内给方案草稿。"
                }""";
    }

    private String buildReportResponse() {
        return """
                {
                  "summary": "客户关系整体稳定，存在融资需求和KYC信息缺口，建议加强跟进。",
                  "keyFindings": ["客户提及融资需求", "KYC信息存在2项缺口", "风险等级无变化"],
                  "riskIndicators": ["中风险客户，需关注经营数据变化"],
                  "opportunityIndicators": ["融资需求信号置信度较高", "产品交叉销售机会"],
                  "recommendations": ["尽快补全KYC信息", "推进融资方案", "安排下次拜访"],
                  "actionItems": ["更新KYC档案", "准备融资方案", "录入承诺事项"]
                }""";
    }

    private String buildScriptGenerationResponse(String userPrompt) {
        return """
                {
                  "content": "尊敬的客户您好，感谢您对我们银行的支持。根据您的业务发展需求，我们为您准备了以下方案建议...",
                  "metadata": {
                    "model": "mock-llm",
                    "generatedAt": "%s"
                  }
                }""".formatted(java.time.Instant.now().toString());
    }

    private String buildKnowledgeDrivenPrevisitResponse(String userPrompt) {
        // 从 userPrompt 提取知识地图/业务上下文片段，体现 LLM 消费知识地图
        String hint = "基于知识地图";
        if (userPrompt != null && userPrompt.contains("KI-009")) {
            hint = "已读取知识地图（KI-009 客户基础 + KI-FRONT-001~006），基于权威知识条目生成";
        }
        return """
                {
                  "visitStrategy": "%s：先补全KYC未知项，再围绕设备采购融资确认授信需求与主体，避免直接推销。",
                  "keyQuestions": ["确认Q3设备采购预算的真实用途与融资期限", "核实是否纳入现有授信主体", "了解近一年经营现金流变化"],
                  "riskReminders": ["不得承诺授信额度（禁令#3）", "客户表达需语义消歧后再认定事实"]
                }""".formatted(hint);
    }

    private String buildGenericResponse(String userPrompt) {
        return """
                {
                  "response": "Mock LLM response for the given prompt.",
                  "model": "mock-llm"
                }""";
    }
}
