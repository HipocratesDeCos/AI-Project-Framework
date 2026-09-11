from decimal import Decimal
from types import SimpleNamespace

import eios.rules.execution_adapter as adapter
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.rules.orchestrator import StockExcessRuleInputs


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-ADAPTER",
        scenario_id="S-ADAPTER",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-ADAPTER",
        scenario_id="S-ADAPTER",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def test_domain_invoker_snapshots_bundles_and_returns_c0_capability(monkeypatch):
    source = {"values": [1]}
    bundle = StockExcessRuleInputs(source, source)
    observed = {}

    def fake_run_domain_rules(**kwargs):
        observed["stock_excess"] = kwargs["stock_excess"]
        observed["base_result"] = kwargs["base_result"]
        return SimpleNamespace(
            c0_capability=CapabilityExecution(
                capability="C0",
                status=O1ExecutionStatus.COMPLETED,
                result_available=True,
                trace_references=("trace-1",),
            )
        )

    monkeypatch.setattr(adapter, "run_domain_rules", fake_run_domain_rules)
    invoker = adapter.build_domain_rules_c0_invoker(
        base_result="COMPRAR",
        stock_excess=bundle,
    )
    source["values"].append(2)

    capability = invoker(_purchase(), _context())

    assert observed["stock_excess"].excess["values"] == [1]
    assert observed["base_result"] == "COMPRAR"
    assert capability.capability == "C0"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True


def test_domain_invoker_is_compatible_with_real_rules_engine_without_bundles():
    invoker = adapter.build_domain_rules_c0_invoker(base_result="NEGOCIAR")

    capability = invoker(_purchase(), _context())

    assert capability.capability == "C0"
    assert capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert capability.result_available is False
    assert capability.unresolved_items == ("C0_NO_ASSESSMENTS",)
