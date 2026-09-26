# 协作协议 · AN0

1. 开工：读 LOOP.yaml / STATE.json / EVIDENCE.md / memory/NEXT_SESSION.md。
2. 单写者：STATE.json、EVIDENCE.json、ROLE_BOARD.yaml、NEXT_SESSION.md 同一时刻仅一人写。
3. 门禁串行执行（E2E 依赖后台服务，禁止并发跑门禁）。
4. 完成声明必须先更新证据与 Baton，再 `make evidence-check LOOP=AN0-ccrm-analytics-landing` / `make memory-check LOOP=AN0-ccrm-analytics-landing`。
5. 开发不得自签 QA_PASS；独立 QA 报告由 QA 角色落盘。
