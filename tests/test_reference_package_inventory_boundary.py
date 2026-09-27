"""Standalone replay must cover the complete local synthetic package."""
import pytest

from examples.reference_business_case_demo import create_reference_demo, verify_reference_demo
from examples.reference_business_case_002 import (
    create_reference_business_case_002, verify_reference_business_case_002,
)


def test_case_001_rejects_undeclared_file_and_external_link(tmp_path):
    package = tmp_path / "case-001"
    create_reference_demo(package)
    verify_reference_demo(package)
    extra = package / "unreviewed.txt"
    extra.write_text("not part of the replay", encoding="utf-8")
    with pytest.raises(ValueError, match="inventory"):
        verify_reference_demo(package)
    extra.unlink()
    external = tmp_path / "outside.txt"
    (package / "reference-review.html").rename(external)
    (package / "reference-review.html").symlink_to(external)
    with pytest.raises(ValueError, match="symlinks"):
        verify_reference_demo(package)


def test_case_002_rejects_external_link_even_if_bytes_match(tmp_path):
    package = tmp_path / "case-002"
    create_reference_business_case_002(package, with_review=True)
    verify_reference_business_case_002(package)
    external = tmp_path / "outside.html"
    (package / "reference-review.html").rename(external)
    (package / "reference-review.html").symlink_to(external)
    with pytest.raises(ValueError, match="symlinks"):
        verify_reference_business_case_002(package)
