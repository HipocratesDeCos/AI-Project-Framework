from types import SimpleNamespace

import pytest

from eios.frontend.visual.view_model import build_view_model


def test_view_model_requires_contractual_model():
    with pytest.raises(TypeError):
        build_view_model({})


def test_view_model_is_presentation_copy():
    source = SimpleNamespace(
        model_dump=lambda mode=None: {
            "execution": {"status": "COMPLETED"},
            "result": {"decision": "INFORMATION"},
            "evidence": [{"id": "E1"}],
            "trace": ["T1"],
            "scenarios": [{"scenario_id": "S1", "status": "VALID"}],
            "limitations": ["L1"],
            "decision_id": "D1",
            "scenario_id": "S1",
            "execution_id": "X1",
            "rules_version": "R1",
            "parameters_version": "P1",
            "data_snapshot_id": "SN1",
        }
    )
    view = build_view_model(source)
    assert view["execution"]["status"] == "COMPLETED"
    assert view["result"]["decision"] == "INFORMATION"
    assert view["identity"]["decision_id"] == "D1"
    assert view["scenarios"][0]["scenario_id"] == "S1"
    assert view["limitations"] == ["L1"]
    view["scenarios"].append({"scenario_id": "S2"})
    assert len(source.model_dump()["scenarios"]) == 1


def test_view_model_does_not_invent_authority_fields():
    source = SimpleNamespace(model_dump=lambda mode=None: {"result": {"status": "COMPLETED"}})
    view = build_view_model(source)
    forbidden = {"score", "ranking", "recommendation", "approval", "best_scenario"}
    assert forbidden.isdisjoint(view)
