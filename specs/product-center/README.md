# 对公产品中心 · PC0 契约与治理设计（CTR-PKC-API-001 / CTR-PKC-DOM-001）

> Loop：`PC0-product-center-baseline`｜工作流：`REQ-PI-01`｜状态：`CANDIDATE / FROZEN=NO`
> 权威输入：`docs/dispatch/PI-ROUND1-需求准入与影响分析-V1.0.md`（含 Owner 决策登记 §11）
> 本文件是合同源 `specs/product-center/*.json` 的治理说明，不是实现文档。
>
> **目录范围（Owner 澄清 OD-PI-12，2026-09-21）**：本中心覆盖受控分类法**全部产品**（当前 13 产品 / 6 族），
> 法人账户透支仅是第一个 8 章完整参考实现，不是范围边界。其余产品数据补齐前，页面必须诚实显示
> 完整度缺口（PkcCoverage.gaps + PENDING_VERIFICATION / NO_PUBLISHED_VERSION），禁止占位数据冒充已核验。
> 目录扩容（新增产品/族）走 `CTR-PK-TAX-001` 合同变更，不在本合同内擅自扩展。

## 1. 复用映射（禁止平行模型）

| 需求对象 | PC0 处置 | 依据 |
|---|---|---|
| ProductFamily / 分类法 | **复用 `CTR-PK-TAX-001`**（3 域/7 族/13 产品），不另建分类；法人账户透支= `PROD-CM-003`（CASH_MANAGEMENT） | OD-PI-04 |
| EvidenceRef | 新契约内声明 `x-aligned-contract: CTR-PK-EVR-001`，字段逐项对齐，消费方落库时映射既有表 | 需求 06 §3 |
| Release / 版本发布态 | **复用 `CTR-PK-RLS-001`**（KERT 侧运行态）；GITS 侧治理态 `VersionStatus`（DRAFT→…→RETIRED）仅描述知识治理生命周期，二者经 `evidenceSnapshotId` 关联 | C-04 |
| 产品解读三视图 | **不改 `CTR-PK-INT-001`**（P38 冻结）；产品中心独立 `/product-center/**` 命名空间 | OD-PI-01 |
| 产品编号 | `product_id` 沿用 `^PROD-[A-Z]+-[0-9]{3}$`；DEMO 前缀只落 `productCode` | OD-PI-05 |
| Skill/知识源 | 沿用 `dsh.*` fail-closed（源不可达 → 503 FAILED_CLOSED，禁止本地补数） | 既有适配器 |

## 2. 端点清单（15 operation）

`listProductCenterFamilies` · `listProductCenterProducts` · `getProductCenterDetail` · `getProductCenterSection` · `searchProductCenterKnowledge` · `listProductCenterProductVersions` · `getProductCenterVersionDiff` · `getProductCenterCoverage` · `putProductCenterFavorite` / `deleteProductCenterFavorite` · `downloadProductCenterInternalNote` · `generateProductCenterOutline` · `askProductCenterAssistant` · `locateProductCenterEvidence` · `createProductCenterFeedback`

实现顺序建议：目录+详情+章节（PC1）→ 搜索/版本/完整度（PC2–PC4）→ 收藏/下载/提纲/助手/反馈（PC5）。

## 3. 错误码 → HTTP → 前端处置（T0-8）

| code | HTTP | 语义 | 前端处置（不得统一显示"暂无数据"） |
|---|---|---|---|
| `BAD_REQUEST` | 400 | 参数错误 | 表单级提示 |
| `PRODUCT_ACCESS_DENIED` | 403 | 无权产品 | 受控无权限页（不泄漏名称/摘要/数量，AT-010） |
| `EVIDENCE_ACCESS_DENIED` | 403 | 无权证据 | 只显示受控元数据（AT-023） |
| `PRODUCT_NOT_FOUND` | 404 | 产品不存在 | 返回目录入口 |
| `NO_PUBLISHED_VERSION` | 404 | 无有效发布版本 | "暂无有效发布版本"+责任人/返回入口（AT-009），不展示草稿 |
| `EVIDENCE_NOT_FOUND` | 404 | 证据缺失 | 显示缺口与维护责任人（AT-024） |
| `VERSION_CONFLICT` | 409 | 版本/证据冲突未决 | 显示冲突状态与责任人，AI 不裁决（AT-029） |
| `VERSION_EXPIRED` | 409 | 版本/证据已失效 | 显示失效原因与替代版本入口（AT-028） |
| `EVIDENCE_EXPIRED` | 409 | 价目/条款证据过期 | 风险状态提示，限制生成（AT-051） |
| `GENERATION_UNAVAILABLE` | 503 | 提纲/助手不可用 | 保留输入与重试；核心页面不受影响（AT-070/077） |
| `ANSWER_WITHOUT_EVIDENCE` | 200+refused | 助手无证据 | 明确"当前版本未找到依据"，不编造编号（AT-067） |
| `DOWNLOAD_FAILED` | 503 | 下载失败 | 可恢复重试 + 维护入口 |
| `SEARCH_TIMEOUT` | 503 | 搜索超时 | 已打开产品页保持可用（AT-005） |

## 4. DEMO 与生产隔离（T0-7，`PI-OI-015` 受控方案）

1. **字段层**：`environment ∈ {DEMO,UAT,PROD}` + `isDemo`；DEMO 证据编号（`DEMO-*`）必须 `evidenceClass=SAMPLE_EVIDENCE && isDemo=true`。
2. **服务端**：`gits.product-center.demo-visible=false`（生产默认）时，目录/搜索/详情/助手一律过滤 `isDemo=true` 对象——过滤在服务端，前端隐藏不算数（AT-065）。
3. **发布阻断**：`isDemo=true` 的对象进入 `environment=PROD` 的版本 → 发布校验失败（需求 03 §8-5）。
4. **前端**：环境条 + 页脚强制声明；`DEMO` 字样不得被配置关闭（PI-FR-001/003/093）。
5. **实现归属**：PC5（下载/生成/助手/审计波）连同服务端过滤一起落地并配负例测试。

## 5. 权限决策点（T0-10，现状=仅 API Key，RBAC 待 `PI-OI-014`/身份服务）

| 决策点 | 服务端必须过滤的维度 | 涉及端点 |
|---|---|---|
| 产品可见性 | 产品 × 机构/角色 | families / products / detail / search |
| 证据可见性 | `accessLevel`（PUBLIC/RM_INTERNAL/SENSITIVE_INTERNAL） | detail/sections/evidence locate/search |
| 价格分级 | `PricingItem.disclosureLevel` | detail/sections/outline/assistant |
| 历史版本 | 变更摘要 vs 全文 | versions / diff |
| 助手 | 可用知识集合 ≤ 直接浏览权限（防提示注入，AT-069） | assistant |

约束：**前端隐藏不作为权限证据**；搜索、导出、助手必须走同一过滤规则（PI-FR-067/089）。

## 6. 搜索片段脱敏（`PI-OI-014` 受控默认）

返回有权限的受控片段；`accessLevel≠PUBLIC` 的证据命中只回元数据（`snippet=null`）；无权内容不返回名称/片段/数量（AT-004）。

## 6.5 比较章节的数据来源与红线（Owner 2026-09-21 决定 B + 造数授权）

比较章节（`PkcComparisonSet` / `COMPARE`）的数据来源**只有三类，且必须逐行标注来源类型**：

| 来源 | 允许程度 | 页面标注 | 硬约束 |
|---|---|---|---|
| **A 本行产品间**（13 张产品卡的前置/互斥/配套） | **主体数据 = 本中心内的权威**（内容为 SIM 授权造数，**不等于**银行正式制度） | 无需特殊标注 | 实例权威在产品卡（WP1.3） |
| **B 公开参考（非权威）** | 允许（Owner 已豁免**只读展示口径**，仅内部） | 「公开参考（非权威）」（**单一标签**；不再逐行标"来源未验证"） | 使用**脱敏代称**；**不得**作本行产品卡字段的权威依据；**不得**把其 `evidenceRef` 写入任何产品卡字段链（这是门禁阻断的唯一触发条件；**只读对比本身不构成"引用"**，Owner 2026-09-22 纠正）；**不得对客** |
| **SIM 同业对照（造数）** | 允许（Owner 授权） | 「同业示例（SIM）」 | `simulationOnly=true`+`isDemo=true`+`evidenceClass=SAMPLE_EVIDENCE`；脱敏代称；价格维度不放造数数字；经产品经理+合规确认后启用 |

**门禁负例（PC4 门禁必测，缺一即 FAIL）**：① 对比行缺来源标签或 SIM 行缺 `simulationOnly`；② 出现真实机构名（未用脱敏代称）；③ 价格维度出现造数数字；④ 造数数据参与 `READY` 类判定；⑤ 公开参考行的 `evidenceRef` 进入产品卡字段链；⑥ 本页被复用于对客交付。
决定登记与边界见 `docs/architecture/ONTO1-SCENARIO-PI-Owner决定登记-V1.0.md` §1（含 2026-09-22 口径纠正）。

## 7. 数据落库（T0-6 决策：**落地推迟至 PC2**）

`specs/product-knowledge/migration-candidates/*/V023__product_knowledge_objects.sql`（12 张 `pk_*` 表）经评估：只覆盖**证据链**（source/span/assertion/conflict/release），**不覆盖**本需求 18 对象中的条款/材料/价格/协议/FAQ 等业务对象。现在落地会形成"表已建齐"的假象并诱发漂移。
决定：PC2 实现核心条款时，把 12 张候选表（改版号 V024+，H2/MySQL 双方言同步）与业务对象表**一并设计落地**，随写路径与读路径同测。本决定已记录 Loop 记忆。

## 8. 消费者测试与变异复验（T0-11）

`scripts/pkc_contract_tests.py`：fail-closed + 单一真值函数 `detect()` + `--self-test` 注入 6 类已知故障（响应 $ref 丢失 / ComparisonSet 放开 additionalProperties / 枚举删态 / productId 正则改写 / 审计事件删除 / 登记项删除），全部必须被捕获。
FAIL-2026-09-20-01（检测器未解析响应级 `$ref`）已按"先记账再修"闭环：原命令重跑 baseline 干净、6/6 变异被捕获。

## 9. 确定性状态映射（OD-PI-03 受控假设，Owner 背书前不得进 PC2）

`SUPPORTED→VERIFIED`、`UNKNOWN→PENDING_VERIFICATION`、`CONFLICT→CONFLICTING`、`STALE→EXPIRED`、`NOT_APPLICABLE→NOT_APPLICABLE`（新增第 7 态承接既有语义）；`APPROVAL_VARIABLE`/`PRICING_VARIABLE` 仅由受控知识版本写入。P38 消费的既有 5 态枚举不改。
