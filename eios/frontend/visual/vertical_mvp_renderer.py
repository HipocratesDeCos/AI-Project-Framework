"""Pure read-only HTML composition for an authorized Vertical MVP view-model.

The renderer consumes only the presentation Mapping produced by
build_vertical_mvp_view_model. It does not import or execute EIOS engines,
domain models, invokers, rules, CRC, scenarios, or other analytical
capabilities.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
import json
from typing import Any


_ROOT_KEYS = frozenset(
    {
        "execution_status",
        "policy_version",
        "failure_reason",
        "unresolved_items",
        "capabilities",
        "rules_available",
        "rule_coverage",
        "crc_support_result",
        "assessments",
        "rule_trace_references",
        "scenario_support_available",
        "scenario_execution_context",
        "scenario_records",
        "scenario_comparison",
    }
)
_CAPABILITY_KEYS = frozenset(
    {
        "capability",
        "status",
        "result_available",
        "trace_references",
        "unresolved_items",
    }
)
_ASSESSMENT_KEYS = frozenset(
    {"rule_id", "status", "outcome", "reason", "evidence_ids"}
)
_SCENARIO_CONTEXT_KEYS = frozenset(
    {
        "execution_id",
        "decision_id",
        "rules_version",
        "parameters_version",
        "data_snapshot_id",
    }
)
_SCENARIO_RECORD_KEYS = frozenset(
    {
        "scenario_id",
        "status",
        "values",
        "trace_references",
        "unresolved_items",
        "failure_reason",
    }
)
_SCENARIO_COMPARISON_KEYS = frozenset(
    {
        "scenario_ids",
        "observations",
        "differences",
        "missing",
        "statuses",
        "unresolved_items",
        "traceability",
    }
)


def _require_keys(section: Mapping[str, Any], required: frozenset[str], name: str) -> None:
    missing = required.difference(section.keys())
    if missing:
        raise ValueError(
            f"{name} carece de claves contractuales: {', '.join(sorted(missing))}"
        )


def _require_sequence(value: Any, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ValueError(f"{name} debe ser una secuencia")
    return value


def _validate_mapping_sequence(
    value: Any,
    required: frozenset[str],
    name: str,
) -> Sequence[Mapping[str, Any]]:
    sequence = _require_sequence(value, name)
    for index, item in enumerate(sequence):
        if not isinstance(item, Mapping):
            raise ValueError(f"{name}[{index}] debe ser un Mapping")
        _require_keys(item, required, f"{name}[{index}]")
    return sequence


def _validate_view_model(view_model: Mapping[str, Any]) -> None:
    if not isinstance(view_model, Mapping):
        raise TypeError("se requiere un view-model contractual de Vertical MVP")
    _require_keys(view_model, _ROOT_KEYS, "view_model")

    _validate_mapping_sequence(
        view_model["capabilities"], _CAPABILITY_KEYS, "capabilities"
    )
    _require_sequence(view_model["unresolved_items"], "unresolved_items")

    rules_available = view_model["rules_available"]
    if not isinstance(rules_available, bool):
        raise ValueError("rules_available debe ser booleano")
    if rules_available:
        coverage = view_model["rule_coverage"]
        crc = view_model["crc_support_result"]
        if not isinstance(coverage, Mapping):
            raise ValueError("rule_coverage debe ser un Mapping cuando rules_available=true")
        if not isinstance(crc, Mapping):
            raise ValueError(
                "crc_support_result debe ser un Mapping cuando rules_available=true"
            )
        _require_keys(
            coverage,
            frozenset({"executed_rule_ids", "omitted_rule_ids"}),
            "rule_coverage",
        )
        _require_keys(
            crc,
            frozenset(
                {
                    "consolidated_result",
                    "dominant_reason",
                    "relevant_factors",
                    "conflicts",
                }
            ),
            "crc_support_result",
        )
        _require_sequence(coverage["executed_rule_ids"], "executed_rule_ids")
        _require_sequence(coverage["omitted_rule_ids"], "omitted_rule_ids")
        _require_sequence(crc["relevant_factors"], "relevant_factors")
        _require_sequence(crc["conflicts"], "conflicts")
        _validate_mapping_sequence(
            view_model["assessments"], _ASSESSMENT_KEYS, "assessments"
        )
        _require_sequence(view_model["rule_trace_references"], "rule_trace_references")
    elif any(
        view_model[key] is not None
        for key in (
            "rule_coverage",
            "crc_support_result",
            "assessments",
            "rule_trace_references",
        )
    ):
        raise ValueError("rules_available=false requiere bloques Rules/CRC ausentes")

    scenario_available = view_model["scenario_support_available"]
    if not isinstance(scenario_available, bool):
        raise ValueError("scenario_support_available debe ser booleano")
    if scenario_available:
        context = view_model["scenario_execution_context"]
        if not isinstance(context, Mapping):
            raise ValueError(
                "scenario_execution_context debe ser un Mapping cuando "
                "scenario_support_available=true"
            )
        _require_keys(context, _SCENARIO_CONTEXT_KEYS, "scenario_execution_context")
        _validate_mapping_sequence(
            view_model["scenario_records"],
            _SCENARIO_RECORD_KEYS,
            "scenario_records",
        )
        comparison = view_model["scenario_comparison"]
        if comparison is not None:
            if not isinstance(comparison, Mapping):
                raise ValueError("scenario_comparison debe ser null o un Mapping")
            _require_keys(
                comparison, _SCENARIO_COMPARISON_KEYS, "scenario_comparison"
            )
    elif any(
        view_model[key] is not None
        for key in (
            "scenario_execution_context",
            "scenario_records",
            "scenario_comparison",
        )
    ):
        raise ValueError(
            "scenario_support_available=false requiere bloques de escenario ausentes"
        )


def _text(value: Any) -> str:
    if value is None:
        return "NO DISPONIBLE"
    if isinstance(value, bool):
        return "true" if value else "false"
    return escape(str(value), quote=True)


def _json_text(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=False,
        indent=2,
        allow_nan=False,
    )
    return escape(serialized, quote=True)


def _list(items: Sequence[Any]) -> str:
    if not items:
        return '<p class="empty">SIN ELEMENTOS SUMINISTRADOS</p>'
    return "<ul>" + "".join(f"<li>{_text(item)}</li>" for item in items) + "</ul>"


def _capabilities(items: Sequence[Mapping[str, Any]]) -> str:
    if not items:
        return '<p class="empty">SIN CAPACIDADES SUMINISTRADAS</p>'
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{_text(item['capability'])}</td>"
            f"<td>{_text(item['status'])}</td>"
            f"<td>{_text(item['result_available'])}</td>"
            f"<td>{_list(item['trace_references'])}</td>"
            f"<td>{_list(item['unresolved_items'])}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>Capacidad</th><th>Estado técnico</th>"
        "<th>Resultado disponible</th><th>Trazas</th><th>No resueltos</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _assessments(items: Sequence[Mapping[str, Any]]) -> str:
    if not items:
        return '<p class="empty">SIN ASSESSMENTS SUMINISTRADOS</p>'
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{_text(item['rule_id'])}</td>"
            f"<td>{_text(item['status'])}</td>"
            f"<td>{_text(item['outcome'])}</td>"
            f"<td>{_text(item['reason'])}</td>"
            f"<td>{_list(item['evidence_ids'])}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>Regla</th><th>Estado</th><th>Outcome</th>"
        "<th>Razón</th><th>Evidencia</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _scenario_records(items: Sequence[Mapping[str, Any]]) -> str:
    if not items:
        return '<p class="empty">SIN ESCENARIOS SUMINISTRADOS</p>'
    cards = []
    for item in items:
        cards.append(
            '<article class="subcard">'
            f"<h3>Escenario {_text(item['scenario_id'])}</h3>"
            f"<p><b>Estado:</b> {_text(item['status'])}</p>"
            f"<p><b>Fallo:</b> {_text(item['failure_reason'])}</p>"
            "<h4>Valores</h4>"
            f"<pre>{_json_text(item['values'])}</pre>"
            "<h4>Trazas</h4>"
            f"{_list(item['trace_references'])}"
            "<h4>No resueltos</h4>"
            f"{_list(item['unresolved_items'])}"
            "</article>"
        )
    return "".join(cards)


def render_vertical_mvp_readonly(view_model: Mapping[str, Any]) -> str:
    """Render one authorized Vertical MVP presentation view-model as safe HTML."""
    _validate_view_model(view_model)

    if view_model["rules_available"]:
        coverage = view_model["rule_coverage"]
        crc = view_model["crc_support_result"]
        rules_html = (
            '<div class="two-col">'
            '<article class="subcard"><h3>Cobertura de reglas</h3>'
            "<h4>Ejecutadas</h4>"
            f"{_list(coverage['executed_rule_ids'])}"
            "<h4>Omitidas</h4>"
            f"{_list(coverage['omitted_rule_ids'])}"
            "</article>"
            '<article class="subcard"><h3>Resultado de soporte CRC — no decisión humana</h3>'
            f"<p><b>Resultado:</b> {_text(crc['consolidated_result'])}</p>"
            f"<p><b>Razón dominante:</b> {_text(crc['dominant_reason'])}</p>"
            "<h4>Factores relevantes</h4>"
            f"{_list(crc['relevant_factors'])}"
            "<h4>Conflictos</h4>"
            f"{_list(crc['conflicts'])}"
            "</article></div>"
            "<h3>Assessments</h3>"
            f"{_assessments(view_model['assessments'])}"
            "<h3>Referencias de traza Rules/CRC</h3>"
            f"{_list(view_model['rule_trace_references'])}"
        )
    else:
        rules_html = (
            '<p class="unavailable">BLOQUE RULES/CRC NO SUMINISTRADO. '
            "La ausencia no implica resultado favorable.</p>"
        )

    if view_model["scenario_support_available"]:
        scenario_html = (
            "<h3>Contexto de ejecución de escenarios</h3>"
            f"<pre>{_json_text(view_model['scenario_execution_context'])}</pre>"
            "<h3>Registros de escenarios</h3>"
            f"{_scenario_records(view_model['scenario_records'])}"
            "<h3>Comparación descriptiva</h3>"
            f"<pre>{_json_text(view_model['scenario_comparison'])}</pre>"
            '<p class="notice">La comparación es descriptiva. '
            "Esta capa no selecciona ni ordena escenarios.</p>"
        )
    else:
        scenario_html = (
            '<p class="unavailable">SOPORTE DE ESCENARIOS NO SUMINISTRADO. '
            "La ausencia no implica ausencia de riesgo.</p>"
        )

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EIOS · Vertical MVP · Solo lectura</title>
<style>
:root{{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f4f6fa;--line:#dfe4ec;--muted:#667085;--panel:#fff;--accent:#315efb}}
*{{box-sizing:border-box}}body{{margin:0}}a{{color:inherit}}.shell{{max-width:1440px;margin:auto;padding:24px}}.top{{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;flex-wrap:wrap}}h1{{margin:.3rem 0}}.eyebrow{{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}.notice,.unavailable{{padding:12px 14px;border-left:4px solid var(--accent);background:#f7f8ff}}nav{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}}nav a{{text-decoration:none;background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 12px}}section{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;margin:16px 0}}.two-col{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.subcard{{border:1px solid var(--line);border-radius:10px;padding:14px;margin:10px 0}}.table-wrap{{overflow:auto}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid var(--line);padding:10px;vertical-align:top;text-align:left}}th{{font-size:12px;color:var(--muted)}}ul{{margin:.35rem 0;padding-left:20px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f7f8fa;padding:12px;border-radius:8px;border:1px solid var(--line)}}.empty{{color:var(--muted);font-size:13px}}.meta{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.meta div{{border:1px solid var(--line);border-radius:10px;padding:12px}}@media(max-width:800px){{.two-col,.meta{{grid-template-columns:1fr}}.shell{{padding:14px}}}}
</style>
</head>
<body>
<main class="shell">
<header class="top">
<div>
<div class="eyebrow">EIOS · Vertical MVP</div>
<h1>Composición visual de solo lectura</h1>
<p>Presenta resultados ya producidos. No ejecuta motores ni constituye decisión humana.</p>
</div>
</header>
<nav aria-label="Secciones">
<a href="#execution">Ejecución</a>
<a href="#capabilities">Capacidades</a>
<a href="#rules">Rules / CRC</a>
<a href="#scenarios">Escenarios</a>
</nav>
<section id="execution">
<h2>Ejecución</h2>
<div class="meta">
<div><b>Estado técnico</b><br>{_text(view_model['execution_status'])}</div>
<div><b>Versión de política</b><br>{_text(view_model['policy_version'])}</div>
<div><b>Fallo técnico</b><br>{_text(view_model['failure_reason'])}</div>
</div>
<h3>Elementos no resueltos</h3>
{_list(view_model['unresolved_items'])}
</section>
<section id="capabilities">
<h2>Capacidades</h2>
{_capabilities(view_model['capabilities'])}
</section>
<section id="rules">
<h2>Rules / CRC</h2>
{rules_html}
</section>
<section id="scenarios">
<h2>Escenarios</h2>
{scenario_html}
</section>
</main>
</body>
</html>"""


__all__ = ["render_vertical_mvp_readonly"]
