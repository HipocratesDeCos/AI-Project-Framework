from datetime import date
from decimal import Decimal

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import Assessment, DecisionContext, PurchaseOperation, Rule
from eios.core.orchestration import O1ExecutionStatus
from eios.rules import RuleAssessmentBinding, run_assessment_set_vertical


CONTEXT = DecisionContext(
    decision_id="D-BATCH",
    scenario_id="S-BATCH",
    rules_version="rules-v1",
    parameters_version="params-v1",
    data_snapshot_id="snapshot-v1",
)
PURCHASE = PurchaseOperation(
    decision_id="D-BATCH",
    scenario_id="S-BATCH",
    article_id="A-1",
    supplier_id="SUP-1",
    quantity=Decimal("10"),
    unit_price=Decimal("5"),
    currency="EUR",
    operation_date=date(2026, 9, 11),
)


def _binding(rule_id: str, *, effect: str, severity: str, outcome: str = "TRUE", status: str = "EVALUABLE") -> RuleAssessmentBinding:
    rule = Rule(rule_id=rule_id, version="rules-v1", requires_evidence=True)
    assessment = Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=[f"EV-{rule_id}"],
        reason=f"reason:{rule_id}",
    )
    metadata = RuleMetadata(
        rule_id=rule_id,
        version="rules-v1",
        effect=effect,
        severity=severity,
    )
    return RuleAssessmentBinding(rule=rule, assessment=assessment, metadata=metadata)


def test_batch_crc_resolves_multiple_active_rules_by_effect_priority() -> None:
    result = run_assessment_set_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        bindings=(
            _binding("R-R2", effect="R2", severity="ALTA"),
            _binding("R-R0", effect="R0", severity="CRÍTICA"),
            _binding("R-R3", effect="R3", severity="INFORMATIVA"),
        ),
        base_result="COMPRAR",
    )

    assert tuple(a.rule_id for a in result.assessments) == ("R-R2", "R-R0", "R-R3")
    assert tuple(t.rule_id for t in result.traces) == ("R-R2", "R-R0", "R-R3")
    assert result.c0_capability.status == O1ExecutionStatus.COMPLETED
    assert result.crc_result.consolidated_result == "NO COMPRAR"
    assert "R-R2:R2" in result.crc_result.conflicts
    assert result.support_package.execution_status == O1ExecutionStatus.COMPLETED
    assert result.support_package.trace_references == tuple(t.trace_id for t in result.traces)


def test_batch_all_false_preserves_explicit_base_result() -> None:
    result = run_assessment_set_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        bindings=(
            _binding("R-A", effect="R1", severity="ALTA", outcome="FALSE"),
            _binding("R-B", effect="R2", severity="MEDIA", outcome="FALSE"),
        ),
        base_result="COMPRAR CONDICIONADO",
    )
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"


def test_batch_not_evaluable_is_not_converted_to_false() -> None:
    result = run_assessment_set_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        bindings=(
            _binding("R-A", effect="R2", severity="ALTA", outcome="FALSE"),
            _binding("R-B", effect="R1", severity="ALTA", status="NOT_EVALUABLE"),
        ),
        base_result="COMPRAR",
    )
    assert result.c0_capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.crc_result.consolidated_result == "INFORMACIÓN INSUFICIENTE"
    assert result.support_package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED


def test_batch_rejects_duplicate_rule_ids() -> None:
    first = _binding("R-DUP", effect="R2", severity="ALTA")
    second = _binding("R-DUP", effect="R1", severity="ALTA")
    with pytest.raises(ValueError, match="rule_id duplicados"):
        run_assessment_set_vertical(
            purchase=PURCHASE,
            context=CONTEXT,
            bindings=(first, second),
            base_result="COMPRAR",
        )


def test_batch_rejects_binding_with_wrong_metadata_version() -> None:
    binding = _binding("R-A", effect="R2", severity="ALTA")
    bad = RuleAssessmentBinding(
        rule=binding.rule,
        assessment=binding.assessment,
        metadata=RuleMetadata(
            rule_id="R-A",
            version="rules-other",
            effect="R2",
            severity="ALTA",
        ),
    )
    with pytest.raises(ValueError, match="RuleMetadata.version"):
        run_assessment_set_vertical(
            purchase=PURCHASE,
            context=CONTEXT,
            bindings=(bad,),
            base_result="COMPRAR",
        )


def test_empty_batch_preserves_base_result_and_reports_c0_not_evaluable() -> None:
    result = run_assessment_set_vertical(
        purchase=PURCHASE,
        context=CONTEXT,
        bindings=(),
        base_result="COMPRAR",
    )
    assert result.assessments == ()
    assert result.traces == ()
    assert result.c0_capability.status == O1ExecutionStatus.NOT_EVALUABLE
    assert result.crc_result.consolidated_result == "COMPRAR"
    assert result.support_package.execution_status == O1ExecutionStatus.PARTIALLY_COMPLETED
