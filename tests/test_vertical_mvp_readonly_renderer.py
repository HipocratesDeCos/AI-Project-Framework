import ast
import copy
import inspect

import pytest

import eios.frontend.visual.vertical_mvp_renderer as renderer_module
from eios.frontend.visual.vertical_mvp_renderer import render_vertical_mvp_readonly
from eios.frontend.visual.vertical_mvp_view_model import build_vertical_mvp_view_model


def _payload(*, rules=True, scenarios=True):
    return {
        "execution": {
            "status": "PARTIAL",
            "policy_version": "POLICY-MOCK-001",
            "unresolved_items": ["CAP-X"],
            "failure_reason": None,
            "capabilities": [
                {
                    "capability": "TCO",
                    "status": "NOT_EVALUABLE",
                    "result_available": False,
                    "trace_references": ["TRACE-TCO"],
                    "unresolved_items": ["TCO-MISSING"],
                },
                {
                    "capability": "C0",
                    "status": "COMPLETED",
                    "result_available": True,
                    "trace_references": ["TRACE-C0"],
                    "unresolved_items": [],
                },
            ],
        },
        "rules": (
            {
                "executed_rule_ids": ["R-STK-003", "R-FIN-001"],
                "omitted_rule_ids": ["R-PAG-001"],
                "consolidated_result": "NEGOCIAR",
                "dominant_reason": "R-STK-003",
                "relevant_factors": ["stock", "liquidez"],
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
            }
            if rules
            else None
        ),
        "scenario_support": (
            {
                "execution_context": {
                    "execution_id": "EXEC-MOCK-001",
                    "decision_id": "DECISION-MOCK-001",
                    "rules_version": "RULES-MOCK-001",
                    "parameters_version": "PARAM-MOCK-001",
                    "data_snapshot_id": "SNAPSHOT-MOCK-001",
                },
                "scenarios": [
                    {
                        "scenario_id": "SCENARIO-B",
                        "status": "NOT_EVALUABLE",
                        "values": {"price": "20.50"},
                        "trace_references": ["TRACE-B"],
                        "unresolved_items": ["UNKNOWN-B"],
                        "failure_reason": None,
                    },
                    {
                        "scenario_id": "SCENARIO-A",
                        "status": "COMPLETED",
                        "values": {"price": "19.75"},
                        "trace_references": ["TRACE-A"],
                        "unresolved_items": [],
                        "failure_reason": None,
                    },
                ],
                "comparison": {
                    "scenario_ids": ["SCENARIO-B", "SCENARIO-A"],
                    "observations": ["comparison only"],
                    "differences": [{"field": "price"}],
                    "missing": [],
                    "statuses": ["NOT_EVALUABLE", "COMPLETED"],
                    "unresolved_items": ["UNKNOWN-B"],
                    "traceability": ["TRACE-COMPARE"],
                },
            }
            if scenarios
            else None
        ),
    }


def _view(*, rules=True, scenarios=True):
    return build_vertical_mvp_view_model(
        _payload(rules=rules, scenarios=scenarios)
    )


def test_renderer_produces_complete_read_only_document_from_authorized_view_model():
    html = render_vertical_mvp_readonly(_view())

    assert html.startswith("<!doctype html>")
    assert '<section id="execution">' in html
    assert '<section id="capabilities">' in html
    assert '<section id="rules">' in html
    assert '<section id="scenarios">' in html
    assert "Estado técnico" in html
    assert "PARTIAL" in html
    assert "Resultado de soporte CRC — no decisión humana" in html
    assert "NEGOCIAR" in html
    assert "NOT_EVALUABLE" in html
    assert "Esta capa no selecciona ni ordena escenarios." in html


def test_rules_absence_is_explicitly_unavailable_not_favorable():
    html = render_vertical_mvp_readonly(_view(rules=False))

    assert "BLOQUE RULES/CRC NO SUMINISTRADO" in html
    assert "La ausencia no implica resultado favorable." in html
    assert "NEGOCIAR" not in html
    assert "R-PAG-001" not in html


def test_scenario_absence_is_explicitly_unavailable_not_no_risk():
    html = render_vertical_mvp_readonly(_view(scenarios=False))

    assert "SOPORTE DE ESCENARIOS NO SUMINISTRADO" in html
    assert "La ausencia no implica ausencia de riesgo." in html
    assert "SCENARIO-A" not in html
    assert "SCENARIO-B" not in html


def test_omitted_rules_and_not_evaluable_are_preserved_without_reinterpretation():
    html = render_vertical_mvp_readonly(_view())

    assert html.index("R-STK-003") < html.index("R-FIN-001")
    assert "R-PAG-001" in html
    assert "NOT_EVALUABLE" in html
    assert "NO DISPONIBLE" in html
    assert "Evidencia financiera insuficiente." in html


def test_renderer_preserves_capability_and_scenario_order():
    html = render_vertical_mvp_readonly(_view())

    assert html.index(">TCO<") < html.index(">C0<")
    assert html.index("Escenario SCENARIO-B") < html.index("Escenario SCENARIO-A")
    comparison_start = html.index("Comparación descriptiva")
    assert html.index("SCENARIO-B", comparison_start) < html.index(
        "SCENARIO-A", comparison_start
    )


def test_dynamic_content_is_html_escaped_and_never_trusted_as_markup():
    payload = _payload()
    payload["rules"]["assessments"][0]["reason"] = '<script>alert("owned")</script>'
    payload["scenario_support"]["scenarios"][0]["values"]["note"] = (
        '<img src=x onerror="alert(1)">'
    )

    html = render_vertical_mvp_readonly(build_vertical_mvp_view_model(payload))

    assert '<script>alert("owned")</script>' not in html
    assert '<img src=x onerror="alert(1)">' not in html
    assert "&lt;script&gt;alert(&quot;owned&quot;)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=\&quot;alert(1)\&quot;&gt;" in html


def test_renderer_does_not_mutate_authorized_view_model_and_is_deterministic():
    view = _view()
    original = copy.deepcopy(view)

    first = render_vertical_mvp_readonly(view)
    second = render_vertical_mvp_readonly(view)

    assert view == original
    assert first == second


def test_renderer_does_not_invent_forbidden_decisional_surfaces():
    html = render_vertical_mvp_readonly(_view()).lower()

    for forbidden in (
        "best scenario",
        "mejor escenario",
        "ranking",
        "score",
        "approval",
        "aprobación automática",
    ):
        assert forbidden not in html


def test_renderer_fails_closed_on_incomplete_or_inconsistent_view_model():
    with pytest.raises(TypeError):
        render_vertical_mvp_readonly([])

    view = _view()
    del view["execution_status"]
    with pytest.raises(ValueError, match="claves contractuales"):
        render_vertical_mvp_readonly(view)

    view = _view(rules=False)
    view["assessments"] = []
    with pytest.raises(ValueError, match="rules_available=false"):
        render_vertical_mvp_readonly(view)

    view = _view(scenarios=False)
    view["scenario_records"] = []
    with pytest.raises(ValueError, match="scenario_support_available=false"):
        render_vertical_mvp_readonly(view)


def test_renderer_module_has_no_eios_or_engine_imports():
    source = inspect.getsource(renderer_module)
    tree = ast.parse(source)
    imported = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")

    assert all(not name.startswith("eios") for name in imported)
    assert imported <= {
        "__future__",
        "collections.abc",
        "html",
        "json",
        "typing",
    }
