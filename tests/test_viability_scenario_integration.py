from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    _complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import ViabilityResult, ViabilityStatus
from eios.core.viability_scenario_integration import (
    build_authorized_analytics_from_viability,
)
from eios.frontend.application_boundary import present_vertical_mvp_result
from eios.vertical_orchestration import run_vertical_mvp_from_orchestration


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-VF-SCENARIO",
        scenario_id="BASE",
        rules_version="RULES-VF-1",
        parameters_version="PARAMS-VF-1",
        data_snapshot_id="SNAP-VF-1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-VF-SCENARIO",
        scenario_id="BASE",
        article_id="ART-VF",
        supplier_id="SUP-VF",
        quantity=Decimal("10"),
        unit_price=Decimal("7.50"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _policy() -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-VF-1")


def _valid_preparation():
    return prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1,),
            ),
        ),
        policy=_policy(),
    )


def _viability(scenario_id: str, **changes) -> ViabilityResult:
    data = dict(
        decision_id="D-VF-SCENARIO",
        scenario_id=scenario_id,
        status=ViabilityStatus.VIABLE,
        assessment_ids=("A-1",),
        rule_ids=("R-1",),
        trace_references=("TRACE-VF-1",),
        rules_version="RULES-VF-1",
        parameters_version="PARAMS-VF-1",
        data_snapshot_id="SNAP-VF-1",
        limitation=None,
    )
    data.update(changes)
    return ViabilityResult(**data)


def _assessments():
    return ({"assessment_id": "A-1", "outcome": "AUTHORIZED"},)


def test_exact_typed_viability_builds_authorized_analytics_with_canonical_payload():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    vf = _viability(scenario_id)

    package = build_authorized_analytics_from_viability(
        preparation=preparation,
        scenario_id=scenario_id,
        assessments=_assessments(),
        viability_result=vf,
        trace_references=("TRACE-O3-1",),
    )

    assert package.scenario_id == scenario_id
    assert package.status is ScenarioEvaluationStatus.COMPLETED
    assert package.viability_result == {
        "decision_id": "D-VF-SCENARIO",
        "scenario_id": scenario_id,
        "status": "VIABLE",
        "assessment_ids": ("A-1",),
        "rule_ids": ("R-1",),
        "trace_references": ("TRACE-VF-1",),
        "rules_version": "RULES-VF-1",
        "parameters_version": "PARAMS-VF-1",
        "data_snapshot_id": "SNAP-VF-1",
        "limitation": None,
    }
    assert package.trace_references == ("TRACE-O3-1",)


def test_foreign_decision_is_rejected():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="decision_id"):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=_assessments(),
            viability_result=_viability(scenario_id, decision_id="OTHER"),
        )


def test_foreign_scenario_is_rejected():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="scenario_id"):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=_assessments(),
            viability_result=_viability("OTHER-SCENARIO"),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("rules_version", "OTHER-RULES"),
        ("parameters_version", "OTHER-PARAMS"),
        ("data_snapshot_id", "OTHER-SNAPSHOT"),
        ("rules_version", None),
        ("parameters_version", None),
        ("data_snapshot_id", None),
    ),
)
def test_foreign_or_missing_version_binding_is_rejected(field, value):
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    vf = replace(_viability(scenario_id), **{field: value})

    with pytest.raises(ValueError, match=field):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=_assessments(),
            viability_result=vf,
        )


def test_unknown_scenario_id_is_rejected_before_binding():
    preparation = _valid_preparation()

    with pytest.raises(ValueError, match="no pertenece"):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id="UNKNOWN",
            assessments=_assessments(),
            viability_result=_viability("UNKNOWN"),
        )


def test_draft_scenario_is_rejected():
    preparation = prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(),
        policy=_policy(),
    )
    draft = preparation.materialization.scenarios[0]

    with pytest.raises(ValueError, match="VALID"):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id=draft.scenario_id,
            assessments=_assessments(),
            viability_result=_viability(draft.scenario_id),
        )


def test_empty_assessments_remain_fail_closed_by_authorized_package_contract():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="Assessment"):
        build_authorized_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=(),
            viability_result=_viability(scenario_id),
        )


def test_viability_status_does_not_map_or_override_explicit_o3_status():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    vf = _viability(scenario_id, status=ViabilityStatus.NOT_VIABLE)

    package = build_authorized_analytics_from_viability(
        preparation=preparation,
        scenario_id=scenario_id,
        assessments=_assessments(),
        viability_result=vf,
        status=ScenarioEvaluationStatus.PARTIALLY_COMPLETED,
        limitations=("technical-pending",),
    )

    assert package.status is ScenarioEvaluationStatus.PARTIALLY_COMPLETED
    assert package.viability_result["status"] == "NOT_VIABLE"
    assert package.limitations == ("technical-pending",)
    assert not hasattr(package, "rejection")


def test_inputs_are_immutable_and_payload_is_detached():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    vf = _viability(scenario_id)
    assessments = _assessments()
    preparation_before = preparation.model_copy(deep=True)
    vf_before = deepcopy(vf)
    assessments_before = deepcopy(assessments)

    package = build_authorized_analytics_from_viability(
        preparation=preparation,
        scenario_id=scenario_id,
        assessments=assessments,
        viability_result=vf,
    )
    package.viability_result["assessment_ids"] += ("MUTATED-OUTPUT",)

    assert preparation == preparation_before
    assert vf == vf_before
    assert assessments == assessments_before


def test_validated_viability_serializes_through_o3_vertical_and_presentation():
    preparation = _valid_preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    package = build_authorized_analytics_from_viability(
        preparation=preparation,
        scenario_id=scenario_id,
        assessments=_assessments(),
        viability_result=_viability(
            scenario_id,
            status=ViabilityStatus.VIABLE_CON_CONDICIONES,
            limitation="CONDITION-TRACE",
        ),
        trace_references=("TRACE-O3-1",),
    )

    orchestration = _complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=(package,),
    )
    vertical = run_vertical_mvp_from_orchestration(
        purchase=_purchase(),
        orchestration_result=orchestration,
        policy_version="MVP-VF-1",
    )
    payload = present_vertical_mvp_result(vertical)
    visible_vf = payload["scenario_support"]["scenarios"][0]["values"][
        "viability_result"
    ]

    assert visible_vf == {
        "decision_id": "D-VF-SCENARIO",
        "scenario_id": scenario_id,
        "status": "VIABLE_CON_CONDICIONES",
        "assessment_ids": ["A-1"],
        "rule_ids": ["R-1"],
        "trace_references": ["TRACE-VF-1"],
        "rules_version": "RULES-VF-1",
        "parameters_version": "PARAMS-VF-1",
        "data_snapshot_id": "SNAP-VF-1",
        "limitation": "CONDITION-TRACE",
    }
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
    assert forbidden.isdisjoint(visible_vf)
