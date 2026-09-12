import copy

import pytest

from eios.frontend.visual.vertical_mvp_view_model import build_vertical_mvp_view_model


def _payload_with_rules():
    return {
        "execution": {
            "status": "COMPLETED",
            "policy_version": "MVP-E2E-1",
            "unresolved_items": ["CAP-X"],
            "failure_reason": None,
            "capabilities": [
                {
                    "capability": "C0",
                    "status": "COMPLETED",
                    "result_available": True,
                    "trace_references": ["TRACE-C0"],
                    "unresolved_items": [],
                }
            ],
        },
        "rules": {
            "executed_rule_ids": ["R-STK-003", "R-FIN-001"],
            "omitted_rule_ids": ["R-PAG-001"],
            "consolidated_result": "NEGOCIAR",
            "dominant_reason": "R-STK-003",
            "relevant_factors": ["stock"],
            "conflicts": [],
            "assessments": [
                {
                    "rule_id": "R-STK-003",
                    "status": "EVALUABLE",
                    "outcome": "TRUE",
                    "reason": "Exceso demostrado.",
                    "evidence_ids": ["EV-STK"],
                },
                {
                    "rule_id": "R-FIN-001",
                    "status": "NOT_EVALUABLE",
                    "outcome": None,
                    "reason": "Evidencia financiera insuficiente.",
                    "evidence_ids": ["EV-FIN"],
                },
            ],
            "trace_references": ["TRACE-RULES"],
        },
        "scenario_support": None,
    }


def test_vertical_view_model_maps_execution_rules_crc_and_traceability():
    view = build_vertical_mvp_view_model(_payload_with_rules())

    assert view["execution_status"] == "COMPLETED"
    assert view["policy_version"] == "MVP-E2E-1"
    assert view["capabilities"][0]["capability"] == "C0"
    assert view["rules_available"] is True
    assert view["rule_coverage"]["executed_rule_ids"] == ["R-STK-003", "R-FIN-001"]
    assert view["rule_coverage"]["omitted_rule_ids"] == ["R-PAG-001"]
    assert view["crc_support_result"]["consolidated_result"] == "NEGOCIAR"
    assert view["rule_trace_references"] == ["TRACE-RULES"]
    assert view["scenario_support_available"] is False
    assert view["scenario_execution_context"] is None
    assert view["scenario_records"] is None
    assert view["scenario_comparison"] is None


def test_rules_null_remains_unavailable_instead_of_false_or_empty_result():
    payload = _payload_with_rules()
    payload["rules"] = None

    view = build_vertical_mvp_view_model(payload)

    assert view["rules_available"] is False
    assert view["rule_coverage"] is None
    assert view["crc_support_result"] is None
    assert view["assessments"] is None
    assert view["rule_trace_references"] is None


def test_omitted_rule_does_not_create_synthetic_assessment():
    view = build_vertical_mvp_view_model(_payload_with_rules())

    assert "R-PAG-001" in view["rule_coverage"]["omitted_rule_ids"]
    assert all(item["rule_id"] != "R-PAG-001" for item in view["assessments"])


def test_not_evaluable_is_preserved_without_becoming_false():
    view = build_vertical_mvp_view_model(_payload_with_rules())
    assessment = next(item for item in view["assessments"] if item["rule_id"] == "R-FIN-001")

    assert assessment["status"] == "NOT_EVALUABLE"
    assert assessment["outcome"] is None


def test_view_model_is_deep_presentation_copy():
    payload = _payload_with_rules()
    original = copy.deepcopy(payload)

    view = build_vertical_mvp_view_model(payload)
    view["capabilities"][0]["trace_references"].append("MUTATED")
    view["assessments"][0]["evidence_ids"].append("MUTATED")
    view["rule_coverage"]["executed_rule_ids"].append("MUTATED")

    assert payload == original


def test_view_model_does_not_invent_decision_authority_fields():
    view = build_vertical_mvp_view_model(_payload_with_rules())
    forbidden = {"score", "ranking", "recommendation", "approval", "best_scenario"}

    assert forbidden.isdisjoint(view)
    assert forbidden.isdisjoint(view["crc_support_result"])


def test_view_model_fails_closed_on_invalid_shape():
    with pytest.raises(TypeError):
        build_vertical_mvp_view_model([])
    with pytest.raises(ValueError, match="rules"):
        build_vertical_mvp_view_model({"execution": {}, "scenario_support": None})
    with pytest.raises(ValueError, match="scenario_support"):
        build_vertical_mvp_view_model({"execution": {}, "rules": None})
    with pytest.raises(ValueError, match="execution"):
        build_vertical_mvp_view_model(
            {"execution": None, "rules": None, "scenario_support": None}
        )
    with pytest.raises(ValueError, match="claves contractuales"):
        build_vertical_mvp_view_model(
            {"execution": {}, "rules": None, "scenario_support": None}
        )
    with pytest.raises(ValueError, match="rules"):
        payload = _payload_with_rules()
        payload["rules"] = []
        build_vertical_mvp_view_model(payload)
    with pytest.raises(ValueError, match="claves contractuales"):
        payload = _payload_with_rules()
        del payload["rules"]["assessments"]
        build_vertical_mvp_view_model(payload)
