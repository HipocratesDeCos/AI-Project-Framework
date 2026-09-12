from copy import deepcopy
from decimal import Decimal

import pytest

from eios.core.execution_boundary import BoundaryStatus, ExecutionOutcome
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o2 import O2ScenarioResult, O2ScenarioStatus, build_support_package
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.frontend.application_boundary import present_vertical_mvp_result
from eios.frontend.visual.vertical_mvp_view_model import build_vertical_mvp_view_model
from eios.mvp import VerticalMVPSupportResult


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-SCENARIO-UI",
        scenario_id="BASE",
        rules_version="rules-v2",
        parameters_version="params-v2",
        data_snapshot_id="snapshot-v2",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-SCENARIO-UI",
        scenario_id="BASE",
        article_id="ART-UI",
        supplier_id="SUP-UI",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-12",
    )


def _support():
    scenarios = (
        O2ScenarioResult(
            scenario_id="SC-B",
            status=O2ScenarioStatus.FAILED,
            values={
                "assessments": [{"rule_id": "R-B", "outcome": "TRUE"}],
                "viability_result": {"status": "FAILED"},
            },
            trace_references=("TRACE-B",),
            unresolved_items=("technical-gap",),
            failure_reason="technical failure",
        ),
        O2ScenarioResult(
            scenario_id="SC-A",
            status=O2ScenarioStatus.NOT_EVALUABLE,
            values={
                "assessments": [{"rule_id": "R-A", "outcome": None}],
                "viability_result": {"status": "NOT_EVALUABLE"},
            },
            trace_references=("TRACE-A",),
            unresolved_items=("missing-evidence",),
        ),
    )
    return build_support_package(_purchase(), _context(), scenarios)


def _vertical_result(with_support: bool = True) -> VerticalMVPSupportResult:
    execution = ExecutionOutcome(
        status=BoundaryStatus.COMPLETED,
        policy_version="MVP-E2E-SCENARIO-1",
        capability_results=(
            CapabilityExecution(
                capability="SCENARIO_COORDINATION",
                status=O1ExecutionStatus.PARTIALLY_COMPLETED,
                result_available=True,
                trace_references=("TRACE-A", "TRACE-B"),
                unresolved_items=("missing-evidence", "technical-gap"),
            ),
        ),
    )
    return VerticalMVPSupportResult(
        execution=execution,
        scenario_support=_support() if with_support else None,
    )


def test_application_boundary_exposes_explicit_null_when_scenario_support_absent():
    payload = present_vertical_mvp_result(_vertical_result(with_support=False))

    assert "scenario_support" in payload
    assert payload["scenario_support"] is None


def test_application_boundary_preserves_o2_scenario_support_structure():
    result = _vertical_result()
    payload = present_vertical_mvp_result(result)
    support = payload["scenario_support"]

    assert support is not None
    assert support["execution_context"]["decision_id"] == "D-SCENARIO-UI"
    assert support["execution_context"]["rules_version"] == "rules-v2"
    assert support["execution_context"]["parameters_version"] == "params-v2"
    assert support["execution_context"]["data_snapshot_id"] == "snapshot-v2"
    assert [item["scenario_id"] for item in support["scenarios"]] == ["SC-A", "SC-B"]
    assert support["scenarios"][0]["status"] == "NOT_EVALUABLE"
    assert support["scenarios"][0]["unresolved_items"] == ["missing-evidence"]
    assert support["scenarios"][0]["trace_references"] == ["TRACE-A"]
    assert support["scenarios"][1]["status"] == "FAILED"
    assert support["scenarios"][1]["failure_reason"] == "technical failure"
    assert support["comparison"]["scenario_ids"] == ["SC-A", "SC-B"]
    assert support["comparison"]["statuses"] == {
        "SC-A": "NOT_EVALUABLE",
        "SC-B": "FAILED",
    }


def test_view_model_copies_scenario_support_without_recalculation():
    payload = present_vertical_mvp_result(_vertical_result())
    payload_before = deepcopy(payload)

    view = build_vertical_mvp_view_model(payload)

    assert view["scenario_support_available"] is True
    assert view["scenario_execution_context"] == payload["scenario_support"]["execution_context"]
    assert view["scenario_records"] == payload["scenario_support"]["scenarios"]
    assert view["scenario_comparison"] == payload["scenario_support"]["comparison"]
    assert view["scenario_records"][0]["status"] == "NOT_EVALUABLE"
    assert view["scenario_records"][1]["status"] == "FAILED"
    assert view["scenario_records"][1]["failure_reason"] == "technical failure"

    view["scenario_records"][0]["trace_references"].append("MUTATED")
    view["scenario_comparison"]["scenario_ids"].append("MUTATED")
    assert payload == payload_before


def test_application_boundary_output_is_detached_from_vertical_result():
    result = _vertical_result()
    original = result.model_copy(deep=True)

    payload = present_vertical_mvp_result(result)
    payload["scenario_support"]["scenarios"][0]["values"]["mutated"] = True

    assert result == original


def test_view_model_fails_closed_on_malformed_scenario_support():
    payload = present_vertical_mvp_result(_vertical_result())

    malformed = deepcopy(payload)
    del malformed["scenario_support"]["execution_context"]
    with pytest.raises(ValueError, match="scenario_support"):
        build_vertical_mvp_view_model(malformed)

    malformed = deepcopy(payload)
    malformed["scenario_support"]["scenarios"] = "SC-A"
    with pytest.raises(ValueError, match="scenarios"):
        build_vertical_mvp_view_model(malformed)

    malformed = deepcopy(payload)
    del malformed["scenario_support"]["scenarios"][0]["status"]
    with pytest.raises(ValueError, match="claves contractuales"):
        build_vertical_mvp_view_model(malformed)

    malformed = deepcopy(payload)
    malformed["scenario_support"]["comparison"] = []
    with pytest.raises(ValueError, match="comparison"):
        build_vertical_mvp_view_model(malformed)


def test_scenario_presentation_does_not_create_decision_authority():
    payload = present_vertical_mvp_result(_vertical_result())
    view = build_vertical_mvp_view_model(payload)
    forbidden = {
        "score",
        "ranking",
        "recommendation",
        "approval",
        "rejection",
        "best_scenario",
        "selected_scenario",
    }

    assert forbidden.isdisjoint(payload["scenario_support"])
    assert forbidden.isdisjoint(view)
    for scenario in view["scenario_records"]:
        assert forbidden.isdisjoint(scenario)
