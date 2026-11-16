"""Contract tests for the F4.1 read-only dependency auditor."""
from pathlib import Path

from tools.audit_eios_dependencies import audit, module_name, static_imports


def _write(root: Path, relative: str, content: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_relative_imports_and_module_aliases_are_resolved_without_execution(tmp_path):
    _write(tmp_path, "eios/core/models.py", "class PurchaseOperation: pass\n")
    _write(tmp_path, "eios/core/runner.py",
           "from .models import PurchaseOperation\n"
           "from ..parameters import center\n"
           "import eios.company_example\n"
           "raise RuntimeError('The scanner must never execute this module')\n")
    _write(tmp_path, "eios/parameters/__init__.py", "from . import center\n")
    _write(tmp_path, "eios/parameters/center.py", "VALUE = 1\n")
    _write(tmp_path, "eios/company_example.py", "VALUE = 1\n")
    _write(tmp_path, "pyproject.toml",
           "[project]\nname='toy-eios'\ndependencies=[]\n"
           "[tool.setuptools.packages.find]\ninclude=['eios*']\n")
    result = audit(tmp_path)
    assert result["python_source_count"] == 5
    assert result["parse_failures"] == []
    assert result["module_family_counts"]["named_core"] == 2
    assert result["module_family_counts"]["parameters"] == 2
    assert result["module_family_counts"]["company_application"] == 1
    assert result["internal_import_edge_count"] == 4
    assert {
        (edge["source"], edge["target"])
        for edge in result["direct_core_or_parameters_to_application"]
    } == {("eios.core.runner", "eios.company_example")}
    assert result["core_files_containing_purchase_contract_name"] == [
        "eios/core/models.py",
        "eios/core/runner.py",
    ]
    assert result["packaging"]["name"] == "toy-eios"


def test_package_initializer_relative_import_is_not_attributed_to_parent():
    known = {"eios.parameters", "eios.parameters.center", "eios.center"}
    dependencies = static_imports(
        "from . import center\n", "eios.parameters", known, is_package=True,
    )
    assert dependencies == {"eios.parameters.center"}


def test_nested_relative_import_to_application_is_recorded():
    known = {"eios.company_finance", "eios.core.adapter"}
    sources = static_imports(
        "from ..company_finance import reconcile\n",
        "eios.core.adapter", known,
    )
    assert sources == {"eios.company_finance"}


def test_invalid_syntax_is_reported_not_executed_or_silently_skipped(tmp_path):
    _write(tmp_path, "eios/core/bad.py", "def )invalid(\n")
    result = audit(tmp_path)
    assert result["python_source_count"] == 1
    assert len(result["parse_failures"]) == 1
    assert result["parse_failures"][0]["file"] == "eios/core/bad.py"


def test_relative_module_name_for_init_file(tmp_path):
    _write(tmp_path, "eios/parameters/__init__.py")
    assert module_name(tmp_path / "eios/parameters/__init__.py", tmp_path) == "eios.parameters"


def test_current_repository_is_scanable_without_importing_production_code():
    repository = Path(__file__).resolve().parents[1]
    report = audit(repository)
    assert report["schema"] == "EIOS-F4-1-STATIC-DEPENDENCIES-01"
    assert report["analysis"] == "STATIC_IMPORTS_ONLY_NOT_RUNTIME_OR_PORTABILITY_CERTIFICATION"
    assert report["python_source_count"] >= 1
    assert report["parse_failures"] == []
    assert "named_core" in report["module_family_counts"]
    assert "company_application" in report["module_family_counts"]
    assert report["packaging"]["name"]
    assert isinstance(report["core_to_specialized_or_support"], list)
