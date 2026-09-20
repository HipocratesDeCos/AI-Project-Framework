from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from eios.core import _projection_synthetic_foundation as private_foundation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import (
    ProjectionOnlySyntheticMaterialBundle,
    SCHEMA_VERSION,
    SyntheticSemanticAdapterError,
    build_projection_only_synthetic_material_bundle,
)
from test_projection_synthetic_foundation import _dataset


FIXTURES = Path(__file__).parent / "fixtures"
STRUCTURAL = FIXTURES / "projection_only_mock_dataset_01"
SEMANTIC = FIXTURES / "projection_only_semantic_dataset_01"


def test_physical_semantic_fixture_builds_complete_atomic_bundle():
    dataset = load_projection_mock_dataset(SEMANTIC)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    payload = bundle.to_payload()
    envelope = bundle.envelope.to_payload()

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["dataset_id"] == "EIOS-PROJECTION-SEMANTIC-MOCK-001"
    assert payload["dataset_fingerprint"] == dataset.fingerprint
    assert payload["envelope_fingerprint"] == bundle.envelope.fingerprint
    assert payload["case_kind"] == "SYNTHETIC"
    assert payload["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert payload["assurance_scope"] == "ATOMIC_SYNTHETIC_MATERIAL_TRANSLATION_ONLY"

    membership = envelope["recomputed_membership"]
    assert membership["contains_synthetic_material"] is True
    assert membership["treasury_pending_conditions"] == []
    assert membership["flow_pending_conditions"] == []
    assert membership["unassessed_captured_flow_ids"] == []
    assert membership["unmatched_candidate_refs"] == []
    assert membership["unreviewed_required_installment_refs"] == []

    assert bundle.finance_quality_preparation.fingerprint == payload[
        "intermediate_fingerprints"]["finance_quality_preparation"]
    assert bundle.flow_review.fingerprint == payload[
        "intermediate_fingerprints"]["flow_review"]
    assert bundle.payment_capture.to_payload()["case_kind"] == "SYNTHETIC"
    assert bundle.treasury_mandate.to_payload()["mandate_kind"] == "SYNTHETIC"
    assert bundle.flow_mandate.to_payload()["mandate_kind"] == "SYNTHETIC"

    with pytest.raises(FrozenInstanceError):
        bundle._material = b"changed"


def test_structural_fixture_remains_valid_structurally_but_semantically_rejected():
    dataset = load_projection_mock_dataset(STRUCTURAL)
    with pytest.raises(SyntheticSemanticAdapterError) as error:
        build_projection_only_synthetic_material_bundle(dataset)
    assert error.value.code == "INVALID_COMPONENT"
    assert error.value.component == "operation"


def test_public_adapter_requires_validated_dataset_and_closed_constructor():
    with pytest.raises(TypeError):
        build_projection_only_synthetic_material_bundle({})
    with pytest.raises(TypeError):
        ProjectionOnlySyntheticMaterialBundle()


def test_same_dataset_is_reproducible_and_material_change_changes_bundle(tmp_path):
    first_dataset = _dataset(tmp_path / "first")
    first = build_projection_only_synthetic_material_bundle(first_dataset)
    repeated = build_projection_only_synthetic_material_bundle(first_dataset)
    assert first.fingerprint == repeated.fingerprint
    assert first.envelope.fingerprint == repeated.envelope.fingerprint

    def changed(values):
        values["flows/inventory.json"]["perimeters"][0][
            "coverage_reason"] = "Changed synthetic declaration"
    second_dataset = _dataset(tmp_path / "second", changed)
    second = build_projection_only_synthetic_material_bundle(second_dataset)

    assert second_dataset.fingerprint != first_dataset.fingerprint
    assert second.flow_record.fingerprint != first.flow_record.fingerprint
    assert second.envelope.fingerprint != first.envelope.fingerprint
    assert second.fingerprint != first.fingerprint


def test_final_fingerprint_binds_all_declared_intermediates(tmp_path):
    bundle = build_projection_only_synthetic_material_bundle(_dataset(tmp_path))
    fingerprints = bundle.to_payload()["intermediate_fingerprints"]
    assert set(fingerprints) == {
        "finance_package",
        "payment_capture",
        "required_installment_calendar_payload",
        "required_installment_coverage",
        "finance_quality_preparation",
        "criteria_manifest",
        "treasury_support",
        "treasury_assessment",
        "treasury_mandate",
        "treasury_review",
        "flow_record",
        "flow_mandate",
        "flow_review",
    }
    assert fingerprints["finance_package"] == bundle.finance_package.fingerprint
    assert fingerprints["payment_capture"] == bundle.payment_capture.fingerprint
    assert fingerprints["required_installment_coverage"] == (
        bundle.required_installment_coverage.fingerprint)
    assert fingerprints["criteria_manifest"] == bundle.criteria_manifest.fingerprint
    assert fingerprints["treasury_support"] == bundle.treasury_support.fingerprint
    assert fingerprints["treasury_assessment"] == bundle.treasury_assessment.fingerprint
    assert fingerprints["treasury_mandate"] == bundle.treasury_mandate.fingerprint
    assert fingerprints["treasury_review"] == bundle.treasury_review.fingerprint
    assert fingerprints["flow_record"] == bundle.flow_record.fingerprint
    assert fingerprints["flow_mandate"] == bundle.flow_mandate.fingerprint
    assert fingerprints["flow_review"] == bundle.flow_review.fingerprint


def test_public_surface_exposes_only_complete_bundle_not_private_stages():
    assert private_foundation.__all__ == ()
    import eios.core.projection_synthetic_adapter as public_adapter
    assert set(public_adapter.__all__) == {
        "ProjectionOnlySyntheticMaterialBundle",
        "SCHEMA_VERSION",
        "SyntheticSemanticAdapterError",
        "build_projection_only_synthetic_material_bundle",
    }
    assert "_build_synthetic_stage6" not in public_adapter.__all__


def test_complete_bundle_is_not_quality_or_operational_result(tmp_path):
    bundle = build_projection_only_synthetic_material_bundle(_dataset(tmp_path))
    payload = bundle.to_payload()
    envelope = bundle.envelope.to_payload()
    forbidden = {
        "quality_result", "quality_checks", "status", "score", "authorized",
        "decision", "projection_result",
    }
    assert not forbidden & payload.keys()
    assert not forbidden & envelope.keys()
    assert payload["effect_scope"] == "NO_OPERATIONAL_EFFECT"


def test_public_bundle_does_not_execute_finance_quality_or_qtg(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("execution boundary crossed")

    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr("eios.finance.provenance.run_provenanced_finance_basic", forbidden)
    monkeypatch.setattr("eios.quality.gate.evaluate_quality", forbidden)

    bundle = build_projection_only_synthetic_material_bundle(_dataset(tmp_path))
    assert bundle.envelope.to_payload()["profile"] == "PROJECTION_ONLY"
