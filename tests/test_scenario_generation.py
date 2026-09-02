import pytest
from pydantic import ValidationError

from eios.core.scenario_generation import (
    GenerationLimits,
    GenerationPolicy,
    GenerationStatus,
    ScenarioGenerationRequest,
    ScenarioVariable,
    generate_scenarios,
)


def limits(**overrides):
    values = dict(
        max_variables=4,
        max_cardinality_per_variable=4,
        max_total_combinations=16,
        max_depth=2,
        max_emitted=16,
    )
    values.update(overrides)
    return GenerationLimits(**values)


def policy():
    return GenerationPolicy(policy_version="o4-v1")


def request(variables=(), **overrides):
    values = dict(
        decision_id="D1",
        scenario_id="S1",
        variables=tuple(variables),
        limits=limits(),
        policy=policy(),
    )
    values.update(overrides)
    return ScenarioGenerationRequest(**values)


def test_zero_variables_produces_one_base_candidate():
    result = generate_scenarios(request())
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 1


def test_empty_domain_is_empty():
    result = generate_scenarios(request([ScenarioVariable(variable_id="x", value_type="int", values=())]))
    assert result.status is GenerationStatus.EMPTY
    assert result.candidates == ()


def test_cartesian_cardinality():
    result = generate_scenarios(
        request([
            ScenarioVariable(variable_id="x", value_type="int", values=(1, 2)),
            ScenarioVariable(variable_id="y", value_type="int", values=(10, 20)),
        ])
    )
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 4


def test_total_limit_blocks_before_expansion():
    result = generate_scenarios(
        request(
            [
                ScenarioVariable(variable_id="x", value_type="int", values=(1, 2)),
                ScenarioVariable(variable_id="y", value_type="int", values=(10, 20)),
            ],
            limits=limits(max_total_combinations=3),
        )
    )
    assert result.status is GenerationStatus.BLOCKED
    assert result.candidates == ()


def test_variable_limit_blocks():
    result = generate_scenarios(
        request([ScenarioVariable(variable_id="x", value_type="int", values=(1,))], limits=limits(max_variables=0))
    )
    assert result.status is GenerationStatus.BLOCKED


def test_depth_limit_blocks():
    result = generate_scenarios(request(depth=3, limits=limits(max_depth=2)))
    assert result.status is GenerationStatus.BLOCKED


def test_order_of_variables_does_not_change_output():
    a = generate_scenarios(
        request([
            ScenarioVariable(variable_id="b", value_type="int", values=(2, 3)),
            ScenarioVariable(variable_id="a", value_type="int", values=(1,)),
        ])
    )
    b = generate_scenarios(
        request([
            ScenarioVariable(variable_id="a", value_type="int", values=(1,)),
            ScenarioVariable(variable_id="b", value_type="int", values=(2, 3)),
        ])
    )
    assert a.candidates == b.candidates


def test_unauthorized_space_is_blocked():
    result = generate_scenarios(request(authorized=False))
    assert result.status is GenerationStatus.BLOCKED


def test_parent_is_preserved_without_mutation():
    result = generate_scenarios(request(parent_scenario_id="P1"))
    assert all(candidate.parent_scenario_id == "P1" for candidate in result.candidates)


def test_policy_is_versioned():
    assert policy().policy_version == "o4-v1"


def test_unsupported_generation_mode_rejected():
    with pytest.raises(ValidationError):
        GenerationPolicy(policy_version="o4-v1", mode="HEURISTIC")
