# 需 Owner 授权事项 —— 为 CI 配置 NVD API Key（OWASP dependency-check）

```text
STATUS=BLOCKED_PENDING_OWNER_AUTHORIZATION
REQUESTED_BY=Tech Lead（会话角色）
REQUESTED_AT=2026-09-14
SCOPE=gits-cbanking 仓 CI 的 dependency-check 数据源凭据
CREDENTIAL_TYPE=第三方只读数据源 API Key（NVD / NIST）
TL_AUTHORITY=无（禁止自行获取、配置或写入任何凭据）
```

---

## 1. 为什么要这个授权

### 1.1 事实（实测，非推断）

CI 的 `integration-test` job 调用：

```
./mvnw ... verify -pl apps/api -am -Dtest="**/*IT" -Dsurefire.failIfNoSpecifiedTests=false -Djacoco.skip=true
```

`verify` 触发根 POM 的 `org.owasp:dependency-check-maven:12.1.0:check`（`pom.xml:121-145`）。CI 日志实测：

```
01:24:59  [WARNING] An NVD API Key was not provided - it is highly recommended to use an NVD API key
01:25:03  [INFO] NVD API has 390,807 records in this update
01:57:35  （NVD 同步完成）                          ← 耗时 32.5 分钟
01:58:00  真正的集成测试开始
01:58:13  测试出结果                                ← 测试本身仅 13 秒
```

- 单轮 Integration job：`33m46s`，其中 **约 96% 耗在无 Key 的 NVD 全量同步**
- 2026-09-14 那轮（run `34836870439`）：**1h54m4s 仍未完成，已人工取消**
- 结论：**该 job 的时长由 NVD 同步支配，与代码改动无关**；无 Key 时表现为 32 分钟至无限期挂起

### 1.2 为什么不能"就地绕过"

根 POM 对 dependency-check 的配置是**有意的 fail-closed**（原文注释）：

```xml
<failBuildOnCVSS>7</failBuildOnCVSS>
<!-- 扫描器执行/数据源错误必须 FAIL（fail-closed），不因网络 401 等静默 PASS。 -->
<failOnError>true</failOnError>
```

因此 **Tech Lead 拒绝**在 CI 中加 `-Ddependency-check.skip=true`：那是把一项有意设计的安全控制静默拿掉，等同于制造假绿。

### 1.3 与既有纪律的关系

本仓已有 `scripts/dependency-check-guard.py`（由 `make backend-deps-check` / `backend-test` 调用），其检查项含「**NVD/主数据源时间可识别（数据新鲜度）**」。即：**数据源新鲜度本就是本仓已确立的门禁语义**。为其提供正规数据源凭据，是让该纪律在 CI 中真正可执行，而非新增要求。

---

## 2. 需 Owner 授权 / 执行的事项

| # | 事项 | 由谁做 | 说明 |
|---|---|---|---|
| **A-1** | 向 NIST 申请 NVD API Key | **Owner**（需机构邮箱） | 入口：`https://nvd.nist.gov/developers/request-an-api-key`。**免费**，需提供邮箱与用途说明；Key 为**只读公共数据源**凭据 |
| **A-2** | 将该 Key 存入 GitHub **仓库 Secrets** | **Owner**（仅仓库管理员可设） | 建议名 `NVD_API_KEY`。参见 §3 的存放与最小权限要求 |
| **A-3** | 授权在 `.github/workflows/ci.yml` 中引用该 secret | **Owner** | 本仓 CI **当前零 secrets 引用**，这将是**第一条**；需 Owner 明示同意 |
| **A-4** | 授权把 NVD 数据目录纳入 `actions/cache` | **Owner** | 见 §4.2：runner 是临时的，不加缓存则**每轮**都要全量同步 |
| **A-5** | 指定轮换 / 复核责任人 | **Owner** | 见 §3.3 |

### 2.1 最小权限与存放要求（必须在授权中逐项确认）

| 项 | 要求 |
|---|---|
| 凭据形态 | NVD API Key（第三方只读数据源；**无任何仓库读写权限**，其泄露后果限于速率限制被占用） |
| 存放位置 | **仅** GitHub Actions **Secrets**（仓库级）；**禁止**写入任何文件、提交、日志、PR 描述、聊天记录 |
| 引用方式 | `env: NVD_API_KEY: ${{ secrets.NVD_API_KEY }}`（插件按环境变量自动识别；`pom.xml` 当前无 `nvdApiKey`/`dataDirectory` 配置，**无需改 POM**） |
| 读取范围 | 仅 `integration-test` job（当前唯一触发 `verify` 的 job）。若日后新增触发 `verify` 的 job，须逐一显式授权 |
| 日志卫生 | 不得 `echo $NVD_API_KEY`、不得 `set -x` 后打印环境变量；实施需在 PR 审查中确认 |
| 有效期 / 轮换 | NVD Key 无固定有效期但可被吊销；**建议 Owner 指定 90 天复核点**，并把复核责任人写入本文件 |
| Fork 场景 | Fork PR **不会**获得 secrets → 该 job 会回到无 Key 路径（fail-closed 但**缓慢**）。本仓当前无 fork PR，故仅登记为已知边界（见 §4.3） |

---

## 3. 授权后由 Feature Pilot 实施的内容（**本清单不含实施，TL 只出规格**）

> 前置：A-1~A-4 已由 Owner 完成。未完成前**不得**开工。

### 3.1 接线（最小改动）

在 `.github/workflows/ci.yml` 的 `integration-test` job（当前 `Run Integration Tests` 步）注入：

```yaml
        env:
          NVD_API_KEY: ${{ secrets.NVD_API_KEY }}
```

**不得**改动：`on:` 触发段、其它 job、POM 的 `failOnError` / `failBuildOnCVSS` / `suppressionFile` 语义。

### 3.2 防"慢挂"守卫（**强制**，本次事故的直接教训）

加一个**前置步骤**：若 `NVD_API_KEY` 为空或在 60 秒内无法完成 NVD 同步 → **立即失败并给出明确原因**。

理由：无 Key 时现状是**挂 114 分钟才被人工取消**，这比快速失败严重得多——它占用 runner 且无人知晓。守卫要把"114 分钟后的静默挂起"变成"1 秒内的显式失败"。

### 3.3 NVD 数据缓存（**强制**）

`actions/cache` 缓存 dependency-check 的数据目录。要点：

- **缓存路径须由实施者实测确认**（不得凭猜测）：从 CI 日志中定位插件实际数据目录（线索：插件会打印 `Skipping the NVD API Update as it was completed within the last 240 minutes`，其作用对象即该目录）；若无法确定，则在 POM 显式配置 `<dataDirectory>` 并缓存之（**该 POM 改动需单独授权**）。
- 缓存键须含日期或周次分量，以便周期性刷新 NVD 数据，避免长期使用陈旧数据（与 `dependency-check-guard.py` 的**数据新鲜度**检查语义一致）。
- 命中缓存时，插件应打印 `Skipping the NVD API Update...`，job 时长应回到**分钟级**。

### 3.4 证据要求

1. 接线后的 CI 运行链接 + 关键日志行：
   - **不再出现** `An NVD API Key was not provided`
   - 出现 `Skipping the NVD API Update...`（缓存命中）或 NVD 同步耗时显著下降
2. `integration-test` job 时长的前后对照（基线：`33m46s`；异常上限：`1h54m4s`）
3. 秘密未被打印的自查（grep 运行日志确认无 Key 值或其前缀）
4. `scripts/dependency-check-guard.py` 在本地仍 PASS（数据源新鲜度语义未被破坏）

---

## 4. 残留风险与边界（授权时须一并接受）

| # | 风险 | 说明与缓解 |
|---|---|---|
| **4.1** | 首次同步仍需数分钟 | 有 Key 亦需完成一次全量同步；缓存命中后才会稳定在分钟级。**不得**据此判断接线失败 |
| **4.2** | runner 临时性 | 不加 §3.3 的缓存，**每轮**都要全量同步——这是本问题在 CI 中的主因，故 3.3 标记为强制 |
| **4.3** | Fork PR 无 secrets | 该 job 回落无 Key 路径。当前无 fork PR；若未来引入外部贡献者，需重新裁决（可能需改为"fork PR 跳过 dependency-check"并**登记豁免**，而非静默通过） |
| **4.4** | 数据新鲜度与门禁的张力 | 缓存过旧会被 `dependency-check-guard.py` 的数据源新鲜度检查抓住；缓存键的刷新周期须与既定新鲜度阈值一致 |
| **4.5** | 凭据管理成本 | 本仓 CI 首次引入 secret，需指定轮换责任人（A-5）；Key 虽只读低敏，仍属凭据 |

---

## 5. 非声明

- 本文件是 **Tech Lead 的授权申请清单**，**不是**授权本身；**在 Owner 明确批准 A-1~A-5 之前，任何凭据不得被获取、配置或写入**。
- Tech Lead **未**获取、**未**配置、**未**引用任何凭据；本仓 CI 仍未引用任何 secret。
- 本文件**不代表** CI 已全绿：Integration job 在本次事故中被**人工取消**（`34836870439`，`1h54m4s`），其红/绿结论**未知**。
- 本文件**不代表** `PRODUCTION_READY=YES`，**不构成** `QA_PASS`。
- 本文件不改变 dependency-check 的 fail-closed 语义；未授权前，CI 的 dependency-check 仍将处于"无 Key 慢路径"状态。
