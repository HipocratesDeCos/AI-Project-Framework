from copy import deepcopy
from datetime import date
from decimal import Decimal

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.frontend.application_boundary import present_vertical_mvp_result
from eios.frontend.visual.vertical_mvp_view_model import build_vertical_mvp_view_model
from eios.vertical_orchestration import run_vertical_mvp_from_orchestration


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-E2E-SCENARIO",
        scenario_id="BASE",
        rules_version="RULES-E2E-1",
        parameters_version="PARAMS-E2E-1",
        data_snapshot_id="SNAP-E2E-1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-E2E-SCENARIO",
        scenario_id="BASE",
        article_id="ART-E2E",
        supplier_id="SUP-E2E",
        quantity=Decimal("12"),
        unit_price=Decimal("4.50"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _policy() -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-E2E-1")


def _variable(domain=(1, 2)) -> GenerationVariable:
    return GenerationVariable(
        variable_id="quantity_delta",
        value_type="integer",
        base_value=0,
        domain=domain,
    )


def _analytics(
    scenario_id: str,
    *,
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED,
) -> AuthorizedScenarioAnalytics:
    kwargs = {
        "scenario_id": scenario_id,
        "assessments": (
            {
                "assessment_id": f"A-{scenario_id}",
                "status": "AUTHORIZED",
            },
        ),
        "viability_result": {
            "viability_id": f"VF-{scenario_id}",
            "status": "AUTHORIZED",
        },
        "trace_references": (f"TRACE-{scenario_id}",),
        "status": status,
    }
    if status is ScenarioEvaluationStatus.NOT_EVALUABLE:
        kwargs["limitations"] = ("missing-evidence",)
    if status is ScenarioEvaluationStatus.FAILED:
        kwargs["failure_reason"] = "technical-evaluation-failure"
    return AuthorizedScenarioAnalytics(**kwargs)


def _run_chain(
    *,
    domain=(1, 2),
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED,
):
    context = _context()
    purchase = _purchase()
    preparation = prepare_o4_o2_o3_orchestration(
        context=context,
        variables=(_variable(domain),),
        policy=_policy(),
    )
    valid_scenarios = tuple(
        scenario
        for scenario in preparation.materialization.scenarios
        if scenario.status.value == "VALID"
    )
    analytics = tuple(
        _analytics(scenario.scenario_id, status=status)
        for scenario in valid_scenarios
    )
    orchestration = complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=analytics,
    )
    vertical = run_vertical_mvp_from_orchestration(
        purchase=purchase,
        orchestration_result=orchestration,
        policy_version="MVP-E2E-SCENARIO-1",
    )
    payload = present_vertical_mvp_result(vertical)
    view = build_vertical_mvp_view_model(payload)
    return {
        "context": context,
        "purchase": purchase,
        "preparation": preparation,
        "analytics": analytics,
        "orchestration": orchestration,
        "vertical": vertical,
        "payload": payload,
        "view": view,
    }


def test_completed_pipeline_preserves_identity_analytics_and_traceability_to_view_model():
    chain = _run_chain()
    view = chain["view"]
    context = view["scenario_execution_context"]

    assert view["execution_status"] == "COMPLETED"
    assert view["rules_available"] is False
    assert view["scenario_support_available"] is True
    assert tuple(item["capability"] for item in view["capabilities"]) == (
        "SCENARIO_COORDINATION",
    )

    assert context["decision_id"] == "D-E2E-SCENARIO"
    assert context["rules_version"] == "RULES-E2E-1"
    assert context["parameters_version"] == "PARAMS-E2E-1"
    assert context["data_snapshot_id"] == "SNAP-E2E-1"

    orchestration_ids = tuple(
        item.scenario_id for item in chain["orchestration"].evaluations
    )
    visible_ids = tuple(item["scenario_id"] for item in view["scenario_records"])
    assert visible_ids == tuple(sorted(orchestration_ids))

    for record in view["scenario_records"]:
        scenario_id = record["scenario_id"]
        assert record["status"] == "COMPLETED"
        assert record["values"]["assessments"] == [
            {
                "assessment_id": f"A-{scenario_id}",
                "status": "AUTHORIZED",
            }
        ]
        assert record["values"]["viability_result"] == {
            "viability_id": f"VF-{scenario_id}",
            "status": "AUTHORIZED",
        }
        assert record["trace_references"] == [f"TRACE-{scenario_id}"]


def test_multiple_scenarios_keep_deterministic_order_through_entire_chain():
    first = _run_chain(domain=(3, 1, 2))
    second = _run_chain(domain=(3, 1, 2))

    first_ids = tuple(item["scenario_id"] for item in first["view"]["scenario_records"])
    second_ids = tuple(item["scenario_id"] for item in second["view"]["scenario_records"])

    assert first_ids == tuple(sorted(first_ids))
    assert first_ids == second_ids
    assert first["view"] == second["view"]


def test_not_evaluable_remains_non_decisional_through_presentation():
    chain = _run_chain(
        domain=(1,),
        status=ScenarioEvaluationStatus.NOT_EVALUABLE,
    )
    view = chain["view"]
    record = view["scenario_records"][0]

    assert view["execution_status"] == "PARTIALLY_COMPLETED"
    assert view["unresolved_items"] == ["missing-evidence"]
    assert view["capabilities"][0]["status"] == "NOT_EVALUABLE"
    assert view["capabilities"][0]["result_available"] is False
    assert view["capabilities"][0]["unresolved_items"] == ["missing-evidence"]
    assert record["status"] == "NOT_EVALUABLE"
    assert record["unresolved_items"] == ["missing-evidence"]
    assert record["failure_reason"] is None
    assert "outcome" not in record or record.get("outcome") is not False


def test_failed_remains_technical_failure_through_presentation():
    chain = _run_chain(
        domain=(1,),
        status=ScenarioEvaluationStatus.FAILED,
    )
    view = chain["view"]
    record = view["scenario_records"][0]

    assert view["execution_status"] == "FAILED"
    assert view["capabilities"][0]["status"] == "FAILED"
    assert view["capabilities"][0]["result_available"] is False
    assert record["status"] == "FAILED"
    assert record["failure_reason"] == "technical-evaluation-failure"
    assert "rejection" not in record


def test_pipeline_is_immutable_and_presentation_outputs_are_detached():
    context = _context()
    purchase = _purchase()
    context_before = context.model_copy(deep=True)
    purchase_before = purchase.model_copy(deep=True)

    preparation = prepare_o4_o2_o3_orchestration(
        context=context,
        variables=(_variable((1,)),),
        policy=_policy(),
    )
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    analytics = (_analytics(scenario_id),)
    analytics_before = deepcopy(analytics)
    preparation_before = preparation.model_copy(deep=True)

    orchestration = complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=analytics,
    )
    orchestration_before = orchestration.model_copy(deep=True)
    vertical = run_vertical_mvp_from_orchestration(
        purchase=purchase,
        orchestration_result=orchestration,
        policy_version="MVP-E2E-SCENARIO-1",
    )
    vertical_before = vertical.model_copy(deep=True)
    payload = present_vertical_mvp_result(vertical)
    payload_before = deepcopy(payload)
    view = build_vertical_mvp_view_model(payload)

    view["scenario_records"][0]["trace_references"].append("MUTATED")
    view["scenario_execution_context"]["decision_id"] = "MUTATED"

    assert context == context_before
    assert purchase == purchase_before
    assert preparation == preparation_before
    assert analytics == analytics_before
    assert orchestration == orchestration_before
    assert vertical == vertical_before
    assert payload == payload_before


def test_e2e_view_model_contains_no_decision_authority():
    view = _run_chain()["view"]
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

    assert forbidden.isdisjoint(view)
    assert forbidden.isdisjoint(view["scenario_comparison"])
    for record in view["scenario_records"]:
        assert forbidden.isdisjoint(record)

    assert view["rules_available"] is False
    assert view["scenario_support_available"] is True
