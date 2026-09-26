"""Two company 002 children each carry their own C0 purchase and trace."""
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet, DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding, decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.rules import AssessmentTraceBinding
from eios.rules.catalog import authorized_rule
from eios.rules.data_quality import evaluate_r_dat_003
from eios.rules.scenario_integration import (
    ProvenancedScenarioAnalyticsInput,
    build_reference_observed_scenario_coordination_invoker,
)
from eios.rules.decision_twin_integration import (
    ProvenancedDecisionTwinAlternativeInput,
    build_reference_observed_decision_twin_invoker,
)

FIXTURE = Path(__file__).parent / "fixtures" / "reference_business_case_002_semantic"


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


def test_second_company_child_trace_payloads_are_reproducible():
    first = _material()[4]
    second = _material()[4]
    assert tuple(item.model_dump(mode="json") for item in first) == tuple(
        item.model_dump(mode="json") for item in second
    )


def _material():
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


def test_second_company_scenario_coordination_uses_distinct_child_c0():
    bundle, purchase, context, preparation, inputs = _material()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert tuple(item.purchase.quantity for item in inputs) == (
        Decimal("16"), Decimal("17"),
    )
    child_traces = tuple(item.assessment_bindings[0].trace.trace_id for item in inputs)
    assert len(set(child_traces)) == 2
    assert all(item.purchase.scenario_id != purchase.scenario_id for item in inputs)
    invoker = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation, inputs=inputs,
        reference_case_id="REF-BUSINESS-002",
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capability.capability == "SCENARIO_COORDINATION"
    assert len(capture.result.scenarios) == 2
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_twin_compares_children_without_selection():
    _, purchase, context, preparation, inputs = _material()
    alternatives = tuple(ProvenancedDecisionTwinAlternativeInput(
        representation_ref=f"REF-BUSINESS-002-ALT-{index}", scenario_input=item,
    ) for index, item in enumerate(inputs, start=1))
    invoker = build_reference_observed_decision_twin_invoker(
        purchase=purchase, preparation=preparation, alternatives=alternatives,
        reference_case_id="REF-BUSINESS-002",
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capability.capability == "DECISION_TWIN"
    assert capture.result.alternatives == (
        "REF-BUSINESS-002-ALT-1", "REF-BUSINESS-002-ALT-2",
    )
    assert "selected_alternative" not in type(capture.result).model_fields


def test_second_company_scenarios_reject_reused_sibling_trace():
    _, purchase, context, preparation, inputs = _material()
    broken = inputs[1].model_copy(update={
        "assessment_bindings": (inputs[1].assessment_bindings[0].model_copy(
            update={"trace": inputs[0].assessment_bindings[0].trace}
        ),),
    })
    invoker = build_reference_observed_scenario_coordination_invoker(
        purchase=purchase, preparation=preparation, inputs=(inputs[0], broken),
        reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="Trace.scenario_id"):
        invoker(purchase, context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
