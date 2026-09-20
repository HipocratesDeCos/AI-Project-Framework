from copy import deepcopy

from eios.frontend.application_boundary import present_vertical_mvp_result
from eios.frontend.visual.vertical_mvp_renderer import render_vertical_mvp_readonly
from eios.frontend.visual.vertical_mvp_view_model import build_vertical_mvp_view_model
from test_vertical_mvp_frontend_presentation import _result_with_rules
from test_vertical_mvp_scenario_support_presentation import _vertical_result


def _full_visual_chain(result):
    payload = present_vertical_mvp_result(result)
    view_model = build_vertical_mvp_view_model(payload)
    return payload, view_model, render_vertical_mvp_readonly(view_model)


def test_rules_crc_path_reaches_readonly_html_without_semantic_loss():
    result = _result_with_rules()
    original = result.model_copy(deep=True)

    payload, view, html = _full_visual_chain(result)

    assert payload["execution"]["status"] == "COMPLETED"
    assert view["execution_status"] == "COMPLETED"
    assert view["rules_available"] is True
    assert view["scenario_support_available"] is False

    assert payload["rules"]["consolidated_result"] == "NEGOCIAR"
    assert view["crc_support_result"]["consolidated_result"] == "NEGOCIAR"
    assert "Resultado de soporte CRC — no decisión humana" in html
    assert "NEGOCIAR" in html

    assert payload["rules"]["executed_rule_ids"] == ["R-STK-003"]
    assert view["rule_coverage"]["executed_rule_ids"] == ["R-STK-003"]
    assert "R-STK-003" in html
    assert "EV-STK" in html

    trace = payload["rules"]["trace_references"][0]
    assert trace in view["rule_trace_references"]
    assert trace in html

    assert "SOPORTE DE ESCENARIOS NO SUMINISTRADO" in html
    assert result == original


def test_scenario_path_reaches_readonly_html_preserving_failure_and_uncertainty():
    result = _vertical_result()
    original = result.model_copy(deep=True)

    payload, view, html = _full_visual_chain(result)

    assert payload["rules"] is None
    assert view["rules_available"] is False
    assert "BLOQUE RULES/CRC NO SUMINISTRADO" in html

    assert view["scenario_support_available"] is True
    assert [item["scenario_id"] for item in view["scenario_records"]] == [
        "SC-A",
        "SC-B",
    ]
    assert view["scenario_records"][0]["status"] == "NOT_EVALUABLE"
    assert view["scenario_records"][1]["status"] == "FAILED"
    assert view["scenario_records"][1]["failure_reason"] == "technical failure"

    assert "Escenario SC-A" in html
    assert "Escenario SC-B" in html
    assert "NOT_EVALUABLE" in html
    assert "FAILED" in html
    assert "technical failure" in html
    assert "missing-evidence" in html
    assert "technical-gap" in html
    assert "TRACE-A" in html
    assert "TRACE-B" in html

    assert "Esta capa no selecciona ni ordena escenarios." in html
    assert result == original


def test_public_visual_chain_does_not_create_decisional_or_ranking_surface():
    _, _, rules_html = _full_visual_chain(_result_with_rules())
    _, _, scenario_html = _full_visual_chain(_vertical_result())

    for html in (rules_html, scenario_html):
        lowered = html.lower()
        assert "best scenario" not in lowered
        assert "mejor escenario" not in lowered
        assert "ranking" not in lowered
        assert "score" not in lowered
        assert "approval" not in lowered
        assert "aprobación automática" not in lowered
        assert "no ejecuta motores ni constituye decisión humana" in lowered


def test_each_stage_returns_detached_presentation_material():
    result = _vertical_result()
    original = result.model_copy(deep=True)

    payload = present_vertical_mvp_result(result)
    payload_before = deepcopy(payload)
    view = build_vertical_mvp_view_model(payload)
    html = render_vertical_mvp_readonly(view)

    view["scenario_records"][0]["trace_references"].append("MUTATED-AFTER-RENDER")
    payload["scenario_support"]["scenarios"][0]["trace_references"].append(
        "MUTATED-PAYLOAD"
    )

    assert "MUTATED-AFTER-RENDER" not in html
    assert "MUTATED-PAYLOAD" not in html
    assert result == original
    assert payload_before != payload
