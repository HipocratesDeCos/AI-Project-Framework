from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import shutil

import pytest

from eios.core.projection_mock_dataset import (
    ProjectionMockDataset, REQUIRED_COMPONENTS, SCHEMA_ID,
    load_projection_mock_dataset,
)


FIXTURE = Path(__file__).parent / "fixtures" / "projection_only_mock_dataset_01"


def copy_fixture(tmp_path):
    target = tmp_path / "dataset"
    shutil.copytree(FIXTURE, target)
    return target


def manifest(root):
    return json.loads((root / "dataset_manifest.json").read_text(encoding="utf-8"))


def write_manifest(root, value):
    (root / "dataset_manifest.json").write_text(json.dumps(value), encoding="utf-8")


def test_loads_exact_synthetic_fixture_without_domain_construction():
    result = load_projection_mock_dataset(FIXTURE)
    payload = result.to_payload()
    assert payload["schema_id"] == SCHEMA_ID
    assert payload["case_kind"] == "SYNTHETIC"
    assert payload["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert [item["name"] for item in payload["components"]] == list(REQUIRED_COMPONENTS)
    assert len(result.fingerprint) == 64
    assert result.component_bytes("operation").startswith(b'{"case_kind":"SYNTHETIC"')


def test_exports_are_immutable_and_constructor_is_closed():
    result = load_projection_mock_dataset(FIXTURE)
    changed = result.to_payload(); changed["limitations"].clear()
    assert result.to_payload()["limitations"]
    with pytest.raises(TypeError):
        result.components["operation"] = b"changed"
    with pytest.raises(FrozenInstanceError):
        result._material = b"changed"
    with pytest.raises(TypeError):
        ProjectionMockDataset()


@pytest.mark.parametrize(("field", "value"), [
    ("schema_id", "OTHER"), ("schema_version", "1.0"),
    ("case_kind", "PRESENTED_OPERATIONAL"), ("profile", "FULL_FINANCE_BASIC"),
    ("effect_scope", "OPERATIONAL"),
])
def test_rejects_any_noncanonical_boundary_constant(tmp_path, field, value):
    root = copy_fixture(tmp_path); data = manifest(root); data[field] = value
    write_manifest(root, data)
    with pytest.raises(ValueError, match=field):
        load_projection_mock_dataset(root)


def test_rejects_hash_mismatch(tmp_path):
    root = copy_fixture(tmp_path)
    (root / "identity" / "operation.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_projection_mock_dataset(root)


@pytest.mark.parametrize("path", ["../outside.json", "/tmp/outside.json", "identity\\operation.json"])
def test_rejects_unsafe_component_paths(tmp_path, path):
    root = copy_fixture(tmp_path); data = manifest(root)
    data["components"]["operation"]["path"] = path; write_manifest(root, data)
    with pytest.raises(ValueError, match="relative POSIX"):
        load_projection_mock_dataset(root)


def test_rejects_duplicate_component_path(tmp_path):
    root = copy_fixture(tmp_path); data = manifest(root)
    data["components"]["operation"] = dict(data["components"]["decision_context"])
    write_manifest(root, data)
    with pytest.raises(ValueError, match="unique"):
        load_projection_mock_dataset(root)


def test_rejects_incomplete_or_extended_component_inventory(tmp_path):
    root = copy_fixture(tmp_path); data = manifest(root); data["components"].pop("flow_review")
    write_manifest(root, data)
    with pytest.raises(ValueError, match="exact required"):
        load_projection_mock_dataset(root)


def test_rejects_undeclared_file(tmp_path):
    root = copy_fixture(tmp_path); (root / "unexpected.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="undeclared"):
        load_projection_mock_dataset(root)


def test_rejects_symlink(tmp_path):
    root = copy_fixture(tmp_path)
    (root / "link.json").symlink_to(root / "identity" / "operation.json")
    with pytest.raises(ValueError, match="symlinks"):
        load_projection_mock_dataset(root)


def test_rejects_manifest_schema_drift_and_non_path_root(tmp_path):
    root = copy_fixture(tmp_path); data = manifest(root); data["expected_qtg_result"] = "APTO"
    write_manifest(root, data)
    with pytest.raises(ValueError, match="not exact"):
        load_projection_mock_dataset(root)
    with pytest.raises(TypeError):
        load_projection_mock_dataset(str(FIXTURE))
