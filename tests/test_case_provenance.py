from pathlib import Path

import pytest

import eios.core.case_provenance as taxonomy
from eios.core.case_provenance import (
    CaseProvenance,
    classify_presented_operational_case,
    classify_reference_operational_simulation,
    classify_synthetic_test_case,
)
from eios.core.operational_intake import empty_operational_expedient_intake_manifest
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)


FIXTURES = Path(__file__).parent / "fixtures"
SEMANTIC = FIXTURES / "projection_only_semantic_dataset_01"


def _dataset():
    return load_projection_mock_dataset(SEMANTIC)


def _bundle():
    return build_projection_only_synthetic_material_bundle(_dataset())


def test_synthetic_test_classification_preserves_nonoperational_semantics():
    dataset = _dataset()
    provenance = classify_synthetic_test_case(dataset)
    payload = provenance.to_payload()

    assert payload["case_kind"] == "SYNTHETIC_TEST"
    assert payload["source_type"] == "ProjectionMockDataset"
    assert payload["source_fingerprint"] == dataset.fingerprint
    assert payload["material_nature"] == "SYNTHETIC"
    assert payload["qtg_execution_mode"] == "SYNTHETIC_TEST"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert payload["validation_scope"] == "TECHNICAL_TEST"
    assert payload["requires_operational_preflight"] is False
    assert payload["decision_authority"] is False


def test_reference_simulation_is_product_e2e_but_remains_synthetic():
    bundle = _bundle()
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id="REF-PROJECTION-001",
    )
    payload = provenance.to_payload()

    assert payload["case_kind"] == "REFERENCE_OPERATIONAL_SIMULATION"
    assert payload["source_type"] == "ProjectionOnlySyntheticMaterialBundle"
    assert payload["source_fingerprint"] == bundle.fingerprint
    assert payload["reference_case_id"] == "REF-PROJECTION-001"
    assert payload["material_nature"] == "SYNTHETIC"
    assert payload["qtg_execution_mode"] == "SYNTHETIC_TEST"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert payload["validation_scope"] == "PRODUCT_REFERENCE_E2E"
    assert payload["decision_authority"] is False
    assert bundle.to_payload()["case_kind"] == "SYNTHETIC"
    assert bundle.envelope.to_payload()["recomputed_membership"][
        "contains_synthetic_material"
    ] is True


def test_presented_operational_classification_grants_no_admission_or_effect():
    manifest = empty_operational_expedient_intake_manifest()
    provenance = classify_presented_operational_case(manifest)
    payload = provenance.to_payload()

    assert payload["case_kind"] == "PRESENTED_OPERATIONAL"
    assert payload["source_type"] == "OperationalExpedientIntakeManifest"
    assert payload["source_fingerprint"] == manifest.manifest_fingerprint
    assert payload["material_nature"] == "PRESENTED_OPERATIONAL"
    assert payload["qtg_execution_mode"] == "OPERATIONAL"
    assert payload["operational_path"] == "REQUIRES_ADMISSION"
    assert payload["effect_scope"] == "NOT_GRANTED_BY_CLASSIFICATION"
    assert payload["validation_scope"] == "ENTERPRISE_PRESENTED_CASE"
    assert payload["requires_operational_preflight"] is True
    assert payload["decision_authority"] is False
    assert manifest.readiness == "REQUIRED_SET_INCOMPLETE"


def test_classifiers_are_source_typed_and_do_not_relabel_foreign_material():
    dataset = _dataset()
    bundle = _bundle()
    manifest = empty_operational_expedient_intake_manifest()

    with pytest.raises(TypeError):
        classify_reference_operational_simulation(
            bundle=dataset,
            reference_case_id="REF-001",
        )
    with pytest.raises(TypeError):
        classify_presented_operational_case(bundle)
    with pytest.raises(TypeError):
        classify_synthetic_test_case(manifest)


def test_reference_case_identifier_is_explicit_and_canonical():
    bundle = _bundle()
    for bad in ("", " REF-001", "REF-001 "):
        with pytest.raises(ValueError, match="reference_case_id"):
            classify_reference_operational_simulation(
                bundle=bundle,
                reference_case_id=bad,
            )


def test_same_source_and_reference_id_produce_same_provenance_fingerprint():
    bundle = _bundle()
    first = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id="REF-PROJECTION-001",
    )
    second = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id="REF-PROJECTION-001",
    )
    assert first.to_payload() == second.to_payload()
    assert first.fingerprint == second.fingerprint


def test_taxonomy_exposes_no_generic_promotion_or_conversion_api():
    public = set(taxonomy.__all__)
    assert not any("promot" in name.lower() for name in public)
    assert not any("convert" in name.lower() for name in public)
    assert "classify_reference_operational_simulation" in public
    assert "classify_presented_operational_case" in public


def test_case_provenance_constructor_is_closed():
    with pytest.raises(TypeError):
        CaseProvenance()
