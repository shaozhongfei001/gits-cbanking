# 交接 —— 2026-09-15 gits-cbanking E2E 收口（G-1）

```text
STATUS=HANDOFF（快照；事实核对与实测于 2026-09-15）
SCOPE=gits-cbanking 的 E2E Tests job（G-1）+ 该 job 判定口径
BRANCH=feature/GK-KE-L0-contract
HEAD=f665e9b（= origin/feature/GK-KE-L0-contract，已独立核对）
SUPERSEDES=Leibniz-KERT:evidence/kert-e2e-ci/HANDOFF-2026-09-15.md §3-G1 的归因
```

---

## 0. 一句话结论

- **G-1 已修复**，但**不是原因的原来那个原因**：E2E job 的红是**用例期望漂移**（导航标签改名未同步），
  **不是**"job 没有启动后端"。原始归因已被实测推翻（§2）。
- 顺带把该 job 的判定从**恒真空转**改成 **fail-closed**（§3）：原判定在任何情况下都会 PASS。
- **已实跑验证**：推送后 CI 两轮均 **10/10 job success**（§5）。

---

## 1. 修复内容（提交）

| 提交 | 内容 |
|---|---|
| `57b8bd3` | `fix(e2e)`：同步 P30 侧边栏导航期望（`证据与知识` → `产品解读与知识`，并补 `产品推荐`） |
| `f665e9b` | `ci(e2e)`：`Verify E2E tests actually ran` 改为 fail-closed 计数；`report.spec.ts` 补 mock 消除误导性代理错误 |

改动文件（5 个，均为显式 `git add`）：

```
.github/workflows/ci.yml                     # 判定步骤改为调用守卫脚本
frontend/e2e/experience-shell.spec.ts        # 期望清单同步 navConfig
frontend/e2e/report.spec.ts                  # 补 installApiMocks（去掉代理噪声）
frontend/playwright.config.ts                # 无条件产出 html + json 报告
frontend/scripts/check-e2e-ran.mjs           # 新增 fail-closed 守卫
```

---

## 2. 归因更正：G-1 的真实原因

### 2.1 原归因（**已推翻**）

> "该 job 只启动了前端 vite，**没有启动任何后端** → 代理目标 `127.0.0.1:8080` 无人监听
> → 页面渲染不出 → 断言失败。"

### 2.2 真相

失败的用例是 **`e2e/experience-shell.spec.ts:5`**，它在 `page.goto` 之前调用
`installApiMocks(page)`（Playwright **浏览器级路由 mock**，见 `e2e/sit-fixtures.ts`）。
套件**按设计不需要后端**：真实后端用例是 `*.live.spec.ts`，由**另一个配置**
`frontend/playwright.live.config.ts` 运行，而默认 `playwright.config.ts` 用
`testIgnore: ['**/*.live.spec.ts']` 把它们排除。

真实原因是**期望漂移**：提交 `11bd3d9`（2026-09-01，IA 改名 + 新增产品推荐菜单）把
导航标签 `证据与知识` 改名为 `产品解读与知识` 并新增 `产品推荐`，**只同步更新了单测**
`src/components/shell/__tests__/AppSidebar.spec.ts`，e2e 用例未同步。

### 2.3 证伪依据（三条，均来自真实日志/代码）

| # | 依据 | 说明 |
|---|---|---|
| 1 | CI 日志 `37 passed (37.9s)` / `1 failed` | 若"页面渲染不出"，38 个用例应大面积失败，而不是 37 过 1 挂 |
| 2 | 失败点在用例**第 26 行**（循环断言第 10 个标签） | 说明第 8–11 行的 `shell-brand` / `shell-sidebar` / `nav-group-daily` / `nav-item-workbench` **都已通过** → 页面**完整渲染**了 |
| 3 | `grep -rn '证据与知识' frontend/src` → **零命中** | 该标签在应用里**根本不存在**（只存在于这个 spec），`11bd3d9` 的 diff 明确显示改名 |

日志里的 `http proxy error: /api/v1/commitments` + `ECONNREFUSED` 来自**另一个并发用例**
（`2 workers`）：`report.spec.ts` 当时**未装 mock**，而 `AppSidebar.vue` 会调
`fetchCommitments`，于是请求经 vite 代理打到无人监听的 8080。
它**与本用例的失败无因果关系** —— 这段噪声正是把人带偏的原因（§3.2 已消除）。
本地已确认该来源：单独跑 `report.spec.ts` 会复现**同样的两行**报错，且**仍然 2 passed**。

### 2.4 本地复现（无后端）

条件：8080 与 5173 **均无监听**、`CI=1`（复刻 `reuseExistingServer` 语义）、
chromium 与 CI 同一 revision（`1234`）。

| 状态 | 结果 |
|---|---|
| 修复前 | `1 failed / 37 passed` —— **失败用例、locator、报错与 CI 逐字一致** |
| 修复后 | `38 passed`，且**不再出现任何** proxy error / ECONNREFUSED |

---

## 3. 顺带修复的两个"假绿"缺口

### 3.1 `Verify E2E tests actually ran` 原为**恒真空转**

原实现读 `playwright-report/index.html`，但 `playwright.config.ts` **没有配置 HTML reporter**
→ 该文件**从不产生** → 步骤固定打印 `WARN: No Playwright report found` 并 **`exit 0`**。

真实证据（run `34870734027`）：`No files were found with the provided path: frontend/playwright-report/`
—— 同时说明该步骤此前**从未真正执行过**（上一步失败后它被 skip）。

现在改由 `frontend/scripts/check-e2e-ran.mjs` 读 JSON reporter 的机器可读计数，
以下情形**一律 exit 1**：报告缺失 / JSON 损坏 / 0 用例 / 有失败 / **有跳过** / 有 flaky /
总数低于基线（38）/ 与 playwright 自算的 `stats` 不一致。

### 3.2 关键发现：**被跳过的用例会让 playwright 退出码仍为 0**

真实变异验证（不是推演）：

```
注入 test.skip → npx playwright test → "1 skipped / 37 passed"，退出码 **0**
                                       ↑ 旧 CI 会把它判为**绿**
守卫判定        → FAIL: 1 个用例被跳过 … → exit 1   ✓ 捕获
还原后          → 38 passed，守卫 PASS             （git diff 为空，现场已还原）
```

### 3.3 守卫非空转的完整证明（8/8 负例 + 正例）

| 用例 | 期望 | 实际 |
|---|---|---|
| 正例 38/38 全过 | PASS | ✓ exit 0 |
| 缺报告文件 | FAIL | ✓ exit 1 |
| JSON 损坏 | FAIL | ✓ exit 1 |
| 0 个用例 | FAIL | ✓ exit 1 |
| 1 个失败 | FAIL | ✓ exit 1 |
| 1 个跳过 | FAIL | ✓ exit 1 |
| 1 个 flaky | FAIL | ✓ exit 1 |
| 37 < 基线 38 | FAIL | ✓ exit 1 |
| 递归计数与 `stats` 不一致 | FAIL | ✓ exit 1 |

---

## 4. 其他本地验证

| 项 | 结果 |
|---|---|
| `npm run check`（`vue-tsc --noEmit`） | 通过 |
| 前端单测 `npm run test` | **341 passed**（63 files） |
| `scripts/secret_scan.py` | PASS；**我的改动未新增任何 advisory 发现** |
| `scripts/sensitive_permissions.py` | PASS |
| `scripts/check_ci_contract_index_wired.py` | PASS（ci.yml 仍正确接线 contract-check） |
| `ci.yml` YAML 解析 | OK；e2e 步骤序列已核对 |

> `frontend/tsconfig.json` 的 `include` 仅含 `src/**` + `vite.config.ts`，
> **不覆盖 `e2e/**` 与 `playwright.config.ts`** → 本次改动不会被 `vue-tsc` 检查
> （这也意味着 e2e 代码目前**没有类型检查**，属既有缺口，未在本次处理）。

---

## 5. CI 状态：**已实跑验证，两轮全绿**

| run | sha | 结论 | 耗时 |
|---|---|---|---|
| `34927339256` | `f665e9b` | **success（10/10 job）** | 8m03s |
| `34927446275` | `9490633`（本次的文档提交，仅 `.md`） | **success（10/10 job）** | 7m12s |

> 第二轮是意外产生的：`paths-ignore` 对 `pull_request` 是按**整个 PR 的 diff** 判定，
> 而不是按单次 push 的 diff → 一个纯 `.md` 提交也会触发整轮 CI。两轮都含本修复，结论一致。

### 5.1 E2E job 的关键日志（run `34927339256` / job `104249382202`）

```
Running 38 tests using 2 workers
38 passed (34.2s)                                    ← 修复前为 "37 passed / 1 failed"
E2E 计数：总用例=38 真实执行=38 通过=38 失败=0 跳过=0 flaky=0 未识别=0（基线 min=38）
PASS: E2E 38 个用例真实执行且全部通过（无跳过、无 flaky）
```

- **判定步骤确实执行了**（不再是恒真空转），且给出结构化计数。
- `grep -c 'proxy error|ECONNREFUSED'` 该 job 日志 → **0 次**（修复前每次 2 次）。
- **artifact 首次上传成功**：`Artifact playwright-report has been successfully finalized`
  （333,245 B）；修复前为 `No files were found with the provided path`。

| job | 结论 | 耗时 |
|---|---|---|
| Contract Index Consistency | success | 5s |
| Compile (JDK 21) | success | 23s |
| Unit Tests | success | 96s |
| Worker Module Tests | success | 33s |
| Frontend Build & Test | success | 77s |
| Security Check | success | 8s |
| **Integration Tests** | success | **199s**（见 §5.2） |
| Docker Build Verification | success | 170s |
| **E2E Tests** | success | 77s |
| Build Summary | success | 2s |

### 5.2 附带实测：**无 NVD API Key 时 Integration 只需约 2–3 分钟**（重要，见 §5.3）

本轮 Integration 的真实日志：

```
Cache restored from key: dc-nvd-Linux-34870734027-1
[WARNING] An NVD API Key was not provided ...
[INFO] NVD API has 1,061 records in this update          ← 冷启动全量为 391,073 条
[INFO] Skipping the NVD API Update as it was completed within the last 240 minutes
[INFO] Total time:  02:56 min
```

机制（**实测 + 推断分开陈述**）：

- **实测**：被恢复的缓存来自**上一轮已完整跑完**的 run `34870734027`
  （该轮虽然 E2E 失败，但 Integration 本身跑完了，因此 `if: always()` 的
  `Save dependency-check NVD data` 存下了一个**一致**的 NVD 库）→ 本轮做成**增量**更新
  （1,061 条，约 1.5 分钟），其余模块直接 `Skipping`。
- **推断（未验证）**：所谓"自污染循环"的成因是**轮次被中途取消**（45 分钟上限时期）。
  一旦轮次能跑完，缓存即可被采信，环路即被打破。若缓存被 LRU 逐出或再次发生中途取消，
  下一轮仍可能回到 39 万条全量（历史观测 33 分钟 ~ 1h54m）。

### 5.3 对 G-2（NVD API Key）结论的影响 —— **请 Owner 复核，本会话不单方面改判**

`docs/governance/OWNER_AUTH_REQUEST-2026-09-14-NVD-API-KEY.md` 的
`A1A2_NECESSITY=REQUIRED` 依据的是"**无 Key 时 CI 无法稳定跑完**"。
本轮实测显示该**依据已被削弱**（无 Key、199s 跑完）。

但**不改变建议**：A-1/A-2 对**冷启动 / 缓存逐出 / 再次中途取消**仍是保险。
本会话**不**改写该文档既有的 necessity 判定（该判定已被更正两次，改判属 Owner 决定），
仅在文档中登记实测证据供复核。

---

## 6. 未完成 / 不属于本次

| # | 项 | 为什么没做 |
|---|---|---|
| **G-2** | gits 的 NVD API Key | 需**能收信的邮箱**（NIST 邮件下发 Key），会话角色没有邮箱；且**不应**让 Key 值进入会话记录。接线已完成，Owner 在 GitHub Secrets 填 `NVD_API_KEY` 即生效。见 `docs/governance/OWNER_AUTH_REQUEST-2026-09-14-NVD-API-KEY.md` |
| **G-3** | KERT 的 A4：systemd 部署核实 | 本地无 `/opt/kert` 部署环境，无法核实。**刻意未改** `deploy/systemd/kert-api.service` |
| — | e2e 代码无类型检查 | 既有缺口（§4 末），本次未动 |
| — | KERT `F-E2E-01`（跨服务 21 条未覆盖） | 仍未解除，按原口径引用 |

---

## 7. 操作风险（本次实际踩到并规避）

1. **工作目录停在他人分支**：gits 主目录在 `recover/PI-ARCH-product-catalog`（含他人未提交改动）。
   本次全程用 **worktree 隔离**：`git worktree add /home/szf/dev/gk-wt/e2e f3ce641`
   → 提交落在 detached HEAD → `git push origin HEAD:refs/heads/feature/GK-KE-L0-contract`。
   **未动他人工作目录。**
2. **推完必须核对远端 sha**：已执行，`gh api … --jq '.object.sha[0:7]'` = `f665e9b` = 本地 HEAD。
3. **不要 `git add .`**：本次 5 个文件全部显式添加。
4. 本地 e2e 产物 `playwright-report/`、`test-results/` **已被 .gitignore 覆盖**，未污染工作区。

---

## 8. 常用命令

```bash
# 隔离检出（避免与他人共用工作目录冲突）
git worktree add /home/szf/dev/gk-wt/e2e <sha>

# 本地复刻 CI 的 e2e（无后端；确认 8080/5173 无监听）
cd frontend && CI=1 npx playwright test && node scripts/check-e2e-ran.mjs

# 守卫负例自测
node scripts/check-e2e-ran.mjs --report <任意 json> --min 38

# CI
gh run list  --repo shaozhongfei001/gits-cbanking --limit 3
gh api repos/shaozhongfei001/gits-cbanking/actions/runs/<id>/jobs \
  --jq '.jobs[]|"\(.name) → \(.conclusion)"'
```

---

## 9. 非声明

- 本文件是**进度快照**，不是 `QA_PASS`，不代表 `PRODUCTION_READY`。
- gits CI 两轮 **10/10 job success**（§5）为**已实跑验证**；但"CI 绿"**不等于**验收通过，
  也**不等于** `PRODUCTION_READY`。
- §2 的结论均有**已实测**依据（本地复现与 CI 日志逐字一致）；§3.2 的"退出码 0"与
  §5.2 的 NVD 时长为**实测**，非推断；§5.2 中标注为"推断（未验证）"的部分不得当作结论引用。
- **G-2 / G-3 仍未完成**（分别需要 Owner 与部署环境）。
