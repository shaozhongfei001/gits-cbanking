# P21-production-readiness｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-08-19T02:45:00+08:00` |
| **holder** | `tech_lead` |
| **packet** | `P21-production-readiness` |
| **wave** | `independent_qa_attestation` |
| **do_not_start** | 冒充 Owner/QA、越界修改 scope 外文件、执行实际生产切换/写回 |

短提示词：你是 `independent_qa`。P21 生产就绪准备 6/6 实现 gate 已 PASS（actor=tech_lead）。执行 `make verify`（除 db-check 外部凭据环境依赖外全绿）+ 两个 P21 专属脚本，记录正式 QA PASS。移交 Owner 审查（不表示生产切换已执行）。
