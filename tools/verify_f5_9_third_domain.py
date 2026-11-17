"""F5.9 — independent third business domain wheel, not an EIOS app re-label.

Build and audit an externally installable maintenance-example project; combine
it with ONLY four already-audited neutral EIOS wheels in a fresh virtualenv
outside the checkout. Run the third-party project twice in independent working
directories and verify its adversarial governance lifecycle and real algorithm.

All scenario data and approval decisions are synthetic. Hash comparisons
prove byte identity of audited modules, not cryptographic signing or trusted
production provenance.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv
import zipfile

if __package__:
    from .verify_f5_8_governance_two_domains import (
        ROOT, WHEEL_SPECS, inspect_wheels,
    )
else:
    from verify_f5_8_governance_two_domains import (
        ROOT, WHEEL_SPECS, inspect_wheels,
    )

FIXTURE_ROOT = ROOT / "tests/fixtures/f5_9_maintenance_consumer"
PROJECT_NAME = "eios-maintenance-example"
PROJECT_VERSION = "0.1.0"
PROJECT_MODULES = frozenset({
    "eios_maintenance_example/__init__.py",
    "eios_maintenance_example/consumer.py",
})
NEUTRAL_WHEELS = (
    "eios-kernel",
    "eios-input-contracts",
    "eios-capability-catalog",
    "eios-catalog-governance",
)
ALLOWED_EIOS_IMPORTS = frozenset({
    "eios.kernel.execution",
    "eios.input_contracts",
    "eios.capability_catalog",
    "eios.catalog_governance",
})
REQUIRED_DEPENDENCIES = {
    "pydantic": ">=2.0,<3.0",
    "eios-kernel": "==0.1.0",
    "eios-input-contracts": "==0.1.0",
    "eios-capability-catalog": "==0.1.0",
    "eios-catalog-governance": "==0.1.0",
}


def _source_files(root: Path = FIXTURE_ROOT) -> dict[str, Path]:
    result = {key: root / "src" / key for key in PROJECT_MODULES}
    for path in result.values():
        if not path.is_file():
            raise ValueError(f"Missing independent business module: {path}")
    return result


def audit_project_source(root: Path = FIXTURE_ROOT) -> None:
    config = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = config["project"]
    if project["name"] != PROJECT_NAME or project["version"] != PROJECT_VERSION:
        raise ValueError("Independent third-party distribution changed identity")
    dependencies = project["dependencies"]
    if len(dependencies) != len(REQUIRED_DEPENDENCIES):
        raise ValueError("Wrong number of independent third-party dependencies")
    for name, suffix in REQUIRED_DEPENDENCIES.items():
        if sum(item.replace(" ", "").lower() == name + suffix for item in dependencies) != 1:
            raise ValueError(f"Missing exact dependency in independent project: {name}")
    included = {path.relative_to(root / "src").as_posix() for path in (root / "src").rglob("*.py")}
    if included != PROJECT_MODULES:
        raise ValueError("Third-party source bundles unexpected modules")
    for item, path in _source_files(root).items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=item)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                paths = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise ValueError("Third-party consumer must use explicit absolute imports")
                paths = (node.module or "",)
            else:
                continue
            for imported in paths:
                if (imported == "eios" or imported.startswith("eios.")) and (
                    imported not in ALLOWED_EIOS_IMPORTS
                ):
                    raise ValueError(f"Third consumer imported a business-specific EIOS module: {imported}")


def _module_bytes_from_wheel(archive: zipfile.ZipFile, path: str) -> bytes:
    return archive.read(path)


def audit_project_wheel(wheel: Path, root: Path = FIXTURE_ROOT) -> dict[str, str]:
    audit_project_source(root)
    hashes = {}
    with zipfile.ZipFile(wheel) as archive:
        all_names = archive.namelist()
        if len(all_names) != len(set(all_names)):
            raise ValueError("Duplicate third-consumer wheel member")
        names = set(all_names)
        packaged_py = {item for item in names if item.endswith(".py")}
        if packaged_py != PROJECT_MODULES:
            raise ValueError("Third-consumer wheel Python modules differ from source")
        if any(
            item.startswith("eios/") or ".data/" in item
            or (item.startswith("eios_maintenance_example/") and item not in PROJECT_MODULES)
            for item in names
        ):
            raise ValueError("Third consumer illegally bundles EIOS code or extraneous files")
        metas = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metas) != 1 or not metas[0].startswith(
            "eios_maintenance_example-0.1.0.dist-info/"
        ):
            raise ValueError("Third-party wheel metadata path drift")
        lines = archive.read(metas[0]).decode("utf-8").splitlines()
        if "Name: eios-maintenance-example" not in lines or "Version: 0.1.0" not in lines:
            raise ValueError("Third-party wheel identity/version drift")
        dependencies: dict[str, str] = {}
        for item in lines:
            if not item.startswith("Requires-Dist:"):
                continue
            match = re.fullmatch(
                r"Requires-Dist:\s*([A-Za-z0-9_-]+)\s*(.*)",
                item,
            )
            if match is None:
                raise ValueError("Invalid third-party dependency metadata")
            key = match.group(1).lower().replace("_", "-")
            if key in dependencies:
                raise ValueError("Duplicate third-party dependency metadata")
            dependencies[key] = match.group(2).replace(" ", "")
        if set(dependencies) != set(REQUIRED_DEPENDENCIES):
            raise ValueError("Third-party wheel dependency scope changed")
        for name, required in REQUIRED_DEPENDENCIES.items():
            value = dependencies[name]
            if value.startswith("(") and value.endswith(")"):
                value = value[1:-1]
            if set(value.split(",")) != set(required.split(",")):
                raise ValueError(f"Third-party wheel dependency not exact: {name}")
        for name, original in _source_files(root).items():
            zipped = _module_bytes_from_wheel(archive, name)
            if zipped != original.read_bytes():
                raise ValueError(f"Third-party wheel differs from canonical fixture: {name}")
            hashes[name] = hashlib.sha256(zipped).hexdigest()
    return hashes


def build_project_wheel(destination: Path, source: Path = FIXTURE_ROOT) -> Path:
    audit_project_source(source)
    destination.mkdir(parents=True, exist_ok=True)
    staged = destination / "fixture"
    shutil.copytree(source, staged)
    build_path = destination / "wheelhouse"
    build_path.mkdir()
    command = [
        sys.executable, "-m", "pip", "wheel", "--no-deps",
        "--no-build-isolation", "--wheel-dir", str(build_path), str(staged),
    ]
    built = subprocess.run(
        command, cwd=destination, capture_output=True, text=True, timeout=150,
    )
    if built.returncode:
        raise RuntimeError("Cannot package independent third project: " + built.stderr[-3500:])
    wheels = list(build_path.glob("eios_maintenance_example-*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected one separately built maintenance wheel")
    audit_project_wheel(wheels[0], source)
    return wheels[0]


def _installed_hash_check(
    python: Path,
    working: Path,
    expected: dict[str, str],
    versions: dict[str, str],
    environment: dict[str, str],
) -> None:
    source = r"""
from importlib import import_module, metadata, util
import hashlib, json, sys
from pathlib import Path
manifest = json.loads(sys.argv[1])
for dist, version in manifest["versions"].items():
    assert metadata.version(dist) == version, dist
for rel, digest in manifest["modules"].items():
    name = rel[:-3].replace("/", ".").removesuffix(".__init__")
    module = import_module(name)
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == digest, rel
for name in ("eios.core", "eios.pricing", "eios.tco", "eios.company_app"):
    assert util.find_spec(name) is None, name
for name in ("eios-mvp", "eios-price-procurement", "eios-tco-procurement", "eios-contracts-procurement"):
    try: metadata.version(name)
    except metadata.PackageNotFoundError: continue
    raise AssertionError(name)
print(json.dumps({"installed_hashes": manifest["modules"], "independent": True}))
"""
    verify = subprocess.run(
        [str(python), "-I", "-c", source,
         json.dumps({"modules": expected, "versions": versions})],
        cwd=working, env=environment, capture_output=True, text=True, timeout=40,
    )
    if verify.returncode:
        raise RuntimeError(
            "Third project installed file or dependency mismatch: "
            + verify.stdout[-1000:] + "\n" + verify.stderr[-2500:]
        )
    actual = json.loads(verify.stdout)
    if actual.get("installed_hashes") != expected or actual.get("independent") is not True:
        raise ValueError("Third project installed module hashes do not match source")


def check(wheels: dict[str, Path]) -> dict:
    if set(wheels) != set(NEUTRAL_WHEELS):
        raise ValueError("F5.9 allows exactly the four neutral EIOS wheels")
    selected = {name: wheels[name].resolve() for name in NEUTRAL_WHEELS}
    neutral_hashes = inspect_wheels(selected)
    for forbidden in (
        "eios/core/models.py", "eios/pricing/models.py", "eios/tco/engine.py",
    ):
        if forbidden in neutral_hashes:
            raise ValueError("Procurement model leaked into third-domain neutral install")

    with tempfile.TemporaryDirectory(prefix="eios-f5-9-third-external-") as directory:
        root = Path(directory)
        maintenance_wheel = build_project_wheel(root / "build")
        standalone_hashes = audit_project_wheel(maintenance_wheel)
        hashes = {**neutral_hashes, **standalone_hashes}
        if len(hashes) != len(neutral_hashes) + len(standalone_hashes):
            raise ValueError("Third-party module overlaps a neutral EIOS module")
        environment_path = root / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment_path)
        python = environment_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        wheels_to_install = [str(selected[dist]) for dist in NEUTRAL_WHEELS] + [str(maintenance_wheel)]
        installed = subprocess.run(
            [str(python), "-m", "pip", "install", "--no-cache-dir", *wheels_to_install],
            cwd=root, env=env, capture_output=True, text=True, timeout=240,
        )
        if installed.returncode:
            raise RuntimeError("Third-party wheel installation failed: " + installed.stderr[-4500:])
        checked = subprocess.run(
            [str(python), "-m", "pip", "check"], cwd=root,
            env=env, capture_output=True, text=True, timeout=45,
        )
        if checked.returncode:
            raise RuntimeError("Third-party dependency check failed: " + checked.stdout[-2500:])
        versions = {name: WHEEL_SPECS[name][2] for name in NEUTRAL_WHEELS}
        versions[PROJECT_NAME] = PROJECT_VERSION
        results: list[dict] = []
        for index in (1, 2):
            working = root / f"execution-{index}"
            working.mkdir()
            _installed_hash_check(python, working, hashes, versions, env)
            run = subprocess.run(
                [str(python), "-I", "-m", "eios_maintenance_example.consumer"],
                cwd=working, env=env, capture_output=True, text=True, timeout=75,
            )
            if run.returncode:
                raise RuntimeError(
                    f"Independent maintenance consumer run {index} failed:\n"
                    + run.stdout[-1000:] + "\n" + run.stderr[-4500:]
                )
            try:
                response = json.loads(run.stdout)
            except json.JSONDecodeError as exc:
                raise ValueError("Third-party consumer did not return JSON") from exc
            results.append(response)
            if not (working / "synthetic_maintenance_catalog.json").is_file():
                raise ValueError("Independent business consumer did not persist governance ledger")
            if (working / "synthetic_maintenance_catalog.json.lock").exists():
                raise ValueError("Unexpected persistent change lock after completion")
        if results[0] != results[1]:
            raise ValueError("Same independently installed client produced inconsistent outcomes")
        result = results[0]
        required_true = (
            "false_grants_rejected", "cross_project_isolation",
            "schema_migration_rejected", "insufficient_scope_rejected",
            "stale_revision_rejected", "stale_invoker_rejected",
            "tampered_copy_rejected", "producer_input_isolated",
        )
        if any(result.get(field) is not True for field in required_true):
            raise ValueError("Missing fail-closed adversarial evidence")
        if result.get("consumer") != "maintenance":
            raise ValueError("Expected maintenance third domain")
        if result.get("initial_status") != "PARTIALLY_COMPLETED":
            raise ValueError("Missing documentary safety evidence was not withheld")
        if result.get("later_status") != "COMPLETED":
            raise ValueError("Authorized remaining technical capability did not run")
        if result.get("operational_path") != "FORBIDDEN" or result.get("decision_authority") is not False:
            raise ValueError("Third domain acquired unauthorized operational decision authority")
        if result.get("authorization") != "SYNTHETIC_TEST_DOUBLE_ONLY":
            raise ValueError("Third domain incorrectly claimed real business authorization")

        return {
            "verification": "F5_9_THIRD_DOMAIN_PORTABILITY_VERIFIED",
            "third_domain": "equipment_maintenance",
            "independently_built_wheel": PROJECT_NAME + "==" + PROJECT_VERSION,
            "installed_distributions": [*NEUTRAL_WHEELS, PROJECT_NAME],
            "no_procurement_sales_modules": True,
            "neutral_module_sha256": neutral_hashes,
            "third_party_module_sha256": standalone_hashes,
            "isolated_repeat_runs": 2,
            "results": result,
            "operational_path": "FORBIDDEN",
            "real_documentary_admission": "NOT_TESTED",
            "real_approver_authentication": "NOT_TESTED",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for directory in ("kernel", "inputs", "catalog", "governance"):
        parser.add_argument(f"--{directory}-dir", type=Path, default=Path("dist") / directory)
    arguments = parser.parse_args()
    wheels = {}
    for dist in NEUTRAL_WHEELS:
        directory, pattern, _, _ = WHEEL_SPECS[dist]
        found = list(getattr(arguments, directory + "_dir").resolve().glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"Expected exactly one wheel for {dist}, found {len(found)}")
        wheels[dist] = found[0]
    print(json.dumps(check(wheels), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
