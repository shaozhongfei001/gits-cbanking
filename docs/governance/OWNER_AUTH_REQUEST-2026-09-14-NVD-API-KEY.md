# 需 Owner 授权事项 —— 为 CI 配置 NVD API Key 与 NVD 数据缓存（OWASP dependency-check）

```text
STATUS=A-3/A-4 与路径过滤已实施并入库；A-1/A-2/A-5 待 Owner 执行
REQUESTED_BY=Tech Lead（会话角色）
REQUESTED_AT=2026-09-14
REVISED_AT=2026-09-14（依实测证据更正根因与守卫设计；见文末修订记录）
AUTHORIZATION=Owner 于 2026-09-14 授权 A-1~A-5 全部 + 新增路径过滤
A1A2_NECESSITY=REQUIRED（**必需**；2026-09-14 二次更正，见 §2.5 —— 缓存机制虽已生效，但恢复出的库仍触发全量拉取，无 Key 时冷启动超出 job 上限，CI 无法稳定跑完）
A1A2_NECESSITY_REVIEW=OPEN（2026-09-15 实测**已削弱**上述依据：无 Key 时 Integration job 199s 跑完，见 §2.6。本文件既有的 REQUIRED 判定**未改写** —— 该判定已被更正两次，改判属 Owner 决定）
SCOPE=gits-cbanking 仓 CI 的 dependency-check 数据源凭据与数据缓存
CREDENTIAL_TYPE=第三方只读数据源 API Key（NVD / NIST）；敏感度低（见 §2.2）
TL_AUTHORITY=可改 ci.yml（A-3/A-4 已授权）；禁止获取/配置任何凭据（A-1/A-2 属 Owner）
```

---

## 1. 问题与根因

### 1.1 现象（实测，非推断）

`integration-test` job 调用：

```
./mvnw ... verify -pl apps/api -am -Dtest="**/*IT" -Dsurefire.failIfNoSpecifiedTests=false -Djacoco.skip=true
```

`verify` 触发根 POM 的 `org.owasp:dependency-check-maven:12.1.0:check`。CI 日志：

```
01:24:59  [WARNING] An NVD API Key was not provided - it is highly recommended to use an NVD API key
01:25:03  [INFO] NVD API has 390,807 records in this update
01:57:35  NVD 同步完成                        ← 耗时 32.5 分钟
01:58:00  真正的集成测试开始
01:58:13  测试出结果                          ← 测试本身仅 13 秒
```

- 四轮 Integration job 时长：`33m46s` / `33m03s` / `32m58s` / `33m08s`
- 2026-09-14 run `34836870439`：**1h54m4s 未完成，已人工取消**
- 结论：**该 job 时长由 NVD 同步支配，与代码改动无关**

### 1.2 根因（**已更正**，原归因不完整）

> 初版把主因写成「runner 临时性 + 缺 API Key」。实测证据表明真正的根因是**缓存主键不可变**。

关键证据：

| 证据 | 值 | 来源 |
|---|---|---|
| 缓存恢复日志 | `Cache hit for: Linux-maven-9d58e815...` | CI 日志 182 行 |
| 该缓存体积 | **~70 MB (73,615,984 B)** | CI 日志 186 行 |
| NVD 库实际体积 | **250,736,640 B ≈ 239 MB**（单文件 `odc.mv.db`） | 本机 `~/.m2/repository/org/owasp/dependency-check-data/` |
| 插件数据目录 | `~/.m2/repository/org/owasp/dependency-check-data`（插件默认值） | 本机实测 + 插件 `plugin.xml` |

**即：恢复出来的缓存里根本没有 NVD 库。** 机制为：

1. NVD 库位于 `~/.m2/repository/org/owasp/dependency-check-data`（239MB），
   **落在现有 `Cache Maven dependencies` 步骤（`path: ~/.m2/repository`）的路径之内**；
2. 但该步骤主键是 `${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}`，
   **主键一旦被创建（由 compile/unit-test 等不含 NVD 库的 job 抢先写入 73MB），
   `actions/cache` 在 HIT 时不会再保存**；
3. 于是 integration 轮次下载的 239MB NVD 库**每轮被丢弃**；
4. 叠加因素：**失败的 job 本就不会保存缓存**，而该 job 长期处在失败状态。

**推论（重要）**：NVD API Key 是**次因**。真正让每轮重下 39 万条的是缓存机制缺陷。
即使没有 API Key，只要缓存能留存，后续轮次只需**增量更新**（数个请求，约 1 分钟），
而非全量 390,807 条。**故 A-4（缓存）为主修，A-3（Key）为加速与速率余量。**

### 1.3 为什么不能"就地绕过"

根 POM 对 dependency-check 的配置是**有意的 fail-closed**（原文注释）：

```xml
<failBuildOnCVSS>7</failBuildOnCVSS>
<!-- 扫描器执行/数据源错误必须 FAIL（fail-closed），不因网络 401 等静默 PASS。 -->
<failOnError>true</failOnError>
```

因此 **Tech Lead 拒绝**加 `-Ddependency-check.skip=true`：那是把一项有意设计的安全控制静默拿掉，等同于制造假绿。

### 1.4 与既有纪律的关系

本仓已有 `scripts/dependency-check-guard.py`（`make backend-deps-check` / `backend-test` 调用），检查项含「**NVD/主数据源时间可识别（数据新鲜度）**」。即数据源新鲜度本就是既有门禁语义；为其提供正规数据源凭据并让缓存按周期刷新，是让该纪律在 CI 中真正可执行。

### 1.5 同时发现、**本次不修**的独立缺陷 D2

日志中存在 **2 条**（不是海量）：

```
[ERROR] Failed to process CVE-2026-6785
org.owasp.dependencycheck.data.nvdcve.DatabaseException: Error updating 'CVE-2026-6785';
  Value too long for column "URL CHARACTER VARYING(1000)": "...bugzilla.mozilla.org... (1585)"
    at ...NvdApiProcessor.updateCveDb (NvdApiProcessor.java:119)
[ERROR] Failed to process CVE-2026-6786
```

性质与影响：

- 原因：NVD 记录中 URL 超过本地 H2 库 `URL VARCHAR(1000)` 列宽，**写入失败被跳过**；
- 后果：这 2 条 CVE **不在本地库中** → 若被测依赖受其影响，扫描会**假阴性**（漏报）；
- **更值得登记的**：该错误被记作 `[ERROR]` 却**非致命**，build 照常继续 →
  根 POM 声称的「数据源错误必须 FAIL（fail-closed）」**对这一类错误并未真正生效**。
  这是"声明的保证"与"实际行为"之间的缺口，**不是**本次授权范围内的事，单列待裁决。

---

## 2. 授权事项与状态

| # | 事项 | 由谁做 | 状态 |
|---|---|---|---|
| **A-1** | 向 NIST 申请 NVD API Key | **Owner**（需机构邮箱） | **待执行**（见 §2.2） |
| **A-2** | 将该 Key 存入 GitHub 仓库 Secrets（名 `NVD_API_KEY`） | **Owner**（仅仓库管理员） | **待执行**（见 §2.3） |
| **A-3** | 授权 `.github/workflows/ci.yml` 引用该 secret | Owner（已授权） | **已实施**（见 §3.1） |
| **A-4** | 授权为 NVD 数据目录建立专用缓存 | Owner（已授权） | **已实施**（见 §3.2） |
| **A-5** | 指定轮换 / 复核责任人（建议 90 天复核点） | **Owner** | **待指定** |

### 2.1 最小权限与存放要求

| 项 | 要求 |
|---|---|
| 凭据形态 | NVD API Key：第三方**只读公共数据源**凭据，**无任何仓库读写权限** |
| 存放位置 | **仅** GitHub Actions **Secrets**（仓库级）。**禁止**写入任何文件、提交、日志、PR 描述、聊天记录 |
| 引用方式 | `-DnvdApiKeyEnvironmentVariable=NVD_API_KEY` + `env: NVD_API_KEY: ${{ secrets.NVD_API_KEY }}`（§3.1） |
| 读取范围 | 仅 `integration-test` job（当前唯一触发 `verify` 的 job） |
| 日志卫生 | 不用 `-DnvdApiKey=<明文>`（会进进程参数与日志）；不 `echo`；不 `set -x` |
| 有效期 / 轮换 | 无固定有效期但可被吊销；建议 90 天复核（A-5） |

### 2.2 A-1：Owner 需执行的动作

1. 访问 `https://nvd.nist.gov/developers/request-an-api-key`，用**机构邮箱**提交申请（免费）；
   用途可填：CI 中对内部仓库 `gits-cbanking` 运行 OWASP dependency-check，需要更高调用速率。
2. Key 由 NIST **邮件下发**。
3. **注意**：CI 日志保留期与访问面较广，故 Key **不要**贴到会话/工单/文档里。

### 2.3 A-2：Owner 需执行的动作

- 仓库 → Settings → Secrets and variables → Actions → New repository secret
  名称 **`NVD_API_KEY`**，值粘贴 NIST 邮件中的 Key。
- 亦可 `gh secret set NVD_API_KEY --repo shaozhongfei001/gits-cbanking`（交互式粘贴，勿带 `--body`）。

> **Tech Lead 不接收、不代填该 Key。** 一旦它进入本会话，就会留存在会话记录中，违背最小暴露原则。

### 2.4 关于 GHSA-qqhq-8r2c-c3f5（已核查，**本项目不受影响**）

- 公告内容：`nvdApiKey` 在 Maven debug（`-X`）模式下会被明文写入日志（CWE-532，低危 CVSS 3.3）；
- **影响版本：`dependency-check-maven` >= 9.0.0, < 9.0.6**；**修复于 9.0.6**；
- 本项目使用 **12.1.0 > 9.0.6 → 不受影响**；
- 仍按插件推荐口径（`nvdApiKeyEnvironmentVariable`）传参，且 CI 不使用 `-X`。

### 2.5 A-1 / A-2 的必要性评估（**二次更正：必需**）

初版写"必需"；根因更正后（§1.2）曾降级为"可选（冷启动保险）"；
**2026-09-14 实测再次更正为「必需」**。依据（真实 CI run `34864871467`）：

- 专用缓存**机制已生效**：`Cache restored from key: dc-nvd-Linux-34849048523-1`、
  `Cache saved with key: dc-nvd-Linux-34864871467-1` 均成功；
- **但恢复出的库仍触发全量拉取**（日志 `NVD API has 391,073 records`）——
  因为被缓存下来的库来自**被取消的轮次**，处于半更新状态，插件不予采信；
- 于是无 Key 的冷启动仍需 45 分钟以上，而 job 上限先到期 → Integration job 被取消
  （`15:51:42Z → 16:37:07Z`，恰好 45min25s）→ **docker-build / e2e 被 skip**
  （其 `needs` 含 integration-test），整轮 CI 无法转绿。

| 场景 | 无 API Key | 有 API Key |
|---|---|---|
| **冷启动**（缓存为空/被逐出/内容不可采信） | 全量 390,807 条 ≈ 196 页，5 请求/30 秒 → **实测 33 分钟 ~ 1h54m** | 50 请求/30 秒 → 约 **3 分钟** |
| **增量更新**（库被采信且较新） | 只拉"自上次以来变更的 CVE" → 约 1 分钟以内 | 秒级 |

**关键更正**：初版断言"缓存修复后正常轮次落在「增量」行，故无 Key 也约 1 分钟"——
**该前提实测不成立**。库能否被采信取决于上次保存是否完整（未被取消），
而当前 CI 一直在半途被取消，形成**自污染循环**。

因此：

- A-1/A-2 是**必需项**，不是保险 —— 无 Key 时本仓 CI **无法稳定跑完** Integration job；
- 过渡措施：job 上限已由 45 分钟放宽至 120 分钟（仅作"真死挂"的有界保护），
  **不能替代 Key**；它只让冷启动有机会跑完；
- 若能完成**一次**完整冷启动，其保存的库应可供后续轮次增量使用 ——
  但该路径**未经验证**，且任何半途取消都会重新污染缓存。

职责边界不变：A-1 需要一个**能收信的邮箱**（NIST 以邮件下发 Key），会话角色没有邮箱，
无法闭环；A-2 的技术能力具备（token 对该仓库 `permissions.admin=true`），
但不应由会话角色执行（需把 Key 值发进会话）。

**职责边界（更正）**：

- A-1 **不要求**你是仓库 Owner：NIST 只要求一个**能收信的邮箱**，Key 与仓库无关，
  团队内**任何有邮箱的人**均可申请；
- 但它**不能由 Tech Lead 完成**：Key 以邮件下发，而会话角色**没有邮箱**，闭环缺一环；
- A-2 的技术能力 Tech Lead **具备**（已核：token 对该仓库 `permissions.admin=true`），
  **但不应当由 Tech Lead 执行** —— 那需要把 Key 值发进会话，而会话记录会被留存，
  违背最小暴露原则。

### 2.6 2026-09-15 实测补充：**无 Key 时 Integration 仅约 2–3 分钟**（请 Owner 复核必要性）

> 本节只**登记证据**。本文件既有的 `A1A2_NECESSITY=REQUIRED` **未改写**；
> 该判定已被更正两次，改判属 Owner 决定（见文末修订记录）。

真实 CI 证据（sha `f665e9b`，run `34927339256`，**未配置任何 API Key**）：

```
Cache restored from key: dc-nvd-Linux-34870734027-1
[WARNING] An NVD API Key was not provided ...
[INFO] NVD API has 1,061 records in this update       ← 冷启动全量为 391,073 条
[INFO] Skipping the NVD API Update as it was completed within the last 240 minutes
[INFO] Total time:  02:56 min
```

| 项 | 值 | 性质 |
|---|---|---|
| Integration job 总耗时 | **199s**（第二轮 run `34927446275` 为 121s） | 实测 |
| 对照（修复前四轮） | 32m58s ~ 33m46s | 实测（本文件 §1.1） |
| NVD 本轮拉取条数 | **1,061**（全量为 391,073） | 实测 |
| 后续模块 | `Skipping the NVD API Update as it was completed within the last 240 minutes` | 实测 |
| §3.4 证据清单第 1、3 项 | **均已满足**（缓存 restore 生效；空 secret 不硬失败） | 实测 |

**机制（实测与推断分开）**：

- **实测**：恢复到的缓存来自**上一轮已完整跑完**的 run `34870734027` —— 该轮虽然
  `E2E Tests` 失败，但 **Integration job 本身跑完了**，因此 `if: always()` 的
  `Save dependency-check NVD data` 存下的是一个**一致的** NVD 库 → 本轮做成**增量**更新。
- **推断（未验证）**：所谓"自污染循环"的成因是**轮次被中途取消**（45 分钟上限时期）。
  轮次能跑完则环路自解。若缓存被 LRU 逐出、或再次发生中途取消，
  下一轮仍可能回到 39 万条全量（历史观测 33 分钟 ~ 1h54m）。
  该推断**未经验证**，不得当作结论引用。

**结论（本会话的立场）**：

1. "**无 Key 时 CI 无法稳定跑完**"这一**依据已被削弱**；
2. 但 A-1/A-2 对**冷启动 / 缓存逐出 / 再次中途取消**仍是保险，**建议仍执行**；
3. necessity 的最终裁定**留给 Owner**；本会话**不**代 Owner 改判。

---

## 3. 已实施内容（A-3 / A-4 / 路径过滤）

改动文件：`.github/workflows/ci.yml`，**仅 `integration-test` job**，未触碰 `on:`、其它 job、POM 的
`failOnError` / `failBuildOnCVSS` / `suppressionFile` 语义。

### 3.1 A-3：NVD API Key 注入

```yaml
      - name: Run Integration Tests
        env:
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
        run: ./mvnw ... verify -pl apps/api -am -Dtest="**/*IT" \
               -Dsurefire.failIfNoSpecifiedTests=false -Djacoco.skip=true \
               -DnvdApiKeyEnvironmentVariable=NVD_API_KEY
```

依据（`plugin.xml` 定论级证据）：
`<nvdApiKeyEnvironmentVariable implementation="java.lang.String">${nvdApiKeyEnvironmentVariable}</nvdApiKeyEnvironmentVariable>`
（`aggregate` goal 第 1185 行、**`check` goal 第 2440 行**）→ 该参数是插件公开的用户属性，`-D` 生效，**无需改 POM**。

空 secret 时的行为：`${{ secrets.NVD_API_KEY }}` 解析为空字符串 → 插件按「未提供 Key」处理，
**与改动前一致，不会硬失败**。（待一次实跑确认，见 §4）

### 3.2 A-4：NVD 数据专用缓存（**主修**）

```yaml
      - name: Restore dependency-check NVD data
        uses: actions/cache/restore@v4
        with:
          path: ~/.m2/repository/org/owasp/dependency-check-data
          key: dc-nvd-${{ runner.os }}-${{ github.run_id }}-${{ github.run_attempt }}
          restore-keys: |
            dc-nvd-${{ runner.os }}-
      ...
      - name: Save dependency-check NVD data
        if: always()
        uses: actions/cache/save@v4
        with:
          path: ~/.m2/repository/org/owasp/dependency-check-data
          key: dc-nvd-${{ runner.os }}-${{ github.run_id }}-${{ github.run_attempt }}
```

设计要点与依据：

- **专用主键**：不再与 Maven 主键共用（根因，§1.2）；
- **`if: always()` 显式保存**：失败的 job 不会自动保存缓存，而本 job 长期失败 → 必须显式保存；
- **主键含 `run_id` + `run_attempt`**：每轮存一份最新快照（`restore-keys` 前缀取最近一次），
  使后续轮次只做增量更新；带 `run_attempt` 可避免 `rerun` 时同名主键已存在导致 save 失败；
- 已知次要低效（不影响正确性）：若未来 Maven 主键发生 MISS，Maven 缓存会把 239MB NVD 库一并收进去，
  产生一个偏大的 Maven 缓存条目。因专用缓存已覆盖该目录，无功能影响。

### 3.3 有界超时（**替代**原拟的"缺 Key 即快速失败"守卫）

```yaml
  integration-test:
    timeout-minutes: 45
```

理由（**这是对本文件初版设计的更正**）：

- 初版 §3.2 拟「`NVD_API_KEY` 为空 → 立即失败」。复核后判定该设计**有害**：
  它会让 dependency-check **完全不执行**（job 在扫描前就失败），即在 A-2 落地前的窗口内
  **把一项安全控制停用**——比"慢"更糟；
- 改为 job 级超时：45 分钟可容纳冷启动全量同步（实测 33 分钟），
  同时把 run `34836870439` 那种「1h54m 静默挂起」变为**有界失败**；
- **不做**「缺 Key 就失败」的硬断言；是否在 A-2 落地后追加该断言（或改为"缺 Key 且缓存未命中才失败"），
  另行裁决。

### 3.4 证据要求（下一次 CI 运行后核验）

1. **缓存生效**：出现 `Cache restored from key: dc-nvd-...`；NVD 同步被跳过或显著缩短
   （关键字：`Skipping the NVD API Update as it was completed within the last 240 minutes`）；
2. **有界**：Integration job 时长回到分钟级；不再出现 >45 分钟挂起；
3. **空 secret 不硬失败**：`An NVD API Key was not provided` 仍出现且 job 行为与改动前一致；
4. **A-2 落地后**：该 warning 消失，且 NVD 同步明显加快（冷启动亦可接受）；
5. **秘密未泄露**：grep 运行日志确认无 Key 值或其前缀；
6. `scripts/dependency-check-guard.py` 本地仍 PASS（数据源新鲜度语义未被破坏）。

### 3.5 路径过滤（独立裁决项 ⑥-1，已实施）

问题：`on:` 原本**无任何路径过滤**，纯文档提交也会触发全量 CI（实例：纯文档提交 `e9dcf45`
触发 run `34847175044`，白跑一轮约 2 小时 runner）。

改动：

```yaml
on:
  push:
    branches: [main, develop]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - 'evidence/**'
      - 'diagrams/**'
  pull_request:
    branches: [main]
    paths-ignore:      # 刻意逐字重复，不用 YAML 锚点
      - '**.md'
      - 'docs/**'
      - 'evidence/**'
      - 'diagrams/**'
```

安全性依据（**改动该列表时必须重新核对**）：

1. **`main` 未受保护**、无 rulesets（已核：`GET branches/main/protection` → 404）
   → 工作流被跳过**不会**让 PR 卡在 pending。⚠ 若日后启用「必需状态检查」，
   纯 `.md` 的 PR 会因检查永不报告而**永久 pending**，本过滤必须重新评估。
2. **忽略路径与 spec 权威源无交集**：`specs/CONTRACT_INDEX.yaml` 的 **58 条**
   `authority_source` 全部位于 `specs/` 下，扩展名仅 `.json`(53)/`.ttl`(2)/`.yaml`(2)/`.dmn`(1)，
   **无 `.md`**，且**无一条**落在 `docs/`、`evidence/`、`diagrams/`。
   → `contract-check` 的存在性校验（`scripts/check_contract_index_refs.py` 第 36 行）
   不会因这些路径的变更而漏检。
   ⚠ **不变量**：若日后有 `authority_source` 指向 `.md` 或落在上述目录内，则「移动/删除该文件」
   将同时满足「跳过 CI」与「破坏 contract-check」= **fail-open**。届时须收紧本列表，
   或把该检查拆到独立的、无路径过滤的工作流。
3. **未**忽略 `specs/**`（其下正是那 58 个权威 schema）；也**未**忽略
   `loops/ scenario/ modules/ monitoring/ tools/ generated/ frontend/ apps/ adapters/ scripts/ tests/`。
4. 语义：`paths-ignore` 是「**全部**变更文件都命中忽略项才跳过」→
   「代码 + 文档」混合提交仍会正常触发 CI。
5. 刻意**不使用 YAML 锚点**：若锚点在 `on:` 段解析失败，工作流会整体失效，
   而「没有 run」与「过滤按预期生效」表象完全相同 → **无法分辨的静默失效**。
   代价是两份列表须同步修改。

---

## 4. 残留风险与边界

| # | 风险 | 说明与缓解 |
|---|---|---|
| **4.1** | 首次冷启动仍需数分钟 | 有 Key 亦需完成一次同步；缓存命中后才稳定在分钟级。不得据此判断接线失败 |
| **4.2** | 缓存体积 | NVD 库 ~239MB/份；`run_id` 主键使每轮新增一份，靠 GitHub LRU 与 10GB 上限自限 |
| **4.3** | Fork PR 无 secrets | 该 job 回落无 Key 路径（慢，但缓存可救）。本仓当前无 fork PR；若引入外部贡献者需重新裁决 |
| **4.4** | 空 secret 的兼容性**未实证** | 见 §3.1。**Owner 已确认**：若下一次 CI 出现 dependency-check 相关硬失败，改为条件注入（仅在变量非空时追加 `-DnvdApiKeyEnvironmentVariable`） |
| **4.5** | D2 未修（§1.5） | 2 条 CVE 缺失 + fail-closed 未覆盖该错误类。**单列待裁决**，不在本次改动范围 |
| **4.6** | 凭据管理成本 | 本仓 CI 首次引入 secret，需指定轮换责任人（A-5 待指定） |
| **4.7** | 路径过滤的两项残留 | 已实施（§3.5）。残留一：若日后启用「必需状态检查」，纯 `.md` 的 PR 会**永久 pending**；残留二：`authority_source` 不变量（不得指向 `.md` 或落在忽略目录内）须在每次改 `CONTRACT_INDEX.yaml` 时保持，否则出现 **fail-open** |

---

## 5. 非声明

- **A-1 / A-2 / A-5 尚未完成**：Tech Lead **未**获取、**未**配置、**未**接收任何凭据。
  A-3/A-4 的代码改动**不等于** CI 已具备 NVD 数据源能力。
- 本次改动**未在真实 CI 中验证过**（本文件写成时仅通过 YAML 语法校验与仓内 `secret-scan` /
  `sensitive-permissions` 门禁，未新增告警）。
- **CI 未全绿**：run `34836870439` 被人工取消（`1h54m4s`），结论未知；
  其失败真因为测试断言（`KnowledgeSnapshotLoaderIT.loadsCompleteNonEmptySnapshot:44 expected: <2> but was: <3>`），
  **不是** dependency-check。
- run `34847175044`（sha `e9dcf45`，含 `e22e844`）为上述断言修复的 **CI 复验轮**，发起时仍在运行中；
  其结论以实际结果为准。
- 本文件**不代表** `PRODUCTION_READY=YES`，**不构成** `QA_PASS`。

---

## 6. 修订记录

| 时间 | 修订 | 依据 |
|---|---|---|
| 2026-09-14 | 初版：归因「runner 临时性 + 缺 API Key」，拟「缺 Key 即快速失败」守卫，称「插件按 `NVD_API_KEY` 自动识别、无需改 POM」 | — |
| 2026-09-14 | **更正根因**为「缓存主键不可变 → 239MB NVD 库每轮被丢弃」（§1.2） | 缓存 HIT 日志 `Cache Size ~70MB` vs 本机 NVD 库 239MB；4 轮均 ~33 分钟 |
| 2026-09-14 | **更正守卫设计**：改为 job 级 `timeout-minutes: 45`，弃用「缺 Key 即失败」（§3.3） | 该守卫会在 A-2 落地前**停用** dependency-check |
| 2026-09-14 | **更正注入口径**：改用 `-DnvdApiKeyEnvironmentVariable`（插件推荐） | `plugin.xml` 第 2440 行（`check` goal）+ GHSA-qqhq-8r2c-c3f5（12.1.0 不受影响） |
| 2026-09-14 | 新增 §1.5 独立缺陷 D2（2 条 CVE + fail-closed 缺口） | CI 日志 `[ERROR] Failed to process CVE-2026-6785/6786` |
| 2026-09-14 | 新增 §3.5 路径过滤并登记其两项残留（§4.7）；§4.4 记录 Owner 对回退方案的确认 | Owner 裁决 ⑥-1、⑥-2 |
| 2026-09-14 | 曾**降级 A-1/A-2 为「非必需」**：缓存修复后正常轮次仅需增量更新，无 Key 也约 1 分钟（§2.5，**该结论已被下一条推翻**） | §1.2 根因更正 |
| 2026-09-14 | **二次更正 A-1/A-2 为「必需」**：缓存机制实测已生效（restore/save 均成功），但恢复出的库仍触发全量拉取（半更新状态不被采信）→ 无 Key 时冷启动超出 job 上限，Integration job 被取消、docker-build/e2e 被 skip（§2.5） | 真实 CI run `34864871467` 的 job 详情与日志 |
| 2026-09-14 | job 上限由 45 分钟放宽至 **120 分钟**（45 分钟已实测误杀合法轮次） | 同上：`15:51:42Z→16:37:07Z`，恰好 45min25s |
| 2026-09-15 | 新增 **§2.6 实测补充**：无 Key 时 Integration job **199s** 跑完（NVD 仅增量 **1,061** 条；缓存来自**已完整跑完**的 run `34870734027`）⇒ `A1A2_NECESSITY=REQUIRED` 的**依据被削弱**。标记 `A1A2_NECESSITY_REVIEW=OPEN`，**未改写**既有判定（改判属 Owner 决定） | 真实 CI run `34927339256` / `34927446275`（sha `f665e9b`）的 Integration job 日志 |
