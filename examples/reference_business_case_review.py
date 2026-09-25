"""Render a local, read-only comparison of two synthetic reference results."""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from eios.core.reference_simulation_execution import SCHEMA_VERSION
from eios.core.reference_price_observation import (
    validate_reference_price_observation_payload,
)
from eios.core.reference_tco_observation import (
    validate_reference_tco_observation_payload,
)
from eios.core.reference_supplier_risk_observation import (
    validate_reference_supplier_risk_observation_payload,
)
from eios.core.reference_c0_observation import validate_reference_c0_observation_payload


def _digest(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _checked(payload: dict, label: str) -> dict:
    if not isinstance(payload, dict):
        raise ValueError(f"{label}: expected terminal object")
    remainder = {key: value for key, value in payload.items() if key != "terminal_fingerprint"}
    if payload.get("terminal_fingerprint") != _digest(remainder):
        raise ValueError(f"{label}: terminal fingerprint mismatch")
    provenance = payload.get("case_provenance")
    quality = payload.get("qtg_quality_result")
    outcome = payload.get("execution_outcome")
    expected = {
        "schema_version": SCHEMA_VERSION,
        "execution_kind": "REFERENCE_OPERATIONAL_SIMULATION",
        "runtime_scope": "PRODUCT_REFERENCE_VALIDATION_ONLY",
        "operational_path": "FORBIDDEN",
        "operational_effect": False,
        "decision_authority": False,
        "qtg_execution_mode": "SYNTHETIC_TEST",
        "qtg_consumption_scope": "TEST_ONLY",
    }
    if any(payload.get(k) != v for k, v in expected.items()):
        raise ValueError(f"{label}: nonoperational terminal invariant violated")
    if not isinstance(provenance, dict) or any(provenance.get(k) != v for k, v in {
        "case_kind": "REFERENCE_OPERATIONAL_SIMULATION",
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "decision_authority": False,
    }.items()) or provenance.get("reference_case_id") != payload.get("reference_case_id"):
        raise ValueError(f"{label}: provenance invariant violated")
    if payload.get("case_provenance_fingerprint") != _digest(provenance):
        raise ValueError(f"{label}: provenance fingerprint mismatch")
    if not isinstance(quality, dict) or not isinstance(quality.get("status"), str) or not isinstance(quality.get("confidence"), str):
        raise ValueError(f"{label}: QTG result missing")
    expected_variant = {
        "negative": ("REF-BUSINESS-001", "NO_APTO", "BAJA"),
        "qtg-eligible": ("REF-BUSINESS-001-QTG-ELIGIBLE", "APTO", "ALTA"),
    }
    case_id, status, confidence = expected_variant[label]
    if (payload.get("reference_case_id"), quality["status"], quality["confidence"]) != (case_id, status, confidence):
        raise ValueError(f"{label}: case identity or QTG variant mismatch")
    checks = quality.get("checks")
    if not isinstance(checks, list) or not checks or any(
        not isinstance(check, dict)
        or not isinstance(check.get("control"), str)
        or not isinstance(check.get("reason"), str)
        or not isinstance(check.get("applicable"), bool)
        or not isinstance(check.get("critical"), bool)
        or not isinstance(check.get("material"), bool)
        or (check.get("satisfied") is not None
            and type(check.get("satisfied")) is not bool)
        or not isinstance(check.get("evidence_refs"), list)
        or any(not isinstance(ref, str) for ref in check["evidence_refs"])
        for check in checks
    ):
        raise ValueError(f"{label}: QTG checks malformed")
    if not isinstance(outcome, dict) or not isinstance(outcome.get("status"), str):
        raise ValueError(f"{label}: execution outcome missing")
    if payload.get("execution_outcome_fingerprint") != _digest(outcome):
        raise ValueError(f"{label}: execution outcome fingerprint mismatch")
    capabilities = outcome.get("capability_results")
    if not isinstance(capabilities, list) or any(not isinstance(item, dict) or
            not isinstance(item.get("capability"), str) or
            not isinstance(item.get("status"), str) or
            not isinstance(item.get("trace_references"), list) or
            any(not isinstance(ref, str) for ref in item["trace_references"])
            for item in capabilities):
        raise ValueError(f"{label}: capability result malformed")
    if payload.get("capability_sequence") != ["QTG", *(item["capability"] for item in capabilities)]:
        raise ValueError(f"{label}: capability sequence mismatch")
    return payload


def render_review(
    negative: dict, eligible: dict,
    price_observations: tuple[dict, dict] | None = None,
    tco_observations: tuple[dict, dict] | None = None,
    supplier_observations: tuple[dict, dict] | None = None,
    c0_observations: tuple[dict, dict] | None = None,
) -> str:
    """Validate terminal artifacts and produce an inert HTML comparison."""
    negative = _checked(negative, "negative")
    eligible = _checked(eligible, "qtg-eligible")
    if negative["reference_case_id"] == eligible["reference_case_id"]:
        raise ValueError("The two reference cases must have distinct identifiers")
    if price_observations is not None:
        if not isinstance(price_observations, tuple) or len(price_observations) != 2:
            raise ValueError("PRICE observations require both variants")
        for observation, terminal in zip(price_observations, (negative, eligible)):
            validate_reference_price_observation_payload(observation, terminal)
    if tco_observations is not None:
        if not isinstance(tco_observations, tuple) or len(tco_observations) != 2:
            raise ValueError("TCO observations require both variants")
        for observation, terminal in zip(tco_observations, (negative, eligible)):
            validate_reference_tco_observation_payload(observation, terminal)
    if supplier_observations is not None:
        if not isinstance(supplier_observations, tuple) or len(supplier_observations) != 2:
            raise ValueError("Supplier observations require both variants")
        for observation, terminal in zip(supplier_observations, (negative, eligible)):
            validate_reference_supplier_risk_observation_payload(observation, terminal)
    if c0_observations is not None:
        if not isinstance(c0_observations, tuple) or len(c0_observations) != 2:
            raise ValueError("C0 observations require both variants")
        for observation, terminal in zip(c0_observations, (negative, eligible)):
            validate_reference_c0_observation_payload(observation, terminal)

    def val(item: object) -> str:
        return escape(str(item), quote=True)

    def cell(payload: dict) -> str:
        quality, outcome = payload["qtg_quality_result"], payload["execution_outcome"]
        return (f'<td><strong>{val(payload["reference_case_id"])}</strong><br>'
                f'QTG: {val(quality["status"])} / {val(quality["confidence"])}<br>'
                f'Ejecución técnica: {val(outcome["status"])}<br>'
                f'Huella terminal: <code>{val(payload["terminal_fingerprint"])}</code></td>')

    def check_state(check: dict) -> str:
        if not check["applicable"]:
            return "No aplica"
        if check["satisfied"] is None:
            return "No evaluable"
        return "Satisfecho" if check["satisfied"] else "No satisfecho"

    sections = []
    for index, (name, payload) in enumerate((("Caso negativo", negative), ("Caso QTG elegible", eligible))):
        rows = []
        for item in payload["execution_outcome"]["capability_results"]:
            traces = item["trace_references"]
            refs = "<br>".join(f"<code>{val(ref)}</code>" for ref in traces) or "Sin referencias"
            rows.append(f'<tr><th scope="row">{val(item["capability"])}</th>'
                        f'<td>{val(item["status"])}</td><td>{refs}</td></tr>')
        check_rows = []
        for check in payload["qtg_quality_result"]["checks"]:
            evidence = "<br>".join(
                f"<code>{val(ref)}</code>" for ref in check["evidence_refs"]
            ) or "Sin referencias"
            check_rows.append(
                f'<tr><th scope="row"><code>{val(check["control"])}</code></th>'
                f'<td>{val(check_state(check))}</td>'
                f'<td>{"Sí" if check["critical"] else "No"}</td>'
                f'<td>{"Sí" if check["material"] else "No"}</td>'
                f'<td>{val(check["reason"])}</td><td>{evidence}</td></tr>'
            )
        price_html = ""
        if price_observations is not None:
            observation = price_observations[index]
            price = observation["price_result"]
            amount = (f'{val(price["pr_value"])} {val(price["currency"])}'
                      if price["pr_value"] is not None else "Sin valor justificable")
            limitations = ", ".join(price["pr_limitations"]) or "Sin limitaciones declaradas"
            price_html = (
                '<h3>Observación PRICE sintética</h3>'
                '<p>Precio de referencia del productor C1; no es un techo, '
                'una oferta ni una autorización de compra.</p>'
                f'<p>Valor: {amount} · Estado: {val(price["pr_status"])} '
                f'· Suficiencia: {val(price["sufficiency_status"])}</p>'
                f'<p>Limitaciones: {val(limitations)}</p>'
                f'<p>Referencias seleccionadas: {val(", ".join(price["reference_set"]) or "Ninguna")}</p>'
                f'<p>Huella de la observación: <code>{val(observation["observation_fingerprint"])}</code></p>'
            )
        tco_html = ""
        if tco_observations is not None:
            observation = tco_observations[index]
            result = observation["tco_result"]
            purchase = observation["tco_input"]["purchase_operation"]
            amount = (f'{val(result["value"])} {val(result["currency"])}'
                      if result["value"] is not None else "Importe no disponible")
            components = ", ".join(result["contributing_components"]) or "Ninguno"
            pending = ", ".join(result["unresolved_components"]) or "Ninguno"
            limitations = ", ".join(result["limitations"]) or "Sin limitaciones declaradas"
            tco_html = (
                '<h3>Observación TCO sintética</h3>'
                '<p>Coste de adquisición modelado para la compra ficticia; '
                'no representa todos los costes de propiedad de una empresa.</p>'
                f'<p>Valor: {amount} · Cantidad: {val(purchase["quantity"])} unidades '
                f'· Precio unitario de entrada: {val(purchase["unit_price"])} '
                f'{val(purchase["currency"])}</p>'
                f'<p>Componentes incluidos: {val(components)}. '
                f'Pendientes: {val(pending)}. Limitaciones: {val(limitations)}.</p>'
                '<p>El fixture no aporta costes atribuibles adicionales. '
                'No se han suministrado importes de transporte, seguros, aranceles, '
                'financiación, almacenaje, obsolescencia ni devoluciones; '
                'lo no informado no equivale a coste cero.</p>'
                '<p>Trazas TCO: sin referencias proporcionadas por el productor. '
                'Sin autoridad decisional ni efecto operacional.</p>'
                f'<p>Huella de la observación: <code>{val(observation["observation_fingerprint"])}</code></p>'
            )
        supplier_html = ""
        if supplier_observations is not None:
            observation = supplier_observations[index]
            result = observation["supplier_result"]
            inventory = observation["source_inventory"]
            declared = ", ".join(
                f'{item["dimension"]}={item["state"]}'
                for item in result["risk_dimensions"]
            ) or "Ninguna"
            inventory_text = ", ".join(
                f"{key}: {count}" for key, count in inventory.items()
            )
            supplier_html = (
                '<h3>Observación Supplier Risk/Value sintética</h3>'
                '<p>Evaluación externa sintética declarada; el estado de riesgo '
                'no se deduce de hechos de desempeño del proveedor en este fixture. '
                'No constituye recomendación ni selección de proveedor.</p>'
                f'<p>Proveedor actual: {val(result["current_supplier_id"])}. '
                f'Dimensiones Risk declaradas: {val(declared)}.</p>'
                f'<p>Inventario de fuentes factuales: {val(inventory_text)}. '
                f'Dimensiones Value: {val(len(result["value_dimensions"]))}. '
                f'Comparación Value disponible: {"Sí" if observation["value_comparison_available"] else "No"}.</p>'
                '<p>La traza identifica la evaluación declarada; no demuestra '
                'por sí sola fiabilidad factual ni autoridad decisional. '
                'Ruta operacional FORBIDDEN.</p>'
                f'<p>Huella de la observación: <code>{val(observation["observation_fingerprint"])}</code></p>'
            )
        c0_html = ""
        if c0_observations is not None:
            observation = c0_observations[index]
            result = observation["vertical_result"]
            crc = observation["crc_result"]
            assessment_rows = "".join(
                f'<tr><th scope="row">{val(item["rule_id"])}</th>'
                f'<td>{val(item["status"])}</td><td>{val(item["outcome"])}</td>'
                f'<td>{val(item["reason"])}</td></tr>'
                for item in result["assessments"]
            )
            traces = ", ".join(item["trace_id"] for item in result["traces"])
            c0_html = (
                '<h3>Observación C0/CRC sintética</h3>'
                f'<p>QTG de esta variante: {val(observation["qtg_status"])}. '
                'No está demostrada una derivación causal del resultado QTG '
                'hacia el Assessment C0. Un C0 COMPLETED no equivale a QTG APTO.</p>'
                '<table><caption>Evaluaciones individuales C0</caption><thead><tr>'
                '<th scope="col">Regla</th><th scope="col">Estado</th>'
                '<th scope="col">Resultado</th><th scope="col">Motivo</th>'
                '</tr></thead><tbody>' + assessment_rows + '</tbody></table>'
                f'<p>Base CRC suministrada al fixture: {val(observation["base_result"])}. '
                f'Consolidado CRC: {val(crc["consolidated_result"])}. '
                'Son resultados sintéticos de composición; no son una orden '
                'ni autorización de compra.</p>'
                f'<p>Motivo CRC: {val(crc["dominant_reason"])}. '
                f'Trazas C0: <code>{val(traces or "Sin referencias")}</code>.</p>'
                f'<p>Huella de la observación: <code>{val(observation["observation_fingerprint"])}</code></p>'
            )
        sections.append(f'<section><h2>{val(name)}: {val(payload["reference_case_id"])}</h2>'
                        f'<p>Secuencia: {val(" → ".join(payload["capability_sequence"]))}</p>'
                        '<div class="table-scroll"><table><caption>Controles QTG declarados</caption>'
                        '<thead><tr><th scope="col">Control</th><th scope="col">Resultado</th>'
                        '<th scope="col">Crítico</th><th scope="col">Material</th>'
                        '<th scope="col">Motivo</th><th scope="col">Evidencias</th>'
                        '</tr></thead><tbody>' + "".join(check_rows) + '</tbody></table></div>'
                        + price_html + tco_html + supplier_html + c0_html +
                        '<table><caption>Capacidades y referencias de traza</caption>'
                        '<thead><tr><th scope="col">Capacidad</th><th scope="col">Estado</th>'
                        '<th scope="col">Trazas</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
                        '<details><summary>Pendientes y motivo de fallo técnico</summary><pre>'
                        + val(json.dumps({k: payload["execution_outcome"].get(k)
                                          for k in ("unresolved_items", "failure_reason")},
                                         ensure_ascii=False, indent=2)) + '</pre></details></section>')
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;">'
            '<title>EIOS · Revisión sintética</title><style>'
            'body{font:16px/1.5 system-ui,sans-serif;max-width:72rem;margin:auto;padding:1.5rem;color:#182435}'
            'table{border-collapse:collapse;width:100%;margin:1rem 0 2rem}th,td{border:1px solid #8693a3;padding:.6rem;text-align:left;vertical-align:top}'
            '.table-scroll{overflow-x:auto}.table-scroll table{min-width:50rem}'
            'thead{background:#e9eff5}section{margin-top:2rem}code,pre{overflow-wrap:anywhere;white-space:pre-wrap}'
            'details{margin:1rem 0}summary{cursor:pointer}</style></head><body>'
            '<main><h1>Revisión de simulación de referencia</h1>'
            '<p>Material SYNTHETIC · Política QTG SYNTHETIC_TEST_ONLY · Ruta operacional FORBIDDEN '
            '· Efecto NO_OPERATIONAL_EFFECT · Autoridad decisional false.</p>'
            '<p>COMPLETED describe la ejecución técnica de la simulación; no constituye aprobación QTG '
            'ni admisión operacional. La calidad QTG se muestra por separado.</p>'
            '<table><caption>Comparación de resultados</caption><thead><tr>'
            '<th scope="col">Caso negativo</th><th scope="col">Caso QTG elegible</th>'
            '</tr></thead><tbody><tr>' + cell(negative) + cell(eligible) + '</tr></tbody></table>'
            + "".join(sections) + '</main></body></html>')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative", type=Path, required=True)
    parser.add_argument("--qtg-eligible", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--negative-price", type=Path)
    parser.add_argument("--qtg-eligible-price", type=Path)
    parser.add_argument("--negative-tco", type=Path)
    parser.add_argument("--qtg-eligible-tco", type=Path)
    parser.add_argument("--negative-supplier-risk", type=Path)
    parser.add_argument("--qtg-eligible-supplier-risk", type=Path)
    parser.add_argument("--negative-c0", type=Path)
    parser.add_argument("--qtg-eligible-c0", type=Path)
    args = parser.parse_args()
    negative = json.loads(args.negative.read_text(encoding="utf-8"))
    eligible = json.loads(args.qtg_eligible.read_text(encoding="utf-8"))
    if (args.negative_price is None) != (args.qtg_eligible_price is None):
        parser.error("Both PRICE observation files must be supplied together")
    observations = None
    if args.negative_price is not None:
        observations = (
            json.loads(args.negative_price.read_text(encoding="utf-8")),
            json.loads(args.qtg_eligible_price.read_text(encoding="utf-8")),
        )
    if (args.negative_tco is None) != (args.qtg_eligible_tco is None):
        parser.error("Both TCO observation files must be supplied together")
    tco_observations = None
    if args.negative_tco is not None:
        tco_observations = (
            json.loads(args.negative_tco.read_text(encoding="utf-8")),
            json.loads(args.qtg_eligible_tco.read_text(encoding="utf-8")),
        )
    if (args.negative_supplier_risk is None) != (args.qtg_eligible_supplier_risk is None):
        parser.error("Both supplier observation files must be supplied together")
    supplier_observations = None
    if args.negative_supplier_risk is not None:
        supplier_observations = (
            json.loads(args.negative_supplier_risk.read_text(encoding="utf-8")),
            json.loads(args.qtg_eligible_supplier_risk.read_text(encoding="utf-8")),
        )
    if (args.negative_c0 is None) != (args.qtg_eligible_c0 is None):
        parser.error("Both C0 observation files must be supplied together")
    c0_observations = None
    if args.negative_c0 is not None:
        c0_observations = (
            json.loads(args.negative_c0.read_text(encoding="utf-8")),
            json.loads(args.qtg_eligible_c0.read_text(encoding="utf-8")),
        )
    html = render_review(negative, eligible, price_observations=observations,
                         tco_observations=tco_observations,
                         supplier_observations=supplier_observations,
                         c0_observations=c0_observations)
    args.output.write_text(html, encoding="utf-8")
    print(f"Vista de revisión creada: {args.output}")


if __name__ == "__main__":
    main()
