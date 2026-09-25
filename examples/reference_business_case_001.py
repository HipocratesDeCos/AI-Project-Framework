"""Executable synthetic Reference Business Case 001, never operational."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from eios.core.c0_reproducibility import build_trace
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import DecisionContext, Evidence, EvidenceValidation, PurchaseOperation
from eios.core.negotiation_intelligence import NegotiationContent
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.price_integration import (
    build_provenanced_price_invoker, build_reference_observed_price_invoker,
)
from eios.core.reference_price_observation import _close_reference_price_observation
from eios.core.reference_tco_observation import _close_reference_tco_observation
from eios.core.reference_supplier_risk_observation import (
    _close_reference_supplier_risk_observation,
)
from eios.core.reference_c0_observation import _close_reference_c0_observation
from eios.core.reference_decision_twin_observation import (
    _close_reference_decision_twin_observation,
)
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.core.reference_simulation_execution import run_reference_operational_simulation
from eios.core.tco_integration import (
    build_provenanced_tco_invoker, build_reference_observed_tco_invoker,
)
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet, DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding, decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.rules import (
    AssessmentTraceBinding, NegotiationContentEvidence,
    ProvenancedDecisionTwinAlternativeInput, ProvenancedScenarioAnalyticsInput,
    build_c0_bound_ni_ladder_invokers,
    build_provenanced_decision_twin_invoker,
    build_provenanced_rules_engine_c0_invoker,
    build_provenanced_scenario_coordination_invoker,
)
from eios.rules.catalog import authorized_rule
from eios.rules.provenance import build_reference_observed_rules_engine_c0_invoker
from eios.rules.decision_twin_integration import build_reference_observed_decision_twin_invoker
from eios.rules.data_quality import evaluate_r_dat_003
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.tco.models import TCOInput
from eios.supplier import (
    SupplierEvidenceInput, SupplierRiskDimensionAssessment,
    build_provenanced_supplier_risk_value_invoker, evaluate_supplier_evidence,
)
from eios.supplier.risk_value import build_reference_observed_supplier_risk_value_invoker

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
SEMANTIC = FIXTURES / "projection_only_semantic_dataset_01"
QTG_ELIGIBLE = FIXTURES / "reference_business_case_001_qtg_eligible"
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

def _provenanced_c0_invoker(purchase, context, *, observed=False,
                           reference_case_id=None):
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
    trace = trace.model_copy(update={
        "created_at": datetime.combine(purchase.operation_date, datetime.min.time(),
                                        tzinfo=timezone.utc),
    })
    binding = AssessmentTraceBinding(
        assessment=assessment,
        trace=trace,
    )
    if observed:
        invoker = build_reference_observed_rules_engine_c0_invoker(
            bindings=(binding,), base_result="COMPRAR",
            reference_case_id=reference_case_id,
        )
    else:
        invoker = build_provenanced_rules_engine_c0_invoker(
            bindings=(binding,), base_result="COMPRAR",
        )
    return invoker, assessment, trace

def _provenanced_price_invoker(purchase, context, *, observed=False,
                              reference_case_id=None):
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
    kwargs = {"payload": price_input, "assessment_context": assessment_context}
    if observed:
        return build_reference_observed_price_invoker(
            **kwargs, reference_case_id=reference_case_id,
        )
    return build_provenanced_price_invoker(**kwargs)

def _provenanced_tco_invoker(purchase, *, observed=False, reference_case_id=None):
    payload = TCOInput(purchase_operation=purchase.model_copy(deep=True))
    if observed:
        return build_reference_observed_tco_invoker(
            payload=payload, reference_case_id=reference_case_id,
        )
    return build_provenanced_tco_invoker(payload=payload)

def _provenanced_supplier_risk_invoker(purchase, context, *, observed=False,
                                      reference_case_id=None):
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
    kwargs = dict(
        supplier_result=supplier_result,
        risk_assessments=(risk,),
        value_assessments=(),
        evidences=evidences,
    )
    if observed:
        return build_reference_observed_supplier_risk_value_invoker(
            reference_case_id=reference_case_id, purchase=purchase, **kwargs,
        )
    return build_provenanced_supplier_risk_value_invoker(**kwargs)

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

def _twin_alternatives(inputs):
    return tuple(
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref=f"REF-BUSINESS-001-ALT-{index}",
            scenario_input=item,
        )
        for index, item in enumerate(inputs, start=1)
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


def _execute_reference_business_case(*, variant: str, observe_price: bool,
                                     observe_tco: bool = False,
                                     observe_supplier_risk: bool = False,
                                     observe_c0: bool = False,
                                     observe_twin: bool = False,
                                     return_observation_map: bool = False):
    """Run the full closed reference sequence from one of two physical fixtures."""
    if variant not in {"negative", "qtg-eligible"}:
        raise ValueError("variant must be negative or qtg-eligible")
    source = SEMANTIC if variant == "negative" else QTG_ELIGIBLE
    dataset = load_projection_mock_dataset(source)
    bundle = build_projection_only_synthetic_material_bundle(dataset)
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    reference_case_id = (
        REFERENCE_CASE_ID if variant == "negative"
        else "REF-BUSINESS-001-QTG-ELIGIBLE"
    )
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id=reference_case_id,
    )
    preparation, inputs, _ = _scenario_sources(purchase, context)
    c0_invoker, assessment, trace = _provenanced_c0_invoker(
        purchase, context, observed=observe_c0,
        reference_case_id=reference_case_id,
    )
    carrier, evidences = _synthetic_negotiation_sources(
        purchase, context, trace.trace_id
    )
    ni_invoker, ladder_invoker = build_c0_bound_ni_ladder_invokers(
        content_evidence=carrier, evidences=evidences,
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
    )
    price_invoker = _provenanced_price_invoker(
        purchase, context, observed=observe_price,
        reference_case_id=reference_case_id,
    )
    tco_invoker = _provenanced_tco_invoker(
        purchase, observed=observe_tco, reference_case_id=reference_case_id,
    )
    supplier_invoker = _provenanced_supplier_risk_invoker(
        purchase, context, observed=observe_supplier_risk,
        reference_case_id=reference_case_id,
    )
    twin_alternatives = _twin_alternatives(inputs)
    if observe_twin:
        twin_invoker = build_reference_observed_decision_twin_invoker(
            purchase=purchase, preparation=preparation,
            alternatives=twin_alternatives, reference_case_id=reference_case_id,
        )
    else:
        twin_invoker = build_provenanced_decision_twin_invoker(
            preparation=preparation, alternatives=twin_alternatives,
        )
    execution = run_reference_operational_simulation(
        provenance=provenance, bundle=bundle, receipt=receipt,
        consumption=consumption, purchase=purchase, context=context,
        policy_version=f"REF-BUSINESS-001-{variant}-v1",
        price_invoker=price_invoker,
        tco_invoker=tco_invoker,
        supplier_risk_value_invoker=supplier_invoker,
        rules_invoker=c0_invoker,
        decision_twin_invoker=twin_invoker,
        scenario_coordination_invoker=(
            build_provenanced_scenario_coordination_invoker(
                preparation=preparation, inputs=inputs,
            )
        ),
        negotiation_intelligence_invoker=ni_invoker,
        negotiation_ladder_invoker=ladder_invoker,
    )
    observations = {}
    if observe_price:
        observations["price"] = _close_reference_price_observation(
            execution=execution, price_invoker=price_invoker,
        )
    if observe_tco:
        observations["tco"] = _close_reference_tco_observation(
            execution=execution, tco_invoker=tco_invoker,
        )
    if observe_supplier_risk:
        observations["supplier_risk"] = _close_reference_supplier_risk_observation(
            execution=execution, supplier_invoker=supplier_invoker,
        )
    if observe_c0:
        observations["c0"] = _close_reference_c0_observation(
            execution=execution, c0_invoker=c0_invoker,
        )
    if observe_twin:
        observations["decision_twin"] = _close_reference_decision_twin_observation(
            execution=execution, twin_invoker=twin_invoker,
        )
    if return_observation_map:
        return execution, observations
    if observations:
        return (execution, *(observations[key] for key in observations))
    return execution


def execute_reference_business_case(*, variant: str):
    """Run the existing full synthetic reference sequence."""
    return _execute_reference_business_case(variant=variant, observe_price=False)


def execute_reference_business_case_with_price_observation(*, variant: str):
    """Return terminal and same-run synthetic PRICE observation."""
    return _execute_reference_business_case(variant=variant, observe_price=True)


def execute_reference_business_case_with_tco_observation(*, variant: str):
    """Return terminal and same-run synthetic TCO observation."""
    return _execute_reference_business_case(
        variant=variant, observe_price=False, observe_tco=True,
    )


def execute_reference_business_case_with_analytical_observations(*, variant: str):
    """Return terminal and both captures from a single reference run."""
    return _execute_reference_business_case(
        variant=variant, observe_price=True, observe_tco=True,
    )


def execute_reference_business_case_with_supplier_risk_observation(*, variant: str):
    """Return terminal and same-run synthetic external supplier assessment."""
    return _execute_reference_business_case(
        variant=variant, observe_price=False, observe_supplier_risk=True,
    )


def execute_reference_business_case_with_selected_observations(
    *, variant: str, with_price: bool = False, with_tco: bool = False,
    with_supplier_risk: bool = False, with_c0: bool = False,
    with_decision_twin: bool = False,
):
    """Run once and return a keyed map of requested same-call captures."""
    return _execute_reference_business_case(
        variant=variant, observe_price=with_price, observe_tco=with_tco,
        observe_supplier_risk=with_supplier_risk, observe_c0=with_c0,
        observe_twin=with_decision_twin,
        return_observation_map=True,
    )


def execute_reference_business_case_with_decision_twin_observation(*, variant: str):
    """Return terminal and same-call descriptive Twin comparison."""
    return _execute_reference_business_case(
        variant=variant, observe_price=False, observe_twin=True,
    )


def execute_reference_business_case_with_c0_observation(*, variant: str):
    """Return terminal and same-call synthetic C0/CRC composition."""
    return _execute_reference_business_case(
        variant=variant, observe_price=False, observe_c0=True,
    )


def main() -> None:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("negative", "qtg-eligible"),
                        required=True)
    parser.add_argument("--output", type=Path,
                        help="Write the complete terminal JSON artifact here")
    args = parser.parse_args()
    execution = execute_reference_business_case(variant=args.variant)
    payload = execution.to_payload()
    if args.output is not None:
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "reference_case_id": payload["reference_case_id"],
        "qtg_status": payload["qtg_quality_result"]["status"],
        "qtg_confidence": payload["qtg_quality_result"]["confidence"],
        "capability_sequence": payload["capability_sequence"],
        "execution_status": payload["execution_outcome"]["status"],
        "operational_path": payload["operational_path"],
        "operational_effect": payload["operational_effect"],
        "decision_authority": payload["decision_authority"],
        "terminal_fingerprint": payload["terminal_fingerprint"],
    }, ensure_ascii=False, sort_keys=True))
    print(
        "Interpretación: execution_status="
        f"{payload['execution_outcome']['status']} indica el estado de la "
        "simulación técnica; no es una aprobación. "
        f"QTG={payload['qtg_quality_result']['status']} describe la calidad "
        "funcional del caso sintético. La ruta operacional permanece prohibida "
        "y no se concede autoridad decisional.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
