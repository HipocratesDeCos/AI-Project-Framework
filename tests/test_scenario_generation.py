from copy import deepcopy

from eios.core.models import DecisionContext
from eios.core.scenario_generation import (
    GenerationPolicy,
    GenerationStatus,
    GenerationVariable,
    generate_scenarios,
)


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D1",
        scenario_id="S0",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SN1",
    )


def test_zero_variables_emits_single_base_candidate():
    result = generate_scenarios(context(), (), GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 1
    assert result.candidates[0].changes == ()


def test_empty_domain_is_empty_not_failure():
    variables = (GenerationVariable(variable_id="price", value_type="number", base_value=10, domain=()),)
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.EMPTY
    assert result.candidates == ()


def test_cartesian_cardinality_is_deterministic():
    variables = (
        GenerationVariable(variable_id="qty", value_type="integer", base_value=1, domain=(1, 2)),
        GenerationVariable(variable_id="price", value_type="number", base_value=10, domain=(10, 12)),
    )
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 4
    assert [tuple(c.changes) for c in result.candidates] == [
        (),
        (result.candidates[1].changes[0],),
        (result.candidates[2].changes[0],),
        (result.candidates[3].changes[0], result.candidates[3].changes[1]),
    ]


def test_limits_block_before_expansion():
    variables = (
        GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2)),
        GenerationVariable(variable_id="b", value_type="integer", base_value=0, domain=(1, 2)),
    )
    policy = GenerationPolicy(policy_version="O4-1", max_total_cardinality=3)
    result = generate_scenarios(context(), variables, policy)
    assert result.status is GenerationStatus.BLOCKED
    assert result.candidates == ()


def test_depth_limit_blocks_derivation():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    policy = GenerationPolicy(policy_version="O4-1", max_depth=1)
    result = generate_scenarios(context(), (variable,), policy, parent_scenario_id="S0", depth=1)
    assert result.status is GenerationStatus.BLOCKED


def test_canonical_variable_order_is_independent_of_input_order():
    a = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    b = GenerationVariable(variable_id="b", value_type="integer", base_value=0, domain=(2,))
    policy = GenerationPolicy(policy_version="O4-1")
    first = generate_scenarios(context(), (a, b), policy)
    second = generate_scenarios(context(), (b, a), policy)
    assert first == second


def test_structural_exclusion_is_deterministic():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2), excluded_values=(2,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 1
    assert result.candidates[0].changes[0].simulated_value == 1


def test_inputs_are_not_mutated():
    variables = (GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2)),)
    before = deepcopy(variables)
    generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert variables == before


def test_identity_and_versioning_are_not_created_by_o4():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"), parent_scenario_id="S0")
    candidate = result.candidates[0]
    assert not hasattr(candidate, "scenario_id")
    assert not hasattr(candidate, "fingerprint")


def test_invalid_type_is_rejected_without_silent_coercion():
    try:
        GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=("1",))
    except ValueError:
        return
    raise AssertionError("Se aceptó coerción silenciosa de tipo")


def test_policy_version_is_required():
    try:
        GenerationPolicy(policy_version="")
    except ValueError:
        return
    raise AssertionError("Se aceptó una policy_version vacía")
