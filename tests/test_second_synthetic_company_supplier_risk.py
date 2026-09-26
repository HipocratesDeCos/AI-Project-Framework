"""Company 002 has explicitly undetermined supplier reliability, not a favorable rating."""
from pathlib import Path

import pytest

from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.supplier import (
    SupplierEvidenceInput, SupplierRiskDimensionAssessment,
    evaluate_supplier_evidence,
)
from eios.supplier.risk_value import build_reference_observed_supplier_risk_value_invoker


FIXTURE = Path(__file__).parent / "fixtures" / "reference_business_case_002_semantic"


def _sources():
    bundle = build_projection_only_synthetic_material_bundle(
        load_projection_mock_dataset(FIXTURE)
    )
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    purchase = PurchaseOperation.model_validate(dip["purchase"])
    context = DecisionContext.model_validate(dip["context"])
    supplier = evaluate_supplier_evidence(SupplierEvidenceInput(
        context=context, purchase_operation=purchase,
        company_scope="COMPANY-MOCK-002", evaluation_date=purchase.operation_date,
    ))
    authority = "authority:synthetic:ref-business-002:supplier:risk"
    risk = SupplierRiskDimensionAssessment(
        supplier_id=purchase.supplier_id, dimension="RELIABILITY",
        state="NOT_DETERMINABLE", authority_ref=authority,
        methodology_ref="method:synthetic:ref-business-002:supplier:risk:v1",
        assessment_ref="assessment:synthetic:ref-business-002:supplier:risk:unknown",
        evidence_refs=("E-REF-002-SRV-UNKNOWN",),
        trace_refs=("trace:synthetic:ref-business-002:supplier:risk:unknown",),
    )
    evidences = (
        Evidence(
            evidence_id="E-REF-002-SRV-AUTH", source_type="supplier-risk",
            source_ref="reference:business:002:supplier:risk:authority",
            captured_at=purchase.operation_date, state="DEMONSTRATED",
            demonstration_ref=authority,
        ),
        Evidence(
            evidence_id="E-REF-002-SRV-UNKNOWN", source_type="supplier-risk",
            source_ref="reference:business:002:supplier:risk:unknown",
            captured_at=purchase.operation_date, state="DEMONSTRATED",
            demonstration_ref=risk.assessment_ref,
        ),
    )
    return bundle, purchase, context, supplier, risk, evidences


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
