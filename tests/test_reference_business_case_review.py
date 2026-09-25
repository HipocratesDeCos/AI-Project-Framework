"""Read-only review of terminal synthetic artifacts."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest

from examples.reference_business_case_001 import execute_reference_business_case
from examples.reference_business_case_review import render_review


@pytest.fixture(scope="module")
def results():
    return (execute_reference_business_case(variant="negative").to_payload(),
            execute_reference_business_case(variant="qtg-eligible").to_payload())


def test_review_compares_quality_and_technical_execution(results):
    html = render_review(*results)
    assert "NO_APTO" in html and "BAJA" in html
    assert "APTO" in html and "ALTA" in html
    assert html.count("Ejecución técnica: COMPLETED") == 2
    assert "COMPLETED describe la ejecución técnica" in html
    assert "FORBIDDEN" in html and "NO_OPERATIONAL_EFFECT" in html
    assert "trace:reference:price:sufficiency" in html
    assert "<script" not in html and "<form" not in html


def test_review_rejects_tampered_terminal(results):
    negative = deepcopy(results[0])
    negative["operational_path"] = "ALLOWED"
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        render_review(negative, results[1])


def test_review_rejects_rehashed_operational_claim(results):
    negative = deepcopy(results[0])
    negative["decision_authority"] = True
    negative["terminal_fingerprint"] = sha256(json.dumps(
        {k: v for k, v in negative.items() if k != "terminal_fingerprint"},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()
    with pytest.raises(ValueError, match="nonoperational terminal invariant"):
        render_review(negative, results[1])


def test_review_escapes_trace_text(results):
    negative = deepcopy(results[0])
    negative["execution_outcome"]["capability_results"][0]["trace_references"].append(
        '<img src=x onerror=alert(1)>')
    negative["execution_outcome_fingerprint"] = sha256(json.dumps(
        negative["execution_outcome"], ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    negative["terminal_fingerprint"] = sha256(json.dumps(
        {k: v for k, v in negative.items() if k != "terminal_fingerprint"},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()
    html = render_review(negative, results[1])
    assert "&lt;img" in html and "<img" not in html


def test_review_requires_two_distinct_cases(results):
    with pytest.raises(ValueError, match="case identity or QTG variant mismatch"):
        render_review(results[0], results[0])


def test_review_rejects_swapped_variant_files(results):
    with pytest.raises(ValueError, match="negative: case identity or QTG variant mismatch"):
        render_review(results[1], results[0])


def test_review_explains_qtg_controls_without_collapsing_unknown_into_failure(results):
    html = render_review(*results)
    assert html.count("Controles QTG declarados") == 2
    assert "FLOW_HORIZON_CLASSIFICATION:FLOW-MOCK-PAYMENT-001" in html
    assert "No evaluable" in html
    assert "No satisfecho" in html
    assert "projection conflict or limitation reported" in html
    assert "FLOW-MOCK-PAYMENT-001" in html
    assert "Satisfecho" in html


def test_review_rejects_missing_qtg_checks_even_with_rehashed_terminal(results):
    negative = deepcopy(results[0])
    negative["qtg_quality_result"]["checks"] = []
    negative["terminal_fingerprint"] = sha256(json.dumps(
        {k: v for k, v in negative.items() if k != "terminal_fingerprint"},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()
    with pytest.raises(ValueError, match="QTG checks malformed"):
        render_review(negative, results[1])
