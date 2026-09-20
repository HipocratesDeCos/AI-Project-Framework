"""Fail-closed structural admission for PROJECTION_ONLY synthetic fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from types import MappingProxyType
from typing import Mapping


SCHEMA_ID = "EIOS-PROJECTION-ONLY-MOCK-DATASET-01"
SCHEMA_VERSION = "0.1"
REQUIRED_COMPONENTS = (
    "operation", "decision_context", "finance_input", "parameter_resolutions",
    "payment_documents", "required_installment_calendar", "projection_criteria",
    "treasury_material", "treasury_mandate", "treasury_review", "flow_inventory",
    "flow_mandate", "flow_review",
)
_MANIFEST_KEYS = {
    "schema_id", "schema_version", "dataset_id", "case_kind", "profile",
    "effect_scope", "components", "limitations",
}
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _nonempty(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _relative_path(value: object, field: str) -> PurePosixPath:
    text = _nonempty(value, field)
    path = PurePosixPath(text)
    if ("\\" in text or path.is_absolute() or str(path) != text
            or any(part in {"", ".", ".."} for part in path.parts)):
        raise ValueError(f"{field} must be a normalized relative POSIX path")
    return path


@dataclass(frozen=True, init=False)
class ProjectionMockDataset:
    """Immutable, hash-bound structural material; never an operational input."""

    _material: bytes
    _components: tuple[tuple[str, str, bytes], ...]
    fingerprint: str

    def __init__(self):
        raise TypeError("Use load_projection_mock_dataset")

    def to_payload(self) -> dict:
        return json.loads(self._material.decode("utf-8"))

    @property
    def components(self) -> Mapping[str, bytes]:
        return MappingProxyType({name: content for name, _, content in self._components})

    def component_bytes(self, name: str) -> bytes:
        for component_name, _, content in self._components:
            if component_name == name:
                return content
        raise KeyError(name)


def load_projection_mock_dataset(root: Path) -> ProjectionMockDataset:
    """Validate and load one exact synthetic package without domain construction."""

    if not isinstance(root, Path):
        raise TypeError("root must be pathlib.Path")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("root must be a non-symlink directory")
    entries = tuple(root.rglob("*"))
    if any(entry.is_symlink() for entry in entries):
        raise ValueError("dataset package must not contain symlinks")
    manifest_path = root / "dataset_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("dataset_manifest.json is required")
    try:
        manifest = json.loads(manifest_path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("dataset manifest must be valid UTF-8 JSON") from exc
    if type(manifest) is not dict or set(manifest) != _MANIFEST_KEYS:
        raise ValueError("dataset manifest fields are not exact")
    constants = {
        "schema_id": SCHEMA_ID, "schema_version": SCHEMA_VERSION,
        "case_kind": "SYNTHETIC", "profile": "PROJECTION_ONLY",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
    }
    for field, expected in constants.items():
        if manifest[field] != expected:
            raise ValueError(f"{field} must equal {expected}")
    _nonempty(manifest["dataset_id"], "dataset_id")
    limitations = manifest["limitations"]
    if (type(limitations) is not list or not limitations
            or any(type(item) is not str or not item.strip() for item in limitations)):
        raise ValueError("limitations must be a non-empty list of non-empty strings")
    components = manifest["components"]
    if type(components) is not dict or set(components) != set(REQUIRED_COMPONENTS):
        raise ValueError("components must contain the exact required logical inventory")
    loaded: list[tuple[str, str, bytes]] = []
    declared_paths: set[str] = set()
    for name in REQUIRED_COMPONENTS:
        record = components[name]
        if type(record) is not dict or set(record) != {"path", "sha256"}:
            raise ValueError(f"components.{name} fields are not exact")
        relative = _relative_path(record["path"], f"components.{name}.path")
        relative_text = relative.as_posix()
        if relative_text == "dataset_manifest.json" or relative_text in declared_paths:
            raise ValueError("component paths must be unique and exclude the manifest")
        declared_paths.add(relative_text)
        expected_hash = record["sha256"]
        if type(expected_hash) is not str or _SHA256.fullmatch(expected_hash) is None:
            raise ValueError(f"components.{name}.sha256 must be lowercase SHA-256")
        candidate = root.joinpath(*relative.parts)
        if not candidate.is_file():
            raise ValueError(f"component file is missing: {relative_text}")
        content = candidate.read_bytes()
        if sha256(content).hexdigest() != expected_hash:
            raise ValueError(f"component hash mismatch: {name}")
        loaded.append((name, relative_text, content))
    actual_files = {entry.relative_to(root).as_posix() for entry in entries if entry.is_file()}
    expected_files = {"dataset_manifest.json", *declared_paths}
    if actual_files != expected_files:
        raise ValueError("dataset package contains missing or undeclared files")
    payload = {
        "schema_id": manifest["schema_id"], "schema_version": manifest["schema_version"],
        "dataset_id": manifest["dataset_id"], "case_kind": manifest["case_kind"],
        "profile": manifest["profile"], "effect_scope": manifest["effect_scope"],
        "limitations": list(limitations),
        "components": [{"name": name, "path": path,
                        "sha256": sha256(content).hexdigest(), "size_bytes": len(content)}
                       for name, path, content in loaded],
    }
    material = _canonical(payload)
    result = object.__new__(ProjectionMockDataset)
    object.__setattr__(result, "_material", material)
    object.__setattr__(result, "_components", tuple(loaded))
    object.__setattr__(result, "fingerprint", sha256(material).hexdigest())
    return result
