"""TCO material for company 002, without claiming a second E2E execution."""

import pytest
from decimal import Decimal
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.tco_integration import build_reference_observed_tco_invoker
from eios.tco.models import TCOInput
from examples.reference_business_case_002_material import bundle_runtime as _material


def test_second_company_tco_uses_exact_synthetic_purchase_once():
    bundle, purchase, context = _material()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert (purchase.article_id, purchase.supplier_id, purchase.quantity,
            purchase.unit_price) == (
                "ARTICLE-MOCK-002", "SUPPLIER-MOCK-002", Decimal("15"),
                Decimal("21.00"),
            )

    invoker = build_reference_observed_tco_invoker(
        payload=TCOInput(purchase_operation=purchase),
        reference_case_id=provenance["reference_case_id"],
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert invoker.input_payload().purchase_operation == purchase
    assert capture.capability == capability
    assert capture.result.value == Decimal("315.00")
    assert capture.result.contributing_components == ("ACQUISITION",)
    assert capture.result.unresolved_components == ()
    assert capture.result.complete
    assert capability.trace_references == ()
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_tco_rejects_a_different_runtime_purchase():
    _, purchase, context = _material()
    invoker = build_reference_observed_tco_invoker(
        payload=TCOInput(purchase_operation=purchase),
        reference_case_id="REF-BUSINESS-002",
    )
    with pytest.raises(ValueError, match="no coincide"):
        invoker(purchase.model_copy(update={"quantity": Decimal("16")}), context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
