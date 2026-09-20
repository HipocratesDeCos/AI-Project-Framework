from dataclasses import FrozenInstanceError
import inspect
import json

import pytest

from test_finance_decision_input_package import capture  # noqa: F401
from test_finance_quality_preparation import prepared_args  # noqa: F401
from test_required_installment_coverage import material  # noqa: F401
from test_projection_material_envelope import envelope_parts  # noqa: F401
from eios.core.mvp_execution import run_mvp_execution
from eios.core.projection_material_envelope import build_projection_material_envelope
from eios.core.projection_quality_consumer import (
    ProjectionQualityConsumption, consume_projection_quality,
    validate_projection_quality_consumption,
)
from eios.core.projection_quality_producer import produce_projection_quality
from eios.mvp import run_vertical_mvp_support


def synthetic_material(parts):
    envelope = build_projection_material_envelope(**parts["envelope_args"])
    receipt = produce_projection_quality(
        envelope=envelope, execution_mode="SYNTHETIC_TEST")
    return envelope, receipt


def test_test_only_consumption_preserves_complete_validated_receipt(envelope_parts):
    envelope, receipt = synthetic_material(envelope_parts)
    result = consume_projection_quality(receipt=receipt, envelope=envelope,
        execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY")
    payload = result.to_payload()
    assert payload["technical_status"] == "VALIDATED"
    assert payload["functional_quality_result"] == receipt.to_payload()["quality_result"]
    assert payload["receipt"] == receipt.to_payload()
    assert payload["receipt_fingerprint"] == receipt.fingerprint
    assert payload["envelope_fingerprint"] == envelope.fingerprint
    assert payload["operational_effect"] is payload["decision_authority"] is False
    validate_projection_quality_consumption(consumption=result, receipt=receipt,
        envelope=envelope, execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY")


def test_synthetic_receipt_cannot_be_consumed_operationally(envelope_parts):
    envelope, receipt = synthetic_material(envelope_parts)
    with pytest.raises(ValueError):
        consume_projection_quality(receipt=receipt, envelope=envelope,
            execution_mode="SYNTHETIC_TEST", consumption_scope="OPERATIONAL")
    with pytest.raises(ValueError):
        consume_projection_quality(receipt=receipt, envelope=envelope,
            execution_mode="OPERATIONAL", consumption_scope="OPERATIONAL")


def test_crossed_material_and_detached_inputs_are_rejected(envelope_parts):
    envelope, receipt = synthetic_material(envelope_parts)
    foreign_payload = envelope.to_payload()
    foreign_payload["assurance_scope"] = "changed"
    foreign = object.__new__(type(envelope))
    object.__setattr__(foreign, "_material", json.dumps(foreign_payload).encode())
    with pytest.raises(ValueError):
        consume_projection_quality(receipt=receipt, envelope=foreign,
            execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY")
    with pytest.raises(TypeError):
        consume_projection_quality(receipt=receipt.to_payload(), envelope=envelope,
            execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY")


def test_consumption_is_immutable_and_recomputed(envelope_parts):
    envelope, receipt = synthetic_material(envelope_parts)
    result = consume_projection_quality(receipt=receipt, envelope=envelope,
        execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY")
    exported = result.to_payload(); exported["receipt"].clear()
    assert result.to_payload()["receipt"]
    with pytest.raises(FrozenInstanceError):
        result._material = b"changed"
    with pytest.raises(TypeError):
        ProjectionQualityConsumption()
    payload = result.to_payload(); payload["technical_status"] = "COMPLETED"
    forged = object.__new__(ProjectionQualityConsumption)
    object.__setattr__(forged, "_material", json.dumps(payload).encode())
    with pytest.raises(ValueError, match="not reproducible"):
        validate_projection_quality_consumption(consumption=forged, receipt=receipt,
            envelope=envelope, execution_mode="SYNTHETIC_TEST",
            consumption_scope="TEST_ONLY")


@pytest.mark.parametrize("scope", ["OTHER", "", None])
def test_invalid_scope_is_rejected(envelope_parts, scope):
    envelope, receipt = synthetic_material(envelope_parts)
    with pytest.raises(ValueError, match="scope"):
        consume_projection_quality(receipt=receipt, envelope=envelope,
            execution_mode="SYNTHETIC_TEST", consumption_scope=scope)


def test_vertical_quarantine_and_generic_invoker_remain_unchanged():
    assert "quality_invoker" not in inspect.signature(run_mvp_execution).parameters
    assert "quality_invoker" not in inspect.signature(run_vertical_mvp_support).parameters
