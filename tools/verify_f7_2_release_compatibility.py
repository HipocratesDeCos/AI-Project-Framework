"""F7.2 — exact neutral release compatibility matrix, deny-by-default."""
from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "08_Implementacion" / "phase7_release_compatibility_matrix_v0.1.json"
BASELINE = ROOT / "08_Implementacion" / "phase7_public_api_baseline_v0.1.json"
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")

DISTRIBUTIONS = (
    "eios-kernel",
    "eios-input-contracts",
    "eios-capability-catalog",
    "eios-catalog-governance",
)

PYPROJECTS = {
    "eios-kernel": "packaging/eios-kernel/pyproject.toml",
    "eios-input-contracts": "packaging/eios-input-contracts/pyproject.toml",
    "eios-capability-catalog": "packaging/eios-capability-catalog/pyproject.toml",
    "eios-catalog-governance": "packaging/eios-catalog-governance/pyproject.toml",
}


class ReleaseCompatibilityError(ValueError):
    pass


def fail(code: str) -> None:
    raise ReleaseCompatibilityError("F7_2_RELEASE_COMPATIBILITY_REJECTED:" + code)


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        fail("INVALID_JSON:" + str(exc))
    if type(data) is not dict:
        fail("JSON_OBJECT_REQUIRED")
    return data


def _validate_tuple(versions: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    if not isinstance(versions, Mapping) or set(versions) != set(DISTRIBUTIONS):
        fail("EXACT_VERSION_TUPLE_REQUIRED")
    result = []
    for name in DISTRIBUTIONS:
        version = versions[name]
        if type(version) is not str or not SEMVER.fullmatch(version):
            fail("INVALID_VERSION:" + name)
        result.append((name, version))
    return tuple(result)


def _installed_declared_versions(root: Path) -> dict[str, str]:
    result = {}
    for name, rel in PYPROJECTS.items():
        path = root / rel
        try:
            project = tomllib.loads(path.read_text(encoding="utf-8"))["project"]
        except (OSError, UnicodeError, ValueError, KeyError) as exc:
            fail("INVALID_PYPROJECT:" + name + ":" + str(exc))
        if project.get("name") != name:
            fail("DISTRIBUTION_IDENTITY_CHANGED:" + name)
        version = project.get("version")
        if type(version) is not str or not SEMVER.fullmatch(version):
            fail("INVALID_DECLARED_VERSION:" + name)
        result[name] = version
    return result


def classify_versions(
    versions: Mapping[str, str],
    *,
    matrix: dict,
) -> str:
    candidate = _validate_tuple(versions)
    certified = {
        _validate_tuple(row["versions"])
        for row in matrix["certified_combinations"]
        if row.get("status") == "CERTIFIED"
    }
    if candidate in certified:
        return "CERTIFIED"
    return "REJECT_UNLISTED"


def verify(root: Path = ROOT) -> dict:
    matrix = _load_json(root / MATRIX.relative_to(ROOT))
    baseline = _load_json(root / BASELINE.relative_to(ROOT))

    expected_top = {
        "schema", "phase", "baseline_main_sha", "policy", "dimensions",
        "certified_combinations", "explicitly_rejected_examples",
        "candidate_admission_requirements",
    }
    if set(matrix) != expected_top:
        fail("MATRIX_SCHEMA_CHANGED")
    if matrix["schema"] != "EIOS_RELEASE_COMPATIBILITY_MATRIX/v0.1":
        fail("MATRIX_IDENTITY_CHANGED")
    if matrix["phase"] != "F7.2":
        fail("PHASE_CHANGED")
    if matrix["baseline_main_sha"] != "f4e0b5f112abb109b85ea93ef57502e3840bc222":
        fail("BASELINE_MAIN_SHA_CHANGED")
    if matrix["dimensions"] != list(DISTRIBUTIONS):
        fail("MATRIX_DIMENSIONS_CHANGED")

    expected_policy = {
        "default": "REJECT_UNLISTED",
        "semver_implies_compatibility": False,
        "partial_tuple_inference_forbidden": True,
        "mixed_release_inference_forbidden": True,
        "candidate_requires_explicit_evidence": True,
    }
    if matrix["policy"] != expected_policy:
        fail("COMPATIBILITY_POLICY_CHANGED")

    certified = matrix["certified_combinations"]
    if type(certified) is not list or len(certified) != 1:
        fail("UNSUPPORTED_CERTIFIED_COMBINATION_COUNT")

    row = certified[0]
    expected_row_keys = {
        "id", "status", "versions", "baseline_manifest", "evidence",
        "production_authorized", "decision_authority", "operational_path",
    }
    if set(row) != expected_row_keys:
        fail("CERTIFIED_ROW_SCHEMA_CHANGED")
    if row["id"] != "NEUTRAL_STACK_0_1_0" or row["status"] != "CERTIFIED":
        fail("CERTIFIED_ROW_IDENTITY_CHANGED")
    if row["baseline_manifest"] != "08_Implementacion/phase7_public_api_baseline_v0.1.json":
        fail("BASELINE_MANIFEST_REFERENCE_CHANGED")
    if (
        row["production_authorized"] is not False
        or row["decision_authority"] is not False
        or row["operational_path"] != "FORBIDDEN"
    ):
        fail("AUTHORITY_ESCALATION")

    exact = dict(_validate_tuple(row["versions"]))
    declared = _installed_declared_versions(root)
    if exact != declared:
        fail("CERTIFIED_TUPLE_DOES_NOT_MATCH_DECLARED_PACKAGES")

    baseline_versions = {
        item["distribution"]: item["version"]
        for item in baseline["packages"]
    }
    if exact != baseline_versions:
        fail("CERTIFIED_TUPLE_DOES_NOT_MATCH_F7_1_BASELINE")

    evidence = row["evidence"]
    required_evidence = {
        "F7.1_PUBLIC_API_BASELINE_PASS",
        "F5.9_THIRD_DOMAIN_PORTABILITY",
        "F5.10_PORTABLE_EXTERNAL_DEPLOYMENT",
        "F6.11_PHASE6_CLOSURE_ACCEPTANCE",
    }
    if type(evidence) is not list or set(evidence) != required_evidence:
        fail("CERTIFICATION_EVIDENCE_CHANGED")

    rejected = matrix["explicitly_rejected_examples"]
    if type(rejected) is not list or len(rejected) < 2:
        fail("NEGATIVE_EXAMPLES_REQUIRED")
    for item in rejected:
        if type(item) is not dict or set(item) != {"reason", "versions"}:
            fail("INVALID_REJECTED_EXAMPLE")
        if classify_versions(item["versions"], matrix=matrix) != "REJECT_UNLISTED":
            fail("UNVERIFIED_EXAMPLE_WAS_CERTIFIED")

    requirements = matrix["candidate_admission_requirements"]
    required = {
        "PUBLIC_API_BASELINE_FOR_CANDIDATE",
        "EXACT_DEPENDENCY_GRAPH",
        "FRESH_INSTALLATION_TEST",
        "EXISTING_CONSUMER_REGRESSION",
        "THIRD_DOMAIN_REGRESSION",
        "LINUX_CERTIFICATION",
        "WINDOWS_PYTHON_3_12_CERTIFICATION",
        "NO_AUTHORITY_ESCALATION",
    }
    if type(requirements) is not list or set(requirements) != required:
        fail("CANDIDATE_ADMISSION_REQUIREMENTS_CHANGED")

    if classify_versions(exact, matrix=matrix) != "CERTIFIED":
        fail("CURRENT_DECLARED_STACK_NOT_CERTIFIED")

    return {
        "verification": "F7_2_RELEASE_COMPATIBILITY_MATRIX_PASS",
        "phase": "F7.2",
        "certified_combination_count": 1,
        "certified_stack": exact,
        "default_policy": "REJECT_UNLISTED",
        "semver_implies_compatibility": False,
        "mixed_release_inference": False,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
