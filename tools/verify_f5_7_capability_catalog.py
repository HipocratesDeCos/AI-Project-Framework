"""F5.7 — prove exact capability release catalog in two isolated real clients.

Reuses both F5.6 synthetic operational programs (including canonical PRICE/TCO
and documentary insufficiency), replacing only their input binding step with
the explicit F5.7 release catalog. No second business calculations.
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
    from .build_eios_capability_catalog_distribution import audit_wheel as audit_catalog
    from .verify_f5_6_two_domains import (
        ROOT, PROCUREMENT, SALES, WHEEL_SPECS as BASE_WHEEL_SPECS,
    )
else:
    from build_eios_capability_catalog_distribution import audit_wheel as audit_catalog
    from verify_f5_6_two_domains import (
        ROOT, PROCUREMENT, SALES, WHEEL_SPECS as BASE_WHEEL_SPECS,
    )

WHEEL_SPECS = {
    **BASE_WHEEL_SPECS,
    "eios-capability-catalog": (
        "catalog", "eios_capability_catalog-*.whl", "0.1.0", audit_catalog,
    ),
}
SELECTED = {
    "sales": ("eios-kernel", "eios-input-contracts", "eios-capability-catalog"),
    "procurement": tuple(WHEEL_SPECS),
}

CATALOG_BINDING = r"""
from eios.capability_catalog import (
    CapabilityCatalog, CapabilityCatalogError, CapabilityRelease,
    bind_catalog_plan,
)
from dataclasses import replace
assert metadata.version("eios-capability-catalog") == "0.1.0"
catalog = CapabilityCatalog(
    project_id=context.project_id,
    catalog_version="1.0.0",
    releases=tuple(
        CapabilityRelease(
            project_id=context.project_id,
            capability=capability,
            release_version="1.0.0",
            schema_id=existing[capability].spec.schema_id,
            compatible_schema_versions=("v1",),
            payload_type=type(operation.payload),
            policy_version=plan.policy_version,
        )
        for capability in plan.capabilities
    ),
)
requested_releases = {name: "1.0.0" for name in plan.capabilities}
invokers = bind_catalog_plan(
    catalog=catalog, requested_releases=requested_releases,
    operation=operation, context=context, plan=plan, bindings=existing,
)
"""

ADVERSARIAL = r"""
# A synthetic plan with a version not in the catalog must fail before invoking
# any producer, even if the code for that producer is physically installed.
calls.clear()
for forbidden in ("1.0.1", "2.0.0"):
    try:
        bind_catalog_plan(
            catalog=catalog,
            requested_releases={**requested_releases, plan.capabilities[-1]: forbidden},
            operation=operation, context=context, plan=plan, bindings=existing,
        )
    except CapabilityCatalogError as exc:
        assert "RELEASE_NOT_REGISTERED" in str(exc)
    else:
        raise AssertionError("Unregistered capability release accepted")
assert calls == []

# Schema versions are never inferred from release numbering.
broken = replace(catalog.releases[-1], compatible_schema_versions=("v2",))
catalog_incompatible = replace(
    catalog, releases=(*catalog.releases[:-1], broken),
)
try:
    bind_catalog_plan(
        catalog=catalog_incompatible, requested_releases=requested_releases,
        operation=operation, context=context, plan=plan, bindings=existing,
    )
except CapabilityCatalogError as exc:
    assert "SCHEMA_VERSION_INCOMPATIBLE" in str(exc)
else:
    raise AssertionError("Incompatible input schema accepted")
assert calls == []

# Disable one selected capability in a newer catalog snapshot.
disabled = replace(catalog.releases[-1], enabled=False)
catalog_disabled = replace(
    catalog, catalog_version="1.0.1",
    releases=(*catalog.releases[:-1], disabled),
)
try:
    bind_catalog_plan(
        catalog=catalog_disabled, requested_releases=requested_releases,
        operation=operation, context=context, plan=plan, bindings=existing,
    )
except CapabilityCatalogError as exc:
    assert "RELEASE_DISABLED" in str(exc)
else:
    raise AssertionError("Disabled catalog entry invoked")
assert calls == []
"""


def _program(domain: str) -> str:
    """Replace exactly one F5.6 bind call, preserving each real domain test."""
    original = SALES if domain == "sales" else PROCUREMENT
    key = "entries" if domain == "sales" else "bindings"
    needle = (
        "invokers = bind_capability_inputs(\n"
        f"    operation=operation, context=context, plan=plan, bindings={key},\n"
        ")"
    )
    if original.count(needle) != 1:
        raise ValueError(f"F5.6 consumer binding changed for {domain}; audit required")
    if original.count("print(json.dumps({") != 1:
        raise ValueError(f"F5.6 consumer reporting changed for {domain}; audit required")
    bound = CATALOG_BINDING.replace("existing[", f"{key}[").replace(
        "bindings=existing", f"bindings={key}"
    )
    # Existing original F5.6 tests run unchanged except the binding function.
    transformed = original.replace(needle, bound, 1)
    tested = ADVERSARIAL.replace("bindings=existing", f"bindings={key}")
    return transformed.replace("print(json.dumps({", tested + "\nprint(json.dumps({", 1)


def inspect_wheels(selected: dict[str, Path]) -> dict[str, str]:
    """Guarantee a unique owner per installed EIOS path and canonical wheel bytes."""
    hashes: dict[str, str] = {}
    for name, path in selected.items():
        WHEEL_SPECS[name][3](path)
        with zipfile.ZipFile(path) as archive:
            listed = archive.namelist()
            if len(listed) != len(set(listed)):
                raise ValueError(f"Duplicate wheel ZIP path in {name}")
            for item in listed:
                if not item.startswith("eios/"):
                    continue
                if item in hashes:
                    raise ValueError(f"Cross-wheel module collision: {item}")
                if not item.endswith(".py"):
                    raise ValueError(f"Unapproved EIOS wheel payload: {item}")
                canonical = ROOT / item
                if not canonical.is_file() or canonical.read_bytes() != archive.read(item):
                    raise ValueError(f"Drift from canonical source: {item}")
                hashes[item] = hashlib.sha256(canonical.read_bytes()).hexdigest()
    for item in (
        "eios/kernel/execution.py",
        "eios/input_contracts/contracts.py",
        "eios/capability_catalog/catalog.py",
    ):
        if item not in hashes:
            raise ValueError(f"Missing neutral runtime module: {item}")
    return hashes


def check(wheels: dict[str, Path]) -> dict:
    if set(wheels) != set(WHEEL_SPECS):
        raise ValueError("F5.7 requires all six audited wheels")
    wheels = {key: value.resolve() for key, value in wheels.items()}
    results = {}
    with tempfile.TemporaryDirectory(prefix="eios-f5-7-isolated-") as tmp:
        for domain in ("sales", "procurement"):
            chosen = SELECTED[domain]
            selected = {name: wheels[name] for name in chosen}
            hashes = inspect_wheels(selected)
            root = Path(tmp) / domain
            root.mkdir()
            environment_path = root / "venv"
            venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment_path)
            python = environment_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env["PYTHONNOUSERSITE"] = "1"
            env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            installed = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-cache-dir",
                 *(str(selected[name]) for name in chosen)],
                cwd=root, env=env, capture_output=True, text=True, timeout=210,
            )
            if installed.returncode:
                raise RuntimeError(f"{domain}: pip installation failed: {installed.stderr[-3000:]}")
            deps = subprocess.run(
                [str(python), "-m", "pip", "check"], cwd=root,
                env=env, capture_output=True, text=True, timeout=45,
            )
            if deps.returncode:
                raise RuntimeError(f"{domain}: dependency conflict: {deps.stdout[-2500:]}")
            output = subprocess.run(
                [str(python), "-I", "-c", _program(domain), json.dumps({
                    "versions": {name: WHEEL_SPECS[name][2] for name in chosen},
                    "hashes": hashes,
                })],
                cwd=root, env=env, capture_output=True, text=True, timeout=85,
            )
            if output.returncode:
                raise RuntimeError(
                    f"{domain}: selected catalog failed:\n"
                    + output.stdout[-1200:] + "\n" + output.stderr[-4500:]
                )
            result = json.loads(output.stdout)
            if result.get("consumer") != domain or result.get("module_hashes") != hashes:
                raise ValueError(f"{domain}: wrong case or noncanonical files")
            if result.get("status") != "PARTIALLY_COMPLETED":
                raise ValueError(f"{domain}: unexpected technical status")
            if result.get("operational_path") != "FORBIDDEN":
                raise ValueError(f"{domain}: illegal operational authority")
            if domain == "procurement" and (
                result.get("price") != "11.00" or result.get("tco") != "57.50"
            ):
                raise ValueError("Existing canonical PRICE/TCO values changed")
            results[domain] = result
    if results["sales"]["module_hashes"]["eios/capability_catalog/catalog.py"] != (
        results["procurement"]["module_hashes"]["eios/capability_catalog/catalog.py"]
    ):
        raise ValueError("Sales and procurement ran different catalog bytes")
    return {
        "verification": "F5_7_EXACT_RELEASE_CATALOG_TWO_DOMAINS_SUCCESS",
        "kernel_sha256": results["sales"]["module_hashes"]["eios/kernel/execution.py"],
        "catalog_sha256": results["sales"]["module_hashes"]["eios/capability_catalog/catalog.py"],
        "sales_without_procurement": True,
        "procurement_price": results["procurement"]["price"],
        "procurement_tco": results["procurement"]["tco"],
        "incompatible_versions_rejected": True,
        "disabled_release_rejected": True,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for folder in ("kernel", "inputs", "catalog", "contracts", "price", "tco"):
        parser.add_argument(f"--{folder}-dir", type=Path, default=Path("dist") / folder)
    args = parser.parse_args()
    wheels = {}
    for name, (folder, pattern, _, _) in WHEEL_SPECS.items():
        found = list(getattr(args, folder + "_dir").resolve().glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"Expected exactly one wheel for {name}: {len(found)} found")
        wheels[name] = found[0]
    print(json.dumps(check(wheels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
