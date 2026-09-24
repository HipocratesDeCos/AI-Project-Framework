"""Render a local, read-only comparison of two synthetic reference results."""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from eios.core.reference_simulation_execution import SCHEMA_VERSION


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


def render_review(negative: dict, eligible: dict) -> str:
    """Validate terminal artifacts and produce an inert HTML comparison."""
    negative = _checked(negative, "negative")
    eligible = _checked(eligible, "qtg-eligible")
    if negative["reference_case_id"] == eligible["reference_case_id"]:
        raise ValueError("The two reference cases must have distinct identifiers")

    def val(item: object) -> str:
        return escape(str(item), quote=True)

    def cell(payload: dict) -> str:
        quality, outcome = payload["qtg_quality_result"], payload["execution_outcome"]
        return (f'<td><strong>{val(payload["reference_case_id"])}</strong><br>'
                f'QTG: {val(quality["status"])} / {val(quality["confidence"])}<br>'
                f'Ejecución técnica: {val(outcome["status"])}<br>'
                f'Huella terminal: <code>{val(payload["terminal_fingerprint"])}</code></td>')

    sections = []
    for name, payload in (("Caso negativo", negative), ("Caso QTG elegible", eligible)):
        rows = []
        for item in payload["execution_outcome"]["capability_results"]:
            traces = item["trace_references"]
            refs = "<br>".join(f"<code>{val(ref)}</code>" for ref in traces) or "Sin referencias"
            rows.append(f'<tr><th scope="row">{val(item["capability"])}</th>'
                        f'<td>{val(item["status"])}</td><td>{refs}</td></tr>')
        checks = payload["qtg_quality_result"].get("checks", [])
        sections.append(f'<section><h2>{val(name)}: {val(payload["reference_case_id"])}</h2>'
                        f'<p>Secuencia: {val(" → ".join(payload["capability_sequence"]))}</p>'
                        '<table><caption>Capacidades y referencias de traza</caption>'
                        '<thead><tr><th scope="col">Capacidad</th><th scope="col">Estado</th>'
                        '<th scope="col">Trazas</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
                        '<details><summary>Resultado QTG completo</summary><pre>'
                        + val(json.dumps(checks, ensure_ascii=False, indent=2)) + '</pre></details>'
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
    args = parser.parse_args()
    negative = json.loads(args.negative.read_text(encoding="utf-8"))
    eligible = json.loads(args.qtg_eligible.read_text(encoding="utf-8"))
    html = render_review(negative, eligible)
    args.output.write_text(html, encoding="utf-8")
    print(f"Vista de revisión creada: {args.output}")


if __name__ == "__main__":
    main()
