from inspect import signature
from pathlib import Path

import pytest

import eios.core.reference_simulation_execution as reference_execution
from eios.core.case_provenance import (
    classify_presented_operational_case,
    classify_reference_operational_simulation,
    classify_synthetic_test_case,
)
from eios.core.mvp_execution import run_mvp_execution
from eios.core.operational_intake import empty_operational_expedient_intake_manifest
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.price_integration import build_reference_observed_price_invoker
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from eios.core.reference_simulation_execution import (
    ReferenceSimulationExecution,
    run_reference_operational_simulation,
)
from eios.core.models import DecisionContext, PurchaseOperation
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput
from eios.pricing.sufficiency import SufficiencyObservation
from test_projection_synthetic_foundation import _dataset


SEMANTIC = (
    Path(__file__).parent / "fixtures" / "projection_only_semantic_dataset_01"
)


def _bundle():
    return build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(SEMANTIC)
    )


def _runtime(bundle):
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    return (
        PurchaseOperation.model_validate(dip["purchase"]),
        DecisionContext.model_validate(dip["context"]),
    )


def _qtg(bundle):
    receipt = produce_projection_quality(
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    consumption = consume_projection_quality(
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )
    return receipt, consumption


def _completed_c0(*_):
    return CapabilityExecution(
        capability="C0",
        status=O1ExecutionStatus.COMPLETED,
        result_available=True,
        trace_references=("trace:reference:c0",),
    )


def _run(bundle, *, provenance=None, purchase=None, context=None):
    receipt, consumption = _qtg(bundle)
    bound_purchase, bound_context = _runtime(bundle)
    return run_reference_operational_simulation(
        provenance=provenance or classify_reference_operational_simulation(
            bundle=bundle,
            reference_case_id="REF-PROJECTION-001",
        ),
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase or bound_purchase,
        context=context or bound_context,
        policy_version="REFERENCE-SIMULATION-v1",
        rules_invoker=_completed_c0,
    )


def test_reference_simulation_closes_qtg_and_mvp_without_operational_effect():
    bundle = _bundle()
    execution = _run(bundle)
    payload = execution.to_payload()

    assert payload["execution_kind"] == "REFERENCE_OPERATIONAL_SIMULATION"
    assert payload["reference_case_id"] == "REF-PROJECTION-001"
    assert payload["runtime_scope"] == "PRODUCT_REFERENCE_VALIDATION_ONLY"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["qtg_execution_mode"] == "SYNTHETIC_TEST"
    assert payload["qtg_consumption_scope"] == "TEST_ONLY"
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["case_provenance"]["qtg_mode_policy"] == "SYNTHETIC_TEST_ONLY"
    assert payload["capability_sequence"] == ["QTG", "C0"]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["qtg_quality_result"]["confidence"] == "BAJA"


def test_reference_simulation_preserves_unjustifiable_price_without_authority():
    bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    reference_case_id = "REF-PRICE-UNJUSTIFIABLE"
    price_invoker = build_reference_observed_price_invoker(
        payload=PriceIntelligenceInput(
            decision_context=context, purchase_operation=purchase,
            references=(), evidence_validations=(),
            methodology_version="REF-PRICE-EMPTY-v1",
        ),
        assessment_context=PriceIntelligenceAssessmentContext(
            sufficiency=SufficiencyObservation(),
        ),
        reference_case_id=reference_case_id,
    )
    execution = run_reference_operational_simulation(
        provenance=classify_reference_operational_simulation(
            bundle=bundle, reference_case_id=reference_case_id,
        ),
        bundle=bundle, receipt=receipt, consumption=consumption,
        purchase=purchase, context=context,
        policy_version="REF-PRICE-UNJUSTIFIABLE-v1",
        price_invoker=price_invoker, rules_invoker=_completed_c0,
    ).to_payload()

    price, c0 = execution["execution_outcome"]["capability_results"]
    assert price["status"] == "NOT_EVALUABLE"
    assert price["result_available"] is False
    assert price["unresolved_items"] == ["PRICE_NOT_JUSTIFIABLE"]
    assert c0["status"] == "COMPLETED"
    assert execution["execution_outcome"]["status"] == "PARTIALLY_COMPLETED"
    assert execution["execution_outcome"]["unresolved_items"] == ["PRICE_NOT_JUSTIFIABLE"]
    assert execution["operational_path"] == "FORBIDDEN"
    assert execution["operational_effect"] is False
    assert execution["decision_authority"] is False


def test_reference_simulation_can_validate_positive_synthetic_qtg_without_promotion(tmp_path):
    def complete(values):
        values["flows/inventory.json"]["perimeters"][0]["limitations"] = []
        for finding in values["flows/review.json"]["findings"]:
            if finding["condition"] in {
                "HORIZON_CLASSIFICATION",
                "FLOW_ATTRIBUTE_SUPPORT",
                "ECONOMIC_DUPLICATION",
            }:
                finding["flow_ids"] = ["FLOW-MOCK-PAYMENT-001"]

    bundle = build_projection_only_synthetic_material_bundle(
        _dataset(tmp_path, complete)
    )
    execution = _run(bundle)
    payload = execution.to_payload()

    assert payload["qtg_quality_result"]["status"] == "APTO"
    assert payload["qtg_quality_result"]["confidence"] == "ALTA"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
    assert payload["case_provenance"]["case_kind"] == (
        "REFERENCE_OPERATIONAL_SIMULATION"
    )
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"


def test_reference_execution_rejects_plain_synthetic_test_classification():
    bundle = _bundle()
    receipt, consumption = _qtg(bundle)
    purchase, context = _runtime(bundle)
    provenance = classify_synthetic_test_case(
        load_projection_mock_dataset(SEMANTIC)
    )

    with pytest.raises(ValueError, match="REFERENCE_OPERATIONAL_SIMULATION"):
        run_reference_operational_simulation(
            provenance=provenance,
            bundle=bundle,
            receipt=receipt,
            consumption=consumption,
            purchase=purchase,
            context=context,
            policy_version="REFERENCE-SIMULATION-v1",
            rules_invoker=_completed_c0,
        )


def test_reference_execution_rejects_presented_operational_classification():
    bundle = _bundle()
    receipt, consumption = _qtg(bundle)
    purchase, context = _runtime(bundle)
    provenance = classify_presented_operational_case(
        empty_operational_expedient_intake_manifest()
    )

    with pytest.raises(ValueError, match="REFERENCE_OPERATIONAL_SIMULATION"):
        run_reference_operational_simulation(
            provenance=provenance,
            bundle=bundle,
            receipt=receipt,
            consumption=consumption,
            purchase=purchase,
            context=context,
            policy_version="REFERENCE-SIMULATION-v1",
            rules_invoker=_completed_c0,
        )


def test_reference_provenance_is_bound_to_exact_bundle(tmp_path):
    first = _bundle()

    def changed(values):
        values["flows/inventory.json"]["perimeters"][0][
            "coverage_reason"
        ] = "Different reference simulation material"

    second = build_projection_only_synthetic_material_bundle(
        _dataset(tmp_path, changed)
    )
    provenance = classify_reference_operational_simulation(
        bundle=first,
        reference_case_id="REF-PROJECTION-001",
    )
    receipt, consumption = _qtg(second)
    purchase, context = _runtime(second)

    with pytest.raises(ValueError, match="not reproducible from exact bundle"):
        run_reference_operational_simulation(
            provenance=provenance,
            bundle=second,
            receipt=receipt,
            consumption=consumption,
            purchase=purchase,
            context=context,
            policy_version="REFERENCE-SIMULATION-v1",
            rules_invoker=_completed_c0,
        )


def test_reference_execution_rejects_runtime_identity_drift():
    bundle = _bundle()
    purchase, context = _runtime(bundle)
    foreign = purchase.model_copy(update={"supplier_id": "FOREIGN-SUPPLIER"})

    with pytest.raises(ValueError, match="PurchaseOperation differs"):
        _run(bundle, purchase=foreign, context=context)


def test_reference_facade_delegates_to_mvp_exactly_once(monkeypatch):
    bundle = _bundle()
    original = run_mvp_execution
    calls = []

    def recording(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(reference_execution, "run_mvp_execution", recording)
    execution = _run(bundle)

    assert len(calls) == 1
    assert execution.to_payload()["execution_outcome"]["status"] == "COMPLETED"


def test_reference_facade_signature_does_not_create_qtg_invoker():
    base = set(signature(run_mvp_execution).parameters)
    facade = set(signature(run_reference_operational_simulation).parameters)
    specialized = {"provenance", "bundle", "receipt", "consumption"}

    assert facade - specialized == base
    assert "qtg_invoker" not in facade
    assert "quality_invoker" not in facade


def test_no_public_posthoc_reference_closer_or_operational_promoter():
    public = set(reference_execution.__all__)
    assert not any("close" in name.lower() for name in public)
    assert not any("promot" in name.lower() for name in public)
    assert not any("operational_admission" in name.lower() for name in public)


def test_reference_execution_constructor_is_closed():
    with pytest.raises(TypeError):
        ReferenceSimulationExecution()
