"""F4.3: distribution is an audited subset, never a second kernel runtime."""
import ast
from pathlib import Path
import tomllib
import zipfile

import pytest

from tools.build_eios_kernel_distribution import (
    METADATA_FILE, SOURCE_FILES, audit_wheel,
    stage_distribution, verify_source_dependencies,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    Path("eios/kernel/execution.py"),
    Path("eios/parameters/center.py"),
}


def test_only_neutral_runtime_and_parameter_center_are_owned():
    assert set(SOURCE_FILES) == EXPECTED
    verify_source_dependencies(ROOT)
    metadata = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert metadata["project"]["name"] == "eios-kernel"
    assert metadata["project"]["dependencies"] == ["pydantic>=2.0,<3.0"]
    assert metadata["tool"]["setuptools"]["packages"]["find"]["namespaces"] is True


def test_staging_copies_canonical_sources_once_with_no_app_code(tmp_path):
    stage_distribution(tmp_path)
    files = {p.relative_to(tmp_path / "src") for p in (tmp_path / "src").rglob("*.py")}
    assert files == EXPECTED
    for relative in SOURCE_FILES:
        assert (tmp_path / "src" / relative).read_bytes() == (ROOT / relative).read_bytes()
    assert not list((tmp_path / "src").rglob("__init__.py"))
    assert not list((tmp_path / "src").rglob("*company*"))


@pytest.mark.parametrize("syntax", [
    "import eios.core.models",
    "from eios.company_finance_parameters import IDS",
    "from .private import helper",
])
def test_build_fails_closed_on_forbidden_dependencies(tmp_path, syntax):
    for relative in SOURCE_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x = 1", encoding="utf-8")
    first = tmp_path / SOURCE_FILES[0]
    first.write_text(syntax + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="dependency forbidden"):
        verify_source_dependencies(tmp_path)


def _fake_wheel(path, python_paths, dependencies=("Requires-Dist: pydantic<3,>=2",)):
    with zipfile.ZipFile(path, "w") as archive:
        for module in python_paths:
            archive.writestr(module, "# fake wheel payload\n")
        archive.writestr(
            "eios_kernel-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.2\nName: eios-kernel\nVersion: 0.1.0\n"
            + "\n".join(dependencies) + "\n",
        )


def test_wheel_allowlist_accepts_only_approved_files(tmp_path):
    wheel = tmp_path / "test.whl"
    names = {str(path).replace("\\", "/") for path in EXPECTED}
    _fake_wheel(wheel, names)
    audit_wheel(wheel)
    _fake_wheel(wheel, names | {"eios/company_finance_parameters.py"})
    with pytest.raises(ValueError, match="Unexpected Python modules"):
        audit_wheel(wheel)


def test_wheel_rejects_missing_contract_and_extra_dependencies(tmp_path):
    wheel = tmp_path / "test.whl"
    names = {str(path).replace("\\", "/") for path in EXPECTED}
    _fake_wheel(wheel, names - {"eios/parameters/center.py"})
    with pytest.raises(ValueError, match="Unexpected Python modules"):
        audit_wheel(wheel)
    _fake_wheel(wheel, names, dependencies=(
        "Requires-Dist: pydantic>=2", "Requires-Dist: openpyxl>=3",
    ))
    with pytest.raises(ValueError, match="Only the required Pydantic"):
        audit_wheel(wheel)


def test_no_copy_or_modification_to_legacy_project_metadata():
    legacy = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert legacy["project"]["name"] == "eios-mvp"
    assert "openpyxl>=3.1,<4.0" in legacy["project"]["dependencies"]
    assert not (ROOT / "eios/kernel/__init__.py").exists()
