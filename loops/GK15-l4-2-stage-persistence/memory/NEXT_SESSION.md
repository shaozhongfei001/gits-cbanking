# GK15-l4-2-stage-persistence｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-12T17:39:12.920891+00:00` |
| **holder** | `tech_lead` |
| **packet** | `GK15-l4-2-stage-persistence` |
| **wave** | `W1` |
| **do_not_start** | REAL_E2E_PASS、BUSINESS_SIGNED |

## 待核验交付物

| 交付物 | 路径 |
|---|---|
| 阶段持久化实现 | KERT `src/kert/infrastructure/stage_store.py` |
| 测试 | KERT `tests/integration/test_stage_store.py`（13 项） |
| 处理报告 | `docs/architecture/GK-KE-三项外部条件处理报告-V1.0.md` |

## 核验重点

1. **承重不变量**：P13 证据变更使 P14 确认失效 —— 三种强制方式是否都真实生效
2. **第三种方式**（摘要值不一致即判无效）尤其在"绕过失效流程"时是否仍能拦截
3. 阶段**不可跳跃**（P12→P14 应被拒）
4. **未做 UI** —— 本轮仅为持久化与不变量，是否与声明一致

短提示词：你是 `independent_qa`。读本 Loop 共享记忆与上述交付物，逐项独立核验并留证；
不得复用 TL 的自检结论；建议做**破坏性验证**（如移除摘要比对，看是否仍能拦截过期确认）。
