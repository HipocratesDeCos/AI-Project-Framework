from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.decision_twin import AlternativeRepresentation
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.orchestration import O1ExecutionStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.core.viability_frontier import ViabilityResult, ViabilityStatus
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedDecisionTwinAlternativeInput,
    ProvenancedScenarioAnalyticsInput,
    authorized_rule,
    build_provenanced_decision_twin_comparison,
    build_provenanced_decision_twin_invoker,
)


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-DT-PROV",
        scenario_id="BASE",
        rules_version="RULES-DT-PROV-1",
        parameters_version="PARAMS-DT-PROV-1",
        data_snapshot_id="SNAP-DT-PROV-1",
    )


def _root_purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-DT-PROV",
        scenario_id="BASE",
        article_id="ART-DT",
        supplier_id="SUP-DT",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )


def _preparation(domain=(1, 2)):
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
        policy=GenerationPolicy(policy_version="O4-DT-PROV-1"),
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


def _analytics(
    preparation,
    scenario_id: str,
    *,
    viability_status: ViabilityStatus = ViabilityStatus.VIABLE,
) -> ProvenancedScenarioAnalyticsInput:
    context = _child_context(preparation, scenario_id)
    purchase = PurchaseOperation(
        decision_id=context.decision_id,
        scenario_id=scenario_id,
        article_id="ART-DT",
        supplier_id="SUP-DT",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 12),
    )
    assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=[f"EV-{scenario_id}"],
        reason="decision twin provenance assessment",
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
        status=viability_status,
        assessment_ids=(f"VF-A-{scenario_id}",),
        rule_ids=(f"VF-R-{scenario_id}",),
        trace_references=(f"VF-T-{scenario_id}",),
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        limitation=(
            "MATERIAL_INSUFFICIENCY"
            if viability_status == ViabilityStatus.NOT_EVALUABLE
            else None
        ),
    )
    return ProvenancedScenarioAnalyticsInput(
        scenario_id=scenario_id,
        purchase=purchase,
        assessment_bindings=(
            AssessmentTraceBinding(assessment=assessment, trace=trace),
        ),
        viability_result=viability,
    )


def _alternatives(preparation):
    scenario_ids = tuple(item.scenario_id for item in preparation.materialization.scenarios)
    return (
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-A",
            analytics=_analytics(preparation, scenario_ids[0]),
        ),
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-B",
            analytics=_analytics(
                preparation,
                scenario_ids[1],
                viability_status=ViabilityStatus.NOT_EVALUABLE,
            ),
        ),
    )


def test_comparison_is_rebuilt_from_provenanced_stage2_inputs() -> None:
    preparation = _preparation()
    alternatives = _alternatives(preparation)

    comparison = build_provenanced_decision_twin_comparison(
        preparation=preparation,
        alternatives=alternatives,
        purchase=_root_purchase(),
        context=_context(),
    )

    assert comparison.alternatives == ("ALT-A", "ALT-B")
    scenario_ids = {
        item.analytics.scenario_id for item in alternatives
    }
    assert not scenario_ids.intersection(comparison.alternatives)

    viability = next(
        item for item in comparison.observations if item.attribute == "viability"
    )
    assert dict(viability.values) == {
        "ALT-A": "VIABLE",
        "ALT-B": "NOT_EVALUABLE",
    }
    assert comparison.viability_differences == ("viability",)

    expected_traces = tuple(
        sorted(
            item.analytics.assessment_bindings[0].trace.trace_id
            for item in alternatives
        )
    )
    assert comparison.trace_refs == expected_traces


def test_not_evaluable_is_preserved_literally() -> None:
    preparation = _preparation()
    comparison = build_provenanced_decision_twin_comparison(
        preparation=preparation,
        alternatives=_alternatives(preparation),
        purchase=_root_purchase(),
        context=_context(),
    )
    viability = next(
        item for item in comparison.observations if item.attribute == "viability"
    )

    assert "NOT_EVALUABLE" in tuple(value for _, value in viability.values)
    assert "NOT_VIABLE" not in tuple(value for _, value in viability.values)


def test_foreign_root_context_is_rejected_before_comparison() -> None:
    preparation = _preparation()
    foreign = _context().model_copy(update={"data_snapshot_id": "SNAP-FOREIGN"})

    with pytest.raises(ValueError, match="preparación Decision Twin"):
        build_provenanced_decision_twin_comparison(
            preparation=preparation,
            alternatives=_alternatives(preparation),
            purchase=_root_purchase(),
            context=foreign,
        )


def test_foreign_root_purchase_is_rejected() -> None:
    preparation = _preparation()
    foreign = _root_purchase().model_copy(update={"scenario_id": "OTHER"})

    with pytest.raises(ValueError, match="PurchaseOperation"):
        build_provenanced_decision_twin_comparison(
            preparation=preparation,
            alternatives=_alternatives(preparation),
            purchase=foreign,
            context=_context(),
        )


def test_duplicate_representation_reference_fails_closed() -> None:
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    duplicated = (
        alternatives[0],
        replace(alternatives[1], representation_ref="ALT-A"),
    )

    with pytest.raises(ValueError, match="representation_ref"):
        build_provenanced_decision_twin_invoker(
            preparation=preparation,
            alternatives=duplicated,
        )


def test_opaque_alternative_representation_is_not_accepted() -> None:
    preparation = _preparation()
    opaque = (
        AlternativeRepresentation(representation_ref="A"),
        AlternativeRepresentation(representation_ref="B"),
    )

    with pytest.raises(TypeError, match="ProvenancedDecisionTwinAlternativeInput"):
        build_provenanced_decision_twin_invoker(
            preparation=preparation,
            alternatives=opaque,
        )


def test_manipulated_trace_is_rejected_by_stage2_provenance() -> None:
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    first = alternatives[0]
    binding = first.analytics.assessment_bindings[0]
    bad_trace = binding.trace.model_copy(update={"trace_id": "BROKEN-TRACE"})
    bad_analytics = replace(
        first.analytics,
        assessment_bindings=(
            AssessmentTraceBinding(
                assessment=binding.assessment,
                trace=bad_trace,
            ),
        ),
    )
    bad_alternatives = (
        replace(first, analytics=bad_analytics),
        alternatives[1],
    )

    with pytest.raises(ValueError, match="trace_id"):
        build_provenanced_decision_twin_comparison(
            preparation=preparation,
            alternatives=bad_alternatives,
            purchase=_root_purchase(),
            context=_context(),
        )


def test_stage2_coverage_must_be_exact() -> None:
    preparation = _preparation(domain=(1, 2, 3))
    scenario_ids = tuple(item.scenario_id for item in preparation.materialization.scenarios)
    alternatives = (
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-A",
            analytics=_analytics(preparation, scenario_ids[0]),
        ),
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-B",
            analytics=_analytics(preparation, scenario_ids[1]),
        ),
    )

    with pytest.raises(ValueError, match="faltan paquetes analíticos"):
        build_provenanced_decision_twin_comparison(
            preparation=preparation,
            alternatives=alternatives,
            purchase=_root_purchase(),
            context=_context(),
        )


def test_invoker_freezes_provenance_snapshot() -> None:
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    invoker = build_provenanced_decision_twin_invoker(
        preparation=preparation,
        alternatives=alternatives,
    )
    original_trace = alternatives[0].analytics.assessment_bindings[0].trace.trace_id

    alternatives[0].analytics.assessment_bindings[0].assessment.reason = "mutated later"

    result = invoker(_root_purchase(), _context())

    assert result.capability == "DECISION_TWIN"
    assert result.status == O1ExecutionStatus.COMPLETED
    assert result.result_available is True
    assert original_trace in result.trace_references


def test_invoker_rejects_foreign_context_on_reuse() -> None:
    preparation = _preparation()
    invoker = build_provenanced_decision_twin_invoker(
        preparation=preparation,
        alternatives=_alternatives(preparation),
    )
    foreign = _context().model_copy(update={"decision_id": "D-FOREIGN"})

    with pytest.raises(ValueError, match="preparación Decision Twin"):
        invoker(_root_purchase(), foreign)
