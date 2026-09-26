"""Export a static, synthetic purchasing walkthrough from a verified demo."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path

from .reference_business_case_demo import verify_reference_demo


_SIDECARS = (
    ("price", "Precio observado", "price_result", "pr_value", "pr_limitations"),
    ("tco", "Coste de adquisición modelado", "tco_result", "value", "limitations"),
    ("supplier-risk", "Riesgo y valor del proveedor", "supplier_result", None, None),
    ("c0", "Evaluación C0 y consolidación CRC", "crc_result", "consolidated_result", None),
    ("decision-twin", "Comparación de alternativas", "comparison", None, None),
    ("scenario-coordination", "Coordinación de escenarios", "support", None, None),
    ("negotiation-intelligence", "Contenido de negociación", "ni_result", None, None),
    ("negotiation-ladder", "Secuencia de negociación", "ladder_result", None, None),
)


def render_buyer_preview(directory: Path) -> str:
    """Verify full fixture replay, then project existing facts without recalculation."""
    directory = Path(directory)
    verify_reference_demo(directory)
    return _render_verified_buyer_preview(directory)


def _render_verified_buyer_preview(directory: Path) -> str:
    """Project a bundle that the caller has already replay-verified."""

    def safe(value: object) -> str:
        return escape(str(value), quote=True)

    negative = json.loads((directory / "reference-negative-result.json").read_text(encoding="utf-8"))
    eligible = json.loads((directory / "reference-result.json").read_text(encoding="utf-8"))
    if negative["purchase"] != eligible["purchase"]:
        raise ValueError("Reference variants have different purchase proposals")
    purchase = negative["purchase"]
    overview_cards = "".join(
        f'<div class="overview-card"><dt>{safe(label)}</dt>'
        f'<dd><strong>{safe(terminal["qtg_quality_result"]["status"])} / '
        f'{safe(terminal["qtg_quality_result"]["confidence"])}</strong></dd>'
        f'<dd>Ejecución técnica: {safe(terminal["execution_outcome"]["status"])}</dd></div>'
        for label, terminal in (
            ("Evidencia insuficiente", negative),
            ("Entrada apta para la prueba", eligible),
        )
    )
    overview = (
        '<section class="overview"><h2>Resumen de las dos variantes</h2>'
        '<p>La propuesta es la misma; cambia la calidad de la evidencia QTG. '
        'La ejecución técnica completada no aprueba una compra.</p>'
        f'<dl class="overview-grid">{overview_cards}</dl></section>'
    )
    proposal = (
        '<section><h2>Propuesta ficticia común</h2>'
        '<p>Los datos siguientes son iguales en ambas variantes. La prueba cambia la '
        'calidad de la evidencia, no la propuesta de compra.</p>'
        '<dl class="proposal">'
        f'<div><dt>Artículo</dt><dd><code>{safe(purchase["article_id"])}</code></dd></div>'
        f'<div><dt>Proveedor</dt><dd><code>{safe(purchase["supplier_id"])}</code></dd></div>'
        f'<div><dt>Cantidad</dt><dd>{safe(purchase["quantity"])} unidades</dd></div>'
        f'<div><dt>Precio unitario propuesto</dt><dd>{safe(purchase["unit_price"])} {safe(purchase["currency"])}</dd></div>'
        f'<div><dt>Fecha de la operación ficticia</dt><dd>{safe(purchase["operation_date"])}</dd></div>'
        '</dl><p>El precio unitario es un dato de entrada; no se presenta como '
        'precio recomendado ni como coste total.</p></section>'
    )
    sections = []
    for variant, prefix, terminal in (
        ("Caso con calidad insuficiente", "reference-negative-", negative),
        ("Caso con calidad apta para la prueba", "reference-", eligible),
    ):
        qtg = terminal["qtg_quality_result"]
        checks = "".join(
            f'<li><strong>{safe(c["control"])}</strong>: {safe(c["reason"])} '
            f'({"no aplica" if not c["applicable"] else "satisfecho" if c["satisfied"] is True else "no satisfecho" if c["satisfied"] is False else "no evaluable"})</li>'
            for c in qtg["checks"]
        )
        observations = []
        for suffix, title, result_key, value_key, limits_key in _SIDECARS:
            path = directory / f"{prefix}{suffix}.json"
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            result = payload[result_key]
            value = (f'<p>Valor declarado: <strong>{safe(result[value_key])}</strong></p>'
                     if value_key and result.get(value_key) is not None else "")
            limits = ""
            if suffix == "price":
                amount = (f'{safe(result["pr_value"])} {safe(result["currency"])}'
                          if result["pr_value"] is not None else "sin valor justificable")
                value = (f'<p>Precio de referencia observado: <strong>{amount}</strong>. '
                         f'Referencias seleccionadas: {safe(len(result["reference_set"]))}; '
                         f'método: {safe(result["aggregation_method"])}.</p>')
                limits = ('<p>Es una referencia de transacciones ficticias comparables; '
                          'no es un precio objetivo, un techo autorizado ni una oferta del proveedor.</p>'
                          f'<p>Limitaciones declaradas por PRICE: '
                          f'{safe(", ".join(result["pr_limitations"]) or "ninguna")}</p>')
            elif suffix == "tco":
                amount = (f'{safe(result["value"])} {safe(result["currency"])}'
                          if result["value"] is not None else "sin importe disponible")
                value = (f'<p>Coste de adquisición modelado: <strong>{amount}</strong>. '
                         f'Componentes incluidos: {safe(", ".join(result["contributing_components"]) or "ninguno")}.</p>')
                limits = ('<p>El fixture no aporta importes atribuibles de transporte, seguros, '
                          'aranceles, financiación, almacenaje, obsolescencia ni devoluciones. '
                          'Lo no informado no equivale a coste cero ni a coste total empresarial.</p>'
                          f'<p>Limitaciones declaradas por TCO: '
                          f'{safe(", ".join(result["limitations"]) or "ninguna")}. '
                          f'Componentes pendientes declarados: '
                          f'{safe(", ".join(result["unresolved_components"]) or "ninguno")}.</p>')
            if suffix == "supplier-risk":
                dimensions = ", ".join(
                    f'{item["dimension"]}: {item["state"]}'
                    for item in result["risk_dimensions"]
                ) or "ninguna"
                sources = payload["source_inventory"]
                factual_count = sum(sources[key] for key in (
                    "observations", "historical_facts", "external_metrics", "signals",
                ))
                value = (
                    f'<p>Proveedor ficticio: <code>{safe(result["current_supplier_id"])}</code>. '
                    f'Dimensiones de riesgo declaradas: {safe(dimensions)}.</p>'
                    f'<p>Fuentes factuales incluidas en este fixture: {safe(factual_count)}. '
                    f'Comparación de valor disponible: {"sí" if payload["value_comparison_available"] else "no"}. '
                    'La valoración externa declarada no prueba desempeño real ni permite '
                    'seleccionar proveedor.</p>'
                )
            elif suffix == "decision-twin":
                viability = next((item for item in result["observations"]
                                  if item["attribute"] == "viability"), None)
                states = (", ".join(f"{ref}: {state}" for ref, state in viability["values"])
                          if viability is not None else "no informada")
                value = (f'<p>Representaciones comparadas: {safe(", ".join(result["alternatives"]))}. '
                         f'Viabilidad declarada por Stage 2: {safe(states)}.</p>'
                         f'<p>Diferencias en atributos incluidos: '
                         f'{safe(", ".join(result["differences"]) or "ninguna")}. '
                         f'Atributos faltantes: '
                         f'{safe(", ".join(result["missing_attributes"]) or "ninguno declarado")}.</p>')
                limits = ('<p>Las condiciones, consecuencias y riesgos no aportados por el '
                          'fixture no prueban equivalencia comercial. Las etiquetas son '
                          'representaciones transitorias; sin puntuación, ranking ni selección. '
                          'VIABLE no acredita viabilidad económica empresarial.</p>')
            elif suffix == "scenario-coordination":
                scenario_rows = "".join(
                    f'<li><code>{safe(item["scenario_id"])}</code>: '
                    f'ejecución {safe(item["status"])}; '
                    f'viabilidad declarada '
                    f'{safe(item["values"].get("viability_result", {}).get("status", "no informada"))}</li>'
                    for item in result["scenarios"]
                )
                value = (f'<p>Escenarios descritos: {safe(len(result["scenarios"]))}.</p>'
                         f'<ul>{scenario_rows}</ul>')
                limits = ('<p>La diferencia estructural en viability_result incluye el '
                          'identificador propio de cada escenario; por sí sola no demuestra '
                          'una diferencia de viabilidad de negocio. La coordinación no '
                          'selecciona ni prioriza un escenario.</p>')
            elif suffix == "negotiation-intelligence":
                content = result["negotiation_content"]
                value = (
                    f'<p>Objetivo ficticio: {safe(content["objective"] or "no informado")}. '
                    f'Solicitud inicial declarada: '
                    f'{safe(content["opening_request"] or "no informada")}. '
                    f'Alternativa de espera: {safe(content["fallback"] or "no informada")}.</p>'
                    f'<p>Justificaciones declaradas: {safe(len(result["justification"]))}. '
                    f'Referencias de traza: {safe(len(result["traceability_references"]))}.</p>'
                )
                limits = ('<p>AUTHORIZED pertenece al fixture sintético; no acredita '
                          'mandato empresarial ni autoriza contacto. La traza C0 vinculada '
                          'no demuestra que el texto se haya derivado causalmente de C0.</p>')
            elif suffix == "negotiation-ladder":
                steps = "".join(
                    f'<li>Posición {safe(step["position"])}: '
                    f'{safe(step["step_type"])}</li>' for step in result["steps"]
                )
                value = (f'<p>Pasos representados: {safe(len(result["steps"]))}; '
                         f'transiciones: {safe(len(result["transitions"]))}; '
                         f'rutas: {safe(len(result["routes"]))}.</p><ol>{steps}</ol>')
                limits = ('<p>La posición describe una representación, no una instrucción '
                          'para ejecutar o contactar al proveedor. Ladder reconstruye '
                          'contenido NI desde fuentes sintéticas: esto no prueba que el '
                          'invocador NI separado haya producido el mismo objeto.</p>')
            elif suffix == "c0":
                value = (
                    f'<p>Base sintética suministrada: {safe(payload["base_result"])}. '
                    f'Consolidado CRC del fixture: <strong>{safe(result["consolidated_result"])}</strong>.</p>'
                )
                limits = (
                    f'<p>QTG de esta variante: {safe(payload["qtg_status"])}. '
                    'No se ha demostrado una derivación causal de QTG hacia C0. '
                    'La base fue suministrada al fixture; el consolidado no es '
                    'una orden ni autorización de compra.</p>'
                )
            observations.append(
                f'<article><h4>{safe(title)}</h4>{value}{limits}'
                '<details class="trace"><summary>Traza de la observación</summary>'
                f'<p>Huella del fixture: <code>{safe(payload["observation_fingerprint"])}</code></p>'
                '</details></article>'
            )
        sections.append(
            f'<section><h2>{safe(variant)}</h2>'
            f'<p>Expediente ficticio: <code>{safe(terminal["reference_case_id"])}</code></p>'
            f'<p>Calidad QTG: <strong>{safe(qtg["status"])} / {safe(qtg["confidence"])}</strong>. '
            f'Ejecución técnica: {safe(terminal["execution_outcome"]["status"])}.</p>'
            f'<details><summary>Motivos de calidad de datos</summary><ul>{checks}</ul></details>'
            '<h3>Análisis disponibles</h3>'
            + ("".join(observations) or '<p>No se exportaron observaciones adicionales.</p>')
            + '<details class="trace"><summary>Trazabilidad terminal</summary>'
            + f'<p>Huella terminal: <code>{safe(terminal["terminal_fingerprint"])}</code></p>'
            + '</details></section>'
        )
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;">'
        '<title>EIOS · Demostración sintética para compras</title><style>'
        'body{font:16px/1.5 system-ui,sans-serif;max-width:68rem;margin:auto;padding:1rem;color:#14263b}'
        '.notice{position:sticky;top:0;background:#fff2c2;border:2px solid #8b6400;padding:.7rem;z-index:1}'
        'section{margin:2rem 0;padding:1rem;border:1px solid #9aa9b8;border-radius:.5rem}'
        'article{padding:.5rem 1rem;margin:.7rem 0;background:#f0f5f8}'
        '.proposal{display:grid;grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));gap:.7rem}'
        '.proposal div{padding:.6rem;background:#f0f5f8}.proposal dt{font-weight:700}.proposal dd{margin:0}'
        '.overview{background:#eaf2f8;border-color:#6d8ca7}'
        '.overview-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem}'
        '.overview-card{padding:1rem;background:white;border-left:4px solid #496d8d}'
        '.overview-card dt{font-weight:700}.overview-card dd{margin:.4rem 0 0}'
        '.trace{font-size:.9rem;color:#36495d}'
        'code{overflow-wrap:anywhere}details{margin:1rem 0}</style></head><body>'
        '<p class="notice"><strong>DEMOSTRACIÓN SINTÉTICA — NO OPERACIONAL</strong><br>'
        'SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · '
        'decision_authority=false</p><main><h1>Cómo leer el caso ficticio de compras</h1>'
        '<p>Dos variantes de la misma simulación muestran cómo se inspecciona la calidad '
        'de datos y qué análisis se han capturado. APTO solo califica la entrada de prueba; '
        'COMPLETED solo describe la ejecución técnica. Ninguno autoriza una compra.</p>'
        '<p>Los importes, el riesgo declarado, el consolidado CRC y el contenido de negociación '
        'proceden del fixture. No se ha probado una derivación causal de QTG a C0 ni una '
        'selección empresarial. AUTHORIZED en una captura negociadora no constituye mandato '
        'para contactar a proveedores. Las huellas comprueban consistencia, no autenticidad externa.</p>'
        + overview + proposal + "".join(sections) + '</main></body></html>'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists")
    html = render_buyer_preview(args.demo_dir)
    args.output.write_text(html, encoding="utf-8")
    print(f"Vista sintética de compras: {args.output}")


if __name__ == "__main__":
    main()
