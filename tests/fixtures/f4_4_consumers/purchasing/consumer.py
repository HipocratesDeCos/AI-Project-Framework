"""Standalone consumer A: synthetic purchasing adapter, never a real authorization.

This fixture is intentionally an independent program. It imports ONLY the
installed eios-kernel wheel, Pydantic and the Python standard library.
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

PROJECT_ID = "F4_4_PURCHASING"
POLICY = "purchase-policy-v1"
CUTOFF = datetime(2026, 1, 1, tzinfo=timezone.utc)


class PurchaseDraft(BaseModel):
    company_id: str
    sku: str
    supplier_id: str
    quantity: int = Field(gt=0)
    reference_price: Decimal = Field(ge=0)


class Catalogue:
    def get_parameter(self, parameter_id: str):
        return ParameterDefinition("BUY-RESERVE") if parameter_id == "BUY-RESERVE" else None


class DenyWrites:
    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool:
        return False


class LocalReadOnlyRepository:
    def get_at(self, company_id: str, parameter_id: str, effective_at: datetime):
        if company_id != PROJECT_ID or parameter_id != "BUY-RESERVE":
            return None
        return Configuration(
            configuration_id=10, parameter_id=parameter_id, company_id=company_id,
            value="5", value_type="int", unit="units",
            valid_from=CUTOFF, valid_to=None, created_at=CUTOFF, updated_at=CUTOFF,
        )


def execute_purchase(draft, context, plan, invokers):
    # Adapter responsibility: never mistake project_id for authenticated identity.
    if draft.company_id != context.project_id:
        raise ValueError("PROJECT_SCOPE_MISMATCH")
    return execute_kernel(
        KernelOperation(
            decision_id=context.decision_id, scenario_id=context.scenario_id,
            payload=draft,
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

    center = ParameterConfigurationCenter(Catalogue(), DenyWrites(), LocalReadOnlyRepository())
    reserve = center.get_configuration_at(PROJECT_ID, "BUY-RESERVE", CUTOFF)
    assert reserve is not None and reserve.value == "5"
    assert center.get_configuration_at("F4_4_SALES", "BUY-RESERVE", CUTOFF) is None
    try:
        center.apply_change(ChangeRequest(
            company_id=PROJECT_ID, parameter_id="BUY-RESERVE", value="999",
            valid_from=CUTOFF, valid_to=None, actor="not-authorized", reason="test",
        ))
    except ParameterConfigurationError as exc:
        assert exc.code == "UNAUTHORIZED_CHANGE"
    else:
        raise AssertionError("Centre permitted a write without authorization")

    draft = PurchaseDraft(
        company_id=PROJECT_ID, sku="SYNTH-SUBSTRATE", supplier_id="SYNTH-SUP-1",
        quantity=3, reference_price=Decimal("12.25"),
    )
    context = KernelContext(
        project_id=PROJECT_ID, decision_id="BUY-01", scenario_id="BASE",
        rules_version="buy-rules-1", parameters_version="buy-param-1",
        data_snapshot_id="SYNTHETIC-BUY-SNAPSHOT",
    )
    plan = KernelPlan(
        capabilities=("PURCHASE_FIELDS", "PURCHASE_TRACE"), policy_version=POLICY,
    )
    calls = []

    def purchase_fields(payload, supplied_context):
        assert isinstance(payload, PurchaseDraft)
        assert supplied_context.project_id == PROJECT_ID
        assert payload.reference_price == Decimal("12.25")
        calls.append("PURCHASE_FIELDS")
        payload.quantity = 777  # The next invoker must see an independent copy.
        return KernelCapabilityResult(
            capability="PURCHASE_FIELDS", status=KernelCapabilityStatus.COMPLETED,
            result_available=True, trace_references=("synthetic:buy-fields",),
        )

    def purchase_trace(payload, supplied_context):
        assert payload.quantity == 3
        assert supplied_context.parameters_version == "buy-param-1"
        calls.append("PURCHASE_TRACE")
        return KernelCapabilityResult(
            capability="PURCHASE_TRACE", status=KernelCapabilityStatus.COMPLETED,
            result_available=True, trace_references=("synthetic:buy-trace",),
        )

    invokers = {"PURCHASE_FIELDS": purchase_fields, "PURCHASE_TRACE": purchase_trace}
    result = execute_purchase(draft, context, plan, invokers)
    assert calls == ["PURCHASE_FIELDS", "PURCHASE_TRACE"]
    assert draft.quantity == 3 and result.status == KernelStatus.COMPLETED
    assert result.policy_version == POLICY and result.project_id == PROJECT_ID
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

    baseline_calls = len(calls)
    try:
        execute_purchase(
            draft.model_copy(update={"company_id": "F4_4_SALES"}),
            context, plan, invokers,
        )
    except ValueError as exc:
        assert str(exc) == "PROJECT_SCOPE_MISMATCH"
    else:
        raise AssertionError("Cross-project purchase was not rejected by the adapter")
    assert len(calls) == baseline_calls
    try:
        execute_kernel(
            KernelOperation(decision_id="BUY-01", scenario_id="BASE", payload=draft),
            context.model_copy(update={"decision_id": "FOREIGN-DECISION"}),
            plan, invokers,
        )
    except KernelExecutionError:
        pass
    else:
        raise AssertionError("Mismatched decision_id was not rejected by kernel")
    assert len(calls) == baseline_calls
    for reserved in ("QTG", "O1"):
        blocked = execute_purchase(
            draft, context,
            KernelPlan(capabilities=(reserved,), policy_version=POLICY),
            {reserved: purchase_fields},
        )
        assert blocked.status == KernelStatus.BLOCKED
    assert len(calls) == baseline_calls
    missing = execute_purchase(
        draft, context,
        KernelPlan(capabilities=("UNKNOWN_CAPABILITY",), policy_version=POLICY),
        {},
    )
    assert missing.status == KernelStatus.BLOCKED

    print(json.dumps({
        "consumer": "purchasing",
        "project_id": PROJECT_ID,
        "policy": POLICY,
        "kernel_version": metadata.version("eios-kernel"),
        "kernel_sha256": hashlib.sha256(Path(kernel_module.__file__).read_bytes()).hexdigest(),
        "parameters_sha256": hashlib.sha256(Path(parameters_module.__file__).read_bytes()).hexdigest(),
        "main_status": result.status.value,
        "parameter_value": reserve.value,
        "scope_rejected": True,
        "identity_rejected": True,
        "reserved_boundaries_blocked": True,
        "unauthorized_write_rejected": True,
        "decision_authority": result.decision_authority,
        "operational_path": result.operational_path,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
