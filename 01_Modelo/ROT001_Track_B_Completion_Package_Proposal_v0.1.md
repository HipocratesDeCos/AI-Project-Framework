# EIOS — ROT001 Track B Completion Package Proposal v0.1

**Baseline:** `main @ 5bc4031ae9d201804206abdd2b8e1c39c4fa8975`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA CONSOLIDADA — NO AUTORIZADA / NO VIGENTE  
**Regla:** `R-ROT-001 — Producto de baja rotación`

---

## 1. Objetivo

Cerrar en una única autoridad ejecutable los gaps:

```text
ROT-G02 → definición de rotation_metric
ROT-G03 → umbral de baja rotación
ROT-G04 → dependencias DATA / PARAMETER / EVIDENCE
```

sin reutilizar `P-ROT-001`, sin introducir stock/consumo/demanda como proxies y sin inferir una fórmula estándar de inventario.

---

## 2. Decisión metodológica propuesta para el MVP

Para el MVP se propone definir `rotation_metric` como **frecuencia de eventos de venta válidos por día**:

```text
rotation_metric =
valid_sale_event_count / rotation_window_days
```

Unidad canónica:

```text
eventos/día
```

Esta métrica:

- mide actividad comercial del artículo;
- usa únicamente eventos ya calificados como ventas válidas upstream;
- no usa cantidad vendida;
- no usa importe;
- no usa stock medio;
- no usa COGS;
- no usa consumo;
- no usa demanda;
- no pretende ser inventory turnover financiero estándar.

Se adopta deliberadamente como métrica operativa MVP acotada a Rules.

---

## 3. Parámetro P-ROT-002 propuesto

```text
P-ROT-002
Nombre: Periodo de cálculo de rotación
Unidad: días
Tipo: entero positivo
Condición: period_days >= 1
Default: ninguno
```

Semántica temporal:

```text
evaluation_date = PurchaseOperation.operation_date
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 days)
```

Ventana inclusiva.

`P-ROT-002` gobierna exclusivamente `R-ROT-001`.

No reutiliza `P-ROT-001`.

---

## 4. Parámetro P-ROT-003 propuesto

```text
P-ROT-003
Nombre: Umbral mínimo de frecuencia de ventas
Unidad: eventos/día
Tipo: decimal finito positivo
Condición: threshold > 0
Default: ninguno
```

Condición Rule:

```text
rotation_metric < threshold
→ R-ROT-001 TRUE
```

Igualdad:

```text
rotation_metric == threshold
→ FALSE
```

No se aplica tolerancia implícita.

---

## 5. Fuente factual

Se propone un carrier específico:

```text
RotationMetricSourceEvidence
├── article_id
├── window_start
├── window_end
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── valid_sale_evidence_refs
├── trace_refs
└── coverage_state
```

`coverage_state` reutiliza la taxonomía ya autorizada en ROT002:

```text
COMPLETE
PARTIAL
NOT_DEMONSTRATED
CONFLICTING
```

La reutilización es taxonómica, no de autoridad temporal.

---

## 6. Regla de completitud

Para calcular un `rotation_metric` evaluable se exige:

```text
coverage_state == COMPLETE
+
source_semantics_ref demostrado
+
completeness_ref demostrado
+
todos los valid_sale_evidence_refs DEMONSTRATED
+
ventana exacta P-ROT-002
```

Cualquier cobertura parcial o contradictoria:

```text
→ NOT_EVALUABLE
```

No se extrapola una frecuencia desde una ventana parcial.

---

## 7. Conteo de eventos

```text
valid_sale_event_count =
len(valid_sale_evidence_refs únicos y demostrados)
```

No se suman cantidades.

No existe netting.

Un evento posteriormente revertido solo puede aparecer o no aparecer en `valid_sale_evidence_refs` según la autoridad upstream `source_semantics_ref`; ROT no recalifica el evento.

---

## 8. Carrier derivado

Se propone:

```text
RotationMetricEvidence
├── article_id
├── evaluation_date
├── window_start
├── window_end
├── window_authority_ref
├── threshold_authority_ref
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── valid_sale_event_count
├── rotation_metric
├── metric_unit
├── evidence_refs
└── trace_refs
```

Invariantes:

```text
metric_unit = "eventos/día"
rotation_metric >= 0
valid_sale_event_count >= 0
```

La métrica se deriva determinísticamente; no se suministra desprendida.

---

## 9. Precision

La división se ejecuta con `Decimal`.

No se redondea antes de comparar con `P-ROT-003`.

La representación puede cuantizarse solo para presentación, nunca para decisión.

---

## 10. Bridge R-ROT-001

Inputs:

```text
DecisionInputPackage
+
RotationMetricSourceEvidence
```

El bridge reconstruye internamente:

- `P-ROT-002`;
- `P-ROT-003`;
- ventana;
- `RotationMetricEvidence`;
- comparación.

Mapping:

```text
metric < threshold
→ EVALUABLE / TRUE

metric >= threshold
→ EVALUABLE / FALSE

missing/invalid config
→ NOT_EVALUABLE

partial/conflicting/not demonstrated source
→ NOT_EVALUABLE
```

No se acepta `rotation_metric` desprendido.

---

## 11. Metadata Rule / CRC propuesta

La Matriz establece:

```text
R-ROT-001
Efecto = R2
Severidad = ALTA
Resultado = NEGOCIAR o NO COMPRAR
```

Para el MVP se propone fijar:

```text
effect = R2
severity = ALTA
active_result = NEGOCIAR
```

Motivo:

- R2 ya representa negociación;
- no existe autoridad documental que determine cuándo la baja rotación debe convertirse automáticamente en `NO COMPRAR`;
- no se eleva una ambigüedad documental a bloqueo automático.

`NO COMPRAR` queda reservado a una futura política específica.

---

## 12. No escalada automática

Esta autoridad no permite:

```text
R2 → R1
R2 → R0
NEGOCIAR → NO COMPRAR
```

sin política posterior explícita.

---

## 13. RDM propuesta

Tras autorización:

```text
R-ROT-001 ← P-ROT-002
R-ROT-001 ← P-ROT-003
R-ROT-001 ← RotationMetricSourceEvidence
R-ROT-001 ← RotationMetricEvidence
R-ROT-001 ← Evidence
```

No se incorpora dependencia directa a:

- STK;
- PYE;
- stock;
- demanda;
- consumo;
- PRICE;
- Finance.

---

## 14. Orchestrator

Se propone bundle:

```text
RotationMetricRuleInputs
└── source: RotationMetricSourceEvidence
```

El bundle se suministra opcionalmente a `run_domain_rules(...)`.

Si no existe:

```text
R-ROT-001 → omitted_rule_ids
```

No se crea un Assessment incompleto.

---

## 15. Tests consolidados

La materialización deberá verificar al menos:

1. ventana P-ROT-002 exacta;
2. P-ROT-001 no se reutiliza;
3. P-ROT-002 missing/invalid → NOT_EVALUABLE;
4. P-ROT-003 missing/invalid → NOT_EVALUABLE;
5. fuente COMPLETE;
6. PARTIAL → NOT_EVALUABLE;
7. NOT_DEMONSTRATED → NOT_EVALUABLE;
8. CONFLICTING → NOT_EVALUABLE;
9. event refs duplicados rechazados;
10. GAP no cuenta como evento;
11. conteo = número de eventos válidos;
12. Decimal sin redondeo decisional;
13. metric < threshold → TRUE;
14. metric == threshold → FALSE;
15. metric > threshold → FALSE;
16. zero events + COMPLETE produce metric 0;
17. no quantity/netting;
18. metadata R2/ALTA/NEGOCIAR;
19. orchestrator;
20. CRC conserva NEGOCIAR;
21. ausencia del bundle → omitted;
22. no R0/R1 automático.

---

## 16. No alcance

No autoriza:

- inventory turnover financiero;
- COGS / average inventory;
- unidades vendidas/día;
- importe vendido/día;
- stock turns;
- cobertura;
- demanda;
- consumo;
- ranking/scoring;
- adaptación ERP concreta;
- política automática `NO COMPRAR`;
- modificación de `R-ROT-002`.

---

## 17. Efecto de una autorización única

Si se autoriza este paquete:

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR:
   - P-ROT-002 / P-ROT-003 authority
   - RotationMetricSourceEvidence
   - RotationMetricEvidence
   - producer/evaluator provenance-safe
   - R-ROT-001 catalog metadata
   - orchestrator
   - RDM/parameter matrix
   - tests
→ CI
→ merge
→ CI main
```

No se requerirán micro-autorizaciones adicionales dentro de este alcance.

---

## 18. Estado

**ROT001 TRACK B COMPLETION PACKAGE v0.1 — PROPUESTA / NO VIGENTE.**
