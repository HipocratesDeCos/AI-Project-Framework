from datetime import date
from decimal import Decimal

import pytest

import eios.vertical_orchestration as vertical
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    _complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable


def _context(**changes) -> DecisionContext:
    data = dict(
        decision_id="D-SC-QUARANTINE",
        scenario_id="BASE",
        rules_version="R1",
        parameters_version="P1",
        data_snapshot_id="SNAP1",
    )
    data.update(changes)
    return DecisionContext(**data)


def _purchase(**changes) -> PurchaseOperation:
    data = dict(
        decision_id="D-SC-QUARANTINE",
        scenario_id="BASE",
        article_id="A1",
        supplier_id="SUP1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 13),
    )
    data.update(changes)
    return PurchaseOperation(**data)


def _orchestration():
    preparation = prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(
            GenerationVariable(
                variable_id="qty",
                value_type="integer",
                base_value=0,
                domain=(1,),
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-Q-1"),
    )
    scenario_id = next(
        item.scenario_id
        for item in preparation.materialization.scenarios
        if item.status.value == "VALID"
    )
    return _complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=(
            AuthorizedScenarioAnalytics(
                scenario_id=scenario_id,
                assessments=({"assessment": scenario_id},),
                viability_result={"viability": scenario_id},
                trace_references=(f"TRACE-{scenario_id}",),
            ),
        ),
    )


def test_orchestration_invoker_rejects_runtime_context_drift():
    invoker = vertical._scenario_coordination_invoker_from_orchestration(
        _orchestration()
    )

    with pytest.raises(ValueError, match="DecisionContext runtime incoherente"):
        invoker(
            _purchase(),
            _context(parameters_version="P2"),
        )


def test_orchestration_invoker_rebuilds_support_from_runtime_purchase(monkeypatch):
    orchestration = _orchestration()
    original = vertical.build_o2_support_from_orchestration
    seen = {}

    def recording_bridge(*, purchase_operation, orchestration_result):
        seen["purchase"] = purchase_operation
        seen["orchestration"] = orchestration_result
        return original(
            purchase_operation=purchase_operation,
            orchestration_result=orchestration_result,
        )

    monkeypatch.setattr(
        vertical,
        "build_o2_support_from_orchestration",
        recording_bridge,
    )
    invoker = vertical._scenario_coordination_invoker_from_orchestration(orchestration)
    runtime_purchase = _purchase(quantity=Decimal("11"))

    capability = invoker(runtime_purchase, _context())

    assert seen["purchase"] == runtime_purchase
    assert seen["orchestration"] == orchestration
    assert capability.capability == "SCENARIO_COORDINATION"
