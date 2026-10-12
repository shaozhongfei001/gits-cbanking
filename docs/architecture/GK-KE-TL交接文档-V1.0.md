# GK-KE 全局 TL 交接文档

> **交接时点**：2026-09-13
> **交接 HEAD**：`19fd228`（工作区干净）
> **上手前请先运行 §六 的验证命令** —— **本文所有状态均为实测，但你需要自己复现一遍。**

---

## 一、三十秒理解本项目的主题

> 本项目做过一个声称：**上游能力（事实对账）的输出，已被下游能力（KYC 缺口）语义消费。**
>
> **全部工作的实质是：验证这个声称，以及验证"我方用于验证它的工具本身是否可信"。**
>
> **结论：该声称未达成。** 当前证据：独立判定 `PASS 0 / FAIL 1 / INCONCLUSIVE 4`。

**这不是一个功能开发项目，是一个"可信度"项目。** 新 TL 最需要理解的是这一点：
**任何"看起来好了"都是可疑的；唯一可信的是"可复现的命令 + 原始输出"。**

---

## 二、当前状态（实测）

```
HEAD                          19fd228   工作区干净
门禁链                        22/23 通过（1 项 INCONCLUSIVE 不计入通过）
  READINESS NOT MET           ['semantic-consumption']
  INCONCLUSIVE                gate-injection-tests（覆盖不完整，见 §四）
loop 实例棘轮                 58/58 合规，基线 0 条
GK16 loop                     phase=closed_owner_authorized_data_constructed
```

**唯一 FAIL = `semantic-consumption`** —— 这是**独立判定**的结论，
**TL 不得代判、不得推翻**。它是当前项目最核心的事实。

---

## 三、最近的实质变更（按时间倒序，均为已提交）

| commit | 内容 |
|---|---|
| `19fd228` | 验收独立判定；修它指出的两处**我方缺陷**（观测过期、`coverageStatus` 枚举越界） |
| `be4b91b` | 验收外部 loop 修复；修它报的 4 项 schema 缺陷 |
| `afeec79` | 产出两份外派提示词（语义消费独立复判、loop 实例修复） |
| `00201d2` | **构造仿真数据**：把"空占位"适配器换成内部自洽的仿真内容 |
| `5ea981c` | 终结 T-14/T-08/T-06（字段映射合同、loop 词表、实例棘轮） |

### 关键新增产物

| 路径 | 是什么 |
|---|---|
| `loops/GK16-trust-hardening/` | **本次可信度收敛的完整记录**（先读 `FAILURES.md`） |
| `specs/knowledge-architecture/contracts/UpstreamFieldMapping.json` | 显式字段映射合同（13 字段全映射） |
| `/home/szf/dev/Leibniz-KERT/src/kert/infrastructure/adapters/sim_bank_front.py` | **仿真数据构造器**（跨仓！） |
| `evidence/gk-ke-semantic-consumption/observations-CURRENT-simulated.json` | 当前实现下的观测 |
| `docs/architecture/GK-KE-语义消费独立复判-派发提示词-V1.0.md` | 待外派 |
| `docs/architecture/GK-KE-loop实例合规修复-派发提示词-V1.0.md` | 已完成，保留存档 |

---

## 四、未完成项（**每一项都有明确归属，不是"没人管"**）

| # | 项 | 归属 | 说明 |
|---|---|---|---|
| 1 | **`semantic-consumption` NOT_MET** | **独立执行者** | 判定已作，TL 不得代判。**新观测已就绪，需另一名独立执行者复判**（提示词已备） |
| 2 | 判据 V1.2.1 **自称预注册但全库零引证** | **判据作者侧** | 最严重的档案缺口。**不得由 TL 改判据内容** |
| 3 | 判据 V1.2.1 **无 §观测 一节** | 判据作者侧 | 委托所指观测路径**悬空** |
| 4 | 判据 S2/S3 **可被空转满足** | 判据作者侧 | **已由两轮独立复核确认**的设计缺陷 |
| 5 | GKC/P38 共 **4 个人工 gate** | 各 loop 负责人 | 现**显式阻碍关闭**（见 §五·3） |
| 6 | **30 条历史 loop** 的细粒度结构已丢失 | 已发生，仅存 git 历史 | 外部执行者已如实声明 |
| 7 | 旧格式迁移脚本缺失 | 未派 | 独立工作项 |

**`gate-injection-tests` 的 INCONCLUSIVE 是设计上的诚实**：仍有 2 项正当排除 + 1 项只读跳过（见 §五·4）。

---

## 五、新 TL **必须知道**的六件事（否则会重犯我的错）

### 1. 本仓最常见的失败形态：**"文本说对、结论说错"**

下游在 `warnings` 里写"规则覆盖不足"，**但结论字段 `kycGaps` 是空的**。
⇒ **任何基于关键词/文本的启发式都会误判。必须看结论字段本身。**

### 2. `INCONCLUSIVE ≠ 通过`，且**不得被"未执行"顶替**

- `NOT_RUN` / 空集合 / `NOT_PROBED` **不得**读成"查了、没问题"
- 判据 `S2_EMPTY_MEANS_NONE` / `S3_NOT_RUN_NOT_NONE` 就是为此设立
- **`loop_guard` 的证据状态词表已含 `inconclusive`**；`expected_exit_code` 已被支持

### 3. 有两种"可疑的通过"，机制已建立但**机制本身需要你维护**

```
[MANUAL-GATE]  1 个 gate 为人工工作项（不可执行 ⇒ 不得声称 pass ⇒ 阻碍 loop 关闭）
[REVERSE-GATE] 1 个 gate 的通过条件是『命令失败』：repro_baseline(expected_exit_code=1)
```

- **人工 gate 永远不得 `pass`** ⇒ 只要存在它，loop 就无法关闭。**这是设计，不是 bug。**
- **反向 gate（负例/红测）**：`expected_exit_code≠0` 每次运行都被打印。
  **残余风险如实存在**：可被用来把失败洗成通过，**唯一防线是"必然被看到"**。
- **你必须维护这两条**：新增人力工作项时不要试图绕开。

### 4. 注入测试覆盖了 18 个门禁，**剩余 3 项是正当的**

| 类别 | 门禁 | 为何正当 |
|---|---|---|
| 自指 | `probe-mutation-tests` | 自身即变异测试，注入需改被测脚本 ⇒ 证据自我指涉 |
| 独立性 | `semantic-consumption` | 判定由独立执行者作出，**TL 攻击它即违规** |
| 只读 | `semantic-rule-gate` | 制品受保护，**按纪律不放开写位**（曾有事故） |

**不要为了"覆盖率好看"去攻击这三项。**

### 5. **我犯过的错，按类型（这是本交接最有价值的部分）**

| 类型 | 实例 |
|---|---|
| **"宣布 X 之前没查"** | 宣布"某控制未建"之前没搜索全仓（**实际早已强制**）；宣布"收敛"之前没攻击 7 个门禁 |
| **"读代码就下结论"** | 连续两次"读代码推测缺陷"，两次被实测证伪 |
| **"编辑没生效却以为生效"** | `PRECISE` 字典**重复键静默覆盖** ⇒ 我"加了注入器"但生效的是旧的。**所有编辑只用"文本是否存在"自证** —— 而"文本在"≠"生效的是这条" |
| **"看统计数字就下结论"** | `diff --stat` 显示删除远多于新增 ⇒ 我判"删内容换合规"，**实际是格式重写，删除文件数 = 0** |
| **"修一个、写一个同族缺陷"** | 修 `chain-trace` 的 `all([])==True` 时，在 `capability-probe` 写了 `if results and ...`（空集合短路）—— **同族** |
| **"没读契约就写实现"** | 写仿真器时随手取 `coverageStatus="INSUFFICIENT"`（**不在技能自己的枚举内**），导致一个判据**在任何环境下都无法判定** |

> **共同根因**：**"我以为"替代了"我验证"。**
> **对策**：任何结论必须附**可复现命令**；任何"通过"必须有**负例测试**。

### 6. 跨仓注意

**仿真适配器在 `/home/szf/dev/Leibniz-KERT`，不在本仓。**
改它要另开工作区；本仓的 `chain-trace` 会**真实调用**它。
**该仓的 `git status` 也需保持干净** —— 我上次提交时差点漏掉。

---

## 六、上手验证（**请逐条跑，不要相信本文**）

```bash
cd /home/szf/dev/gits-cbanking && git status --porcelain     # 应为空
python3 scripts/run_gates.py                                 # 22/23，READINESS NOT MET: semantic-consumption
python3 scripts/loop_guard.py --instances-check              # 58/58，基线 0 条，exit=0
python3 scripts/gate_selftest.py                             # 分类器用例 10/10
python3 scripts/gate_injection_tests.py                      # 18 项受控检出 / 0 崩溃 / 0 未确立
python3 scripts/gk_ke_chain_trace.py                         # CHAIN_TRACE_PROVEN_INPUT_LEVEL（输入级，非语义级）
python3 scripts/loop_guard.py --loop GK16-trust-hardening    # PASS
cd /home/szf/dev/Leibniz-KERT && git status --porcelain      # 应为空
```

**若任一项与本文不符 ⇒ 先查差异，不要按本文继续。**

---

## 七、不得做的事（硬约束）

1. **不得修改判据文档内容**（`docs/architecture/GK-KE-语义级消费验证方案-*.md`）—— 作者已移交独立方
2. **不得代判 `semantic-consumption`** —— 独立性是硬要求
3. **不得为让门禁变绿而改合同** —— 合同忠实于 §9.3 原文；改它就是"迁就实现"
4. **不得放开只读制品的写权限**（曾有事故：写坏了受保护制品且 git 无法恢复其权限）
5. **不得把"未执行/未探测/空集合"记为通过**
6. **不得在未做负例测试的情况下新增门禁** —— 否则它会成为新的"看起来有防线"
7. **不得删改独立判定文件、`report.json`、观测文件** —— 新增可以，覆盖不行

---

## 八、建议的第一步

1. 跑 §六 全部命令，确认状态
2. 读 `loops/GK16-trust-hardening/FAILURES.md`（T-01 ~ T-20，**这是本项目最有价值的文档**）
3. 读 `loops/GK16-trust-hardening/INDEPENDENT-JUDGEMENT-DISPOSITION.md`
4. **决定是否把第 1 项（新观测下的语义消费复判）派发出去** —— 提示词已备好
5. **不要急着"推进功能"** —— 本项目的价值在于**把"不可信"变成"可信"**

---

## 九、TL 的一句自述

> **我做的大部分工作，不是让东西工作，而是发现"我以为工作的东西其实没工作"。**
>
> 这里面有 **21 条失败记录**（T-01 ~ T-21），其中**至少 7 条是我在修复过程中新造的缺陷**。
> **T-21 尤其值得注意**：该文件自身曾被**多次整文件覆盖**，致 T-01~T-11 丢失，
> 后从 git 历史 7 个版本重建。**教训：记录类文件必须追加，不可重写。**
> **它们被记下来，不是为了自责，而是因为它们全都属于同一族：**
> **"用一个看起来对的东西，替代一个被验证过的东西。"**
>
> **新 TL 若只继承一件事，请继承这条：**
> **不要相信任何未附可复现命令的结论 —— 包括本文。**
