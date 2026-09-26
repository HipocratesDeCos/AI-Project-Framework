"""TCO material for company 002, without claiming a second E2E execution."""
from decimal import Decimal
from pathlib import Path

import pytest

from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.core.tco_integration import build_reference_observed_tco_invoker
from eios.tco.models import TCOInput


FIXTURE = Path(__file__).parent / "fixtures" / "reference_business_case_002_semantic"


def _material():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    return (
        bundle,
        PurchaseOperation.model_validate(dip["purchase"]),
        DecisionContext.model_validate(dip["context"]),
    )


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
