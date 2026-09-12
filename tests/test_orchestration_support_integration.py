from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o2 import O2ScenarioStatus
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    _complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.orchestration import O1ExecutionStatus
from eios.core.orchestration_support_integration import build_o2_support_from_orchestration
from eios.core.scenario_coordination_adapter import adapt_scenario_coordination
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable


def _context(**changes) -> DecisionContext:
    data = dict(
        decision_id="D-ORCH-SUPPORT",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="S1",
    )
    data.update(changes)
    return DecisionContext(**data)


def _purchase(**changes) -> PurchaseOperation:
    data = dict(
        decision_id="D-ORCH-SUPPORT",
        scenario_id="BASE",
        article_id="A1",
        supplier_id="SUP1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )
    data.update(changes)
    return PurchaseOperation(**data)


def _policy() -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-SUPPORT-1")


def _variable(domain=(1,)) -> GenerationVariable:
    return GenerationVariable(
        variable_id="qty",
        value_type="integer",
        base_value=0,
        domain=domain,
    )


def _analytics(scenario_id: str, **changes) -> AuthorizedScenarioAnalytics:
    data = dict(
        scenario_id=scenario_id,
        assessments=({"assessment": scenario_id},),
        viability_result={"viability": scenario_id},
        trace_references=(f"TRACE-{scenario_id}",),
    )
    data.update(changes)
    return AuthorizedScenarioAnalytics(**data)


def _completed_orchestration(domain=(1,), analytics_factory=_analytics):
    prepared = prepare_o4_o2_o3_orchestration(
        context=_context(), variables=(_variable(domain),), policy=_policy()
    )
    packets = tuple(
        analytics_factory(scenario.scenario_id)
        for scenario in prepared.materialization.scenarios
        if scenario.status.value == "VALID"
    )
    return _complete_o4_o2_o3_orchestration(
        preparation=prepared,
        analytics=packets,
    )


def test_builds_o2_support_from_completed_orchestration():
    orchestration_result = _completed_orchestration()
    scenario_id = orchestration_result.evaluations[0].scenario_id

    support = build_o2_support_from_orchestration(
        purchase_operation=_purchase(),
        orchestration_result=orchestration_result,
    )

    assert support.execution_context.decision_id == "D-ORCH-SUPPORT"
    assert support.execution_context.rules_version == "R1"
    assert support.execution_context.parameters_version == "P1"
    assert support.execution_context.data_snapshot_id == "S1"
    assert len(support.scenarios) == 1
    assert support.scenarios[0].scenario_id == scenario_id
    assert support.scenarios[0].status is O2ScenarioStatus.COMPLETED
    assert support.scenarios[0].values["assessments"] == ({"assessment": scenario_id},)
    assert support.scenarios[0].values["viability_result"] == {"viability": scenario_id}


def test_multiple_scenarios_are_deterministic_and_comparable():
    orchestration_result = _completed_orchestration(domain=(2, 1))

    first = build_o2_support_from_orchestration(
        purchase_operation=_purchase(), orchestration_result=orchestration_result
    )
    second = build_o2_support_from_orchestration(
        purchase_operation=_purchase(), orchestration_result=orchestration_result
    )

    assert first == second
    assert first.comparison is not None
    ids = tuple(item.scenario_id for item in first.scenarios)
    assert ids == tuple(sorted(ids))
    assert first.comparison.scenario_ids == ids


def test_partial_state_traces_and_limitations_are_preserved():
    def partial(scenario_id: str) -> AuthorizedScenarioAnalytics:
        return _analytics(
            scenario_id,
            status=ScenarioEvaluationStatus.PARTIALLY_COMPLETED,
            limitations=("missing-evidence",),
            trace_references=("TRACE-B", "TRACE-A"),
        )

    orchestration_result = _completed_orchestration(analytics_factory=partial)
    support = build_o2_support_from_orchestration(
        purchase_operation=_purchase(), orchestration_result=orchestration_result
    )
    scenario = support.scenarios[0]

    assert scenario.status is O2ScenarioStatus.PARTIALLY_COMPLETED
    assert scenario.unresolved_items == ("missing-evidence",)
    assert scenario.trace_references == ("TRACE-B", "TRACE-A")


def test_failed_state_and_reason_are_preserved_without_business_rejection():
    def failed(scenario_id: str) -> AuthorizedScenarioAnalytics:
        return _analytics(
            scenario_id,
            status=ScenarioEvaluationStatus.FAILED,
            failure_reason="technical failure",
        )

    orchestration_result = _completed_orchestration(analytics_factory=failed)
    support = build_o2_support_from_orchestration(
        purchase_operation=_purchase(), orchestration_result=orchestration_result
    )
    scenario = support.scenarios[0]

    assert scenario.status is O2ScenarioStatus.FAILED
    assert scenario.failure_reason == "technical failure"
    assert not hasattr(scenario, "rejection")
    assert not hasattr(support, "decision")


def test_foreign_purchase_decision_is_rejected():
    orchestration_result = _completed_orchestration()

    with pytest.raises(ValueError, match="decision_id"):
        build_o2_support_from_orchestration(
            purchase_operation=_purchase(decision_id="OTHER"),
            orchestration_result=orchestration_result,
        )


def test_foreign_purchase_base_scenario_is_rejected():
    orchestration_result = _completed_orchestration()

    with pytest.raises(ValueError, match="scenario_id"):
        build_o2_support_from_orchestration(
            purchase_operation=_purchase(scenario_id="OTHER"),
            orchestration_result=orchestration_result,
        )


def test_draft_only_orchestration_fails_closed_without_fabricated_o2_state():
    prepared = prepare_o4_o2_o3_orchestration(
        context=_context(), variables=(), policy=_policy()
    )
    orchestration_result = _complete_o4_o2_o3_orchestration(
        preparation=prepared, analytics=()
    )

    with pytest.raises(ValueError, match="al menos una evaluación O3"):
        build_o2_support_from_orchestration(
            purchase_operation=_purchase(), orchestration_result=orchestration_result
        )


def test_empty_generation_fails_closed_without_fabricated_o2_state():
    prepared = prepare_o4_o2_o3_orchestration(
        context=_context(), variables=(_variable(domain=()),), policy=_policy()
    )
    orchestration_result = _complete_o4_o2_o3_orchestration(
        preparation=prepared, analytics=()
    )

    with pytest.raises(ValueError, match="al menos una evaluación O3"):
        build_o2_support_from_orchestration(
            purchase_operation=_purchase(), orchestration_result=orchestration_result
        )


def test_not_started_keeps_existing_o3_to_o2_fail_closed_rule():
    def not_started(scenario_id: str) -> AuthorizedScenarioAnalytics:
        return _analytics(
            scenario_id,
            status=ScenarioEvaluationStatus.NOT_STARTED,
        )

    orchestration_result = _completed_orchestration(analytics_factory=not_started)

    with pytest.raises(ValueError, match="no tiene equivalencia O2 literal"):
        build_o2_support_from_orchestration(
            purchase_operation=_purchase(), orchestration_result=orchestration_result
        )


def test_inputs_are_not_mutated():
    purchase = _purchase()
    orchestration_result = _completed_orchestration()
    purchase_before = purchase.model_copy(deep=True)
    orchestration_before = deepcopy(orchestration_result)

    build_o2_support_from_orchestration(
        purchase_operation=purchase,
        orchestration_result=orchestration_result,
    )

    assert purchase == purchase_before
    assert orchestration_result == orchestration_before


def test_output_is_directly_compatible_with_existing_scenario_coordination_adapter():
    orchestration_result = _completed_orchestration()
    support = build_o2_support_from_orchestration(
        purchase_operation=_purchase(), orchestration_result=orchestration_result
    )

    capability = adapt_scenario_coordination(support)

    assert capability.capability == "SCENARIO_COORDINATION"
    assert capability.status is O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
    assert not hasattr(capability, "ranking")
    assert not hasattr(capability, "recommendation")
