"""F7.6 — Phase 7 closure acceptance regression tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from tools.verify_f7_phase7_closure import verify

ROOT = Path(__file__).resolve().parents[1]


def clone_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "dist"),
    )
    return target


def test_phase7_acceptance_passes_on_repository():
    result = verify(ROOT)
    assert result["verification"] == "F7_6_PHASE7_CLOSURE_ACCEPTANCE_PASS"
    assert result["accepted_units"] == [f"F7.{n}" for n in range(1, 6)]
    assert result["production_authorized"] is False
    assert result["decision_authority"] is False
    assert result["real_pilot_admitted"] is False
    assert result["operational_path"] == "FORBIDDEN"
    assert result["canonical_engine_phase7_leaks"] == 0
    assert result["further_f7_unit_required"] is False


def test_missing_f7_unit_artifact_blocks_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    path = repo / "08_Implementacion" / "Core_Phase7_5_Immutable_Release_Identity_v0.1.md"
    path.unlink()
    with pytest.raises(ValueError, match="MISSING_REQUIRED_ARTIFACT"):
        verify(repo)


def test_missing_policy_artifact_blocks_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    path = repo / "08_Implementacion" / "phase7_release_identity_policy_v0.1.json"
    path.unlink()
    with pytest.raises(ValueError, match="MISSING_POLICY_ARTIFACT"):
        verify(repo)


def test_authority_promotion_blocks_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    path = repo / "08_Implementacion" / "phase7_acceptance_manifest_v0.1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["production_authorized"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="AUTHORITY_BOUNDARY_VIOLATION"):
        verify(repo)


def test_missing_windows_release_identity_gate_blocks_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    workflow = repo / ".github" / "workflows" / "tests.yml"
    text = workflow.read_text(encoding="utf-8").replace(
        "F7.5 generate immutable Windows release identity receipt",
        "REMOVED_F7_WINDOWS_RELEASE_IDENTITY_GATE",
    )
    workflow.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="MISSING_CI_MARKERS"):
        verify(repo)


def test_canonical_engine_f7_governance_leak_blocks_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    rogue = repo / "eios" / "f7_release_governance.py"
    rogue.write_text("# forbidden phase-specific governance leak", encoding="utf-8")
    with pytest.raises(ValueError, match="PHASE7_GOVERNANCE_LEAKED"):
        verify(repo)


def test_reordered_or_missing_units_block_closure(tmp_path: Path):
    repo = clone_repo(tmp_path)
    path = repo / "08_Implementacion" / "phase7_acceptance_manifest_v0.1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["units"] = data["units"][:-1]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="INCOMPLETE_OR_REORDERED_PHASE_UNITS"):
        verify(repo)
