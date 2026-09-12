from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule
from eios.rules import (
    AssessmentTraceBinding,
    RulesEngineInput,
    authorized_rule,
    run_rules_engine,
)


RULES = "rules-v1"


def _context(*, decision_id: str = "D-ENGINE", scenario_id: str = "S-ENGINE") -> DecisionContext:
    return DecisionContext(
        decision_id=decision_id,
        scenario_id=scenario_id,
        rules_version=RULES,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase(*, decision_id: str = "D-ENGINE", scenario_id: str = "S-ENGINE") -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=decision_id,
        scenario_id=scenario_id,
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _assessment(
    rule_id: str,
    outcome: str | None = "TRUE",
    *,
    status: str = "EVALUABLE",
) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=[f"EV-{rule_id}"],
        reason=f"{rule_id} assessment.",
    )


def _binding(
    rule_id: str,
    outcome: str | None = "TRUE",
    *,
    status: str = "EVALUABLE",
    context: DecisionContext | None = None,
    purchase: PurchaseOperation | None = None,
) -> AssessmentTraceBinding:
    ctx = context or _context()
    operation = purchase or _purchase()
    assessment = _assessment(rule_id, outcome, status=status)
    rule = authorized_rule(rule_id, ctx.rules_version)
    trace = build_trace(ctx, operation, rule, tuple(assessment.evidence_ids), assessment)
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


def test_rules_engine_executes_provenanced_authorized_binding_set() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            bindings=(
                _binding("R-FIN-001", "FALSE"),
                _binding("R-STK-003", "TRUE"),
                _binding("R-HIS-002", "TRUE"),
            ),
            base_result="COMPRAR",
        )
    )

    assert result.crc_result.consolidated_result == "NEGOCIAR"
    assert result.crc_result.dominant_reason == "R-STK-003 assessment."
    assert tuple(item.rule_id for item in result.assessments) == (
        "R-FIN-001",
        "R-STK-003",
        "R-HIS-002",
    )
    assert tuple(trace.rule_id for trace in result.traces) == (
        "R-FIN-001",
        "R-STK-003",
        "R-HIS-002",
    )


def test_rules_engine_preserves_authorized_base_result_when_bindings_empty() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            bindings=(),
            base_result="COMPRAR CONDICIONADO",
        )
    )

    assert result.assessments == ()
    assert result.traces == ()
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert result.c0_capability.result_available is False
    assert result.c0_capability.unresolved_items == ("C0_NO_ASSESSMENTS",)


def test_rules_engine_fails_closed_for_uncatalogued_binding() -> None:
    context = _context()
    purchase = _purchase()
    assessment = _assessment("R-PRE-001")
    rule = Rule(rule_id="R-PRE-001", version=RULES, requires_evidence=True)
    trace = build_trace(context, purchase, rule, tuple(assessment.evidence_ids), assessment)
    payload = RulesEngineInput(
        purchase=purchase,
        context=context,
        bindings=(AssessmentTraceBinding(assessment=assessment, trace=trace),),
        base_result="COMPRAR",
    )

    with pytest.raises(ValueError, match="no materializada"):
        run_rules_engine(payload)


def test_rules_engine_rejects_purchase_context_identity_mismatch() -> None:
    with pytest.raises(ValueError, match="decision_id distintos"):
        RulesEngineInput(
            purchase=_purchase(decision_id="D-OTHER"),
            context=_context(),
            bindings=(),
            base_result="COMPRAR",
        )


def test_rules_engine_keeps_not_evaluable_as_not_evaluable() -> None:
    result = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            bindings=(
                _binding(
                    "R-FIN-001",
                    None,
                    status="NOT_EVALUABLE",
                ),
            ),
            base_result="COMPRAR",
        )
    )

    assert result.assessments[0].status == "NOT_EVALUABLE"
    assert result.assessments[0].outcome is None
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"


def test_public_engine_rejects_legacy_assessments_field() -> None:
    with pytest.raises(ValidationError, match="assessments"):
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(_assessment("R-STK-003"),),
            base_result="COMPRAR",
        )


def test_public_engine_rejects_binding_from_another_context() -> None:
    binding = _binding("R-STK-003")
    foreign_context = _context(decision_id="D-OTHER", scenario_id="S-OTHER")
    foreign_purchase = _purchase(decision_id="D-OTHER", scenario_id="S-OTHER")

    with pytest.raises(ValueError, match="Trace.decision_id"):
        run_rules_engine(
            RulesEngineInput(
                purchase=foreign_purchase,
                context=foreign_context,
                bindings=(binding,),
                base_result="COMPRAR",
            )
        )


def test_public_engine_rejects_legacy_trace_without_assessment_fingerprint() -> None:
    binding = _binding("R-STK-003")
    legacy = AssessmentTraceBinding(
        assessment=binding.assessment,
        trace=binding.trace.model_copy(update={"assessment_fingerprint": None}),
    )

    with pytest.raises(ValueError, match="legacy sin assessment_fingerprint"):
        run_rules_engine(
            RulesEngineInput(
                purchase=_purchase(),
                context=_context(),
                bindings=(legacy,),
                base_result="COMPRAR",
            )
        )
