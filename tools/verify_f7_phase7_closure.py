"""F7.6 — machine-verifiable Phase 7 closure acceptance gate."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "08_Implementacion" / "phase7_acceptance_manifest_v0.1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def fail(message: str) -> None:
    raise ValueError("F7_6_PHASE7_CLOSURE_REJECTED:" + message)


def verify(root: Path = ROOT) -> dict:
    manifest_path = root / MANIFEST.relative_to(ROOT)
    if not manifest_path.is_file():
        fail("MISSING_ACCEPTANCE_MANIFEST")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        fail("INVALID_ACCEPTANCE_MANIFEST:" + str(exc))

    required_top = {
        "schema", "phase", "status", "baseline_main_sha", "synthetic_only",
        "production_authorized", "decision_authority", "real_pilot_admitted",
        "operational_path", "units", "required_policy_artifacts",
        "required_ci_markers", "closure_statement",
    }
    if type(data) is not dict or set(data) != required_top:
        fail("MANIFEST_SCHEMA_MISMATCH")
    if data["schema"] != "EIOS_PHASE7_ACCEPTANCE/v0.1":
        fail("SCHEMA_VERSION_MISMATCH")
    if data["phase"] != "F7" or data["status"] != "CLOSURE_CANDIDATE":
        fail("INVALID_PHASE_STATUS")
    if data["baseline_main_sha"] != "6de352fda51dd95431e6778d41530f9531949ff9":
        fail("BASELINE_SHA_MISMATCH")
    if not SHA40.fullmatch(data["baseline_main_sha"]):
        fail("INVALID_BASELINE_SHA")
    if data["synthetic_only"] is not True:
        fail("SYNTHETIC_ONLY_REQUIRED")
    if (
        data["production_authorized"] is not False
        or data["decision_authority"] is not False
        or data["real_pilot_admitted"] is not False
        or data["operational_path"] != "FORBIDDEN"
    ):
        fail("AUTHORITY_BOUNDARY_VIOLATION")

    units = data["units"]
    expected_ids = [f"F7.{n}" for n in range(1, 6)]
    if type(units) is not list or [row.get("id") for row in units] != expected_ids:
        fail("INCOMPLETE_OR_REORDERED_PHASE_UNITS")

    checked_paths: list[str] = []
    for row in units:
        if type(row) is not dict:
            fail("INVALID_UNIT_RECORD")
        if set(row) != {"id", "artifact", "test", "verifier"}:
            fail("UNIT_RECORD_SCHEMA_MISMATCH:" + str(row.get("id")))
        for key in ("artifact", "test", "verifier"):
            path = row.get(key)
            if type(path) is not str or not path or path.startswith("/") or ".." in Path(path).parts:
                fail("INVALID_ARTIFACT_PATH:" + str(path))
            if path.startswith("eios/"):
                fail("CANONICAL_ENGINE_PATH_FORBIDDEN:" + path)
            if not (root / path).is_file():
                fail("MISSING_REQUIRED_ARTIFACT:" + path)
            checked_paths.append(path)

    policies = data["required_policy_artifacts"]
    expected_policies = [
        "08_Implementacion/phase7_public_api_baseline_v0.1.json",
        "08_Implementacion/phase7_release_compatibility_matrix_v0.1.json",
        "08_Implementacion/phase7_upgrade_migration_contract_v0.1.json",
        "08_Implementacion/phase7_deprecation_support_lifecycle_v0.1.json",
        "08_Implementacion/phase7_release_identity_policy_v0.1.json",
    ]
    if policies != expected_policies:
        fail("POLICY_ARTIFACT_INVENTORY_MISMATCH")
    for path in policies:
        if not (root / path).is_file():
            fail("MISSING_POLICY_ARTIFACT:" + path)
        checked_paths.append(path)

    workflow = (root / WORKFLOW.relative_to(ROOT)).read_text(encoding="utf-8")
    markers = data["required_ci_markers"]
    if type(markers) is not list or not markers:
        fail("CI_MARKERS_REQUIRED")
    missing = [marker for marker in markers if marker not in workflow]
    if missing:
        fail("MISSING_CI_MARKERS:" + ",".join(missing))

    canonical_f7 = sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for path in (root / "eios").rglob("*f7*")
        if path.is_file()
    ) if (root / "eios").is_dir() else []
    if canonical_f7:
        fail("PHASE7_GOVERNANCE_LEAKED_INTO_CANONICAL_ENGINE:" + ",".join(canonical_f7))

    statement = data["closure_statement"]
    if (
        type(statement) is not str
        or "does not authorize production or operational execution" not in statement
    ):
        fail("CLOSURE_LIMITATION_MISSING")

    return {
        "verification": "F7_6_PHASE7_CLOSURE_ACCEPTANCE_PASS",
        "phase": "F7",
        "accepted_units": expected_ids,
        "artifact_count": len(set(checked_paths)),
        "synthetic_only": True,
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
        "canonical_engine_phase7_leaks": 0,
        "further_f7_unit_required": False,
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
