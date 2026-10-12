# P30-gits-bank-experience-shell｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260825T153717Z｜contract_check

- Command: `make check`
- Exit: `2`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/contract_check-20260825T153717Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### Root cause

`scripts/secret_scan.py` 将 `git ls-files -co --exclude-standard` 中的未跟踪 `scenario/dkws-platform/.venv/**/auth.py` 当成阻塞凭据。该目录不属于 P30，且 `.venv` 未列入扫描跳过集合（已有 `node_modules`/`target`）。修复后重跑：`contract_check` 第二次 attempt 退出码 0，见 `EVIDENCE.json`。

## 20260825T153925Z｜frontend_shell

- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `1`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/frontend_shell-20260825T153925Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### Root cause

`npm ci` 失败：`package-lock.json` 缺少 `@emnapi/wasi-threads@1.2.1`，与 `package.json` 不同步。P30 未新增 npm 依赖。修复：在 `frontend/` 运行 `npm install` 回写 lockfile。重跑：`frontend_shell` 第二次 attempt 退出码 0，证据 `loops/P30-gits-bank-experience-shell/evidence/frontend_shell-20260825T154531Z.log`。
