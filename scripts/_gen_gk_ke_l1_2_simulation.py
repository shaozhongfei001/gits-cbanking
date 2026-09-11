#!/usr/bin/env python3
"""生成 GK-KE L1-2 模拟源（C08 L1-2 / wave B2）。

权威源：docs/dd/gk-ke-contract/simulation/（V1.0.2 封版，只读）。
产出：scenario/seed/17_gk_ke_sim/（SIM 命名空间 + simulationOnly 清单 + 异常集）。

纪律：
  - 只读封版，绝不修改 docs/dd/gk-ke-contract/
  - 行数据逐字节复制（不重写数值，避免破坏 2,983,333.33 真值）
  - 新增 dataset_manifest.json（SIM 命名空间）与 negatives/（C07 §6 异常集）
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from decimal import ROUND_HALF_UP, Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEALED = ROOT / "docs" / "dd" / "gk-ke-contract" / "simulation"
OUT = ROOT / "scenario" / "seed" / "17_gk_ke_sim"
TABLES_OUT = OUT / "tables"
NEG_OUT = OUT / "negatives"

TABLES = [
    "organizations", "customers", "accounts", "products", "transactions",
    "ledger_entries", "daily_balances", "credit_facilities", "holdings", "calendar",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not SEALED.is_dir():
        raise SystemExit(f"sealed simulation missing: {SEALED}")

    TABLES_OUT.mkdir(parents=True, exist_ok=True)
    NEG_OUT.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    files: list[dict] = []

    # 1. 逐字节复制表数据
    for name in TABLES:
        src = SEALED / "tables" / f"{name}.csv"
        dst = TABLES_OUT / f"{name}.csv"
        shutil.copyfile(src, dst)
        with src.open(newline="", encoding="utf-8") as fh:
            counts[name] = sum(1 for _ in csv.DictReader(fh))
        files.append({"path": f"tables/{name}.csv", "sha256": sha256(dst)})

    # 2. 复制 statements.json 与 seed_scenarios.json（源事件种子）
    for extra in ("statements.json", "seed_scenarios.json", "source_catalog.json"):
        src = SEALED / extra
        if src.is_file():
            dst = OUT / extra
            shutil.copyfile(src, dst)
            files.append({"path": extra, "sha256": sha256(dst)})

    # 3. C001 日均复算（独立于测试，作为生成期自证）
    with (TABLES_OUT / "accounts.csv").open(newline="", encoding="utf-8") as fh:
        accounts = list(csv.DictReader(fh))
    with (TABLES_OUT / "daily_balances.csv").open(newline="", encoding="utf-8") as fh:
        balances = list(csv.DictReader(fh))
    c001 = {a["accountId"] for a in accounts if a["customerId"] == "SIM-C001" and a["currency"] == "CNY"}
    by_date: dict[str, D] = {}
    for r in balances:
        if r["accountId"] in c001:
            by_date[r["businessDate"]] = by_date.get(r["businessDate"], D("0")) + D(
                r["closingBalance"]
            ).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    period_days = 30  # 2026-09-01 至 2026-10-01 左闭右开（C07 §5）
    total = sum(by_date.values(), D("0"))
    avg = (total / D(period_days)).quantize(D("0.01"), rounding=ROUND_HALF_UP)

    # 4. SIM 命名空间清单
    manifest = {
        "simulationOnly": True,
        "namespace": "gk-ke/v1 SIM",
        "version": "1.0.0",
        "snapshotId": "SIM-SNAPSHOT-20261001",
        "generationMethod": "PROMOTED_FROM_SEALED_V1.0.2_PACKAGE",
        "sealedSource": "docs/dd/gk-ke-contract/simulation (V1.0.2, read-only)",
        "externalModelApiCalled": False,
        "tableCounts": counts,
        "files": files,
        "c001AverageDailyDeposit": str(avg),
        "c001PeriodDays": period_days,
        "c001AccountCount": len(c001),
        "c001Expected": "2983333.33",
        "c001MatchesExpected": str(avg) == "2983333.33",
        "currencyPolicy": "CNY_ONLY for C001 scenario; USD account present as C002 cross-currency negative",
        "notes": [
            "行数据逐字节复制自封版包，未重写数值（保护 2,983,333.33 真值）",
            "所有行 simulationOnly 由本 envelope 约束，行内不重复元数据（C07 section 2）",
            "主数据 ID 由种子确定，名称不作外键（C07 section 5）",
        ],
    }

    # 5. C07 §6 异常集：负例必须声明 expectedError
    negatives = [
        ("missing_day", "DAILY_BALANCE_MISSING_DAY", "某账户缺少某一业务日余额行"),
        ("duplicate_account_day", "DUPLICATE_ACCOUNT_DAY", "同一 accountId+businessDate 出现两行"),
        ("cross_currency_add", "CROSS_CURRENCY_ADDITION", "把 USD 账户余额与 CNY 账户余额直接相加"),
        ("unknown_customer", "FK_CUSTOMER_UNRESOLVED", "账户引用不存在的 customerId"),
        ("unbalanced_ledger", "LEDGER_NOT_BALANCED", "交易借贷分录金额不等或方向相同"),
        ("missing_simulation_flag", "SIM_FLAG_MISSING", "行数据缺少 simulationOnly 标记"),
        ("balance_roll_break", "BALANCE_ROLL_BREAK", "次日 opening 不等于前日 closing"),
    ]
    for name, error, desc in negatives:
        payload = {
            "expectedError": error,
            "simulationOnly": True,
            "case": name,
            "description": desc,
            "source": "C07 section 6 异常集",
            "mustNotPolluteNormalSnapshot": True,
        }
        (NEG_OUT / f"{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    (OUT / "dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("L1-2 simulation generated")
    print(f"  tables={len(counts)} rows={sum(counts.values())}")
    print(f"  C001 avg = {avg} (matches={manifest['c001MatchesExpected']})")
    print(f"  negatives={len(negatives)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
