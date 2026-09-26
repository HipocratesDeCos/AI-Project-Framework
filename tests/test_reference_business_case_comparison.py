"""The two-company view reads only fully verified synthetic packages."""
import pytest

from examples.reference_business_case_demo import create_reference_demo
from examples.reference_business_case_002 import create_reference_business_case_002
from examples.reference_business_case_comparison import render_comparison


def test_comparison_requires_verified_packages_and_keeps_limits_visible(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    create_reference_demo(first, with_supplier_risk=True)
    create_reference_business_case_002(second, with_review=True)
    html = render_comparison(first, second)
    assert "Completada parcialmente" in html
    assert "No determinable" in html
    assert "Favorable en la prueba" in html
    assert "Ninguna compra está autorizada" in html
    assert "el caso negativo 001 no interviene" in html
    assert "<script" not in html.lower()

    (second / "reference-review.html").write_text("alterado", encoding="utf-8")
    with pytest.raises(ValueError, match="reference-review.html"):
        render_comparison(first, second)


def test_comparison_rejects_missing_supplier_observation(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    create_reference_demo(first)
    create_reference_business_case_002(second)
    with pytest.raises(ValueError, match="supplier-risk observations"):
        render_comparison(first, second)
