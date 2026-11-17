"""F5.8 — prove governed release selections in fully isolated Sales and Procurement.

Reuses the original F5.7 consumer programs, replacing ONLY the release-binding
step with an externally authorized durable ledger. The original PRICE/TCO
calculators, documentary gates and kernel statuses are unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import venv
import zipfile

if __package__:
    from .build_eios_catalog_governance_distribution import audit_wheel as audit_governance
    from .verify_f5_7_capability_catalog import (
        ROOT, WHEEL_SPECS as BASE_WHEEL_SPECS, _program as f5_7_program,
    )
else:
    from build_eios_catalog_governance_distribution import audit_wheel as audit_governance
    from verify_f5_7_capability_catalog import (
        ROOT, WHEEL_SPECS as BASE_WHEEL_SPECS, _program as f5_7_program,
    )

WHEEL_SPECS = {
    **BASE_WHEEL_SPECS,
    "eios-catalog-governance": (
        "governance", "eios_catalog_governance-*.whl", "0.1.0",
        audit_governance,
    ),
}
SELECTED = {
    "sales": (
        "eios-kernel", "eios-input-contracts",
        "eios-capability-catalog", "eios-catalog-governance",
    ),
    "procurement": tuple(WHEEL_SPECS),
}

GOVERNED_BINDING = r"""
from eios.catalog_governance import (
    AuthorizationGrant, CatalogChange, CatalogGovernanceError,
    bind_governed_plan, commit_catalog_change, load_governed_state,
)
governance_path = Path.cwd() / "catalog-history.json"

def external_policy(change, previous, actions):
    # Synthetic test ONLY. Production must authenticate actor, policy and
    # documentary evidence OUTSIDE this neutral governance package.
    assert change.project_id == context.project_id
    return AuthorizationGrant(
        project_id=context.project_id, actor_id="SYNTH-AUTHORIZED-ACTOR",
        authorization_ref="SYNTH-AUTH-REF", authorization_policy="SYNTH-POLICY-v1",
        allowed_actions=actions,
    )

initial = commit_catalog_change(
    governance_path,
    CatalogChange(
        project_id=context.project_id,
        catalog=catalog,
        desired_releases=tuple(sorted(requested_releases.items())),
        expected_revision=0, expected_head_hash=None,
        reason="Synthetic bootstrap for independent capability client",
    ),
    external_policy,
)
assert initial.revision == 1
assert load_governed_state(governance_path, project_id=context.project_id) == initial
invokers = bind_governed_plan(
    path=governance_path, catalog=catalog,
    expected_revision=initial.revision, expected_head_hash=initial.head_hash,
    operation=operation, context=context, plan=plan, bindings=existing,
)
"""

GOVERNANCE_ADVERSARIAL = r"""
# A later authorized configuration disables one release. Previously bound
# invokers must stop, even though the old producer is physically installed.
calls.clear()
desired_after = {name: requested_releases[name] for name in plan.capabilities[:-1]}
changed = commit_catalog_change(
    governance_path,
    CatalogChange(
        project_id=context.project_id,
        catalog=catalog,
        desired_releases=tuple(sorted(desired_after.items())),
        expected_revision=initial.revision,
        expected_head_hash=initial.head_hash,
        reason="Synthetic authorized disabling of last capability",
    ),
    external_policy,
)
assert changed.revision == 2
assert changed.head_hash != initial.head_hash
try:
    invokers[plan.capabilities[0]](operation.payload, context)
except CatalogGovernanceError as exc:
    assert "GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION" in str(exc)
else:
    raise AssertionError("Stale pre-change invoker still ran")
assert calls == []

try:
    bind_governed_plan(
        path=governance_path, catalog=catalog,
        expected_revision=changed.revision, expected_head_hash=changed.head_hash,
        operation=operation, context=context, plan=plan, bindings=existing,
    )
except CatalogGovernanceError as exc:
    assert "GOVERNED_CAPABILITY_DISABLED" in str(exc)
else:
    raise AssertionError("Disabled capability still selected")
assert calls == []

try:
    commit_catalog_change(
        governance_path,
        CatalogChange(
            project_id=context.project_id,
            catalog=catalog,
            desired_releases=tuple(sorted(requested_releases.items())),
            expected_revision=initial.revision, expected_head_hash=initial.head_hash,
            reason="Stale duplicate attempt",
        ),
        external_policy,
    )
except CatalogGovernanceError as exc:
    assert "STALE_CATALOG_REVISION" in str(exc)
else:
    raise AssertionError("Stale revision overwrote the approved selection")
assert calls == []

import json as _json
persisted = _json.loads(governance_path.read_text(encoding="utf-8"))
assert [record["actions"] for record in persisted["records"]] == [
    ["BOOTSTRAP"], ["DISABLE"],
]
assert persisted["records"][1]["previous_hash"] == initial.head_hash
assert persisted["records"][1]["entry_hash"] == changed.head_hash
"""


def _program(domain: str) -> str:
    existing = "entries" if domain == "sales" else "bindings"
    source = f5_7_program(domain)
    original_binding = (
        "invokers = bind_catalog_plan(\n"
        "    catalog=catalog, requested_releases=requested_releases,\n"
        f"    operation=operation, context=context, plan=plan, bindings={existing},\n"
        ")"
    )
    if source.count(original_binding) != 1 or source.count("print(json.dumps({") != 1:
        raise ValueError(f"Changed F5.7 {domain} consumer requires explicit re-audit")
    governed = GOVERNED_BINDING.replace("bindings=existing", f"bindings={existing}")
    updated = source.replace(original_binding, governed, 1)
    adversarial = GOVERNANCE_ADVERSARIAL.replace("bindings=existing", f"bindings={existing}")
    return updated.replace(
        "print(json.dumps({", adversarial + "\nprint(json.dumps({", 1,
    )


def inspect_wheels(selected: dict[str, Path]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for dist, wheel in selected.items():
        WHEEL_SPECS[dist][3](wheel)
        with zipfile.ZipFile(wheel) as archive:
            listed = archive.namelist()
            if len(listed) != len(set(listed)):
                raise ValueError(f"Duplicate ZIP entries in {dist}")
            for name in listed:
                if not name.startswith("eios/"):
                    continue
                if not name.endswith(".py") or name in hashes:
                    raise ValueError(f"Forbidden collision or data in EIOS wheel: {name}")
                origin = ROOT / name
                if not origin.is_file() or origin.read_bytes() != archive.read(name):
                    raise ValueError(f"Wheel did not ship canonical source: {name}")
                hashes[name] = hashlib.sha256(origin.read_bytes()).hexdigest()
    for name in (
        "eios/kernel/execution.py",
        "eios/input_contracts/contracts.py",
        "eios/capability_catalog/catalog.py",
        "eios/catalog_governance/ledger.py",
    ):
        if name not in hashes:
            raise ValueError(f"Missing independent governance dependency: {name}")
    return hashes


def check(wheels: dict[str, Path]) -> dict:
    if set(wheels) != set(WHEEL_SPECS):
        raise ValueError("Expected exactly seven distinct modular EIOS wheels")
    wheels = {dist: file.resolve() for dist, file in wheels.items()}
    reports = {}
    with tempfile.TemporaryDirectory(prefix="eios-f5-8-two-domains-") as workspace:
        for domain in ("sales", "procurement"):
            names = SELECTED[domain]
            selected = {name: wheels[name] for name in names}
            hashes = inspect_wheels(selected)
            working = Path(workspace) / domain
            working.mkdir()
            environment_path = working / "venv"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment_path)
            python = environment_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env["PYTHONNOUSERSITE"] = "1"
            env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            install = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-cache-dir",
                 *(str(selected[name]) for name in names)],
                cwd=working, env=env, capture_output=True, text=True, timeout=240,
            )
            if install.returncode:
                raise RuntimeError(
                    f"{domain}: modular installation failed: {install.stderr[-4000:]}"
                )
            dependencies = subprocess.run(
                [str(python), "-m", "pip", "check"],
                cwd=working, env=env, capture_output=True, text=True, timeout=45,
            )
            if dependencies.returncode:
                raise RuntimeError(f"{domain}: unresolved dependencies: {dependencies.stdout[-2000:]}")
            script = _program(domain)
            if domain == "sales":
                if "eios.core" not in script:
                    raise ValueError("Unchanged Sales isolation probe missing")
            result = subprocess.run(
                [str(python), "-I", "-c", script, json.dumps({
                    "versions": {name: WHEEL_SPECS[name][2] for name in names},
                    "hashes": hashes,
                })],
                cwd=working, env=env, capture_output=True, text=True, timeout=90,
            )
            if result.returncode:
                raise RuntimeError(
                    f"{domain}: governed program failed:\n"
                    + result.stdout[-1200:] + "\n" + result.stderr[-5000:]
                )
            actual = json.loads(result.stdout)
            if actual.get("consumer") != domain or actual.get("module_hashes") != hashes:
                raise ValueError(f"{domain}: wrong consumer or installed module hashes")
            if actual.get("status") != "PARTIALLY_COMPLETED":
                raise ValueError(f"{domain}: technical execution changed")
            if actual.get("operational_path") != "FORBIDDEN":
                raise ValueError(f"{domain}: acquired illegal operational authority")
            if domain == "procurement" and (
                actual.get("price") != "11.00" or actual.get("tco") != "57.50"
            ):
                raise ValueError("Canonical PRICE/TCO results changed")
            reports[domain] = actual
    catalog_sha = "eios/catalog_governance/ledger.py"
    if reports["sales"]["module_hashes"][catalog_sha] != reports["procurement"]["module_hashes"][catalog_sha]:
        raise ValueError("Governance module differs between independent clients")
    return {
        "verification": "F5_8_AUTHORIZED_CATALOG_TWO_DOMAINS_SUCCESS",
        "governance_module_sha256": reports["sales"]["module_hashes"][catalog_sha],
        "sales_without_procurement": True,
        "procurement_price": reports["procurement"]["price"],
        "procurement_tco": reports["procurement"]["tco"],
        "authorized_history": "BOOTSTRAP->DISABLE",
        "stale_revision_and_invoker": "REJECTED",
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for folder in ("kernel", "inputs", "catalog", "governance", "contracts", "price", "tco"):
        parser.add_argument(f"--{folder}-dir", type=Path, default=Path("dist") / folder)
    args = parser.parse_args()
    wheels: dict[str, Path] = {}
    for name, (folder, pattern, _, _) in WHEEL_SPECS.items():
        found = list(getattr(args, folder + "_dir").resolve().glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"Expected exactly one wheel for {name}: {len(found)} found")
        wheels[name] = found[0]
    print(json.dumps(check(wheels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
