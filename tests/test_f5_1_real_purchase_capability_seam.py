"""F5.1 — Real PRICE/TCO business capabilities through the single neutral kernel.

Test integration of *existing closed engines*, not mock invokers, and do not
mistake their technical execution for enterprise provenance or authorization.
No production code, domain algorithm or capability contracts are changed.
"""
from datetime import date
from decimal import Decimal
import ast
from pathlib import Path

import pytest

from eios.core import execution_boundary as boundary
from eios.core.execution_boundary import BoundaryStatus
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.mvp_execution import run_mvp_execution
from eios.core.orchestration import O1ExecutionStatus
from eios.core.price_integration import build_provenanced_price_invoker
from eios.core.tco_integration import build_provenanced_tco_invoker
from eios.kernel.execution import KernelStatus
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput
from eios.pricing.sufficiency import SufficiencyObservation
from eios.tco.engine import calculate_tco
from eios.tco.models import CostComponent, TCOInput


ROOT = Path(__file__).resolve().parents[1]


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-F5-1",
        scenario_id="S-F5-1",
        rules_version="RULES-F5-1",
        parameters_version="PARAM-F5-1",
        data_snapshot_id="SYNTHETIC-SNAPSHOT-F5-1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-F5-1",
        scenario_id="S-F5-1",
        article_id="SYNTH-ARTICLE",
        supplier_id="SYNTH-SUPPLIER",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 10, 1),
    )


def _price_payload() -> PriceIntelligenceInput:
    return PriceIntelligenceInput(
        decision_context=_context(),
        purchase_operation=_purchase(),
        references=(),
        evidence_validations=(),
        normalization_basis=None,
        economic_basis_evidence=(),
        methodology_version="PRICE-F5-1",
    )


def _price_invoker():
    return build_provenanced_price_invoker(
        payload=_price_payload(),
        assessment_context=PriceIntelligenceAssessmentContext(
            sufficiency=SufficiencyObservation(),
        ),
    )


def _tco_payload(*, incomplete=False) -> TCOInput:
    if incomplete:
        return TCOInput(
            purchase_operation=_purchase(),
            attributable_costs=(
                CostComponent(
                    component="TRANSPORT", amount=None, currency="EUR",
                    applicability="APPLICABLE",
                    attribution_ref="SYNTHETIC-TRANSPORT",
                    rule_reference="RULE-TCO-TRANSPORT",
                ),
            ),
        )
    return TCOInput(purchase_operation=_purchase())


def test_two_closed_business_engines_share_one_real_neutral_execution_loop(monkeypatch):
    """One execution, two real producers; no duplicate business calculation."""
    actual_execute = boundary.execute_kernel
    observed = []

    def spy(operation, context, plan, invokers):
        observed.append((operation, context, plan, tuple(invokers)))
        outcome = actual_execute(operation, context, plan, invokers)
        assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
        assert outcome.decision_authority is False
        assert outcome.operational_path == "FORBIDDEN"
        return outcome

    monkeypatch.setattr(boundary, "execute_kernel", spy)
    actual_tco = calculate_tco(_tco_payload())
    assert actual_tco.complete is True
    assert actual_tco.value == Decimal("50")
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="PURCHASE-POLICY-F5-1",
        price_invoker=_price_invoker(),
        tco_invoker=build_provenanced_tco_invoker(payload=_tco_payload()),
    )

    assert len(observed) == 1
    operation, context, plan, invokers = observed[0]
    assert type(operation.payload) is PurchaseOperation
    assert operation.payload.supplier_id == "SYNTH-SUPPLIER"
    assert context.project_id == "EIOS_PURCHASES"
    assert context.parameters_version == "PARAM-F5-1"
    assert plan.capabilities == ("PRICE", "TCO")
    assert invokers == ("PRICE", "TCO")
    assert outcome.policy_version == "PURCHASE-POLICY-F5-1"
    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("PRICE_NOT_JUSTIFIABLE",)
    assert tuple((entry.capability, entry.status, entry.result_available)
                 for entry in outcome.capability_results) == (
        ("PRICE", O1ExecutionStatus.NOT_EVALUABLE, False),
        ("TCO", O1ExecutionStatus.COMPLETED, True),
    )


@pytest.mark.parametrize("changed", [
    {"quantity": Decimal("999")},
    {"supplier_id": "FOREIGN-SUPPLIER"},
    {"unit_price": Decimal("25")},
])
def test_price_provenance_mismatch_fails_closed_before_tco(changed):
    tco_calls = []
    real_tco_invoker = build_provenanced_tco_invoker(payload=_tco_payload())

    def tracked_tco(purchase, context):
        tco_calls.append("CALLED")
        return real_tco_invoker(purchase, context)

    outcome = run_mvp_execution(
        purchase=_purchase().model_copy(update=changed),
        context=_context(),
        policy_version="PURCHASE-POLICY-F5-1",
        price_invoker=_price_invoker(),
        tco_invoker=tracked_tco,
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert outcome.failure_reason.startswith("PRICE:")
    assert outcome.capability_results == ()
    assert tco_calls == []


@pytest.mark.parametrize("field", [
    "rules_version", "parameters_version", "data_snapshot_id",
])
def test_price_full_context_version_mismatch_fails_closed(field):
    tco_calls = []
    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context().model_copy(update={field: "FOREIGN-VERSION"}),
        policy_version="PURCHASE-POLICY-F5-1",
        price_invoker=_price_invoker(),
        tco_invoker=lambda *_: tco_calls.append("CALLED"),
    )
    assert outcome.status == BoundaryStatus.FAILED
    assert field in outcome.failure_reason
    assert tco_calls == []


def test_incomplete_tco_and_nonjustifiable_price_preserve_both_deficits():
    direct = calculate_tco(_tco_payload(incomplete=True))
    assert direct.value is None
    assert direct.unresolved_components == ("TRANSPORT",)

    outcome = run_mvp_execution(
        purchase=_purchase(),
        context=_context(),
        policy_version="PURCHASE-POLICY-F5-1",
        price_invoker=_price_invoker(),
        tco_invoker=build_provenanced_tco_invoker(
            payload=_tco_payload(incomplete=True),
        ),
    )
    assert outcome.status == BoundaryStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("PRICE_NOT_JUSTIFIABLE", "TRANSPORT")
    assert [c.status for c in outcome.capability_results] == [
        O1ExecutionStatus.NOT_EVALUABLE,
        O1ExecutionStatus.PARTIALLY_COMPLETED,
    ]
    assert [c.result_available for c in outcome.capability_results] == [
        False, False,
    ]


def test_selected_capabilities_are_vertical_integrations_not_kernel_dependencies():
    """Guard against silently packaging the purchase PRICE/TCO engines."""
    root = ROOT / "eios"
    for relative in (
        "kernel/execution.py",
        "core/price_integration.py",
        "core/tco_integration.py",
        "pricing/models.py",
        "tco/models.py",
    ):
        assert (root / relative).is_file()

    kernel = ast.parse((root / "kernel/execution.py").read_text(encoding="utf-8"))
    kernel_imports = [
        node.module for node in ast.walk(kernel)
        if isinstance(node, ast.ImportFrom)
    ] + [
        alias.name for node in ast.walk(kernel)
        if isinstance(node, ast.Import) for alias in node.names
    ]
    assert not any(name and name.startswith("eios.") for name in kernel_imports)

    for path in ("pricing/models.py", "tco/models.py"):
        tree = ast.parse((root / path).read_text(encoding="utf-8"))
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        assert "eios.core.models" in imports, (
            f"{path} changed dependencies: review before declaring it portable"
        )
