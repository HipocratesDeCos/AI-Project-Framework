from datetime import date
from decimal import Decimal

import pytest

from eios.core.c0_reproducibility import build_trace
from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import prepare_o4_o2_o3_orchestration
from eios.core.orchestration import O1ExecutionStatus
from eios.core.scenario_generation import GenerationPolicy, GenerationVariable
from eios.rules import (
    AssessmentTraceBinding,
    ProvenancedDecisionTwinAlternativeInput,
    ProvenancedScenarioAnalyticsInput,
    build_provenanced_decision_twin_comparison,
    build_provenanced_decision_twin_invoker,
)
from eios.rules.catalog import authorized_rule


RULES_VERSION = "rules-v1"


def _root_context():
    return DecisionContext(
        decision_id="D-TWIN-PROV",
        scenario_id="BASE",
        rules_version=RULES_VERSION,
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _root_purchase():
    return PurchaseOperation(
        decision_id="D-TWIN-PROV",
        scenario_id="BASE",
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=date(2026, 9, 23),
    )


def _preparation():
    return prepare_o4_o2_o3_orchestration(
        context=_root_context(),
        variables=(
            GenerationVariable(
                variable_id="quantity_delta",
                value_type="integer",
                base_value=0,
                domain=(1, 2),
            ),
        ),
        policy=GenerationPolicy(policy_version="O4-TWIN-PROV-1"),
    )


def _child_purchase(scenario_id: str):
    return _root_purchase().model_copy(update={"scenario_id": scenario_id})


def _binding(scenario_id: str, *, rule_id="R-FIN-001", outcome="FALSE"):
    context = _root_context().model_copy(update={"scenario_id": scenario_id})
    purchase = _child_purchase(scenario_id)
    assessment = Assessment(
        rule_id=rule_id,
        status="EVALUABLE",
        outcome=outcome,
        evidence_ids=[f"EV-{scenario_id}-{rule_id}"],
        reason=f"{rule_id} {scenario_id}",
    )
    trace = build_trace(
        context,
        purchase,
        authorized_rule(rule_id, RULES_VERSION),
        tuple(assessment.evidence_ids),
        assessment,
    )
    return AssessmentTraceBinding(assessment=assessment, trace=trace)


def _alternatives(preparation):
    scenario_ids = tuple(
        item.scenario_id
        for item in preparation.materialization.scenarios
        if item.status.value == "VALID"
    )
    assert len(scenario_ids) == 2
    return (
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-A",
            scenario_input=ProvenancedScenarioAnalyticsInput(
                scenario_id=scenario_ids[0],
                purchase=_child_purchase(scenario_ids[0]),
                assessment_bindings=(_binding(scenario_ids[0], outcome="FALSE"),),
            ),
        ),
        ProvenancedDecisionTwinAlternativeInput(
            representation_ref="ALT-B",
            scenario_input=ProvenancedScenarioAnalyticsInput(
                scenario_id=scenario_ids[1],
                purchase=_child_purchase(scenario_ids[1]),
                assessment_bindings=(_binding(scenario_ids[1], outcome="TRUE"),),
            ),
        ),
    )


def test_provenanced_twin_rebuilds_stage2_and_preserves_viability_literals():
    preparation = _preparation()
    alternatives = _alternatives(preparation)

    result = build_provenanced_decision_twin_comparison(
        purchase=_root_purchase(),
        context=_root_context(),
        preparation=preparation,
        alternatives=alternatives,
    )

    assert result.alternatives == ("ALT-A", "ALT-B")
    assert "viability" in result.differences
    viability = next(
        item for item in result.observations if item.attribute == "viability"
    )
    observed = dict(viability.values)
    assert observed["ALT-A"] == "VIABLE"
    assert observed["ALT-B"] == "NOT_VIABLE"
    assert result.missing_attributes == ()
    assert result.trace_refs


def test_provenanced_twin_does_not_invent_conditions_consequences_or_risks():
    preparation = _preparation()
    result = build_provenanced_decision_twin_comparison(
        purchase=_root_purchase(),
        context=_root_context(),
        preparation=preparation,
        alternatives=_alternatives(preparation),
    )

    by_attribute = {item.attribute: item for item in result.observations}
    assert all(value == {} for _, value in by_attribute["conditions"].values)
    assert all(value == {} for _, value in by_attribute["consequences"].values)
    assert all(value == () for _, value in by_attribute["risk_refs"].values)


def test_twin_invoker_is_o1_compatible():
    preparation = _preparation()
    invoker = build_provenanced_decision_twin_invoker(
        preparation=preparation,
        alternatives=_alternatives(preparation),
    )

    capability = invoker(_root_purchase(), _root_context())
    assert capability.capability == "DECISION_TWIN"
    assert capability.status == O1ExecutionStatus.COMPLETED
    assert capability.result_available is True
    assert capability.trace_references


def test_root_context_mismatch_fails_closed():
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    foreign = _root_context().model_copy(update={"data_snapshot_id": "foreign"})

    with pytest.raises(ValueError, match="data_snapshot_id incompatible"):
        build_provenanced_decision_twin_comparison(
            purchase=_root_purchase(),
            context=foreign,
            preparation=preparation,
            alternatives=alternatives,
        )


def test_duplicate_representation_ref_fails_closed():
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    duplicate = alternatives[1].model_copy(update={"representation_ref": "ALT-A"})

    with pytest.raises(ValueError, match="representation_ref duplicada"):
        build_provenanced_decision_twin_comparison(
            purchase=_root_purchase(),
            context=_root_context(),
            preparation=preparation,
            alternatives=(alternatives[0], duplicate),
        )


def test_duplicate_scenario_id_fails_closed():
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    duplicate = alternatives[1].model_copy(
        update={"scenario_input": alternatives[0].scenario_input.model_copy(deep=True)}
    )

    with pytest.raises(ValueError, match="scenario_id analítico duplicado"):
        build_provenanced_decision_twin_comparison(
            purchase=_root_purchase(),
            context=_root_context(),
            preparation=preparation,
            alternatives=(alternatives[0], duplicate),
        )


def test_invoker_freezes_provenanced_material_against_later_mutation():
    preparation = _preparation()
    alternatives = _alternatives(preparation)
    invoker = build_provenanced_decision_twin_invoker(
        preparation=preparation,
        alternatives=alternatives,
    )

    alternatives[0].scenario_input.assessment_bindings[0].assessment.reason = "tampered later"

    capability = invoker(_root_purchase(), _root_context())
    assert capability.status == O1ExecutionStatus.COMPLETED


def test_less_than_two_alternatives_is_rejected():
    preparation = _preparation()
    with pytest.raises(ValueError, match="al menos dos alternativas"):
        build_provenanced_decision_twin_invoker(
            preparation=preparation,
            alternatives=(_alternatives(preparation)[0],),
        )
