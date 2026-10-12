# ONTO1｜ARCH-ONTO-2026-001 复审轮「送审操作清单」V1.0

| 项 | 值 |
|---|---|
| 文档编号 | `ONTO1-W-1-SUBMIT-01` |
| 版本 / 日期 | V1.0 / 2026-09-20 |
| 编制角色 | `architect-review-liaison`（Tech Lead 侧程序与文书包；**不含技术判断、不代表委员会结论**） |
| Baton holder | `tech_lead`（本文书落盘后 Baton 仍为 `tech_lead`） |
| 依据 | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md`（V1.1）、`13-送审函-书面复审.md`、`14-书面复审决议签署页.md`、`ARCH-ONTO-2026-001_整改复审意见_V1.0.md` §5/§6/§7、`docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §0、`loops/ONTO1-ontology-split/LOOP.yaml` |
| 当前门禁 | `RETURN_TO_HLD`（有效）→ 目标 `DESIGN_APPROVED`，上限 `PASS_WITH_REQUIRED_CHANGES` |
| 本文书性质 | **程序就绪清单**。它不构成送审、不构成批准、不构成结论；**发出与签署只能由 Owner / 委员会执行** |

---

## 1. 前置校验（本会话已完成，可复算）

| # | 检查 | 命令 | 结果 | 证据 |
|---|---|---|---|---|
| 1 | 01~12 与 V1.0 冻结哈希逐字一致 | `python3 scripts/onto1_review_package_check.py --gate` | `[R1] 12/12` | `evidence/wi_review_package_integrity-20260920T141501Z.log`（`sha256 23e0bf34…`） |
| 2 | 可签署载体 13/14 齐备 | 同上 | `[R2] ['13-送审函-书面复审.md','14-书面复审决议签署页.md']` | 同上 |
| 3 | MANIFEST 登记项自洽（存在 + 哈希一致） | 同上 | `[R3] MANIFEST 登记 14 件` | 同上 |
| 4 | 门禁有牙齿（变异复验） | `python3 scripts/onto1_review_package_check.py --selftest` | `M1` 静默改 01 ⇒ FAIL；`M2` 删 14 ⇒ FAIL；`M0` 对照 ⇒ PASS | `evidence/wi_review_package_selftest-20260920T141504Z.log`（`sha256 0f5f502c…`） |
| 5 | 重打包命令预演（**仅写 `/tmp`，未产出仓库制品**） | 见 §3 步骤 2 | 解包清单 **16 项**（1 目录 + 15 件） | `evidence/review-submission-zip-dryrun-20260920T1415Z.log` |

**受检包定型值**（与 MANIFEST V1.1 一致，此轮不得再改）：

| 件 | SHA-256 |
|---|---|
| `13-送审函-书面复审.md` | `964a546c86e5cf80633a0b75e733d227c22a618a23d36cd13709b1145d20a4ef` |
| `14-书面复审决议签署页.md` | `df2933d1e183b9d50e98d784ab7f1c342a589b7e558f5202780f71601eb826c8` |

> **诚实声明**：上述门禁只证明**包内自洽、13/14 齐备、01~12 未发生静默漂移**；它**不证明包内内容技术正确**。技术正确性只能由委员会书面复审裁定。

---

## 2. 送审件角色与待填位（**委员会侧由 Owner 指定后填入，TL 不得代填/代签**）

### 2.1 送达对象（`13` 表头「送达对象」对应）

| 角色 | 姓名 | 单位 / 部门 | 送达渠道 | 送达日期 |
|---|---|---|---|---|
| 委员会主席 | （待 Owner 指定） | | | |
| 架构委员（语义/本体） | （待 Owner 指定） | | | |
| 架构委员（集成/合同） | （待 Owner 指定） | | | |
| 架构委员（数据/标准） | （待 Owner 指定） | | | |
| 秘书处（汇总人） | （待 Owner 指定） | | | |

### 2.2 项目侧（已定，仅待 Owner 在 `13` 末页确认）

| 角色 | 落位 | 状态 |
|---|---|---|
| 送审单位 | GITS-KERT 联合项目架构组（全局架构师执笔；TL 侧送审） | 已在 `13` 表头写明 |
| 送审单位代表（全局 Tech Lead） | `13` 末页签署区 | **待签（仅 Owner 可批准发出）** |
| 项目负责人 / Owner 确认送审 | `13` 末页签署区 | **待签** |

### 2.3 表决与汇总（`14` 签署表 5 个签署位）

主席 1 + 委员 3 + 秘书处汇总人 1。**姓名/签字/日期栏必须全部留白直到委员会填写**；项目侧不得预填、不得代签、不得先填结论倾向。

---

## 3. 交付方式（推荐 B：重打包 zip 含 13/14）

| 方案 | 做法 | 判断 |
|---|---|---|
| A 只给目录路径 | 委员直接读 `docs/review/ARCH-ONTO-2026-001-rereview-package/` | **不推荐**：委员需访问代码仓，破坏「自含性」，且无法固定"委员看到的就是受检包" |
| **B 重打包 zip（推荐）** | 见下方三步 | **采用**：可复算、可留痕、与 MANIFEST 哈希可对证 |
| C 纸质/电子直发 | 打印或 PDF 直送 | 若组织流程要求，可与 B 并行；结论仍以 `14` 为准 |

**步骤 1（打包；Owner 侧执行）**

```bash
cd /home/szf/dev/gits-cbanking/docs/review
zip -r -X ARCH-ONTO-2026-001-rereview-package.zip \
    ARCH-ONTO-2026-001-rereview-package -x '*.DS_Store'
unzip -l ARCH-ONTO-2026-001-rereview-package.zip | tail -3   # 期望 16 项
```

- 新包名 `ARCH-ONTO-2026-001-rereview-package.zip` 与旧包 `ARCH-ONTO-2026-001-committee-package.zip` **不同名**；
- **禁止**覆盖/复用旧包；旧包内 `00-送审函与阅读指南.md`、`08-评审决议签署页.md` 属已归档轮次，其裁定项（三层模型 / 沿用 `gits:` 前缀 / Product 归 KERT）**已被委员会推翻**，随旧包分发会造成误引；
- 若同名文件已存在，先确认来源与轮次再决定去留，不得无条件覆盖。

**步骤 2（打包后自证：发出的包 == 受检的包）**

```bash
rm -rf /tmp/onto1-sent-verify && mkdir -p /tmp/onto1-sent-verify
unzip -q -d /tmp/onto1-sent-verify \
    /home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001-rereview-package.zip
cd /tmp/onto1-sent-verify/ARCH-ONTO-2026-001-rereview-package && sha256sum * | sort > /tmp/onto1-sent.txt
cd /home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001-rereview-package && sha256sum * | sort > /tmp/onto1-src.txt
diff /tmp/onto1-src.txt /tmp/onto1-sent.txt && echo SENT_PACKAGE_IDENTICAL
```

`SENT_PACKAGE_IDENTICAL` 是发出前的硬条件；若 `diff` 非空 ⇒ **停止发送**并查打包范围（禁把临时/隐藏文件带出）。

**步骤 3（发出前最后一道）**

```bash
cd /home/szf/dev/gits-cbanking && python3 scripts/onto1_review_package_check.py --gate
```

必须 PASS。若 FAIL（例如有人在打包期间改了 01）⇒ 按 `FAILURES.md` **先记后修**，**不得**"改了哈希就发出"。

**附件范围**：`MANIFEST.md` + `01`~`14`，共 15 件。**不附**旧包任何文件、不附仓库路径说明、不附未定稿草案。

---

## 4. 期限、回执与催办

| 项 | 值 | 依据 |
|---|---|---|
| 建议反馈期限 | **2026-10-09**（自送达起 10 个工作日） | `13` §四；与 D1 目标日期同日 |
| 汇总责任方 | 委员会秘书处（汇总人） | `13` §四 / `14` 签署表 |
| 送达回执 | 渠道 + 收件人 + 日期三项须回写本清单 §2.1 | 程序留痕 |
| 阻塞级意见格式 | 必须指明**具体文件号 + 条款** | `13` §四；`14`「意见与条件」 |
| 逾期（2026-10-09 未回任何回执） | 登记 `OVERDUE`，由 **Owner** 催办；项目侧**保持 `RETURN_TO_HLD`，不静默推进** | `LOOP.yaml.gate_state` |
| 催办动作 | 由 Owner / 秘书处执行；TL 只可提交「待办提醒」，不得替委员会设定结论 | 红线 |

---

## 5. 回收路径（唯一入口，避免多头收件）

```text
秘书处汇总人填写并签署 14
   └─▶ 交付「送审单位代表（全局 Tech Lead）」
          └─▶ 归档到 docs/review/（见 5.1）
                 └─▶ 记账：sha256 + 有效件登记（见 5.2）
                        └─▶ 24 小时内执行《结论回收与门禁更新预案》
```

### 5.1 归档位置（到达后落位，未到达前**不预建**）

| 件 | 建议落位 | 说明 |
|---|---|---|
| 已签署的 `14`（原件/扫描件/电子签署） | `docs/review/ARCH-ONTO-2026-001_委员会书面复审决议_V1.0-<YYYYMMDD签署>.md`（或同名 `.pdf` 影像） | 结论唯一载体；**不得**改名后失去可追溯性 |
| 原始签署页非电子件 | 秘书处留存原件；项目侧存影像 + 哈希 | 影像哈希进记账 |
| 送达/回执记录 | 本清单 §2.1 回填 + `EVIDENCE.md` | 程序证据 |

### 5.2 记账要求（到达即做，先记账后动作）

1. 计算归档件 `sha256`；
2. 写 `loops/ONTO1-ontology-split/evidence/review-submission-verdict.json`：`{file, sha256, signed_at, signers[], verdict_item1, received_at, received_by}`；
3. 追加 `EVIDENCE.md`（人类导航层，不复制状态）；
4. **回收件本身不得被后续动作改写**（改即失真；如需补正另存新版本并保留原件）。

### 5.3 回收件有效性判定（fail-closed：不合格 ⇒ 退回补正，**门禁不动**）

| 检查 | 不合格判定 |
|---|---|
| 决议 1 恰好勾选一项 | 未勾 / 多勾 ⇒ `INVALID_RETURN` |
| 勾选第 2 项 ⇒ `1a` 必要条件非空 | 空白 ⇒ `INVALID_RETURN` |
| 勾选第 3 项 ⇒ `1b` 退回理由非空且含文件号/条款 | 空白或仅"方向问题" ⇒ `INVALID_RETURN` |
| 决议 4 选「有条件」⇒ 未关闭项表非空 | 空白 ⇒ `INVALID_RETURN` |
| 决议 5/6 选「要求修改/补充」⇒ 列明项非空 | 空白 ⇒ `INVALID_RETURN` |
| 签署表含主席 + 秘书处汇总人签字**与日期** | 缺任一位或缺日期 ⇒ `INVALID_RETURN` |
| 知悉确认三项已勾 | 未勾 ⇒ 记 `OBSERVATION`（不阻断，但要求补勾） |

`INVALID_RETURN` 的处置：退回秘书处补正；**不得**据此更新 `LOOP.yaml.gate_state`、**不得**启动任何 Wave。

---

## 6. 发出前红线自查（逐条打勾，缺一不发）

- [ ] 未代替委员会出具任何结论（本清单只写"收到后做什么"）
- [ ] 未替 Owner 签署：`13` 末页 Owner 确认栏、`14` 全部签署栏**保持空白**
- [ ] `RETURN_TO_HLD` 仍有效；Wave 0 及以后**零动作**（禁标 `DESIGN_APPROVED`/`FROZEN`、禁拆本体、禁切消费入口、禁正式重钉）
- [ ] 01~12 零改动（`[R1] 12/12`）；`MANIFEST` 仍为 **V1.1**
- [ ] 若发出后 01~12 任一件需要改动 ⇒ 必须走「重发快照 + 重算哈希 + MANIFEST 记版本沿革」升 V1.2 并重发，**禁止静默改哈希**
- [ ] 分发范围仅限指定委员 + 授权秘书处（`13` 密级：内部资料）
- [ ] 未夹带旧送审包文件，未引用其已被推翻的裁定项
- [ ] 未使用 `git add .`（`docs/dd/` 下有未跟踪文件）

---

## 7. 程序完成记录（**非批准、非签署**）

| 项 | 值 |
|---|---|
| 结论回收链路 | 已建立（本清单 + 《结论回收与门禁更新预案》V1.0 + 包级 handoff），落盘 `memory/handoffs/` |
| 编制人 / 时间 | `architect-review-liaison` / 2026-09-20T14:15Z（本地 22:15） |
| 门禁证据 | `wi_review_package_integrity` PASS（Attempt 2，`23e0bf34…`）；`wi_review_package_selftest` PASS（Attempt 2，`0f5f502c…`） |
| 项目侧状态 | `in_progress` / Wave -1 / `blocked=false` |
| **Owner 唯一待办** | `memory/OWNER_REQUESTS.md` §C-1-a ~ C-1-e（指定评审人 → 批准发出 → 交付包 → 设定期限 → 收回签署页） |

> 本清单**不启动**任何后续动作：**未收到正式签署件前，项目侧保持 `RETURN_TO_HLD`，Wave 0 及以后全部禁止。**
