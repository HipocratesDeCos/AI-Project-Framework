from pydantic import ValidationError
import pytest

from eios.core.models import DecisionContext
from eios.core.scenario_engine import AuthorizedScenarioChange, ScenarioStatus, create_scenario
from eios.core.scenario_evaluation import (
    ScenarioEvaluationStatus,
    evaluate_scenario,
)


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-O3-001",
        scenario_id="S-BASE-001",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
    )


def valid_scenario():
    return create_scenario(
        context(),
        changes=(
            AuthorizedScenarioChange(
                variable="unit_price",
                base_value=10,
                simulated_value=9,
                unit="EUR",
                authorization=True,
                origin="human",
            ),
        ),
    )


def test_valid_scenario_produces_derived_result_with_context_preserved():
    scenario = valid_scenario()
    result = evaluate_scenario(scenario, context(), assessments=("A1",), viability_result="VIABLE")
    assert result.status == ScenarioEvaluationStatus.COMPLETED
    assert result.scenario_id == scenario.scenario_id
    assert result.decision_id == "D-O3-001"
    assert result.rules_version == "R-1"
    assert result.parameters_version == "P-1"
    assert result.data_snapshot_id == "SNAP-1"


def test_invalid_scenario_is_rejected():
    scenario = create_scenario(
        context(),
        changes=(
            AuthorizedScenarioChange(
                variable="unit_price",
                base_value=10,
                simulated_value=9,
                unit="EUR",
                authorization=False,
                origin="human",
            ),
        ),
    )
    assert scenario.status == ScenarioStatus.INVALID
    with pytest.raises(ValueError, match="VALID"):
        evaluate_scenario(scenario, context())


def test_context_mismatch_is_rejected():
    scenario = valid_scenario()
    mismatched = context().model_copy(update={"rules_version": "R-2"})
    with pytest.raises(ValueError, match="rules_version"):
        evaluate_scenario(scenario, mismatched)


def test_partial_evaluation_is_not_business_negative():
    result = evaluate_scenario(
        valid_scenario(),
        context(),
        status=ScenarioEvaluationStatus.PARTIALLY_COMPLETED,
        limitations=("missing assessment",),
    )
    assert result.status == ScenarioEvaluationStatus.PARTIALLY_COMPLETED
    assert result.limitations == ("missing assessment",)


def test_not_evaluable_is_not_not_viable():
    result = evaluate_scenario(
        valid_scenario(), context(), status=ScenarioEvaluationStatus.NOT_EVALUABLE
    )
    assert result.status == ScenarioEvaluationStatus.NOT_EVALUABLE


def test_failed_requires_explicit_reason():
    with pytest.raises(ValidationError, match="failure_reason"):
        evaluate_scenario(
            valid_scenario(), context(), status=ScenarioEvaluationStatus.FAILED
        )


def test_failed_is_technical_not_business_negative():
    result = evaluate_scenario(
        valid_scenario(),
        context(),
        status=ScenarioEvaluationStatus.FAILED,
        failure_reason="evaluation dependency unavailable",
    )
    assert result.status == ScenarioEvaluationStatus.FAILED
    assert result.failure_reason == "evaluation dependency unavailable"


def test_completed_cannot_hide_limitations():
    with pytest.raises(ValidationError, match="limitaciones"):
        evaluate_scenario(
            valid_scenario(),
            context(),
            assessments=("A1",),
            viability_result="VIABLE",
            status=ScenarioEvaluationStatus.COMPLETED,
            limitations=("pending",),
        )


def test_completed_requires_assessment_and_viability():
    with pytest.raises(ValidationError, match="Assessment"):
        evaluate_scenario(
            valid_scenario(),
            context(),
            viability_result="VIABLE",
        )
    with pytest.raises(ValidationError, match="Viability Frontier"):
        evaluate_scenario(
            valid_scenario(),
            context(),
            assessments=("A1",),
        )
