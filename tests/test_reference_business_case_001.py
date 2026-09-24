from decimal import Decimal
from pathlib import Path

import pytest

from examples.reference_business_case_001 import (
    _bundle, _runtime, _qtg, _provenanced_c0_invoker,
    _provenanced_price_invoker, _provenanced_tco_invoker,
    _provenanced_supplier_risk_invoker, _scenario_sources,
    _twin_alternatives, _synthetic_negotiation_sources,
    execute_reference_business_case,
)
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from eios.core.reference_simulation_execution import (
    run_reference_operational_simulation,
)
from eios.rules import (
    AssessmentTraceBinding, build_c0_bound_ni_ladder_invokers,
    build_provenanced_decision_twin_comparison,
    build_provenanced_decision_twin_invoker,
    build_provenanced_scenario_coordination_invoker,
)


SEMANTIC = (
    Path(__file__).parent / "fixtures" / "projection_only_semantic_dataset_01"
)
QTG_ELIGIBLE = (
    Path(__file__).parent / "fixtures" / "reference_business_case_001_qtg_eligible"
)
REFERENCE_CASE_ID = "REF-BUSINESS-001"












def test_reference_business_case_001_uses_physical_synthetic_dataset():
    dataset, bundle = _bundle()
    purchase, context = _runtime(bundle)

    assert dataset.to_payload()["dataset_id"] == "EIOS-PROJECTION-SEMANTIC-MOCK-001"
    assert dataset.to_payload()["case_kind"] == "SYNTHETIC"
    assert dataset.to_payload()["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert purchase.decision_id == "DECISION-MOCK-001"
    assert purchase.supplier_id == "SUPPLIER-MOCK-001"
    assert str(purchase.quantity) == "10"
    assert str(purchase.unit_price) == "20.50"
    assert context.data_snapshot_id == "SNAPSHOT-MOCK-001"


def test_reference_business_case_001_runs_qtg_plus_provenanced_c0():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=REFERENCE_CASE_ID,
    )
    c0_invoker, assessment, trace = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v1",
        rules_invoker=c0_invoker,
    )
    payload = execution.to_payload()

    assert assessment.rule_id == "R-DAT-003"
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert trace.trace_id
    assert payload["reference_case_id"] == REFERENCE_CASE_ID
    assert payload["capability_sequence"] == ["QTG", "C0"]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert payload["execution_outcome"]["capability_results"][0]["capability"] == "C0"
    assert payload["execution_outcome"]["capability_results"][0]["status"] == "COMPLETED"
    assert payload["execution_outcome"]["capability_results"][0][
        "trace_references"
    ] == [trace.trace_id]
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
    assert payload["operational_path"] == "FORBIDDEN"


def test_reference_business_case_001_preserves_known_qtg_limitation():
    _, bundle = _bundle()
    receipt, consumption = _qtg(bundle)

    quality = consumption.to_payload()["functional_quality_result"]
    assert quality["status"] == "NO_APTO"
    assert quality["confidence"] == "BAJA"
    assert receipt.to_payload()["operational_effect"] is False
    assert consumption.to_payload()["operational_effect"] is False


def test_reference_business_case_001_extends_to_price_tco_and_c0():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=REFERENCE_CASE_ID,
    )
    c0_invoker, _, _ = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v2",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        rules_invoker=c0_invoker,
    )
    payload = execution.to_payload()
    capability_results = {
        item["capability"]: item
        for item in payload["execution_outcome"]["capability_results"]
    }

    assert payload["capability_sequence"] == ["QTG", "PRICE", "TCO", "C0"]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert set(capability_results) == {"PRICE", "TCO", "C0"}
    assert all(
        item["status"] == "COMPLETED" and item["result_available"] is True
        for item in capability_results.values()
    )
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["qtg_quality_result"]["confidence"] == "BAJA"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


def test_reference_business_case_001_extends_to_supplier_risk_value():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=REFERENCE_CASE_ID,
    )
    c0_invoker, _, _ = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v3",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        supplier_risk_value_invoker=_provenanced_supplier_risk_invoker(
            purchase, context
        ),
        rules_invoker=c0_invoker,
    )
    payload = execution.to_payload()
    capability_results = {
        item["capability"]: item
        for item in payload["execution_outcome"]["capability_results"]
    }

    assert payload["capability_sequence"] == [
        "QTG",
        "PRICE",
        "TCO",
        "SUPPLIER_RISK_VALUE",
        "C0",
    ]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert capability_results["SUPPLIER_RISK_VALUE"]["status"] == "COMPLETED"
    assert capability_results["SUPPLIER_RISK_VALUE"]["result_available"] is True
    assert capability_results["SUPPLIER_RISK_VALUE"]["trace_references"] == [
        "trace:reference:business:001:supplier:risk"
    ]
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


def test_reference_business_case_001_coordinates_provenanced_scenarios():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id=REFERENCE_CASE_ID,
    )
    preparation, inputs, traces = _scenario_sources(purchase, context)
    c0_invoker, _, _ = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v4",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        supplier_risk_value_invoker=_provenanced_supplier_risk_invoker(
            purchase, context
        ),
        rules_invoker=c0_invoker,
        scenario_coordination_invoker=(
            build_provenanced_scenario_coordination_invoker(
                preparation=preparation, inputs=inputs,
            )
        ),
    )
    payload = execution.to_payload()
    results = payload["execution_outcome"]["capability_results"]
    assert payload["capability_sequence"] == [
        "QTG", "PRICE", "TCO", "SUPPLIER_RISK_VALUE", "C0",
        "SCENARIO_COORDINATION",
    ]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert [item["capability"] for item in results] == payload["capability_sequence"][1:]
    assert results[-1]["status"] == "COMPLETED"
    assert results[-1]["trace_references"] == list(traces)
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["case_provenance"]["qtg_mode_policy"] == "SYNTHETIC_TEST_ONLY"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


def test_reference_business_case_001_rejects_foreign_child_trace():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    preparation, inputs, _ = _scenario_sources(purchase, context)
    first, second = inputs
    foreign = first.model_copy(update={
        "assessment_bindings": second.assessment_bindings,
    }, deep=True)
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation, inputs=(foreign, second),
    )

    with pytest.raises(ValueError):
        invoker(purchase, context)




def test_reference_business_case_001_compares_provenanced_alternatives():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id=REFERENCE_CASE_ID,
    )
    preparation, inputs, traces = _scenario_sources(purchase, context)
    alternatives = _twin_alternatives(inputs)
    comparison = build_provenanced_decision_twin_comparison(
        purchase=purchase, context=context, preparation=preparation,
        alternatives=alternatives,
    )
    c0_invoker, _, _ = _provenanced_c0_invoker(purchase, context)
    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v5",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        supplier_risk_value_invoker=_provenanced_supplier_risk_invoker(
            purchase, context
        ),
        rules_invoker=c0_invoker,
        decision_twin_invoker=build_provenanced_decision_twin_invoker(
            preparation=preparation, alternatives=alternatives,
        ),
        scenario_coordination_invoker=(
            build_provenanced_scenario_coordination_invoker(
                preparation=preparation, inputs=inputs,
            )
        ),
    )
    payload = execution.to_payload()
    results = payload["execution_outcome"]["capability_results"]

    assert comparison.alternatives == tuple(
        item.representation_ref for item in alternatives
    )
    assert set(comparison.trace_refs) == set(traces)
    by_attribute = {item.attribute: item for item in comparison.observations}
    assert all(value == {} for _, value in by_attribute["conditions"].values)
    assert all(value == {} for _, value in by_attribute["consequences"].values)
    assert all(value == () for _, value in by_attribute["risk_refs"].values)
    assert payload["capability_sequence"] == [
        "QTG", "PRICE", "TCO", "SUPPLIER_RISK_VALUE", "C0",
        "DECISION_TWIN", "SCENARIO_COORDINATION",
    ]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert [item["capability"] for item in results] == payload["capability_sequence"][1:]
    assert results[-2]["status"] == "COMPLETED"
    assert set(results[-2]["trace_references"]) == set(traces)
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


def test_reference_business_case_001_rejects_duplicate_twin_representations():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    preparation, inputs, _ = _scenario_sources(purchase, context)
    first, second = _twin_alternatives(inputs)
    duplicate = second.model_copy(
        update={"representation_ref": first.representation_ref}, deep=True
    )
    with pytest.raises(ValueError, match="representation_ref duplicada"):
        build_provenanced_decision_twin_comparison(
            purchase=purchase, context=context, preparation=preparation,
            alternatives=(first, duplicate),
        )




def test_reference_business_case_001_runs_synthetic_negotiation_and_ladder():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id=REFERENCE_CASE_ID,
    )
    preparation, inputs, _ = _scenario_sources(purchase, context)
    c0_invoker, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    ni_invoker, ladder_invoker = build_c0_bound_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
    )
    execution = run_reference_operational_simulation(
        provenance=provenance, bundle=bundle, receipt=receipt,
        consumption=consumption, purchase=purchase, context=context,
        policy_version="REF-BUSINESS-001-v6",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        supplier_risk_value_invoker=_provenanced_supplier_risk_invoker(
            purchase, context
        ),
        rules_invoker=c0_invoker,
        decision_twin_invoker=build_provenanced_decision_twin_invoker(
            preparation=preparation, alternatives=_twin_alternatives(inputs),
        ),
        scenario_coordination_invoker=(
            build_provenanced_scenario_coordination_invoker(
                preparation=preparation, inputs=inputs,
            )
        ),
        negotiation_intelligence_invoker=ni_invoker,
        negotiation_ladder_invoker=ladder_invoker,
    )
    payload = execution.to_payload()
    results = payload["execution_outcome"]["capability_results"]
    assert payload["capability_sequence"] == [
        "QTG", "PRICE", "TCO", "SUPPLIER_RISK_VALUE", "C0",
        "DECISION_TWIN", "SCENARIO_COORDINATION",
        "NEGOTIATION_INTELLIGENCE", "NEGOTIATION_LADDER",
    ]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert all(item["status"] == "COMPLETED" for item in results)
    assert results[-2]["trace_references"] == [trace.trace_id]
    assert results[-1]["trace_references"] == [trace.trace_id]
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


def test_reference_business_case_001_rejects_unauthorized_negotiation():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    denied = carrier.model_copy(update={"authority_state": "NOT_AUTHORIZED"})
    ni_invoker, _ = build_c0_bound_ni_ladder_invokers(
        content_evidence=denied, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
    )
    with pytest.raises(ValueError, match="no autorizado"):
        ni_invoker(purchase, context)


def test_reference_negotiation_rejects_foreign_or_unclaimed_c0_trace():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    binding = AssessmentTraceBinding(assessment=assessment, trace=trace)
    with pytest.raises(ValueError, match="trace_refs no coincide"):
        build_c0_bound_ni_ladder_invokers(
            content_evidence=carrier.model_copy(
                update={"trace_refs": ("FOREIGN-TRACE",)}
            ),
            evidences=evidences, bindings=(binding,),
        )

    ni_invoker, ladder_invoker = build_c0_bound_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences, bindings=(binding,),
    )
    foreign_purchase = purchase.model_copy(
        update={"quantity": purchase.quantity + Decimal("1")}
    )
    for invoker in (ni_invoker, ladder_invoker):
        with pytest.raises(ValueError, match="input_fingerprint incompatible"):
            invoker(foreign_purchase, context)


def test_reference_negotiation_rejects_tampered_c0_assessment():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    _, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    tampered = assessment.model_copy(update={"reason": "altered"})
    ni_invoker, _ = build_c0_bound_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=tampered, trace=trace),),
    )
    with pytest.raises(ValueError, match="assessment_fingerprint incompatible"):
        ni_invoker(purchase, context)


def test_reference_business_case_001_qtg_eligible_runs_full_synthetic_sequence():
    dataset = load_projection_mock_dataset(QTG_ELIGIBLE)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-001-QTG-ELIGIBLE",
    )
    preparation, inputs, _ = _scenario_sources(purchase, context)
    c0_invoker, assessment, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    ni_invoker, ladder_invoker = build_c0_bound_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
    )
    execution = run_reference_operational_simulation(
        provenance=provenance, bundle=bundle, receipt=receipt,
        consumption=consumption, purchase=purchase, context=context,
        policy_version="REF-BUSINESS-001-QTG-ELIGIBLE-v1",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        supplier_risk_value_invoker=_provenanced_supplier_risk_invoker(
            purchase, context
        ),
        rules_invoker=c0_invoker,
        decision_twin_invoker=build_provenanced_decision_twin_invoker(
            preparation=preparation, alternatives=_twin_alternatives(inputs),
        ),
        scenario_coordination_invoker=(
            build_provenanced_scenario_coordination_invoker(
                preparation=preparation, inputs=inputs,
            )
        ),
        negotiation_intelligence_invoker=ni_invoker,
        negotiation_ladder_invoker=ladder_invoker,
    )
    payload = execution.to_payload()
    assert dataset.to_payload()["dataset_id"] == (
        "EIOS-REFERENCE-BUSINESS-001-QTG-ELIGIBLE"
    )
    assert payload["qtg_quality_result"]["status"] == "APTO"
    assert payload["qtg_quality_result"]["confidence"] == "ALTA"
    assert payload["capability_sequence"] == [
        "QTG", "PRICE", "TCO", "SUPPLIER_RISK_VALUE", "C0",
        "DECISION_TWIN", "SCENARIO_COORDINATION",
        "NEGOTIATION_INTELLIGENCE", "NEGOTIATION_LADDER",
    ]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["case_provenance"]["qtg_mode_policy"] == "SYNTHETIC_TEST_ONLY"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False


@pytest.mark.parametrize(
    ("variant", "expected_status", "expected_confidence"),
    (("negative", "NO_APTO", "BAJA"), ("qtg-eligible", "APTO", "ALTA")),
)
def test_executable_reference_runner_preserves_nonoperational_boundary(
    variant, expected_status, expected_confidence,
):
    execution = execute_reference_business_case(variant=variant)
    payload = execution.to_payload()
    assert payload["qtg_quality_result"]["status"] == expected_status
    assert payload["qtg_quality_result"]["confidence"] == expected_confidence
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert len(payload["capability_sequence"]) == 9
    assert payload["case_provenance"]["material_nature"] == "SYNTHETIC"
    assert payload["operational_path"] == "FORBIDDEN"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
