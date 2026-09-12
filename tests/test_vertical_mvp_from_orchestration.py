from copy import deepcopy
from datetime import date
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.orchestration import O1ExecutionStatus
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.vertical_orchestration import run_vertical_mvp_from_orchestration


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-VERTICAL-ORCH",
        scenario_id="BASE",
        rules_version="R-VERTICAL-1",
        parameters_version="P-VERTICAL-1",
        data_snapshot_id="SNAP-VERTICAL-1",
    )


def _purchase(**changes) -> PurchaseOperation:
    data = dict(
        decision_id="D-VERTICAL-ORCH",
        scenario_id="BASE",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )
    data.update(changes)
    return PurchaseOperation(**data)


def _policy() -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-VERTICAL-1")


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


def _orchestration(domain=(1,), analytics_factory=_analytics):
    preparation = prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(_variable(domain),),
        policy=_policy(),
    )
    analytics = tuple(
        analytics_factory(scenario.scenario_id)
        for scenario in preparation.materialization.scenarios
        if scenario.status.value == "VALID"
    )
    return complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=analytics,
    )


def test_completed_orchestration_becomes_single_vertical_scenario_capability():
    orchestration = _orchestration()

    result = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=orchestration,
        policy_version="MVP-ORCH-1",
    )

    assert result.status is BoundaryStatus.COMPLETED
    assert result.rules is None
    assert result.scenario_support is not None
    assert tuple(item.capability for item in result.capability_results) == (
        "SCENARIO_COORDINATION",
    )
    capability = result.capability_results[0]
    assert capability.status is O1ExecutionStatus.COMPLETED
    assert capability.result_available is True


def test_context_versions_and_snapshot_come_from_orchestration():
    result = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=_orchestration(),
        policy_version="MVP-ORCH-1",
    )
    context = result.scenario_support.execution_context

    assert context.decision_id == "D-VERTICAL-ORCH"
    assert context.rules_version == "R-VERTICAL-1"
    assert context.parameters_version == "P-VERTICAL-1"
    assert context.data_snapshot_id == "SNAP-VERTICAL-1"


def test_scenario_support_preserves_orchestrated_analytics():
    orchestration = _orchestration(domain=(2, 1))
    result = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=orchestration,
        policy_version="MVP-ORCH-1",
    )

    assert len(result.scenario_support.scenarios) == 2
    ids = tuple(item.scenario_id for item in result.scenario_support.scenarios)
    assert ids == tuple(sorted(ids))
    for scenario in result.scenario_support.scenarios:
        assert scenario.values["assessments"] == ({"assessment": scenario.scenario_id},)
        assert scenario.values["viability_result"] == {"viability": scenario.scenario_id}


def test_not_evaluable_remains_not_evaluable_without_business_falsehood():
    def not_evaluable(scenario_id: str) -> AuthorizedScenarioAnalytics:
        return _analytics(
            scenario_id,
            status=ScenarioEvaluationStatus.NOT_EVALUABLE,
            limitations=("missing-evidence",),
        )

    result = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=_orchestration(analytics_factory=not_evaluable),
        policy_version="MVP-ORCH-1",
    )

    capability = result.capability_results[0]
    assert capability.status is O1ExecutionStatus.NOT_EVALUABLE
    assert capability.result_available is False
    assert result.scenario_support.scenarios[0].status.value == "NOT_EVALUABLE"
    assert not hasattr(result, "viable")
    assert not hasattr(result, "rejection")


def test_failed_remains_technical_failed_not_business_rejection():
    def failed(scenario_id: str) -> AuthorizedScenarioAnalytics:
        return _analytics(
            scenario_id,
            status=ScenarioEvaluationStatus.FAILED,
            failure_reason="technical failure",
        )

    result = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=_orchestration(analytics_factory=failed),
        policy_version="MVP-ORCH-1",
    )

    capability = result.capability_results[0]
    assert capability.status is O1ExecutionStatus.FAILED
    assert capability.failure_reason is not None
    assert result.scenario_support.scenarios[0].failure_reason == "technical failure"
    assert not hasattr(result, "rejection")
    assert not hasattr(result.scenario_support, "decision")


def test_foreign_purchase_identity_fails_closed():
    orchestration = _orchestration()

    with pytest.raises(ValueError, match="decision_id"):
        run_vertical_mvp_from_orchestration(
            purchase=_purchase(decision_id="OTHER"),
            orchestration_result=orchestration,
            policy_version="MVP-ORCH-1",
        )

    with pytest.raises(ValueError, match="scenario_id"):
        run_vertical_mvp_from_orchestration(
            purchase=_purchase(scenario_id="OTHER"),
            orchestration_result=orchestration,
            policy_version="MVP-ORCH-1",
        )


def test_draft_only_and_empty_generation_fail_closed():
    draft_preparation = prepare_o4_o2_o3_orchestration(
        context=_context(), variables=(), policy=_policy()
    )
    draft_result = complete_o4_o2_o3_orchestration(
        preparation=draft_preparation, analytics=()
    )
    with pytest.raises(ValueError, match="al menos una evaluación O3"):
        run_vertical_mvp_from_orchestration(
            purchase=_purchase(),
            orchestration_result=draft_result,
            policy_version="MVP-ORCH-1",
        )

    empty_preparation = prepare_o4_o2_o3_orchestration(
        context=_context(), variables=(_variable(domain=()),), policy=_policy()
    )
    empty_result = complete_o4_o2_o3_orchestration(
        preparation=empty_preparation, analytics=()
    )
    with pytest.raises(ValueError, match="al menos una evaluación O3"):
        run_vertical_mvp_from_orchestration(
            purchase=_purchase(),
            orchestration_result=empty_result,
            policy_version="MVP-ORCH-1",
        )


def test_public_signature_has_no_detached_context_or_scenario_payload():
    parameters = signature(run_vertical_mvp_from_orchestration).parameters

    assert tuple(parameters) == (
        "purchase",
        "orchestration_result",
        "policy_version",
    )
    assert "context" not in parameters
    assert "scenario_evaluation_results" not in parameters
    assert "scenario_support" not in parameters


def test_inputs_are_immutable_and_output_has_no_decision_authority():
    purchase = _purchase()
    orchestration = _orchestration()
    purchase_before = purchase.model_copy(deep=True)
    orchestration_before = deepcopy(orchestration)

    first = run_vertical_mvp_from_orchestration(
        purchase=purchase,
        orchestration_result=orchestration,
        policy_version="MVP-ORCH-1",
    )
    second = run_vertical_mvp_from_orchestration(
        purchase=purchase,
        orchestration_result=orchestration,
        policy_version="MVP-ORCH-1",
    )

    assert purchase == purchase_before
    assert orchestration == orchestration_before
    assert first.scenario_support == second.scenario_support
    forbidden = {
        "score",
        "ranking",
        "recommendation",
        "approval",
        "rejection",
        "best_scenario",
        "selected_scenario",
        "decision",
    }
    assert forbidden.isdisjoint(first.model_fields)
    assert forbidden.isdisjoint(first.scenario_support.model_fields)
