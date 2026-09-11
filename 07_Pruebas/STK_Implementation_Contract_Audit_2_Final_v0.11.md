# EIOS — STK Implementation Contract · Audit 2 Final v0.11

**Estado:** NO SUPERADA — DEPURACIÓN L1…L5 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.12  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.12 resuelve K1…K8: ausencia físicamente representable, ledger evidenciado, horizonte `PYE-001`, frontera PYE, ámbito operativo, trazabilidad M06, reconstruibilidad M01/M02/M03 e IDs canónicos de parámetros.

La auditoría independiente de implementabilidad final detecta **5 huecos restantes**, todos técnicos. No requieren decisión empresarial nueva.

**DICTAMEN:** NO CERRAR v0.12. Resolver L1…L5 y repetir Audit 2 Final completa.

---

## 2. L1 — Tipos contractuales referenciados pero no materializados

**Tipo:** BLOQUEANTE DE IMPLEMENTABILIDAD.

v0.12 referencia conceptos que el futuro `models.py` tendría que inventar:

- el objeto `forecast` usado para construir `DemandRateResult`;
- la forma física de `StockMaximumBasis` y `ExcessToleranceBasis`;
- `ExcessResult`, referenciado después por M08;
- la salida material de absorción M08.

**Corrección requerida:** declarar estructuras mínimas explícitas y discriminadas para:

1. `AuthorizedForecastRate` — ámbito/artículo, tasa diaria, unidad, versión, referencia/aplicabilidad, estado, fuente/trazas;
2. `StockMaximumBasis` — `DIRECT_QUANTITY | COVERAGE_MAXIMUM`, con ramas exclusivas;
3. `ExcessToleranceBasis` — `QUANTITY | RATE`, con ramas exclusivas;
4. `ExcessResult` — identidad, referencia, máximo, tolerancia, umbral, exceso, estado y composición de demanda incorporada;
5. `ConfirmedDemandAbsorptionResult` — identidad, exceso original, total aplicable, absorbido, residual, plan, ledger resultante, estado/trazas.

Los tipos no crean lógica nueva; fijan físicamente lógica ya autorizada.

---

## 3. L2 — Métricas agregadas de proyección necesitan estado propio

**Tipo:** BLOQUEANTE M09.

`StockProjectionResult` v0.12 tiene un único `state`, pero también contiene `minimum_projected_stock` y `depletion_date`. La propia proyección puede tener un prefijo determinado y después quedar contaminada por un movimiento desconocido.

La fórmula actual `min(opening, determined daily closings)` podría producir un número parcial aunque la proyección completa no fuese `KNOWN`, contradiciendo el principio `state ↔ payload`.

**Corrección requerida:** materializar ambos agregados como valores con estado propio, por ejemplo:

```text
ProjectedDecimalMetric(value, state, trace_refs)
ProjectedDateMetric(value, state, trace_refs)
```

Reglas conservadoras:

- `minimum_projected_stock` solo es `KNOWN` cuando el horizonte necesario para demostrar el mínimo está completamente determinado;
- `depletion_date` es `KNOWN` cuando puede demostrarse la primera fecha de agotamiento sin que exista incertidumbre previa capaz de adelantarla; opening cero conocido sigue permitiendo `evaluation_date`;
- en caso contrario el valor es nulo con estado de incertidumbre apropiado.

No se publica un mínimo parcial como mínimo del horizonte.

---

## 4. L3 — La composición M05 debe existir por punto proyectado

**Tipo:** BLOQUEANTE DE NO DOBLE CONTEO M05↔M08.

M08 debe descontar exactamente la demanda confirmada ya incorporada **hasta `stock_reference.reference_date`**.

v0.12 conserva una sola composición agregada en `StockProjectionResult`, mientras `ProjectionPoint` no la contiene. Para una referencia M07 intermedia, usar la composición de fin de horizonte descontaría demanda posterior; usar ninguna permitiría reutilizar demanda ya incorporada.

**Corrección requerida:** cada `ProjectionPoint` conserva:

```text
incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
```

acumulada exclusivamente hasta `reference_date`. `StockReferenceValue(PROJECTED)` copia la composición del punto concreto. La composición de nivel resultado puede conservar, si se desea, la del último punto, pero nunca sustituye a la composición por fecha.

---

## 5. L4 — M08 debe consumir el mismo horizonte autorizado, no una fecha raw

**Tipo:** BLOQUEANTE DE AUTORIDAD TEMPORAL.

K3 cerró que M05 obtiene su horizonte de `PYE-001`, pero `AllocationScope` v0.12 todavía contiene `horizon_end` + `horizon_source_ref` libres. Un llamador podría evaluar M08 con un horizonte diferente del autorizado para el contexto STK.

**Corrección requerida:** `AllocationScope` consume un `ProjectionHorizon` `KNOWN` compatible con contexto/fecha/configuración y deriva de él `horizon_end`. Para un exceso proyectado, debe ser el horizonte de la proyección que originó la referencia. Para referencia actual, sigue siendo el horizonte STK `PYE-001` del contexto evaluado. No se admite una fecha final paralela.

---

## 6. L5 — Ledger M08 debe estar aislado por ámbito y artículo

**Tipo:** BLOQUEANTE DE AISLAMIENTO.

K5 incorporó `StockScope`, pero `AllocationLedgerEntry/Snapshot` no conservan ámbito ni artículo. Depender únicamente de `confirmed_demand_id` presupone unicidad global y permitiría mezclar un snapshot de otro artículo/centro si el adaptador falla.

**Corrección requerida:**

- `AllocationLedgerSnapshot` conserva `scope` y `article_id` y debe coincidir con `AllocationScope`;
- cada `AllocationLedgerEntry` conserva, directa o inmutablemente mediante el snapshot, ámbito/artículo; v0.1 materializa ambos explícitamente para validación local;
- una entrada de otro ámbito/artículo es estructuralmente incompatible y no se agrega.

---

## 7. Verificaciones transversales sin nuevo bloqueo

- K1…K8: resueltos en v0.12.
- M01/M02/M03: reconstruibilidad y ausencia preservadas.
- M04: zero demand → UNBOUNDED.
- M05/M06: horizonte, cutoff, proveedor/origen y no doble conteo preservados.
- M07: autoridad/versiones y estados correctos.
- M08: no prioridad y reconciliación cuantitativa correctas una vez cerrados L3…L5.
- M09/M10: sin imputación ni heurística.
- C0/Rules/CRC/MED: fronteras intactas.

---

## 8. Resultado

- A…K: resueltos.
- L1…L5: abiertos en v0.12.

**Siguiente paso:** DEPURAR v0.13 → repetir Audit 2 Final completa.