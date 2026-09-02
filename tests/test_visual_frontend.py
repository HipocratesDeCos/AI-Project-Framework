from types import SimpleNamespace

import pytest

from eios.frontend.visual.view_model import build_view_model


def test_view_model_requires_contractual_model():
    with pytest.raises(TypeError):
        build_view_model({})


def test_view_model_maps_real_o1_fields():
    source = SimpleNamespace(
        model_dump=lambda mode=None: {
            "execution_context": {
                "execution_id": "X1",
                "decision_id": "D1",
                "scenario_id": "S1",
                "rules_version": "R1",
                "parameters_version": "P1",
                "data_snapshot_id": "SN1",
            },
            "execution_status": "COMPLETED",
            "capability_results": [{"capability": "TCO", "status": "COMPLETED"}],
            "evidence_status": ["VALID"],
            "trace_references": ["T1"],
            "unresolved_items": [],
        }
    )
    view = build_view_model(source)
    assert view["execution_status"] == "COMPLETED"
    assert view["capability_results"][0]["capability"] == "TCO"
    assert view["evidence_status"] == ["VALID"]
    assert view["trace_references"] == ["T1"]
    assert view["identity"]["decision_id"] == "D1"
    assert view["identity"]["execution_id"] == "X1"


def test_view_model_is_presentation_copy():
    source = SimpleNamespace(
        model_dump=lambda mode=None: {
            "execution_context": {"decision_id": "D1", "scenario_id": "S1"},
            "execution_status": "COMPLETED",
            "capability_results": [{"capability": "TCO"}],
        }
    )
    view = build_view_model(source)
    view["capability_results"].append({"capability": "S2"})
    assert len(source.model_dump()["capability_results"]) == 1


def test_view_model_does_not_invent_authority_fields():
    source = SimpleNamespace(model_dump=lambda mode=None: {"execution_status": "COMPLETED"})
    view = build_view_model(source)
    forbidden = {"score", "ranking", "recommendation", "approval", "best_scenario"}
    assert forbidden.isdisjoint(view)
