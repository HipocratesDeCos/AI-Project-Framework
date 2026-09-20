from pathlib import Path

import pytest

from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_quality_consumer import (
    consume_projection_quality,
    validate_projection_quality_consumption,
)
from eios.core.projection_quality_producer import (
    produce_projection_quality,
    validate_projection_quality_receipt,
)
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from test_projection_synthetic_foundation import _dataset


SEMANTIC = (
    Path(__file__).parent / "fixtures" / "projection_only_semantic_dataset_01"
)


@pytest.fixture(autouse=True)
def prohibit_finance_execution(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Synthetic QTG E2E must not execute Finance")

    monkeypatch.setattr("eios.finance.engine.calculate_finance_basic", forbidden)
    monkeypatch.setattr(
        "eios.finance.provenance.run_provenanced_finance_basic", forbidden)


def _produce_and_consume(bundle):
    receipt = produce_projection_quality(
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    validate_projection_quality_receipt(
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    consumption = consume_projection_quality(
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )
    validate_projection_quality_consumption(
        consumption=consumption,
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )
    return receipt, consumption


def test_physical_semantic_fixture_reaches_validated_test_only_consumption():
    dataset = load_projection_mock_dataset(SEMANTIC)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    receipt, consumption = _produce_and_consume(bundle)

    receipt_payload = receipt.to_payload()
    consumed = consumption.to_payload()

    assert receipt_payload["quality_result"]["status"] == "NO_APTO"
    assert receipt_payload["quality_result"]["confidence"] == "BAJA"
    assert receipt_payload["operational_effect"] is False
    assert receipt_payload["assurance_scope"] == "SYNTHETIC_TEST_RESULT_ONLY"

    conflicts = next(
        item for item in receipt_payload["control_inventory"]
        if item["check"]["control"] == "PROJECTION_CONFLICTS_AND_LIMITATIONS")
    assert conflicts["check"]["satisfied"] is False
    assert conflicts["check"]["reason"] == "projection conflict or limitation reported"

    assert consumed["technical_status"] == "VALIDATED"
    assert consumed["functional_quality_result"] == receipt_payload["quality_result"]
    assert consumed["operational_effect"] is False
    assert consumed["decision_authority"] is False
    assert consumed["envelope_fingerprint"] == bundle.envelope.fingerprint
    assert consumed["receipt_fingerprint"] == receipt.fingerprint


def test_explicitly_completed_synthetic_variant_reaches_nonoperational_apto(tmp_path):
    def complete(values):
        values["flows/inventory.json"]["perimeters"][0]["limitations"] = []
        for finding in values["flows/review.json"]["findings"]:
            if finding["condition"] in {
                "HORIZON_CLASSIFICATION",
                "FLOW_ATTRIBUTE_SUPPORT",
                "ECONOMIC_DUPLICATION",
            }:
                finding["flow_ids"] = ["FLOW-MOCK-PAYMENT-001"]

    dataset = _dataset(tmp_path, complete)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    receipt, consumption = _produce_and_consume(bundle)

    result = receipt.to_payload()["quality_result"]
    consumed = consumption.to_payload()

    assert result["status"] == "APTO"
    assert result["confidence"] == "ALTA"
    assert receipt.to_payload()["operational_effect"] is False
    assert consumed["functional_quality_result"] == result
    assert consumed["consumption_scope"] == "TEST_ONLY"
    assert consumed["operational_effect"] is False
    assert consumed["decision_authority"] is False


def test_complete_membership_does_not_prejudge_quality_result():
    dataset = load_projection_mock_dataset(SEMANTIC)
    bundle = build_projection_only_synthetic_material_bundle(dataset)

    membership = bundle.envelope.to_payload()["recomputed_membership"]
    assert membership["treasury_pending_conditions"] == []
    assert membership["flow_pending_conditions"] == []
    assert membership["unassessed_captured_flow_ids"] == []
    assert membership["unmatched_candidate_refs"] == []
    assert membership["unreviewed_required_installment_refs"] == []

    receipt = produce_projection_quality(
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    assert receipt.to_payload()["quality_result"]["status"] == "NO_APTO"


def test_synthetic_bundle_cannot_cross_operational_producer_boundary():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(SEMANTIC))

    with pytest.raises(ValueError, match="rejects synthetic"):
        produce_projection_quality(
            envelope=bundle.envelope,
            execution_mode="OPERATIONAL",
        )


def test_provenance_chain_is_exact_from_dataset_to_consumption(tmp_path):
    bundle = build_projection_only_synthetic_material_bundle(_dataset(tmp_path))
    receipt, consumption = _produce_and_consume(bundle)

    bundle_payload = bundle.to_payload()
    receipt_payload = receipt.to_payload()
    consumed = consumption.to_payload()

    assert bundle.dataset_fingerprint == bundle_payload["dataset_fingerprint"]
    assert bundle.envelope.fingerprint == bundle_payload["envelope_fingerprint"]
    assert receipt_payload["envelope_fingerprint"] == bundle.envelope.fingerprint
    assert consumed["envelope_fingerprint"] == bundle.envelope.fingerprint
    assert consumed["receipt_fingerprint"] == receipt.fingerprint
    assert consumed["receipt"] == receipt_payload
