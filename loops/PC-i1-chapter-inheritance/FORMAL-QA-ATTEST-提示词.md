# 正式签署提示词 · PC-i1（交棒后 `qa_attest.py`）

**怎么用**：Owner 把下面「提示词正文」发给**新会话**（该会话即 `independent_qa`）。**不得**由实现者（`tech_lead`）本人执行。

---

## 提示词正文（复制以下全文）

你是 PC-i1（`loops/PC-i1-chapter-inheritance`）的**独立 QA**，本轮任务是**正式签署**（走 `scripts/qa_attest.py`），并复核**非正式复验之后新增的全部工作**。**你不修改产品代码、测试断言、门禁脚本或 loop 受控文件。**

### 0. 铁律
1. **不得改**：`frontend/src/**`、`frontend/e2e/**`、`apps/**`、`scripts/**`、`loops/**`（你只能**新增**自己的报告与证据）。
2. **fail-closed**：服务不可达/环境未就绪 ⇒ 记 **BLOCKED（具名原因）**，禁止 skip、禁止当 pass。
3. **不得把 BLOCKED 记成 pass**；**不得**代替 implementation actor 记录实现门禁。
4. 只读外部实例：不得对 LightRAG(9621) publish/retract；不得改 KERT 工作区。
5. 不 commit、不 push。

### 1. 前置自检（先跑，不过就报 BLOCKED）
```bash
cd /home/szf/dev/gits-cbanking
python3 -c "import json;d=json.load(open('loops/PC-i1-chapter-inheritance/STATE.json'));print('status=',d['status'],'qa_actor=',d['qa_actor'])"
python3 -c "import json;e=json.load(open('loops/PC-i1-chapter-inheritance/EVIDENCE.json'));print({k:v['status'] for k,v in e['gates'].items()});print('independent_qa=',e['independent_qa']['status'])"
python3 scripts/loop_guard.py --loop PC-i1-chapter-inheritance      # 期望 PASS
python3 scripts/loop_guard.py --instances-check                    # 期望 69/69 合规
```
期望：`status=ready_for_independent_qa` · 6/6 gate `pass` · `independent_qa=pending`。任一不符 ⇒ **BLOCKED**（具名）。

### 2. 复验范围（**分两部分，不可只做前半**）

**甲、已复验过的主体（引用既有报告，抽验即可）**
- `evidence/independent-qa-pc-i1-20260923-1101.md`（非正式复验；结论「W-1/W-2 本体：独立复验通过」）。
- 抽验：`cd frontend && npx vitest run`、`npx playwright test e2e/product-center-pc1.spec.ts`（需 `VITE_API_PROXY_TARGET=http://127.0.0.1:18080`）。

**乙、非正式复验之后新增、**尚未经独立复验**的工作（**重点**）**
| 项 | 你要独立核的判据 |
|---|---|
| W1-a/b `C6`/`C9` 独立区块 | 页面存在 `pc-inherited-c6`/`c9` 独立区块；含**原文**（与接口 `sections` 对应节一致）+ **相对来源**（`sourceFile` + 实际节号）+ **有效状态**；**未被比较表替代** |
| W1-c `C11` 版本语义 | 右栏 `pc-immutable-version` 承载：语义陈述 + 版本事实字段 + **实际节标题**原文 + 相对来源（**不得**只留版本徽章） |
| W1-d `C2/C3/C10` 指名引用 | `pc-inherited-c2/c3/c10` 均含「承接位置」；`C10` 呈现**产品级** `salesBoundaries`（含 `boundaryKind`/`riskCategory`/`mandatoryDisplay`/`text`），为空时**具名**标注 |
| W1-e `C12` | `PROD-FIN-*` 3 卡渲染 `EvidenceRef` 原文；其余卡**具名缺失**（非空白） |
| **卡间节号错位**（实现者自报修复） | `PROD-FIN-003`：§11=`EvidenceRef`、§12=`不可变版本语义` ⇒ 版本区必须绑 **§12**、`C12` 必须绑 **§11**（不得错配） |
| W1-g 三判定文档 | `memory/waves/W1-g-同产品对照.md` 是否**诚实**：落点 12/12 可复核；**来源可达**与**操作路径更短**须有实测依据；**「事实等价未验证」必须如实保留**；**不得**出现任何"用时"结论；**不得**声称"新版优于 P38" |
| 门禁与证据自洽 | `EVIDENCE.json` 的 `command` 与 `LOOP.yaml` **逐字一致**；对 `evidence_file` 重算 sha256 == `output_sha256`；`Revision epoch 1` 的开启理由在 `W0-ITER.md` 可查（`--revision-note` 使用正当） |
| 失败未被粉饰 | `make check` 的 `semantic-consumption`=**READINESS NOT MET**、`gate-injection-tests`=**INCONCLUSIVE** 必须如实保留，不得被宣称通过 |

### 3. 证据与产出
- 报告（仓内）：`loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-<YYYYMMDD-HHMM>.md`
  （结构：总判 PASS/REJECT/BLOCKED · 甲/乙逐项 · 缺陷清单 · **未覆盖/存疑（必填）** · 环境变动 · 原始产物索引）
- 每个 FAIL 附：最小复现 + trace/截图/响应体 + console 原文
- 逐章/逐块结构化 JSON 建议落同目录（结构对齐 `w1-per-chapter-evidence.json`）

### 4. 签署（**仅在结论为 pass 时**）
```bash
python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
  --actor independent_qa --session <你的会话名> --decision pass \
  --evidence loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-<ts>.md
```
- 若发现问题 ⇒ 用 `--decision reject`，并在报告里给出**具名阻断项**（脚本同时要求实现证据有效且 loop 处于 `ready_for_independent_qa`）。
- **禁止**：`--actor` 填 `tech_lead`；代签；把 BLOCKED 说成通过。

### 5. 完成判据
甲/乙两侧均有结论（含 BLOCKED 具名原因）；每个 FAIL 有证据；「未覆盖/存疑」非空；未违反 §0；末尾一句话：**PC-i1 是否可签 `QA_PASS`**，及未满足项。
