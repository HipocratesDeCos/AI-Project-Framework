import json

import pytest

from test_finance_decision_input_package import capture  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401
from test_required_installment_coverage import material  # noqa: F401
from test_projection_material_envelope import envelope_parts  # noqa: F401

from eios.core.operational_admission import (
    build_operational_qtg_from_admitted_envelope,
    preflight_projection_only_operational_envelope,
)
from eios.core.projection_material_envelope import (
    ProjectionMaterialEnvelope,
    build_projection_material_envelope,
)


def _synthetic_envelope(parts):
    return build_projection_material_envelope(**parts["envelope_args"])


def test_synthetic_envelope_is_rejected_without_relabeling(envelope_parts):
    envelope = _synthetic_envelope(envelope_parts)
    result = preflight_projection_only_operational_envelope(envelope)

    assert result.status == "REJECTED_SYNTHETIC_MATERIAL"
    assert result.structurally_admissible is False
    assert any(value == "SYNTHETIC" for _, value in result.material_natures)
    assert any("no equivale a APTO" in item for item in result.limitations)


def test_preflight_preserves_pending_operationally_relevant_gaps(envelope_parts):
    result = preflight_projection_only_operational_envelope(
        _synthetic_envelope(envelope_parts)
    )
    assert (
        result.pending_treasury_conditions
        or result.pending_flow_conditions
        or result.unassessed_captured_flow_ids
        or result.unmatched_candidate_refs
        or result.unreviewed_required_installment_refs
    )


def test_preflight_is_deterministic_for_same_exact_envelope(envelope_parts):
    envelope = _synthetic_envelope(envelope_parts)
    first = preflight_projection_only_operational_envelope(envelope)
    second = preflight_projection_only_operational_envelope(envelope)
    assert first == second
    assert first.preflight_fingerprint == second.preflight_fingerprint


def test_tampered_membership_is_rejected_before_admission(envelope_parts):
    envelope = _synthetic_envelope(envelope_parts)
    payload = envelope.to_payload()
    payload["recomputed_membership"]["contains_synthetic_material"] = False
    payload["recomputed_membership"]["material_natures"] = {
        key: ("PRESENTED_OPERATIONAL" if value is not None else None)
        for key, value in payload["recomputed_membership"]["material_natures"].items()
    }
    forged = object.__new__(ProjectionMaterialEnvelope)
    object.__setattr__(
        forged,
        "_material",
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(),
    )

    with pytest.raises(ValueError, match="membership summary is not reproducible"):
        preflight_projection_only_operational_envelope(forged)


def test_tampered_bound_fingerprint_is_rejected(envelope_parts):
    envelope = _synthetic_envelope(envelope_parts)
    payload = envelope.to_payload()
    payload["preparation"]["fingerprint"] = "0" * 64
    forged = object.__new__(ProjectionMaterialEnvelope)
    object.__setattr__(
        forged,
        "_material",
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(),
    )

    with pytest.raises(ValueError, match="nonreproducible bound fingerprint"):
        preflight_projection_only_operational_envelope(forged)


def test_operational_qtg_builder_cannot_run_from_synthetic_fixture(envelope_parts):
    with pytest.raises(ValueError, match="not admissible"):
        build_operational_qtg_from_admitted_envelope(
            _synthetic_envelope(envelope_parts)
        )


def test_no_positive_operational_fixture_is_fabricated():
    # The first positive OPERATIONAL path is intentionally reserved for a real
    # authorized expediente. Tests must not relabel synthetic material.
    import inspect
    import eios.core.operational_admission as admission

    source = inspect.getsource(admission)
    assert "case_kind=" not in source
    assert "PRESENTED_OPERATIONAL" in source
