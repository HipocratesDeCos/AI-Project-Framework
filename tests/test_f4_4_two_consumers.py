"""F4.4 contract: two distinct programs, no second runtime implementation."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.verify_f4_4_two_consumers import (
    CONSUMERS, EXPECTED_FLAGS, MODULE_HASH_KEYS, ROOT,
    validate_result,
)

def test_two_consumers_have_distinct_domains_and_policies():
    assert set(CONSUMERS) == {"purchasing", "sales"}
    assert len({item["project_id"] for item in CONSUMERS.values()}) == 2
    assert len({item["policy"] for item in CONSUMERS.values()}) == 2
    assert set(MODULE_HASH_KEYS) == {
        "eios/kernel/execution.py", "eios/parameters/center.py",
    }
    assert all((ROOT / entry["path"]).is_file() for entry in CONSUMERS.values())


@pytest.mark.parametrize("name,model_name", [
    ("purchasing", "PurchaseDraft"),
    ("sales", "SalesOffer"),
])
def test_independent_adapters_import_only_installed_public_kernel(name, model_name):
    fixture = ROOT / CONSUMERS[name]["path"]
    source = fixture.read_text(encoding="utf-8")
    tree = ast.parse(source)
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    assert model_name in classes
    modules = [
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]
    modules += [
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
        for alias in node.names
    ]
    assert "eios.kernel.execution" in modules
    assert "eios.parameters.center" in modules
    assert not any(
        module.startswith((
            "eios.core", "eios.company", "eios.frontend",
            "eios.rules", "eios.pricing", "eios.finance",
        ))
        for module in modules
    )
    assert "execute_kernel(" in source
    assert "PROJECT_SCOPE_MISMATCH" in source
    assert "decision_authority is False" in source


def _result(name):
    return {
        "consumer": name,
        "project_id": CONSUMERS[name]["project_id"],
        "policy": CONSUMERS[name]["policy"],
        "main_status": CONSUMERS[name]["main_status"],
        "parameter_value": CONSUMERS[name]["parameter_value"],
        "kernel_sha256": "a" * 64,
        "parameters_sha256": "b" * 64,
        **EXPECTED_FLAGS,
    }


@pytest.mark.parametrize("name", ["purchasing", "sales"])
def test_report_contract_rejects_foreign_project_or_policy(name):
    hashes = {"kernel_sha256": "a" * 64, "parameters_sha256": "b" * 64}
    result = _result(name)
    validate_result(name, result, hashes)
    foreign = "sales" if name == "purchasing" else "purchasing"
    for key, value in (
        ("project_id", CONSUMERS[foreign]["project_id"]),
        ("policy", CONSUMERS[foreign]["policy"]),
        ("main_status", "FAILED"),
        ("operational_path", "ALLOWED"),
        ("decision_authority", True),
        ("kernel_sha256", "f" * 64),
    ):
        changed = {**result, key: value}
        with pytest.raises(ValueError, match="violates consumer contract"):
            validate_result(name, changed, hashes)


def test_report_contract_rejects_unverified_flags_or_missing_sources():
    hashes = {"kernel_sha256": "a" * 64, "parameters_sha256": "b" * 64}
    original = _result("purchasing")
    for key in ("scope_rejected", "identity_rejected",
                "reserved_boundaries_blocked", "unauthorized_write_rejected"):
        with pytest.raises(ValueError, match="violates consumer contract"):
            validate_result("purchasing", {**original, key: False}, hashes)
    with pytest.raises(ValueError, match="Invalid contract keys"):
        validate_result("purchasing", {k: v for k, v in original.items() if k != "parameters_sha256"}, hashes)
