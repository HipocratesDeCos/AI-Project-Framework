# EIOS — STK Implementation Contract · Audit 2 Final v0.2

**Estado:** NO SUPERADA — REQUIERE DEPURACIÓN FINAL  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.3  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La revisión independiente confirma que los hallazgos A1…A9 de Audit 1 y B1…B13 de Audit 2 v0.1 están incorporados en v0.3 y que no existe regresión contra M01…M10, C0, Matriz de Reglas, Rule Dependency Matrix ni la frontera de autoridad humana.

Sin embargo, la auditoría de implementabilidad final detecta **7 ambigüedades físicas adicionales**. Ninguna requiere nueva política empresarial: todas son cierres de representación, identidad o validación necesarios para impedir dobles conteos, mezcla de contexto o inferencias técnicas no autorizadas.

**DICTAMEN:** NO CERRAR v0.3. Aplicar DEPURACIÓN FINAL y repetir Audit 2 Final.

---

## 2. C1 — Periodos históricos: unicidad y correspondencia de calendario

**Tipo:** BLOQUEANTE.

La igualdad de conjuntos entre `period_id` recibidos y requeridos no impide recibir dos registros con el mismo `period_id`, porque la conversión conceptual a conjunto ocultaría la duplicidad. Además, un registro puede declarar un ID correcto con límites `period_start/period_end` incompatibles con el calendario que originó la política.

**Corrección requerida:**

- representar los periodos requeridos mediante especificaciones explícitas `RequiredPeriodSpec` con `period_id`, `period_start` y `period_end`;
- exigir unicidad física de `ConsumptionPeriod.period_id`;
- exigir correspondencia uno-a-uno entre ID y límites temporales de cada periodo recibido y la especificación requerida;
- no inferir ni reconstruir silenciosamente el calendario.

---

## 3. C2 — Cantidad pendiente M08 sin estado cuantitativo propio

**Tipo:** BLOQUEANTE.

`ConfirmedDemandRecord.pending_quantity: Decimal | null` no permite demostrar físicamente si la cantidad es `KNOWN`, `UNKNOWN`, `NOT_EVIDENCED` o `CONFLICTING_DATA`, aunque el contrato exige que sea `KNOWN` para absorber exceso.

**Corrección requerida:** representar la cantidad pendiente mediante `NormalizedQuantity` o estructura equivalente con estado, artículo, unidad y trazabilidad explícitos. La absorción solo puede consumir una cantidad `KNOWN` compatible.

---

## 4. C3 — Unicidad de `movement_id`

**Tipo:** BLOQUEANTE.

La unicidad de `supply_identity` protege M06, pero dos movimientos no logísticos con el mismo `movement_id` podrían duplicar la misma salida/entrada en la proyección.

**Corrección requerida:** `movement_id` debe ser único dentro de la colección de movimientos de una evaluación/proyección. Un duplicado es error estructural y no se suma dos veces.

---

## 5. C4 — Afinidad de contexto de resultados intermedios

**Tipo:** BLOQUEANTE.

`StockAvailabilityResult` identifica artículo, unidad y fecha, pero no demuestra que pertenece al mismo `decision_id`, `scenario_id`, `data_snapshot_id`, `parameters_version` y versión metodológica que el consumidor posterior. Esto permitiría mezclar resultados de otro escenario con coincidencia casual de artículo/fecha/unidad.

**Corrección requerida:** definir una identidad STK canónica de resultado/contexto (`StockResultIdentity` o equivalente) derivada de `DecisionContext` y del contexto STK. Todo resultado intermedio que pueda reutilizarse debe conservarla y todo consumidor debe exigir igualdad exacta cuando corresponda.

---

## 6. C5 — Ramas discriminadas no son mutuamente exclusivas

**Tipo:** BLOQUEANTE.

`StockMaximumBasis` y `ExcessToleranceBasis` contienen discriminante `kind`, pero v0.3 no prohíbe que ambas ramas estén simultáneamente pobladas.

**Corrección requerida:** cerrar la exclusividad estructural:

- `DIRECT_QUANTITY` → solo `direct_quantity` presente;
- `COVERAGE_MAXIMUM` → solo `coverage_maximum + demand_rate` presentes;
- `QUANTITY` → solo `quantity` presente;
- `RATE` → solo `rate` presente.

Los campos de ramas inactivas deben ser nulos y el estado de la base debe ser compatible con la rama activa.

---

## 7. C6 — Unidad de P-STK-006 no cerrada

**Tipo:** BLOQUEANTE.

La política histórica valida ID y valor entero, pero no la dimensión/unidad configurada. Un valor con unidad incompatible podría interpretarse como número de periodos mensuales.

**Corrección requerida:** P-STK-006 solo puede gobernar la ventana histórica cuando su unidad está normalizada y autorizada como número de meses/periodos mensuales, o cuando existe una normalización trazable equivalente. No se infiere la unidad por el ID del parámetro.

---

## 8. C7 — Fecha prevista M08 para pedido aplicable y validado

**Tipo:** BLOQUEANTE.

M08 metodológico exige fecha prevista de entrega entre la evidencia mínima del pedido confirmado y limita la absorción a demanda aplicable al horizonte. v0.3 permite `expected_delivery_date = null` incluso cuando `applicability_state = APLICABLE_Y_VALIDADA`.

**Corrección requerida:** un registro `APLICABLE_Y_VALIDADA` debe tener `expected_delivery_date` evidenciada y compatible con la fecha/horizonte de la evaluación de exceso. Si falta o no puede verificarse, no puede clasificarse como aplicable y validado.

---

## 9. Revisión transversal

Se confirma que estos hallazgos **no autorizan**:

- cambios en C0;
- nuevos parámetros o valores por defecto;
- forecast interno;
- transformación automática ventas → demanda;
- nuevas relaciones parámetro ↔ regla;
- resolución heurística de contradicciones;
- reposición/compra automática;
- reescritura de M07 por M08;
- decisión final STK.

Las reglas R-STK-001…004 permanecen bajo autoridad del Motor de Reglas/CRC; STK solo produce hechos y métricas trazables.

---

## 10. Resultado

- Hallazgos Audit 1 A1…A9: **resueltos**.
- Hallazgos Audit 2 B1…B13: **resueltos**.
- Hallazgos Audit 2 Final C1…C7: **abiertos en v0.3**.

**Estado:** NO SUPERADA.  
**Siguiente paso:** DEPURACIÓN FINAL del contrato y repetición independiente de Audit 2 Final.
