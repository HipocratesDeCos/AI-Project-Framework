"""F5.8 — optional project-scoped catalog governance with durable audit chain.

A *trusted project adapter* must authorize every initial or subsequent change
through an explicit callback. This package cannot authenticate a human or
verify a document. SHA-256 entries detect accidental edits and broken chains,
not malicious rewrites by a writer who controls the entire local ledger.

Local-file snapshot replacement is atomic on the same filesystem. A fail-fast
exclusive .lock file serializes writers that observe this protocol; unexpected
locks fail closed and require operator intervention, never automatic removal.
No QTG/O1 or business decision authority is granted.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from types import MappingProxyType
from typing import Any

from eios.capability_catalog import (
    CapabilityCatalog, CapabilityCatalogError, KERNEL_API_VERSION,
    INPUT_CONTRACT_API_VERSION, bind_catalog_plan,
)
from eios.input_contracts import CapabilityInputBinding
from eios.kernel.execution import (
    KernelContext, KernelInvoker, KernelOperation, KernelPlan,
)

_RECORD_KEYS = frozenset({
    "revision", "project_id", "catalog_version", "catalog_digest",
    "active_releases", "actions", "reason", "actor_id", "authorization_ref",
    "authorization_policy", "occurred_at", "previous_hash", "entry_hash",
})
_ACTIONS = frozenset({
    "BOOTSTRAP", "ENABLE", "DISABLE", "REPLACE",
    "UPGRADE_CATALOG", "ROLLBACK",
})
_SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
_HASH = re.compile(r"[a-f0-9]{64}\Z")
_SIZE_LIMIT = 2_000_000
_FORMAT_VERSION = 1


class CatalogGovernanceError(CapabilityCatalogError):
    """An authorized release selection is stale, invalid or unauditable."""


def _text(value: object, name: str, limit: int = 512) -> str:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > limit
    ):
        raise CatalogGovernanceError(f"INVALID_GOVERNANCE_FIELD:{name}")
    return value


def _semver(value: object, name: str) -> str:
    result = _text(value, name, 64)
    if not _SEMVER.fullmatch(result):
        raise CatalogGovernanceError(f"INVALID_GOVERNANCE_VERSION:{name}")
    return result


def _hash(value: object, name: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if type(value) is not str or not _HASH.fullmatch(value):
        raise CatalogGovernanceError(f"INVALID_GOVERNANCE_HASH:{name}")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def fingerprint_catalog(catalog: CapabilityCatalog) -> str:
    """Stable configuration fingerprint; NOT a signature of executable code."""
    if type(catalog) is not CapabilityCatalog:
        raise CatalogGovernanceError("INVALID_GOVERNANCE_CATALOG")
    return _digest({
        "project_id": catalog.project_id,
        "catalog_version": catalog.catalog_version,
        "releases": [
            {
                "capability": release.capability,
                "version": release.release_version,
                "schema_id": release.schema_id,
                "schema_versions": sorted(release.compatible_schema_versions),
                "model_module": release.payload_type.__module__,
                "model_qualname": release.payload_type.__qualname__,
                "policy_version": release.policy_version,
                "required_kernel_api": release.required_kernel_api,
                "required_input_api": release.required_input_contract_api,
                "enabled": release.enabled,
            }
            for release in sorted(
                catalog.releases,
                key=lambda release: (release.capability, release.release_version),
            )
        ],
    })


def _normalize_selection(selection: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    if not isinstance(selection, Mapping):
        raise CatalogGovernanceError("INVALID_RELEASE_SELECTION")
    entries = []
    for name, version in selection.items():
        _text(name, "capability", 64)
        if name in {"O1", "QTG"}:
            raise CatalogGovernanceError("FORBIDDEN_BOUNDARY_CAPABILITY")
        entries.append((name, _semver(version, "release_version")))
    return tuple(sorted(entries))


def _validated_catalog_selection(catalog: CapabilityCatalog, selected: tuple[tuple[str, str], ...]) -> None:
    valid = {(x.capability, x.release_version): x for x in catalog.releases}
    for name, version in selected:
        release = valid.get((name, version))
        if release is None:
            raise CatalogGovernanceError(f"UNREGISTERED_GOVERNED_RELEASE:{name}")
        if not release.enabled:
            raise CatalogGovernanceError(f"DISABLED_GOVERNED_RELEASE:{name}")
        if release.required_kernel_api != KERNEL_API_VERSION:
            raise CatalogGovernanceError(f"KERNEL_API_INCOMPATIBLE:{name}")
        if release.required_input_contract_api != INPUT_CONTRACT_API_VERSION:
            raise CatalogGovernanceError(f"INPUT_API_INCOMPATIBLE:{name}")


@dataclass(frozen=True)
class CatalogChange:
    """Full replacement proposal with explicit optimistic concurrency anchor."""

    project_id: str
    catalog: CapabilityCatalog
    desired_releases: tuple[tuple[str, str], ...]
    expected_revision: int
    expected_head_hash: str | None
    reason: str
    allow_rollback: bool = False

    def __post_init__(self) -> None:
        _text(self.project_id, "project_id", 128)
        _text(self.reason, "reason", 512)
        if type(self.catalog) is not CapabilityCatalog or self.catalog.project_id != self.project_id:
            raise CatalogGovernanceError("FOREIGN_OR_INVALID_CHANGE_CATALOG")
        if type(self.expected_revision) is not int or self.expected_revision < 0:
            raise CatalogGovernanceError("INVALID_EXPECTED_REVISION")
        _hash(self.expected_head_hash, "expected_head_hash", optional=self.expected_revision == 0)
        if self.expected_revision > 0 and self.expected_head_hash is None:
            raise CatalogGovernanceError("MISSING_EXPECTED_HEAD_HASH")
        if self.expected_revision == 0 and self.expected_head_hash is not None:
            raise CatalogGovernanceError("GENESIS_REQUIRES_NULL_HEAD")
        if type(self.allow_rollback) is not bool:
            raise CatalogGovernanceError("INVALID_ROLLBACK_FLAG")
        if type(self.desired_releases) is not tuple:
            raise CatalogGovernanceError("MUTABLE_RELEASE_SELECTION")
        desired = dict(self.desired_releases)
        if len(desired) != len(self.desired_releases):
            raise CatalogGovernanceError("DUPLICATE_RELEASE_SELECTION")
        if _normalize_selection(desired) != self.desired_releases:
            raise CatalogGovernanceError("NONCANONICAL_RELEASE_SELECTION")
        _validated_catalog_selection(self.catalog, self.desired_releases)


@dataclass(frozen=True)
class AuthorizationGrant:
    """Claim supplied by a trusted *external* policy callback, never by caller data."""

    project_id: str
    actor_id: str
    authorization_ref: str
    authorization_policy: str
    allowed_actions: frozenset[str]

    def __post_init__(self) -> None:
        _text(self.project_id, "grant_project_id", 128)
        _text(self.actor_id, "actor_id", 128)
        _text(self.authorization_ref, "authorization_ref", 256)
        _text(self.authorization_policy, "authorization_policy", 128)
        if (
            type(self.allowed_actions) is not frozenset
            or not self.allowed_actions
            or not self.allowed_actions <= _ACTIONS
        ):
            raise CatalogGovernanceError("INVALID_AUTHORIZATION_ACTIONS")


@dataclass(frozen=True)
class GovernedState:
    project_id: str
    revision: int
    head_hash: str
    catalog_version: str
    catalog_digest: str
    active_releases: tuple[tuple[str, str], ...]


def _actions(previous: dict[str, Any] | None, active: tuple[tuple[str, str], ...], catalog: CapabilityCatalog, digest: str) -> frozenset[str]:
    if previous is None:
        if not active:
            raise CatalogGovernanceError("EMPTY_INITIAL_CONFIGURATION")
        return frozenset({"BOOTSTRAP"})
    original = dict(previous["active_releases"])
    proposed = dict(active)
    changes = set()
    for name in original.keys() | proposed.keys():
        if name not in original:
            changes.add("ENABLE")
        elif name not in proposed:
            changes.add("DISABLE")
        elif original[name] != proposed[name]:
            changes.add("REPLACE")
            if tuple(map(int, proposed[name].split("."))) < tuple(map(int, original[name].split("."))):
                changes.add("ROLLBACK")
    old_version = tuple(map(int, previous["catalog_version"].split(".")))
    new_version = tuple(map(int, catalog.catalog_version.split(".")))
    if new_version != old_version:
        changes.add("UPGRADE_CATALOG")
        if new_version < old_version:
            changes.add("ROLLBACK")
    elif previous["catalog_digest"] != digest:
        raise CatalogGovernanceError("CATALOG_CHANGED_WITHOUT_VERSION_INCREMENT")
    if not changes:
        raise CatalogGovernanceError("NO_CONFIGURATION_CHANGE")
    return frozenset(changes)


def _parse_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CatalogGovernanceError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def _load_records(path: Path) -> list[dict[str, Any]]:
    if path.is_symlink():
        raise CatalogGovernanceError("UNTRUSTED_LEDGER_SYMLINK")
    if not path.exists():
        return []
    if path.stat().st_size > _SIZE_LIMIT:
        raise CatalogGovernanceError("LEDGER_EXCEEDS_SIZE_LIMIT")
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_parse_no_duplicates)
    except (ValueError, UnicodeError) as exc:
        raise CatalogGovernanceError("INVALID_LEDGER_JSON") from exc
    if type(data) is not dict or set(data) != {"format_version", "records"}:
        raise CatalogGovernanceError("INVALID_LEDGER_ENVELOPE")
    if type(data["format_version"]) is not int or data["format_version"] != _FORMAT_VERSION:
        raise CatalogGovernanceError("INVALID_LEDGER_FORMAT_VERSION")
    records = data["records"]
    if type(records) is not list or not records:
        raise CatalogGovernanceError("EMPTY_OR_INVALID_LEDGER")
    prior = None
    for index, entry in enumerate(records):
        if type(entry) is not dict or set(entry) != _RECORD_KEYS:
            raise CatalogGovernanceError("INVALID_LEDGER_RECORD")
        if type(entry["revision"]) is not int or entry["revision"] != index + 1:
            raise CatalogGovernanceError("NONSEQUENTIAL_LEDGER_REVISION")
        if entry["previous_hash"] != (None if prior is None else prior["entry_hash"]):
            raise CatalogGovernanceError("BROKEN_LEDGER_HASH_CHAIN")
        _hash(entry["entry_hash"], "entry_hash")
        _hash(entry["catalog_digest"], "catalog_digest")
        _text(entry["project_id"], "project_id", 128)
        _semver(entry["catalog_version"], "catalog_version")
        _text(entry["reason"], "reason")
        _text(entry["actor_id"], "actor_id", 128)
        _text(entry["authorization_ref"], "authorization_ref", 256)
        _text(entry["authorization_policy"], "authorization_policy", 128)
        _text(entry["occurred_at"], "occurred_at", 64)
        if type(entry["active_releases"]) is not list or any(
            type(item) is not list or len(item) != 2 for item in entry["active_releases"]
        ):
            raise CatalogGovernanceError("INVALID_PERSISTED_SELECTION")
        mapping = dict(map(tuple, entry["active_releases"]))
        if len(mapping) != len(entry["active_releases"]) or tuple(map(tuple, entry["active_releases"])) != _normalize_selection(mapping):
            raise CatalogGovernanceError("NONCANONICAL_PERSISTED_SELECTION")
        if type(entry["actions"]) is not list or (
            entry["actions"] != sorted(set(entry["actions"]))
            or not set(entry["actions"]) <= _ACTIONS
        ):
            raise CatalogGovernanceError("INVALID_PERSISTED_ACTIONS")
        if index == 0:
            if entry["actions"] != ["BOOTSTRAP"] or not mapping:
                raise CatalogGovernanceError("INVALID_GENESIS_ACTION")
        else:
            if entry["project_id"] != prior["project_id"]:
                raise CatalogGovernanceError("MIXED_PROJECT_LEDGER")
            expected = _derive_persisted_actions(prior, entry)
            if set(entry["actions"]) != expected:
                raise CatalogGovernanceError("INCONSISTENT_PERSISTED_ACTIONS")
        if entry["entry_hash"] != _digest({key: value for key, value in entry.items() if key != "entry_hash"}):
            raise CatalogGovernanceError("LEDGER_RECORD_HASH_MISMATCH")
        prior = entry
    return records


def _derive_persisted_actions(previous: dict[str, Any], current: dict[str, Any]) -> set[str]:
    old, new = dict(previous["active_releases"]), dict(current["active_releases"])
    actions: set[str] = set()
    for cap in old.keys() | new.keys():
        if cap not in old:
            actions.add("ENABLE")
        elif cap not in new:
            actions.add("DISABLE")
        elif old[cap] != new[cap]:
            actions.add("REPLACE")
            if tuple(map(int, new[cap].split("."))) < tuple(map(int, old[cap].split("."))):
                actions.add("ROLLBACK")
    old_version = tuple(map(int, previous["catalog_version"].split(".")))
    new_version = tuple(map(int, current["catalog_version"].split(".")))
    if old_version != new_version:
        actions.add("UPGRADE_CATALOG")
        if new_version < old_version:
            actions.add("ROLLBACK")
    elif previous["catalog_digest"] != current["catalog_digest"]:
        raise CatalogGovernanceError("CATALOG_CHANGED_WITHOUT_VERSION_INCREMENT")
    if not actions:
        raise CatalogGovernanceError("REDUNDANT_LEDGER_RECORD")
    return actions


def load_governed_state(path: Path, *, project_id: str) -> GovernedState:
    _text(project_id, "project_id", 128)
    records = _load_records(Path(path))
    if not records:
        raise CatalogGovernanceError("GOVERNED_CONFIGURATION_NOT_INITIALIZED")
    last = records[-1]
    if last["project_id"] != project_id:
        raise CatalogGovernanceError("GOVERNED_PROJECT_MISMATCH")
    return GovernedState(
        project_id=last["project_id"], revision=last["revision"],
        head_hash=last["entry_hash"], catalog_version=last["catalog_version"],
        catalog_digest=last["catalog_digest"],
        active_releases=tuple(map(tuple, last["active_releases"])),
    )


def _persist(path: Path, records: list[dict[str, Any]]) -> None:
    payload = _canonical({"format_version": _FORMAT_VERSION, "records": records})
    if len(payload) > _SIZE_LIMIT:
        raise CatalogGovernanceError("LEDGER_EXCEEDS_SIZE_LIMIT")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix="." + path.name + ".",
            suffix=".pending", delete=False,
        ) as output:
            temporary = output.name
            os.chmod(temporary, 0o600)
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        if path.is_symlink():
            raise CatalogGovernanceError("UNTRUSTED_LEDGER_SYMLINK")
        os.replace(temporary, path)
        temporary = None
        if os.name == "posix":
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def commit_catalog_change(
    path: Path,
    change: CatalogChange,
    authorize: Callable[[CatalogChange, GovernedState | None, frozenset[str]], AuthorizationGrant | None],
) -> GovernedState:
    """Require trusted external policy approval and atomically append one revision.

    The trusted adapter is responsible for authenticated principals, role rules,
    and evidence verification. A caller-controlled callback is NOT authentication.
    """
    if type(change) is not CatalogChange or not callable(authorize):
        raise CatalogGovernanceError("INVALID_CHANGE_OR_AUTHORIZER")
    path = Path(path)
    if not path.parent.is_dir() or path.is_symlink():
        raise CatalogGovernanceError("INVALID_LEDGER_LOCATION")
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CatalogGovernanceError("CONCURRENT_OR_STALE_LEDGER_LOCK") from exc
    try:
        os.close(descriptor)
        prior = _load_records(path)
        previous = prior[-1] if prior else None
        if previous is not None and previous["project_id"] != change.project_id:
            raise CatalogGovernanceError("GOVERNED_PROJECT_MISMATCH")
        revision = 0 if previous is None else previous["revision"]
        head = None if previous is None else previous["entry_hash"]
        if change.expected_revision != revision:
            raise CatalogGovernanceError("STALE_CATALOG_REVISION")
        if change.expected_head_hash != head:
            raise CatalogGovernanceError("STALE_CATALOG_HEAD")
        digest = fingerprint_catalog(change.catalog)
        actions = _actions(previous, change.desired_releases, change.catalog, digest)
        if "ROLLBACK" in actions and not change.allow_rollback:
            raise CatalogGovernanceError("ROLLBACK_NOT_EXPLICITLY_REQUESTED")
        current = None if previous is None else GovernedState(
            project_id=previous["project_id"], revision=previous["revision"],
            head_hash=head, catalog_version=previous["catalog_version"],
            catalog_digest=previous["catalog_digest"],
            active_releases=tuple(map(tuple, previous["active_releases"])),
        )
        grant = authorize(change, current, actions)
        if type(grant) is not AuthorizationGrant:
            raise CatalogGovernanceError("MISSING_TRUSTED_AUTHORIZATION")
        if grant.project_id != change.project_id or not actions <= grant.allowed_actions:
            raise CatalogGovernanceError("INSUFFICIENT_AUTHORIZATION_SCOPE")
        entry: dict[str, Any] = {
            "revision": revision + 1,
            "project_id": change.project_id,
            "catalog_version": change.catalog.catalog_version,
            "catalog_digest": digest,
            "active_releases": [list(item) for item in change.desired_releases],
            "actions": sorted(actions),
            "reason": change.reason,
            "actor_id": grant.actor_id,
            "authorization_ref": grant.authorization_ref,
            "authorization_policy": grant.authorization_policy,
            "occurred_at": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            "previous_hash": head,
        }
        entry["entry_hash"] = _digest(entry)
        _persist(path, prior + [entry])
        return load_governed_state(path, project_id=change.project_id)
    finally:
        lock.unlink(missing_ok=True)


def bind_governed_plan(
    *,
    path: Path,
    catalog: CapabilityCatalog,
    expected_revision: int,
    expected_head_hash: str,
    operation: KernelOperation,
    context: KernelContext,
    plan: KernelPlan,
    bindings: Mapping[str, CapabilityInputBinding],
) -> Mapping[str, KernelInvoker]:
    """Bind ONLY selected releases from the persistent authorized ledger.

    Every invocation rechecks the active head to catch a configuration change
    between planning and actual execution. The technical kernel still owns
    execution and always forbids operational decision authority.
    """
    if type(catalog) is not CapabilityCatalog:
        raise CatalogGovernanceError("INVALID_GOVERNED_CATALOG")
    if type(expected_revision) is not int or expected_revision < 1:
        raise CatalogGovernanceError("INVALID_GOVERNED_REVISION")
    _hash(expected_head_hash, "expected_head_hash")
    path = Path(path)
    state = load_governed_state(path, project_id=catalog.project_id)
    if state.revision != expected_revision or state.head_hash != expected_head_hash:
        raise CatalogGovernanceError("STALE_GOVERNED_EXECUTION")
    if state.catalog_version != catalog.catalog_version or state.catalog_digest != fingerprint_catalog(catalog):
        raise CatalogGovernanceError("GOVERNED_CATALOG_FINGERPRINT_MISMATCH")
    enabled = dict(state.active_releases)
    for capability in plan.capabilities:
        if capability not in enabled:
            raise CatalogGovernanceError(f"GOVERNED_CAPABILITY_DISABLED:{capability}")
    requested = {name: enabled[name] for name in plan.capabilities}
    invokers = bind_catalog_plan(
        catalog=catalog, requested_releases=requested, operation=operation,
        context=context, plan=plan, bindings=bindings,
    )
    def with_recheck(invoker: KernelInvoker) -> KernelInvoker:
        def run(payload: BaseModel, runtime_context: KernelContext):
            current = load_governed_state(path, project_id=catalog.project_id)
            if current.revision != expected_revision or current.head_hash != expected_head_hash:
                raise CatalogGovernanceError("GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION")
            return invoker(payload, runtime_context)
        return run
    return MappingProxyType({cap: with_recheck(inv) for cap, inv in invokers.items()})


__all__ = [
    "AuthorizationGrant", "CatalogChange", "CatalogGovernanceError",
    "GovernedState", "bind_governed_plan", "commit_catalog_change",
    "fingerprint_catalog", "load_governed_state",
]
