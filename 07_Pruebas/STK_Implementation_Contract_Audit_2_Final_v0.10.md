# EIOS — STK Implementation Contract · Audit 2 Final v0.10

**Estado:** NO SUPERADA — DEPURACIÓN FINAL K1…K7 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.11  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.11 resuelve J1…J4 y conserva resueltos A…I. La auditoría completa vuelve a recorrer M01…M10, autoridad de entrada, C0, Centro de Parametrización, catálogo PYE, especificación STK/PYE↔reglas y fronteras M01/M02/M03/M05/M06/M08/M09.

Persisten **7 bloqueos técnicos**. Ninguno requiere nueva política empresarial, fórmula o valor. Impiden representar ausencia sin inventar datos, preservar ámbito operativo, demostrar autoridad temporal o reconstruir la evidencia exigida por M01/M02/M03/M06.

**DICTAMEN:** NO CERRAR v0.11. Resolver K1…K7 y repetir Audit 2 Final desde cero.

---

## 2. K1 — Estados no determinados deben ser físicamente representables

**Tipo:** BLOQUEANTE M09 / IMPLEMENTABILIDAD.

El contrato declara correctamente `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA`, pero varias estructuras mantienen obligatorios campos que pueden faltar precisamente cuando aparece ese estado.

Afecta como mínimo a `AuthorizedStockPolicyQuantity`, `AuthorizedQuantityThreshold`, `ConfiguredParameterValue`, `ConsumptionPeriod`, `ProjectionMovement` y `ConfirmedDemandRecord`.

**Corrección requerida:**

1. los campos empresariales que pueden faltar son físicamente opcionales;
2. `KNOWN` o `APLICABLE_Y_VALIDADA` exige todos los campos requeridos por su autoridad;
3. estados no determinados no se rellenan con cero, fechas sintéticas, IDs ficticios o defaults;
4. identificadores de contexto conocidos por construcción pueden seguir siendo obligatorios;
5. cada tipo declara invariante `state ↔ payload`.

---

## 3. K2 — Ledger M08 ausente no puede equivaler a ledger vacío

**Tipo:** BLOQUEANTE M08/M09.

`AllocationLedgerSnapshot` v0.11 no tiene estado de evidencia. `entries=()` podría significar tanto “ninguna asignación activa” como “ledger no recuperado”.

**Corrección requerida:** estado explícito `KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`; solo `KNOWN + entries=()` con fuente/traza significa vacío evidenciado. `state != KNOWN` no autoriza suma cero ni absorción determinada. `source_ref` puede ser nula cuando falta evidencia. `KNOWN` exige fecha correcta, fuente/traza y unicidad.

---

## 4. K3 — Horizonte M05 anclado a `P-PYE-001`

**Tipo:** BLOQUEANTE DE AUTORIDAD/PARAMETRIZACIÓN.

M05 exige horizonte explícito, versionado y efectivo; la especificación STK/PYE determina que `P-PYE-001` configura M05. v0.11 permite `horizon_end` suministrado sin demostrar esa configuración.

**Corrección requerida para v0.1:** `ProjectionHorizon` o equivalente consume `ConfiguredParameterValue(P-PYE-001)` `KNOWN`, versión/fecha correctas, entero positivo no booleano y unidad días autorizada/normalizada. `horizon_end = evaluation_date + horizon_days`; el valor inicial 90 no es fallback. Ausencia del parámetro impide proyección completa `KNOWN`.

---

## 5. K4 — Frontera operativa de `P-PYE-002…006`

**Tipo:** BLOQUEANTE DE AMBIGÜEDAD CONTRACTUAL.

La autoridad los clasifica como controles potenciales/no operativos sin consumidor directo demostrado, pero v0.11 no declara si el motor los consume.

**Corrección requerida v0.1:**

- `P-PYE-001`: operativo solo como horizonte (K3);
- `P-PYE-002/003`: no operativos como gates configurables; M06 decide elegibilidad por evidencia/estado/temporalidad. Su futura activación requiere contrato adicional;
- `P-PYE-004`: no operativo porque v0.1 no deriva fechas desde `lead_time`;
- `P-PYE-005`: no operativo para ventas→demanda;
- `P-PYE-006`: no operativo como umbral de R-STK-001.

Esto no elimina parámetros del catálogo; impide comportamiento divergente.

---

## 6. K5 — Falta el ámbito operativo en identidad y compatibilidad

**Tipo:** BLOQUEANTE DE AISLAMIENTO DE DATOS.

La autoridad de entrada exige que `stock_on_hand`, `stock_committed` y `stock_available` pertenezcan al mismo **ámbito operativo**. M01 agrega consumo por artículo y organización/unidad operativa. v0.11 identifica artículo, escenario y snapshot, pero no conserva el ámbito organizativo/operativo de las cantidades.

Sin este campo, dos cantidades del mismo artículo y fecha pero de almacenes/unidades distintas podrían resultar compatibles técnicamente.

**Corrección requerida:**

- introducir una referencia canónica `operational_scope_id` —o estructura equivalente— suministrada aguas arriba y no inferida por STK;
- incluirla en `StockComputationContext` y `StockResultIdentity`;
- las entradas cuantitativas y evidencias de stock/consumo/movimientos/demanda aplicables deben pertenecer al mismo ámbito o demostrar explícitamente su aplicabilidad a él;
- no definir desde STK jerarquías organizativas, redistribución entre centros ni equivalencias de ámbito.

---

## 7. K6 — M06 debe conservar proveedor y origen documental

**Tipo:** BLOQUEANTE DE TRAZABILIDAD M06.

M06 exige que cada pedido pendiente/tránsito conserve como mínimo origen documental, artículo, cantidad/unidad, **proveedor**, estado, fecha prevista y evidencia. `ProjectionMovement` v0.11 conserva `supply_identity` y `source_ref`, pero no distingue proveedor ni origen documental de forma contractual.

**Corrección requerida:** para `source_kind == PENDING_ORDER | IN_TRANSIT` y estado `KNOWN`, conservar `supplier_id` y `supply_document_ref` (o referencias equivalentes), además de `supply_identity`, fecha, cantidad, fuente y trazas. No se inventan cuando falta evidencia; el movimiento queda no determinado.

---

## 8. K7 — Reconstruibilidad M01/M02/M03 y normalización

**Tipo:** BLOQUEANTE DE TRAZABILIDAD.

M01 exige preservar organización/unidad, periodo, cantidad/unidad fuente, unidad base, conversión aplicada, procedencia/fecha y versión metodológica. M02/M03 exigen poder reconstruir política/método, versión, variables/evidencias utilizadas y vigencia del valor autorizado.

v0.11 conserva valores finales y trazas genéricas, pero no fija una referencia contractual suficiente para demostrar esa reconstrucción.

**Corrección requerida:**

- `NormalizedQuantity` conserva `source_unit` y `normalization_ref` cuando exista transformación; una conversión no demostrada no produce `KNOWN`;
- `ConsumptionPeriod` conserva `operational_scope_id`, `methodology_version` y una referencia de agregación/normalización capaz de reconstruir registros fuente, unidades y conversiones;
- `AuthorizedStockPolicyQuantity` conserva `derivation_ref` o conjunto equivalente de referencias que permita reconstruir las variables/evidencias exigidas por M02/M03, además de política, versión y vigencia;
- estas referencias no crean una fórmula STK ni duplican el artefacto fuente: preservan su localización y autoridad.

---

## 9. Verificaciones sin nuevo bloqueo

- M04: cero confirmado → `UNBOUNDED / NOT_APPLICABLE`, sin infinito numérico.
- M05/M06: cutoff diario estricto y `supply_identity` permanecen correctos; K3/K6 refuerzan autoridad y trazabilidad.
- M07: máximo/tolerancia conservan versión y fecha aplicable.
- M08: opening→M05→M08 y no prioridad siguen correctos; K2 refuerza ausencia del ledger.
- La tasa de demanda **no se calendariza automáticamente** en M05: v0.1 solo consume movimientos futuros explícitamente autorizados; no se introduce una transformación forecast/tasa→calendario no documentada.
- M10: no resolución heurística.
- C0: no se modifica.
- Rules/CRC/MED: sin transferencia de autoridad.
- Autoridad humana: preservada.

---

## 10. Resultado

- A…J: resueltos.
- K1…K7: abiertos en v0.11.

**Siguiente paso:** DEPURAR v0.12 → repetir Audit 2 Final completa.