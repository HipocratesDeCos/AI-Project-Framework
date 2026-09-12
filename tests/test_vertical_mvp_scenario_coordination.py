from datetime import date
from decimal import Decimal

import pytest

import eios.mvp as mvp
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import MVP_CAPABILITY_ORDER, run_mvp_execution
from eios.core.o2 import O2ScenarioResult, O2ScenarioStatus, build_support_package
from eios.core.scenario_coordination_adapter import adapt_scenario_coordination
from eios.core.scenario_evaluation import ScenarioEvaluationResult, ScenarioEvaluationStatus


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-SC-VERTICAL",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SNAP1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-SC-VERTICAL",
        scenario_id="BASE",
        article_id="A1",
        supplier_id="SUP1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _o2_package(*scenarios: O2ScenarioResult):
    return build_support_package(_purchase(), _context(), scenarios)


def _completed_o3(scenario_id: str) -> ScenarioEvaluationResult:
    return ScenarioEvaluationResult(
        scenario_id=scenario_id,
        decision_id="D-SC-VERTICAL",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SNAP1",
        status=ScenarioEvaluationStatus.COMPLETED,
        assessments=(f"assessment-{scenario_id}",),
        viability_result={"scenario": scenario_id, "status": "AVAILABLE"},
        trace_references=(f"trace-{scenario_id}",),
    )


def test_scenario_coordination_capability_is_canonically_between_twin_and_negotiation():
    assert MVP_CAPABILITY_ORDER.index("DECISION_TWIN") < MVP_CAPABILITY_ORDER.index(
        "SCENARIO_COORDINATION"
    )
    assert MVP_CAPABILITY_ORDER.index("SCENARIO_COORDINATION") < MVP_CAPABILITY_ORDER.index(
        "NEGOTIATION_INTELLIGENCE"
    )


def test_adapter_all_completed_is_completed_and_traceable():
    package = _o2_package(
        O2ScenarioResult(
            scenario_id="ALT-A",
            status=O2ScenarioStatus.COMPLETED,
            trace_references=("trace-b", "trace-a"),
        ),
        O2ScenarioResult(
            scenario_id="ALT-B",
            status=O2ScenarioStatus.COMPLETED,
            trace_references=("trace-a", "trace-c"),
        ),
    )

    capability = adapt_scenario_coordination(package)

    assert capability.capability == "SCENARIO_COORDINATION"
    assert capability.status.value == "COMPLETED"
    assert capability.result_available is True
    assert capability.trace_references == ("trace-a", "trace-b", "trace-c")
    assert capability.unresolved_items == ()


def test_adapter_preserves_homogeneous_not_evaluable_without_false_semantics():
    package = _o2_package(
        O2ScenarioResult(
            scenario_id="ALT-A",
            status=O2ScenarioStatus.NOT_EVALUABLE,
            unresolved_items=("missing-evidence",),
        ),
        O2ScenarioResult(
            scenario_id="ALT-B",
            status=O2ScenarioStatus.NOT_EVALUABLE,
        ),
    )

    capability = adapt_scenario_coordination(package)

    assert capability.status.value == "NOT_EVALUABLE"
    assert capability.result_available is False
    assert capability.unresolved_items == (
        "ALT-A:missing-evidence",
        "ALT-B:NOT_EVALUABLE",
    )


def test_adapter_mixed_nonfailed_states_become_partial_only():
    package = _o2_package(
        O2ScenarioResult(scenario_id="ALT-A", status=O2ScenarioStatus.COMPLETED),
        O2ScenarioResult(
            scenario_id="ALT-B",
            status=O2ScenarioStatus.PARTIALLY_COMPLETED,
            unresolved_items=("tco unavailable",),
        ),
    )

    capability = adapt_scenario_coordination(package)

    assert capability.status.value == "PARTIALLY_COMPLETED"
    assert capability.result_available is False
    assert capability.unresolved_items == ("ALT-B:tco unavailable",)


def test_adapter_failed_state_names_failed_scenarios_without_business_rejection():
    package = _o2_package(
        O2ScenarioResult(
            scenario_id="ALT-B",
            status=O2ScenarioStatus.FAILED,
            failure_reason="technical B",
        ),
        O2ScenarioResult(
            scenario_id="ALT-A",
            status=O2ScenarioStatus.FAILED,
            failure_reason="technical A",
        ),
    )

    capability = adapt_scenario_coordination(package)

    assert capability.status.value == "FAILED"
    assert capability.result_available is False
    assert capability.failure_reason == "FAILED scenarios: ALT-A, ALT-B"
    assert "rejection" not in capability.failure_reason.lower()


def test_execution_service_accepts_scenario_coordination_as_a_vertical_capability():
    package = _o2_package(
        O2ScenarioResult(scenario_id="ALT-A", status=O2ScenarioStatus.COMPLETED),
        O2ScenarioResult(scenario_id="ALT-B", status=O2ScenarioStatus.COMPLETED),
    )

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-SCENARIO-1",
        scenario_coordination_result=package,
    )

    assert outcome.status == BoundaryStatus.COMPLETED
    assert tuple(item.capability for item in outcome.capability_results) == (
        "SCENARIO_COORDINATION",
    )


def test_execution_service_rejects_scenario_package_from_foreign_context():
    foreign_context = _context().model_copy(update={"rules_version": "R2"})
    package = build_support_package(
        _purchase(),
        foreign_context,
        (O2ScenarioResult(scenario_id="ALT-A", status=O2ScenarioStatus.COMPLETED),),
    )

    with pytest.raises(ValueError, match="rules_version"):
        run_mvp_execution(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-SCENARIO-1",
            scenario_coordination_result=package,
        )


def test_vertical_facade_builds_o2_from_o3_and_preserves_full_support_package():
    a = _completed_o3("ALT-A")
    b = _completed_o3("ALT-B")

    result = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-SCENARIO-1",
        base_result="COMPRAR",
        scenario_evaluation_results=(b, a),
    )

    assert result.status == BoundaryStatus.COMPLETED
    assert result.rules is None
    assert result.scenario_support is not None
    assert tuple(item.scenario_id for item in result.scenario_support.scenarios) == (
        "ALT-A",
        "ALT-B",
    )
    assert tuple(item.capability for item in result.capability_results) == (
        "SCENARIO_COORDINATION",
    )
    assert result.scenario_support.scenarios[0].values["assessments"] == a.assessments
    assert result.scenario_support.scenarios[0].values["viability_result"] == a.viability_result


def test_vertical_scenario_support_is_order_independent():
    a = _completed_o3("ALT-A")
    b = _completed_o3("ALT-B")

    first = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-SCENARIO-1",
        base_result="COMPRAR",
        scenario_evaluation_results=(b, a),
    )
    second = mvp.run_vertical_mvp_support(
        purchase=_purchase(),
        context=_context(),
        policy_version="MVP-E2E-SCENARIO-1",
        base_result="COMPRAR",
        scenario_evaluation_results=(a, b),
    )

    assert first.scenario_support == second.scenario_support
    assert first.capability_results == second.capability_results


def test_not_started_o3_still_fails_closed_through_vertical_facade():
    not_started = ScenarioEvaluationResult(
        scenario_id="ALT-A",
        decision_id="D-SC-VERTICAL",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SNAP1",
        status=ScenarioEvaluationStatus.NOT_STARTED,
    )

    with pytest.raises(ValueError, match="no tiene equivalencia O2 literal"):
        mvp.run_vertical_mvp_support(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-SCENARIO-1",
            base_result="COMPRAR",
            scenario_evaluation_results=(not_started,),
        )


def test_absent_scenarios_do_not_create_synthetic_capability(monkeypatch):
    captured = {}

    def fake_run_mvp_execution(**kwargs):
        captured.update(kwargs)
        raise RuntimeError("captured")

    monkeypatch.setattr(mvp, "run_mvp_execution", fake_run_mvp_execution)

    with pytest.raises(RuntimeError, match="captured"):
        mvp.run_vertical_mvp_support(
            purchase=_purchase(),
            context=_context(),
            policy_version="MVP-E2E-SCENARIO-1",
            base_result="COMPRAR",
        )

    assert captured["scenario_coordination_result"] is None
