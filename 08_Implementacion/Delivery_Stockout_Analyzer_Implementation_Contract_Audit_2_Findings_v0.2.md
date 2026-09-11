# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION CONTRACT AUDIT 2 FINDINGS v0.2

**Estado:** AUDIT 2 — HALLAZGOS A DEPURAR  
**Fecha:** 11/09/2026  
**Contrato auditado:** `Delivery_Stockout_Analyzer_Implementation_Contract_v0.2.md`

---

## 1. Dictamen

v0.2 corrige completamente Audit 1, pero Audit 2 identifica tres puntos de representabilidad antes del cierre.

```text
ENT-TC-A2-01  BLOCKER
ENT-TC-A2-02  HIGH
ENT-TC-A2-03  MEDIUM
```

No se identifica política empresarial nueva pendiente.

---

## 2. ENT-TC-A2-01 — Mismatch entre dependencias no puede convertirse en excepción general

### Evidencia metodológica

ENT v0.3 establece como precondiciones compatibles:

- `decision_id`;
- `article_id`;
- `evaluated_purchase_trace_ref`;
- provenance.

Y fija:

```text
si falla una precondición de identidad/provenance
→ NOT_DETERMINABLE
```

### Defecto v0.2

El contrato convierte cualquier incompatibilidad entre baseline y delivery en error de validación.

Esto impediría producir el estado factual autorizado `NOT_DETERMINABLE` ante dependencias válidas por separado pero incompatibles entre sí.

### Distinción necesaria

Debe separarse:

**A. Objeto internamente malformado**

Ejemplo:

```text
baseline.decision_id != baseline.projection.identity.decision_id
```

→ error de validación del modelo.

**B. Dos dependencias válidas pero incompatibles entre sí**

Ejemplo:

```text
baseline.decision_id != delivery.decision_id
```

→ `DeliveryStockoutAnalysisResult.state = NOT_DETERMINABLE`.

Lo mismo aplica a artículo, evaluation_date y evaluated_purchase_ref.

**Severidad:** BLOCKER.

---

## 3. ENT-TC-A2-02 — `NOT_EVIDENCED` no debe destruir el valor declarado

### Autoridad

STK-M09 define:

```text
NOT_EVIDENCED = existe un valor declarado,
pero carece de evidencia suficiente.
```

### Defecto v0.2

El contrato obliga:

```text
delivery.state = NOT_EVIDENCED
→ expected_delivery_date = None
```

Esto puede perder el valor declarado y reducir trazabilidad.

### Corrección requerida

Permitir que `PurchaseSpecificDeliveryTimingEvidence.expected_delivery_date` exista en estado `NOT_EVIDENCED` cuando haya sido declarado, pero:

- nunca usarlo en la comparación;
- nunca promoverlo a KNOWN;
- conservar estado `NOT_EVIDENCED` en el resultado;
- conservar fuente/evidence refs disponibles;
- no exigir que exista fecha: `NOT_EVIDENCED` también puede representar ausencia de evidencia suficiente sin valor utilizable.

Para `CONFLICTING_DATA`, no se publicará una fecha única como si fuera resuelta.

**Severidad:** HIGH.

---

## 4. ENT-TC-A2-03 — Adaptación de `DataIssueRef` STK no especificada

### Evidencia física

`StockProjectionResult.issue_refs` contiene objetos `eios.stock.models.DataIssueRef`.

El resultado ENT propuesto declara:

```text
issue_refs: tuple[str, ...]
```

### Riesgo

Una mezcla directa de ambos tipos rompería el contrato físico o induciría una serialización arbitraria.

### Corrección requerida

Cerrar una transformación exclusivamente referencial:

```text
STK DataIssueRef.issue_record_ref
→ ENT issue_refs[]
```

El analizador puede conservar también `issue_id` únicamente si se declara un campo separado; no debe concatenar/serializar objetos completos ni reinterpretar el tipo de issue.

Para mantener mínima la implementación, se recomienda usar solo `issue_record_ref` como referencia estable y conservar `projection.trace_refs` por separado.

**Severidad:** MEDIUM.

---

## 5. Puntos de Audit 2 superados

Quedan limpios:

1. separación baseline/delivery states;
2. reconciliación `depletion NOT_EVIDENCED → NOT_DETERMINABLE`;
3. restitución de fecha pasada;
4. `evaluation_date` restaurada;
5. `valid_from/valid_to` preservados;
6. `evidence_refs` plural;
7. `baseline_projection_ref` explícita;
8. no inferencia desde `scenario_id`;
9. no Supplier adapter automático;
10. no lead-time derivation;
11. no Assessment/CRC/NEGOCIAR;
12. no SQL/persistencia;
13. horizonte limitado correctamente;
14. mismo día sin orden intradía inventado;
15. provenance baseline obligatoria;
16. exclusión de compra obligatoria;
17. `evaluated_purchase_ref` no convertido en identidad global.

---

## 6. Corrección autorizada

Procede una v0.3 exclusivamente para:

```text
A2-01 separar malformed input de incompatible dependencies
A2-02 preservar declared date en NOT_EVIDENCED sin usarla
A2-03 explicitar DataIssueRef.issue_record_ref → ENT issue_refs
```

Después: Audit 2 final.

---

## 7. Estado

```text
AUDIT 2 FINDINGS       MATERIALIZADOS
BLOQUEADORES           1
HIGH                    1
MEDIUM                  1
CÓDIGO                  NO AUTORIZADO
```
