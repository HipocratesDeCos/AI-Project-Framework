"""F5.6: explicit neutral input contracts for purchase and independent sales."""
from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType

import pytest
from pydantic import BaseModel, Field, ValidationError

from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
    InputContractError, bind_capability_inputs,
)
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)


class PurchaseInput(BaseModel):
    decision_id: str
    scenario_id: str
    sku: str
    quantity: int = Field(gt=0)


class SalesInput(BaseModel):
    company_id: str
    customer_id: str
    offered_price: Decimal = Field(ge=0)


def _context(project="PURCHASES", decision="DEC-1"):
    return KernelContext(
        project_id=project, decision_id=decision, scenario_id="BASE",
        rules_version="RULES-1", parameters_version="PARAMS-1",
        data_snapshot_id="SNAP-1",
    )


def _build(
    payload=None, ctx=None, capability="TEST_CAPABILITY",
    schema_id="synthetic.contract", version="v1", model=PurchaseInput,
    invoker=None,
):
    context = ctx or _context()
    operation_payload = payload or PurchaseInput(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        sku="SYNTH", quantity=2,
    )
    operation = KernelOperation(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        payload=operation_payload,
    )
    plan = KernelPlan(capabilities=(capability,), policy_version="SYNTH-POLICY-1")
    spec = CapabilityInputSpec(
        project_id=context.project_id, capability=capability,
        schema_id=schema_id, schema_version=version, payload_type=model,
    )
    envelope = CapabilityInputEnvelope(
        **{attr: getattr(context, attr) for attr in KernelContext.model_fields},
        capability=capability, schema_id=schema_id, schema_version=version,
        payload=operation_payload,
    )
    if invoker is None:
        def invoker(typed, context):
            assert type(typed) is model
            return KernelCapabilityResult(
                capability=capability, status=KernelCapabilityStatus.COMPLETED,
                result_available=True,
            )
    return operation, context, plan, CapabilityInputBinding(
        spec=spec, envelope=envelope, invoker=invoker,
    )


def test_one_neutral_contract_supports_purchases_without_changing_kernel():
    operation, ctx, plan, binding = _build()
    bound = bind_capability_inputs(
        operation=operation, context=ctx, plan=plan,
        bindings={"TEST_CAPABILITY": binding},
    )
    assert isinstance(bound, MappingProxyType)
    result = execute_kernel(operation, ctx, plan, bound)
    assert result.status == KernelStatus.COMPLETED
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    with pytest.raises(TypeError):
        bound["EXTRA"] = lambda *_: None


def test_same_contract_api_supports_an_independent_sales_model():
    calls = []
    context = _context("SALES", "SALE-88")
    sale = SalesInput(
        company_id="SALES", customer_id="SYNTH-CUSTOMER",
        offered_price=Decimal("12.50"),
    )

    def sales_invoker(payload, current):
        assert type(payload) is SalesInput
        assert current.project_id == "SALES"
        assert payload.company_id == current.project_id  # domain-owned scope check
        calls.append("SALES")
        payload.offered_price = Decimal("999")
        return KernelCapabilityResult(
            capability="SALES_VALIDATION", status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False, unresolved_items=("DOCUMENTARY_SALES_MISSING",),
        )

    operation, ctx, plan, binding = _build(
        payload=sale, ctx=context, capability="SALES_VALIDATION",
        schema_id="synthetic.sales.offer", version="v9",
        model=SalesInput, invoker=sales_invoker,
    )
    bound = bind_capability_inputs(
        operation=operation, context=ctx, plan=plan,
        bindings={"SALES_VALIDATION": binding},
    )
    outcome = execute_kernel(operation, ctx, plan, bound)
    assert calls == ["SALES"]
    assert sale.offered_price == Decimal("12.50")
    assert outcome.status == KernelStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("DOCUMENTARY_SALES_MISSING",)
    assert outcome.operational_path == "FORBIDDEN"


@pytest.mark.parametrize("field", tuple(KernelContext.model_fields))
def test_all_six_identity_and_version_dimensions_are_checked_before_execution(field):
    operation, ctx, plan, binding = _build()
    value = "FOREIGN-PROJECT" if field == "project_id" else "FOREIGN-" + field
    forged = binding.envelope.model_copy(update={field: value})
    with pytest.raises(InputContractError, match="PROJECT_SCOPE_MISMATCH|ENVELOPE_CONTEXT_MISMATCH"):
        bind_capability_inputs(
            operation=operation, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: CapabilityInputBinding(
                spec=binding.spec, envelope=forged, invoker=binding.invoker,
            )},
        )


@pytest.mark.parametrize("field", ("project_id", "capability", "schema_id", "schema_version"))
def test_spec_and_envelope_must_match_exactly(field):
    operation, ctx, plan, binding = _build()
    changed = binding.envelope.model_copy(update={field: "FOREIGN-" + field})
    with pytest.raises(InputContractError, match="SPEC_ENVELOPE_MISMATCH"):
        bind_capability_inputs(
            operation=operation, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: CapabilityInputBinding(
                spec=binding.spec, envelope=changed, invoker=binding.invoker,
            )},
        )


def test_undeclared_schema_and_payload_change_are_rejected_before_first_producer():
    first_calls = []
    operation, ctx, _, base = _build()
    plan = KernelPlan(capabilities=("FIRST", "SECOND"), policy_version="TEST")
    b1 = CapabilityInputBinding(
        spec=CapabilityInputSpec(
            project_id=ctx.project_id, capability="FIRST",
            schema_id="schema.purchase", schema_version="v1",
            payload_type=PurchaseInput,
        ),
        envelope=base.envelope.model_copy(
            update={"capability": "FIRST", "schema_id": "schema.purchase"}
        ),
        invoker=lambda *_: first_calls.append("CALLED"),
    )
    second = CapabilityInputBinding(
        spec=CapabilityInputSpec(
            project_id=ctx.project_id, capability="SECOND",
            schema_id="schema.purchase", schema_version="v2",
            payload_type=PurchaseInput,
        ),
        envelope=base.envelope.model_copy(
            update={"capability": "SECOND", "schema_id": "schema.purchase"}
        ),
        invoker=lambda *_: None,
    )
    with pytest.raises(InputContractError, match="schema_version"):
        bind_capability_inputs(
            operation=operation, context=ctx, plan=plan,
            bindings={"FIRST": b1, "SECOND": second},
        )
    assert first_calls == []


def test_exact_model_class_not_structural_duck_typing():
    operation, ctx, plan, binding = _build()
    forged_spec = CapabilityInputSpec(
        project_id=ctx.project_id, capability=plan.capabilities[0],
        schema_id=binding.spec.schema_id, schema_version=binding.spec.schema_version,
        payload_type=SalesInput,
    )
    with pytest.raises(InputContractError, match="INPUT_SCHEMA_TYPE_MISMATCH"):
        bind_capability_inputs(
            operation=operation, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: CapabilityInputBinding(
                spec=forged_spec, envelope=binding.envelope,
                invoker=binding.invoker,
            )},
        )


def test_payload_internal_identity_checked_when_present():
    operation, ctx, plan, binding = _build()
    payload = operation.payload.model_copy(update={"scenario_id": "FOREIGN"})
    forged_operation = operation.model_copy(update={"payload": payload})
    forged_env = binding.envelope.model_copy(update={"payload": payload})
    with pytest.raises(InputContractError, match="PAYLOAD_CONTEXT_MISMATCH:scenario_id"):
        bind_capability_inputs(
            operation=forged_operation, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: CapabilityInputBinding(
                spec=binding.spec, envelope=forged_env, invoker=binding.invoker,
            )},
        )


@pytest.mark.parametrize("field", tuple(KernelContext.model_fields))
def test_runtime_context_drift_fails_before_producer(field):
    calls = []
    op, context, plan, entry = _build(
        invoker=lambda *_: calls.append("CALLED"),
    )
    bound = bind_capability_inputs(
        operation=op, context=context, plan=plan,
        bindings={plan.capabilities[0]: entry},
    )
    current = context.model_copy(update={field: "MODIFIED"})
    with pytest.raises(InputContractError, match="CONTEXT_DRIFT"):
        bound[plan.capabilities[0]](op.payload, current)
    assert calls == []


def test_runtime_payload_drift_and_mutation_are_isolated():
    calls = []

    def mutate(value, ctx):
        calls.append(value.quantity)
        value.quantity = 600
        return KernelCapabilityResult(
            capability="TEST_CAPABILITY", status=KernelCapabilityStatus.COMPLETED,
            result_available=True,
        )

    op, context, plan, entry = _build(invoker=mutate)
    bound = bind_capability_inputs(
        operation=op, context=context, plan=plan,
        bindings={plan.capabilities[0]: entry},
    )
    inv = bound[plan.capabilities[0]]
    with pytest.raises(InputContractError, match="INPUT_PAYLOAD_DRIFT"):
        inv(op.payload.model_copy(update={"quantity": 8}), context)
    inv(op.payload, context)
    inv(op.payload, context)
    assert calls == [2, 2]
    assert op.payload.quantity == 2


def test_missing_unregistered_and_reserved_capabilities_fail_closed():
    operation, ctx, _, binding = _build()
    bad_plan = KernelPlan(capabilities=("ONE", "TWO"), policy_version="TEST")
    with pytest.raises(InputContractError, match="CAPABILITY_BINDING_SET_MISMATCH"):
        bind_capability_inputs(
            operation=operation, context=ctx, plan=bad_plan, bindings={},
        )
    for reserved in ("QTG", "O1"):
        reserved_plan = KernelPlan(capabilities=(reserved,), policy_version="TEST")
        with pytest.raises(InputContractError, match="FORBIDDEN_BOUNDARY_CAPABILITY"):
            bind_capability_inputs(
                operation=operation, context=ctx, plan=reserved_plan,
                bindings={reserved: binding},
            )
        with pytest.raises(InputContractError, match="FORBIDDEN_BOUNDARY_CAPABILITY"):
            CapabilityInputSpec(
                project_id=ctx.project_id, capability=reserved,
                schema_id="forbidden", schema_version="v1",
                payload_type=PurchaseInput,
            )


def test_forged_authority_and_provenance_do_not_pass_envelope_schema():
    _, _, _, entry = _build()
    data = entry.envelope.model_dump()
    with pytest.raises(ValidationError):
        CapabilityInputEnvelope(**{**data, "decision_authority": True})
    with pytest.raises(ValidationError):
        CapabilityInputEnvelope(**{**data, "provenance_status": "DOCUMENT_AUTHENTICATED"})


@pytest.mark.parametrize("invalid", (None, str, object, int))
def test_registration_needs_explicit_pydantic_model_class(invalid):
    with pytest.raises(InputContractError, match="INVALID_PAYLOAD_MODEL"):
        CapabilityInputSpec(
            project_id="PURCHASES", capability="PRICE",
            schema_id="schema-1", schema_version="v1", payload_type=invalid,
        )


def test_no_implicit_default_executor_and_no_project_inference():
    op, ctx, plan, binding = _build()
    with pytest.raises(InputContractError, match="INVALID_CAPABILITY_INVOKER"):
        bind_capability_inputs(
            operation=op, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: CapabilityInputBinding(
                spec=binding.spec, envelope=binding.envelope, invoker=None,
            )},
        )
    wrong = op.model_copy(update={"decision_id": "FOREIGN"})
    with pytest.raises(InputContractError, match="OPERATION_CONTEXT_MISMATCH:decision_id"):
        bind_capability_inputs(
            operation=wrong, context=ctx, plan=plan,
            bindings={plan.capabilities[0]: binding},
        )
