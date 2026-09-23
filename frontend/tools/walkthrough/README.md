# 人工验证走查台（tools/walkthrough）

**用途**：把"人工走查"变成**可点击判定 + 可导出**的可用工具（而不是在 markdown 里手填）。

## 用法

```bash
cd frontend
node tools/walkthrough/run.mjs                 # ① 采集证据（只读；默认 base=http://127.0.0.1:15173）
python3 -m http.server 15200 --directory tools/walkthrough/viewer   # ② 起走查台
# 打开 http://127.0.0.1:15200/ ，逐场景点 PASS / FAIL / BLOCKED + 备注，最后「导出判定」
```

## 口径（不得放宽）

- 判据**外生**：以每卡右侧「oracle：本页实际收到的接口」与「期望」为准，**不得凭"看起来对"**；
- **BLOCKED 必须写具名原因**，且不得计为通过；设计性禁用（只读切片）**不是故障**；
- 判定存 localStorage，导出 JSON/Markdown 交回 TL；`run.mjs` **不做写操作**（写路径由人工在应用里执行）。

## 产物

- `viewer/data.js`（`window.WALKTHROUGH_DATA`）· `viewer/shots/*.jpg`（每场景整页截图）· `viewer/index.html`（判定台）
