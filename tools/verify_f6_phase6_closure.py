"""F6.11 — machine-verifiable Phase 6 closure acceptance gate."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "08_Implementacion" / "phase6_acceptance_manifest_v0.1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def fail(message: str) -> None:
    raise ValueError("F6_11_PHASE_CLOSURE_REJECTED:" + message)


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
        "operational_path", "units", "external_modules",
        "required_ci_markers", "closure_statement",
    }
    if type(data) is not dict or set(data) != required_top:
        fail("MANIFEST_SCHEMA_MISMATCH")
    if data["schema"] != "EIOS_PHASE6_ACCEPTANCE/v0.1":
        fail("SCHEMA_VERSION_MISMATCH")
    if data["phase"] != "F6" or data["status"] != "CLOSURE_CANDIDATE":
        fail("INVALID_PHASE_STATUS")
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
    expected_ids = [f"F6.{n}" for n in range(1, 11)]
    if type(units) is not list or [row.get("id") for row in units] != expected_ids:
        fail("INCOMPLETE_OR_REORDERED_PHASE_UNITS")

    checked_paths: list[str] = []
    for row in units:
        if type(row) is not dict or "artifact" not in row:
            fail("INVALID_UNIT_RECORD")
        for key in ("artifact", "test", "verifier"):
            path = row.get(key)
            if path is None:
                continue
            if type(path) is not str or not path or path.startswith("/") or ".." in Path(path).parts:
                fail("INVALID_ARTIFACT_PATH:" + str(path))
            if path.startswith("eios/"):
                fail("CANONICAL_ENGINE_PATH_FORBIDDEN:" + path)
            if not (root / path).is_file():
                fail("MISSING_REQUIRED_ARTIFACT:" + path)
            checked_paths.append(path)

    modules = data["external_modules"]
    if type(modules) is not list or len(modules) != 9:
        fail("EXTERNAL_MODULE_INVENTORY_MISMATCH")
    for path in modules:
        if (
            type(path) is not str
            or path.startswith("eios/")
            or not (root / path).is_file()
        ):
            fail("INVALID_EXTERNAL_MODULE:" + str(path))
        checked_paths.append(path)

    workflow = (root / WORKFLOW.relative_to(ROOT)).read_text(encoding="utf-8")
    markers = data["required_ci_markers"]
    if type(markers) is not list or not markers:
        fail("CI_MARKERS_REQUIRED")
    missing = [marker for marker in markers if marker not in workflow]
    if missing:
        fail("MISSING_CI_MARKERS:" + ",".join(missing))

    canonical_f6 = sorted(
        str(path.relative_to(root)).replace("\\", "/")
        for path in (root / "eios").rglob("*f6*")
        if path.is_file()
    ) if (root / "eios").is_dir() else []
    if canonical_f6:
        fail("PHASE6_EXTERNAL_BOUNDARY_LEAKED_INTO_CANONICAL_ENGINE:" + ",".join(canonical_f6))

    statement = data["closure_statement"]
    if (
        type(statement) is not str
        or "does not authorize production or operational execution" not in statement
    ):
        fail("CLOSURE_LIMITATION_MISSING")

    return {
        "verification": "F6_11_PHASE6_CLOSURE_ACCEPTANCE_PASS",
        "phase": "F6",
        "accepted_units": expected_ids,
        "artifact_count": len(set(checked_paths)),
        "synthetic_only": True,
        "production_authorized": False,
        "decision_authority": False,
        "real_pilot_admitted": False,
        "operational_path": "FORBIDDEN",
        "canonical_engine_phase6_leaks": 0,
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
