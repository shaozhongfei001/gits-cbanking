# 附录 A：ContextPackage 与 ServiceResult 详细 Schema

> 关联主文档：`GITS-DKWS-SERVICE-PROPOSAL-INTEGRATION-DESIGN.md` §4

---

## A.1 ContextPackage 完整 Schema

GITS 后端组装、传递给 DKWS 的上下文包。

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://gien.gits/specs/schemas/context-package.schema.json",
  "title": "ContextPackage",
  "description": "GITS 传递给 DKWS 的服务建议书生成上下文",
  "type": "object",
  "required": ["schemaVersion", "customerId", "customerName", "industry", "engagementPhase", "journeyId", "operatingCaseId", "roundNumber", "enterpriseData", "proposalContext"],
  "properties": {
    "schemaVersion": {
      "type": "string",
      "const": "1.0.0"
    },
    "customerId": {
      "type": "string",
      "description": "客户ID",
      "pattern": "^CUST-"
    },
    "customerName": {
      "type": "string",
      "description": "客户名称"
    },
    "industry": {
      "type": "string",
      "description": "行业分类，格式：一级-二级，如'制造业-装备制造'",
      "examples": ["制造业-装备制造", "批发零售-大宗商品", "信息技术-软件开发"]
    },
    "engagementPhase": {
      "type": "string",
      "enum": ["PROSPECTING", "FIRST_CONTACT", "ACTIVE_ENGAGEMENT", "PROPOSAL_DELIVERED", "IMPLEMENTATION", "RETENTION"],
      "description": "客户经营阶段"
    },
    "journeyId": {
      "type": "string",
      "description": "旅程ID"
    },
    "operatingCaseId": {
      "type": "string",
      "description": "经营案例ID"
    },
    "roundNumber": {
      "type": "integer",
      "minimum": 1,
      "description": "迭代轮次"
    },

    "enterpriseData": {
      "type": "object",
      "description": "企业内数据",
      "properties": {
        "basicInfo": {
          "type": "object",
          "description": "企业基本信息",
          "properties": {
            "registeredCapital": { "type": "string" },
            "establishedDate": { "type": "string", "format": "date" },
            "legalRepresentative": { "type": "string" },
            "businessScope": { "type": "string" },
            "registeredAddress": { "type": "string" },
            "companyType": { "type": "string" },
            "stockListing": { "type": "string", "description": "上市情况：未上市/A股/H股/新三板" }
          }
        },
        "financialSummary": {
          "type": "object",
          "description": "财务摘要（最近3年）",
          "properties": {
            "revenue": { "type": "array", "items": { "type": "object" }, "description": "营业收入" },
            "netProfit": { "type": "array", "items": { "type": "object" }, "description": "净利润" },
            "totalAssets": { "type": "array", "items": { "type": "object" }, "description": "总资产" },
            "totalLiabilities": { "type": "array", "items": { "type": "object" }, "description": "总负债" },
            "operatingCashFlow": { "type": "array", "items": { "type": "object" }, "description": "经营性现金流" }
          }
        },
        "creditFacility": {
          "type": "object",
          "description": "授信额度信息",
          "properties": {
            "totalApproved": { "type": "number", "description": "已批总额（万元）" },
            "totalUsed": { "type": "number", "description": "已用额度（万元）" },
            "products": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "productName": { "type": "string" },
                  "approvedAmount": { "type": "number" },
                  "usedAmount": { "type": "number" },
                  "expiryDate": { "type": "string", "format": "date" }
                }
              }
            }
          }
        },
        "transactionSummary": {
          "type": "object",
          "description": "交易摘要",
          "properties": {
            "monthlyAvgVolume": { "type": "number", "description": "月均交易量（万元）" },
            "mainTransactionTypes": { "type": "array", "items": { "type": "string" } },
            "settlementMethods": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    },

    "publicData": {
      "type": "object",
      "description": "公开行业/产业数据",
      "properties": {
        "industryReports": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": { "type": "string" },
              "source": { "type": "string" },
              "date": { "type": "string", "format": "date" },
              "keyFindings": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "newsEvents": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": { "type": "string" },
              "source": { "type": "string" },
              "date": { "type": "string", "format": "date" },
              "summary": { "type": "string" }
            }
          }
        },
        "regulatoryChanges": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": { "type": "string" },
              "authority": { "type": "string" },
              "effectiveDate": { "type": "string", "format": "date" },
              "impact": { "type": "string" }
            }
          }
        }
      }
    },

    "interactionHistory": {
      "type": "array",
      "description": "交互历史纪要",
      "items": {
        "type": "object",
        "required": ["interactionId", "date", "type", "summary"],
        "properties": {
          "interactionId": { "type": "string" },
          "date": { "type": "string", "format": "date" },
          "type": {
            "type": "string",
            "enum": ["FACE_TO_FACE", "PHONE", "WECHAT", "EMAIL", "VIDEO_CONFERENCE"]
          },
          "summary": { "type": "string" },
          "keyFindings": { "type": "array", "items": { "type": "string" } },
          "participants": { "type": "array", "items": { "type": "string" } }
        }
      }
    },

    "interactionMemory": {
      "type": "array",
      "description": "结构化交互记忆（阶段二才有）",
      "items": {
        "type": "object",
        "required": ["memoryId", "category", "content", "confidence", "validFrom", "status"],
        "properties": {
          "memoryId": { "type": "string", "pattern": "^MEM-" },
          "category": {
            "type": "string",
            "enum": ["PREFERENCE", "DECISION_PATTERN", "RELATIONSHIP", "BUSINESS_SIGNAL", "EMOTIONAL_STATE"]
          },
          "content": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "validFrom": { "type": "string", "format": "date" },
          "validUntil": { "type": "string", "format": "date" },
          "decayRule": { "type": "string", "enum": ["NONE", "LINEAR", "STEP"] },
          "status": { "type": "string", "enum": ["CANDIDATE", "CONFIRMED", "EXPIRED", "SUPERSEDED"] }
        }
      }
    },

    "evidence": {
      "type": "array",
      "description": "已有证据列表",
      "items": {
        "type": "object",
        "required": ["evidenceId", "type", "source", "content", "status", "factLabel"],
        "properties": {
          "evidenceId": { "type": "string", "pattern": "^EVID-" },
          "type": { "type": "string", "enum": ["PUBLIC_DATA", "ENTERPRISE_DATA", "INTERACTION_DERIVED", "EXPERT_INPUT"] },
          "source": { "type": "string" },
          "date": { "type": "string", "format": "date" },
          "content": { "type": "string" },
          "status": { "type": "string", "enum": ["CANDIDATE", "CONFIRMED", "CONFLICTING"] },
          "factLabel": { "type": "string", "enum": ["F", "C", "B", "H", "P", "A"] }
        }
      }
    },

    "proposalContext": {
      "type": "object",
      "required": ["proposalType", "gateStatus"],
      "properties": {
        "proposalType": {
          "type": "string",
          "enum": ["INITIAL", "UPDATE"],
          "description": "INITIAL=首次生成，UPDATE=基于交互记忆更新"
        },
        "existingProposalVersion": {
          "type": ["string", "null"],
          "description": "已有建议书版本ID（更新时必填）"
        },
        "gateStatus": {
          "type": "object",
          "properties": {
            "G0": { "$ref": "#/$defs/gateState" },
            "G1": { "$ref": "#/$defs/gateState" },
            "G2": { "$ref": "#/$defs/gateState" },
            "G3": { "$ref": "#/$defs/gateState" },
            "G4": { "$ref": "#/$defs/gateState" },
            "G5": { "$ref": "#/$defs/gateState" }
          }
        }
      }
    }
  },

  "$defs": {
    "gateState": {
      "type": "string",
      "enum": ["PENDING", "READY_FOR_REVIEW", "PASSED", "BLOCKED"]
    }
  }
}
```

---

## A.2 ServiceResult 完整 Schema

DKWS 返回给 GITS 的服务建议书生成结果。

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://gien.gits/specs/schemas/proposal-service-result.schema.json",
  "title": "ProposalServiceResult",
  "description": "DKWS SP-20 返回的服务建议书生成结果",
  "type": "object",
  "required": ["schemaVersion", "skillId", "runId", "status", "timestamp", "content", "citations", "unknowns", "limitations", "gateRecommendations"],
  "properties": {
    "schemaVersion": { "type": "string", "const": "1.0.0" },
    "skillId": { "type": "string", "const": "SP-20" },
    "runId": { "type": "string", "description": "DKWS 运行ID，格式 RUN-YYYYMMDD-NNN" },
    "status": { "type": "string", "enum": ["SUCCESS", "PARTIAL", "FAILED"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "errorMessage": { "type": "string", "description": "仅 FAILED 时" },

    "content": {
      "type": "object",
      "required": ["proposalDraft", "internalVersion"],
      "properties": {
        "proposalDraft": {
          "type": "string",
          "description": "建议书正文（Markdown 格式），8大章节 + 5张配套表"
        },
        "internalVersion": {
          "type": "object",
          "required": ["content", "factLabels"],
          "properties": {
            "content": {
              "type": "string",
              "description": "内部版正文（含假设、风险红旗、内部判断）"
            },
            "factLabels": {
              "type": "object",
              "description": "事实标签映射：断言文本 → 标签",
              "additionalProperties": {
                "type": "string",
                "enum": ["F", "C", "B", "H", "P", "A"]
              }
            }
          }
        },
        "customerVersion": {
          "type": ["object", "null"],
          "description": "对客版（仅 G1+G2+G3 完成后生成）",
          "properties": {
            "content": { "type": "string" },
            "filteringNotes": {
              "type": "array",
              "items": { "type": "string" },
              "description": "过滤说明：哪些内容被移除及原因"
            }
          }
        },
        "customerVersionNote": {
          "type": "string",
          "description": "对客版未生成时的说明"
        }
      }
    },

    "citations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "claim", "source", "date", "factLabel"],
        "properties": {
          "id": { "type": "string", "pattern": "^CIT-" },
          "claim": { "type": "string", "description": "断言内容" },
          "source": { "type": "string", "description": "来源" },
          "date": { "type": "string", "format": "date", "description": "来源日期" },
          "factLabel": { "type": "string", "enum": ["F", "C", "B", "H", "P", "A"] },
          "chapterRef": { "type": "string", "description": "所在章节引用，如 CH02" }
        }
      }
    },

    "unknowns": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "description", "suggestedAction"],
        "properties": {
          "id": { "type": "string", "pattern": "^UNK-" },
          "description": { "type": "string" },
          "suggestedAction": { "type": "string", "description": "建议获取方式" },
          "relatedChapter": { "type": "string" }
        }
      }
    },

    "limitations": {
      "type": "array",
      "items": { "type": "string" }
    },

    "gateRecommendations": {
      "type": "object",
      "required": ["currentGate", "nextGate"],
      "properties": {
        "currentGate": { "type": "string", "enum": ["G0", "G1", "G2", "G3", "G4", "G5"] },
        "currentGateStatus": { "type": "string", "enum": ["PENDING", "READY_FOR_REVIEW", "PASSED", "BLOCKED"] },
        "checklist": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["item", "status"],
            "properties": {
              "item": { "type": "string", "description": "检查项" },
              "status": { "type": "string", "enum": ["PASS", "PARTIAL", "FAIL", "NOT_APPLICABLE"] },
              "detail": { "type": "string" }
            }
          }
        },
        "nextGate": { "type": "string", "enum": ["G0", "G1", "G2", "G3", "G4", "G5", "COMPLETE"] },
        "nextGatePrerequisites": { "type": "string", "description": "推进到下一闸门的前置条件" }
      }
    }
  }
}
```

---

## A.3 五层工作区文件布局

DKWS 端建议书相关的文件布局：

```
01_raw/
  └── {customerId}/
      └── proposal/
          ├── context-package.json          ← GITS 传入的 ContextPackage
          └── source-evidence/             ← 原始证据文件
              ├── EVID-001.json
              └── ...

02_work/
  └── {customerId}/
      └── proposal/
          ├── run-{runId}/
          │   ├── draft-v{version}.md      ← 建议书草稿（内部版）
          │   ├── draft-v{version}.frontmatter.yaml
          │   ├── citations.json           ← 引用索引
          │   ├── unknowns.json            ← 未知项
          │   ├── gate-checklist.json      ← 闸门检查清单
          │   └── llm-trace.json           ← LLM 生成追踪
          └── ...

03_core/
  └── {customerId}/
      └── proposal/
          ├── v1.0.0.md                    ← 发布版建议书（不可变）
          ├── v1.0.0.frontmatter.yaml
          ├── v1.1.0.md                    ← 更新版
          ├── v1.1.0.frontmatter.yaml
          └── templates/                   ← 建议书模板
              ├── ch01-enterprise-overview.md
              ├── ch02-industry-analysis.md
              ├── ch03-financial-analysis.md
              ├── ch04-risk-analysis.md
              ├── ch05-need-identification.md
              ├── ch06-service-design.md
              ├── ch07-product-recommendation.md
              ├── ch08-implementation-path.md
              ├── apx-a-customer-info-table.md
              ├── apx-b-industry-analysis-table.md
              ├── apx-c-need-solution-product-mapping.md
              ├── apx-d-expert-collaboration.md
              └── apx-e-implementation-plan.md

04_serve/
  └── {customerId}/
      └── proposal/
          ├── v1.0.0-customer.md           ← 对客版（脱敏+合规过滤）
          ├── v1.0.0-customer.frontmatter.yaml
          └── filtering-report.json        ← 过滤报告

90_control/
  └── {customerId}/
      └── proposal/
          ├── gate-g0-evidence-preparation.json
          ├── gate-g1-customer-verification.json
          ├── gate-g2-expert-design.json
          ├── gate-g3-internal-approval.json
          ├── gate-g4-customer-confirmation.json
          ├── gate-g5-implementation-review.json
          └── audit-log.jsonl              ← 审计日志（追加写入）
```
