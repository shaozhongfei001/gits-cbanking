# GITS-KERT 交付物架构评审 · Tech Lead 意见 V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对象：《GITS-KERT CodeBuddy 交付物架构评审报告 V1.0》（GK-KE-AR-20260911-01）
> 结论：**接受架构评审报告的退回决定（RETURN_TO_HLD / INSUFFICIENT_EVIDENCE），启动 AR-R0→R5 整改。**

---

## 一、结论摘要

机构委员会架构评审报告（下称"报告"）对当前交付的判定——**契约符合性退回补正、设计包完整性与实现完成效果证据不足**——经 TL 逐项复核后**全部成立，予以接受**。

报告所固定的文档身份、所列 11 项发现（F01–F11）、C01–C08 覆盖缺口、以及 5 张整改工作单（AR-R0–R5）均指向真实且可复现的问题，不是误判。本意见不推翻报告，而是补充 TL 已核实的客观事实、明确整改责任与执行顺序，并落盘为下一轮交付的依据。

---

## 二、TL 已核实的客观事实（作为整改起点）

| # | 事实 | 核实结果 | 对报告的意义 |
|---|---|---|---|
| 1 | 总契约 `GITS-KERT_知识工程体系_项目总契约_V1.0.md` | 存在于 `/home/szf/dev/gits-kert-docs/dd/`，SHA-256 = `a4abb089b663a904ee08c0db90dd8426052fba584b1d81f56a41f0564067830f`，**与报告 F01/§1.2 固定的 A 完全一致** | 报告固定依据正确；总契约不在 `gits-cbanking` 仓库内，是独立的 `gits-kert-docs` 目录 |
| 2 | 交付包 `GK-KE-CONTRACT-V1.0/` | 存在于同目录，含 `MANIFEST.json`、`tools/validate_package.py`、`acceptance/package_self_check.json` | 实物存在，与报告 F02"未取得实物"的表述形成差异——实物已在提交者环境，但**未随评审材料提交**，故报告结论仍成立 |
| 3 | MANIFEST 文件数 | 实际 `files` 数组 = **117 项**，非清单 §1 声称的 100；目录含 `.venv` 等合计 1676 个文件 | 证实报告 F10"计数口径不一致"成立；100 与 117 的差需区分"去重受控文件数 vs 分类引用数" |
| 4 | 包自检 | `tools/validate_package.py` 可复现运行，输出 `passed: 125, failed: 0`，`acceptance/package_self_check.json` 内 `checks` 数组 = 125 项全 PASS，且正确标注 5 项 `NOT_PERFORMED` | 证实报告 F09：125/0 是**作者离线自检**，`scope=OFFLINE_AUTHOR_SELF_CHECK`、`independentQa=NOT_PERFORMED`，不是独立 QA，不得继承 |
| 5 | `gits-cbanking` 仓库 HEAD | `81a058ff288ab73c20f2bb9142fab04db6d3f493`，最新提交即"docs(dd): add GITS-KERT V1.0 deliverable architect review checklist" | 报告 F02"无 HEAD/源码/运行证据"成立——仓库当前只含评审清单与报告两份文档，不含本次交付包本体 |
| 6 | 评审清单 §12 声明的"已落地" | 与仓库实际代码（modules/adapters/apps/scenario + P22/P23 记忆）方向一致，但**无本次交付包的逐项映射** | 证实报告核心判断：清单是设计/组织包，不是实现证据 |

**一句话定位**：这不是"评审报告挑刺"，而是"提交物把设计包当作完成交付、且依据与范围未对齐"。TL 接受退回是正确选择。

---

## 三、对 11 项发现（F01–F11）的 TL 定性

| 发现 | 级别 | TL 定性 | 处置 |
|---|---|---|---|
| F01 总契约身份与引用体系未对齐 | BLOCKER | **成立**。清单 §1–§11 引用了"§0.3 十层/§2.2 17 端点/§2.4 12 事件"等 A 中不存在的章节，确实存在按另一版本验收的风险 | 归入 AR-R0 |
| F02 只有清单、缺本次交付实物 | BLOCKER | **部分成立**。实物其实存在于提交者环境（本意见已核实），但**未随评审提交**，评审方无法独立读取 | 归入 AR-R1（补交实物与 hash） |
| F03 系统权威与迁移合同未落实 | MAJOR | **成立**。对象权威矩阵、CR-01/02 迁移证据未在清单建立 | 归入 AR-R2 |
| F04 知识地图与注册中心无运行合同 | MAJOR | **成立**。六类注册模块、三视图、确定性/权限合同未逐项 | 归入 AR-R2 |
| F05 自动建图→审核发布主链无独立验收 | MAJOR | **成立**。知识认定流水线（Source→Fragment→Candidate→Review→Release→Revoke）未走完一个完整设计实例 | 归入 AR-R2 |
| F06 分析语义服务覆盖不足 | MAJOR | **成立，优先级最高**。MetricDefinition、Owner、受控 QueryPlan、C001 日均 2,983,333.33 CNY 复算均无证据 | 归入 AR-R2，优先 |
| F07 RAG 与图适配未证明符合边界 | MAJOR | **成立**。ExistingRagAdapter 来源/ACL、Kuzu 可重建投影、LightRAG 可关闭试验均无合同 | 归入 AR-R2 |
| F08 种子样例未覆盖完整模拟闭环 | MAJOR | **成立**。缺 720 账户日余额等最小参考数据、UNKNOWN/回执负例、3000 万经营场景 | 归入 AR-R3 |
| F09 自检与历史 QA 声明缺范围绑定 | MAJOR | **成立**。125/0 与 1808/0.8001 均未绑定本次 HEAD/范围/原始报告 | 归入 AR-R4 |
| F10 文件与事件计数口径不一致 | MINOR | **成立**。100 vs 117（MANIFEST 实为 117）、JSON 8 vs 至少 10、12 类 vs 18 事件名 | 归入 AR-R4 |
| F11 局部治理用语需限定范围 | MINOR | **成立**。Flyway 表述、Supervisor 不提问表述需限定适用范围 | 归入 AR-R4 |

---

## 四、整改工作单执行顺序与责任

采纳报告 §6 的 AR-R0–R5，TL 补充执行顺序与责任分工：

| 顺序 | 工作单 | 责任 | 关键动作（TL 补充） |
|---|---|---|---|
| 1 | **AR-R0 固定评审依据** | TL + 契约 Owner | 将 `gits-kert-docs/dd/` 下的总契约纳入版本控制或明确其权威位置；给出与 A 的 diff；明确本次为 **D（设计包）阶段**交付，非 I/A |
| 2 | **AR-R1 补交实物与追踪** | Feature Pilot + TL | 提交 MANIFEST（117 文件，含逐项 sha256）、validate_package.py、package_self_check.json 原始输出；建立 REQ/C/CR/Loop/T → 路径/符号/测试 映射表 |
| 3 | **AR-R2 修复核心设计覆盖** | 各领域 TL/Owner | 依次补：权威矩阵 → 六注册/三视图 → 构建发布主链 → MetricDefinition/受控查询 → RAG/图适配；**先补 F06 分析语义**（业务正确性风险最高） |
| 4 | **AR-R3 复用模拟闭环** | 模拟平台/KERT/GITS | 复用原样例、复算 C001 指标、验证 UNKNOWN/回执负例、准备 3000 万经营场景 |
| 5 | **AR-R4 重做验收证据** | 开发 + 独立 QA | 按 117 文件重生成自检；单列历史 QA（125/0 与 1808 分开，各自绑定 HEAD）；修正 F10 计数与 F11 用语 |
| 6 | **AR-R5 复审与决定** | TL 提交，架构/QA/Owner 各司其职 | 逐发现项提交"问题—实际变更—制品版本—验证输入输出—残留项" |

**红线（TL 重申，报告 §7 一致）**：
- 不直接改 `generated/`，合同变更走 `specs/` → `make generate` → `make check`。
- 不擅自替换 P20/DKES/PI-0，不模拟真实 Owner 签署。
- 开发只记 `DEV_SELF_CHECK_PASS`；独立 QA 才记 `QA_PASS`。
- 历史 125/0、1808 测试、安全 QA **不继承**为本次验收。

---

## 五、TL 对报告的一点校正说明

报告 F02 措辞为"本轮没有取得相应包、MANIFEST、自检脚本"，TL 已核实这些实物**确实存在于提交者环境**（`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/`），只是**未随评审材料一并提交**。

这不改变报告结论——评审方确实无法独立读取，退回仍成立——但整改时 AR-R1 的动作应是"**提交（打包/提供可访问路径）**"而非"**重新生成**"。MANIFEST 实际 117 项也印证 F10：清单"100 文件"的计数口径需要澄清，而不是实物缺失。

---

## 六、下一轮提交包（与报告 §8 对齐）

1. **依据**：总契约全文 + hash（`a4abb089...`）+ 与 A 的 diff + 批准/待批准状态。
2. **实物**：`GK-KE-CONTRACT-V1.0/` 完整目录（或精确仓库地址+提交号）+ MANIFEST.json（117 项逐项 sha256）。
3. **自检**：validate_package.py + 依赖记录 + package_self_check.json 完整输出 + 运行命令。
4. **实现证据**（若申请实现验收才需要）：各仓库 HEAD + diff + 构建/运行结果 + 请求/trace + 测试原始报告。
5. **验收与整改**：T01–T36 状态表 + F01–F11 关闭证据 + 独立 QA 签署范围 + Owner 决议。

---

## 七、TL 落盘声明

```
[裁决] 对象: GK-KE-AR-20260911-01, 决定: 接受退回, 阶段: D(设计包)
       依据: 总契约 a4abb089...(已核实一致), MANIFEST 117 文件(非100), 自检 125/0(作者离线自检)
       整改: AR-R0→R5, 优先 F06 分析语义, 责任: TL/各领域 Owner/独立 QA
```

本意见作为 TL 对机构委员会评审报告的正式响应，落盘于 `docs/dd/`，供下一轮整改与复审引用。
