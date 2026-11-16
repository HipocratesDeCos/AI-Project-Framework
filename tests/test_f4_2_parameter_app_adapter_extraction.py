"""F4.2.2: the finance activation version source belongs to the application.

The legacy module is an explicit *transitional* import alias. It must be
excluded from F4.3's standalone kernel/parameter distribution.
"""
import ast
from pathlib import Path
import subprocess
import sys

from eios.company_local_finance_version_source import LocalSyntheticFinanceVersionSource
from eios.parameters.local_finance_version_source import (
    LocalSyntheticFinanceVersionSource as LegacyFinanceVersionSource,
)


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_and_legacy_imports_resolve_to_the_same_class():
    assert LegacyFinanceVersionSource is LocalSyntheticFinanceVersionSource
    assert LegacyFinanceVersionSource.source_authentication == "NOT_EXTERNALLY_AUTHENTICATED"
    assert LegacyFinanceVersionSource.operational_path == "FORBIDDEN"
    assert LegacyFinanceVersionSource.decision_authority is False


def test_parameter_modules_have_no_company_imports_except_documented_legacy_bridge():
    parameter_root = ROOT / "eios" / "parameters"
    legacy = parameter_root / "local_finance_version_source.py"
    assert legacy.is_file()
    actual_bridge = ast.parse(legacy.read_text(encoding="utf-8"))
    direct_imports = [
        (node.module, tuple(name.name for name in node.names))
        for node in ast.walk(actual_bridge)
        if isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("eios.company")
    ]
    assert direct_imports == [
        ("eios.company_local_finance_version_source", ("LocalSyntheticFinanceVersionSource",))
    ]
    for path in sorted(parameter_root.glob("*.py")):
        if path == legacy:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("eios.company"), path.name
            if isinstance(node, ast.Import):
                assert all(not alias.name.startswith("eios.company") for alias in node.names), path.name


def test_plain_parameter_public_import_does_not_load_synthetic_company_adapter():
    script = (
        "import sys; import eios.parameters;"
        "assert 'eios.company_local_finance_version_source' not in sys.modules;"
        "assert 'eios.company_finance_parameters' not in sys.modules;"
        "assert 'eios.company_parameter_bindings' not in sys.modules"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_company_adapter_is_the_real_implementation_and_old_path_is_a_bridge():
    application = ROOT / "eios" / "company_local_finance_version_source.py"
    old = ROOT / "eios" / "parameters" / "local_finance_version_source.py"
    source = ast.parse(application.read_text(encoding="utf-8"))
    bridge = ast.parse(old.read_text(encoding="utf-8"))
    assert any(
        isinstance(node, ast.ClassDef)
        and node.name == "LocalSyntheticFinanceVersionSource"
        for node in source.body
    )
    assert not any(
        isinstance(node, ast.ClassDef)
        for node in bridge.body
    )
    assert not any(
        isinstance(node, ast.FunctionDef) and node.name == "get_version_manifest"
        for node in bridge.body
    )
