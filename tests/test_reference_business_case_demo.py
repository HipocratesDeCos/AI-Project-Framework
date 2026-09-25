"""Single-command synthetic demonstration packaging."""
import json

import pytest

from examples.reference_business_case_demo import (
    create_reference_demo, verify_reference_demo,
)


def test_demo_generates_both_exact_terminal_results_and_review(tmp_path):
    output = tmp_path / "reference-demo"
    negative_path, eligible_path, review_path = create_reference_demo(output)
    negative = json.loads(negative_path.read_text(encoding="utf-8"))
    eligible = json.loads(eligible_path.read_text(encoding="utf-8"))
    html = review_path.read_text(encoding="utf-8")

    assert negative["qtg_quality_result"]["status"] == "NO_APTO"
    assert eligible["qtg_quality_result"]["status"] == "APTO"
    assert negative["operational_path"] == eligible["operational_path"] == "FORBIDDEN"
    assert negative["operational_effect"] is eligible["operational_effect"] is False
    assert negative["decision_authority"] is eligible["decision_authority"] is False
    assert negative["terminal_fingerprint"] in html
    assert eligible["terminal_fingerprint"] in html


def test_demo_does_not_replace_existing_output(tmp_path):
    output = tmp_path / "reference-demo"
    output.mkdir()
    sentinel = output / "my-notes.txt"
    sentinel.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Output already exists"):
        create_reference_demo(output)
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_demo_replay_verifies_artifacts_without_writing(tmp_path):
    output = tmp_path / "reference-demo"
    negative_path, eligible_path, review_path = create_reference_demo(output)
    before = {p.name: p.read_bytes() for p in (negative_path, eligible_path, review_path)}
    fingerprints = verify_reference_demo(output)
    assert fingerprints == tuple(json.loads(p.read_text(encoding="utf-8"))["terminal_fingerprint"]
                                 for p in (negative_path, eligible_path))
    assert before == {p.name: p.read_bytes() for p in (negative_path, eligible_path, review_path)}


def test_demo_replay_detects_html_drift(tmp_path):
    output = tmp_path / "reference-demo"
    _, _, review_path = create_reference_demo(output)
    review_path.write_text("stale review", encoding="utf-8")
    with pytest.raises(ValueError, match="Review HTML differs"):
        verify_reference_demo(output)


def test_demo_exports_and_replays_both_price_observations(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    assert len(files) == 5
    negative, eligible = (json.loads(files[i].read_text(encoding="utf-8"))
                          for i in (0, 1))
    negative_price, eligible_price = (json.loads(files[i].read_text(encoding="utf-8"))
                                      for i in (3, 4))
    html = files[2].read_text(encoding="utf-8")
    assert negative_price["terminal_fingerprint"] == negative["terminal_fingerprint"]
    assert eligible_price["terminal_fingerprint"] == eligible["terminal_fingerprint"]
    assert negative["qtg_quality_result"]["status"] == "NO_APTO"
    assert negative_price["price_result"]["pr_status"] == "PR_AVAILABLE"
    assert html.count("Observación PRICE sintética") == 2
    assert "no es un techo" in html
    assert "20.25 EUR" in html
    assert verify_reference_demo(output) == (
        negative["terminal_fingerprint"], eligible["terminal_fingerprint"],
    )


def test_demo_rejects_incomplete_or_changed_price_sidecar(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    files[4].unlink()
    with pytest.raises(ValueError, match="Both PRICE observations"):
        verify_reference_demo(output)
    files[4].write_bytes(files[3].read_bytes())
    with pytest.raises(ValueError, match="PRICE observation identity"):
        verify_reference_demo(output)


def test_demo_rejects_changed_price_value(tmp_path):
    output = tmp_path / "reference-with-price"
    files = create_reference_demo(output, with_price=True)
    altered = json.loads(files[3].read_text(encoding="utf-8"))
    altered["price_result"]["pr_value"] = "999.00"
    files[3].write_text(json.dumps(altered), encoding="utf-8")
    with pytest.raises(ValueError, match="PRICE observation fingerprint"):
        verify_reference_demo(output)
