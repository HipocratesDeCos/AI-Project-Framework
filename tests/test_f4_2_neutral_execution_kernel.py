"""F4.2 — neutral kernel contracts and purchase-compatibility boundary.

A second synthetic *non-purchase* consumer uses the kernel without ever
building/importing PurchaseOperation or the EIOS procurement MVP pipeline.
"""
from decimal import Decimal

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from eios.kernel.execution import (
    KernelCapabilityResult,
    KernelCapabilityStatus,
    KernelContext,
    KernelExecutionError,
    KernelOperation,
    KernelOutcome,
    KernelPlan,
    KernelStatus,
    execute_kernel,
)


class SalesProposal(BaseModel):
    """Unrelated domain payload owned by the example client, not the kernel."""

    model_config = ConfigDict(extra="forbid")

    customer_ref: str
    service: str
    amount: Decimal = Field(ge=0)
    assumptions: list[str]


def context(project_id="PROJECT-SALES", decision_id="SALE-1", scenario_id="QUOTE-1"):
    return KernelContext(
        project_id=project_id,
        decision_id=decision_id,
        scenario_id=scenario_id,
        rules_version="RULES-2026",
        parameters_version="PARAMS-3",
        data_snapshot_id="SYNTH-SALES-1",
    )


def operation(decision_id="SALE-1", scenario_id="QUOTE-1"):
    return KernelOperation(
        decision_id=decision_id,
        scenario_id=scenario_id,
        payload=SalesProposal(
            customer_ref="CLIENT-01",
            service="subscription",
            amount=Decimal("120.00"),
            assumptions=["synthesized"],
        ),
    )


def ok(name, trace=None):
    return KernelCapabilityResult(
        capability=name,
        status=KernelCapabilityStatus.COMPLETED,
        result_available=True,
        trace_references=(trace or f"synthetic-{name}",),
    )


def test_second_business_domain_executes_without_purchase_operation():
    received = []
    def price_check(sales, versions):
        assert type(sales) is SalesProposal
        received.append((
            versions.project_id,
            versions.rules_version,
            versions.parameters_version,
            sales.customer_ref,
            sales.amount,
        ))
        return ok("CHECK_QUOTE_LIMIT")

    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=("CHECK_QUOTE_LIMIT",), policy_version="POLICY-SALES"),
        {"CHECK_QUOTE_LIMIT": price_check},
    )
    assert out.status == KernelStatus.COMPLETED
    assert out.project_id == "PROJECT-SALES"
    assert out.decision_id == "SALE-1"
    assert out.scenario_id == "QUOTE-1"
    assert out.policy_version == "POLICY-SALES"
    assert [c.capability for c in out.capability_results] == ["CHECK_QUOTE_LIMIT"]
    assert received == [
        ("PROJECT-SALES", "RULES-2026", "PARAMS-3", "CLIENT-01", Decimal("120.00")),
    ]
    assert out.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    assert out.operational_path == "FORBIDDEN"
    assert out.decision_authority is False
    assert not hasattr(out, "recommendation")
    assert not hasattr(out, "approved")
    assert not hasattr(out, "business_decision")


@pytest.mark.parametrize("field", ["decision_id", "scenario_id"])
def test_mismatched_identity_rejected_before_any_invocation(field):
    observed = []
    bad = operation(**{field: "MISMATCH"})
    with pytest.raises(KernelExecutionError, match=field):
        execute_kernel(
            bad, context(),
            KernelPlan(capabilities=("CHECK_QUOTE_LIMIT",), policy_version="P-1"),
            {"CHECK_QUOTE_LIMIT": lambda *_: (observed.append("CALLED") or ok("CHECK_QUOTE_LIMIT"))},
        )
    assert observed == []


def test_explicit_order_and_preflight_missing_invoker():
    observed = []
    plan = KernelPlan(
        capabilities=("CHECK_TERM", "CHECK_MARGIN"), policy_version="P-1"
    )
    out = execute_kernel(
        operation(), context(), plan,
        {"CHECK_TERM": lambda *_: (observed.append("CHECK_TERM") or ok("CHECK_TERM"))},
    )
    assert out.status == KernelStatus.BLOCKED
    assert out.unresolved_items == ("CHECK_MARGIN",)
    assert observed == []
    full = execute_kernel(
        operation(), context(), plan,
        {
            "CHECK_MARGIN": lambda *_: (observed.append("CHECK_MARGIN") or ok("CHECK_MARGIN")),
            "CHECK_TERM": lambda *_: (observed.append("CHECK_TERM") or ok("CHECK_TERM")),
        },
    )
    assert full.status == KernelStatus.COMPLETED
    assert observed == ["CHECK_TERM", "CHECK_MARGIN"]


@pytest.mark.parametrize("capability", ["O1", "QTG"])
def test_authority_sensitive_capabilities_are_never_run_as_generic_invokers(capability):
    observed = []
    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=(capability, "CHECK_MARGIN"), policy_version="P-1"),
        {
            capability: lambda *_: (observed.append(capability) or ok(capability)),
            "CHECK_MARGIN": lambda *_: (observed.append("CHECK_MARGIN") or ok("CHECK_MARGIN")),
        },
    )
    assert out.status == KernelStatus.BLOCKED
    assert out.unresolved_items == (f"{capability}:FORBIDDEN_BOUNDARY_CAPABILITY",)
    assert observed == []


def test_non_callable_rejected_as_a_preflight_error():
    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=("CHECK_MARGIN",), policy_version="P-1"),
        {"CHECK_MARGIN": object()},
    )
    assert out.status == KernelStatus.BLOCKED
    assert out.unresolved_items == ("CHECK_MARGIN:INVALID_INVOKER",)


def test_mutating_one_invoker_cannot_mutate_caller_or_subsequent_invoker():
    request = operation()
    original_context = context()
    before = request.payload.model_dump(mode="python")
    observed = []
    def first(value, execution_context):
        value.assumptions.append("MUTATED")
        value.amount = Decimal("9999")
        return ok("FIRST")
    def second(value, execution_context):
        observed.append((
            value.amount, tuple(value.assumptions),
            execution_context.project_id, execution_context.data_snapshot_id,
        ))
        return ok("SECOND")

    out = execute_kernel(
        request, original_context,
        KernelPlan(capabilities=("FIRST", "SECOND"), policy_version="P-1"),
        {"FIRST": first, "SECOND": second},
    )
    assert out.status == KernelStatus.COMPLETED
    assert observed == [(Decimal("120"), ("synthesized",), "PROJECT-SALES", "SYNTH-SALES-1")]
    assert request.payload.model_dump(mode="python") == before


def test_catalog_frozen_once_before_first_invoker():
    catalog = {}
    def first(*_):
        catalog["SECOND"] = lambda *_: ok("WRONG")
        return ok("FIRST")
    catalog.update({
        "FIRST": first,
        "SECOND": lambda *_: ok("SECOND"),
    })
    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=("FIRST", "SECOND"), policy_version="P-1"),
        catalog,
    )
    assert out.status == KernelStatus.COMPLETED
    assert [item.capability for item in out.capability_results] == ["FIRST", "SECOND"]


def test_exception_and_wrong_identity_fail_without_business_recommendation():
    for invoker in (
        lambda *_: 1 / 0,
        lambda *_: ok("OTHER"),
        lambda *_: {"price": 100},
        lambda *_: KernelCapabilityResult(
            capability="CHECK", status=KernelCapabilityStatus.COMPLETED,
            result_available=False,
        ),
    ):
        out = execute_kernel(
            operation(), context(),
            KernelPlan(capabilities=("CHECK",), policy_version="P-1"),
            {"CHECK": invoker},
        )
        assert out.status == KernelStatus.FAILED
        assert out.failure_reason.startswith("CHECK:")
        assert out.decision_authority is False
        assert out.operational_path == "FORBIDDEN"


def test_failure_partial_and_unresolved_are_not_a_completed_decision():
    incomplete = KernelCapabilityResult(
        capability="CHECK",
        status=KernelCapabilityStatus.NOT_EVALUABLE,
        result_available=False,
        unresolved_items=("PROOF_MISSING",),
    )
    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=("CHECK",), policy_version="P-1"),
        {"CHECK": lambda *_: incomplete},
    )
    assert out.status == KernelStatus.PARTIALLY_COMPLETED
    assert out.unresolved_items == ("PROOF_MISSING",)
    assert out.decision_authority is False
    assert out.operational_path == "FORBIDDEN"


def test_failed_capability_preserves_reason_and_does_not_suppress_trace():
    expected = KernelCapabilityResult(
        capability="CHECK",
        status=KernelCapabilityStatus.FAILED,
        result_available=False,
        failure_reason="synthetic upstream timeout",
    )
    out = execute_kernel(
        operation(), context(),
        KernelPlan(capabilities=("CHECK",), policy_version="P-1"),
        {"CHECK": lambda *_: expected},
    )
    assert out.status == KernelStatus.FAILED
    assert out.failure_reason == "CHECK: synthetic upstream timeout"
    assert out.capability_results == (expected,)


def test_independent_projects_do_not_share_operation_payload_or_context():
    seen = []
    def record(value, execution_context):
        seen.append((execution_context.project_id, value.customer_ref))
        return ok("CHECK")
    for project in ("PROJECT-A", "PROJECT-B"):
        out = execute_kernel(
            operation(), context(project_id=project),
            KernelPlan(capabilities=("CHECK",), policy_version="P-1"),
            {"CHECK": record},
        )
        assert out.project_id == project
        assert out.decision_authority is False
    assert seen == [("PROJECT-A", "CLIENT-01"), ("PROJECT-B", "CLIENT-01")]


def test_plain_dict_payload_is_not_treated_as_valid_domain_contract():
    with pytest.raises(ValidationError):
        KernelOperation(
            decision_id="S-1", scenario_id="Q-1",
            payload={"amount": "100"},
        )


def test_malformed_plan_or_spoofed_authority_is_rejected():
    with pytest.raises(ValidationError):
        KernelPlan(capabilities=("CHECK", "CHECK"), policy_version="P")
    with pytest.raises(ValidationError):
        KernelPlan(capabilities=(" CHECK",), policy_version="P")
    with pytest.raises(ValidationError):
        KernelOutcome(
            status=KernelStatus.COMPLETED,
            project_id="S", decision_id="D", scenario_id="Q",
            policy_version="P", decision_authority=True,
        )
    with pytest.raises(ValidationError):
        KernelOutcome(
            status=KernelStatus.COMPLETED,
            project_id="S", decision_id="D", scenario_id="Q",
            policy_version="P", operational_path="ALLOWED",
        )


def test_kernel_does_not_statically_depend_on_purchase_or_company_packages():
    from pathlib import Path
    import ast
    path = Path(__file__).resolve().parents[1] / "eios/kernel/execution.py"
    parsed = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for statement in ast.walk(parsed):
        if isinstance(statement, ast.Import):
            modules.extend(alias.name for alias in statement.names)
        if isinstance(statement, ast.ImportFrom):
            modules.append(statement.module or "")
    assert not any(
        module.startswith(("eios.core", "eios.company", "eios.pricing", "eios.rules", "eios.frontend"))
        for module in modules
    )
