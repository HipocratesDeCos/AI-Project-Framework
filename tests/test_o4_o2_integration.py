from copy import deepcopy
import inspect

import pytest

from eios.core.models import DecisionContext
from eios.core.o4_o2_integration import (
    O4O2MaterializationResult,
    run_o4_o2_materialization,
)
from eios.core.scenario_engine import ScenarioStatus, create_scenario
from eios.core.scenario_generation import (
    GenerationPolicy,
    GenerationStatus,
    GenerationVariable,
)


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-O4-O2",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SNAP1",
    )


def _policy(**updates) -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-POLICY-1", **updates)


def _variable(
    variable_id: str = "qty",
    *,
    base_value=1,
    domain=(2,),
) -> GenerationVariable:
    return GenerationVariable(
        variable_id=variable_id,
        value_type="integer",
        base_value=base_value,
        domain=domain,
    )


def test_generated_candidate_is_materialized_only_through_o2():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(),),
        policy=_policy(),
        parent_scenario_id="BASE",
    )

    assert result.generation.status is GenerationStatus.GENERATED
    assert len(result.generation.candidates) == 1
    assert len(result.scenarios) == 1

    scenario = result.scenarios[0]
    assert scenario.status is ScenarioStatus.VALID
    assert scenario.parent_scenario_id == "BASE"
    assert scenario.decision_id == "D-O4-O2"
    assert scenario.rules_version == "R1"
    assert scenario.parameters_version == "P1"
    assert scenario.data_snapshot_id == "SNAP1"

    candidate = result.generation.candidates[0]
    expected = create_scenario(
        _context(),
        candidate.changes,
        parent_scenario_id=candidate.parent_scenario_id,
        validate=True,
    )
    assert scenario == expected


def test_o4_source_representation_is_preserved_separately_from_o2_canonicalization():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(),),
        policy=_policy(),
    )

    source_change = result.generation.candidates[0].changes[0]
    materialized_change = result.scenarios[0].changes[0]

    assert source_change.base_value == 1
    assert source_change.simulated_value == 2
    assert materialized_change.base_value == {"type": "int", "value": 1}
    assert materialized_change.simulated_value == {"type": "int", "value": 2}


def test_same_inputs_produce_same_generation_ids_and_fingerprints():
    kwargs = {
        "context": _context(),
        "variables": (
            _variable("a", base_value=0, domain=(1, 2)),
            _variable("b", base_value=0, domain=(1,)),
        ),
        "policy": _policy(),
        "parent_scenario_id": "BASE",
    }

    first = run_o4_o2_materialization(**kwargs)
    second = run_o4_o2_materialization(**kwargs)

    assert first.generation == second.generation
    assert tuple(item.scenario_id for item in first.scenarios) == tuple(
        item.scenario_id for item in second.scenarios
    )
    assert tuple(item.fingerprint for item in first.scenarios) == tuple(
        item.fingerprint for item in second.scenarios
    )


def test_materialized_order_tracks_o4_candidate_order():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(
            _variable("a", base_value=0, domain=(0, 1)),
            _variable("b", base_value=0, domain=(0, 2)),
        ),
        policy=_policy(),
    )

    expected = tuple(
        create_scenario(
            _context(),
            candidate.changes,
            parent_scenario_id=candidate.parent_scenario_id,
            validate=True,
        ).scenario_id
        for candidate in result.generation.candidates
    )
    assert tuple(item.scenario_id for item in result.scenarios) == expected
    assert len(set(expected)) == len(expected)


def test_zero_variables_remains_o2_draft_and_is_not_forced_valid():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(),
        policy=_policy(),
    )

    assert result.generation.status is GenerationStatus.GENERATED
    assert result.generation.candidates[0].changes == ()
    assert len(result.scenarios) == 1
    assert result.scenarios[0].status is ScenarioStatus.DRAFT
    assert result.scenarios[0].changes == ()


def test_empty_generation_creates_no_scenario():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(domain=()),),
        policy=_policy(),
    )
    assert result.generation.status is GenerationStatus.EMPTY
    assert result.scenarios == ()


def test_blocked_generation_creates_no_scenario():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(domain=(1, 2)),),
        policy=_policy(max_cardinality_per_variable=1),
    )
    assert result.generation.status is GenerationStatus.BLOCKED
    assert result.generation.reason
    assert result.scenarios == ()


def test_failed_generation_creates_no_scenario():
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(),),
        policy=_policy(),
        depth=-1,
    )
    assert result.generation.status is GenerationStatus.FAILED
    assert result.generation.reason
    assert result.scenarios == ()


def test_not_evaluable_generation_creates_no_scenario(monkeypatch):
    import eios.core.scenario_generation as generation

    def exploding_prod(_):
        raise TypeError("cardinalidad indeterminable")

    monkeypatch.setattr(generation, "prod", exploding_prod)
    result = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(),),
        policy=_policy(),
    )

    assert result.generation.status is GenerationStatus.NOT_EVALUABLE
    assert result.generation.reason
    assert result.scenarios == ()


def test_inputs_are_not_mutated():
    context = _context()
    variables = (_variable(domain=(1, 2)),)
    policy = _policy()
    before = (deepcopy(context), deepcopy(variables), deepcopy(policy))

    run_o4_o2_materialization(
        context=context,
        variables=variables,
        policy=policy,
        parent_scenario_id="BASE",
    )

    assert context == before[0]
    assert variables == before[1]
    assert policy == before[2]


def test_public_operation_does_not_accept_detached_generation_result():
    parameters = inspect.signature(run_o4_o2_materialization).parameters
    assert "generation" not in parameters
    assert "generation_result" not in parameters
    assert set(parameters) == {
        "context",
        "variables",
        "policy",
        "parent_scenario_id",
        "depth",
    }


def test_output_contract_rejects_scenarios_for_non_generated_state():
    generated = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(),),
        policy=_policy(),
    )
    empty = run_o4_o2_materialization(
        context=_context(),
        variables=(_variable(domain=()),),
        policy=_policy(),
    )

    with pytest.raises(ValueError, match="Solo GENERATED"):
        O4O2MaterializationResult(
            generation=empty.generation,
            scenarios=generated.scenarios,
        )


def test_output_has_no_decision_or_ranking_fields():
    forbidden = {
        "score",
        "ranking",
        "recommendation",
        "selection",
        "approval",
        "rejection",
        "decision",
        "best_scenario",
    }
    assert forbidden.isdisjoint(O4O2MaterializationResult.model_fields)
