# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL AUDIT 1 v0.1

**Estado:** AUDIT 1 COMPLETADA — REQUIERE DEPURACIÓN  
**Fecha:** 11/09/2026  
**Baseline:** `main @ ab922bed82fb63af509c033d69fd62a178b8d058`  
**Objeto auditado:** `Delivery_Stockout_Methodological_Design_v0.1.md`

---

## 1. Alcance contrastado

Se contrasta el diseño ENT v0.1 contra:

- `03_Arquitectura/Architecture_Blueprint.md`;
- `01_Modelo/STK_M05_Projection_Authority.md`;
- `01_Modelo/STK_M06_Logistics_Authority.md`;
- `08_Implementacion/STK_Implementation_Contract.md`;
- `eios/stock/models.py`;
- `eios/stock/engine.py`;
- `08_Implementacion/Decision_Twin_Comparison_Contract.md`;
- `08_Implementacion/Decision_Twin_Implementation_Contract.md`;
- `05_Motor/Viability_Scenario_Engine.md`;
- `eios/supplier/models.py`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.4;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.9;
- C0 físico.

---

## 2. ENT-A1-01 — Escenario base sin compra: autoridad CONFIRMADA

Architecture Blueprint Capa 3 establece expresamente:

> compra comparada contra escenario base sin compra.

STK físico admite `PROPOSED_PURCHASE` como movimiento futuro y, si se suministra, dicha entrada puede alterar el `depletion_date`.

Por tanto, el diseño acierta al exigir que el agotamiento usado por `R-ENT-001` proceda del escenario base sin la compra propuesta evaluada.

**Dictamen:** CONFIRMADO — INVARIANTE OBLIGATORIO.

---

## 3. ENT-A1-02 — `StockProjectionResult` no demuestra por sí solo la exclusión de la compra

El resultado físico STK publica `depletion_date`, horizonte, puntos y estados agregados, pero no preserva la colección de movimientos de entrada que originó la proyección.

En consecuencia:

```text
StockProjectionResult
!=
prueba suficiente de “base scenario without proposed purchase”
```

ENT necesita provenance/input ref suficiente para demostrar exclusión de la propuesta.

No procede modificar STK solo para resolver este consumidor.

**Dictamen:** GAP DE REPRESENTABILIDAD CONFIRMADO.

---

## 4. ENT-A1-03 — `Scenario_ID` no demuestra semántica de baseline

Decision Twin conserva `Decision_ID` y `Scenario_ID`, y su comparación exige escenarios distintos dentro de la misma decisión.

Sin embargo, su contrato prohíbe reutilizar `Scenario_ID` con semántica adicional por conveniencia física.

Viability Scenario Engine establece que:

- un escenario deriva de una operación/escenario precedente;
- debe conservar identidad, relación con el precedente y trazabilidad;
- el esquema físico concreto de dicha relación sigue pendiente de especificación.

Por tanto:

```text
same decision_id + different scenario_id
```

no demuestra por sí mismo que uno sea el baseline autorizado sin compra.

El diseño v0.1 debe sustituir cualquier idea de “base_scenario_id basta” por una **calificación trazable de baseline** basada en provenance/autorización, sin crear un nuevo `scenario_type` global.

**Dictamen:** HALLAZGO CORRECTIVO.

---

## 5. ENT-A1-04 — C0 no contiene expected delivery ni lead time

`PurchaseOperation` físico contiene `operation_date`, pero no:

- `expected_delivery_date`;
- `expected_receipt_date`;
- `lead_time`.

Por tanto ENT no puede recuperar la fecha requerida desde C0.

**Dictamen:** FUENTE EXTERNA/ESPECIALIZADA NECESARIA; C0 NO SE MODIFICA POR INFERENCIA.

---

## 6. ENT-A1-05 — Supplier `DELIVERY_DATE` es fuente posible, no suficiente por nombre

Supplier Evidence Core puede representar observaciones:

```text
dimension = DELIVERY_DATE
value_kind = DATE
```

con identidad de proveedor/candidato/artículo, `semantic_ref`, fuente, evidencia y trazas.

Sin embargo `SupplierObservation` no contiene `applicability_ref` de propuesta específica.

Por tanto una observación DATE no demuestra automáticamente:

> esta es la fecha prevista/comprometida de la compra evaluada.

ENT necesita una adaptación o provenance que demuestre aplicabilidad a la propuesta evaluada.

**Dictamen:** DISEÑO v0.1 CORRECTO EN FRONTERA; REQUIERE REPRESENTABILIDAD MÁS EXPLÍCITA.

---

## 7. ENT-A1-06 — Lead time no autoriza derivación de fecha

No existe autoridad suficiente para ejecutar internamente:

```text
anchor_date + lead_time → expected_delivery_date
```

Faltan, entre otros:

- fecha de anclaje;
- calendario natural/laborable;
- unidad;
- cut-off/feriados;
- vigencia;
- aplicabilidad.

PYE-004 permanece control metodológico STK y no demuestra consumo directo por `R-ENT-001`.

**Dictamen:** PROHIBICIÓN CORRECTA.

---

## 8. ENT-A1-07 — Tratamiento de depletion `NOT_APPLICABLE` y horizonte: CORRECTO

STK devuelve `depletion_date = NOT_APPLICABLE` cuando no se agota el stock dentro del horizonte proyectado completamente determinado.

No significa agotamiento imposible en todo futuro.

El diseño v0.1 acierta:

```text
expected_delivery_date <= horizon_end
→ no entrega posterior al agotamiento dentro del horizonte evidenciado

expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
```

sin extrapolar STK.

**Dictamen:** CONFIRMADO.

---

## 9. ENT-A1-08 — Igualdad de fechas: comparación estricta correcta con limitación intradía

`R-ENT-001` utiliza la expresión “posterior”.

A granularidad DATE:

```text
expected_delivery_date == depletion_date
```

no satisface estrictamente “posterior”.

Pero tampoco demuestra que la entrega preceda físicamente al agotamiento dentro de ese día.

El diseño debe conservar una limitación explícita de granularidad.

**Dictamen:** CONFIRMADO.

---

## 10. ENT-A1-09 — RDM no contiene R-ENT-001

La RDM vigente no registra dependencias para `R-ENT-001`.

Antes de implementación deberán demostrarse al menos las dependencias semánticas equivalentes a:

```text
R-ENT-001 → qualified base stockout timing evidence
R-ENT-001 → purchase-specific delivery timing evidence
```

No se inventa todavía `Evaluability_Impact`, Criticality, fallback ni COMPONENT adicional.

**Dictamen:** GAP RDM CONFIRMADO.

---

## 11. ENT-A1-10 — No se requiere parámetro ENT demostrado

La regla vigente compara dos fechas de forma directa. No exige umbral adicional.

No existe evidencia para crear `P-ENT-*`.

PYE-004 no se transforma en parámetro consumidor de R-ENT-001.

**Dictamen:** NO CREAR PARÁMETRO ENT.

---

## 12. Corrección requerida

El diseño v0.2 deberá reemplazar la noción insuficiente de `base_scenario_id` como prueba por un objeto conceptual equivalente a:

```text
BaselineStockoutQualification
├── decision_id
├── evaluated_purchase_ref
├── baseline_projection_ref
├── baseline_relation_ref
├── projection_input_or_provenance_ref
├── proposed_purchase_exclusion_ref
├── depletion_state/date
├── horizon_end
├── issue_refs
└── trace_refs
```

### Invariantes

1. `baseline_relation_ref` demuestra la relación del baseline con la decisión/operación precedente; no es un simple `scenario_id`.
2. `proposed_purchase_exclusion_ref` demuestra que la compra evaluada no contribuyó a la proyección base.
3. ENT no crea `scenario_type`, `parent_scenario_id` ni entidad global nueva.
4. ENT no recalcula STK para fabricar la prueba.

---

## 13. Resultado de Audit 1

| Área | Estado |
|---|---|
| Regla R-ENT-001 | EXISTE |
| Stockout date STK | IMPLEMENTADA |
| Base sin compra | AUTORIDAD CONFIRMADA |
| Prueba física de baseline/exclusión | GAP / REQUIERE ADAPTADOR DE PROVENANCE |
| Expected delivery en C0 | NO EXISTE |
| Supplier DELIVERY_DATE | POSIBLE FUENTE, NO AUTOMÁTICA |
| Lead-time derivation | NO AUTORIZADA |
| Horizonte | CERRABLE |
| Igualdad date-level | CERRABLE CON LIMITACIÓN |
| RDM | GAP |
| Parámetro ENT | NO NECESARIO / NO DEMOSTRADO |

**AUDIT 1: NO SUPERADA PARA CIERRE.**

Bloqueador correctivo de diseño: representar adecuadamente la calificación del baseline y la aplicabilidad de delivery timing sin crear semántica global nueva.
