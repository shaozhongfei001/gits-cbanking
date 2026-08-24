# P24-dkws-platform BLOCKED

- Time: `2026-08-21T09:46:00Z`
- Actor: `independent_qa`
- Decision: **reject** (process) — functional tests passed; cannot `qa_attest`
- `QA_PASS` recorded: **NO**

## blocking_reason

implementation evidence board incomplete (cannot qa_attest)

## Functional result (independent QA, offline)

- Command: `cd scenario/dkws-platform && PYTHONPATH=src:tests:scripts python3 -m unittest discover -s tests -v`
- Result: **Ran 54 tests in 3.344s — OK** (`unittest_exit_code=0`)
- CLI smoke: `python3 -m dkws --help` exit 0 (no `--llm real`, no secrets)
- Evidence: `loops/P24-dkws-platform/evidence/independent_qa_20260821T094459Z.log`
- sha256: `f0920c24f717e9e92be31791dd8f5327dfe9d467d8aa28746ee8aa8f2d0efb94`

## loop_guard / qa_attest

```
loop-guard --evidence-only: FAIL: missing loop files:
  ['loops/P24-dkws-platform/EVIDENCE.json', 'loops/P24-dkws-platform/HANDOFF.md']
qa_attest --decision pass: FAIL: implementation evidence is invalid (exit 2; no board write)
```

`qa_attest` was not eligible; independent QA did not invent implementation gate hashes.

## Missing vs loop_guard required files

| File | Status |
|---|---|
| LOOP.yaml | present |
| STATE.json | present (`baseline_commit` invalid: null) |
| EVIDENCE.json | **MISSING** |
| EVIDENCE.md | present (narrative only) |
| FAILURES.md | present |
| HANDOFF.md | **MISSING** |
| SHARED_MEMORY.md | **MISSING** |
| memory/PROTOCOL.md | **MISSING** |
| memory/ROLE_BOARD.yaml | present (schema ≠ loop_guard JSON `baton.holder`) |
| memory/NEXT_SESSION.md | present (holder table missing at IQA start) |
| memory/ORCHESTRATOR.md | **MISSING** |

## Unblock (feature_pilot)

1. Create `EVIDENCE.json` matching LOOP.yaml gates, with real per-gate logs under `loops/P24-dkws-platform/evidence/` and matching `output_sha256` from gates **you executed as implementation**. Do not copy independent QA hashes onto P0–P9 gates.
2. Add `HANDOFF.md`, `SHARED_MEMORY.md`, `memory/PROTOCOL.md`, `memory/ORCHESTRATOR.md` (template-conformant; do not leave unsubstituted template tokens).
3. Set `STATE.json.baseline_commit` to a full 40-char Git SHA.
4. Align `ROLE_BOARD.yaml` JSON `baton.holder` with `NEXT_SESSION.md` `| **holder** | \`...\` |`.
5. `python3 scripts/loop_guard.py --loop P24-dkws-platform --evidence-only` must PASS, then return status to `ready_for_independent_qa` and re-dispatch independent QA.

Do not ask independent QA to fabricate `EVIDENCE.json`.
