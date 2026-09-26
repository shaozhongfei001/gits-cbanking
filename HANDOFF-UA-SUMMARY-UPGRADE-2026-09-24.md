# 交接文档：298 个文件语义摘要升级到 LLM 级

> 日期：2026-09-24｜会话：当前（已结束）｜下一会话：新开会话
> 仓库：`/home/szf/dev/gits-cbanking`（分支 `recover/PI-ARCH-product-catalog`）
> 关联规则：CODE-FACT-INDEX-PROCESS（GOV-CFI-001）· Loop 共享记忆（仅 `.ua/` 派生产物，非 loop 任务）

## 1. 任务目标（已完成）

把代码事实索引 `.ua/knowledge-graph.json` 中 **298 个文件节点** 的
`summary / tags / complexity / languageNotes` 四个字段从「非 LLM / 低质量」升级为
**LLM 级语义摘要**。

硬约束（已遵守）：
- **只改字段值，不改图结构**（节点/边/ID/层/tour 一律未增删）→ 不触发符号守卫。
- **`make index-gate-tests` 必须保持 PASS**。

## 2. 完成状态与核验（已实测）

| 项 | 结果 |
|---|---|
| 298/298 个 reanalyze 路径在 kg 中已设 LLM 级 summary | ✅ 全量覆盖 |
| kg 节点总数 / 边总数 / layers / tour | 4492 / 3545 / 54 / 26 —— 与修改前**完全一致**（结构未变） |
| `make index-gate-tests`（变异复验） | ✅ **18/18 PASS**（含「恢复即 PASS」证明断言非空转） |
| 实际落盘 | `.ua/knowledge-graph.json`（gitignore，未入库，符合「索引永不升格」红线） |

抽样复核（4 个代表性文件，summary/tags/complexity 均已升级）：
- `loops/PC8-reg-cb001-naming/memory/waves/W0-PLAN.md`
- `docs/dispatch/PI-4功能失效诊断与修复计划-V1.0.md`
- `apps/api/src/test/java/com/gien/gits/adapter/skill/ServiceProposalMapperTest.java`
- `loops/PC-i1-chapter-inheritance/evidence/independent-qa-replay-spec-d1-cross-page-20260923-1101.json`

## 3. 关键产物 / 文件位置

- **最终交付物**：`/home/szf/dev/gits-cbanking/.ua/knowledge-graph.json`
  （仅文件节点的 4 个字段被升级；其余内容未动）
- **298 个路径权威列表**来源：在 baseCommit
  `71169042227ce86f870cea81b50f77bf985ffe7f` 下由 understand-anything 的
  `prepare-incremental` 产出（当时存于 `/tmp/ua_reanalyze.json`，见 §5 注意）。
- **批处理元数据**：`/tmp/ua_missing_batches.json`（140 个缺失文件，12 批）。

## 4. 在新会话如何重新核验

```bash
cd /home/szf/dev/gits-cbanking

# 1) 结构完整性（必须无任何差异）
python3 - <<'PY'
import json
g=json.load(open('.ua/knowledge-graph.json'))
print('nodes',len(g['nodes']),'edges',len(g['edges']),
      'layers',len(g['layers']),'tour',len(g['tour']))
PY

# 2) 门禁（必须全绿）
make index-gate-tests

# 3) 抽查某 reanalyze 节点是否已升级
python3 - <<'PY'
import json
g=json.load(open('.ua/knowledge-graph.json'))
m={n.get('filePath'):n for n in g['nodes'] if n.get('filePath')}
p='docs/dispatch/PI-4功能失效诊断与修复计划-V1.0.md'
n=m.get(p)
print(n and n.get('summary')[:80], '|', n and n.get('tags'))
PY
```

> `.ua/` 是 gitignore 派生产物，**不会出现在 `git status`**。不要因为 `git status`
> 看不到它而误以为未修改——直接读文件 / 跑上面的核验即可。

## 5. 注意事项 / 边界

- **`/tmp` 中间产物已清空**：`ua_reanalyze.json`、`ua_summaries.json`、
  `ua_missing_batches.json`、`collate_*.py`、`kg_backup_*.json` 均为一次性 scratch，
  新会话若需「298 路径清单」或「重新对账」，须按 §3 在 baseCommit 处重跑
  `prepare-incremental` 重新生成（约 1 次调用，代价低）。**最终交付物不受影响**，
  因为它已落在 `.ua/knowledge-graph.json` 磁盘文件里。
- **不要重新跑全量再覆盖**：落盘已经完成且 gate 通过。除非确有新批次要补，否则
  不要重新生成摘要覆盖 kg——会引入无谓漂移。
- **索引红线**：`.ua/` 不得入库、不得作为 ADR / Gate 判定依据；与 `specs/` 冲突以
  `specs/` 为准。本次仅升级摘要文本，未触碰任何结构性内容，符合红线。
- **未进行（也无需进行）**：未改任何实现代码、未改 `specs/`、`generated/`、
  未动 git 暂存区（`.ua/` 本就未跟踪）。`git status` 中出现的其它修改属于
  会话开始前已有的业务改动，与本次任务无关。

## 6. 一句话交接

> 298 个文件的 LLM 级语义摘要已升级并落盘到 `.ua/knowledge-graph.json`，仅改
> 字段值、图结构完全不变、`index-gate-tests` 18/18 PASS。新会话直接读取该文件即可，
> 无需重做；如需 298 路径清单，在 baseCommit `7116904…` 重跑 `prepare-incremental`。
