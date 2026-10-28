"""T32/T33 negative-case tests for the vendored CR-07 simulation factory.

Pure stdlib + jsonschema conventions aligned with tests/tooling. The tests
mutate copies of the real simulation fixtures; no model, network or database
is touched and no fixed seed is modified.
"""
import copy
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG = REPO_ROOT / 'tools' / 'gk-ke-simulation'


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, PKG / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


guards = _load_module('gk_ke_simulation_guards', 'guards.py')
builder = _load_module('gk_ke_simulation_build', 'build_simulation.py')


class T32HumanControlTests(unittest.TestCase):
    """T32: human-control gates must reject unsafe candidates."""

    @classmethod
    def setUpClass(cls):
        cls.capability = guards.load('capability_contract.json')
        cls.confirmation = guards.load('confirmation_fixture.json')
        cls.statements = guards.load('statements.json')
        cls.query = guards.load('query_registry.json')

    def test_baseline_fixtures_pass(self):
        guards.guard_capability_readonly(self.capability)
        confirmation = copy.deepcopy(self.confirmation)
        confirmation['authorPrincipal'] = 'SIM-AUTHOR'
        guards.guard_confirmation_reviewer(confirmation)
        guards.guard_confirmation_version(self.confirmation, 1)
        guards.guard_claim_modality(self.statements[0])
        guards.guard_query_parameter_source(self.query)

    def test_capability_write_side_effect_rejected(self):
        bad = copy.deepcopy(self.capability)
        bad['sideEffect'] = 'WRITE_STATE'
        with self.assertRaisesRegex(ValueError, 'SIDE_EFFECT_NOT_READ_ONLY'):
            guards.guard_capability_readonly(bad)

    def test_self_confirmation_rejected(self):
        bad = copy.deepcopy(self.confirmation)
        bad['authorPrincipal'] = bad['reviewer']
        with self.assertRaisesRegex(ValueError, 'SELF_APPROVAL'):
            guards.guard_confirmation_reviewer(bad)

    def test_stale_version_confirmation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'STALE_TARGET_VERSION'):
            guards.guard_confirmation_version(self.confirmation, current_version=2)

    def test_forecast_treated_as_fact_rejected(self):
        bad = copy.deepcopy(self.statements[0])
        bad['factStatus'] = 'CONFIRMED'
        bad['certainty'] = True
        with self.assertRaisesRegex(ValueError, 'FORECAST_TREATED_AS_FACT'):
            guards.guard_claim_modality(bad)

    def test_client_controlled_authorization_rejected(self):
        bad = copy.deepcopy(self.query)
        bad['parametersFromServer'] = []
        with self.assertRaisesRegex(ValueError, 'AUTH_PARAM_CLIENT_CONTROLLED'):
            guards.guard_query_parameter_source(bad)


class T33SimulationBoundaryTests(unittest.TestCase):
    """T33: simulation-only boundary and oracle isolation."""

    @classmethod
    def setUpClass(cls):
        cls.customer = {
            'customerId': 'SIM-C001',
            'syntheticName': '模拟华东贸易有限公司',
            'simulationOnly': True,
        }

    def test_baseline_fixtures_pass(self):
        guards.guard_simulation_only(self.customer)
        guards.guard_synthetic_id(self.customer)
        guards.guard_oracle_isolation()

    def test_missing_simulation_only_rejected(self):
        bad = copy.deepcopy(self.customer)
        bad['simulationOnly'] = False
        with self.assertRaisesRegex(ValueError, 'SIMULATION_ONLY_NOT_TRUE'):
            guards.guard_simulation_only(bad)

    def test_real_identity_mapping_rejected(self):
        bad = copy.deepcopy(self.customer)
        bad['customerId'] = 'REAL-CUST-0001'
        with self.assertRaisesRegex(ValueError, 'NON_SIM_ID'):
            guards.guard_synthetic_id(bad)

    def test_oracle_leak_into_corpus_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'simulation' / 'oracles').mkdir(parents=True)
            (root / 'simulation' / 'graph').mkdir(parents=True)
            (root / 'simulation' / 'documents').mkdir(parents=True)
            (root / 'simulation' / 'oracles' / 'expected.json').write_text(
                '{"expectedValue": "2983333.33"}', encoding='utf-8')
            (root / 'simulation' / 'graph' / 'nodes.jsonl').write_text(
                '{"id": "LEAK", "label": "2983333.33"}\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'ORACLE_LEAK_IN_CORPUS'):
                guards.guard_oracle_isolation(root)


class DeterministicBuildTests(unittest.TestCase):
    """The factory must rebuild derived artifacts byte-for-byte stably."""

    def test_rebuild_is_byte_stable(self):
        sim = PKG / 'simulation'
        before = {

            str(p.relative_to(sim)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sim.rglob('*') if p.is_file()
        }
        builder.main()
        after = {
            str(p.relative_to(sim)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sim.rglob('*') if p.is_file()
        }
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
