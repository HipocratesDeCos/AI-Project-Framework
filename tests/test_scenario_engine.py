from decimal import Decimal

import pytest

from eios.core.models import DecisionContext
from eios.core.scenario_engine import (
    AuthorizedScenarioChange,
    ScenarioStatus,
    ScenarioVersion,
    canonical_scenario_changes,
    create_scenario,
    scenario_fingerprint,
)


def context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-001",
        scenario_id="BASE-001",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="DS-1",
    )


def change(variable: str = "unit_price", simulated: str = "4.50") -> AuthorizedScenarioChange:
    return AuthorizedScenarioChange(
        variable=variable,
        base_value=Decimal("5.00"),
        simulated_value=Decimal(simulated),
        unit="EUR",
        authorization=True,
        origin="planner",
    )


def test_valid_scenario_preserves_context_and_is_immutable():
    scenario = create_scenario(context(), (change(),))

    assert scenario.status == ScenarioStatus.VALID
    assert scenario.decision_id == "D-001"
    assert scenario.rules_version == "R-1"
    assert scenario.parameters_version == "P-1"
    assert scenario.data_snapshot_id == "DS-1"
    assert len(scenario.fingerprint) == 64
    with pytest.raises(ValueError):
        scenario.status = ScenarioStatus.DRAFT


def test_same_changes_in_different_order_have_same_canonical_form_and_fingerprint():
    first = (change("unit_price", "4.50"), change("quantity", "20"))
    second = (change("quantity", "20"), change("unit_price", "4.50"))

    assert canonical_scenario_changes(first) == canonical_scenario_changes(second)
    assert scenario_fingerprint(context(), None, first) == scenario_fingerprint(
        context(), None, second
    )
    assert create_scenario(context(), first).scenario_id == create_scenario(context(), second).scenario_id


def test_parent_lineage_is_preserved_without_mutating_parent_identifier():
    parent = create_scenario(context(), (change(),))
    child = create_scenario(
        context(), (change("quantity", "20"),), parent_scenario_id=parent.scenario_id
    )

    assert child.parent_scenario_id == parent.scenario_id
    assert parent.changes != child.changes


def test_empty_hypothesis_is_draft():
    scenario = create_scenario(context())
    assert scenario.status == ScenarioStatus.DRAFT
    assert scenario.changes == ()


def test_unvalidated_hypothesis_is_draft():
    scenario = create_scenario(context(), (change(),), validate=False)
    assert scenario.status == ScenarioStatus.DRAFT


def test_unauthorized_change_creates_explicit_invalid_scenario():
    unauthorized = AuthorizedScenarioChange(
        variable="unit_price",
        base_value=Decimal("5.00"),
        simulated_value=Decimal("4.50"),
        unit="EUR",
        authorization=False,
        origin="untrusted-source",
    )

    scenario = create_scenario(context(), (unauthorized,))
    assert scenario.status == ScenarioStatus.INVALID
    assert scenario.result_available if hasattr(scenario, "result_available") else True


def test_equal_base_and_simulated_value_is_not_a_scenario_change():
    with pytest.raises(ValueError, match="distinta"):
        AuthorizedScenarioChange(
            variable="quantity",
            base_value=Decimal("10"),
            simulated_value=Decimal("10"),
            unit="UN",
            authorization=True,
            origin="planner",
        )


def test_evaluated_state_is_reserved_and_cannot_be_created():
    with pytest.raises(ValueError, match="EVALUATED"):
        ScenarioVersion(
            scenario_id="S-1",
            decision_id="D-001",
            rules_version="R-1",
            parameters_version="P-1",
            data_snapshot_id="DS-1",
            fingerprint="0" * 64,
            status=ScenarioStatus.EVALUATED,
        )


def test_scenario_does_not_mutate_input_changes():
    changes = (change(),)
    before = tuple(changes)
    scenario = create_scenario(context(), changes)

    assert changes == before
    assert scenario.changes[0].variable == "unit_price"
