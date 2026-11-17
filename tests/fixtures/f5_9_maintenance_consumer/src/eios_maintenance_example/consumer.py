"""Third EIOS consumer — synthetic equipment maintenance, outside purchases/sales.

This is a complete independently installed application-specific distribution.
It imports only neutral EIOS modules, defines its own business schema, creates
two own producers, and governs their exact versions in an isolated local file.
All data and authorization actors here are SYNTHETIC TEST DOUBLES.

Successful technical execution must NOT authorize field service or repair.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from importlib import metadata, util
import json
from pathlib import Path

from pydantic import BaseModel, Field

from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelContext,
    KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)
from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
    InputContractError,
)
from eios.capability_catalog import (
    CapabilityCatalog, CapabilityCatalogError, CapabilityRelease,
)
from eios.catalog_governance import (
    AuthorizationGrant, CatalogChange, CatalogGovernanceError,
    bind_governed_plan, commit_catalog_change, load_governed_state,
)


class MaintenanceWorkOrder(BaseModel):
    """Business input owned exclusively by this standalone maintenance project."""

    decision_id: str
    scenario_id: str
    facility_id: str
    equipment_id: str
    hours_since_service: int = Field(ge=0)
    maintenance_interval_hours: int = Field(gt=0)
    measured_vibration_mm_s: Decimal = Field(ge=0)
    lockout_document_present: bool = False


CAPABILITIES = ("SERVICE_INTERVAL_CHECK", "INSPECTION_EVIDENCE_CHECK")
PROJECT_ID = "SYNTH_MAINTENANCE_3"
POLICY_VERSION = "MAINT-SYNTH-1"
SCHEMA_ID = "maintenance.work_order"
SCHEMA_VERSION = "v1"


def _no_purchase_or_sales_installed() -> None:
    for module in ("eios.core", "eios.pricing", "eios.tco", "eios.company_app"):
        assert util.find_spec(module) is None, f"Unexpected business dependency: {module}"
    for distribution in (
        "eios-mvp", "eios-contracts-procurement",
        "eios-price-procurement", "eios-tco-procurement",
    ):
        try:
            metadata.version(distribution)
        except metadata.PackageNotFoundError:
            continue
        raise AssertionError(f"Procurement/legacy distribution leaked: {distribution}")


def _external_test_authorizer(
    proposal: CatalogChange, current, actions: frozenset[str],
) -> AuthorizationGrant:
    """TEST DOUBLE, NOT a real human authentication or permission provider."""
    assert proposal.project_id == PROJECT_ID
    assert actions and actions <= {
        "BOOTSTRAP", "ENABLE", "DISABLE", "REPLACE", "UPGRADE_CATALOG",
        "ROLLBACK",
    }
    return AuthorizationGrant(
        project_id=PROJECT_ID,
        actor_id="SYNTHETIC_TEST_APPROVER",
        authorization_ref=f"SYNTH_AUTH_{proposal.expected_revision + 1}",
        authorization_policy="SYNTHETIC_POLICY_V1",
        allowed_actions=actions,
    )


def run() -> dict[str, object]:
    _no_purchase_or_sales_installed()
    versions = {
        "eios-kernel": "0.1.0",
        "eios-input-contracts": "0.1.0",
        "eios-capability-catalog": "0.1.0",
        "eios-catalog-governance": "0.1.0",
        "eios-maintenance-example": "0.1.0",
    }
    for name, version in versions.items():
        assert metadata.version(name) == version, name

    payload = MaintenanceWorkOrder(
        decision_id="MAINT-SYNTH-0001", scenario_id="TEST-BASE",
        facility_id="TEST-FACILITY-01", equipment_id="TEST-PUMP-42",
        hours_since_service=610, maintenance_interval_hours=500,
        measured_vibration_mm_s=Decimal("2.35"),
        lockout_document_present=False,
    )
    context = KernelContext(
        project_id=PROJECT_ID,
        decision_id=payload.decision_id,
        scenario_id=payload.scenario_id,
        rules_version="RULES-MAINT-SYNTH-1",
        parameters_version="PARAMS-MAINT-SYNTH-1",
        data_snapshot_id="SNAPSHOT-MAINT-SYNTH-1",
    )
    operation = KernelOperation(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id, payload=payload,
    )
    plan = KernelPlan(capabilities=CAPABILITIES, policy_version=POLICY_VERSION)
    calls: list[str] = []

    def interval_check(work_order: MaintenanceWorkOrder, current: KernelContext):
        assert type(work_order) is MaintenanceWorkOrder
        assert current.project_id == PROJECT_ID
        assert work_order.hours_since_service == 610
        assert work_order.maintenance_interval_hours == 500
        assert work_order.facility_id == "TEST-FACILITY-01"
        calls.append("SERVICE_INTERVAL_CHECK")
        due_for_review = (
            work_order.hours_since_service >= work_order.maintenance_interval_hours
        )
        assert due_for_review is True  # informational classification, NOT work authorization
        work_order.hours_since_service = 0  # deliberate mutation: isolation check
        return KernelCapabilityResult(
            capability="SERVICE_INTERVAL_CHECK",
            status=KernelCapabilityStatus.COMPLETED,
            result_available=True,
            trace_references=("SYNTHETIC_MAINTENANCE_THRESHOLD_RULE",),
        )

    def inspection_check(work_order: MaintenanceWorkOrder, current: KernelContext):
        assert type(work_order) is MaintenanceWorkOrder
        assert current.project_id == PROJECT_ID
        # The producer must see a fresh copy, unaffected by the prior producer.
        assert work_order.hours_since_service == 610
        assert work_order.measured_vibration_mm_s == Decimal("2.35")
        calls.append("INSPECTION_EVIDENCE_CHECK")
        assert work_order.lockout_document_present is False
        return KernelCapabilityResult(
            capability="INSPECTION_EVIDENCE_CHECK",
            status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False,
            unresolved_items=("SYNTHETIC_SAFETY_INSPECTION_EVIDENCE_MISSING",),
        )

    producers = {
        "SERVICE_INTERVAL_CHECK": interval_check,
        "INSPECTION_EVIDENCE_CHECK": inspection_check,
    }
    catalog = CapabilityCatalog(
        project_id=PROJECT_ID,
        catalog_version="1.0.0",
        releases=tuple(
            CapabilityRelease(
                project_id=PROJECT_ID, capability=name,
                release_version="1.0.0", schema_id=SCHEMA_ID,
                compatible_schema_versions=(SCHEMA_VERSION,),
                payload_type=MaintenanceWorkOrder,
                policy_version=POLICY_VERSION,
            )
            for name in CAPABILITIES
        ),
    )
    bindings = {
        name: CapabilityInputBinding(
            spec=CapabilityInputSpec(
                project_id=PROJECT_ID, capability=name, schema_id=SCHEMA_ID,
                schema_version=SCHEMA_VERSION, payload_type=MaintenanceWorkOrder,
            ),
            envelope=CapabilityInputEnvelope(
                **{field: getattr(context, field) for field in KernelContext.model_fields},
                capability=name, schema_id=SCHEMA_ID,
                schema_version=SCHEMA_VERSION, payload=payload,
            ),
            invoker=producers[name],
        )
        for name in CAPABILITIES
    }
    ledger = Path.cwd() / "synthetic_maintenance_catalog.json"
    assert not ledger.exists()

    # The adapter is REQUIRED; missing/incorrect authorization cannot create ledger.
    for denied_authorizer in (
        lambda *_: None,
        lambda *_: True,
        lambda *_: AuthorizationGrant(
            project_id="FOREIGN_PROJECT",
            actor_id="SYNTH_BAD_ACTOR", authorization_ref="SYNTH_BAD_APPROVAL",
            authorization_policy="SYNTH_TEST_POLICY",
            allowed_actions=frozenset({"BOOTSTRAP"}),
        ),
    ):
        try:
            commit_catalog_change(
                ledger,
                CatalogChange(
                    project_id=PROJECT_ID, catalog=catalog,
                    desired_releases=tuple(sorted((name, "1.0.0") for name in CAPABILITIES)),
                    expected_revision=0, expected_head_hash=None,
                    reason="Synthetic third-domain bootstrap test",
                ),
                denied_authorizer,
            )
        except CatalogGovernanceError:
            pass
        else:
            raise AssertionError("Missing or foreign authorization created a ledger")
        assert not ledger.exists()

    desired = tuple(sorted((name, "1.0.0") for name in CAPABILITIES))
    approved = commit_catalog_change(
        ledger,
        CatalogChange(
            project_id=PROJECT_ID, catalog=catalog, desired_releases=desired,
            expected_revision=0, expected_head_hash=None,
            reason="Explicit synthetic maintenance capability enablement",
        ),
        _external_test_authorizer,
    )
    assert approved.revision == 1
    assert approved.active_releases == desired
    assert load_governed_state(ledger, project_id=PROJECT_ID) == approved
    assert not Path(str(ledger) + ".lock").exists()

    # No cross-project reuse of the ledger, even if the capability names match.
    try:
        load_governed_state(ledger, project_id="ANOTHER_COMPANY")
    except CatalogGovernanceError as exc:
        assert "GOVERNED_PROJECT_MISMATCH" in str(exc)
    else:
        raise AssertionError("Foreign project reused maintenance ledger")

    bound = bind_governed_plan(
        path=ledger, catalog=catalog,
        expected_revision=approved.revision,
        expected_head_hash=approved.head_hash,
        operation=operation, context=context,
        plan=plan, bindings=bindings,
    )
    result = execute_kernel(operation, context, plan, bound)
    assert calls == list(CAPABILITIES)
    assert payload.hours_since_service == 610
    assert result.status == KernelStatus.PARTIALLY_COMPLETED
    assert result.unresolved_items == (
        "SYNTHETIC_SAFETY_INSPECTION_EVIDENCE_MISSING",
    )
    assert result.decision_authority is False
    assert result.operational_path == "FORBIDDEN"
    assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"

    # New version is NEVER inferred; a new schema is not silently compatible.
    calls.clear()
    incompatible = replace(
        catalog,
        releases=(
            catalog.releases[0],
            replace(catalog.releases[1], compatible_schema_versions=("v2",)),
        ),
        catalog_version="1.0.1",
    )
    # The current ledger fingerprint rejects changed catalog even before F5.7.
    try:
        bind_governed_plan(
            path=ledger, catalog=incompatible,
            expected_revision=approved.revision,
            expected_head_hash=approved.head_hash,
            operation=operation, context=context,
            plan=plan, bindings=bindings,
        )
    except CatalogGovernanceError as exc:
        assert "GOVERNED_CATALOG_FINGERPRINT_MISMATCH" in str(exc)
    else:
        raise AssertionError("Unapproved schema migration bypassed ledger")
    assert calls == []

    # An authority grant restricted to ENABLE may not disable any capability.
    proposal = CatalogChange(
        project_id=PROJECT_ID, catalog=catalog,
        desired_releases=(("SERVICE_INTERVAL_CHECK", "1.0.0"),),
        expected_revision=approved.revision,
        expected_head_hash=approved.head_hash,
        reason="Synthetic disablement of inspection capability",
    )

    def limited_grant(change, old, actions):
        return replace(
            _external_test_authorizer(change, old, actions),
            allowed_actions=frozenset({"ENABLE"}),
        )

    try:
        commit_catalog_change(ledger, proposal, limited_grant)
    except CatalogGovernanceError as exc:
        assert "INSUFFICIENT_AUTHORIZATION_SCOPE" in str(exc)
    else:
        raise AssertionError("Wrong action grant disabled a capability")
    assert load_governed_state(ledger, project_id=PROJECT_ID) == approved

    revoked = commit_catalog_change(ledger, proposal, _external_test_authorizer)
    assert revoked.revision == 2
    assert revoked.head_hash != approved.head_hash
    assert revoked.active_releases == (("SERVICE_INTERVAL_CHECK", "1.0.0"),)

    # Previously bound producer is invalid after committed change.
    try:
        bound["SERVICE_INTERVAL_CHECK"](payload, context)
    except CatalogGovernanceError as exc:
        assert "GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION" in str(exc)
    else:
        raise AssertionError("Stale producer executed after a recorded revocation")
    assert calls == []

    try:
        bind_governed_plan(
            path=ledger, catalog=catalog,
            expected_revision=revoked.revision,
            expected_head_hash=revoked.head_hash,
            operation=operation, context=context,
            plan=plan, bindings=bindings,
        )
    except CatalogGovernanceError as exc:
        assert "GOVERNED_CAPABILITY_DISABLED" in str(exc)
    else:
        raise AssertionError("Disabled safety capability still admitted")
    assert calls == []

    try:
        commit_catalog_change(ledger, proposal, _external_test_authorizer)
    except CatalogGovernanceError as exc:
        assert "STALE_CATALOG_REVISION" in str(exc)
    else:
        raise AssertionError("Stale change unexpectedly overwrote current revision")

    # Tamper detection is tested on a COPY, never on the canonical ledger.
    copied = Path.cwd() / "tampered_maintenance_ledger.json"
    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert [row["actions"] for row in data["records"]] == [
        ["BOOTSTRAP"], ["DISABLE"],
    ]
    assert data["records"][1]["previous_hash"] == approved.head_hash
    data["records"][0]["reason"] = "SYNTHETIC_TAMPERED_RECORD"
    copied.write_text(json.dumps(data), encoding="utf-8")
    try:
        load_governed_state(copied, project_id=PROJECT_ID)
    except CatalogGovernanceError:
        pass
    else:
        raise AssertionError("Modified audit chain not rejected")
    assert load_governed_state(ledger, project_id=PROJECT_ID) == revoked

    # The current authorized capability alone can still technically execute.
    one_plan = KernelPlan(
        capabilities=("SERVICE_INTERVAL_CHECK",),
        policy_version=POLICY_VERSION,
    )
    approved_one = bind_governed_plan(
        path=ledger, catalog=catalog,
        expected_revision=revoked.revision,
        expected_head_hash=revoked.head_hash,
        operation=operation, context=context,
        plan=one_plan, bindings={"SERVICE_INTERVAL_CHECK": bindings["SERVICE_INTERVAL_CHECK"]},
    )
    latest = execute_kernel(operation, context, one_plan, approved_one)
    assert latest.status == KernelStatus.COMPLETED
    assert latest.decision_authority is False
    assert latest.operational_path == "FORBIDDEN"

    return {
        "consumer": "maintenance",
        "project_id": PROJECT_ID,
        "independent_wheel_version": metadata.version("eios-maintenance-example"),
        "revision_history": [1, 2],
        "actions": ["BOOTSTRAP", "DISABLE"],
        "initial_status": result.status.value,
        "later_status": latest.status.value,
        "unresolved_items": result.unresolved_items,
        "false_grants_rejected": True,
        "cross_project_isolation": True,
        "schema_migration_rejected": True,
        "insufficient_scope_rejected": True,
        "stale_revision_rejected": True,
        "stale_invoker_rejected": True,
        "tampered_copy_rejected": True,
        "producer_input_isolated": True,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
        "provenance_status": result.provenance_status,
        "authorization": "SYNTHETIC_TEST_DOUBLE_ONLY",
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
