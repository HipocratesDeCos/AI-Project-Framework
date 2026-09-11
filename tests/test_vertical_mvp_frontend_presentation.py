from decimal import Decimal

import pytest

from eios.core.execution_boundary import BoundaryStatus, ExecutionOutcome
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.orchestration import CapabilityExecution, O1ExecutionStatus
from eios.frontend.application_boundary import FrontendBoundaryError, present_vertical_mvp_result
from eios.mvp import VerticalMVPSupportResult
from eios.rules import RulesEngineInput, implemented_rule_ids, run_rules_engine
from eios.rules.orchestrator import DecisionRuleExecutionResult


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-UI",
        scenario_id="S-UI",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-UI",
        scenario_id="S-UI",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date="2026-09-11",
    )


def _result_with_rules() -> VerticalMVPSupportResult:
    assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK"],
        reason="Exceso de stock demostrado.",
    )
    engine = run_rules_engine(
        RulesEngineInput(
            purchase=_purchase(),
            context=_context(),
            assessments=(assessment,),
            base_result="COMPRAR",
        )
    )
    rules = DecisionRuleExecutionResult(
        executed_rule_ids=("R-STK-003",),
        omitted_rule_ids=tuple(
            rule_id for rule_id in implemented_rule_ids() if rule_id != "R-STK-003"
        ),
        rules_engine_result=engine,
    )
    execution = ExecutionOutcome(
        status=BoundaryStatus.COMPLETED,
        policy_version="MVP-E2E-1",
        capability_results=(
            CapabilityExecution(
                capability="C0",
                status=O1ExecutionStatus.COMPLETED,
                result_available=True,
                trace_references=tuple(trace.trace_id for trace in rules.traces),
            ),
        ),
    )
    return VerticalMVPSupportResult(execution=execution, rules=rules)


def test_present_vertical_mvp_result_exposes_execution_crc_and_traceability():
    payload = present_vertical_mvp_result(_result_with_rules())

    assert payload["execution"]["status"] == "COMPLETED"
    assert payload["execution"]["policy_version"] == "MVP-E2E-1"
    assert payload["execution"]["capabilities"][0]["capability"] == "C0"
    assert payload["rules"]["executed_rule_ids"] == ["R-STK-003"]
    assert payload["rules"]["consolidated_result"] == "NEGOCIAR"
    assert payload["rules"]["assessments"][0]["rule_id"] == "R-STK-003"
    assert payload["rules"]["assessments"][0]["evidence_ids"] == ["EV-STK"]
    assert len(payload["rules"]["trace_references"]) == 1


def test_present_vertical_mvp_result_without_rules_keeps_rules_null():
    result = VerticalMVPSupportResult(
        execution=ExecutionOutcome(
            status=BoundaryStatus.COMPLETED,
            policy_version="MVP-E2E-1",
            capability_results=(
                CapabilityExecution(
                    capability="QTG",
                    status=O1ExecutionStatus.COMPLETED,
                    result_available=True,
                ),
            ),
        )
    )

    payload = present_vertical_mvp_result(result)
    assert payload["rules"] is None
    assert payload["execution"]["capabilities"][0]["capability"] == "QTG"


def test_present_vertical_mvp_result_rejects_arbitrary_object():
    with pytest.raises(FrontendBoundaryError, match="Vertical MVP"):
        present_vertical_mvp_result(object())
