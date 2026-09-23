from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from eios.core.c0_reproducibility import build_trace
from eios.core.case_provenance import classify_reference_operational_simulation
from eios.core.models import (
    DecisionContext,
    Evidence,
    EvidenceValidation,
    PurchaseOperation,
)
from eios.core.price_integration import build_provenanced_price_invoker
from eios.core.projection_mock_dataset import load_projection_mock_dataset
from eios.core.projection_quality_consumer import consume_projection_quality
from eios.core.projection_quality_producer import produce_projection_quality
from eios.core.projection_synthetic_adapter import (
    build_projection_only_synthetic_material_bundle,
)
from eios.core.reference_simulation_execution import (
    run_reference_operational_simulation,
)
from eios.core.tco_integration import build_provenanced_tco_invoker
from eios.data_sufficiency import (
    DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
    DecisionEvidenceRequirementSet,
    DecisionEvidenceSufficiencyProducer,
    RequirementEvidenceBinding,
    decision_evidence_purchase_ref,
    decision_evidence_sufficiency_ref,
)
from eios.rules import AssessmentTraceBinding, build_provenanced_rules_engine_c0_invoker
from eios.rules.catalog import authorized_rule
from eios.rules.data_quality import evaluate_r_dat_003
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
)
from eios.pricing.representativeness import RepresentativenessObservation
from eios.pricing.sufficiency import SufficiencyObservation
from eios.tco.models import TCOInput


SEMANTIC = (
    Path(__file__).parent / "fixtures" / "projection_only_semantic_dataset_01"
)
REFERENCE_CASE_ID = "REF-BUSINESS-001"
REFERENCE_COMPANY_ID = "COMPANY-MOCK-001"


def _bundle():
    dataset = load_projection_mock_dataset(SEMANTIC)
    return dataset, build_projection_only_synthetic_material_bundle(dataset)


def _runtime(bundle):
    dip = bundle.envelope.to_payload()["preparation"]["payload"]["capture"][
        "finance_package"
    ]["decision_input_package"]
    return (
        PurchaseOperation.model_validate(dip["purchase"]),
        DecisionContext.model_validate(dip["context"]),
    )


def _qtg(bundle):
    receipt = produce_projection_quality(
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    consumption = consume_projection_quality(
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )
    return receipt, consumption


def _provenanced_c0_invoker(purchase, context):
    requirement_evidence = Evidence(
        evidence_id="E-REF-REQ-QTG",
        source_type="ReferenceRequirementEvidence",
        source_ref="reference:business:001:requirement:qtg",
        captured_at=purchase.operation_date,
        state="DEMONSTRATED",
        demonstration_ref="reference:business:001:requirement:qtg:demonstrated",
    )
    requirement_set = DecisionEvidenceRequirementSet(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        company_scope=REFERENCE_COMPANY_ID,
        purchase_operation_ref=decision_evidence_purchase_ref(purchase),
        effective_date=purchase.operation_date,
        requirement_set_id="REQSET-REF-BUSINESS-001",
        requirement_set_version="1.0",
        requirement_ids=("REQ-PROJECTION-QUALITY",),
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        methodology_ref="METHOD-REF-BUSINESS-001-DATA",
        trace_refs=("trace:reference:requirements",),
    )
    requirement_binding = RequirementEvidenceBinding(
        requirement_id="REQ-PROJECTION-QUALITY",
        classification="SATISFIED",
        evidence=(requirement_evidence,),
        classification_ref="reference:business:001:classification:qtg:satisfied",
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        trace_refs=("trace:reference:requirement:qtg",),
    )
    producer = DecisionEvidenceSufficiencyProducer(
        authority_ref="AUTH-REF-BUSINESS-001-DATA",
        methodology_ref="METHOD-REF-BUSINESS-001-DATA",
    )
    observation = producer.produce(
        purchase=purchase,
        context=context,
        company_scope=REFERENCE_COMPANY_ID,
        state="AVAILABLE",
        requirement_set=requirement_set,
        bindings=(requirement_binding,),
        source_ref="reference:business:001:data-sufficiency",
        trace_refs=("trace:reference:data-sufficiency",),
    )
    sufficiency_evidence = Evidence(
        evidence_id="E-REF-DAT003",
        source_type=DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE,
        source_ref="reference:business:001:data-sufficiency:evidence",
        captured_at=purchase.operation_date,
        state="DEMONSTRATED",
        demonstration_ref=decision_evidence_sufficiency_ref(observation),
    )
    rule = authorized_rule("R-DAT-003", context.rules_version)
    assessment = evaluate_r_dat_003(
        purchase=purchase,
        context=context,
        rule=rule,
        observation=observation,
        sufficiency_evidence=sufficiency_evidence,
    )
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    binding = AssessmentTraceBinding(
        assessment=assessment,
        trace=trace,
    )
    invoker = build_provenanced_rules_engine_c0_invoker(
        bindings=(binding,),
        base_result="COMPRAR",
    )
    return invoker, assessment, trace



def _provenanced_price_invoker(purchase, context):
    reference_ids = ("REF-PRICE-TX-001", "REF-PRICE-TX-002")
    evidence_ids = ("E-REF-PRICE-001", "E-REF-PRICE-002")
    references = (
        PriceReference(
            source_transaction_id=reference_ids[0],
            article_identity=purchase.article_id,
            supplier_identity="SUPPLIER-REFERENCE-A",
            quantity=Decimal("8"),
            unit="UNIT",
            unit_price=Decimal("19.50"),
            currency="EUR",
            operation_date=purchase.operation_date - timedelta(days=10),
            evidence_refs=(evidence_ids[0],),
        ),
        PriceReference(
            source_transaction_id=reference_ids[1],
            article_identity=purchase.article_id,
            supplier_identity="SUPPLIER-REFERENCE-B",
            quantity=Decimal("12"),
            unit="UNIT",
            unit_price=Decimal("21.00"),
            currency="EUR",
            operation_date=purchase.operation_date - timedelta(days=5),
            evidence_refs=(evidence_ids[1],),
        ),
    )
    validations = tuple(
        EvidenceValidation(
            evidence_id=evidence_id,
            status="VALID",
            reason="Synthetic reference price evidence validated for product test",
        )
        for evidence_id in evidence_ids
    )
    price_input = PriceIntelligenceInput(
        decision_context=context.model_copy(deep=True),
        purchase_operation=purchase.model_copy(deep=True),
        references=references,
        evidence_validations=validations,
        normalization_basis=None,
        economic_basis_evidence=(),
        methodology_version="REF-BUSINESS-001-PRICE-v1",
    )
    representativeness = {
        reference_id: RepresentativenessObservation(
            ordinary_market_context=True,
            exceptional_condition=False,
            material_commercial_distortion=False,
            contradiction_material_unresolved=False,
            evidence_refs=(evidence_id,),
            rule_reference="REF-BUSINESS-001-REPRESENTATIVENESS-v1",
            trace_reference=f"trace:reference:price:{reference_id}",
        )
        for reference_id, evidence_id in zip(reference_ids, evidence_ids)
    }
    assessment_context = PriceIntelligenceAssessmentContext(
        temporal={
            reference_id: (
                "ELIGIBLE",
                f"trace:reference:price:temporal:{reference_id}",
            )
            for reference_id in reference_ids
        },
        representativeness=representativeness,
        sufficiency=SufficiencyObservation(
            evidence_sufficient=True,
            contradictions_resolved=True,
            methodological_limitations=(),
            evidence_refs=evidence_ids,
            rule_reference="REF-BUSINESS-001-PRICE-SUFFICIENCY-v1",
            trace_reference="trace:reference:price:sufficiency",
            selected_reference_ids=reference_ids,
        ),
    )
    return build_provenanced_price_invoker(
        payload=price_input,
        assessment_context=assessment_context,
    )


def _provenanced_tco_invoker(purchase):
    return build_provenanced_tco_invoker(
        payload=TCOInput(purchase_operation=purchase.model_copy(deep=True))
    )


def test_reference_business_case_001_uses_physical_synthetic_dataset():
    dataset, bundle = _bundle()
    purchase, context = _runtime(bundle)

    assert dataset.to_payload()["dataset_id"] == "EIOS-PROJECTION-SEMANTIC-MOCK-001"
    assert dataset.to_payload()["case_kind"] == "SYNTHETIC"
    assert dataset.to_payload()["effect_scope"] == "NO_OPERATIONAL_EFFECT"
    assert purchase.decision_id == "DECISION-MOCK-001"
    assert purchase.supplier_id == "SUPPLIER-MOCK-001"
    assert str(purchase.quantity) == "10"
    assert str(purchase.unit_price) == "20.50"
    assert context.data_snapshot_id == "SNAPSHOT-MOCK-001"


def test_reference_business_case_001_runs_qtg_plus_provenanced_c0():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=REFERENCE_CASE_ID,
    )
    c0_invoker, assessment, trace = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v1",
        rules_invoker=c0_invoker,
    )
    payload = execution.to_payload()

    assert assessment.rule_id == "R-DAT-003"
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"
    assert trace.trace_id
    assert payload["reference_case_id"] == REFERENCE_CASE_ID
    assert payload["capability_sequence"] == ["QTG", "C0"]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert payload["execution_outcome"]["capability_results"][0]["capability"] == "C0"
    assert payload["execution_outcome"]["capability_results"][0]["status"] == "COMPLETED"
    assert payload["execution_outcome"]["capability_results"][0][
        "trace_references"
    ] == [trace.trace_id]
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
    assert payload["operational_path"] == "FORBIDDEN"


def test_reference_business_case_001_preserves_known_qtg_limitation():
    _, bundle = _bundle()
    receipt, consumption = _qtg(bundle)

    quality = consumption.to_payload()["functional_quality_result"]
    assert quality["status"] == "NO_APTO"
    assert quality["confidence"] == "BAJA"
    assert receipt.to_payload()["operational_effect"] is False
    assert consumption.to_payload()["operational_effect"] is False


def test_reference_business_case_001_extends_to_price_tco_and_c0():
    _, bundle = _bundle()
    purchase, context = _runtime(bundle)
    receipt, consumption = _qtg(bundle)
    provenance = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=REFERENCE_CASE_ID,
    )
    c0_invoker, _, _ = _provenanced_c0_invoker(purchase, context)

    execution = run_reference_operational_simulation(
        provenance=provenance,
        bundle=bundle,
        receipt=receipt,
        consumption=consumption,
        purchase=purchase,
        context=context,
        policy_version="REF-BUSINESS-001-v2",
        price_invoker=_provenanced_price_invoker(purchase, context),
        tco_invoker=_provenanced_tco_invoker(purchase),
        rules_invoker=c0_invoker,
    )
    payload = execution.to_payload()
    capability_results = {
        item["capability"]: item
        for item in payload["execution_outcome"]["capability_results"]
    }

    assert payload["capability_sequence"] == ["QTG", "PRICE", "TCO", "C0"]
    assert payload["execution_outcome"]["status"] == "COMPLETED"
    assert set(capability_results) == {"PRICE", "TCO", "C0"}
    assert all(
        item["status"] == "COMPLETED" and item["result_available"] is True
        for item in capability_results.values()
    )
    assert payload["qtg_quality_result"]["status"] == "NO_APTO"
    assert payload["qtg_quality_result"]["confidence"] == "BAJA"
    assert payload["operational_effect"] is False
    assert payload["decision_authority"] is False
