# GK14-l4-0-capability-closure｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-12T13:22:15.597172+00:00` |
| **holder** | `independent_qa` |
| **packet** | `GK14-l4-0-capability-closure` |
| **wave** | `W1` |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

## 待核验交付物（R-1/R-2/R-3 + WP02）

| 交付物 | 路径 |
|---|---|
| R-1 能力注册闭合 | `specs/knowledge-architecture/registry/Capability.json` |
| R-2 ID 全链映射 | `specs/knowledge-architecture/registry/CapabilityIdMapping.json` |
| WP02 行业方案包 | `specs/knowledge-architecture/industry/SIM-IND-MANUFACTURING.json` |
| 修复报告 | `docs/architecture/GK-KE-GK14-R1R2R3修复报告-V1.0.md` |

## 核验重点

1. `Capability.json` 中 **9 项 IMPLEMENTED*/DESIGN_ONLY 的 `callable` 是否全部为 false**，
   是否仅 `SIM-CAP-INTERPRET` 为 `true`（防止把"有代码"误读为"可运行"）。
2. `CapabilityIdMapping.json` 的 `summary.provenCompatible` 是否为 **0**，
   且 `forbiddenAssumptions` 10 条是否完整。
3. R-3 定性：是否已按"文档与代码不一致"（非僵尸注册）登记，
   证据行号（169 / 218 / 542 / 635）是否与 KERT 实际一致。
4. WP02 的 `comparisonToExisting` 是否覆盖全部 8 维，
   且结论是否明确写出"**不得认定两者等价**"。
5. `make check` 是否 PASS；`generated/` 与 `_registry.json` 是否**未被手改**。

短提示词：你是 `independent_qa`。读本 Loop 共享记忆与上述交付物，逐项独立核验并留证；
**不得复用 TL 的自检结论**；发现问题记入 `FAILURES.md` 后再判定。

---

## ⏳ 当前阻塞：等待 KERT 回函（R-3）

**状态**：`SIM-CAP-REPORT-ASSEMBLE` 的 `callable=false`，计划编译 `BLOCKED`，OC-04 不达标。

**在等什么**：KERT 维护方裁定 `skills.py` 中
「模块注释称 R1 拜访报告 2026-08-21 已下线」vs「代码四环可达」何者为准。
函件：`docs/architecture/GK-KE-致KERT维护方确认函-V1.0.md`

**怎么查进度**：
```bash
python3 scripts/gk_ke_kert_watch.py          # 与基线比对四信号
python3 scripts/gk_ke_kert_watch.py --snapshot  # 记录新基线
```

**四信号**：KERT HEAD / 未提交改动数 / `skills.py` sha256 / 疑似回函文件。
基线快照：`loops/GK14-l4-0-capability-closure/kert-watch-baseline.json`

**基线值（2026-09-12）**：HEAD `3b6640b`，未提交 464 项，`skills.py` mtime `2026-09-02`，无回函。

**三条纪律（不可违反）**：
1. **「无变化」不等于「未在处理」** —— 对方可能内部分析或在独立分支工作
2. **「沉默」不等于「同意」** —— 无回函则 `callable` 永久保持 `false`
3. **不把轮询结论当作 KERT 的进度声明**

**收到回函后**：
- 裁定「注释过时」→ 修正后重跑 `make probe-write` → 若转 `PASSED`，重跑 `make plan-compile` 应解除阻断
- 裁定「应下线」→ 该能力标不合格，评估替代路径；**不删 KERT 代码**
- 判定「暂缓/不回复」→ 如实标注，`callable` 保持 `false`

**监控机制文档**：`docs/architecture/GK-KE-KERT回函监控机制-V1.0.md`
