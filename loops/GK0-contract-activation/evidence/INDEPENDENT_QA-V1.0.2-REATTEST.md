# GK0-contract-activation｜独立 QA 二次复核报告（封版 V1.0.2 · AC-01/02/03 关闭判定）

- **复核角色**: independent_qa（独立 QA，与 Feature Pilot 隔离）
- **actor**: gk0-qa1
- **session**: qa-gk0-v102-reattest-001
- **受测封版 HEAD**: `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e`
- **受测受控目录 tree**: `4c5f5373c83386d27ea996293a49ee7f3b9f10ce`
- **受测 ZIP**: `docs/dd/GK-KE-CONTRACT-V1.0.2_REVIEW.zip` sha256 `b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0`
- **包 ID**: `GK-KE-CONTRACT-V1.0.2`（`status=CONTRACT_CANDIDATE`）
- **复核日期**: 2026-09-11
- **复核范围**: 封版制品一致性（AC-01 制品封版 / AC-02 补充脚本交付 / AC-03 Git-QA 一一对应）

> 独立性声明：本报告全部结论均由独立复现命令得出，未采信 Feature Pilot 自检结论、未继承 `INDEPENDENT_QA-R4-1.md` 的判定。对关键断言执行了变异测试（mutation test）以证明检查非空转。

---

## 一、受测版本锚定

| 检查 | 命令 | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| 封版 commit | `git rev-parse 886f710^{commit}` | `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e` | `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e` | ✅ |
| 受控目录 tree | `git rev-parse 886f710:docs/dd/gk-ke-contract` | `4c5f5373c83386d27ea996293a49ee7f3b9f10ce` | `4c5f5373c83386d27ea996293a49ee7f3b9f10ce` | ✅ |
| 封版后受控目录未被改动 | `git diff --stat 886f710 HEAD -- docs/dd/gk-ke-contract` | 空 | 空 | ✅ |
| 工作区受控目录干净 | `git status --short docs/dd/gk-ke-contract` | 空 | 空 | ✅ |
| 封版后仅锚点提交 | `git log --oneline 886f710..HEAD` | 仅锚点更新 | `aad011d docs(gk-ke): update evidence-chain anchors for reseal V1.0.2` | ✅ |

**HEAD vs 封版 HEAD 说明**：最新 HEAD 为 `aad011d`（锚点更新），其仅修改 FAILURES.md / 整改答复 / QA 提示词 / STATE.json / EVIDENCE.json，**不触碰 `docs/dd/gk-ke-contract`**，故复查对象可安全锚定 `886f710`。

---

## 二、复核前必做项（独立复现）

| # | 命令 | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| 1 | `git rev-parse 886f710:docs/dd/gk-ke-contract` | `4c5f5373…` | `4c5f5373…` | ✅ |
| 2 | `python3 tools/validate_package.py` | 148 passed / 0 failed | `{"passed": 148, "failed": 0}` | ✅ |
| 3 | `python3 tools/gk_ke_contract_examples.py` | 20 正例 / 40 负例 | `正例通过 20/20，负例被拒 40 个` | ✅ |
| 4 | `python3 tools/verify_simulation.py` | PASS, C001=2983333.33 | `verify_simulation: PASS`；`expected.json` 与脚本常量均为 `2983333.33` | ✅ |
| 5a | `sha256sum GK-KE-CONTRACT-V1.0.2_REVIEW.zip` | `b21638ab…d97a5ad0` | 完全一致 | ✅ |
| 5b | 解压 vs 受控目录逐文件 sha256 | 145 文件 / 0 差异 | 145 vs 145，`diff -r` rc=0，逐文件 sha256 差异数 = 0 | ✅ |

**独立性交叉验证（AC-02 硬核）**：将 ZIP 解压到仓库外隔离目录 `/tmp/qa_isolated/gk-ke-contract`，**脱离仓库上下文**重新执行三个脚本，结果全部复现：

```
/tmp/qa_isolated/gk-ke-contract $ python3 tools/gk_ke_contract_examples.py
gk-ke 合同样例: 正例通过 20/20，负例被拒 40 个
gk-ke-contract-examples: PASS
/tmp/qa_isolated/gk-ke-contract $ python3 tools/verify_simulation.py
verify_simulation: PASS
/tmp/qa_isolated/gk-ke-contract $ python3 tools/validate_package.py
{"passed": 148, "failed": 0}
```

---

## 三、逐项结论

### AC-01 封版完整性 — **PASS**

1. **MANIFEST 覆盖率精确**（独立枚举磁盘文件 vs MANIFEST 条目）：
   - 磁盘文件 145，MANIFEST 条目 144，差集恰为 `MANIFEST.json` 自身（自排除）。
   - `IN ACTUAL NOT IN MANIFEST = ['MANIFEST.json']`；`IN MANIFEST NOT ACTUAL = []`。无遗漏、无幻影路径。✅
2. **完整总契约已纳入**：`00_项目总契约.md`（8258 bytes）在 MANIFEST 第 1 条。✅
3. **simulation/oracles 已纳入**：`simulation/oracles/expected.json`、`simulation/oracles/negative_cases.json` 均在册。✅
4. **manifest 自校验非空转（变异测试证明）**：
   - 篡改任一受控文件末尾 1 字节 → `validate_package.py` 抛出 JSONDecodeError 并失败；篡改 MANIFEST 中某条目 sha256 → 输出 `{"passed": 147, "failed": 1}`，`{'check': 'manifest-bytes-sha256', 'status': 'FAIL'}`。
   - 证明 `manifest-covers-all-files` / `manifest-no-missing-paths` / `manifest-bytes-sha256` / `manifest-paths-unique` 四项均为真实比对逻辑。✅
   - 从 ZIP 隔离目录独立复算 144 条 sha256：`sha256 mismatches: 0`。✅
5. `packageId` 已更新为 `GK-KE-CONTRACT-V1.0.2`。✅

### AC-02 脚本可复现 — **PASS**

1. **包内交付**：`tools/gk_ke_contract_examples.py`、`tools/verify_simulation.py` 均存在于受控目录与 ZIP 内。✅
2. **无仓库外依赖**：
   - `grep` 全部 `tools/*.py`：无 `/home/`、`/Users/`、`/tmp/`、`../../`、`gits-cbanking` 等绝对/越界路径引用。
   - 唯一 `specs/gk-ke` 字样出现在 `gk_ke_contract_examples.py` 第 4 行**中文注释**中，非代码路径引用。✅
3. **隔离环境可复现**：见第二节隔离运行，三脚本在 ZIP 解压目录外均可 100% 复现。✅
4. **结果由包内数据驱动（变异测试证明）**：
   - `examples/positive` 20 个文件、`examples/negative` 40 个文件，脚本按目录扫描驱动（`POS_DIR`/`NEG_DIR`）。
   - 删除 1 个负例后输出变为 `负例被拒 39 个`，证明 20/40 **非硬编码**，且已从历史 14/28 正确升级为 20/40。✅

### AC-03 Git-QA 一一对应 + SemanticPackage 分叉修复 — **PASS**

1. **三值锚点一一对应**：
   - HEAD `886f7104…` ↔ tree `4c5f5373…` ↔ ZIP sha256 `b21638ab…` 均可独立复现，且 ZIP 内 145 文件与 `886f710:docs/dd/gk-ke-contract` tree 逐字节一致。✅
2. **SemanticPackage 分叉已修复（核心）**：
   - `diff -r specs/gk-ke/v1/schemas docs/dd/gk-ke-contract/schemas` → **rc=0，0 差异**（20 schema 全同步）。
   - `diff -r specs/gk-ke/v1/examples docs/dd/gk-ke-contract/examples` → **rc=0，0 差异**（20 正例 + 40 负例 = 60 文件）。
   - 逐文件 sha256 交叉核对 20 schema：0 MISMATCH。
   - `SemanticPackage.schema.json` 的 `types[].items` 已补 `writeOwner` / `writeEntry` / `authorityScope`（三字段，`minLength:1`），synced 到 specs 与交付包两端一致。✅
3. **`required` 语义正确**：`types[].items.required` 仍为 `['typeId','definition','identityRule']`，三新字段为**可选**，向后兼容；正例中 `core.Money` 未携带 `authorityScope` 仍通过校验，符合设计。✅
4. **V1.0.1 → V1.0.2 修复范围精准无附带改动**：
   ```
   git diff --name-status daa9b511 4c5f5373
   M  MANIFEST.json
   M  examples/positive/SemanticPackage.json
   M  schemas/SemanticPackage.schema.json
   ```
   仅 3 文件变更，与"分叉修复 + MANIFEST 重生成"声明完全吻合，无越界改动。✅
5. **修复未回退 QA 已复核内容**：`git diff --stat 91d5fed 886f710 -- specs/gk-ke/v1` 为空，证明封版未改动 QA 已复核（`91d5fed`）的合同源内容。✅

---

## 四、证据边界（须如实标注，不构成 AC 失败）

1. **ZIP 未被 git 跟踪**：`docs/dd/GK-KE-CONTRACT-V1.0.2_REVIEW.zip` 为未跟踪文件（`??`），V1.0.0/V1.0.1/V1.0.2 三个 ZIP 均从未提交（仓库既有惯例，无 .gitignore 规则）。
   - 影响：ZIP 的完整性依赖**其自身 SHA-256 值**（已写入 STATE.json / EVIDENCE.json / 整改答复 / 本报告）作为外部锚点，而非 git 对象。
   - QA 判定：**不阻断**。因 ZIP 内容已被证明与 `886f710` 的受控 tree 逐字节一致，tree 由 git 保证不可篡改，故 ZIP 可溯源至 git。**但建议**将 ZIP 纳入 git 跟踪或（更佳）改为 `make package` 从 tree 确定性重建，以形成纯粹的 git 内生证据链。
2. **`acceptance/package_self_check.json` 内 `independentQa=NOT_PERFORMED`**：属包内作者自检快照的如实标注，独立 QA 结论记录在 Loop `EVIDENCE.json` 的 `independent_qa` 字段（不同层级证据），二者不冲突。
3. **`EVIDENCE.json.independent_qa` 仍绑定旧 head**：该记录 `reviewed_head=91d5fed…`，scope 为"WP-R4-1 六合同源变更"，**不是**本次封版 `886f710` 的复核记录。本次复核完成后须由 QA 追加独立记录并显式绑定 `886f710`（见第六节），**在此之前不得以旧记录宣称封版已 QA_PASS**。
4. **Owner 未决事项未变**：`STATE.json.owner_decisions_pending` 四项（metric 口径 / 知识认证 / 地图任务价值 / 试点范围）仍待 Owner 决议，**不属 QA 权限**，不影响本次制品一致性判定。

---

## 五、结论

| 项目 | 判定 |
|---|---|
| AC-01 制品封版（MANIFEST 全覆盖 + 自校验有效） | **PASS** |
| AC-02 补充脚本交付（包内独立可运行 + 20/40 可复现） | **PASS** |
| AC-03 Git-QA 一一对应（三值锚点 + SemanticPackage 分叉逐字节修复） | **PASS** |

**最终结论：QA_PASS**

- 范围限定：**封版制品一致性**（AC-01/02/03 + sealing_v1_0_2）。
- 未覆盖：服务级 E2E、Kuzu / LightRAG 集成、真实人工批准、Owner 决议事项（与包内自检标注一致）。
- 依据：全部断言由独立复现得出，关键检查经变异测试证伪有效性，未继承任何开发自检结论。
- V1.0.1（HEAD `a65c336` / tree `daa9b511` / ZIP `3bf13635`）**确认废止**，由 V1.0.2 取代。

**建议（非阻断，供 Owner / TL 决策）**：
1. 将封版 ZIP 改为从 `886f710` tree 确定性重建（`make package`），消除未跟踪二进制件的溯源缺口。
2. 补记 `EVIDENCE.json.independent_qa` 为 `reviewed_head=886f710…` 的新条目，替换/并存于旧 `91d5fed` 记录。
3. D 阶段门禁可提升为 `PASS_FOR_OWNER_REVIEW`，同时保留四项 Owner 决议为独立待办。
