"""Static comparison of two verified synthetic EIOS packages."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path

from .reference_business_case_demo import verify_reference_demo
from .reference_business_case_002 import verify_reference_business_case_002


def render_comparison(case_001_dir: Path, case_002_dir: Path) -> str:
    """Replay both packages and render only fixed, descriptive facts."""
    case_001_dir, case_002_dir = Path(case_001_dir), Path(case_002_dir)
    verify_reference_demo(case_001_dir)
    verify_reference_business_case_002(case_002_dir)
    supplier_001 = case_001_dir / "reference-supplier-risk.json"
    if not supplier_001.is_file():
        raise ValueError("Case 001 comparison requires both supplier-risk observations")

    def read(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    first = read(case_001_dir / "reference-result.json")
    second = read(case_002_dir / "reference-result.json")
    first_risk = read(supplier_001)["supplier_result"]["risk_dimensions"][0]["state"]
    second_risk = read(case_002_dir / "reference-supplier-risk.json")["supplier_result"]["risk_dimensions"][0]["state"]
    if (first["reference_case_id"], second["reference_case_id"], first_risk, second_risk) != (
        "REF-BUSINESS-001-QTG-ELIGIBLE", "REF-BUSINESS-002", "FAVORABLE", "NOT_DETERMINABLE"
    ):
        raise ValueError("Comparison requires the fixed eligible 001 and partial 002 cases")

    def safe(value: object) -> str:
        return escape(str(value), quote=True)

    def case(label: str, data: dict, reliability: str, summary: str) -> str:
        purchase = data["purchase"]
        status = {"COMPLETED": "Completada", "PARTIALLY_COMPLETED": "Completada parcialmente"}[
            data["execution_outcome"]["status"]
        ]
        return f'''<article class="case"><div class="eyebrow">{safe(label)}</div>
<h2>{safe(status)}</h2><p>{safe(summary)}</p>
<dl><div><dt>Calidad de la entrada</dt><dd>{safe(data['qtg_quality_result']['status'])} / {safe(data['qtg_quality_result']['confidence'])}</dd></div>
<div><dt>Fiabilidad del proveedor</dt><dd>{safe(reliability)}</dd></div>
<div><dt>Compra ficticia</dt><dd>{safe(purchase['quantity'])} unidades × {safe(purchase['unit_price'])} {safe(purchase['currency'])}</dd></div></dl>
<p class="ref">Expediente {safe(data['reference_case_id'])}<br>Huella del resultado: <code>{safe(data['terminal_fingerprint'])}</code></p></article>'''

    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comparación de simulaciones · EIOS</title>
<style>
:root{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#17364b;background:#f2f7f9}}
*{{box-sizing:border-box}}body{{margin:0;line-height:1.55}}main{{max-width:1040px;margin:auto;padding:2rem 1.25rem 4rem}}
header{{background:#12364d;color:white;border-radius:22px;padding:2rem}}header p{{color:#d9e9ee;max-width:70ch}}
h1{{font-size:clamp(2rem,4vw,3rem);line-height:1.15;margin:.4rem 0}}h2{{margin:.35rem 0;font-size:1.5rem}}
.eyebrow{{font-size:.8rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase;color:#18717a}}
header .eyebrow{{color:#a7dee0}}.notice{{background:#fff4df;border-left:5px solid #d99a28;border-radius:10px;padding:1rem 1.25rem;margin:1.25rem 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:1rem}}
.case{{background:white;border:1px solid #d6e4e9;border-radius:18px;padding:1.5rem;box-shadow:0 5px 18px #12364d0c}}
.case p{{max-width:64ch}}dl{{margin:1.3rem 0}}dl div{{padding:.7rem 0;border-top:1px solid #e4ecef}}
dt{{font-size:.85rem;color:#466271}}dd{{margin:.2rem 0 0;font-weight:750;font-size:1.1rem}}
.ref{{font-size:.8rem;color:#496372;overflow-wrap:anywhere}}.explain{{background:#e5f2f0;border-radius:15px;padding:1.2rem 1.5rem;margin-top:1.25rem}}
footer{{font-size:.85rem;color:#486473;margin-top:2rem}}
</style></head><body><main><header><div class="eyebrow">EIOS · comparación de pruebas</div>
<h1>Dos empresas ficticias, dos resultados distintos</h1>
<p>Esta vista reúne hechos de paquetes sintéticos verificados por repetición exacta. Compara la variante apta del caso 001 con el caso 002; el caso negativo 001 no interviene en estas columnas.</p></header>
<div class="notice"><strong>Ninguna compra está autorizada.</strong> Ambas simulaciones tienen la ruta operacional prohibida, carecen de efecto operacional y no conceden autoridad decisional.</div>
<section class="grid" aria-label="Resultados de los dos casos">
{case('Caso 001 · variante apta', first, 'Favorable en la prueba', 'Todas las capacidades terminaron; el juicio sobre el proveedor pertenece únicamente al material ficticio 001.')}
{case('Caso 002', second, 'No determinable', 'Las capacidades se ejecutaron, pero faltan hechos para valorar la fiabilidad del proveedor.')}
</section><section class="explain"><h2>Cómo leer la diferencia</h2>
<p>«Completada» describe la ejecución técnica del caso 001; no equivale a aprobar una compra. «Completada parcialmente» señala que el caso 002 conserva una cuestión sin resolver. La calidad de entrada APTO / ALTA tampoco resuelve por sí sola la fiabilidad del proveedor.</p>
<p>Las cantidades y precios pertenecen a empresas ficticias diferentes. Su presencia permite reconocer los expedientes, no ordenar proveedores ni establecer cuál conviene comprar.</p></section>
<footer>Vista local de solo lectura · Material sintético · Sin efecto operacional · Sin autoridad decisional</footer>
</main></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-001-dir", type=Path, required=True)
    parser.add_argument("--case-002-dir", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    args = parser.parse_args()
    html = render_comparison(args.case_001_dir, args.case_002_dir)
    if args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != html:
            raise ValueError("Comparison HTML differs from exact package replay")
        print("Comparación verificada; ambas rutas operacionales prohibidas.")
    else:
        with args.output.open("x", encoding="utf-8") as target:
            target.write(html)
        print(f"Comparación sintética creada: {args.output}")


if __name__ == "__main__":
    main()
