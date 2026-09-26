"""Read-only, replay-backed HTML review of the synthetic case 002 package."""
from __future__ import annotations

from html import escape


def render_case_002_review(terminal: dict, sidecars: dict[str, dict]) -> str:
    """Render only the exact validated synthetic case, with no active content."""
    from .reference_business_case_002 import CASE_ID, OBSERVATIONS

    if terminal.get("reference_case_id") != CASE_ID or set(sidecars) != set(OBSERVATIONS):
        raise ValueError("Case 002 review requires its complete terminal and observations")
    if terminal.get("execution_outcome", {}).get("status") != "PARTIALLY_COMPLETED" or \
            terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("Case 002 review requires the synthetic partial terminal")
    for name, (_, validate, _) in OBSERVATIONS.items():
        validate(sidecars[name], terminal)

    def safe(value: object) -> str:
        return escape(str(value), quote=True)

    purchase = terminal["purchase"]
    qtg = terminal["qtg_quality_result"]
    outcome = terminal["execution_outcome"]
    price = sidecars["price"]["price_result"]
    tco = sidecars["tco"]["tco_result"]
    supplier = sidecars["supplier-risk"]["supplier_result"]
    c0 = sidecars["c0"]["crc_result"]
    twin = sidecars["decision-twin"]["comparison"]
    scenarios = sidecars["scenario-coordination"]["support"]["scenarios"]
    ni = sidecars["negotiation-intelligence"]["ni_result"]["negotiation_content"]
    ladder = sidecars["negotiation-ladder"]["ladder_result"]["steps"]
    if c0["consolidated_result"] != "INFORMACIÓN INSUFICIENTE" or \
            supplier["risk_dimensions"][0]["state"] != "NOT_DETERMINABLE" or \
            sidecars["decision-twin"]["selected_alternative"] is not None:
        raise ValueError("Case 002 review cannot hide unresolved material")

    def card(title: str, value: object, explanation: str, tone: str = "") -> str:
        return (f'<article class="card {tone}"><h3>{safe(title)}</h3>'
                f'<p class="value">{safe(value)}</p><p>{safe(explanation)}</p></article>')

    cards = "".join((
        card("Calidad de la entrada", f'{qtg["status"]} / {qtg["confidence"]}',
             "La proyección ficticia supera sus controles de calidad. No autoriza una compra."),
        card("Estado de la ejecución", "Completada parcialmente",
             "Las capacidades se ejecutaron, pero la fiabilidad del proveedor sigue sin determinarse.",
             "attention"),
        card("Resultado C0", c0["consolidated_result"],
             "Falta vincular formalmente un requisito de evidencia. C0 no concede autoridad decisional.",
             "attention"),
    ))
    risk = supplier["risk_dimensions"][0]
    results = "".join((
        card("Precio de referencia", f'{price["pr_value"]} {price["currency"]}',
             "Mediana de dos precios ficticios declarados; no es un techo ni una oferta."),
        card("Coste modelado", f'{tco["value"]} {tco["currency"]}',
             "Incluye la adquisición. No se aportaron costes adicionales; no equivale al coste total empresarial."),
        card("Fiabilidad del proveedor", "No determinable",
             "No hay historial, métricas ni señales factuales en este expediente. No se compara su valor.",
             "attention"),
        card("Escenarios", f'{len(scenarios)} alternativas',
             "Compras simuladas de 16 y 17 unidades, cada una con su propia traza C0."),
        card("Decision Twin", f'{len(twin["alternatives"])} comparadas',
             "Compara estructura; no recomienda ni selecciona una alternativa."),
        card("Negociación", f'{len(ladder)} pasos',
             "Solicitud sintética de información, organizada como objetivo, petición y espera."),
    ))
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisión sintética · Caso 002</title>
<style>
:root{{color-scheme:light;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#19324b;background:#f3f7fa}}
*{{box-sizing:border-box}}body{{margin:0;line-height:1.55}}main{{max-width:1100px;margin:auto;padding:2rem 1.25rem 4rem}}
h1{{font-size:clamp(2rem,4vw,3.4rem);line-height:1.12;margin:.6rem 0}}h2{{margin:2.2rem 0 .5rem;font-size:1.55rem}}
p{{max-width:72ch}}.eyebrow{{font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:#156c75;font-size:.76rem}}
.hero{{background:#102f46;color:#fff;border-radius:24px;padding:clamp(1.5rem,4vw,3rem)}}.hero p{{color:#dbe8ed}}
.banner{{margin-top:1.2rem;padding:1rem 1.2rem;border-left:5px solid #e3a22f;background:#fff7e5;color:#50391a;border-radius:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin-top:1rem}}
.card{{background:#fff;border:1px solid #dbe6ec;border-radius:16px;padding:1.2rem;box-shadow:0 4px 16px #17354a0d}}
.card.attention{{border-top:4px solid #e3a22f}}.card h3{{font-size:.85rem;color:#3b6170;margin:0 0 .7rem}}
.card .value{{font-size:1.3rem;font-weight:750;color:#153b52;overflow-wrap:anywhere;margin:0 0 .4rem}}
.card p:last-child{{font-size:.91rem;color:#475d6a;margin:0}}
dl{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem}}
dl div{{background:#eaf2f5;border-radius:12px;padding:.85rem}}dt{{font-size:.77rem;color:#43616f}}dd{{margin:.2rem 0 0;font-weight:700;overflow-wrap:anywhere}}
.note{{background:#e9f4f2;border-radius:16px;padding:1.2rem 1.4rem;margin-top:2rem}}
code{{font-size:.85em}}footer{{margin-top:2.5rem;font-size:.82rem;color:#526a77;overflow-wrap:anywhere}}
</style></head><body><main>
<header class="hero"><span class="eyebrow">EIOS · Empresa ficticia 002</span><h1>Revisión de simulación de referencia</h1>
<p>Una lectura guiada de la compra simulada y de sus ocho capacidades. Todos los datos son sintéticos.</p></header>
<div class="banner"><strong>Sin decisión de compra.</strong> La ruta operacional está prohibida y el resultado técnico es parcial. Se necesita evidencia adicional y revisión humana.</div>
<section aria-labelledby="summary"><h2 id="summary">Lo esencial</h2><div class="grid">{cards}</div></section>
<section aria-labelledby="proposal"><h2 id="proposal">Propuesta ficticia</h2>
<p>Estos datos son la entrada del ensayo; no son una orden.</p><dl>
<div><dt>Artículo</dt><dd>{safe(purchase['article_id'])}</dd></div>
<div><dt>Proveedor</dt><dd>{safe(purchase['supplier_id'])}</dd></div>
<div><dt>Cantidad</dt><dd>{safe(purchase['quantity'])} unidades</dd></div>
<div><dt>Precio unitario</dt><dd>{safe(purchase['unit_price'])} {safe(purchase['currency'])}</dd></div>
</dl></section>
<section aria-labelledby="results"><h2 id="results">Qué aportó cada análisis</h2><p>Los importes y las etiquetas describen el material suministrado a esta prueba.</p>
<div class="grid">{results}</div></section>
<aside class="note"><h2>Qué queda pendiente</h2><p>La calidad QTG es apta para la simulación, pero el requisito C0 sigue indeterminado; no se ha demostrado el vínculo entre ambos. Tampoco hay hechos suficientes para valorar la fiabilidad del proveedor.</p>
<p>El contenido NI propone pedir información: {safe(ni['opening_request'])}. Su autoridad declarada solo existe dentro del ensayo y no permite contactar a un proveedor.</p></aside>
<footer>Expediente {safe(terminal['reference_case_id'])} · Fingerprint del terminal: <code>{safe(terminal['terminal_fingerprint'])}</code><br>
SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false<br>
Vista local de solo lectura, vinculada al paquete JSON verificado.</footer>
</main></body></html>
"""
