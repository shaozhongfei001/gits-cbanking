"""P1 验收：seeds 合法样例全通过、非法样例全被拒（标准库 unittest）。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
SEEDS = Path(__file__).resolve().parent.parent / "seeds"

from dkws import schemas  # noqa: E402,F401
from dkws.contract import parse_frontmatter, resolve_by_contract, validate_text  # noqa: E402
from dkws.errors import ContractError, DkwError  # noqa: E402

# 依据 frontmatter schema 值选择合同
_CONTRACT_BY_PREFIX = {
    "manifest": "manifest/v1", "entity": "entity/v1", "statement": "statement/v1",
    "current": "current_pointer/v1", "rule": "rule/v1", "schema-mismatch": "manifest/v1",
    "auto-owner": "review_decision/v1",
}


def _dispatch(name: str, text: str) -> None:
    data, _ = parse_frontmatter(text)
    contract = str(data.get("schema", ""))
    s = resolve_by_contract(contract)
    validate_text(text, s)


class TestLegalSeeds(unittest.TestCase):
    def test_all_legal_pass(self):
        legal_dir = SEEDS / "legal"
        if not legal_dir.is_dir():
            self.skipTest("seeds/legal 不存在（先运行 scripts/make_seeds.py）")
        for p in sorted(legal_dir.glob("*.md")):
            with self.subTest(file=p.name):
                _dispatch(p.name, p.read_text(encoding="utf-8"))  # 不应抛错


class TestIllegalSeeds(unittest.TestCase):
    def test_all_illegal_rejected(self):
        illegal_dir = SEEDS / "illegal"
        if not illegal_dir.is_dir():
            self.skipTest("seeds/illegal 不存在")
        for p in sorted(illegal_dir.glob("*.md")):
            with self.subTest(file=p.name):
                with self.assertRaises(DkwError):
                    _dispatch(p.name, p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()