"""Declared synthetic price references for the independent company 002."""

import pytest
from decimal import Decimal
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.price_integration import build_reference_observed_price_invoker
from examples.reference_business_case_002_material import price_sources as _sources


def test_second_company_price_uses_only_declared_002_references():
    bundle, purchase, context, payload, assessment = _sources()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert payload.purchase_operation == purchase
    assert payload.decision_context == context
    assert purchase.article_id == "ARTICLE-MOCK-002"
    assert tuple(ref.source_transaction_id for ref in payload.references) == (
        "REF-PRICE-TX-002-A", "REF-PRICE-TX-002-B",
    )
    invoker = build_reference_observed_price_invoker(
        payload=payload, assessment_context=assessment,
        reference_case_id=provenance["reference_case_id"],
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capture.result.pr_value == Decimal("21.00")
    assert capture.result.reference_set == (
        "REF-PRICE-TX-002-A", "REF-PRICE-TX-002-B",
    )
    assert capture.result.pr_status == "PR_AVAILABLE"
    assert capture.result.counts.n_selected == 2
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_price_rejects_foreign_runtime():
    _, purchase, context, payload, assessment = _sources()
    invoker = build_reference_observed_price_invoker(
        payload=payload, assessment_context=assessment,
        reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="PurchaseOperation"):
        invoker(purchase.model_copy(update={"supplier_id": "FOREIGN"}), context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
