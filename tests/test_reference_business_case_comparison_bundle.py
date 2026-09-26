"""The one-command comparison bundle remains replayable and immutable."""
import pytest

from examples.reference_business_case_comparison_bundle import (
    create_comparison_bundle, verify_comparison_bundle,
)


def test_bundle_creates_two_full_cases_and_rejects_changed_comparison(tmp_path):
    directory = tmp_path / "comparison"
    case_001, case_002, html = create_comparison_bundle(directory)
    assert (case_001 / "reference-buyer-preview.html").is_file()
    assert (case_002 / "reference-review.html").is_file()
    assert "Completada parcialmente" in html.read_text(encoding="utf-8")
    verify_comparison_bundle(directory)
    with pytest.raises(FileExistsError):
        create_comparison_bundle(directory)
    html.write_text("alterado", encoding="utf-8")
    with pytest.raises(ValueError, match="Comparison HTML"):
        verify_comparison_bundle(directory)


def test_bundle_rejects_changed_source_and_extra_file(tmp_path):
    directory = tmp_path / "comparison"
    case_001, case_002, _ = create_comparison_bundle(directory)
    (directory / "extra.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly both cases"):
        verify_comparison_bundle(directory)
    (directory / "extra.txt").unlink()
    (case_002 / "reference-review.html").write_text("alterado", encoding="utf-8")
    with pytest.raises(ValueError, match="reference-review.html"):
        verify_comparison_bundle(directory)


def test_bundle_rejects_external_comparison_even_when_bytes_match(tmp_path):
    directory = tmp_path / "comparison"
    _, _, html = create_comparison_bundle(directory)
    external = tmp_path / "external.html"
    html.rename(external)
    html.symlink_to(external)
    with pytest.raises(ValueError, match="symlinks"):
        verify_comparison_bundle(directory)
