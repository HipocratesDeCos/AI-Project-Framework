"""F5.7 — explicit compatibility matrices and immutable catalog preflight."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest
from pydantic import BaseModel, Field

from eios.capability_catalog import (
    CapabilityCatalog, CapabilityCatalogError, CapabilityRelease,
    KERNEL_API_VERSION, INPUT_CONTRACT_API_VERSION, bind_catalog_plan,
)
from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
    InputContractError,
)
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)


class SalesQuote(BaseModel):
    company_id: str
    customer_id: str
    offered_price: Decimal = Field(ge=0)


class PurchaseDraft(BaseModel):
    decision_id: str
    scenario_id: str
    sku: str
    quantity: int = Field(gt=0)


def make_case(domain="SALES", version="v1", release="1.0.0"):
    cls = SalesQuote if domain == "SALES" else PurchaseDraft
    cap = "SALES_ANALYSIS" if domain == "SALES" else "PURCHASE_ANALYSIS"
    payload = (
        SalesQuote(company_id=domain, customer_id="CLIENT-SYNTH", offered_price=Decimal("15"))
        if domain == "SALES"
        else PurchaseDraft(decision_id="D-1", scenario_id="BASE", sku="SKU-SYNTH", quantity=2)
    )
    context = KernelContext(
        project_id=domain, decision_id="D-1", scenario_id="BASE",
        rules_version="R-1", parameters_version="P-1", data_snapshot_id="S-1",
    )
    operation = KernelOperation(
        decision_id=context.decision_id, scenario_id=context.scenario_id, payload=payload,
    )
    plan = KernelPlan(capabilities=(cap,), policy_version="POLICY-1")
    spec = CapabilityInputSpec(
        project_id=domain, capability=cap, schema_id="schema.example",
        schema_version=version, payload_type=cls,
    )
    envelope = CapabilityInputEnvelope(
        **{name: getattr(context, name) for name in KernelContext.model_fields},
        capability=cap, schema_id="schema.example", schema_version=version, payload=payload,
    )
    calls = []
    def producer(typed, supplied_context):
        assert type(typed) is cls and supplied_context.project_id == domain
        calls.append(cap)
        return KernelCapabilityResult(
            capability=cap, status=KernelCapabilityStatus.COMPLETED,
            result_available=True,
        )
    binding = CapabilityInputBinding(spec=spec, envelope=envelope, invoker=producer)
    registered = CapabilityRelease(
        project_id=domain, capability=cap, release_version=release,
        schema_id="schema.example", compatible_schema_versions=("v1", "v1.1"),
        payload_type=cls, policy_version=plan.policy_version,
    )
    catalog = CapabilityCatalog(
        project_id=domain, catalog_version="1.0.0", releases=(registered,),
    )
    return catalog, {cap: release}, operation, context, plan, {cap: binding}, calls


@pytest.mark.parametrize("domain", ("SALES", "PURCHASES"))
def test_catalog_uses_exact_release_and_explicit_allowed_schemas(domain):
    catalog, selected, operation, context, plan, bindings, called = make_case(domain)
    invokers = bind_catalog_plan(
        catalog=catalog, requested_releases=selected,
        operation=operation, context=context, plan=plan, bindings=bindings,
    )
    assert isinstance(invokers, MappingProxyType)
    outcome = execute_kernel(operation, context, plan, invokers)
    assert called == list(plan.capabilities)
    assert outcome.status == KernelStatus.COMPLETED  # technical execution only
    assert outcome.decision_authority is False
    assert outcome.operational_path == "FORBIDDEN"
    assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    with pytest.raises(TypeError):
        invokers["EXTRA"] = None


def test_explicit_schema_compatibility_can_allow_minor_schema_without_semver_inference():
    catalog, selections, operation, context, plan, bindings, _ = make_case(version="v1.1")
    assert bind_catalog_plan(
        catalog=catalog, requested_releases=selections,
        operation=operation, context=context, plan=plan, bindings=bindings,
    )
    wrong = make_case(version="v2")
    with pytest.raises(CapabilityCatalogError, match="SCHEMA_VERSION_INCOMPATIBLE"):
        bind_catalog_plan(
            catalog=wrong[0], requested_releases=wrong[1],
            operation=wrong[2], context=wrong[3],
            plan=wrong[4], bindings=wrong[5],
        )


@pytest.mark.parametrize("bad_release", ("1.0.1", "2.0.0", "9.0.0"))
def test_newer_version_is_never_selected_automatically(bad_release):
    catalog, selected, operation, context, plan, bindings, called = make_case()
    with pytest.raises(CapabilityCatalogError, match="RELEASE_NOT_REGISTERED"):
        bind_catalog_plan(
            catalog=catalog,
            requested_releases={plan.capabilities[0]: bad_release},
            operation=operation, context=context, plan=plan, bindings=bindings,
        )
    assert called == []


@pytest.mark.parametrize("version", ("latest", "1.0", "v1", "01.0.0", "-1.0.0", "1.0.0.dev1"))
def test_no_implicit_ranges_or_loose_version_labels(version):
    catalog, selected, operation, context, plan, bindings, called = make_case()
    with pytest.raises(CapabilityCatalogError, match="INVALID_CATALOG_VERSION"):
        bind_catalog_plan(
            catalog=catalog, requested_releases={plan.capabilities[0]: version},
            operation=operation, context=context, plan=plan, bindings=bindings,
        )
    assert called == []


def test_multiple_release_versions_require_exact_selection():
    catalog, selection, op, ctx, plan, bindings, _ = make_case()
    entry = catalog.releases[0]
    legacy = replace(entry, release_version="0.9.0", compatible_schema_versions=("v0",))
    new_catalog = replace(catalog, releases=(legacy, entry))
    assert bind_catalog_plan(
        catalog=new_catalog, requested_releases=selection,
        operation=op, context=ctx, plan=plan, bindings=bindings,
    )
    with pytest.raises(CapabilityCatalogError, match="SCHEMA_VERSION_INCOMPATIBLE"):
        bind_catalog_plan(
            catalog=new_catalog, requested_releases={plan.capabilities[0]: "0.9.0"},
            operation=op, context=ctx, plan=plan, bindings=bindings,
        )


def test_disabled_release_rejected_prior_to_capability_execution():
    catalog, selected, operation, context, plan, bindings, called = make_case()
    disabled = replace(catalog.releases[0], enabled=False)
    with pytest.raises(CapabilityCatalogError, match="RELEASE_DISABLED"):
        bind_catalog_plan(
            catalog=replace(catalog, releases=(disabled,)), requested_releases=selected,
            operation=operation, context=context, plan=plan, bindings=bindings,
        )
    assert called == []


def test_catalog_cannot_mix_companies_or_duplicate_release_keys():
    catalog, _, _, _, _, _, _ = make_case()
    release = catalog.releases[0]
    with pytest.raises(CapabilityCatalogError, match="FOREIGN_PROJECT_IN_CATALOG"):
        CapabilityCatalog(
            project_id="FOREIGN", catalog_version="1.0.0",
            releases=(release,),
        )
    with pytest.raises(CapabilityCatalogError, match="DUPLICATE_CAPABILITY_RELEASE"):
        CapabilityCatalog(
            project_id=catalog.project_id, catalog_version="1.0.0",
            releases=(release, replace(release)),
        )
    with pytest.raises(CapabilityCatalogError, match="EMPTY_OR_MUTABLE"):
        CapabilityCatalog(project_id=catalog.project_id, catalog_version="1.0.0", releases=[])


@pytest.mark.parametrize("field,expected", (
    ("required_kernel_api", "KERNEL_API_INCOMPATIBLE"),
    ("required_input_contract_api", "INPUT_API_INCOMPATIBLE"),
    ("policy_version", "POLICY_VERSION_INCOMPATIBLE"),
))
def test_catalog_requires_explicit_kernel_input_and_policy_versions(field, expected):
    catalog, selected, operation, context, plan, bindings, called = make_case()
    modified = replace(catalog.releases[0], **{field: "9.9.9" if field != "policy_version" else "FOREIGN-POLICY"})
    with pytest.raises(CapabilityCatalogError, match=expected):
        bind_catalog_plan(
            catalog=replace(catalog, releases=(modified,)),
            requested_releases=selected, operation=operation, context=context,
            plan=plan, bindings=bindings,
        )
    assert called == []


def test_versions_are_explicit_pinned_api_not_inferred_from_wheel_names():
    assert KERNEL_API_VERSION == "0.1.0"
    assert INPUT_CONTRACT_API_VERSION == "0.1.0"
    catalog, *_ = make_case()
    assert catalog.releases[0].required_kernel_api == KERNEL_API_VERSION
    assert catalog.releases[0].required_input_contract_api == INPUT_CONTRACT_API_VERSION


@pytest.mark.parametrize("field,value", (
    ("schema_id", "alien.schema"),
    ("payload_type", PurchaseDraft),
    ("project_id", "FOREIGN"),
))
def test_release_schema_and_project_are_exact(field, value):
    catalog, selected, operation, context, plan, bindings, called = make_case()
    if field == "project_id":
        # The catalog itself refuses foreign-project entries.
        with pytest.raises(CapabilityCatalogError, match="FOREIGN_PROJECT_IN_CATALOG"):
            replace(catalog, releases=(replace(catalog.releases[0], project_id=value),))
    else:
        changed = replace(catalog.releases[0], **{field: value})
        with pytest.raises(CapabilityCatalogError, match="RELEASE_SCHEMA_INCOMPATIBLE"):
            bind_catalog_plan(
                catalog=replace(catalog, releases=(changed,)),
                requested_releases=selected, operation=operation,
                context=context, plan=plan, bindings=bindings,
            )
    assert called == []


def test_cross_project_catalog_is_rejected_even_when_capability_names_match():
    catalog, selected, operation, context, plan, bindings, called = make_case()
    foreign_context = context.model_copy(update={"project_id": "FOREIGN"})
    with pytest.raises(CapabilityCatalogError, match="CATALOG_PROJECT_MISMATCH"):
        bind_catalog_plan(
            catalog=catalog, requested_releases=selected, operation=operation,
            context=foreign_context, plan=plan, bindings=bindings,
        )
    assert called == []


def test_schema_envelope_identity_remains_checked_by_f5_6_binder():
    catalog, selected, operation, context, plan, bindings, called = make_case()
    name = plan.capabilities[0]
    envelope = bindings[name].envelope.model_copy(update={"data_snapshot_id": "FOREIGN"})
    with pytest.raises(InputContractError, match="ENVELOPE_CONTEXT_MISMATCH"):
        bind_catalog_plan(
            catalog=catalog, requested_releases=selected, operation=operation,
            context=context, plan=plan,
            bindings={name: replace(bindings[name], envelope=envelope)},
        )
    assert called == []


@pytest.mark.parametrize("selected_keys,binding_keys,expected", (
    ((), ("SALES_ANALYSIS",), "RELEASE_SELECTION_SET_MISMATCH"),
    (("SALES_ANALYSIS", "EXTRA"), ("SALES_ANALYSIS",), "RELEASE_SELECTION_SET_MISMATCH"),
    (("SALES_ANALYSIS",), (), "CATALOG_BINDINGS_SET_MISMATCH"),
))
def test_no_inferred_or_missing_capabilities(selected_keys, binding_keys, expected):
    catalog, selected, operation, context, plan, bindings, called = make_case()
    choices = {key: "1.0.0" for key in selected_keys}
    bound = {key: bindings[plan.capabilities[0]] for key in binding_keys}
    with pytest.raises(CapabilityCatalogError, match=expected):
        bind_catalog_plan(
            catalog=catalog, requested_releases=choices,
            operation=operation, context=context, plan=plan, bindings=bound,
        )
    assert called == []


def test_invalid_second_capability_blocks_entire_plan_before_first_invoker():
    catalog, selected, operation, context, plan, bindings, called = make_case()
    original = catalog.releases[0]
    second = replace(original, capability="SECOND_CAPABILITY", release_version="2.0.0")
    second_spec = replace(bindings[plan.capabilities[0]].spec, capability="SECOND_CAPABILITY")
    second_envelope = bindings[plan.capabilities[0]].envelope.model_copy(
        update={"capability": "SECOND_CAPABILITY"},
    )
    plan = KernelPlan(capabilities=(original.capability, second.capability), policy_version=plan.policy_version)
    bindings = {**bindings, second.capability: CapabilityInputBinding(
        spec=second_spec, envelope=second_envelope, invoker=bindings[original.capability].invoker,
    )}
    with pytest.raises(CapabilityCatalogError, match="SCHEMA_VERSION_INCOMPATIBLE"):
        bind_catalog_plan(
            catalog=replace(catalog, releases=(original, replace(second, compatible_schema_versions=("v2",)))),
            requested_releases={original.capability: "1.0.0", second.capability: "2.0.0"},
            operation=operation, context=context, plan=plan, bindings=bindings,
        )
    assert called == []


@pytest.mark.parametrize("name", ("QTG", "O1"))
def test_protected_authority_boundaries_cannot_be_catalogued(name):
    _, _, _, _, _, _, _ = make_case()
    with pytest.raises(CapabilityCatalogError, match="FORBIDDEN_BOUNDARY_CAPABILITY"):
        CapabilityRelease(
            project_id="SALES", capability=name, release_version="1.0.0",
            schema_id="schema.example", compatible_schema_versions=("v1",),
            payload_type=SalesQuote, policy_version="POLICY-1",
        )


@pytest.mark.parametrize("schemas", ((), ("v1", "v1"), ["v1"], ("v1", None)))
def test_ambiguous_or_mutable_schema_version_allowlists_rejected(schemas):
    with pytest.raises(CapabilityCatalogError, match="INVALID|DUPLICATE"):
        CapabilityRelease(
            project_id="SALES", capability="SALES_ANALYSIS", release_version="1.0.0",
            schema_id="schema.example", compatible_schema_versions=schemas,
            payload_type=SalesQuote, policy_version="POLICY-1",
        )


def test_catalog_snapshot_is_immutable_not_a_hidden_mutable_registry():
    catalog, _, _, _, _, _, _ = make_case()
    with pytest.raises(FrozenInstanceError):
        catalog.catalog_version = "999.0.0"
    with pytest.raises(FrozenInstanceError):
        catalog.releases[0].enabled = False
