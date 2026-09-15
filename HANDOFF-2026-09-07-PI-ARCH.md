# 交接文档 · PI-ARCH-IMPLEMENTATION-01（CodeBuddy Tech Lead → 下一任）

- 交接时间：2026-09-07
- 交接人：CodeBuddy（Tech Lead / Feature Pilot / 修复波次）
- 接手起点：Owner 决议 **DECISION-20260906-01**（演示路径 C，L10–L13 授权）
- 两仓分支：`feature/PI-ARCH-L10-L13`（均已 push，**未合并**）

---

## 0. 最重要的一条：我留下的一处错误结论，已修正但请复核

我在收尾阶段用 Playwright 遍历了全部 51 条路由，产出
`docs/demo/GITS-BUSINESS-SCENARIO-CATALOG.md`，初版结论是"30 页渲染无数据、12 页接口失败"。

**这个结论是错的。** 我把两件事误判为故障：

1. **次要接口 4xx**（`/api/v1/engagement/claims`、`/kyc/{id}/gap-profile`）——页面主体照常渲染；
2. **写操作被禁用**（页面顶部写"原因：XXX 无本 Loop 合同 / 仅授权只读切片"）——这是 **P30 分支的红线设计**，不是 bug。

**Owner 已纠正**：客户经营旅程、客户建议书等**除产品解读外的业务场景，在我接手前均为 OK**。

抽样复核证据（P37 / P04 / P20 / P23 / P15）已写入清单顶部「结论修正」章节。

> **给下一任**：那份清单的逐页路径与依赖接口表仍可用；
> **但"✅/⚠️/❌"三档计数已作废，不要据此排期，也不要对外引用。**

---

## 1. 我接手后做了什么

### 1.1 主交付：产品解读链路 L10–L13

| Loop | 内容 | 状态 |
|---|---|---|
| **L10** | 3 份 DEMO 演示制度（`.DEMO.md`）入库 → 3 SourceVersion / 51 Fragment | PASS |
| **L11** | 29 EvidenceSpan + 14 FieldAssertion（11 CANDIDATE / 3 UNKNOWN） | PASS |
| **L12** | 冲突检测（内建 50万 vs 100万）+ 七字段体检 + 候选卡 | PASS |
| **L13** | Release `RLS-2026.09.06.1` **PUBLISHED** + 三视图投影 + 解读 API | PASS |
| **L14** | 前端解读演示页 + 业务场景剧本（新增范围） | PASS |

独立 QA 已签：**`REAL_E2E_PASS = YES`**（S1–S17 全 PASS，双实例真实 HTTP）。

### 1.2 关键设计决策（后续不得反向覆盖）

| 决策 | 内容 | 原因 |
|---|---|---|
| **DEMO 三道防冒充闸** | `.DEMO.md` 物理隔离 / front matter `provenance_state: DEMO` / 登记表 §5.8 单列统计 | 演示文本不得被当真实制度消费 |
| **真实缺口不抵扣** | DEMO 不计入权威区基数，真实材料缺口仍 **27/28** | F-L00-07 未解除，演示不替代 Owner 上传义务 |
| **INV-ASM-09** | SUPPORTED 可保留 `conflictId` 溯源，但冲突须 RESOLVED 且 `decisionId` 一致，证据集不得含被否决证据 | 清空会丢失"谁裁决了冲突"的审计信息 |
| **F-L13-01 路径 A** | 注册 `ASSET-KNOW-PRODUCT-RULES`，资产基线 20→21 | 不删依赖（掩盖缺口），也不擅自造资产内容 |
| **F-L13-07** | `/api/v1/product-knowledge` 基础路径 500 → 404 | 500 污染告警、误导调用方 |

### 1.3 修复的缺陷

| ID | 级别 | 内容 |
|---|---|---|
| F-L10-01 | MAJOR | `make check`/`generate` 失败：15 条合同 `generated` 目标缺失 + `yaml_taxonomy` 不支持 → **generate 转 PASS** |
| F-L13-02 | MAJOR | 快照目录不可达返回 404（应 503 FAILED_CLOSED）+ 补 Adapter 级测试 |
| F-L13-03 | MAJOR | `view`/`purpose` 未校验枚举（`view=BOGUS` 曾返 200） |
| F-L13-04 | MINOR | 缺参返回非统一错误体 |
| F-L13-05 | MINOR | 合同缺 400 响应与 `BAD_REQUEST` 码 |
| F-L13-06 | MINOR | 投影证据重复（9 条实为 4 个去重 ID） |
| F-L13-07 | MINOR | 基础路径 500 → 404 |
| F-L12-01/02 | MAJOR | `conflictType` 硬编码；ENUM 多源互补误判为冲突 |

### 1.4 合同变更（均已 `make generate`）

- `CTR-PK-EVS-002`：`INV-EVS-09/10/11`
- `CTR-PK-RLS-001`：`provenanceState` + `INV-RLS-09`
- `CTR-PK-ASM-001`：`INV-ASM-09`
- `CTR-PK-INT-001`：3.1.1 + 400 响应 + `BAD_REQUEST`
- V023 迁移候选：`provenance_state` 增 `DEMO`、`pk_rls_prov_ck`、`pk_rls_demo_ck`
- 主 OpenAPI：解读端点（paths 53→54）+ 4 schema
- 知识架构：新增 `assets/knowledge-rules/product-rules.md`

---

## 2. 环境与启动（下一任用得上）

```bash
# 后端（必须带 snapshot-dir，端口 8080 = 前端代理目标）
cd gits-cbanking
./mvnw -q -pl apps/api spring-boot:run -DskipTests \
  -Dspring-boot.run.arguments="--gits.product-knowledge.snapshot-dir=/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/04_serve/interpretation"

# 前端
cd frontend && npx vite --port 5173 --host

# 演示页
http://localhost:5173/product-knowledge/interpretation
```

**真实种子 ID**：客户 `CUST-CORP-0003`（RM-001 张明远）· 旅程 `a1b2c3d4-e5f6-7890-abcd-000000000003`
· 报告 `b1b2c3d4-e5f6-7890-abcd-000000000031`

**两个坑**：
1. 门禁脚本必须用 **`/usr/bin/python3`**（3.10.12，带 jsonschema 4.26.0）；
   用 workbuddy python 3.14 跑会全报"请先安装 jsonschema"
2. 后端测试 **968** 是跨模块聚合口径，`apps/api` 单模块约 585

---

## 3. 验证命令

```bash
# 统一门禁（11 门禁）
/usr/bin/python3 specs/product-knowledge/check_all.py     # 11/11
/usr/bin/python3 specs/product-knowledge/check_invariants.py   # 103/103（51 条）

# make check（首次全线绿灯）
make check                                                  # EXIT=0

# 后端
./mvnw -q -pl apps/api -am test -DskipITs                   # 968/0/0/4

# KERT（先切到 KERT 仓分支）
for g in check_registry_consistency check_l10_sources check_l11_spans \
         check_l12_conflicts check_l13_release; do python3 tools/$g.py; done
```

---

## 4. 提交清单

### gits-cbanking（分支 `feature/PI-ARCH-L10-L13`）
```
2ceb66d contract: DEMO 语义与解读合同登记，修复生成管线阻塞
5f062b0 feat: 产品解读只读 API（CTR-PK-INT-001）
ca5ed72 docs: L10–L13 证据台账、状态与交接
68d2782 fix: E2E 退办项修复（F-L13-02..06）
972756c docs: L13 E2E 退办项修复记录与复核数据
9c5be78 contract: O-L13-03 裁决为 INV-ASM-09；F-L13-01 登记 ADR
433a21d feat: 注册 ASSET-KNOW-PRODUCT-RULES（F-L13-01 路径 A）
be837c8 docs: 两仓 PR 描述与自检清单
7dec68d fix: 基础路径 500 → 404（F-L13-07）
d2d20da feat: 产品解读演示页与业务场景剧本（L14）
b77930f docs: GITS 全路由业务场景清单（判定有误，见 §0）
1d82bcd docs: 修正全路由清单结论
```

### Leibniz-KERT（同名分支）
```
d0d3df6 feat: L10 演示制度入库与 SourceVersion/Fragment
b46cd5c feat: L11 证据断言抽取 + L12 冲突检测与候选卡
5f3a2b8 feat: L13 Release 签发与三视图投影（DECISION-20260906-02）
0a3a51d fix: L13 投影证据去重（F-L13-06）
52d435c test: L12 门禁落地 INV-ASM-09
3b6640b feat: 规则包容器落地，rulePackageHash 改真实文件哈希
```

PR 描述：`docs/pr/PI-ARCH-L10-L13-PR.md`（**KERT 先合、GITS 后合**）

---

## 5. 遗留（都不是工程缺陷，是内容/授权类）

| 项 | 说明 | 谁 |
|---|---|---|
| F-L00-07 | 真实行内制度 **27/28** 未上传 → 演示结论为 DEMO 级 | Product/Risk Owner |
| OQ-C | 公开价目能否用于解读展示未裁决 → `pricing.serviceFee` 恒 UNKNOWN | Owner |
| 规则包 | `status=NOT_BUILT`，`rules=[]`；须产品管理部+风险部签署后转 BUILT | Owner |
| O-L13-02 | `attestedBy="OWNER"` 是会话级标识，**正式发布前须换自然人标识** | Owner |
| O-L10-02 | SourceVersion/Fragment 无 JSON Schema 合同（现以 V023 表列为真值） | Contract Owner |
| O-L13-03 | 是否要求 SUPPORTED 清空 `conflictId`（现由 INV-ASM-09 收敛） | Contract Owner |

---

## 6. 给下一任的三条建议

1. **别信那份清单的失败计数**（§0）。要看真实健康度，重新设计判定：以"页面是否渲染出业务数据"为准，
   把"写操作被禁"和"次要接口 404"归为信息项而非失败项。
2. **产品解读链路本身是完整可信的**：门禁 11/11、后端 968/0、E2E 全 PASS、Release 已发布、演示页可看。
   它只覆盖 P38「知识卡与产品适用边界」相关能力，**不覆盖其余业务场景**——其余场景按 Owner 说法本就 OK。
3. **未合并**：两仓分支都只 push 未 merge。要演示必须留在 `feature/PI-ARCH-L10-L13` 分支。

---

## 7. 关键文件索引

```
loops/L10-demo-authoritative-chain/      源/版本/片段 + 证据
loops/L11-evidence-span-assertion/       证据/断言
loops/L12-conflict-health-candidate/     冲突/体检/候选卡
loops/L13-release-interpretation-api/    Release + 解读 API + DECISION-20260906-02.md
loops/L14-interpretation-demo-ui/        演示页
docs/adr/ADR-PK-PRODUCT-RULES-ASSET.md   产品规则资产裁决
docs/pr/PI-ARCH-L10-L13-PR.md            两仓 PR 描述
docs/demo/GITS-BUSINESS-SCENARIO-CATALOG.md  全路由清单（判定已修正）
```
