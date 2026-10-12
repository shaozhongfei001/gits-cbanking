# PI-ARCH 未提交 WIP 盘点与还原记录 V1.0

> **编制**：Tech Lead｜**日期**：2026-09-14
> **触发**：Owner 指出「产品解读与知识」「产品推荐」在 2026-09-07 的真实状态均优于当前，要求盘点并改回
> **结论**：**Owner 正确。根因不是有人刻意改差，而是一整批未提交的工作区 WIP 在 2026-09-10 被 `git stash` 且从未回合并。**

---

## 1. 根因（对两个投诉同一解释）

| 时间 | 事件 |
|---|---|
| 09-01 | 提交 `96f01c8` / `11bd3d9`：产品推荐三段式工作区、发起链路（**纯文本框版**） |
| 09-04 | `PRODUCT_RECOMMENDATION_CONTRACT_REVIEW_2026-09-04.md`（合同复核） |
| 09-07 | PI-ARCH L10–L13 交付 + 交接（`HANDOFF-2026-09-07-PI-ARCH.md`）；独立 QA `REAL_E2E_PASS=YES` |
| 09-07～09-08 | **工作区里另有一批未提交 WIP**：产品推荐表单选项/默认值、商机字段对齐、产品解读目录页…… Owner 据此截图（现存 `evidence/p24-e2e/s1-product-knowledge/`、`s2-product-recommendation/`） |
| **09-10** | GK-KE L0 接管分支 → **整包 `git stash`**（`stash@{0}: PI-ARCH-L10-L13 WIP before GK-KE-L0`），工作树回落到"最后提交版" |
| 09-10 至今 | 该 WIP **从未回合并** |

**关键取证（证明它不在任何提交/分支）**：

```bash
# 表单选项 composable 在以下分支全部不存在：
for b in feature/PI-ARCH-L10-L13 feature/P30-gits-bank-experience-shell \
         feature/P24-dkws-supplychain main; do
  git cat-file -e "$b:frontend/src/composables/useRecommendationFormOptions.ts" && echo "有" || echo "$b 无"
done
# 结果：全部「无」⇒ 该能力只存在于工作区，从未落盘
```

⇒ 所以「回退后看起来变差」= **提交版（09-01/09-07）本来就弱**，Owner 记忆中的好版本是**未提交的 WIP**。

**为什么会误判**：前任 TL 在 09-07 曾把「30 页无数据/12 页接口失败」当故障上报，
**Owner 当场纠正：除产品解读外，其余业务场景在他接手前都是 OK 的**（见 `HANDOFF-2026-09-07-PI-ARCH.md` §0）。
本次我同样在首轮把该版判为"从未存在"，已被 Owner 纠正（见 `FAILURES.md` FAIL-2026-09-14-02）。

---

## 2. 盘点总表（差异 117 个文件）

stash 基线 `2934a9e` → HEAD `ca47192`。`Clean` = HEAD 自基线起未动过该文件（可安全把 stash 版前移）；
`DIRTY` = HEAD 已改动（**禁止用旧版覆盖**）。

| 业务场景 | 差异文件 | 还原状态 |
|---|---|---|
| **产品推荐**（发起表单默认值/选项 + 三段式面板 + 编排后端） | 前端 8 + 后端 14 | ✅ **已还原** |
| **需求与机会**（商机字段对齐后端 record） | 前端 5 | ✅ **已还原** |
| **产品解读与知识**（目录 + 产品卡 + 三视图） | 前端 4 + 后端 7 | ✅ **已还原** |
| **客户记录/全景**（含 V022/V023 种子） | 前端 5 + 后端 5 | ✅ **已还原** |
| **建议书** | 前端 3 + 后端 2 | ✅ **已还原** |
| **知识地图 / 知识卡** | 前端 2 + 后端 2 | ✅ **已还原** |
| **访前 / 互动 / 供应链 / 技能适配** | 后端 26 | ✅ **已还原** |
| **Claim / Evidence 中心**（`GET /engagement/claims` 404 的修复） | 后端 2 | ✅ **已还原** |
| **V14 集成**（DKWS → KERT 替换） | 1 新增 + **1 删除** | ✅ **已还原** |
| **`specs/product-knowledge/` 5 个合同** | 5 | ⛔ **未还原**（DIRTY，须**合同先行**合并） |

**合计：已还原 112 / 117；未还原 5。**

---

## 3. 还原提交

| 提交 | 内容 |
|---|---|
| `1bd4363` | 产品解读目录页最小完整集 + `FAIL-2026-09-14-02` 登记 |
| `3ae5f38` | 失败与教训登记 |
| `dd4f6d2` | 前端 34 个业务场景文件（含 `useRecommendationFormOptions.ts`） |
| `24a600f` | 后端 74 个业务场景文件 + 删除被取代的 `V14DkwsIntegrationController` |

分支：**`recover/PI-ARCH-product-catalog`**（`feature/GK-KE-L0-contract` 未动；`stash@{0}` 保留未 drop）。

---

## 4. 验证证据（实测，非推断）

| 项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | **exit 0，0 错误** |
| `./mvnw -pl apps/api -am compile/package` | **exit 0** |
| 启动 | `health=200`，无 Ambiguous mapping |
| `GET /api/v1/engagement/customer?rmId=ALL` | 200，6 条 |
| `GET /api/v1/opportunities` | 200，3 条 |
| `GET /api/v1/product-knowledge/recent?limit=50` | 200，12 条 |
| `GET /api/v1/product-knowledge/cards` | 200，**13 张卡**，`interpretable=true` **仅 `PROD-CM-001`** |
| `GET …/PROD-CM-001/interpretation?view=ELIGIBILITY` | 200，`minAccountBalance="50 万元"/SUPPORTED`，证据 `SRC-CM-001` / `第十条` |
| 浏览器截图 `/recommendation/new` | 客户下拉带默认值、经营案例下拉默认 **污水处理厂三期项目融资**、**需求多选带 2 条默认值**、产品域 **融资(3)/结算(2)/现金管理(2)/贸易金融(2)**、推荐目的默认、asOf 自动填充 |
| 发起链路（日志实测） | `createRun` → `SP-15` 打 KERT 8107 → `run succeeded, status=AWAITING_HUMAN` |

**还原前→后对照（产品推荐发起表单）**：

| 字段 | HEAD 版（弱） | 还原后（= 09-07） |
|---|---|---|
| 客户 | 无（文本框填 ID） | 下拉 + 默认值 |
| 经营案例 | 文本框填 ID | 下拉 + 默认值 + 动态提示 |
| 需求 | 无 | **多选列表 + 默认勾选** |
| 请求产品域 | 「逗号分隔」文本框 | **多选列表 + 默认勾选** |
| 推荐目的 | 手填 | 默认值 |
| asOf | 手填 | 自动填充 |

---

## 5. 未完成（明确归属）

| 项 | 原因 | 归属 |
|---|---|---|
| `specs/product-knowledge/` 5 个合同（`conflict-case` / `evidence-ref` / `field-policy` / `product-knowledge-changed` schema、`product-taxonomy.yaml`） | **DIRTY**：HEAD 在基线后已改过，**不得用旧版覆盖新版**，须**合同先行**逐一合并后 `make generate` / `make check` | Tech Lead |
| `make check`、`specs/product-knowledge/check_all.py` 等门禁 | 未跑（本轮只做编译 + 端到端实测） | 下一步 |
| 前端 vitest / 后端测试套件 | 未跑 | 下一步 |
| `PAGE_ID='P38'` 冲突（`KnowledgeMapView` 与 `ProductInterpretationView` 都声明 P38） | 待随 IA 变更一并解决 | 随 `GITS-Bank-产品解读与知识-需求变更方案-V1.0.md` |
| `stash@{0}` 处置（drop / 归档） | 待全部还原项确认后 | 待 Owner 确认 |

---

## 6. 长期纪律（写入约定）

1. **未提交 WIP 不得跨越"换分支"存活**：切分支前必须提交、或转专用分支、或落盘登记；**不得只留在 `stash`**。
2. **检索不得以"零命中"下"不存在"的结论**（数据串 ≠ 代码串；须查 stash / 悬挂提交 / 分支）。
3. **成果必须有索引**：`docs/pr/` 有 PR、`evidence/` 有截图，却无人据此回头核对是否真的落地 —— 本次即为反例。
