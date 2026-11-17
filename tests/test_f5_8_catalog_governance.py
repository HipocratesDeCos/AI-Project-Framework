"""F5.8 — authorized versioned local catalog audit and fail-closed execution."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from eios.capability_catalog import (
    CapabilityCatalog, CapabilityRelease,
)
from eios.catalog_governance import (
    AuthorizationGrant, CatalogChange, CatalogGovernanceError,
    bind_governed_plan, commit_catalog_change, fingerprint_catalog,
    load_governed_state,
)
from eios.input_contracts import (
    CapabilityInputBinding, CapabilityInputEnvelope, CapabilityInputSpec,
)
from eios.kernel.execution import (
    KernelCapabilityResult, KernelCapabilityStatus,
    KernelContext, KernelOperation, KernelPlan, KernelStatus, execute_kernel,
)


class SaleQuote(BaseModel):
    customer_id: str
    amount: int


class PurchaseDraft(BaseModel):
    decision_id: str
    scenario_id: str
    units: int


def catalog(project="SALES", version="1.0.0", *, include_replacement=True, class_type=None):
    model = class_type or (SaleQuote if project == "SALES" else PurchaseDraft)
    releases = [
        CapabilityRelease(
            project_id=project, capability="FIRST",
            release_version="1.0.0", schema_id="example.input",
            compatible_schema_versions=("v1",), payload_type=model,
            policy_version="POLICY-1",
        ),
        CapabilityRelease(
            project_id=project, capability="SECOND",
            release_version="1.0.0", schema_id="example.input",
            compatible_schema_versions=("v1",), payload_type=model,
            policy_version="POLICY-1",
        ),
    ]
    if include_replacement:
        releases.append(replace(releases[0], release_version="2.0.0"))
    return CapabilityCatalog(
        project_id=project, catalog_version=version,
        releases=tuple(releases),
    )


def grant(changes, state, actions):
    return AuthorizationGrant(
        project_id=changes.project_id,
        actor_id="SYNTH-APPROVER-1",
        authorization_ref=f"SYNTH-AUTH-{changes.expected_revision + 1}",
        authorization_policy="TEST-POLICY-1",
        allowed_actions=actions,
    )


def propose(catalog, selected, prior=None, **kwargs):
    return CatalogChange(
        project_id=catalog.project_id,
        catalog=catalog,
        desired_releases=tuple(sorted(selected.items())),
        expected_revision=0 if prior is None else prior.revision,
        expected_head_hash=None if prior is None else prior.head_hash,
        reason="Test synthetic approval of explicit catalog changes",
        **kwargs,
    )


def make_runtime(catalog, capabilities=("FIRST",)):
    context = KernelContext(
        project_id=catalog.project_id, decision_id="D-10", scenario_id="BASE",
        rules_version="RULES-1", parameters_version="PARAMS-1",
        data_snapshot_id="SNAPSHOT-1",
    )
    model = catalog.releases[0].payload_type
    payload = (
        SaleQuote(customer_id="CUSTOMER-SYNTH", amount=15)
        if model is SaleQuote
        else PurchaseDraft(
            decision_id=context.decision_id, scenario_id=context.scenario_id, units=3,
        )
    )
    operation = KernelOperation(
        decision_id=context.decision_id, scenario_id=context.scenario_id,
        payload=payload,
    )
    plan = KernelPlan(capabilities=capabilities, policy_version="POLICY-1")
    called = []
    bindings = {}
    for cap in capabilities:
        entry_spec = CapabilityInputSpec(
            project_id=context.project_id, capability=cap,
            schema_id="example.input", schema_version="v1", payload_type=model,
        )
        envelope = CapabilityInputEnvelope(
            **{f: getattr(context, f) for f in KernelContext.model_fields},
            capability=cap, schema_id=entry_spec.schema_id,
            schema_version=entry_spec.schema_version, payload=payload,
        )
        def producer(p, ctx, capability=cap):
            assert type(p) is model
            called.append(capability)
            return KernelCapabilityResult(
                capability=capability, status=KernelCapabilityStatus.COMPLETED,
                result_available=True,
            )
        bindings[cap] = CapabilityInputBinding(
            spec=entry_spec, envelope=envelope, invoker=producer,
        )
    return operation, context, plan, bindings, called


def test_initial_approval_is_persisted_and_reloaded_with_provenance(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    state = commit_catalog_change(
        f, propose(cat, {"FIRST": "1.0.0"}), grant,
    )
    assert state.revision == 1
    assert state.catalog_version == "1.0.0"
    assert state.active_releases == (("FIRST", "1.0.0"),)
    assert len(state.head_hash) == 64
    assert load_governed_state(f, project_id="SALES") == state
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["format_version"] == 1
    assert len(data["records"]) == 1
    entry = data["records"][0]
    assert entry["actions"] == ["BOOTSTRAP"]
    assert entry["actor_id"] == "SYNTH-APPROVER-1"
    assert entry["authorization_ref"] == "SYNTH-AUTH-1"
    assert entry["authorization_policy"] == "TEST-POLICY-1"
    assert entry["catalog_digest"] == fingerprint_catalog(cat)
    assert not Path(str(f) + ".lock").exists()


def test_enable_disable_replace_have_consecutive_revisions_and_stable_hash_chain(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    a = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    b = commit_catalog_change(
        f, propose(cat, {"FIRST": "1.0.0", "SECOND": "1.0.0"}, a), grant,
    )
    c = commit_catalog_change(
        f, propose(cat, {"FIRST": "2.0.0", "SECOND": "1.0.0"}, b), grant,
    )
    d = commit_catalog_change(
        f, propose(cat, {"FIRST": "2.0.0"}, c), grant,
    )
    assert [x.revision for x in (a, b, c, d)] == [1, 2, 3, 4]
    assert len({x.head_hash for x in (a, b, c, d)}) == 4
    data = json.loads(f.read_text(encoding="utf-8"))
    assert [record["actions"] for record in data["records"]] == [
        ["BOOTSTRAP"], ["ENABLE"], ["REPLACE"], ["DISABLE"],
    ]
    assert [record["previous_hash"] for record in data["records"]] == [
        None, a.head_hash, b.head_hash, c.head_hash,
    ]
    assert load_governed_state(f, project_id="SALES") == d


def test_no_self_declared_authority_bypass_and_no_partial_write(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    change = propose(cat, {"FIRST": "1.0.0"})
    for policy in (
        lambda *_: None,
        lambda *_: True,
        lambda *_: AuthorizationGrant(
            project_id="FOREIGN", actor_id="APPROVER", authorization_ref="A-1",
            authorization_policy="P-1", allowed_actions=frozenset({"BOOTSTRAP"}),
        ),
        lambda *_: AuthorizationGrant(
            project_id="SALES", actor_id="APPROVER", authorization_ref="A-1",
            authorization_policy="P-1", allowed_actions=frozenset({"DISABLE"}),
        ),
    ):
        with pytest.raises(CatalogGovernanceError, match="AUTHORIZATION"):
            commit_catalog_change(f, change, policy)
        assert not f.exists()
        assert not Path(str(f) + ".lock").exists()


def test_stale_revision_and_stale_hash_rejected_without_callback(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    state = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    forbidden_calls = []
    def forbidden(*args):
        forbidden_calls.append("called")
        return grant(*args)
    with pytest.raises(CatalogGovernanceError, match="STALE_CATALOG_REVISION"):
        commit_catalog_change(
            f, propose(cat, {"SECOND": "1.0.0"}), forbidden,
        )
    with pytest.raises(CatalogGovernanceError, match="STALE_CATALOG_HEAD"):
        commit_catalog_change(
            f, replace(propose(cat, {"SECOND": "1.0.0"}, state),
                       expected_head_hash="0" * 64),
            forbidden,
        )
    assert forbidden_calls == []
    assert load_governed_state(f, project_id="SALES") == state


def test_catalog_version_upgrades_require_external_approval_and_new_revision(tmp_path):
    f = tmp_path / "ledger.json"
    original = catalog()
    head = commit_catalog_change(f, propose(original, {"FIRST": "1.0.0"}), grant)
    upgraded = catalog(version="1.1.0")
    new = commit_catalog_change(
        f, propose(upgraded, {"FIRST": "1.0.0"}, head), grant,
    )
    assert new.revision == 2
    assert new.catalog_version == "1.1.0"
    assert new.catalog_digest != head.catalog_digest
    assert json.loads(f.read_text())["records"][-1]["actions"] == ["UPGRADE_CATALOG"]
    with pytest.raises(CatalogGovernanceError, match="CATALOG_CHANGED_WITHOUT_VERSION_INCREMENT"):
        modified = replace(upgraded, releases=upgraded.releases[:-1])
        commit_catalog_change(
            f, propose(modified, {"FIRST": "1.0.0"}, new), grant,
        )
    assert load_governed_state(f, project_id="SALES") == new


def test_rollbacks_require_explicit_request_and_scope(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    a = commit_catalog_change(f, propose(cat, {"FIRST": "2.0.0"}), grant)
    with pytest.raises(CatalogGovernanceError, match="ROLLBACK_NOT_EXPLICITLY_REQUESTED"):
        commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}, a), grant)
    def no_rollback_permission(change, state, actions):
        result = grant(change, state, actions)
        return replace(result, allowed_actions=frozenset({"REPLACE"}))
    with pytest.raises(CatalogGovernanceError, match="INSUFFICIENT_AUTHORIZATION_SCOPE"):
        commit_catalog_change(
            f, propose(cat, {"FIRST": "1.0.0"}, a, allow_rollback=True),
            no_rollback_permission,
        )
    b = commit_catalog_change(
        f, propose(cat, {"FIRST": "1.0.0"}, a, allow_rollback=True), grant,
    )
    assert b.revision == 2
    assert json.loads(f.read_text())["records"][-1]["actions"] == [
        "REPLACE", "ROLLBACK",
    ]


def test_governed_runtime_uses_saved_selections_and_blocks_changes(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    a = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    op, ctx, plan, bindings, called = make_runtime(cat)
    invokers = bind_governed_plan(
        path=f, catalog=cat, expected_revision=a.revision,
        expected_head_hash=a.head_hash, operation=op, context=ctx,
        plan=plan, bindings=bindings,
    )
    outcome = execute_kernel(op, ctx, plan, invokers)
    assert called == ["FIRST"]
    assert outcome.status == KernelStatus.COMPLETED
    assert outcome.decision_authority is False
    assert outcome.operational_path == "FORBIDDEN"
    assert outcome.provenance_status == "UNVERIFIED_ADAPTER_RESPONSIBILITY"
    called.clear()
    new_state = commit_catalog_change(f, propose(cat, {"SECOND": "1.0.0"}, a), grant)
    with pytest.raises(CatalogGovernanceError, match="GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION"):
        invokers["FIRST"](op.payload, ctx)
    assert called == []
    with pytest.raises(CatalogGovernanceError, match="GOVERNED_CAPABILITY_DISABLED"):
        bind_governed_plan(
            path=f, catalog=cat, expected_revision=new_state.revision,
            expected_head_hash=new_state.head_hash,
            operation=op, context=ctx, plan=plan, bindings=bindings,
        )


@pytest.mark.parametrize("domain", ("SALES", "PROCUREMENT"))
def test_same_governance_api_accepts_two_independent_domains(tmp_path, domain):
    cat = catalog("SALES" if domain == "SALES" else "PROCUREMENT")
    f = tmp_path / (domain + ".json")
    state = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    op, ctx, plan, bindings, calls = make_runtime(cat)
    inv = bind_governed_plan(
        path=f, catalog=cat, expected_revision=state.revision,
        expected_head_hash=state.head_hash,
        operation=op, context=ctx, plan=plan, bindings=bindings,
    )
    result = execute_kernel(op, ctx, plan, inv)
    assert calls == ["FIRST"]
    assert result.operational_path == "FORBIDDEN"
    with pytest.raises(CatalogGovernanceError, match="GOVERNED_PROJECT_MISMATCH"):
        load_governed_state(f, project_id="FOREIGN")


def test_mutated_or_corrupt_hash_chain_fails_closed(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    a = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    commit_catalog_change(f, propose(cat, {"SECOND": "1.0.0"}, a), grant)
    original = f.read_text()
    for changed in (
        lambda d: d["records"][0].update({"reason": "TAMPERED"}),
        lambda d: d["records"][1].update({"previous_hash": "0" * 64}),
        lambda d: d["records"][1].update({"revision": 9}),
        lambda d: d["records"][1].update({"actions": ["BOOTSTRAP"]}),
    ):
        raw = json.loads(original)
        changed(raw)
        f.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(CatalogGovernanceError):
            load_governed_state(f, project_id="SALES")
    f.write_text(original)
    assert load_governed_state(f, project_id="SALES").revision == 2


def test_invalid_missing_duplicate_json_and_external_lock_fail_closed(tmp_path):
    f = tmp_path / "ledger.json"
    with pytest.raises(CatalogGovernanceError, match="GOVERNED_CONFIGURATION_NOT_INITIALIZED"):
        load_governed_state(f, project_id="SALES")
    f.write_text('{"format_version":1,"format_version":1,"records":[]}')
    with pytest.raises(CatalogGovernanceError):
        load_governed_state(f, project_id="SALES")
    f.unlink()
    lock = Path(str(f) + ".lock")
    lock.write_text("held by another writer", encoding="utf-8")
    with pytest.raises(CatalogGovernanceError, match="CONCURRENT_OR_STALE_LEDGER_LOCK"):
        commit_catalog_change(
            f, propose(catalog(), {"FIRST": "1.0.0"}), grant,
        )
    assert lock.exists()
    lock.unlink()


def test_catalog_fingerprint_mismatch_and_disabled_release_fail_before_execution(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    state = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    op, ctx, plan, bindings, calls = make_runtime(cat)
    modified = catalog(version="1.1.0")
    with pytest.raises(CatalogGovernanceError, match="GOVERNED_CATALOG_FINGERPRINT_MISMATCH"):
        bind_governed_plan(
            path=f, catalog=modified,
            expected_revision=state.revision,
            expected_head_hash=state.head_hash, operation=op,
            context=ctx, plan=plan, bindings=bindings,
        )
    disabled = replace(
        cat, catalog_version="1.1.0",
        releases=tuple(
            replace(entry, enabled=False) if entry.capability == "FIRST" else entry
            for entry in cat.releases
        ),
    )
    with pytest.raises(CatalogGovernanceError, match="DISABLED_GOVERNED_RELEASE"):
        commit_catalog_change(
            f, propose(disabled, {"FIRST": "1.0.0"}, state), grant,
        )
    assert calls == []


def test_frozen_proposals_do_not_allow_inline_changes(tmp_path):
    cat = catalog()
    change = propose(cat, {"FIRST": "1.0.0"})
    with pytest.raises(FrozenInstanceError):
        change.project_id = "FOREIGN"
    with pytest.raises(CatalogGovernanceError, match="NONCANONICAL"):
        replace(change, desired_releases=(("SECOND", "1.0.0"), ("FIRST", "1.0.0")))
    with pytest.raises(CatalogGovernanceError, match="UNREGISTERED_GOVERNED_RELEASE"):
        replace(change, desired_releases=(("FIRST", "9.0.0"),))


def test_repeated_noop_change_never_creates_a_revision(tmp_path):
    f = tmp_path / "ledger.json"
    cat = catalog()
    state = commit_catalog_change(f, propose(cat, {"FIRST": "1.0.0"}), grant)
    with pytest.raises(CatalogGovernanceError, match="NO_CONFIGURATION_CHANGE"):
        commit_catalog_change(
            f, propose(cat, {"FIRST": "1.0.0"}, state), grant,
        )
    assert load_governed_state(f, project_id="SALES") == state
