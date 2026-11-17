"""F6.11 — Phase 6 closure acceptance regression tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from tools.verify_f6_phase6_closure import verify

ROOT = Path(__file__).resolve().parents[1]


def clone_minimal_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    return target


def test_phase6_acceptance_passes_on_repository():
    result = verify(ROOT)
    assert result["verification"] == "F6_11_PHASE6_CLOSURE_ACCEPTANCE_PASS"
    assert result["accepted_units"] == [f"F6.{n}" for n in range(1, 11)]
    assert result["synthetic_only"] is True
    assert result["production_authorized"] is False
    assert result["decision_authority"] is False
    assert result["real_pilot_admitted"] is False
    assert result["operational_path"] == "FORBIDDEN"
    assert result["canonical_engine_phase6_leaks"] == 0


def test_missing_unit_artifact_blocks_closure(tmp_path):
    repo = clone_minimal_repo(tmp_path)
    path = repo / "08_Implementacion" / "Core_Phase6_10_Idempotent_Retry_Safety_v0.1.md"
    path.unlink()
    with pytest.raises(ValueError, match="MISSING_REQUIRED_ARTIFACT"):
        verify(repo)


def test_authority_promotion_blocks_closure(tmp_path):
    repo = clone_minimal_repo(tmp_path)
    path = repo / "08_Implementacion" / "phase6_acceptance_manifest_v0.1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["production_authorized"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="AUTHORITY_BOUNDARY_VIOLATION"):
        verify(repo)


def test_missing_windows_or_linux_ci_marker_blocks_closure(tmp_path):
    repo = clone_minimal_repo(tmp_path)
    workflow = repo / ".github" / "workflows" / "tests.yml"
    text = workflow.read_text(encoding="utf-8").replace(
        "F6.5–F6.10 certify onboarding through retry safety on Windows",
        "REMOVED_F6_WINDOWS_GATE",
    )
    workflow.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="MISSING_CI_MARKERS"):
        verify(repo)


def test_canonical_engine_phase6_leak_blocks_closure(tmp_path):
    repo = clone_minimal_repo(tmp_path)
    eios = repo / "eios"
    eios.mkdir(exist_ok=True)
    (eios / "f6_rogue_boundary.py").write_text("# forbidden", encoding="utf-8")
    with pytest.raises(ValueError, match="PHASE6_EXTERNAL_BOUNDARY_LEAKED"):
        verify(repo)


def test_reordered_or_missing_units_block_closure(tmp_path):
    repo = clone_minimal_repo(tmp_path)
    path = repo / "08_Implementacion" / "phase6_acceptance_manifest_v0.1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["units"] = data["units"][:-1]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="INCOMPLETE_OR_REORDERED_PHASE_UNITS"):
        verify(repo)
