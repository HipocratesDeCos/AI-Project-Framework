"""Declared synthetic inputs for Reference Business Case 002; never operational.

These functions assemble fixed fictitious material through existing EIOS producers.
They do not validate real supplier facts or grant decision authority.
"""
from __future__ import annotations

from datetime import timedelta, datetime, timezone
from decimal import Decimal
from pathlib import Path
from eios.core.c0_reproducibility import build_trace
from eios.core.models import (
    DecisionContext,
    PurchaseOperation,
    EvidenceValidation,
    Evidence,
)
from eios.core.negotiation_intelligence import NegotiationContent
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet,
    DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding,
    decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.rules import AssessmentTraceBinding
from eios.rules.catalog import authorized_rule
from eios.rules.data_quality import evaluate_r_dat_003
from eios.rules.negotiation_provenance import NegotiationContentEvidence
from eios.rules.scenario_integration import ProvenancedScenarioAnalyticsInput
from eios.supplier import (
    SupplierEvidenceInput,
    SupplierRiskDimensionAssessment,
    evaluate_supplier_evidence,
)

FIXTURE = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "reference_business_case_002_semantic"


def bundle_runtime():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    return (
        bundle,
        PurchaseOperation.model_validate(dip["purchase"]),
        DecisionContext.model_validate(dip["context"]),
    )


def price_sources():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    reference_ids = ("REF-PRICE-TX-002-A", "REF-PRICE-TX-002-B")
    evidence_ids = ("E-REF-PRICE-002-A", "E-REF-PRICE-002-B")
    references = tuple(
        PriceReference(
            source_transaction_id=reference_id,
            article_identity=purchase.article_id,
            supplier_identity=f"SUPPLIER-REFERENCE-002-{index}",
            quantity=quantity,
            unit="UNIT",
            unit_price=price,
            currency=purchase.currency,
            operation_date=purchase.operation_date - timedelta(days=days),
            evidence_refs=(evidence_id,),
        )
        for index, (reference_id, evidence_id, quantity, price, days) in enumerate(
            zip(reference_ids, evidence_ids, (Decimal("10"), Decimal("14")),
                (Decimal("20.00"), Decimal("22.00")), (9, 4)), start=1
        )
    )
    payload = PriceIntelligenceInput(
        decision_context=context,
        purchase_operation=purchase,
        references=references,
        evidence_validations=tuple(
            EvidenceValidation(
                evidence_id=evidence_id, status="VALID",
                reason="Declared synthetic price reference for product test",
            ) for evidence_id in evidence_ids
        ),
        methodology_version="REF-BUSINESS-002-PRICE-v1",
    )
    assessment = PriceIntelligenceAssessmentContext(
        temporal={reference_id: (
            "ELIGIBLE", f"trace:reference:business:002:price:temporal:{reference_id}"
        ) for reference_id in reference_ids},
        representativeness={
            reference_id: RepresentativenessObservation(
                ordinary_market_context=True,
                exceptional_condition=False,
                material_commercial_distortion=False,
                contradiction_material_unresolved=False,
                evidence_refs=(evidence_id,),
                rule_reference="REF-BUSINESS-002-REPRESENTATIVENESS-v1",
                trace_reference=f"trace:reference:business:002:price:{reference_id}",
            ) for reference_id, evidence_id in zip(reference_ids, evidence_ids)
        },
        sufficiency=SufficiencyObservation(
            evidence_sufficient=True, contradictions_resolved=True,
            evidence_refs=evidence_ids,
            rule_reference="REF-BUSINESS-002-PRICE-SUFFICIENCY-v1",
            trace_reference="trace:reference:business:002:price:sufficiency",
            selected_reference_ids=reference_ids,
        ),
    )
    return bundle, purchase, context, payload, assessment


def supplier_sources():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    supplier = evaluate_supplier_evidence(SupplierEvidenceInput(
        context=context, purchase_operation=purchase,
        company_scope="COMPANY-MOCK-002", evaluation_date=purchase.operation_date,
    ))
    authority = "authority:synthetic:ref-business-002:supplier:risk"
    risk = SupplierRiskDimensionAssessment(
        supplier_id=purchase.supplier_id, dimension="RELIABILITY",
        state="NOT_DETERMINABLE", authority_ref=authority,
        methodology_ref="method:synthetic:ref-business-002:supplier:risk:v1",
        assessment_ref="assessment:synthetic:ref-business-002:supplier:risk:unknown",
        evidence_refs=("E-REF-002-SRV-UNKNOWN",),
        trace_refs=("trace:synthetic:ref-business-002:supplier:risk:unknown",),
    )
    evidences = (
        Evidence(
            evidence_id="E-REF-002-SRV-AUTH", source_type="supplier-risk",
            source_ref="reference:business:002:supplier:risk:authority",
            captured_at=purchase.operation_date, state="DEMONSTRATED",
            demonstration_ref=authority,
        ),
        Evidence(
            evidence_id="E-REF-002-SRV-UNKNOWN", source_type="supplier-risk",
            source_ref="reference:business:002:supplier:risk:unknown",
            captured_at=purchase.operation_date, state="DEMONSTRATED",
            demonstration_ref=risk.assessment_ref,
        ),
    )
    return bundle, purchase, context, supplier, risk, evidences


def c0_sources():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    authority = "AUTH-REF-BUSINESS-002-DATA"
    methodology = "METHOD-REF-BUSINESS-002-DATA"
    requirement_set = DecisionEvidenceRequirementSet(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        company_scope="COMPANY-MOCK-002",
        purchase_operation_ref=decision_evidence_purchase_ref(purchase),
        effective_date=purchase.operation_date,
        requirement_set_id="REQSET-REF-BUSINESS-002",
        requirement_set_version="1.0",
        requirement_ids=("REQ-PROJECTION-QUALITY",),
        authority_ref=authority, methodology_ref=methodology,
        trace_refs=("trace:reference:business:002:requirements",),
    )
    binding = RequirementEvidenceBinding(
        requirement_id="REQ-PROJECTION-QUALITY", classification="UNDETERMINED",
        authority_ref=authority,
        trace_refs=("trace:reference:business:002:requirement:qtg:undetermined",),
    )
    observation = DecisionEvidenceSufficiencyProducer(
        authority_ref=authority, methodology_ref=methodology,
    ).produce(
        purchase=purchase, context=context, company_scope="COMPANY-MOCK-002",
        state="AVAILABLE", requirement_set=requirement_set, bindings=(binding,),
        source_ref="reference:business:002:data-sufficiency",
        trace_refs=("trace:reference:business:002:data-sufficiency",),
    )
    sufficiency_evidence = Evidence(
        evidence_id="E-REF-002-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref="reference:business:002:data-sufficiency:evidence",
        captured_at=purchase.operation_date, state="DEMONSTRATED",
        demonstration_ref=decision_evidence_sufficiency_ref(observation),
    )
    rule = authorized_rule("R-DAT-003", context.rules_version)
    assessment = evaluate_r_dat_003(
        purchase=purchase, context=context, rule=rule,
        observation=observation, sufficiency_evidence=sufficiency_evidence,
    )
    trace = build_trace(
        context, purchase, rule, tuple(assessment.evidence_ids), assessment,
    ).model_copy(update={
        "created_at": datetime.combine(
            purchase.operation_date, datetime.min.time(), tzinfo=timezone.utc,
        ),
    })
    return bundle, purchase, context, observation, assessment, trace


def _child_binding(purchase, context):
    authority = "AUTH-REF-BUSINESS-002-DATA"
    requirement_set = DecisionEvidenceRequirementSet(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        company_scope="COMPANY-MOCK-002",
        purchase_operation_ref=decision_evidence_purchase_ref(purchase),
        effective_date=purchase.operation_date,
        requirement_set_id=f"REQSET-REF-BUSINESS-002-{context.scenario_id}",
        requirement_set_version="1.0",
        requirement_ids=("REQ-PROJECTION-QUALITY",),
        authority_ref=authority,
        methodology_ref="METHOD-REF-BUSINESS-002-DATA",
        trace_refs=(f"trace:reference:business:002:{context.scenario_id}:requirements",),
    )
    observation = DecisionEvidenceSufficiencyProducer(
        authority_ref=authority, methodology_ref="METHOD-REF-BUSINESS-002-DATA",
    ).produce(
        purchase=purchase, context=context, company_scope="COMPANY-MOCK-002",
        state="AVAILABLE", requirement_set=requirement_set,
        bindings=(RequirementEvidenceBinding(
            requirement_id="REQ-PROJECTION-QUALITY", classification="UNDETERMINED",
            authority_ref=authority,
            trace_refs=(f"trace:reference:business:002:{context.scenario_id}:undetermined",),
        ),),
        source_ref=f"reference:business:002:{context.scenario_id}:data-sufficiency",
    )
    evidence = Evidence(
        evidence_id=f"E-REF-002-{context.scenario_id}-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref=f"reference:business:002:{context.scenario_id}:sufficiency:evidence",
        captured_at=purchase.operation_date, state="DEMONSTRATED",
        demonstration_ref=decision_evidence_sufficiency_ref(observation),
    )
    rule = authorized_rule("R-DAT-003", context.rules_version)
    assessment = evaluate_r_dat_003(
        purchase=purchase, context=context, rule=rule,
        observation=observation, sufficiency_evidence=evidence,
    )
    trace = build_trace(
        context, purchase, rule, tuple(assessment.evidence_ids), assessment,
    ).model_copy(update={
        "created_at": datetime.combine(
            purchase.operation_date, datetime.min.time(), tzinfo=timezone.utc,
        ),
    })
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


def scenario_material():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    preparation = prepare_o4_o2_o3_orchestration(
        context=context,
        variables=(GenerationVariable(
            variable_id="quantity_delta", value_type="integer", base_value=0,
            domain=(1, 2),
        ),),
        policy=GenerationPolicy(policy_version="REF-BUSINESS-002-SCENARIOS-v1"),
    )
    valid = tuple(s for s in preparation.materialization.scenarios
                  if s.status.value == "VALID")
    assert len(valid) == 2
    inputs = []
    for scenario, delta in zip(valid, (1, 2)):
        child_purchase = purchase.model_copy(update={
            "scenario_id": scenario.scenario_id,
            "quantity": purchase.quantity + Decimal(delta),
        }, deep=True)
        child_context = context.model_copy(
            update={"scenario_id": scenario.scenario_id}, deep=True,
        )
        inputs.append(ProvenancedScenarioAnalyticsInput(
            scenario_id=scenario.scenario_id, purchase=child_purchase,
            assessment_bindings=(_child_binding(child_purchase, child_context),),
        ))
    return bundle, purchase, context, preparation, tuple(inputs)


def negotiation_material():
    bundle, purchase, context, observation, assessment, trace = c0_sources()
    assert observation.undetermined_requirement_ids == ("REQ-PROJECTION-QUALITY",)
    authority = "authority:synthetic:ref-business-002:negotiation:information-request"
    evidence = Evidence(
        evidence_id="E-REF-002-NI-AUTH",
        source_type="synthetic-negotiation-authority",
        source_ref="reference:business:002:negotiation:information-request",
        captured_at=purchase.operation_date, state="DEMONSTRATED",
        demonstration_ref=authority,
    )
    content = NegotiationContentEvidence(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        authority_ref=authority, authority_state="AUTHORIZED",
        negotiation_content=NegotiationContent(
            objective="Request missing supporting information in this synthetic case",
            opening_request="Ask for documented supplier reliability information",
            fallback="Pause the simulated discussion pending human review",
        ),
        evidence_refs=(evidence.evidence_id,), trace_refs=(trace.trace_id,),
    )
    bindings = (AssessmentTraceBinding(assessment=assessment, trace=trace),)
    return bundle, purchase, context, content, (evidence,), bindings
