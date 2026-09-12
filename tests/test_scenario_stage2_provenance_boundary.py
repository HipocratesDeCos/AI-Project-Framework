from datetime import date
from decimal import Decimal

import pytest

import eios.core.o4_o2_o3_orchestration as raw_stage2
from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import ViabilityResult, ViabilityStatus
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedScenarioAnalyticsInput,
    authorized_rule,
    complete_provenanced_o4_o2_o3_orchestration,
)


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-STAGE2-PROV",
        scenario_id="BASE",
        rules_version="RULES-STAGE2-1",
        parameters_version="PARAMS-STAGE2-1",
        data_snapshot_id="SNAP-STAGE2-1",
    )


def _preparation(domain=(1,)):
    return prepare_o4_o2_o3_orchestration(
        context=_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=domain,
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-STAGE2-PROV-1"),
    )


def _child_context(preparation, scenario_id: str) -> DecisionContext:
    base = preparation.context
    return DecisionContext(
        decision_id=base.decision_id,
        scenario_id=scenario_id,
        rules_version=base.rules_version,
        parameters_version=base.parameters_version,
        data_snapshot_id=base.data_snapshot_id,
    )


def _child_purchase(preparation, scenario_id: str) -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=preparation.context.decision_id,
        scenario_id=scenario_id,
        article_id="ART-STAGE2",
        supplier_id="SUP-STAGE2",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _input(preparation, scenario_id: str) -> ProvenancedScenarioAnalyticsInput:
    context = _child_context(preparation, scenario_id)
    purchase = _child_purchase(preparation, scenario_id)
    assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=[f"EV-{scenario_id}"],
        reason="stage2 provenance assessment",
    )
    rule = authorized_rule(assessment.rule_id, context.rules_version)
    trace = build_trace(
        context,
        purchase,
        rule,
        tuple(assessment.evidence_ids),
        assessment,
    )
    viability = ViabilityResult(
        decision_id=context.decision_id,
        scenario_id=scenario_id,
        status=ViabilityStatus.VIABLE,
        assessment_ids=(f"VF-A-{scenario_id}",),
        rule_ids=(f"VF-R-{scenario_id}",),
        trace_references=(f"VF-T-{scenario_id}",),
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
    )
    return ProvenancedScenarioAnalyticsInput(
        scenario_id=scenario_id,
        purchase=purchase,
        assessment_bindings=(
            AssessmentTraceBinding(assessment=assessment, trace=trace),
        ),
        viability_result=viability,
    )


def test_raw_stage2_completion_is_not_public_api() -> None:
    assert "complete_o4_o2_o3_orchestration" not in raw_stage2.__all__
    assert "AuthorizedScenarioAnalytics" not in raw_stage2.__all__
    assert "_complete_o4_o2_o3_orchestration" not in raw_stage2.__all__


def test_public_completion_rejects_opaque_stage2_transport() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    opaque = AuthorizedScenarioAnalytics(
        scenario_id=scenario_id,
        assessments=({"arbitrary": True},),
        viability_result={"arbitrary": True},
        trace_references=("ARBITRARY-TRACE",),
    )

    with pytest.raises(TypeError, match="ProvenancedScenarioAnalyticsInput"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            analytics=(opaque,),
        )


def test_valid_provenanced_input_completes_o3() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    item = _input(preparation, scenario_id)

    result = complete_provenanced_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=(item,),
    )

    assert len(result.evaluations) == 1
    evaluation = result.evaluations[0]
    assert evaluation.scenario_id == scenario_id
    assert evaluation.assessments[0]["rule_id"] == "R-STK-003"
    assert evaluation.trace_references == (
        item.assessment_bindings[0].trace.trace_id,
    )
    assert evaluation.viability_result["status"] == "VIABLE"


def test_manipulated_trace_fails_before_o3(monkeypatch) -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    item = _input(preparation, scenario_id)
    binding = item.assessment_bindings[0]
    bad_trace = binding.trace.model_copy(update={"trace_id": "00000000-0000-0000-0000-000000000000"})
    bad = ProvenancedScenarioAnalyticsInput(
        scenario_id=item.scenario_id,
        purchase=item.purchase,
        assessment_bindings=(
            AssessmentTraceBinding(assessment=binding.assessment, trace=bad_trace),
        ),
        viability_result=item.viability_result,
    )

    def must_not_run(*args, **kwargs):
        raise AssertionError("O3 no debe ejecutarse cuando falla la procedencia")

    monkeypatch.setattr(raw_stage2, "evaluate_scenario", must_not_run)
    with pytest.raises(ValueError, match="trace_id"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            analytics=(bad,),
        )


def test_missing_and_extra_analytical_coverage_fail_closed() -> None:
    preparation = _preparation(domain=(1, 2))
    scenario_ids = tuple(item.scenario_id for item in preparation.materialization.scenarios)

    with pytest.raises(ValueError, match="faltan paquetes analíticos"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            analytics=(_input(preparation, scenario_ids[0]),),
        )

    foreign = ProvenancedScenarioAnalyticsInput(
        scenario_id="UNKNOWN",
        purchase=_child_purchase(preparation, "UNKNOWN"),
        assessment_bindings=_input(preparation, scenario_ids[0]).assessment_bindings,
        viability_result=ViabilityResult(
            decision_id=preparation.context.decision_id,
            scenario_id="UNKNOWN",
            status=ViabilityStatus.VIABLE,
            assessment_ids=("VF-A-UNKNOWN",),
            rule_ids=("VF-R-UNKNOWN",),
            trace_references=("VF-T-UNKNOWN",),
            rules_version=preparation.context.rules_version,
            parameters_version=preparation.context.parameters_version,
            data_snapshot_id=preparation.context.data_snapshot_id,
        ),
    )
    with pytest.raises(ValueError, match="no pertenece"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            analytics=(
                _input(preparation, scenario_ids[0]),
                _input(preparation, scenario_ids[1]),
                foreign,
            ),
        )


def test_duplicate_scenario_inputs_fail_closed() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    item = _input(preparation, scenario_id)

    with pytest.raises(ValueError, match="duplicado"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            analytics=(item, item),
        )
