from datetime import date
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.fingerprint import assessment_fingerprint
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Trace
from eios.core.orchestration import O1ExecutionStatus
from eios.rules.catalog import authorized_rule
from eios.rules.provenance import (
    AssessmentTraceBinding,
    build_provenanced_rules_engine_c0_invoker,
    run_provenanced_assessments_vertical,
)


RULES_VERSION = "rules-v1"


def _context(
    *,
    decision_id: str = "D-PROV",
    scenario_id: str = "S-PROV",
    parameters_version: str = "params-v1",
    data_snapshot_id: str = "snapshot-v1",
) -> DecisionContext:
    return DecisionContext(
        decision_id=decision_id,
        scenario_id=scenario_id,
        rules_version=RULES_VERSION,
        parameters_version=parameters_version,
        data_snapshot_id=data_snapshot_id,
    )


def _purchase(
    *,
    decision_id: str = "D-PROV",
    scenario_id: str = "S-PROV",
    unit_price: Decimal = Decimal("5"),
) -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=decision_id,
        scenario_id=scenario_id,
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=unit_price,
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _assessment(
    *,
    rule_id: str = "R-STK-003",
    status: str = "EVALUABLE",
    outcome: str | None = "TRUE",
    reason: str = "canonical assessment reason",
) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=[f"EV-{rule_id}"],
        reason=reason,
    )


def _binding(
    *,
    context: DecisionContext | None = None,
    purchase: PurchaseOperation | None = None,
    assessment: Assessment | None = None,
) -> AssessmentTraceBinding:
    ctx = context or _context()
    operation = purchase or _purchase()
    item = assessment or _assessment()
    rule = authorized_rule(item.rule_id, ctx.rules_version)
    trace = build_trace(ctx, operation, rule, tuple(item.evidence_ids), item)
    return AssessmentTraceBinding(assessment=item, trace=trace)


def test_canonical_binding_is_accepted_and_original_trace_is_preserved() -> None:
    binding = _binding()
    result = run_provenanced_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        bindings=(binding,),
        base_result="COMPRAR",
    )

    assert result.assessments == (binding.assessment,)
    assert result.traces == (binding.trace,)
    assert result.traces[0].trace_id == binding.trace.trace_id
    assert result.traces[0].created_at == binding.trace.created_at
    assert result.c0_capability.status == O1ExecutionStatus.COMPLETED
    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.support_package.trace_references == (binding.trace.trace_id,)


def test_assessment_fingerprint_covers_reason_and_changes_trace_identity() -> None:
    context = _context()
    purchase = _purchase()
    first = _assessment(reason="reason A")
    second = _assessment(reason="reason B")
    rule = authorized_rule(first.rule_id, context.rules_version)

    first_trace = build_trace(context, purchase, rule, tuple(first.evidence_ids), first)
    second_trace = build_trace(context, purchase, rule, tuple(second.evidence_ids), second)

    assert assessment_fingerprint(first) != assessment_fingerprint(second)
    assert first_trace.assessment_fingerprint != second_trace.assessment_fingerprint
    assert first_trace.trace_id != second_trace.trace_id


def test_reason_mutation_after_trace_creation_fails_closed() -> None:
    binding = _binding()
    tampered_assessment = binding.assessment.model_copy(
        update={"reason": "different reason after trace creation"}
    )
    tampered = AssessmentTraceBinding(
        assessment=tampered_assessment,
        trace=binding.trace,
    )

    with pytest.raises(ValueError, match="assessment_fingerprint"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(tampered,),
            base_result="COMPRAR",
        )


def test_legacy_trace_without_assessment_fingerprint_is_rejected() -> None:
    binding = _binding()
    legacy_trace = binding.trace.model_copy(update={"assessment_fingerprint": None})

    with pytest.raises(ValueError, match="legacy sin assessment_fingerprint"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(
                AssessmentTraceBinding(
                    assessment=binding.assessment,
                    trace=legacy_trace,
                ),
            ),
            base_result="COMPRAR",
        )


@pytest.mark.parametrize(
    ("context", "message"),
    (
        (_context(decision_id="D-OTHER"), "Trace.decision_id"),
        (_context(scenario_id="S-OTHER"), "Trace.scenario_id"),
        (_context(parameters_version="params-other"), "Trace.parameters_version"),
        (_context(data_snapshot_id="snapshot-other"), "Trace.data_snapshot_id"),
    ),
)
def test_foreign_context_is_rejected(context: DecisionContext, message: str) -> None:
    binding = _binding()
    purchase = _purchase(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
    )

    with pytest.raises(ValueError, match=message):
        run_provenanced_assessments_vertical(
            purchase=purchase,
            context=context,
            bindings=(binding,),
            base_result="COMPRAR",
        )


def test_foreign_purchase_fingerprint_is_rejected() -> None:
    binding = _binding()
    changed_purchase = _purchase(unit_price=Decimal("9.99"))

    with pytest.raises(ValueError, match="input_fingerprint"):
        run_provenanced_assessments_vertical(
            purchase=changed_purchase,
            context=_context(),
            bindings=(binding,),
            base_result="COMPRAR",
        )


def test_manipulated_trace_id_is_rejected() -> None:
    binding = _binding()
    bad_trace = binding.trace.model_copy(update={"trace_id": "tampered-trace-id"})

    with pytest.raises(ValueError, match="trace_id no es reproducible"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(AssessmentTraceBinding(assessment=binding.assessment, trace=bad_trace),),
            base_result="COMPRAR",
        )


def test_status_outcome_or_evidence_mismatch_is_rejected() -> None:
    binding = _binding()

    wrong_status = binding.trace.model_copy(update={"assessment_status": "NOT_EVALUABLE"})
    with pytest.raises(ValueError, match="assessment_status"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(AssessmentTraceBinding(assessment=binding.assessment, trace=wrong_status),),
            base_result="COMPRAR",
        )

    wrong_outcome = binding.trace.model_copy(update={"assessment_outcome": "FALSE"})
    with pytest.raises(ValueError, match="assessment_outcome"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(AssessmentTraceBinding(assessment=binding.assessment, trace=wrong_outcome),),
            base_result="COMPRAR",
        )

    wrong_evidence = binding.trace.model_copy(update={"evidence_ids": ("EV-OTHER",)})
    with pytest.raises(ValueError, match="evidence_ids"):
        run_provenanced_assessments_vertical(
            purchase=_purchase(),
            context=_context(),
            bindings=(AssessmentTraceBinding(assessment=binding.assessment, trace=wrong_evidence),),
            base_result="COMPRAR",
        )


def test_uncatalogued_rule_and_duplicate_rule_ids_fail_closed() -> None:
    context = _context()
    purchase = _purchase()
    unknown_assessment = _assessment(rule_id="R-UNKNOWN")
    unknown_trace = build_trace(
        context,
        purchase,
        rule=type(authorized_rule("R-STK-003", RULES_VERSION))(
            rule_id="R-UNKNOWN",
            version=RULES_VERSION,
            requires_evidence=True,
        ),
        evidence_ids=tuple(unknown_assessment.evidence_ids),
        assessment=unknown_assessment,
    )
    unknown_binding = AssessmentTraceBinding(
        assessment=unknown_assessment,
        trace=unknown_trace,
    )

    with pytest.raises(ValueError, match="no materializada"):
        run_provenanced_assessments_vertical(
            purchase=purchase,
            context=context,
            bindings=(unknown_binding,),
            base_result="COMPRAR",
        )

    binding = _binding()
    with pytest.raises(ValueError, match="rule_id duplicados"):
        run_provenanced_assessments_vertical(
            purchase=purchase,
            context=context,
            bindings=(binding, binding.model_copy(deep=True)),
            base_result="COMPRAR",
        )


def test_not_evaluable_semantics_are_preserved() -> None:
    assessment = _assessment(
        rule_id="R-FIN-001",
        status="NOT_EVALUABLE",
        outcome=None,
        reason="insufficient evidence",
    )
    binding = _binding(assessment=assessment)

    result = run_provenanced_assessments_vertical(
        purchase=_purchase(),
        context=_context(),
        bindings=(binding,),
        base_result="COMPRAR",
    )

    assert result.assessments[0].status == "NOT_EVALUABLE"
    assert result.assessments[0].outcome is None
    assert result.c0_capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"


def test_provenanced_invoker_rejects_reuse_in_another_context() -> None:
    binding = _binding()
    invoker = build_provenanced_rules_engine_c0_invoker(
        bindings=(binding,),
        base_result="COMPRAR",
    )

    foreign_context = _context(decision_id="D-OTHER", scenario_id="S-OTHER")
    foreign_purchase = _purchase(decision_id="D-OTHER", scenario_id="S-OTHER")

    with pytest.raises(ValueError, match="Trace.decision_id"):
        invoker(foreign_purchase, foreign_context)


def test_invoker_freezes_binding_snapshot_against_later_source_mutation() -> None:
    binding = _binding()
    invoker = build_provenanced_rules_engine_c0_invoker(
        bindings=(binding,),
        base_result="COMPRAR",
    )

    binding.assessment.reason = "mutated after invoker construction"

    capability = invoker(_purchase(), _context())
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True


def test_inputs_are_not_mutated_by_safe_runtime() -> None:
    purchase = _purchase()
    context = _context()
    binding = _binding()
    purchase_before = purchase.model_dump(mode="python")
    context_before = context.model_dump(mode="python")
    assessment_before = binding.assessment.model_dump(mode="python")
    trace_before = binding.trace.model_dump(mode="python")

    run_provenanced_assessments_vertical(
        purchase=purchase,
        context=context,
        bindings=(binding,),
        base_result="COMPRAR",
    )

    assert purchase.model_dump(mode="python") == purchase_before
    assert context.model_dump(mode="python") == context_before
    assert binding.assessment.model_dump(mode="python") == assessment_before
    assert binding.trace.model_dump(mode="python") == trace_before


def test_trace_type_remains_separate_from_assessment_contract() -> None:
    assert "decision_id" not in Assessment.model_fields
    assert "scenario_id" not in Assessment.model_fields
    assert "assessment_fingerprint" in Trace.model_fields
