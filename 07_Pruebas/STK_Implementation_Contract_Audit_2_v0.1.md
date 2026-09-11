# EIOS — STK Implementation Contract · Audit 2 v0.1

**Estado:** NO SUPERADA — REQUIERE DEPURACIÓN ADICIONAL  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.2  
**Fecha:** 11/09/2026

---

## 1. Dictamen

Audit 2 confirma que los 9 hallazgos de Audit 1 están correctamente incorporados. No se detecta regresión contra M01…M10, C0, reglas, parámetros ni autoridad decisional.

Sin embargo, la revisión de implementabilidad y no ambigüedad detecta **11 hallazgos adicionales**, 9 bloqueantes y 2 preventivos.

**Dictamen:** NO CERRAR v0.2.

---

## 2. B1 — Colección `KNOWN` sin traza

**Tipo:** BLOQUEANTE.

`CollectionEnvelope` permite `KNOWN + items=()` sin exigir `source_ref` o `trace_refs`. Eso permitiría afirmar “no existen registros” sin evidencia de completitud.

**Corrección:** toda colección `KNOWN`, incluida la vacía, exige al menos una referencia trazable. En otro caso debe ser `NOT_EVIDENCED`.

---

## 3. B2 — Versión de parámetros no verificable físicamente

**Tipo:** BLOQUEANTE.

`ConfiguredParameterValue` declara que debe ser coherente con `DecisionContext.parameters_version`, pero el modelo no contiene la versión de la configuración de la que procede.

**Corrección:** añadir `parameters_version` al valor configurado y exigir igualdad con `DecisionContext.parameters_version`.

---

## 4. B3 — Conteo de periodos no demuestra ventana correcta

**Tipo:** BLOQUEANTE.

`len(periods) == required_period_count` no impide sustituir un periodo requerido por otro distinto. Dos conjuntos de 12 periodos pueden contener ventanas diferentes.

**Corrección:** `HistoricalDemandPolicy` debe identificar `required_period_ids` y `period_calendar_ref`/fuente equivalente. El conjunto recibido debe coincidir exactamente con los IDs requeridos. STK no inventa cuáles son los meses naturales.

---

## 5. B4 — `supply_identity` repetido todavía puede duplicarse

**Tipo:** BLOQUEANTE.

El contrato impide `PENDING_ORDER + IN_TRANSIT` simultáneo para la misma identidad, pero no prohíbe dos movimientos `PENDING_ORDER` con la misma `supply_identity`.

**Corrección:** cada `supply_identity` activo aparece una sola vez en el conjunto proyectivo. Una parcialidad logística distinta requiere una identidad de segmento distinta y trazable.

---

## 6. B5 — `PROPOSED_PURCHASE` no contiene scenario_id propio

**Tipo:** BLOQUEANTE.

La sección exige `scenario_id`, pero `ProjectionMovement` no lo contiene. Una propuesta podría entrar en un escenario diferente sin validación estructural.

**Corrección:** añadir `scenario_id: str | null` a `ProjectionMovement`; obligatorio para `PROPOSED_PURCHASE` e igual a `DecisionContext.scenario_id`. Para movimientos factuales no se utiliza como sustituto de identidad fuente.

---

## 7. B6 — Dirección incompatible con source_kind

**Tipo:** BLOQUEANTE.

El modelo permite físicamente combinaciones como `PENDING_ORDER + OUTFLOW`.

**Corrección:** cerrar invariantes:

- `PENDING_ORDER`, `IN_TRANSIT`, `PROPOSED_PURCHASE` → `INFLOW`;
- `AUTHORIZED_DEMAND`, `RESERVATION`, `OTHER_AUTHORIZED_NEED` → `OUTFLOW`.

No se permite dirección contradictoria.

---

## 8. B7 — Opening projection pierde unidad/traza

**Tipo:** BLOQUEANTE.

`opening_stock_available: Decimal | null` + `opening_state` reduce la información respecto a `StockAvailabilityResult`, perdiendo vínculo explícito al cálculo de disponibilidad.

**Corrección:** `StockProjectionInput` debe consumir `opening_availability: StockAvailabilityResult`, verificando artículo/contexto/unidad. No volver a materializar el mismo hecho como Decimal huérfano.

---

## 9. B8 — Movimiento no resuelto sin fecha

**Tipo:** BLOQUEANTE.

Si un movimiento requerido tiene estado no determinado y `effective_date = null`, el contrato no sabe desde qué fecha debe contaminar la proyección.

**Corrección:** un movimiento requerido no determinado sin fecha conocida hace no determinada la proyección futura desde `evaluation_date`. Si la fecha sí se conoce, la incertidumbre comienza en esa fecha.

---

## 10. B9 — Máximo por cobertura con demanda cero

**Tipo:** BLOQUEANTE.

La fórmula `stock_maximum = coverage_maximum_days * authorized_daily_demand` produciría cero si la demanda confirmada es cero. Pero M04 clasifica la cobertura con demanda cero como `UNBOUNDED / NOT_APPLICABLE`; no autoriza convertir ese caso en un máximo de stock igual a cero.

**Corrección:** la derivación por `COVERAGE_MAXIMUM` exige `authorized_daily_demand > 0`. Con cero confirmado, el máximo por cobertura no es aplicable/determinable mediante esa base y no se produce `stock_maximum = 0`.

---

## 11. B10 — Reutilización M08 entre operaciones de absorción

**Tipo:** BLOQUEANTE.

La unicidad de `confirmed_demand_id` dentro de una colección impide duplicidad en una llamada, pero no garantiza que una segunda operación dentro de la misma evaluación vuelva a utilizar el mismo pedido contra otro exceso.

**Corrección:** definir un `allocation_scope_id` derivado de `decision_id + scenario_id + article_id + evaluation_date` o equivalente y un conjunto explícito de IDs ya asignados. La operación es pura: recibe `already_allocated_ids` y devuelve `allocated_ids` actualizados. No requiere persistencia interna.

---

## 12. B11 — Estructura de M07 insuficientemente cerrada

**Tipo:** PREVENTIVO CON IMPACTO DE IMPLEMENTABILIDAD.

El contrato define tipos conceptuales `DIRECT_QUANTITY/COVERAGE_MAXIMUM` y `QUANTITY/RATE`, pero no cierra las estructuras físicas de entrada. Un implementador podría resolverlas con campos ambiguos o inferir tipo por presencia/valor.

**Corrección:** declarar modelos equivalentes a `StockMaximumBasis`, `ExcessToleranceBasis` y `ExcessInput`, con tipo discriminante explícito, estado, fuente/traza y parámetros esperados (`P-STK-004`, `P-STK-005`) cuando proceda.

---

## 13. B12 — Forecast version debe coincidir con contexto

**Tipo:** PREVENTIVO.

Existe `forecast_version` en contexto y forecast, pero falta invariante de igualdad.

**Corrección:** si `method = AUTHORIZED_FORECAST`, `AuthorizedDemandForecast.forecast_version == StockComputationContext.forecast_version` y ninguno puede estar vacío.

---

## 14. B13 — Estado inicial cero en proyección

**Tipo:** PREVENTIVO.

`depletion_date` se define sobre cierres diarios. Si el stock inicial conocido ya es cero en `evaluation_date` y no hay movimiento ese día, podría quedar sin fecha de agotamiento.

**Corrección:** el stock inicial forma parte de la secuencia. Si `opening_availability.stock_available == 0`, `depletion_date = evaluation_date`. `minimum_projected_stock` incluye el valor inicial.

---

## 15. Revisión transversal

Audit 2 confirma además:

- no se introduce forecast interno;
- no se usa `P-PYE-006` como regla oculta;
- no se convierte `PurchaseOperation.quantity` sin unidad;
- no se recorta stock proyectado negativo;
- no existe infinito numérico en cobertura;
- no se hardcodean valores iniciales;
- no se asignan nuevas relaciones P-STK/P-PYE ↔ reglas;
- M08 sigue sin borrar M07;
- M09/M10 permanecen explícitos;
- STK sigue sin decisión final.

---

## 16. Resultado

**Hallazgos Audit 1:** 9/9 resueltos.  
**Hallazgos Audit 2:** 13 (10 bloqueantes, 3 preventivos).  
**Estado:** NO SUPERADA.

Se requiere **DEPURACIÓN 2** y repetición de Audit 2 antes de CERRAR.
