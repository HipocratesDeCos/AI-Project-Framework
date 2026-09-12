from copy import deepcopy

import pytest

import eios.core.o4_o2_o3_orchestration as orchestration
from eios.core.models import DecisionContext
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    _complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_engine import ScenarioStatus
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationStatus, GenerationVariable


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D1",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SN1",
    )


def policy(**kwargs) -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-ORCH-1", **kwargs)


def variable(domain=(1,)) -> GenerationVariable:
    return GenerationVariable(
        variable_id="qty",
        value_type="integer",
        base_value=0,
        domain=domain,
    )


def analytics_for(scenario_id: str, **kwargs) -> AuthorizedScenarioAnalytics:
    payload = {
        "scenario_id": scenario_id,
        "assessments": ({"assessment": scenario_id},),
        "viability_result": {"viability": scenario_id},
    }
    payload.update(kwargs)
    return AuthorizedScenarioAnalytics(**payload)


def test_stage_one_materializes_and_exposes_real_o2_ids():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )

    assert prepared.materialization.generation.status is GenerationStatus.GENERATED
    assert len(prepared.materialization.scenarios) == 1
    scenario = prepared.materialization.scenarios[0]
    assert scenario.status is ScenarioStatus.VALID
    assert scenario.scenario_id
    assert scenario.decision_id == "D1"
    assert scenario.rules_version == "R1"
    assert scenario.parameters_version == "P1"
    assert scenario.data_snapshot_id == "SN1"


def test_stage_two_completes_o3_only_with_explicit_assessment_and_viability():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id

    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared,
        analytics=(analytics_for(scenario_id),),
    )

    assert [item.scenario_id for item in result.evaluations] == [scenario_id]
    assert result.evaluations[0].status is ScenarioEvaluationStatus.COMPLETED
    assert result.evaluations[0].assessments
    assert result.evaluations[0].viability_result is not None


def test_missing_analytics_fails_before_o3_is_invoked(monkeypatch):
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )

    def must_not_run(*args, **kwargs):
        raise AssertionError("O3 no debe ejecutarse sin paquete analítico completo")

    monkeypatch.setattr(orchestration, "evaluate_scenario", must_not_run)
    with pytest.raises(ValueError, match="faltan paquetes analíticos"):
        _complete_o4_o2_o3_orchestration(preparation=prepared, analytics=())


def test_empty_assessments_are_rejected():
    with pytest.raises(ValueError, match="Assessment explícito"):
        AuthorizedScenarioAnalytics(
            scenario_id="S1",
            assessments=(),
            viability_result={"viability": True},
        )


def test_missing_viability_is_rejected():
    with pytest.raises(ValueError, match="Viability Frontier explícito"):
        AuthorizedScenarioAnalytics(
            scenario_id="S1",
            assessments=({"assessment": True},),
            viability_result=None,
        )


def test_unknown_or_extra_analytics_are_rejected():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    valid_id = prepared.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="no autorizados/sobrantes"):
        _complete_o4_o2_o3_orchestration(
            preparation=prepared,
            analytics=(analytics_for(valid_id), analytics_for("UNKNOWN")),
        )


def test_duplicate_analytics_ids_are_rejected():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id
    packet = analytics_for(scenario_id)

    with pytest.raises(ValueError, match="duplicado"):
        _complete_o4_o2_o3_orchestration(
            preparation=prepared,
            analytics=(packet, packet.model_copy(deep=True)),
        )


def test_zero_variable_draft_is_preserved_and_never_sent_to_o3(monkeypatch):
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(), policy=policy()
    )
    assert len(prepared.materialization.scenarios) == 1
    assert prepared.materialization.scenarios[0].status is ScenarioStatus.DRAFT

    def must_not_run(*args, **kwargs):
        raise AssertionError("O3 no debe recibir DRAFT")

    monkeypatch.setattr(orchestration, "evaluate_scenario", must_not_run)
    result = _complete_o4_o2_o3_orchestration(preparation=prepared, analytics=())
    assert result.evaluations == ()


def test_non_generative_o4_state_produces_no_o3_evaluation():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(domain=()),), policy=policy()
    )
    assert prepared.materialization.generation.status is GenerationStatus.EMPTY
    assert prepared.materialization.scenarios == ()

    result = _complete_o4_o2_o3_orchestration(preparation=prepared, analytics=())
    assert result.evaluations == ()


def test_partial_o3_state_limitations_and_traces_are_preserved():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id
    packet = analytics_for(
        scenario_id,
        status=ScenarioEvaluationStatus.PARTIALLY_COMPLETED,
        limitations=("dato pendiente",),
        trace_references=("TRACE-2", "TRACE-1"),
    )

    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared, analytics=(packet,)
    )
    evaluation = result.evaluations[0]
    assert evaluation.status is ScenarioEvaluationStatus.PARTIALLY_COMPLETED
    assert evaluation.limitations == ("dato pendiente",)
    assert evaluation.trace_references == ("TRACE-2", "TRACE-1")


def test_output_order_depends_on_o2_scenarios_not_analytics_input_order():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(domain=(1, 2)),), policy=policy()
    )
    ids = tuple(item.scenario_id for item in prepared.materialization.scenarios)
    assert len(ids) == 2

    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared,
        analytics=(analytics_for(ids[1]), analytics_for(ids[0])),
    )
    assert tuple(item.scenario_id for item in result.evaluations) == ids


def test_stage_two_does_not_rerun_o4_o2(monkeypatch):
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id

    def must_not_rerun(*args, **kwargs):
        raise AssertionError("Etapa 2 no debe reejecutar O4/O2")

    monkeypatch.setattr(orchestration, "run_o4_o2_materialization", must_not_rerun)
    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared,
        analytics=(analytics_for(scenario_id),),
    )
    assert len(result.evaluations) == 1


def test_inputs_and_nested_analytics_are_isolated():
    ctx = context()
    variables = (variable(),)
    variables_before = deepcopy(variables)
    prepared = prepare_o4_o2_o3_orchestration(
        context=ctx, variables=variables, policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id

    assessment = {"nested": [1]}
    viability = {"nested": [2]}
    packet = AuthorizedScenarioAnalytics(
        scenario_id=scenario_id,
        assessments=(assessment,),
        viability_result=viability,
    )
    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared, analytics=(packet,)
    )

    assessment["nested"].append(9)
    viability["nested"].append(9)
    assert result.evaluations[0].assessments[0] == {"nested": [1]}
    assert result.evaluations[0].viability_result == {"nested": [2]}
    assert variables == variables_before
    assert ctx == context()


def test_orchestration_exposes_no_decision_authority_fields():
    prepared = prepare_o4_o2_o3_orchestration(
        context=context(), variables=(variable(),), policy=policy()
    )
    scenario_id = prepared.materialization.scenarios[0].scenario_id
    result = _complete_o4_o2_o3_orchestration(
        preparation=prepared,
        analytics=(analytics_for(scenario_id),),
    )

    for forbidden in ("ranking", "score", "recommendation", "selection", "approval", "rejection", "decision"):
        assert not hasattr(result, forbidden)
