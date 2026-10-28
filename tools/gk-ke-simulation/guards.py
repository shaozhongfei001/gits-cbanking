"""Human-control and simulation-boundary guards for CR-07 (T32/T33).

Pure stdlib, no model/network/database access. Every guard raises ValueError
with a stable machine-readable code when the candidate object violates the
contract; the real simulation fixtures are valid and pass unchanged.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIM = ROOT / 'simulation'


def load(rel):
    return json.loads((SIM / rel).read_text(encoding='utf-8'))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(obj) -> str:
    return sha256_hex(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                 separators=(',', ':')).encode('utf-8'))


# ---- T32: human control gates ---------------------------------------------

def guard_capability_readonly(contract: dict) -> None:
    """T32-1: a capability that writes production state must be rejected."""
    if contract.get('sideEffect') != 'READ_ONLY':
        raise ValueError('SIDE_EFFECT_NOT_READ_ONLY')
    if contract.get('productionProbePassed') is not False:
        raise ValueError('PRODUCTION_PROBE_NOT_FALSE')
    if contract.get('status') != 'SIMULATED_CONTRACT_ONLY':
        raise ValueError('NOT_SIMULATED_CONTRACT_ONLY')


def guard_confirmation_reviewer(confirmation: dict) -> None:
    """T32-2: self-approval (reviewer == author/principal) must be rejected."""
    author = confirmation.get('authorPrincipal')
    reviewer = confirmation.get('reviewer')
    if not reviewer:
        raise ValueError('REVIEWER_MISSING')
    if author and reviewer == author:
        raise ValueError('SELF_APPROVAL')
    if confirmation.get('isRealApproval') is not False:
        raise ValueError('REAL_APPROVAL_FLAG_SET')


def guard_confirmation_version(confirmation: dict, current_version: int) -> None:
    """T32-3: a confirmation against a stale target version must be rejected."""
    if confirmation.get('targetVersion') != current_version:
        raise ValueError('STALE_TARGET_VERSION')


def guard_claim_modality(claim: dict) -> None:
    """T32-4: uncertain forecast statements must not be treated as confirmed facts."""
    if claim.get('modality') != 'FORECAST':
        raise ValueError('MODALITY_NOT_FORECAST')
    if claim.get('certainty') is True or claim.get('factStatus') == 'CONFIRMED':
        raise ValueError('FORECAST_TREATED_AS_FACT')
    if claim.get('currency') is None:
        raise ValueError('CURRENCY_UNCONFIRMED')


def guard_query_parameter_source(query: dict, name: str = 'authorizedOrgId') -> None:
    """T32-5: authorization scope must be injected server-side, never by the client."""
    params_from_server = set(query.get('parametersFromServer', []))
    parameter_names = set(query.get('parameterNames', []))
    if name not in parameter_names:
        raise ValueError('AUTH_PARAM_UNDECLARED')
    if name not in params_from_server:
        raise ValueError('AUTH_PARAM_CLIENT_CONTROLLED')


# ---- T33: simulation boundary ---------------------------------------------

def guard_simulation_only(obj: dict) -> None:
    """T33-1: every synthetic artifact must carry simulationOnly=true."""
    if obj.get('simulationOnly') is not True:
        raise ValueError('SIMULATION_ONLY_NOT_TRUE')


def guard_synthetic_id(obj: dict, field: str = 'customerId') -> None:
    """T33-2: synthetic identifiers must use the SIM- prefix (no real mapping)."""
    value = obj.get(field, '')
    if not str(value).startswith('SIM-'):
        raise ValueError('NON_SIM_ID')


def guard_oracle_isolation(package_root: Path = ROOT) -> None:
    """T33-3: oracle answers must not leak into retrieval corpora.

    Retrieval corpora are the graph projection and the original documents;
    the oracle directory itself is the only allowed location.
    """
    oracle = (package_root / 'simulation' / 'oracles' / 'expected.json')
    if not oracle.is_file():
        raise ValueError('ORACLE_MISSING')
    expected = json.loads(oracle.read_text(encoding='utf-8'))
    secret = str(expected['expectedValue'])
    for corpus in [package_root / 'simulation' / 'graph',
                   package_root / 'simulation' / 'documents']:
        for path in corpus.rglob('*'):
            if path.is_file() and secret in path.read_text(encoding='utf-8'):
                raise ValueError('ORACLE_LEAK_IN_CORPUS')
