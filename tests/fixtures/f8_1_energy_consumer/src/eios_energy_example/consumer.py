"""Synthetic energy-monitoring EIOS client; no operational authority.

Runs as an independently built wheel outside the EIOS checkout.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from importlib import metadata, util
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)
from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
)
from eios.capability_catalog import CapabilityCatalog, CapabilityRelease
from eios.catalog_governance import (
    AuthorizationGrant, CatalogChange, CatalogGovernanceError,
    bind_governed_plan, commit_catalog_change, load_governed_state,
)

PROJECT = "SYNTH_ENERGY_DOMAIN_4"
POLICY = "SYNTH_ENERGY_POLICY_V1"
SCHEMA = "energy.meter_observation"
CAPS = ("PEAK_DEMAND_OBSERVATION", "METER_SUPPORT_CHECK")


class MeterObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision_id: str
    scenario_id: str
    site_id: str
    meter_id: str
    demand_kw: Decimal = Field(ge=0)
    reference_limit_kw: Decimal = Field(gt=0)
    meter_document_verified: bool = False


def authorize_test_only(change, state, actions):
    assert change.project_id == PROJECT
    return AuthorizationGrant(
        project_id=PROJECT,
        actor_id="SYNTHETIC_ENERGY_TEST_APPROVER",
        authorization_ref="SYNTH_ENERGY_APPROVAL",
        authorization_policy="SYNTHETIC_TEST_ONLY",
        allowed_actions=actions,
    )


def reject(label, action, error_type=Exception):
    try:
        action()
    except error_type:
        return
    raise AssertionError("adversarial case unexpectedly accepted: " + label)


def run():
    for forbidden in ("eios.core", "eios.pricing", "eios.tco", "eios.company_app"):
        assert util.find_spec(forbidden) is None, forbidden
    expected = {
        "eios-kernel": "0.1.0",
        "eios-input-contracts": "0.1.0",
        "eios-capability-catalog": "0.1.0",
        "eios-catalog-governance": "0.1.0",
        "eios-energy-example": "0.1.0",
    }
    for name, version in expected.items():
        assert metadata.version(name) == version, name

    payload = MeterObservation(
        decision_id="ENERGY-SYNTH-001", scenario_id="SCENARIO-BASE",
        site_id="TEST-SITE-01", meter_id="METER-SYNTH-02",
        demand_kw=Decimal("89.5"), reference_limit_kw=Decimal("75"),
        meter_document_verified=False,
    )
    context = KernelContext(
        project_id=PROJECT, decision_id=payload.decision_id,
        scenario_id=payload.scenario_id, rules_version="ENERGY-R1",
        parameters_version="ENERGY-P1", data_snapshot_id="SYNTH-SNAPSHOT-1",
    )
    operation = KernelOperation(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        payload=payload,
    )
    plan = KernelPlan(capabilities=CAPS, policy_version=POLICY)
    calls = []

    def observe(record, ctx):
        calls.append("peak")
        assert ctx.project_id == PROJECT
        assert record.demand_kw == Decimal("89.5")
        assert record.reference_limit_kw == Decimal("75")
        record.demand_kw = Decimal("0")  # producer isolation attack
        return KernelCapabilityResult(
            capability=CAPS[0], status=KernelCapabilityStatus.COMPLETED,
            result_available=True, trace_references=("SYNTH_PEAK_OBSERVATION",),
        )

    def evidence(record, ctx):
        calls.append("support")
        assert record.demand_kw == Decimal("89.5")  # deep-copy isolation
        assert record.meter_document_verified is False
        return KernelCapabilityResult(
            capability=CAPS[1], status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False, unresolved_items=("METER_DOCUMENT_UNVERIFIED",),
        )

    producers = {CAPS[0]: observe, CAPS[1]: evidence}
    catalog = CapabilityCatalog(
        project_id=PROJECT, catalog_version="1.0.0",
        releases=tuple(
            CapabilityRelease(
                project_id=PROJECT, capability=name, release_version="1.0.0",
                schema_id=SCHEMA, compatible_schema_versions=("v1",),
                payload_type=MeterObservation, policy_version=POLICY,
            ) for name in CAPS
        ),
    )
    bindings = {
        name: CapabilityInputBinding(
            spec=CapabilityInputSpec(
                project_id=PROJECT, capability=name, schema_id=SCHEMA,
                schema_version="v1", payload_type=MeterObservation,
            ),
            envelope=CapabilityInputEnvelope(
                **{field: getattr(context, field) for field in KernelContext.model_fields},
                capability=name, schema_id=SCHEMA, schema_version="v1",
                payload=payload,
            ),
            invoker=producers[name],
        ) for name in CAPS
    }
    ledger = Path.cwd() / "energy_synthetic_ledger.json"
    assert not ledger.exists()
    desired = tuple(sorted((name, "1.0.0") for name in CAPS))

    def proposal():
        return CatalogChange(
            project_id=PROJECT, catalog=catalog,
            desired_releases=desired, expected_revision=0,
            expected_head_hash=None, reason="Synthetic fourth-domain admission",
        )

    for bad in (
        lambda *_: None,
        lambda *_: True,
        lambda *_: AuthorizationGrant(
            project_id="FOREIGN_PROJECT", actor_id="BAD_ACTOR",
            authorization_ref="BAD_REF", authorization_policy="SYNTHETIC",
            allowed_actions=frozenset({"BOOTSTRAP"}),
        ),
    ):
        reject("invalid authorization", lambda: commit_catalog_change(
            ledger, proposal(), bad), CatalogGovernanceError)
        assert not ledger.exists()

    approved = commit_catalog_change(ledger, proposal(), authorize_test_only)
    assert approved.revision == 1
    assert load_governed_state(ledger, project_id=PROJECT) == approved
    reject("foreign ledger", lambda: load_governed_state(
        ledger, project_id="FOREIGN_PROJECT"), CatalogGovernanceError)

    def bind(current_catalog=catalog, current_plan=plan, current_bindings=bindings):
        return bind_governed_plan(
            path=ledger, catalog=current_catalog,
            expected_revision=approved.revision,
            expected_head_hash=approved.head_hash,
            operation=operation, context=context, plan=current_plan,
            bindings=current_bindings,
        )

    invokers = bind()
    outcome = execute_kernel(operation, context, plan, invokers)
    assert calls == ["peak", "support"]
    assert payload.demand_kw == Decimal("89.5")
    assert outcome.status == KernelStatus.PARTIALLY_COMPLETED
    assert outcome.unresolved_items == ("METER_DOCUMENT_UNVERIFIED",)
    assert outcome.decision_authority is False
    assert outcome.operational_path == "FORBIDDEN"
    assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

    calls.clear()
    changed = replace(
        catalog, catalog_version="1.0.1",
        releases=tuple(
            replace(x, compatible_schema_versions=("v2",)) for x in catalog.releases
        ),
    )
    reject("unapproved schema change", lambda: bind(changed),
           CatalogGovernanceError)
    reject("missing capability", lambda: bind(
        current_bindings={CAPS[0]: bindings[CAPS[0]]}),
        Exception)
    reject("mixed release", lambda: bind(
        current_plan=KernelPlan(capabilities=("UNREGISTERED_CAPABILITY",),
                                policy_version=POLICY)), Exception)
    assert not calls

    tampered = Path.cwd() / "energy_tampered_ledger.json"
    saved = json.loads(ledger.read_text(encoding="utf-8"))
    saved["records"][0]["reason"] = "TAMPERED"
    tampered.write_text(json.dumps(saved), encoding="utf-8")
    reject("tampered ledger", lambda: load_governed_state(
        tampered, project_id=PROJECT), CatalogGovernanceError)

    return {
        "domain": "energy_management",
        "consumer": "energy",
        "initial_status": outcome.status.value,
        "unresolved_items": list(outcome.unresolved_items),
        "revision": approved.revision,
        "invalid_authorization_rejected": True,
        "cross_project_rejected": True,
        "schema_version_rejected": True,
        "unregistered_capability_rejected": True,
        "missing_binding_rejected": True,
        "tampered_ledger_rejected": True,
        "producer_input_isolated": True,
        "decision_authority": outcome.decision_authority,
        "operational_path": outcome.operational_path,
        "production_authorized": False,
        "real_pilot_admitted": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
