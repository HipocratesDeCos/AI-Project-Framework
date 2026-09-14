from dataclasses import replace

import pytest

import eios.core.viability_scenario_integration as vf_bridge
from eios.core.models import DecisionContext
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import ViabilityResult, ViabilityStatus


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-VF-SCENARIO",
        scenario_id="BASE",
        rules_version="RULES-VF-1",
        parameters_version="PARAMS-VF-1",
        data_snapshot_id="SNAP-VF-1",
    )


def _preparation():
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
        policy=GenerationPolicy(policy_version="O4-VF-1"),
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


def test_vf_scenario_bridge_is_internal_and_not_exported() -> None:
    assert vf_bridge.__all__ == []
    assert not hasattr(vf_bridge, "build_authorized_analytics_from_viability")
    assert callable(vf_bridge._build_context_bound_analytics_from_viability)


def test_internal_bridge_validates_context_and_preserves_payload() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    package = vf_bridge._build_context_bound_analytics_from_viability(
        preparation=preparation,
        scenario_id=scenario_id,
        assessments=({"internal": True},),
        viability_result=_viability(scenario_id),
        trace_references=("TRACE-O3-1",),
    )

    assert package.scenario_id == scenario_id
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


def test_internal_bridge_rejects_foreign_decision_and_scenario() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="decision_id"):
        vf_bridge._build_context_bound_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=({"internal": True},),
            viability_result=_viability(scenario_id, decision_id="OTHER"),
        )

    with pytest.raises(ValueError, match="scenario_id"):
        vf_bridge._build_context_bound_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=({"internal": True},),
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
def test_internal_bridge_rejects_foreign_or_missing_version_binding(field, value) -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    vf = replace(_viability(scenario_id), **{field: value})

    with pytest.raises(ValueError, match=field):
        vf_bridge._build_context_bound_analytics_from_viability(
            preparation=preparation,
            scenario_id=scenario_id,
            assessments=({"internal": True},),
            viability_result=vf,
        )


def test_internal_bridge_rejects_unknown_scenario() -> None:
    preparation = _preparation()

    with pytest.raises(ValueError, match="no pertenece"):
        vf_bridge._build_context_bound_analytics_from_viability(
            preparation=preparation,
            scenario_id="UNKNOWN",
            assessments=({"internal": True},),
            viability_result=_viability("UNKNOWN"),
        )
