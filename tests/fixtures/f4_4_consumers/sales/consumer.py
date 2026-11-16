"""Standalone consumer B: sales proposal adapter, independent of purchasing.

Synthetic data and technical outcomes only: this program does not decide
whether to accept a client offer, price, payment date or discount.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import hashlib
from importlib import metadata, util
import json
from pathlib import Path
import sys

from pydantic import BaseModel, Field
import eios.kernel.execution as kernel_module
import eios.parameters.center as parameters_module
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext, KernelExecutionError,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)
from eios.parameters.center import (
    ChangeRequest, Configuration, ParameterConfigurationCenter,
    ParameterConfigurationError, ParameterDefinition,
)

PROJECT_ID = "F4_4_SALES"
POLICY = "sales-policy-v7"
CUTOFF = datetime(2026, 1, 1, tzinfo=timezone.utc)


class SalesOffer(BaseModel):
    company_id: str
    customer_id: str
    product_id: str
    offered_price: Decimal = Field(ge=0)
    payment_days: int = Field(ge=0)


class SalesCatalogue:
    def get_parameter(self, parameter_id: str):
        return ParameterDefinition("SALES-TERMS") if parameter_id == "SALES-TERMS" else None


class SalesAuthorization:
    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool:
        return False


class SalesReadOnlyRepository:
    def get_at(self, company_id: str, parameter_id: str, effective_at: datetime):
        if company_id != PROJECT_ID or parameter_id != "SALES-TERMS":
            return None
        return Configuration(
            configuration_id=30, parameter_id=parameter_id, company_id=company_id,
            value="30", value_type="int", unit="days",
            valid_from=CUTOFF, valid_to=None, created_at=CUTOFF, updated_at=CUTOFF,
        )


def execute_offer(offer, context, plan, invokers):
    # Explicit adapter gate; the kernel does not authenticate the company.
    if offer.company_id != context.project_id:
        raise ValueError("PROJECT_SCOPE_MISMATCH")
    return execute_kernel(
        KernelOperation(
            decision_id=context.decision_id, scenario_id=context.scenario_id,
            payload=offer,
        ),
        context, plan, invokers,
    )


def main():
    assert metadata.version("eios-kernel") == "0.1.0"
    assert util.find_spec("eios.core") is None
    assert util.find_spec("eios.company_local_finance_version_source") is None
    assert util.find_spec("eios.parameters.local_finance_version_source") is None
    assert util.find_spec("openpyxl") is None
    assert "eios.core" not in sys.modules

    center = ParameterConfigurationCenter(
        SalesCatalogue(), SalesAuthorization(), SalesReadOnlyRepository(),
    )
    terms = center.get_configuration_at(PROJECT_ID, "SALES-TERMS", CUTOFF)
    assert terms is not None and terms.value == "30"
    assert center.get_configuration_at("F4_4_PURCHASING", "SALES-TERMS", CUTOFF) is None
    try:
        center.apply_change(ChangeRequest(
            company_id=PROJECT_ID, parameter_id="SALES-TERMS", value="180",
            valid_from=CUTOFF, valid_to=None, actor="not-authorized", reason="test",
        ))
    except ParameterConfigurationError as exc:
        assert exc.code == "UNAUTHORIZED_CHANGE"
    else:
        raise AssertionError("Centre permitted an unauthorized write")

    offer = SalesOffer(
        company_id=PROJECT_ID, customer_id="SYNTH-CLIENT-1",
        product_id="SYNTH-PRODUCT-2", offered_price=Decimal("24.90"),
        payment_days=30,
    )
    context = KernelContext(
        project_id=PROJECT_ID, decision_id="SALE-88", scenario_id="CUSTOMER-A",
        rules_version="sales-rules-9", parameters_version="sales-params-7",
        data_snapshot_id="SYNTHETIC-SALES-SNAPSHOT",
    )
    plan = KernelPlan(
        capabilities=("SALES_FIELDS", "SALES_DOCUMENTARY"),
        policy_version=POLICY,
    )
    calls = []

    def sales_fields(payload, supplied_context):
        assert isinstance(payload, SalesOffer)
        assert supplied_context.project_id == PROJECT_ID
        assert payload.payment_days == 30
        calls.append("SALES_FIELDS")
        payload.offered_price = Decimal("0")
        return KernelCapabilityResult(
            capability="SALES_FIELDS", status=KernelCapabilityStatus.COMPLETED,
            result_available=True, trace_references=("synthetic:sales-fields",),
        )

    def sales_documentary(payload, supplied_context):
        assert payload.offered_price == Decimal("24.90")
        assert supplied_context.parameters_version == "sales-params-7"
        calls.append("SALES_DOCUMENTARY")
        return KernelCapabilityResult(
            capability="SALES_DOCUMENTARY",
            status=KernelCapabilityStatus.PARTIALLY_COMPLETED,
            result_available=True,
            unresolved_items=("CLIENT_EVIDENCE_NOT_PROVIDED",),
            trace_references=("synthetic:sales-docs",),
        )

    invokers = {"SALES_FIELDS": sales_fields, "SALES_DOCUMENTARY": sales_documentary}
    result = execute_offer(offer, context, plan, invokers)
    assert calls == ["SALES_FIELDS", "SALES_DOCUMENTARY"]
    assert offer.offered_price == Decimal("24.90")
    assert result.status == KernelStatus.PARTIALLY_COMPLETED
    assert result.unresolved_items == ("CLIENT_EVIDENCE_NOT_PROVIDED",)
    assert result.policy_version == POLICY and result.project_id == PROJECT_ID
    assert result.decision_authority is False and result.operational_path == "FORBIDDEN"
    assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

    baseline_calls = len(calls)
    try:
        execute_offer(
            offer.model_copy(update={"company_id": "F4_4_PURCHASING"}),
            context, plan, invokers,
        )
    except ValueError as exc:
        assert str(exc) == "PROJECT_SCOPE_MISMATCH"
    else:
        raise AssertionError("Cross-project sales offer was not rejected")
    assert len(calls) == baseline_calls
    try:
        execute_kernel(
            KernelOperation(decision_id="SALE-88", scenario_id="CUSTOMER-A", payload=offer),
            context.model_copy(update={"scenario_id": "FOREIGN-SCENARIO"}),
            plan, invokers,
        )
    except KernelExecutionError:
        pass
    else:
        raise AssertionError("Mismatched scenario_id was not rejected")
    assert len(calls) == baseline_calls
    for reserved in ("QTG", "O1"):
        blocked = execute_offer(
            offer, context,
            KernelPlan(capabilities=(reserved,), policy_version=POLICY),
            {reserved: sales_fields},
        )
        assert blocked.status == KernelStatus.BLOCKED
    assert len(calls) == baseline_calls
    missing = execute_offer(
        offer, context,
        KernelPlan(capabilities=("UNKNOWN_CAPABILITY",), policy_version=POLICY),
        {},
    )
    assert missing.status == KernelStatus.BLOCKED

    print(json.dumps({
        "consumer": "sales",
        "project_id": PROJECT_ID,
        "policy": POLICY,
        "kernel_version": metadata.version("eios-kernel"),
        "kernel_sha256": hashlib.sha256(Path(kernel_module.__file__).read_bytes()).hexdigest(),
        "parameters_sha256": hashlib.sha256(Path(parameters_module.__file__).read_bytes()).hexdigest(),
        "main_status": result.status.value,
        "parameter_value": terms.value,
        "scope_rejected": True,
        "identity_rejected": True,
        "reserved_boundaries_blocked": True,
        "unauthorized_write_rejected": True,
        "decision_authority": result.decision_authority,
        "operational_path": result.operational_path,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
