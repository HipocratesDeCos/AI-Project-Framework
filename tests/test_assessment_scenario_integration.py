from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    complete_o4_o2_o3_orchestration,
    prepare_o4_o2_o3_orchestration,
)
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import ViabilityResult, ViabilityStatus
from eios.frontend.application_boundary import present_vertical_mvp_result
from eios.rules import (
    AssessmentTraceBinding,
    authorized_rule,
    build_authorized_scenario_analytics_from_provenanced_assessments,
)
from eios.vertical_orchestration import run_vertical_mvp_from_orchestration


def _base_context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-AS-SCENARIO",
        scenario_id="BASE",
        rules_version="RULES-AS-1",
        parameters_version="PARAMS-AS-1",
        data_snapshot_id="SNAP-AS-1",
    )


def _base_purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-AS-SCENARIO",
        scenario_id="BASE",
        article_id="ART-AS",
        supplier_id="SUP-AS",
        quantity=Decimal("10"),
        unit_price=Decimal("7.50"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _policy() -> GenerationPolicy:
    return GenerationPolicy(policy_version="O4-AS-1")


def _preparation():
    return prepare_o4_o2_o3_orchestration(
        context=_base_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1,),
            ),
        ),
        policy=_policy(),
    )


def _child_context(preparation) -> DecisionContext:
    scenario = preparation.materialization.scenarios[0]
    base = preparation.context
    return DecisionContext(
        decision_id=base.decision_id,
        scenario_id=scenario.scenario_id,
        rules_version=base.rules_version,
        parameters_version=base.parameters_version,
        data_snapshot_id=base.data_snapshot_id,
    )


def _child_purchase(
    preparation,
    *,
    decision_id: str | None = None,
    scenario_id: str | None = None,
    unit_price: Decimal = Decimal("7.50"),
) -> PurchaseOperation:
    scenario = preparation.materialization.scenarios[0]
    return PurchaseOperation(
        decision_id=decision_id or preparation.context.decision_id,
        scenario_id=scenario_id or scenario.scenario_id,
        article_id="ART-AS",
        supplier_id="SUP-AS",
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
    reason: str = "scenario child assessment",
) -> Assessment:
    return Assessment(
        rule_id=rule_id,
        status=status,
        outcome=outcome if status == "EVALUABLE" else None,
        evidence_ids=[f"EV-{rule_id}"],
        reason=reason,
    )


def _binding(
    preparation,
    *,
    assessment: Assessment | None = None,
    context: DecisionContext | None = None,
    purchase: PurchaseOperation | None = None,
) -> AssessmentTraceBinding:
    item = assessment or _assessment()
    ctx = context or _child_context(preparation)
    operation = purchase or _child_purchase(preparation)
    rule = authorized_rule(item.rule_id, ctx.rules_version)
    trace = build_trace(ctx, operation, rule, tuple(item.evidence_ids), item)
    return AssessmentTraceBinding(assessment=item, trace=trace)


def _viability(preparation, **changes) -> ViabilityResult:
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    data = dict(
        decision_id=preparation.context.decision_id,
        scenario_id=scenario_id,
        status=ViabilityStatus.VIABLE,
        assessment_ids=("FRONTIER-ASSESSMENT-X",),
        rule_ids=("VF-RULE-X",),
        trace_references=("VF-TRACE-X",),
        rules_version=preparation.context.rules_version,
        parameters_version=preparation.context.parameters_version,
        data_snapshot_id=preparation.context.data_snapshot_id,
        limitation=None,
    )
    data.update(changes)
    return ViabilityResult(**data)


def _package(preparation=None, *, bindings=None, viability=None, **kwargs):
    prep = preparation or _preparation()
    scenario_id = prep.materialization.scenarios[0].scenario_id
    selected_bindings = bindings if bindings is not None else (_binding(prep),)
    return build_authorized_scenario_analytics_from_provenanced_assessments(
        preparation=prep,
        scenario_id=scenario_id,
        purchase=_child_purchase(prep),
        assessment_bindings=selected_bindings,
        viability_result=viability or _viability(prep),
        **kwargs,
    )


def test_child_scenario_binding_builds_authorized_analytics() -> None:
    preparation = _preparation()
    binding = _binding(preparation)
    package = _package(preparation, bindings=(binding,))

    assert package.scenario_id == preparation.materialization.scenarios[0].scenario_id
    assert package.assessments == (
        {
            "rule_id": "R-STK-003",
            "status": "EVALUABLE",
            "outcome": "TRUE",
            "evidence_ids": ["EV-R-STK-003"],
            "reason": "scenario child assessment",
        },
    )
    assert package.trace_references == (binding.trace.trace_id,)
    assert package.viability_result["assessment_ids"] == ("FRONTIER-ASSESSMENT-X",)


def test_frontier_ids_are_independent_from_c0_assessment_contract() -> None:
    preparation = _preparation()
    package = _package(preparation)

    assert "assessment_id" not in package.assessments[0]
    assert package.viability_result["assessment_ids"] == ("FRONTIER-ASSESSMENT-X",)
    assert package.viability_result["rule_ids"] == ("VF-RULE-X",)
    assert package.assessments[0]["rule_id"] == "R-STK-003"


def test_trace_references_are_derived_only_from_validated_bindings_in_order() -> None:
    preparation = _preparation()
    first = _binding(preparation, assessment=_assessment(rule_id="R-STK-003"))
    second = _binding(preparation, assessment=_assessment(rule_id="R-FIN-001", outcome="FALSE"))

    package = _package(preparation, bindings=(second, first))

    assert package.trace_references == (second.trace.trace_id, first.trace.trace_id)
    assert tuple(item["rule_id"] for item in package.assessments) == (
        "R-FIN-001",
        "R-STK-003",
    )


def test_trace_from_base_scenario_is_rejected() -> None:
    preparation = _preparation()
    base_binding = _binding(
        preparation,
        context=_base_context(),
        purchase=_base_purchase(),
    )

    with pytest.raises(ValueError, match="Trace.scenario_id"):
        _package(preparation, bindings=(base_binding,))


def test_foreign_trace_decision_or_versions_are_rejected() -> None:
    preparation = _preparation()
    binding = _binding(preparation)

    for field, value in (
        ("decision_id", "D-OTHER"),
        ("rules_version", "RULES-OTHER"),
        ("parameters_version", "PARAMS-OTHER"),
        ("data_snapshot_id", "SNAP-OTHER"),
    ):
        bad_trace = binding.trace.model_copy(update={field: value})
        bad = AssessmentTraceBinding(assessment=binding.assessment, trace=bad_trace)
        with pytest.raises(ValueError, match=field):
            _package(preparation, bindings=(bad,))


def test_foreign_purchase_identity_is_rejected_before_trace_reuse() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id
    binding = _binding(preparation)

    with pytest.raises(ValueError, match="PurchaseOperation.decision_id"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation,
            scenario_id=scenario_id,
            purchase=_child_purchase(preparation, decision_id="D-OTHER"),
            assessment_bindings=(binding,),
            viability_result=_viability(preparation),
        )

    with pytest.raises(ValueError, match="PurchaseOperation.scenario_id"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation,
            scenario_id=scenario_id,
            purchase=_child_purchase(preparation, scenario_id="S-OTHER"),
            assessment_bindings=(binding,),
            viability_result=_viability(preparation),
        )


def test_purchase_fingerprint_mismatch_is_rejected() -> None:
    preparation = _preparation()
    binding = _binding(preparation)
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="input_fingerprint"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation,
            scenario_id=scenario_id,
            purchase=_child_purchase(preparation, unit_price=Decimal("99.99")),
            assessment_bindings=(binding,),
            viability_result=_viability(preparation),
        )


def test_reason_mutation_and_legacy_trace_fail_closed() -> None:
    preparation = _preparation()
    binding = _binding(preparation)

    changed_assessment = binding.assessment.model_copy(update={"reason": "tampered reason"})
    with pytest.raises(ValueError, match="assessment_fingerprint"):
        _package(
            preparation,
            bindings=(AssessmentTraceBinding(assessment=changed_assessment, trace=binding.trace),),
        )

    legacy_trace = binding.trace.model_copy(update={"assessment_fingerprint": None})
    with pytest.raises(ValueError, match="legacy"):
        _package(
            preparation,
            bindings=(AssessmentTraceBinding(assessment=binding.assessment, trace=legacy_trace),),
        )


def test_empty_bindings_and_duplicate_rules_fail_closed() -> None:
    preparation = _preparation()
    scenario_id = preparation.materialization.scenarios[0].scenario_id

    with pytest.raises(ValueError, match="bindings no vacíos"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation,
            scenario_id=scenario_id,
            purchase=_child_purchase(preparation),
            assessment_bindings=(),
            viability_result=_viability(preparation),
        )

    binding = _binding(preparation)
    with pytest.raises(ValueError, match="rule_id duplicados"):
        _package(preparation, bindings=(binding, binding.model_copy(deep=True)))


def test_unknown_and_draft_scenarios_fail_closed() -> None:
    preparation = _preparation()
    binding = _binding(preparation)

    with pytest.raises(ValueError, match="no pertenece"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=preparation,
            scenario_id="UNKNOWN",
            purchase=_child_purchase(preparation),
            assessment_bindings=(binding,),
            viability_result=_viability(preparation),
        )

    draft_preparation = prepare_o4_o2_o3_orchestration(
        context=_base_context(),
        variables=(),
        policy=_policy(),
    )
    draft = draft_preparation.materialization.scenarios[0]
    draft_context = DecisionContext(
        decision_id=draft_preparation.context.decision_id,
        scenario_id=draft.scenario_id,
        rules_version=draft_preparation.context.rules_version,
        parameters_version=draft_preparation.context.parameters_version,
        data_snapshot_id=draft_preparation.context.data_snapshot_id,
    )
    draft_purchase = PurchaseOperation(
        **_base_purchase().model_dump(exclude={"scenario_id"}),
        scenario_id=draft.scenario_id,
    )
    draft_binding = _binding(
        draft_preparation,
        context=draft_context,
        purchase=draft_purchase,
    )
    draft_vf = ViabilityResult(
        decision_id=draft_preparation.context.decision_id,
        scenario_id=draft.scenario_id,
        status=ViabilityStatus.VIABLE,
        assessment_ids=("FRONTIER-DRAFT",),
        rule_ids=("VF-DRAFT",),
        trace_references=("VF-TRACE-DRAFT",),
        rules_version=draft_preparation.context.rules_version,
        parameters_version=draft_preparation.context.parameters_version,
        data_snapshot_id=draft_preparation.context.data_snapshot_id,
    )

    with pytest.raises(ValueError, match="VALID"):
        build_authorized_scenario_analytics_from_provenanced_assessments(
            preparation=draft_preparation,
            scenario_id=draft.scenario_id,
            purchase=draft_purchase,
            assessment_bindings=(draft_binding,),
            viability_result=draft_vf,
        )


def test_foreign_viability_remains_rejected_by_typed_vf_boundary() -> None:
    preparation = _preparation()
    foreign = replace(_viability(preparation), scenario_id="VF-OTHER")

    with pytest.raises(ValueError, match="ViabilityResult.scenario_id"):
        _package(preparation, viability=foreign)


def test_not_evaluable_assessment_is_preserved_without_false_conversion() -> None:
    preparation = _preparation()
    assessment = _assessment(
        rule_id="R-FIN-001",
        status="NOT_EVALUABLE",
        outcome=None,
        reason="insufficient scenario evidence",
    )
    package = _package(preparation, bindings=(_binding(preparation, assessment=assessment),))

    visible = package.assessments[0]
    assert visible["status"] == "NOT_EVALUABLE"
    assert visible["outcome"] is None


def test_viability_status_does_not_derive_o3_status() -> None:
    preparation = _preparation()
    vf = replace(_viability(preparation), status=ViabilityStatus.NOT_VIABLE)

    package = _package(
        preparation,
        viability=vf,
        status=ScenarioEvaluationStatus.PARTIALLY_COMPLETED,
        limitations=("explicit-o3-limitation",),
    )

    assert package.status is ScenarioEvaluationStatus.PARTIALLY_COMPLETED
    assert package.viability_result["status"] == "NOT_VIABLE"
    assert package.limitations == ("explicit-o3-limitation",)


def test_complete_stage2_consumes_provenanced_package_without_reexecution() -> None:
    preparation = _preparation()
    binding = _binding(preparation)
    package = _package(preparation, bindings=(binding,))

    result = complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=(package,),
    )

    assert len(result.evaluations) == 1
    evaluation = result.evaluations[0]
    assert evaluation.scenario_id == package.scenario_id
    assert evaluation.assessments == package.assessments
    assert evaluation.viability_result == package.viability_result
    assert evaluation.trace_references == (binding.trace.trace_id,)


def test_provenanced_payload_serializes_through_vertical_presentation() -> None:
    preparation = _preparation()
    binding = _binding(preparation)
    package = _package(preparation, bindings=(binding,))
    orchestration = complete_o4_o2_o3_orchestration(
        preparation=preparation,
        analytics=(package,),
    )

    vertical = run_vertical_mvp_from_orchestration(
        purchase=_base_purchase(),
        orchestration_result=orchestration,
        policy_version="MVP-AS-1",
    )
    payload = present_vertical_mvp_result(vertical)
    scenario = payload["scenario_support"]["scenarios"][0]

    assert scenario["scenario_id"] == package.scenario_id
    assert scenario["values"]["assessments"][0] == {
        "rule_id": "R-STK-003",
        "status": "EVALUABLE",
        "outcome": "TRUE",
        "evidence_ids": ["EV-R-STK-003"],
        "reason": "scenario child assessment",
    }
    assert scenario["values"]["viability_result"]["assessment_ids"] == [
        "FRONTIER-ASSESSMENT-X"
    ]
    assert scenario["trace_references"] == [binding.trace.trace_id]

    forbidden = {
        "score",
        "ranking",
        "recommendation",
        "approval",
        "rejection",
        "best_scenario",
        "selected_scenario",
        "decision",
    }
    assert forbidden.isdisjoint(scenario)
    assert forbidden.isdisjoint(scenario["values"]["assessments"][0])


def test_inputs_are_immutable_and_output_is_detached() -> None:
    preparation = _preparation()
    purchase = _child_purchase(preparation)
    binding = _binding(preparation)
    vf = _viability(preparation)
    preparation_before = preparation.model_copy(deep=True)
    purchase_before = purchase.model_copy(deep=True)
    binding_before = binding.model_copy(deep=True)
    vf_before = deepcopy(vf)

    package = build_authorized_scenario_analytics_from_provenanced_assessments(
        preparation=preparation,
        scenario_id=preparation.materialization.scenarios[0].scenario_id,
        purchase=purchase,
        assessment_bindings=(binding,),
        viability_result=vf,
    )
    package.assessments[0]["reason"] = "mutated output"
    package.viability_result["assessment_ids"] += ("MUTATED",)

    assert preparation == preparation_before
    assert purchase == purchase_before
    assert binding == binding_before
    assert vf == vf_before
