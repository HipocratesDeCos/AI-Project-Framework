from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

import eios.rules.scenario_integration as scenario_integration
from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.orchestration import O1ExecutionStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedScenarioAnalyticsInput,
    build_provenanced_scenario_coordination_invoker,
)
from eios.rules.catalog import authorized_rule


RULES_VERSION = "rules-v1"


def _context():
    return DecisionContext(
        decision_id="D-SC-PROV",
        scenario_id="BASE",
        rules_version=RULES_VERSION,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="D-SC-PROV",
        scenario_id="BASE",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 23),
    )


def _preparation():
    return prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1, 2),
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-SC-PROV-1"),
    )


def _binding(scenario_id: str, *, outcome: str, quantity: Decimal):
    context = _context().model_copy(update={"scenario_id": scenario_id})
    purchase = _purchase().model_copy(
        update={"scenario_id": scenario_id, "quantity": quantity}
    )
    assessment = Assessment(
        rule_id="R-DAT-003",
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=[f"EV-{scenario_id}"],
        reason=f"R-DAT-003 {scenario_id}",
    )
    rule = authorized_rule("R-DAT-003", RULES_VERSION)
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


def _inputs(preparation):
    scenario_ids = tuple(
        item.scenario_id
        for item in preparation.materialization.scenarios
        if item.status.value == "VALID"
    )
    assert len(scenario_ids) == 2
    return (
        ProvenancedScenarioAnalyticsInput(
            scenario_id=scenario_ids[0],
            purchase=_purchase().model_copy(
                update={"scenario_id": scenario_ids[0], "quantity": Decimal("11")}
            ),
            assessment_bindings=(
                _binding(scenario_ids[0], outcome="FALSE", quantity=Decimal("11")),
            ),
        ),
        ProvenancedScenarioAnalyticsInput(
            scenario_id=scenario_ids[1],
            purchase=_purchase().model_copy(
                update={"scenario_id": scenario_ids[1], "quantity": Decimal("12")}
            ),
            assessment_bindings=(
                _binding(scenario_ids[1], outcome="TRUE", quantity=Decimal("12")),
            ),
        ),
    )


def test_provenanced_scenario_coordination_rebuilds_stage2_at_runtime():
    preparation = _preparation()
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation,
        inputs=_inputs(preparation),
    )

    capability = invoker(_purchase(), _context())

    assert capability.capability == "SCENARIO_COORDINATION"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
    assert len(capability.trace_references) == 2
    assert capability.unresolved_items == ()


def test_provenanced_scenario_coordination_is_mvp_compatible():
    preparation = _preparation()
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation,
        inputs=_inputs(preparation),
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-SC-PROV-1",
        scenario_coordination_invoker=invoker,
    )

    assert outcome.status.value == "COMPLETED"
    assert len(outcome.capability_results) == 1
    capability = outcome.capability_results[0]
    assert capability.capability == "SCENARIO_COORDINATION"
    assert capability.status == O1ExecutionStatus.COMPLETED


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "D-OTHER"),
        ("scenario_id", "S-OTHER"),
        ("rules_version", "rules-other"),
        ("parameters_version", "params-other"),
        ("data_snapshot_id", "snapshot-other"),
    ),
)
def test_root_context_drift_fails_closed(field, value):
    preparation = _preparation()
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation,
        inputs=_inputs(preparation),
    )
    foreign = _context().model_copy(update={field: value})

    with pytest.raises(ValueError, match=field):
        invoker(_purchase(), foreign)


def test_tampered_stage2_trace_fails_closed_at_invocation():
    preparation = _preparation()
    inputs = list(_inputs(preparation))
    first = inputs[0]
    binding = first.assessment_bindings[0]
    bad_binding = AssessmentTraceBinding(
        assessment=binding.assessment,
        trace=binding.trace.model_copy(update={"trace_id": "tampered"}),
    )
    inputs[0] = first.model_copy(
        update={"assessment_bindings": (bad_binding,)},
        deep=True,
    )
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation,
        inputs=tuple(inputs),
    )

    with pytest.raises(ValueError, match="trace_id no es reproducible"):
        invoker(_purchase(), _context())


def test_invoker_freezes_provenanced_sources_against_later_mutation():
    preparation = _preparation()
    inputs = _inputs(preparation)
    invoker = build_provenanced_scenario_coordination_invoker(
        preparation=preparation,
        inputs=inputs,
    )

    inputs[0].assessment_bindings[0].assessment.reason = "tampered later"
    capability = invoker(_purchase(), _context())

    assert capability.status == O1ExecutionStatus.COMPLETED


def test_builder_rejects_empty_and_duplicate_inputs():
    preparation = _preparation()
    with pytest.raises(ValueError, match="inputs no vacíos"):
        build_provenanced_scenario_coordination_invoker(
            preparation=preparation,
            inputs=(),
        )

    inputs = _inputs(preparation)
    duplicate = inputs[1].model_copy(
        update={"scenario_id": inputs[0].scenario_id},
        deep=True,
    )
    with pytest.raises(ValueError, match="scenario_id duplicado"):
        build_provenanced_scenario_coordination_invoker(
            preparation=preparation,
            inputs=(inputs[0], duplicate),
        )


def test_public_builder_accepts_sources_not_detached_orchestration_results():
    params = signature(
        build_provenanced_scenario_coordination_invoker
    ).parameters
    assert set(params) == {"preparation", "inputs"}
    assert "orchestration_result" not in params
    assert "scenario_support" not in params

    assert "build_provenanced_scenario_coordination_invoker" in (
        scenario_integration.__all__
    )
