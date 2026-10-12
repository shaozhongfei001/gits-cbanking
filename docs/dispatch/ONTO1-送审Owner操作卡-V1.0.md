# ONTO1 送审·Owner 操作卡（3 分钟版）V1.0

> 目的：把"最硬卡点"压缩成**只需人类做三件事**：填 4 个名字、勾 6 个框、跑 3 条命令。
> 详细说明见《送审操作清单》V1.0（`loops/ONTO1-ontology-split/memory/handoffs/ONTO1-W-1-送审操作清单-V1.0.md`）。
> **TL 不得代发函、不得代签**；本卡只是把动作排好序。

---

## 第 1 步（1 分钟）：填 4 个名字

打开 `docs/review/ARCH-ONTO-2026-001-rereview-package/14-书面复审决议签署页.md`，最底部签署表填：

| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 委员会主席 | | | |
| 本体语义架构委员 | | | |
| 数据治理委员 | | | |
| 集成架构委员 | | | |
| 秘书处（汇总人，**TL**） | | | |

同时把 `13-送审函-书面复审.md` 表头「送达对象」补上这些人（或写"详见 14 签署表"）。

> **强制约束（Owner 2026-09-21 最终决议第 4、6 条）**：《14》的**六项技术结论必须由具名评审组完成评审后分别确认**——**不得**由项目 Owner 在发函前**预填或代勾**。
> 若项目 Owner 依法兼任其中一个评审角色，**只能签署自己对应的角色意见**，**不能替代其他评审角色或代表整个委员会签署**。
> 未形成规定的独立评审角色与有效签署结果时，**只能记录为 `OWNER_REVIEW`**，**不得**记录为 `ARCHITECTURE_COMMITTEE_APPROVED`。

> **⚠ 隐藏前置（2026-09-21 收口时补登，`OWNER_REQUESTS.md §C-3`）**：本页第 1 步**不能直接照做**，因为
> ① `14` **在冻结包内**（哈希 `df2933d1e183b9d50e98d784…`，与包内 MANIFEST 一致）——**填入姓名会改哈希、破坏包自洽**；
> ② 冻结包 `14` 的签署表沿用**旧角色名**，与决议第 5 条的四角色名不一致。
> ⇒ 请先定：**姓名手写填入**（包不动）还是由 TL **重发 V1.2 包**（新哈希 + 重跑 integrity/zip 自证）；以及
> **补 ≥3 位真正独立具名评审**还是**维持 `OWNER_REVIEW`**。

## 第 2 步（1 分钟）：勾 6 个框

仍在 `14`，由**具名评审组按角色分工评审后分别确认**（每位评审只签自己角色对应的意见；**TL 仅汇总与校验，不代答、不代勾**）：

| 决议 | 你要选什么 |
|---|---|
| 1 门禁结论 | ☐ `DESIGN_APPROVED`　☐ `PASS_WITH_REQUIRED_CHANGES`（附条件）　☐ 继续 `RETURN_TO_HLD`（附理由） |
| 2 批准范围路线 | ☐ 确认"缩小批准范围路线"（GB/T 条款级对齐移出基线、禁符合性表述） |
| 3 状态四态分离 | ☐ 确认"委员会只批设计基线，不批实现/QA/激活/生产可用" |
| 4 16 项缺陷关闭核对 | ☐ 逐项已核　☐ 有条件（列明未关闭项） |
| 5 32→45 分口径映射 | ☐ 认可　☐ 要求修改 |
| 6 外部依赖 D1~D4 登记 | ☐ 认可登记（含未决禁止动作）　☐ 要求补充 |

## 第 3 步（1 分钟）：跑 3 条命令

```bash
# ① 打包（在仓库根执行；产物放仓库外或 /tmp，避免误入 git）
cd /home/szf/dev/gits-cbanking
mkdir -p /tmp/onto1-submit && rm -f /tmp/onto1-submit/rereview-package.zip
(cd docs/review && zip -r -X -q /tmp/onto1-submit/rereview-package.zip \
   ARCH-ONTO-2026-001-rereview-package -x '*.DS_Store')

# ② 自证「发出的包 == 受检的包」：逐件比对 zip 内容 vs 仓内冻结件
#    （会额外做一次篡改变异，证明这个证明不是恒真）
python3 scripts/onto1_zip_manifest_verify.py --dryrun
python3 scripts/onto1_zip_manifest_verify.py --zip /tmp/onto1-submit/rereview-package.zip

# ③ 固化回执：记下 zip 的 sha256（与待发件一起登记）
sha256sum /tmp/onto1-submit/rereview-package.zip
```

**期望输出**：
- ② 第一次（dryrun）末行应为 `onto1-zip-manifest-verify: PASS（预演包与仓内冻结件逐件一致；篡改可被检出）`
- ② 第二次（你的 zip）末行应为 `onto1-zip-manifest-verify: PASS`
- 若任一次出现 `hash mismatch` / `missing in zip` / `unexpected extra member` ⇒ **停**，说明包与冻结件不一致，回到 TL 处核对（不得带病发出）

> **注意**：zip 自身哈希会随打包时间变化（`zip` 会记录成员 mtime），因此第 ③ 条命令的哈希**只用于回执登记**，不作为一致性判据。
> **一致性判据是第 ② 条的逐件内容哈希**（2026-09-20 预演实测：`members=15 missing=0 extra=0 mismatch=0`；
> 当次 zip 自身哈希 = `958a33948a9d942c…`，仅供参考，**不要**拿去比对）。

## 发出与回收

| 项 | 内容 |
|---|---|
| 发出 | **由项目 Owner 批准并发出** `rereview-package.zip` + 送达说明；分发动作可由评审秘书处（TL）执行（**仅分发**，不投票、不代签） |
| 期限 | 建议 **2026-10-09**（与 D1 标准文本同批）；逾期建议书面催办 |
| 回收物 | 已签署的 `14-书面复审决议签署页.md`（纸质/电子均可） |
| 回收后放哪 | 放回 `docs/review/ARCH-ONTO-2026-001-rereview-package/`（文件名加 `-SIGNED-<日期>`）并通知 TL |
| 之后 | **TL 在 1 个工作日内**按《结论回收与门禁更新预案》V1.0 更新门禁并通知全部角色（**不需你再操作**） |

## 三条红线（发出前最后确认）

1. **不得改包内容**：01~12 已冻结（门禁 `wi_review_package_integrity` 会拦）；确需改 ⇒ 走"重发快照 + 重算哈希 + MANIFEST 记版本沿革"流程，不得就地覆盖。
2. **不得由 AI 代签**：`13`/`14` 的签署位只能由人类填；AI 会话只能把文件准备好。
3. **签署前保持 `RETURN_TO_HLD`**：在拿到签署件之前，项目侧**不得**启动 Wave 0 及以后任何动作（本体拆分、消费切换、重钉、候选模块标 ACTIVE 一律禁止）。

---

## 附：此刻的完整状态（一句话）

设计 V2.0 的自含复审包（01~14）**已备齐并自证**，只差**人把名字填上、把框勾上、把包发出去**。
其余四类卡点（两个 Owner 角色任命、D1~D4 签署、O-D4-2 差异决议）都在同一批 Owner 待办里，见
`loops/ONTO1-ontology-split/memory/OWNER_REQUESTS.md`。
