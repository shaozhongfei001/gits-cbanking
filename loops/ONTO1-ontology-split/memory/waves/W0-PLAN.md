# W0｜Plan

> **状态：未开工**。W0（冻结与 Loop 骨架）须等 `G-1`：书面复审结论 + WI-A2/A4/A6 + D3 签署。
> 当前波次是 **Wave -1**，其 PLAN 见本目录 `W-1-PLAN.md`；W-1 的实际 attempt 由 `record_gate.py`
> 追加在 `W0-ITER.md`（模板文件名沿用，内容含 W-1 全部 attempt）。

## Goal

执行 LOOP 中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

## W0 开工前必须核对的输入锚点（m-03：低风险≠零风险）

| 锚点 | 值 | 失败条件 |
|---|---|---|
| 复审包 MANIFEST 12 文件哈希 | 见 `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md` | 任一不符 ⇒ STOP |
| 基线本体哈希 | `sha256:705578d6324abd0c…`（32/34/1） | IRI 差异/计数不符 ⇒ STOP |
| `attribution-45-v2.csv` | `sha256 05ec849e57a163a5…` | 分口径计数不符 ⇒ STOP |
| ADR 签署件 | D3 双 Owner 签署 | 未签 ⇒ 不得进 Wave 2 |
| 消费者扫描处置表 | 零 `PENDING_TRIAGE` | 有遗漏 ⇒ STOP（扫描缺漏） |
