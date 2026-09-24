from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import (
    DecisionContext,
    Evidence,
    EvidenceValidation,
    PurchaseOperation,
)
from eios.core.negotiation_intelligence import NegotiationContent
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.price_integration import build_provenanced_price_invoker
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from eios.core.reference_simulation_execution import (
    run_reference_operational_simulation,
)
from eios.core.tco_integration import build_provenanced_tco_invoker
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet,
    DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding,
    decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedDecisionTwinAlternativeInput,
    ProvenancedScenarioAnalyticsInput,
    NegotiationContentEvidence,
    build_provenanced_decision_twin_comparison,
    build_provenanced_decision_twin_invoker,
    build_provenanced_ni_ladder_invokers,
    build_provenanced_rules_engine_c0_invoker,
    build_provenanced_scenario_coordination_invoker,
)
from eios.rules.catalog import authorized_rule
from eios.rules.data_quality import evaluate_r_dat_003
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.tco.models import TCOInput
from eios.supplier import (
    SupplierEvidenceInput,
    SupplierRiskDimensionAssessment,
    build_provenanced_supplier_risk_value_invoker,
    evaluate_supplier_evidence,
)


SEMANTIC = (
    Path(__file__).parent / "fixtures" / "projection_only_semantic_dataset_01"
)
REFERENCE_CASE_ID = "REF-BUSINESS-001"
REFERENCE_COMPANY_ID = "COMPANY-MOCK-001"


def _bundle():
    dataset = load_projection_mock_dataset(SEMANTIC)
    return dataset, build_projection_only_synthetic_material_bundle(dataset)


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


def _provenanced_c0_invoker(purchase, context):
    requirement_evidence = Evidence(
        evidence_id="E-REF-REQ-QTG",
        source_type="ReferenceRequirementEvidence",
        source_ref="reference:business:001:requirement:qtg",
        captured_at=purchase.operation_date,
        state="DEMONSTRATED",
        demonstration_ref="reference:business:001:requirement:qtg:demonstrated",
    )
    requirement_set = DecisionEvidenceRequirementSet(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        company_scope=REFERENCE_COMPANY_ID,
        purchase_operation_ref=decision_evidence_purchase_ref(purchase),
        effective_date=purchase.operation_date,
        requirement_set_id="REQSET-REF-BUSINESS-001",
        requirement_set_version="1.0",
        requirement_ids=("REQ-PROJECTION-QUALITY",),
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        methodology_ref="METHOD-REF-BUSINESS-001-DATA",
        trace_refs=("trace:reference:requirements",),
    )
    requirement_binding = RequirementEvidenceBinding(
        requirement_id="REQ-PROJECTION-QUALITY",
        classification="SATISFIED",
        evidence=(requirement_evidence,),
        classification_ref="reference:business:001:classification:qtg:satisfied",
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        trace_refs=("trace:reference:requirement:qtg",),
    )
    producer = DecisionEvidenceSufficiencyProducer(
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        methodology_ref="METHOD-REF-BUSINESS-001-DATA",
    )
    observation = producer.produce(
        purchase=purchase,
        context=context,
        company_scope=REFERENCE_COMPANY_ID,
        state="AVAILABLE",
        requirement_set=requirement_set,
        bindings=(requirement_binding,),
        source_ref="reference:business:001:data-sufficiency",
        trace_refs=("trace:reference:data-sufficiency",),
    )
    sufficiency_evidence = Evidence(
        evidence_id="E-REF-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref="reference:business:001:data-sufficiency:evidence",
        captured_at=purchase.operation_date,
        state="DEMONSTRATED",
        demonstration_ref=decision_evidence_sufficiency_ref(observation),
    )
    rule = authorized_rule("R-DAT-003", context.rules_version)
    assessment = evaluate_r_dat_003(
        purchase=purchase,
        context=context,
        rule=rule,
        observation=observation,
        sufficiency_evidence=sufficiency_evidence,
    )
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    binding = AssessmentTraceBinding(
        assessment=assessment,
        trace=trace,
    )
    invoker = build_provenanced_rules_engine_c0_invoker(
        bindings=(binding,),
        base_result="COMPRAR",
    )
    return invoker, assessment, trace



def _provenanced_price_invoker(purchase, context):
    reference_ids = ("REF-PRICE-TX-001", "REF-PRICE-TX-002")
    evidence_ids = ("E-REF-PRICE-001", "E-REF-PRICE-002")
    references = (
        PriceReference(
            source_transaction_id=reference_ids[0],
            article_identity=purchase.article_id,
            supplier_identity="SUPPLIER-REFERENCE-A",
            quantity=Decimal("8"),
            unit="UNIT",
            unit_price=Decimal("19.50"),
            currency="EUR",
            operation_date=purchase.operation_date - timedelta(days=10),
            evidence_refs=(evidence_ids[0],),
        ),
        PriceReference(
            source_transaction_id=reference_ids[1],
            article_identity=purchase.article_id,
            supplier_identity="SUPPLIER-REFERENCE-B",
            quantity=Decimal("12"),
            unit="UNIT",
            unit_price=Decimal("21.00"),
            currency="EUR",
            operation_date=purchase.operation_date - timedelta(days=5),
            evidence_refs=(evidence_ids[1],),
        ),
    )
    validations = tuple(
        EvidenceValidation(
            evidence_id=evidence_id,
            status="VALID",
            reason="Synthetic reference price evidence validated for product test",
        )
        for evidence_id in evidence_ids
    )
    price_input = PriceIntelligenceInput(
        decision_context=context.model_copy(deep=True),
        purchase_operation=purchase.model_copy(deep=True),
        references=references,
        evidence_validations=validations,
        normalization_basis=None,
        economic_basis_evidence=(),
        methodology_version="REF-BUSINESS-001-PRICE-v1",
    )
    representativeness = {
        reference_id: RepresentativenessObservation(
            ordinary_market_context=True,
            exceptional_condition=False,
            material_commercial_distortion=False,
            contradiction_material_unresolved=False,
            evidence_refs=(evidence_id,),
            rule_reference="REF-BUSINESS-001-REPRESENTATIVENESS-v1",
            trace_reference=f"trace:reference:price:{reference_id}",
        )
        for reference_id, evidence_id in zip(reference_ids, evidence_ids)
    }
    assessment_context = PriceIntelligenceAssessmentContext(
        temporal={
            reference_id: (
                "ELIGIBLE",
                f"trace:reference:price:temporal:{reference_id}",
            )
            for reference_id in reference_ids
        },
        representativeness=representativeness,
        sufficiency=SufficiencyObservation(
            evidence_sufficient=True,
            contradictions_resolved=True,
            methodological_limitations=(),
            evidence_refs=evidence_ids,
            rule_reference="REF-BUSINESS-001-PRICE-SUFFICIENCY-v1",
            trace_reference="trace:reference:price:sufficiency",
            selected_reference_ids=reference_ids,
        ),
    )
    return build_provenanced_price_invoker(
        payload=price_input,
        assessment_context=assessment_context,
    )


def _provenanced_tco_invoker(purchase):
    return build_provenanced_tco_invoker(
        payload=TCOInput(purchase_operation=purchase.model_copy(deep=True))
    )



def _provenanced_supplier_risk_invoker(purchase, context):
    supplier_result = evaluate_supplier_evidence(
        SupplierEvidenceInput(
            context=context.model_copy(deep=True),
            purchase_operation=purchase.model_copy(deep=True),
            company_scope=REFERENCE_COMPANY_ID,
            evaluation_date=purchase.operation_date,
            candidates=(),
            observations=(),
            historical_facts=(),
            external_metrics=(),
            signals=(),
            comparison_requests=(),
        )
    )
    evidences = (
        Evidence(
            evidence_id="E-REF-SRV-AUTH",
            source_type="supplier-risk",
            source_ref="reference:business:001:supplier:risk:authority",
            captured_at=purchase.operation_date,
            state="DEMONSTRATED",
            demonstration_ref="authority:reference:business:001:supplier:risk",
        ),
        Evidence(
            evidence_id="E-REF-SRV-RISK",
            source_type="supplier-risk",
            source_ref="reference:business:001:supplier:risk:assessment",
            captured_at=purchase.operation_date,
            state="DEMONSTRATED",
            demonstration_ref="assessment:reference:business:001:supplier:risk",
        ),
    )
    risk = SupplierRiskDimensionAssessment(
        supplier_id=purchase.supplier_id,
        dimension="RELIABILITY",
        state="FAVORABLE",
        authority_ref="authority:reference:business:001:supplier:risk",
        methodology_ref="method:reference:business:001:supplier:risk:v1",
        assessment_ref="assessment:reference:business:001:supplier:risk",
        evidence_refs=("E-REF-SRV-RISK",),
        trace_refs=("trace:reference:business:001:supplier:risk",),
    )
    return build_provenanced_supplier_risk_value_invoker(
        supplier_result=supplier_result,
        risk_assessments=(risk,),
        value_assessments=(),
        evidences=evidences,
    )


def _scenario_sources(purchase, context):
    preparation = prepare_o4_o2_o3_orchestration(
        context=context,
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1, 2),
            ),
        ),
        policy=GenerationPolicy(policy_version="REF-BUSINESS-001-SCENARIOS-v1"),
    )
    valid = tuple(
        item for item in preparation.materialization.scenarios
        if item.status.value == "VALID"
    )
    assert len(valid) == 2
    inputs = []
    traces = []
    for scenario, delta in zip(valid, (1, 2)):
        child_purchase = purchase.model_copy(update={
            "scenario_id": scenario.scenario_id,
            "quantity": purchase.quantity + Decimal(delta),
        }, deep=True)
        child_context = context.model_copy(
            update={"scenario_id": scenario.scenario_id}, deep=True
        )
        _, assessment, trace = _provenanced_c0_invoker(
            child_purchase, child_context
        )
        inputs.append(ProvenancedScenarioAnalyticsInput(
            scenario_id=scenario.scenario_id,
            purchase=child_purchase,
            assessment_bindings=(AssessmentTraceBinding(
                assessment=assessment, trace=trace,
            ),),
        ))
        traces.append(trace.trace_id)
    return preparation, tuple(inputs), tuple(traces)


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


def _twin_alternatives(inputs):
    return tuple(
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref=f"REF-BUSINESS-001-ALT-{index}",
            scenario_input=item,
        )
        for index, item in enumerate(inputs, start=1)
    )


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


def _synthetic_negotiation_sources(purchase, context, trace_id):
    authority_ref = "authority:synthetic:ref-business-001:negotiation:v1"
    evidence = Evidence(
        evidence_id="E-REF-NI-AUTH",
        source_type="synthetic-negotiation-authority",
        source_ref="reference:business:001:negotiation:authority",
        captured_at=purchase.operation_date,
        state="DEMONSTRATED",
        demonstration_ref=authority_ref,
    )
    carrier = NegotiationContentEvidence(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        authority_ref=authority_ref,
        negotiation_content=NegotiationContent(
            objective="Explore a conditional improvement in the synthetic offer",
            opening_request="Request a revised written quotation",
            fallback="Retain the simulated offer pending human review",
        ),
        evidence_refs=(evidence.evidence_id,),
        trace_refs=(trace_id,),
        authority_state="AUTHORIZED",
    )
    return carrier, (evidence,)


def test_reference_business_case_001_runs_synthetic_negotiation_and_ladder():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id=REFERENCE_CASE_ID,
    )
    preparation, inputs, _ = _scenario_sources(purchase, context)
    c0_invoker, _, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    ni_invoker, ladder_invoker = build_provenanced_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences,
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
    c0_invoker, _, trace = _provenanced_c0_invoker(purchase, context)
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    denied = carrier.model_copy(update={"authority_state": "NOT_AUTHORIZED"})
    ni_invoker, _ = build_provenanced_ni_ladder_invokers(
        content_evidence=denied, evidences=evidences,
    )
    with pytest.raises(ValueError, match="no autorizado"):
        ni_invoker(purchase, context)
