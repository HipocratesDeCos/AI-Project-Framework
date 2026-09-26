"""Company 002 has explicitly undetermined supplier reliability, not a favorable rating."""

import pytest
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.supplier.risk_value import build_reference_observed_supplier_risk_value_invoker
from examples.reference_business_case_002_material import supplier_sources as _sources


def test_second_company_supplier_risk_is_explicitly_undetermined():
    bundle, purchase, context, supplier, risk, evidences = _sources()
    provenance = classify_reference_operational_simulation(
        bundle=bundle, reference_case_id="REF-BUSINESS-002"
    ).to_payload()
    assert (provenance["material_nature"], provenance["qtg_mode_policy"],
            provenance["operational_path"], provenance["effect_scope"],
            provenance["decision_authority"]) == (
                "SYNTHETIC", "SYNTHETIC_TEST_ONLY", "FORBIDDEN",
                "NO_OPERATIONAL_EFFECT", False,
            )
    assert supplier.identity.company_scope == "COMPANY-MOCK-002"
    assert supplier.current_supplier_id == purchase.supplier_id == "SUPPLIER-MOCK-002"
    assert not any((supplier.candidates, supplier.observations,
                    supplier.historical_facts, supplier.external_metrics,
                    supplier.signals, supplier.structural_comparisons))
    invoker = build_reference_observed_supplier_risk_value_invoker(
        reference_case_id=provenance["reference_case_id"], purchase=purchase,
        supplier_result=supplier, risk_assessments=(risk,),
        value_assessments=(), evidences=evidences,
    )
    capability = invoker(purchase, context)
    capture = invoker.capture()
    assert capture.capability == capability
    assert capture.result.risk_dimensions == (risk,)
    assert capture.result.value_dimensions == ()
    assert capture.result.unresolved_items == (
        "RISK:SUPPLIER-MOCK-002:RELIABILITY:NOT_DETERMINABLE",
    )
    assert capability.status == "PARTIALLY_COMPLETED"
    assert capability.trace_references == risk.trace_refs
    with pytest.raises(ValueError, match="single-use"):
        invoker(purchase, context)


def test_second_company_supplier_risk_rejects_foreign_purchase():
    _, purchase, context, supplier, risk, evidences = _sources()
    invoker = build_reference_observed_supplier_risk_value_invoker(
        reference_case_id="REF-BUSINESS-002", purchase=purchase,
        supplier_result=supplier, risk_assessments=(risk,),
        value_assessments=(), evidences=evidences,
    )
    with pytest.raises(ValueError, match="purchase mismatch"):
        invoker(purchase.model_copy(update={"supplier_id": "FOREIGN"}), context)
    with pytest.raises(ValueError, match="unavailable"):
        invoker.capture()
