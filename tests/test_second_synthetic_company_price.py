"""Declared synthetic price references for the independent company 002."""
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import DecisionContext, EvidenceValidation, PurchaseOperation
from eios.core.price_integration import build_reference_observed_price_invoker
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_synthetic_adapter import build_projection_only_synthetic_material_bundle
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput, PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation


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
    reference_ids = ("REF-PRICE-TX-002-A", "REF-PRICE-TX-002-B")
    evidence_ids = ("E-REF-PRICE-002-A", "E-REF-PRICE-002-B")
    references = tuple(
        PriceReference(
            source_transaction_id=reference_id,
            article_identity=purchase.article_id,
            supplier_identity=f"SUPPLIER-REFERENCE-002-{index}",
            quantity=quantity,
            unit="UNIT",
            unit_price=price,
            currency=purchase.currency,
            operation_date=purchase.operation_date - timedelta(days=days),
            evidence_refs=(evidence_id,),
        )
        for index, (reference_id, evidence_id, quantity, price, days) in enumerate(
            zip(reference_ids, evidence_ids, (Decimal("10"), Decimal("14")),
                (Decimal("20.00"), Decimal("22.00")), (9, 4)), start=1
        )
    )
    payload = PriceIntelligenceInput(
        decision_context=context,
        purchase_operation=purchase,
        references=references,
        evidence_validations=tuple(
            EvidenceValidation(
                evidence_id=evidence_id, status="VALID",
                reason="Declared synthetic price reference for product test",
            ) for evidence_id in evidence_ids
        ),
        methodology_version="REF-BUSINESS-002-PRICE-v1",
    )
    assessment = PriceIntelligenceAssessmentContext(
        temporal={reference_id: (
            "ELIGIBLE", f"trace:reference:business:002:price:temporal:{reference_id}"
        ) for reference_id in reference_ids},
        representativeness={
            reference_id: RepresentativenessObservation(
                ordinary_market_context=True,
                exceptional_condition=False,
                material_commercial_distortion=False,
                contradiction_material_unresolved=False,
                evidence_refs=(evidence_id,),
                rule_reference="REF-BUSINESS-002-REPRESENTATIVENESS-v1",
                trace_reference=f"trace:reference:business:002:price:{reference_id}",
            ) for reference_id, evidence_id in zip(reference_ids, evidence_ids)
        },
        sufficiency=SufficiencyObservation(
            evidence_sufficient=True, contradictions_resolved=True,
            evidence_refs=evidence_ids,
            rule_reference="REF-BUSINESS-002-PRICE-SUFFICIENCY-v1",
            trace_reference="trace:reference:business:002:price:sufficiency",
            selected_reference_ids=reference_ids,
        ),
    )
    return bundle, purchase, context, payload, assessment


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
