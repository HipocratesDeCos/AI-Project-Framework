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
                value = f'<p>Proveedor ficticio: <code>{safe(result["current_supplier_id"])}</code>. '
                value += 'Riesgo declarado; sin prueba factual de desempeño del proveedor.</p>'
            elif suffix == "decision-twin":
                value = f'<p>Representaciones comparadas: {safe(", ".join(result["alternatives"]))}. '
                value += 'Sin puntuación, ranking ni selección.</p>'
            elif suffix == "scenario-coordination":
                value = f'<p>Escenarios descritos: {safe(len(result["scenarios"]))}. '
                value += 'La coordinación no selecciona un escenario.</p>'
            elif suffix == "negotiation-intelligence":
                value = f'<p>Objetivo ficticio: {safe(result["negotiation_content"]["objective"] or "no informado")}. '
                value += 'No demuestra mandato empresarial.</p>'
            elif suffix == "negotiation-ladder":
                value = f'<p>Pasos representados: {safe(len(result["steps"]))}. '
                value += 'Su orden no instruye a ejecutarlos.</p>'
            elif suffix == "c0":
                limits = '<p>Consolidado sintético: no es una orden ni autorización de compra.</p>'
            observations.append(
                f'<article><h4>{safe(title)}</h4>{value}{limits}'
                f'<p>Observación del fixture; <code>{safe(payload["observation_fingerprint"])}</code></p></article>'
            )
        sections.append(
            f'<section><h2>{safe(variant)}</h2>'
            f'<p>Expediente ficticio: <code>{safe(terminal["reference_case_id"])}</code></p>'
            f'<p>Calidad QTG: <strong>{safe(qtg["status"])} / {safe(qtg["confidence"])}</strong>. '
            f'Ejecución técnica: {safe(terminal["execution_outcome"]["status"])}.</p>'
            f'<details><summary>Motivos de calidad de datos</summary><ul>{checks}</ul></details>'
            '<h3>Análisis disponibles</h3>'
            + ("".join(observations) or '<p>No se exportaron observaciones adicionales.</p>')
            + f'<p>Huella terminal: <code>{safe(terminal["terminal_fingerprint"])}</code></p></section>'
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
        + proposal + "".join(sections) + '</main></body></html>'
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
