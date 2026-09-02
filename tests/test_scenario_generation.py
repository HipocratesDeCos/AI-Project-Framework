from copy import deepcopy

from eios.core.models import DecisionContext
from eios.core.scenario_generation import GenerationPolicy, GenerationStatus, GenerationVariable, generate_scenarios


def context() -> DecisionContext:
    return DecisionContext(decision_id="D1", scenario_id="S0", rules_version="R1", parameters_version="P1", data_snapshot_id="SN1")


def test_zero_variables_emits_single_base_candidate():
    result = generate_scenarios(context(), (), GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 1
    assert result.candidates[0].changes == ()


def test_empty_domain_is_empty_not_failure():
    variables = (GenerationVariable(variable_id="price", value_type="number", base_value=10, domain=()),)
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.EMPTY


def test_cartesian_cardinality_excludes_no_op_and_is_deterministic():
    variables = (
        GenerationVariable(variable_id="qty", value_type="integer", base_value=1, domain=(1, 2)),
        GenerationVariable(variable_id="price", value_type="number", base_value=10, domain=(10, 12)),
    )
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert len(result.candidates) == 3
    assert [tuple(change.variable for change in c.changes) for c in result.candidates] == [("qty",), ("price",), ("price", "qty")]


def test_max_variables_blocks_before_expansion():
    variables = tuple(GenerationVariable(variable_id=str(i), value_type="integer", base_value=0, domain=(1,)) for i in range(2))
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1", max_variables=1))
    assert result.status is GenerationStatus.BLOCKED


def test_max_cardinality_per_variable_blocks_before_expansion():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2, 3))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1", max_cardinality_per_variable=2))
    assert result.status is GenerationStatus.BLOCKED


def test_max_total_cardinality_blocks_before_expansion():
    variables = (
        GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2)),
        GenerationVariable(variable_id="b", value_type="integer", base_value=0, domain=(1, 2)),
    )
    result = generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1", max_total_cardinality=3))
    assert result.status is GenerationStatus.BLOCKED


def test_max_emitted_candidates_blocks_before_expansion():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1", max_emitted_candidates=1))
    assert result.status is GenerationStatus.BLOCKED


def test_depth_limit_blocks_derivation():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1", max_depth=1), parent_scenario_id="S0", depth=1)
    assert result.status is GenerationStatus.BLOCKED


def test_negative_depth_is_failed_with_cause():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"), depth=-1)
    assert result.status is GenerationStatus.FAILED
    assert result.reason


def test_missing_context_is_failed_with_cause():
    result = generate_scenarios(None, (), GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.FAILED
    assert result.reason


def test_runtime_space_error_is_not_evaluable():
    class ExplodingPolicy(GenerationPolicy):
        @property
        def max_total_cardinality(self):
            raise TypeError("cardinalidad indeterminable")

    policy = ExplodingPolicy(policy_version="O4-1")
    result = generate_scenarios(context(), (), policy)
    assert result.status is GenerationStatus.NOT_EVALUABLE
    assert result.reason


def test_generated_candidates_preserve_parent_and_increment_depth():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"), parent_scenario_id="S0", depth=1)
    assert result.status is GenerationStatus.GENERATED
    assert result.candidates[0].parent_scenario_id == "S0"
    assert result.candidates[0].depth == 2


def test_canonical_variable_order_is_independent_of_input_order():
    a = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    b = GenerationVariable(variable_id="b", value_type="integer", base_value=0, domain=(2,))
    policy = GenerationPolicy(policy_version="O4-1")
    assert generate_scenarios(context(), (a, b), policy) == generate_scenarios(context(), (b, a), policy)


def test_structural_exclusion_is_deterministic():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2), excluded_values=(2,))
    result = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"))
    assert result.status is GenerationStatus.GENERATED
    assert result.candidates[0].changes[0].simulated_value == 1


def test_inputs_are_not_mutated():
    variables = (GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1, 2)),)
    before = deepcopy(variables)
    generate_scenarios(context(), variables, GenerationPolicy(policy_version="O4-1"))
    assert variables == before


def test_identity_and_versioning_are_not_created_by_o4():
    variable = GenerationVariable(variable_id="a", value_type="integer", base_value=0, domain=(1,))
    candidate = generate_scenarios(context(), (variable,), GenerationPolicy(policy_version="O4-1"), parent_scenario_id="S0").candidates[0]
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
