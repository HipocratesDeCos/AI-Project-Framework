"""F7.1 — verify the declared public API baseline of the neutral EIOS Motor."""
from __future__ import annotations

import dataclasses
import importlib
import inspect
import json
from pathlib import Path
import tomllib
from types import ModuleType
from typing import Any

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "08_Implementacion" / "phase7_public_api_baseline_v0.1.json"


class PublicApiBaselineError(ValueError):
    pass


def fail(code: str) -> None:
    raise PublicApiBaselineError("F7_1_PUBLIC_API_BASELINE_REJECTED:" + code)


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST.relative_to(ROOT)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        fail("INVALID_MANIFEST:" + str(exc))
    if type(data) is not dict:
        fail("MANIFEST_MUST_BE_OBJECT")
    return data


def _function_shape(obj: Any) -> list[list[Any]]:
    signature = inspect.signature(obj)
    result: list[list[Any]] = []
    for parameter in signature.parameters.values():
        result.append([
            parameter.name,
            parameter.kind.name,
            parameter.default is not inspect._empty,
        ])
    return result


def _assert_exports(module: ModuleType, expected: list[str]) -> None:
    actual = getattr(module, "__all__", None)
    if actual is None:
        fail("MISSING___ALL__:" + module.__name__)
    if list(actual) != expected:
        fail("EXPORT_SET_OR_ORDER_CHANGED:" + module.__name__)
    for name in expected:
        if not hasattr(module, name):
            fail("DECLARED_EXPORT_MISSING:" + module.__name__ + ":" + name)


def _assert_pydantic(module: ModuleType, models: dict[str, list[str]]) -> None:
    for name, fields in models.items():
        obj = getattr(module, name, None)
        if not isinstance(obj, type) or not issubclass(obj, BaseModel):
            fail("PYDANTIC_MODEL_MISSING_OR_CHANGED:" + module.__name__ + ":" + name)
        if list(obj.model_fields) != fields:
            fail("PYDANTIC_FIELDS_CHANGED:" + module.__name__ + ":" + name)


def _assert_dataclasses(module: ModuleType, models: dict[str, list[str]]) -> None:
    for name, fields in models.items():
        obj = getattr(module, name, None)
        if not isinstance(obj, type) or not dataclasses.is_dataclass(obj):
            fail("DATACLASS_MISSING_OR_CHANGED:" + module.__name__ + ":" + name)
        actual = [field.name for field in dataclasses.fields(obj)]
        if actual != fields:
            fail("DATACLASS_FIELDS_CHANGED:" + module.__name__ + ":" + name)


def _assert_enums(module: ModuleType, enums: dict[str, list[str]]) -> None:
    for name, values in enums.items():
        obj = getattr(module, name, None)
        if not isinstance(obj, type) or not hasattr(obj, "__members__"):
            fail("ENUM_MISSING_OR_CHANGED:" + module.__name__ + ":" + name)
        actual = [member.value for member in obj]
        if actual != values:
            fail("ENUM_VALUES_CHANGED:" + module.__name__ + ":" + name)


def _assert_functions(module: ModuleType, functions: dict[str, list[list[Any]]]) -> None:
    for name, expected in functions.items():
        obj = getattr(module, name, None)
        if not callable(obj):
            fail("FUNCTION_MISSING:" + module.__name__ + ":" + name)
        if _function_shape(obj) != expected:
            fail("FUNCTION_SIGNATURE_CHANGED:" + module.__name__ + ":" + name)


def _assert_constants(module: ModuleType, constants: dict[str, Any]) -> None:
    for name, expected in constants.items():
        if getattr(module, name, object()) != expected:
            fail("PUBLIC_CONSTANT_CHANGED:" + module.__name__ + ":" + name)


def _assert_distribution(root: Path, package: dict[str, Any]) -> None:
    path = root / package["pyproject"]
    try:
        project = tomllib.loads(path.read_text(encoding="utf-8"))["project"]
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        fail("INVALID_PYPROJECT:" + package["distribution"] + ":" + str(exc))
    if project.get("name") != package["distribution"]:
        fail("DISTRIBUTION_NAME_CHANGED:" + package["distribution"])
    if project.get("version") != package["version"]:
        fail("DISTRIBUTION_VERSION_CHANGED:" + package["distribution"])


def verify(root: Path = ROOT) -> dict[str, Any]:
    data = _load_manifest(root)
    expected_top = {
        "schema", "phase", "baseline_main_sha", "policy", "packages",
        "excluded_from_public_baseline",
    }
    if set(data) != expected_top:
        fail("MANIFEST_SCHEMA_CHANGED")
    if data["schema"] != "EIOS_PUBLIC_API_BASELINE/v0.1" or data["phase"] != "F7.1":
        fail("MANIFEST_IDENTITY_CHANGED")
    if type(data["baseline_main_sha"]) is not str or len(data["baseline_main_sha"]) != 40:
        fail("INVALID_BASELINE_SHA")
    policy = data["policy"]
    if policy != {
        "public_surface_only": True,
        "unlisted_symbols_are_internal": True,
        "semver_does_not_imply_compatibility": True,
        "breaking_change_requires_new_compatibility_evidence": True,
    }:
        fail("PUBLIC_API_POLICY_CHANGED")

    packages = data["packages"]
    if type(packages) is not list or [p.get("distribution") for p in packages] != [
        "eios-kernel",
        "eios-input-contracts",
        "eios-capability-catalog",
        "eios-catalog-governance",
    ]:
        fail("NEUTRAL_PACKAGE_SET_CHANGED")

    for package in packages:
        _assert_distribution(root, package)
        module = importlib.import_module(package["module"])
        _assert_exports(module, package["exports"])
        _assert_functions(module, package["functions"])
        _assert_pydantic(module, package["pydantic_models"])
        _assert_dataclasses(module, package["dataclasses"])
        _assert_enums(module, package["enums"])
        _assert_constants(module, package["constants"])

    excluded = data["excluded_from_public_baseline"]
    if "eios.core" not in excluded or "eios.pricing" not in excluded or "eios.tco" not in excluded:
        fail("BUSINESS_MODULE_EXCLUSION_MISSING")

    return {
        "verification": "F7_1_PUBLIC_API_BASELINE_PASS",
        "phase": "F7.1",
        "neutral_distributions": [p["distribution"] for p in packages],
        "public_modules": [p["module"] for p in packages],
        "public_export_count": sum(len(p["exports"]) for p in packages),
        "breaking_change_requires_new_evidence": True,
        "semver_implies_compatibility": False,
        "production_authorized": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
    }


def main() -> None:
    print(json.dumps(verify(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
