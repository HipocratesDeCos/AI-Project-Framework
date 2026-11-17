"""Independent company adapter E2E: two synthetic tenants, guarded capabilities.

Only a TEST DOUBLE approves catalog initialization. No real users, documents,
financial decisions or production permission are involved.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus, KernelStatus, execute_kernel,
)
from eios.catalog_governance import (
    AuthorizationGrant, CatalogChange, CatalogGovernanceError,
    bind_governed_plan, commit_catalog_change, load_governed_state,
)

from .adapter import (
    CAPABILITIES, ExternalSourceScope, prepare_external_case,
)


def _record(company: str) -> dict:
    return {
        "project_id": "MAINT_" + company,
        "company_id": company,
        "source_id": "SYNTHETIC_CSV_" + company,
        "data_snapshot_id": "SYNTHETIC_SNAPSHOT_001",
        "schema_version": "v1",
        "evidence_class": "SYNTHETIC_TEST",
        "documentary_status": "UNVERIFIED",
        "decision_id": "SYNTHETIC_DECISION_001",
        "scenario_id": "BASE",
        "facility_id": "FACILITY_" + company,
        "equipment_id": "TEST_PUMP_1",
        "hours_since_service": 720,
        "service_interval_hours": 600,
        "inspection_reference": "DECLARED_NOT_AUTHENTICATED",
    }


def _prepare(record: dict, calls: list[str]):
    data = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    scope = ExternalSourceScope(
        project_id=record["project_id"],
        company_id=record["company_id"],
        source_id=record["source_id"],
        expected_sha256=hashlib.sha256(data).hexdigest(),
        data_snapshot_id=record["data_snapshot_id"],
        rules_version="SYNTH_RULES_1",
        parameters_version="SYNTH_PARAMS_1",
        schema_version="v1",
        purpose="SYNTHETIC_TEST_ONLY",
    )

    def hours(value, context):
        calls.append(context.project_id)
        assert value.company_id == record["company_id"]
        assert context.project_id == record["project_id"]
        return KernelCapabilityResult(
            capability="SERVICE_HOURS_CHECK",
            status=KernelCapabilityStatus.COMPLETED,
            result_available=True,
            trace_references=("SYNTHETIC_HOURS_THRESHOLD_CHECK",),
        )

    def inspection(value, context):
        calls.append(context.project_id)
        assert value.company_id == record["company_id"]
        # A document *reference* does not authenticate its content or reviewer.
        return KernelCapabilityResult(
            capability="INSPECTION_REFERENCE_CHECK",
            status=KernelCapabilityStatus.NOT_EVALUABLE,
            result_available=False,
            unresolved_items=("INSPECTION_DOCUMENT_NOT_AUTHENTICATED",),
        )

    prepared = prepare_external_case(
        scope=scope, source_bytes=data,
        producers={CAPABILITIES[0]: hours, CAPABILITIES[1]: inspection},
    )
    return prepared


def _synthetic_test_grant(change, previous, actions):
    return AuthorizationGrant(
        project_id=change.project_id,
        actor_id="SYNTHETIC_TEST_ACTOR",
        authorization_ref="SYNTHETIC_GRANT_001",
        authorization_policy="SYNTHETIC_TEST_POLICY",
        allowed_actions=actions,
    )


def run() -> dict:
    root = Path.cwd()
    summaries = []
    for company in ("EXTERNAL_COMPANY_A", "EXTERNAL_COMPANY_B"):
        calls: list[str] = []
        prepared = _prepare(_record(company), calls)
        ledger = root / ("catalog_" + company + ".json")
        if ledger.exists():
            raise RuntimeError("A previous tenant ledger already exists")
        change = CatalogChange(
            project_id=prepared.context.project_id,
            catalog=prepared.catalog,
            desired_releases=tuple(sorted((key, "1.0.0") for key in CAPABILITIES)),
            expected_revision=0,
            expected_head_hash=None,
            reason="F6.2 SYNTHETIC adapter acceptance only",
        )
        # A missing authorization may not even create a ledger.
        try:
            commit_catalog_change(ledger, change, lambda *_: None)
        except CatalogGovernanceError:
            pass
        else:
            raise AssertionError("An absent grant unexpectedly initialized the ledger")
        assert not ledger.exists()
        state = commit_catalog_change(ledger, change, _synthetic_test_grant)
        assert state.revision == 1
        assert load_governed_state(ledger, project_id=prepared.context.project_id) == state
        try:
            load_governed_state(ledger, project_id="OTHER_COMPANY")
        except CatalogGovernanceError:
            pass
        else:
            raise AssertionError("Cross-company catalog access was accepted")
        invokers = bind_governed_plan(
            path=ledger, catalog=prepared.catalog,
            expected_revision=state.revision,
            expected_head_hash=state.head_hash,
            operation=prepared.operation, context=prepared.context,
            plan=prepared.plan, bindings=prepared.bindings,
        )
        result = execute_kernel(
            prepared.operation, prepared.context, prepared.plan, invokers,
        )
        assert result.status is KernelStatus.PARTIALLY_COMPLETED
        assert result.unresolved_items == ("INSPECTION_DOCUMENT_NOT_AUTHENTICATED",)
        assert result.operational_path == "FORBIDDEN"
        assert result.decision_authority is False
        assert result.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
        assert calls == [prepared.context.project_id] * 2
        summaries.append({
            "company_id": prepared.company_id,
            "project_id": prepared.context.project_id,
            "source_sha256": prepared.raw_sha256,
            "catalog_revision": state.revision,
            "status": result.status.value,
            "unresolved_items": result.unresolved_items,
            "decision_authority": result.decision_authority,
            "operational_path": result.operational_path,
            "provenance_status": result.provenance_status,
        })
    assert len({s["company_id"] for s in summaries}) == 2
    return {
        "verification": "F6_2_EXTERNAL_SYNTHETIC_COMPANY_ADAPTER_SUCCESS",
        "cases": summaries,
        "real_source_authentication": "NOT_TESTED",
        "documentary_admission": "NOT_TESTED",
        "human_authorization": "SYNTHETIC_TEST_DOUBLE_ONLY",
        "production_authorized": False,
        "operational_path": "FORBIDDEN",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
