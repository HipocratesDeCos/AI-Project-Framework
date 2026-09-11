# EIOS — R-ENT-001 · Assessment Bridge Design v0.1

**Estado:** DISEÑADO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** `main @ 9c4bdfc25fb1056cbc7114dafb48a6b06af5081d`  
**Regla:** `R-ENT-001` — Entrega posterior al riesgo de rotura

---

## 1. Propósito

Definir la unidad técnica que convierte un `DeliveryStockoutAnalysisResult` ya calculado por ENT en un `Assessment` individual compatible con C0 para `R-ENT-001`.

El bridge no recalcula STK, no recalcula ENT, no modifica la regla, no produce `NEGOCIAR`, no aplica efecto/severidad, no ejecuta CRC y no toma decisiones empresariales.

---

## 2. Autoridad preservada

La unidad consume exclusivamente autoridades ya cerradas:

- `04_Reglas/Matriz_Reglas_MVP.md` v2.1 — condición de `R-ENT-001`;
- `04_Reglas/Especificacion_Reglas_Entrega_MVP.md` v1.0 — dos dependencias EVIDENCE confirmadas;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.5 — dependencias canónicas;
- `04_Reglas/Evidence_Contract.md` v1.0 — `DEMONSTRATED/GAP` y validación;
- `08_Implementacion/Assessment_Individual_Result_Contract.md` v1.0 — contrato Assessment;
- metodología ENT v0.3 + reconciliación v0.3.1;
- `DeliveryStockoutAnalysisResult` implementado e integrado.

No se crea política empresarial nueva.

---

## 3. Propiedad del bridge

La implementación pertenece a Rules:

```text
eios/rules/delivery.py
```

No se incorpora conversión a `Assessment` dentro de `eios/delivery`.

Frontera:

```text
ENT analyzer
    ↓
DeliveryStockoutAnalysisResult
    ↓
Rules bridge R-ENT-001
    ↓
Assessment
```

---

## 4. Firma conceptual

```text
evaluate_r_ent_001(
    context: DecisionContext,
    rule: Rule,
    analysis: DeliveryStockoutAnalysisResult,
    baseline_evidence: Evidence,
    delivery_evidence: Evidence,
) -> Assessment
```

No se amplía `Assessment`.

---

## 5. Invariantes de identidad

Antes de evaluar:

1. `rule.rule_id == "R-ENT-001"`;
2. `rule.version == context.rules_version`;
3. `rule.requires_evidence == True`;
4. `analysis.decision_id == context.decision_id`;
5. `baseline_evidence.source_type == "BaselineStockoutQualification"`;
6. `delivery_evidence.source_type == "PurchaseSpecificDeliveryTimingEvidence"`.

Una incompatibilidad de contrato/identidad es error de programación/configuración y no se degrada silenciosamente a `FALSE`.

---

## 6. Vinculación de evidencia C0

### 6.1 Baseline

La evidencia C0 de baseline debe cumplir:

```text
source_type = BaselineStockoutQualification
source_ref = analysis.baseline_projection_ref
state = DEMONSTRATED | GAP
```

Si es `DEMONSTRATED`, su `demonstration_ref` debe aparecer en el conjunto reproducible de referencias publicado por ENT:

```text
analysis.evidence_refs ∪ analysis.trace_refs
```

La igualdad de `source_ref` por sí sola no convierte GAP en evidencia válida.

### 6.2 Delivery

La evidencia C0 de delivery debe cumplir:

```text
source_type = PurchaseSpecificDeliveryTimingEvidence
state = DEMONSTRATED | GAP
```

Si es `DEMONSTRATED`, su `demonstration_ref` debe aparecer en:

```text
analysis.evidence_refs ∪ analysis.trace_refs
```

No se impone catálogo universal adicional a `source_ref`; la vinculación se apoya en el rol canónico (`source_type`) y en una referencia de demostración publicada por ENT.

### 6.3 Validación

Ambas evidencias se validan mediante el mecanismo C0 vigente:

```text
DEMONSTRATED -> VALID
GAP          -> INVALID
```

El bridge no redefine `validate_evidence()`.

---

## 7. Mapeo ENT → Assessment

La regla normativa permanece:

```text
expected_delivery_date > depletion_date
```

Mapeo cerrado propuesto:

| ENT state | Assessment.status | Assessment.outcome | Condición adicional |
|---|---|---|---|
| `LATE_DELIVERY_DEMONSTRATED` | `EVALUABLE` | `TRUE` | ambas evidencias C0 VALID |
| `NOT_LATE_DEMONSTRATED` | `EVALUABLE` | `FALSE` | ambas evidencias C0 VALID |
| `NOT_LATE_WITHIN_EVIDENCED_HORIZON` | `EVALUABLE` | `FALSE` | ambas evidencias C0 VALID |
| `NOT_EVIDENCED` | `NOT_EVALUABLE` | `None` | sin conversión a FALSE |
| `CONFLICTING_DATA` | `NOT_EVALUABLE` | `None` | contradicción preservada |
| `NOT_DETERMINABLE` | `NOT_EVALUABLE` | `None` | indeterminación preservada |

Si un estado ENT concluyente recibe una o ambas evidencias C0 `INVALID`, el resultado es:

```text
NOT_EVALUABLE / None
```

Nunca `FALSE` por ausencia/GAP.

---

## 8. Justificación de NOT_LATE_WITHIN_EVIDENCED_HORIZON

La metodología ENT declara la comparación concluyente cuando `depletion_state` es `KNOWN` o `NOT_APPLICABLE`.

Para `NOT_APPLICABLE`:

```text
expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON
```

Por tanto, dentro del horizonte evidenciado la condición de `R-ENT-001` no queda demostrada y el resultado individual es `EVALUABLE / FALSE`.

No se extrapola más allá de `horizon_end`; dicho caso permanece `NOT_DETERMINABLE → NOT_EVALUABLE`.

---

## 9. evidence_ids

`Assessment.evidence_ids` contiene únicamente IDs de los objetos `Evidence` C0 recibidos por el bridge.

Orden determinista:

```text
[
  baseline_evidence.evidence_id,
  delivery_evidence.evidence_id,
]
```

No se copian como `evidence_ids`:

- `analysis.evidence_refs`;
- `analysis.trace_refs`;
- `issue_refs`;
- `baseline_projection_ref`;
- otros refs ENT.

Estos siguen siendo provenance/trace, no identidades C0 de Evidence.

---

## 10. Reason

`reason` será determinista, explicativo y no decisional.

Mensajes mínimos:

```text
TRUE  -> "R-ENT-001 demostrada: entrega posterior al agotamiento estimado."
FALSE -> "R-ENT-001 no demostrada: entrega no posterior al agotamiento estimado."
FALSE/HORIZON -> "R-ENT-001 no demostrada dentro del horizonte STK evidenciado."
NOT_EVALUABLE -> razón factual según estado ENT o insuficiencia de evidencia C0.
```

`reason` no contiene `NEGOCIAR`, recomendación, severidad, efecto, CRC ni decisión.

---

## 11. RDM

Este bridge consume las dos dependencias ya `CONFIRMED`:

```text
DEP-ENT-BSQ-RENT-001
DEP-ENT-DTE-RENT-001
```

No modifica:

- `Criticality = PENDING`;
- `Evaluability_Impact = PENDING`;
- `Fallback = NONE`;
- `Affected_Component = NONE`.

No se crea un tercer registro RDM.

---

## 12. Tests mínimos obligatorios

1. late + 2 VALID → `EVALUABLE/TRUE`;
2. before + 2 VALID → `EVALUABLE/FALSE`;
3. same-day ENT result + 2 VALID → `EVALUABLE/FALSE`;
4. within evidenced horizon + 2 VALID → `EVALUABLE/FALSE`;
5. `NOT_EVIDENCED` → `NOT_EVALUABLE/None`;
6. `CONFLICTING_DATA` → `NOT_EVALUABLE/None`;
7. `NOT_DETERMINABLE` → `NOT_EVALUABLE/None`;
8. concluyente + baseline GAP → `NOT_EVALUABLE`;
9. concluyente + delivery GAP → `NOT_EVALUABLE`;
10. source_type incorrecto → rechazo;
11. demonstration_ref no vinculado a ENT → rechazo;
12. rule_id incorrecto → rechazo;
13. rules_version incompatible → rechazo;
14. decision_id incompatible → rechazo;
15. Assessment no expone recomendación/efecto/severidad/CRC.

---

## 13. Alcance físico previsto

Solo tras Audit 1 + depuración + Audit 2 limpio:

```text
eios/rules/delivery.py
tests/test_r_ent_001_assessment_bridge.py
```

Opcionalmente `eios/rules/__init__.py` únicamente para exportar la función si la auditoría lo considera necesario.

No se modifica:

```text
eios/core/*
eios/delivery/*
eios/stock/*
eios/supplier/*
04_Reglas/Rule_Dependency_Matrix.md
04_Reglas/Matriz_Reglas_MVP.md
```

---

## 14. Estado

**DISEÑO v0.1 COMPLETADO.**  
**Implementación:** NO AUTORIZADA hasta Audit 1 → depuración → Audit 2 final → cierre.  
**Política empresarial nueva:** 0.
