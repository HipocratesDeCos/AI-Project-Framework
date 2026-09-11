# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION CONTRACT AUDIT 1 v0.1

**Estado:** AUDIT 1 COMPLETADA — HALLAZGOS BLOQUEANTES  
**Fecha:** 11/09/2026  
**Contrato auditado:** `08_Implementacion/Delivery_Stockout_Analyzer_Implementation_Contract_v0.1.md`

---

## 1. Alcance

Auditar el contrato técnico ENT v0.1 contra:

- metodología ENT v0.3 cerrada;
- cierre metodológico v0.3;
- especificación R-ENT-001 v1.0;
- RDM v1.5;
- `StockProjectionResult` físico;
- `calculate_stock_projection()` físico;
- Supplier Evidence Core;
- Assessment/C0.

No se audita todavía código ENT porque no existe ni está autorizado.

---

## 2. Resultado ejecutivo

**DICTAMEN: NO APTO PARA CIERRE.**

El diseño mantiene correctamente la frontera factual, pero contiene gaps de representabilidad que deben depurarse antes de Audit 2.

Hallazgos:

```text
ENT-TC-A1-01  BLOCKER
ENT-TC-A1-02  BLOCKER
ENT-TC-A1-03  HIGH
ENT-TC-A1-04  HIGH
ENT-TC-A1-05  MEDIUM
```

---

## 3. ENT-TC-A1-01 — Caso metodológico autorizado de fecha pasada no representable

### Evidencia

`Delivery_Stockout_Methodological_Design_v0.3.md` autoriza expresamente:

```text
si expected_delivery_date < evaluation_date
    y aplicabilidad actual NO demostrada
→ NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

El contrato técnico v0.1:

- omitió `evaluation_date` en `PurchaseSpecificDeliveryTimingEvidence`;
- omitió `valid_from / valid_to`;
- omitió `PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN` de los códigos de limitación;
- prohibió `expected_delivery_date` en cualquier estado distinto de KNOWN.

La última restricción impide representar precisamente el caso en que una fecha existe pero su aplicabilidad temporal actual no queda demostrada.

### Corrección requerida

- restaurar `evaluation_date`;
- restaurar `valid_from / valid_to`;
- incorporar `PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN`;
- permitir conservar una fecha observada en un estado `NOT_DETERMINABLE` únicamente cuando existe fuente/evidencia de esa fecha pero falla la aplicabilidad actual;
- prohibir convertir esa fecha en evidencia KNOWN.

**Severidad:** BLOCKER.

---

## 4. ENT-TC-A1-02 — `depletion_date = NOT_EVIDENCED` físicamente alcanzable pero sin semántica ENT cerrada

### Evidencia metodológica

ENT v0.3 enumera para depletion:

```text
CONFLICTING_DATA → CONFLICTING_DATA
UNKNOWN          → NOT_DETERMINABLE
KNOWN            → comparar
NOT_APPLICABLE   → horizonte
```

Y declara:

```text
No existe otro mapeo implícito.
```

### Evidencia física

STK define `ProjectedDateMetric.state` mediante `StockDataState`, que incluye `NOT_EVIDENCED`.

`calculate_stock_projection()` puede producir efectivamente `depletion_date.state = NOT_EVIDENCED` cuando una incertidumbre `NOT_EVIDENCED` se propaga a la proyección antes de poder determinar depletion.

Por tanto, el caso es físicamente alcanzable.

### Defecto del contrato técnico

v0.1 introdujo unilateralmente:

```text
depletion NOT_EVIDENCED → NOT_DETERMINABLE
```

Esa transformación es razonable como conservación de incertidumbre, pero la metodología cerrada prohíbe expresamente mapeos implícitos no enumerados. No puede incorporarse por conveniencia técnica.

### Corrección requerida

Realizar una **reconciliación metodológica mínima v0.3.1**, limitada a este gap de representabilidad, sustentada en:

- M09 / no data ≠ zero/false;
- semántica STK de `NOT_EVIDENCED`;
- frontera ENT factual;
- Assessment `NOT_EVALUABLE ≠ FALSE`.

La reconciliación no puede:

- crear política empresarial;
- cambiar la comparación de fechas;
- crear parámetros;
- redefinir STK;
- convertir ausencia en punctualidad.

Hasta esa reconciliación, el contrato técnico no puede cerrarse.

**Severidad:** BLOCKER.

---

## 5. ENT-TC-A1-03 — Estado común `ENTEvidenceState` mezcla dos semánticas distintas

### Evidencia

La metodología v0.3 autoriza explícitamente los estados:

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

para `PurchaseSpecificDeliveryTimingEvidence`.

No define el mismo catálogo como estado canónico de `BaselineStockoutQualification`; para baseline define precondiciones:

- cualificado/provenance suficiente;
- falta/incompatibilidad → NOT_DETERMINABLE;
- contradicción → CONFLICTING_DATA.

### Riesgo

Compartir un único `ENTEvidenceState` permite `baseline.state = NOT_EVIDENCED` aunque la semántica cerrada de baseline no establece ese estado como salida especializada.

### Corrección requerida

Separar:

```text
BaselineQualificationState = KNOWN | CONFLICTING_DATA | NOT_DETERMINABLE
DeliveryTimingEvidenceState = KNOWN | NOT_EVIDENCED | CONFLICTING_DATA | NOT_DETERMINABLE
```

Los nombres son de representación técnica local; no deben declararse autoridades transversales.

**Severidad:** HIGH.

---

## 6. ENT-TC-A1-04 — Provenance y campos conceptuales incompletos

La metodología v0.3 incluye en `BaselineStockoutQualification`:

- `evaluation_date`;
- `baseline_projection_ref`;
- `evaluated_purchase_trace_ref`;
- `unresolved_refs`;
- `limitations`;
- además de relation/provenance/exclusion refs.

El contrato v0.1 sustituyó parte de esta representación por un objeto `projection` directo y por `evaluated_purchase_ref`, pero omitió:

- `evaluation_date` explícita;
- `baseline_projection_ref` estable;
- `unresolved_refs`;
- `limitations` de entrada.

Consumir el objeto STK directamente es compatible con la implementación, pero no sustituye una referencia trazable al resultado consumido.

### Corrección requerida

Agregar al menos:

```text
evaluation_date
baseline_projection_ref
unresolved_refs
limitations
```

`evaluated_purchase_ref` puede conservarse como nombre físico si queda documentado que representa `evaluated_purchase_trace_ref` y no una identidad global nueva.

Debe validarse:

```text
baseline.evaluation_date == projection.identity.evaluation_date
```

**Severidad:** HIGH.

---

## 7. ENT-TC-A1-05 — Delivery evidence perdió pluralidad y vigencia

La metodología conceptual define:

- `evidence_refs`;
- `valid_from / valid_to`.

El contrato v0.1 redujo evidencia a `evidence_id` singular y omitió vigencia.

Esto puede perder trazabilidad cuando la aplicabilidad de una fecha necesite más de una evidencia.

### Corrección requerida

Usar:

```text
evidence_refs: tuple[str, ...]
valid_from: date | None
valid_to: date | None
```

Una fuente Supplier puede añadir su `evidence_id` como una de esas referencias, sin convertir Supplier en dependencia obligatoria.

**Severidad:** MEDIUM.

---

## 8. Puntos superados

Audit 1 confirma como correctos:

1. paquete especializado `eios/delivery`;
2. no modificación de C0;
3. no modificación de STK;
4. no modificación de Supplier;
5. no nuevo parámetro ENT;
6. no cálculo de fecha desde lead time;
7. no uso de `operation_date` como delivery date;
8. no inferencia de baseline desde `scenario_id`;
9. no persistencia SQL;
10. salida analítica separada de Assessment/CRC/decisión;
11. comparación estricta `delivery > depletion`;
12. igualdad tratada como no posterior;
13. límite de horizonte preservado;
14. incompatibilidad de contexto tratada como error de contrato, no como regla de negocio.

---

## 9. Supplier adapter

No se identifica autoridad suficiente para elevar automáticamente una `SupplierObservation` a evidencia propuesta-específica.

La decisión del contrato v0.1 de **no autorizar todavía** un adaptador automático es correcta.

Una futura adaptación requerirá aportación explícita de `purchase_applicability_ref` y compatibilidad contextual demostrada; `candidate_id` por sí solo no basta.

---

## 10. Secuencia autorizada de depuración

```text
1. reconciliar exclusivamente depletion NOT_EVIDENCED
2. depurar contrato técnico a v0.2
3. Audit 2 transversal
4. solo si limpio → CERRAR
5. solo después → código/tests
```

---

## 11. Estado

```text
AUDIT 1                    COMPLETADA
BLOQUEADORES               2
HALLAZGOS HIGH             2
HALLAZGOS MEDIUM           1
CÓDIGO                      NO AUTORIZADO
POLÍTICA EMPRESARIAL NUEVA 0
```

**DICTAMEN: DEPURAR ANTES DE AUDIT 2.**
