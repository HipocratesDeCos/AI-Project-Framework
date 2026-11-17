"""F5.4 audit: optional canonical procurement PRICE, no second algorithm."""
from __future__ import annotations

from pathlib import Path
import shutil
import tomllib
import zipfile

import pytest

from tools.build_eios_price_distribution import (
    ALLOWED_INTERNAL_MODULES, METADATA_FILE, ROOT, SOURCE_FILES,
    audit_wheel, stage_distribution, verify_source_dependencies,
)
from tools.verify_f5_4_optional_price import (
    ensure_no_shared_paths, installed_paths,
)

PRICING_FILES = {
    Path("eios/pricing/" + name)
    for name in (
        "__init__.py", "aggregation.py", "company_coverage.py",
        "comparable_reference.py", "critical_baseline.py", "engine.py",
        "historical_comparability.py", "historical_reference.py", "models.py",
        "recommended_ceiling.py", "representativeness.py", "sufficiency.py",
    )
}
CANONICAL = PRICING_FILES | {
    Path("eios/core/validation.py"),
}


def test_manifest_and_transitive_dependencies_are_fully_audited():
    assert set(SOURCE_FILES) == CANONICAL
    verify_source_dependencies()
    assert "eios.core.models" in ALLOWED_INTERNAL_MODULES
    assert "eios.core.validation" in ALLOWED_INTERNAL_MODULES
    assert "eios.pricing.company_coverage" in ALLOWED_INTERNAL_MODULES
    assert "eios.pricing.historical_comparability" in ALLOWED_INTERNAL_MODULES
    cfg = tomllib.loads((ROOT / METADATA_FILE).read_text(encoding="utf-8"))
    assert cfg["project"]["name"] == "eios-price-procurement"
    assert cfg["project"]["version"] == "0.2.0"
    assert cfg["project"]["dependencies"] == ["pydantic>=2.0,<3.0", "eios-contracts-procurement==0.1.0"]
    assert cfg["tool"]["setuptools"]["packages"]["find"]["namespaces"] is True
    legacy = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert legacy["project"]["name"] == "eios-mvp"


def test_staging_has_exact_canonical_files_and_no_extra_price_engine(tmp_path):
    stage_distribution(tmp_path)
    found = {
        p.relative_to(tmp_path / "src") for p in (tmp_path / "src").rglob("*.py")
    }
    assert found == CANONICAL
    for path in SOURCE_FILES:
        assert (tmp_path / "src" / path).read_bytes() == (ROOT / path).read_bytes()
    assert not (tmp_path / "src" / "eios/kernel/execution.py").exists()
    assert not (tmp_path / "src" / "eios/quality/gate.py").exists()
    assert not (tmp_path / "src" / "eios/company_app.py").exists()


@pytest.mark.parametrize("injected", (
    "from eios.rules.pricing import evaluate_rule",
    "import eios.company_app",
    "from eios.kernel.execution import execute_kernel",
    "from .fictitious_calculator import calculate",
    "from ..core.models import PurchaseOperation",
))
def test_new_unbundled_business_dependency_is_rejected(tmp_path, injected):
    for path in SOURCE_FILES:
        dest = tmp_path / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, dest)
    target = tmp_path / "eios/pricing/engine.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\n" + injected + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Forbidden"):
        verify_source_dependencies(tmp_path)


def _synthetic_wheel(path, sources, *, dependencies=(
    "Requires-Dist: pydantic>=2,<3",
    "Requires-Dist: eios-contracts-procurement==0.1.0",
)):
    with zipfile.ZipFile(path, "w") as archive:
        for relative in sources:
            archive.writestr(relative, "# synthetic module\n")
        archive.writestr(
            "eios_price_procurement-0.2.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: eios-price-procurement\nVersion: 0.2.0\n"
            + "\n".join(dependencies) + "\n",
        )


def test_wheel_audit_accepts_closed_file_set_and_dependencies(tmp_path):
    wheel = tmp_path / "price.whl"
    _synthetic_wheel(wheel, {p.as_posix() for p in SOURCE_FILES})
    audit_wheel(wheel)


@pytest.mark.parametrize("extra", (
    "eios/pricing/other_engine.py",
    "eios/core/execution_boundary.py",
    "eios/pricing/__pycache__/engine.pyc",
    "eios/finance/secrets.json",
))
def test_wheel_rejects_hidden_extra_files(tmp_path, extra):
    wheel = tmp_path / "price.whl"
    _synthetic_wheel(wheel, {p.as_posix() for p in SOURCE_FILES} | {extra})
    with pytest.raises(ValueError, match="Unexpected|unapproved"):
        audit_wheel(wheel)


def test_wheel_rejects_missing_modules_extra_dependencies_or_wrong_metadata(tmp_path):
    wheel = tmp_path / "price.whl"
    files = {p.as_posix() for p in SOURCE_FILES}
    _synthetic_wheel(wheel, files - {"eios/pricing/company_coverage.py"})
    with pytest.raises(ValueError, match="Unexpected"):
        audit_wheel(wheel)
    _synthetic_wheel(
        wheel, files, dependencies=(
            "Requires-Dist: pydantic>=2,<3",
            "Requires-Dist: openpyxl>=3",
        ),
    )
    with pytest.raises(ValueError, match="Pydantic and shared C0"):
        audit_wheel(wheel)


def test_wheel_rejects_an_injected_import_even_when_module_list_is_unchanged(tmp_path):
    wheel = tmp_path / "price.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for file in SOURCE_FILES:
            contents = "# synthetic\n"
            if file.as_posix() == "eios/pricing/engine.py":
                contents = "import eios.company_app\n"
            archive.writestr(file.as_posix(), contents)
        archive.writestr(
            "eios_price_procurement-0.2.0.dist-info/METADATA",
            "Name: eios-price-procurement\nVersion: 0.2.0\n"
            "Requires-Dist: pydantic>=2,<3\n",
        )
    with pytest.raises(ValueError, match="Forbidden"):
        audit_wheel(wheel)


def test_old_duplicate_ownership_is_still_rejected_by_collision_checker(tmp_path):
    price = tmp_path / "price.whl"
    tco = tmp_path / "tco.whl"
    kernel = tmp_path / "kernel.whl"
    with zipfile.ZipFile(price, "w") as archive:
        archive.writestr("eios/core/models.py", "pass")
        archive.writestr("eios/pricing/engine.py", "pass")
    with zipfile.ZipFile(tco, "w") as archive:
        archive.writestr("eios/core/models.py", "pass")
        archive.writestr("eios/tco/engine.py", "pass")
    with zipfile.ZipFile(kernel, "w") as archive:
        archive.writestr("eios/kernel/execution.py", "pass")
    assert installed_paths(price) & installed_paths(tco) == {"eios/core/models.py"}
    with pytest.raises(ValueError, match="eios/core/models.py"):
        ensure_no_shared_paths(price, tco)
    ensure_no_shared_paths(price, kernel)


def test_price_engines_remain_from_one_existing_canonical_module():
    from eios.pricing.engine import run_price_intelligence

    assert callable(run_price_intelligence)
    source = (ROOT / "eios/pricing/engine.py").read_text(encoding="utf-8")
    assert source.count("def run_price_intelligence(") == 1
    assert "aggregate_selected_prices" in source
    assert "assess_sufficiency" in source
