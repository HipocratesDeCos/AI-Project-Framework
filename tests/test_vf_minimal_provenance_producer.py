from datetime import date
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import FrontierClass, ViabilityStatus
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedScenarioAnalyticsInput,
    complete_provenanced_o4_o2_o3_orchestration,
    evaluate_provenanced_viability,
    produce_frontier_assessments,
)
from eios.rules.catalog import authorized_rule


RULES_VERSION = "rules-v1"


def _context(*, scenario_id="S-VF"):
    return DecisionContext(
        decision_id="D-VF",
        scenario_id=scenario_id,
        rules_version=RULES_VERSION,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase(*, scenario_id="S-VF"):
    return PurchaseOperation(
        decision_id="D-VF",
        scenario_id=scenario_id,
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 23),
    )


def _binding(rule_id: str, *, outcome="TRUE", status="EVALUABLE", scenario_id="S-VF"):
    context = _context(scenario_id=scenario_id)
    purchase = _purchase(scenario_id=scenario_id)
    assessment = Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=(f"EV-{rule_id}",),
        reason=f"reason {rule_id}",
    )
    rule = authorized_rule(rule_id, RULES_VERSION)
    trace = build_trace(context, purchase, rule, tuple(assessment.evidence_ids), assessment)
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


@pytest.mark.parametrize(
    ("outcome", "satisfied"),
    [("TRUE", False), ("FALSE", True)],
)
def test_fin001_maps_explicitly_to_h(outcome, satisfied):
    result = produce_frontier_assessments(
        purchase=_purchase(),
        context=_context(),
        bindings=(_binding("R-FIN-001", outcome=outcome),),
    )
    assert len(result) == 1
    item = result[0]
    assert item.frontier_class == FrontierClass.H
    assert item.evaluated is True
    assert item.satisfied is satisfied
    assert item.solvable is False


def test_fin001_not_evaluable_becomes_materially_insufficient_h():
    item = produce_frontier_assessments(
        purchase=_purchase(),
        context=_context(),
        bindings=(_binding("R-FIN-001", status="NOT_EVALUABLE"),),
    )[0]
    assert item.frontier_class == FrontierClass.H
    assert item.evaluated is False
    assert item.materially_insufficient is True


@pytest.mark.parametrize(
    ("outcome", "satisfied"),
    [("TRUE", False), ("FALSE", True)],
)
def test_pag002_maps_explicitly_to_k(outcome, satisfied):
    item = produce_frontier_assessments(
        purchase=_purchase(),
        context=_context(),
        bindings=(_binding("R-PAG-002", outcome=outcome),),
    )[0]
    assert item.frontier_class == FrontierClass.K
    assert item.evaluated is True
    assert item.satisfied is satisfied
    assert item.solvable is True


def test_dat003_true_and_not_evaluable_produce_u_but_false_does_not():
    true_result = produce_frontier_assessments(
        purchase=_purchase(), context=_context(),
        bindings=(_binding("R-DAT-003", outcome="TRUE"),),
    )
    assert len(true_result) == 1
    assert true_result[0].frontier_class == FrontierClass.U
    assert true_result[0].materially_insufficient is True

    false_result = produce_frontier_assessments(
        purchase=_purchase(), context=_context(),
        bindings=(_binding("R-DAT-003", outcome="FALSE"),),
    )
    assert false_result == ()

    unknown_result = produce_frontier_assessments(
        purchase=_purchase(), context=_context(),
        bindings=(_binding("R-DAT-003", status="NOT_EVALUABLE"),),
    )
    assert len(unknown_result) == 1
    assert unknown_result[0].frontier_class == FrontierClass.U


def test_uncatalogued_rule_is_validated_but_not_promoted_to_s():
    result = produce_frontier_assessments(
        purchase=_purchase(), context=_context(),
        bindings=(_binding("R-STK-003", outcome="TRUE"),),
    )
    assert result == ()


def test_duplicate_rule_ids_fail_closed():
    b = _binding("R-FIN-001")
    with pytest.raises(ValueError, match="rule_id duplicados"):
        produce_frontier_assessments(
            purchase=_purchase(),
            context=_context(),
            bindings=(b, b.model_copy(deep=True)),
        )


def test_tampered_trace_fails_closed():
    b = _binding("R-FIN-001")
    bad = AssessmentTraceBinding(
        assessment=b.assessment,
        trace=b.trace.model_copy(update={"trace_id": "tampered"}),
    )
    with pytest.raises(ValueError, match="trace_id no es reproducible"):
        produce_frontier_assessments(
            purchase=_purchase(), context=_context(), bindings=(bad,)
        )


def test_vf_precedence_h_then_u_then_k():
    h = evaluate_provenanced_viability(
        purchase=_purchase(), context=_context(),
        bindings=(
            _binding("R-FIN-001", outcome="TRUE"),
            _binding("R-DAT-003", outcome="TRUE"),
            _binding("R-PAG-002", outcome="TRUE"),
        ),
    )
    assert h.status == ViabilityStatus.NOT_VIABLE

    u = evaluate_provenanced_viability(
        purchase=_purchase(), context=_context(),
        bindings=(
            _binding("R-FIN-001", outcome="FALSE"),
            _binding("R-DAT-003", outcome="TRUE"),
            _binding("R-PAG-002", outcome="TRUE"),
        ),
    )
    assert u.status == ViabilityStatus.NOT_EVALUABLE

    k = evaluate_provenanced_viability(
        purchase=_purchase(), context=_context(),
        bindings=(
            _binding("R-FIN-001", outcome="FALSE"),
            _binding("R-DAT-003", outcome="FALSE"),
            _binding("R-PAG-002", outcome="TRUE"),
        ),
    )
    assert k.status == ViabilityStatus.VIABLE_CON_CONDICIONES


def test_no_active_frontier_consequence_is_viable_and_versions_preserved():
    result = evaluate_provenanced_viability(
        purchase=_purchase(), context=_context(),
        bindings=(
            _binding("R-DAT-003", outcome="FALSE"),
            _binding("R-STK-003", outcome="TRUE"),
        ),
    )
    assert result.status == ViabilityStatus.VIABLE
    assert result.rules_version == "rules-v1"
    assert result.parameters_version == "params-v1"
    assert result.data_snapshot_id == "snapshot-v1"


def _preparation():
    return prepare_o4_o2_o3_orchestration(
        context=DecisionContext(
            decision_id="D-VF",
            scenario_id="BASE",
            rules_version=RULES_VERSION,
            parameters_version="params-v1",
            data_snapshot_id="snapshot-v1",
        ),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1,),
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-VF-MIN-1"),
    )


def test_stage2_public_boundary_reconstructs_vf_internally():
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    child_context = _context(scenario_id=scenario_id)
    child_purchase = _purchase(scenario_id=scenario_id)
    binding = _binding("R-FIN-001", outcome="FALSE", scenario_id=scenario_id)

    result = complete_provenanced_o4_o2_o3_orchestration(
        preparation=preparation,
        inputs=(
            ProvenancedScenarioAnalyticsInput(
                scenario_id=scenario_id,
                purchase=child_purchase,
                assessment_bindings=(binding,),
            ),
        ),
    )

    assert len(result.evaluations) == 1
    evaluation = result.evaluations[0]
    assert evaluation.scenario_id == scenario_id
    assert evaluation.viability_result["status"] == "VIABLE"
    assert evaluation.viability_result["scenario_id"] == child_context.scenario_id


def test_stage2_rejects_foreign_purchase_and_tampered_binding():
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    binding = _binding("R-FIN-001", outcome="FALSE", scenario_id=scenario_id)

    with pytest.raises(ValueError, match="scenario_id incompatible"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            inputs=(
                ProvenancedScenarioAnalyticsInput(
                    scenario_id=scenario_id,
                    purchase=_purchase(scenario_id="OTHER"),
                    assessment_bindings=(binding,),
                ),
            ),
        )

    bad = AssessmentTraceBinding(
        assessment=binding.assessment,
        trace=binding.trace.model_copy(update={"trace_id": "tampered"}),
    )
    with pytest.raises(ValueError, match="trace_id no es reproducible"):
        complete_provenanced_o4_o2_o3_orchestration(
            preparation=preparation,
            inputs=(
                ProvenancedScenarioAnalyticsInput(
                    scenario_id=scenario_id,
                    purchase=_purchase(scenario_id=scenario_id),
                    assessment_bindings=(bad,),
                ),
            ),
        )
