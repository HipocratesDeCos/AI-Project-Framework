# EIOS — STK Executable Implementation · Audit 2 v0.1

**Estado:** NO SUPERADA — DEPURACIÓN J1…J7 REQUERIDA  
**Implementación auditada:** `eios/stock` tras depuración I1…I8  
**Evidencia dinámica:** GitHub Actions #538 — SUCCESS  
**Contrato:** STK Implementation Contract v0.17  
**Fecha:** 11/09/2026

---

## 1. Dictamen

I1…I8 quedan resueltos y la suite de PR es verde. La segunda auditoría no usa CI como sustituto del contrato: revisa los bordes no cubiertos por las pruebas actuales y detecta **7 invariantes físicos adicionales**.

Ninguno requiere nueva política empresarial.

**DICTAMEN:** NO CERRAR todavía. Resolver J1…J7 y repetir Audit 2 final.

---

## J1 — Identidad M06 debe ser única en toda la colección conocida

**BLOQUEANTE.**

La implementación comprueba `supply_identity` únicamente después del gate temporal. Dos registros KNOWN de la misma cantidad logística, uno dentro y otro fuera del horizonte, podrían coexistir como pending/transit sin ser rechazados.

El contrato exige que una misma cantidad no ocupe simultáneamente ambos estados; que no contribuya por estar fuera del horizonte no convierte el registro en otra cantidad.

**Corrección:** validar unicidad/exclusividad de `supply_identity` para todos los movimientos KNOWN M06 de la colección antes de decidir contribución temporal.

---

## J2 — `PROPOSED_PURCHASE` debe pertenecer al escenario evaluado

**BLOQUEANTE.**

El modelo exige `scenario_id`, pero el engine no comprueba que coincida con `DecisionContext.scenario_id`.

**Corrección:** todo `PROPOSED_PURCHASE` KNOWN presente en el payload debe tener `scenario_id == context.decision_context.scenario_id`; una propuesta de otro escenario es incompatibilidad estructural, aunque su fecha quede fuera del horizonte.

---

## J3 — `NO_APLICABLE` M08 exige exclusión demostrada

**BLOQUEANTE.**

`ConfirmedDemandRecord(applicability_state=NO_APLICABLE)` puede construirse sin `applicability_source_ref` ni evidencia.

M09/M08 distinguen no aplicabilidad de ausencia precisamente porque `NO_APLICABLE` debe estar demostrado.

**Corrección:** `NO_APLICABLE` exige `applicability_source_ref` y fuente/traza suficiente; si no existe evidencia para demostrar exclusión corresponde `NO_VERIFICABLE`, no `NO_APLICABLE`.

---

## J4 — Ledger M08 debe conservar compatibilidad de unidad al agregarse

**BLOQUEANTE.**

El snapshot valida scope/article, pero M08 suma `allocated_quantity` por pedido sin comprobar `entry.unit` contra la unidad del exceso/pending.

**Corrección:** antes de agregar, toda entry activa consumida debe cumplir `entry.unit == excess.stock_reference.unit`; no se convierten unidades dentro del ledger.

---

## J5 — Identidad/composición de resultados debe estar protegida en el modelo público

**BLOQUEANTE.**

El engine construye correctamente los resultados, pero los modelos aún permiten instanciar manualmente:

- `ExcessResult.identity != stock_reference.identity`;
- `ConfirmedDemandAbsorptionResult.identity != excess_result.identity`;
- `StockProjectionResult.incorporated_confirmed_demand_at_horizon` distinto del último point.

**Corrección:** invariantes model-level. Cuando existan points, la composición de horizonte debe ser exactamente la del último point. Un resultado no puede declarar otra identidad que su fuente contractual.

---

## J6 — Estados determinados M08 deben proteger sus propias fórmulas

**BLOQUEANTE.**

`ConfirmedDemandAbsorptionResult` permite actualmente un `APLICABLE_Y_VALIDADA` con absorción cero, plan vacío o sin ledger resultante, y permite `NO_APLICABLE/NO_EXISTE` con plan no vacío.

**Corrección model-level:**

- `APLICABLE_Y_VALIDADA`: `absorbed_excess > 0`, plan no vacío, suma plan = absorción, ledger resultante KNOWN y `absorbed + residual == excess_result.excess_quantity`;
- `NO_EXISTE / NO_APLICABLE`: absorción 0, plan vacío, residual = exceso determinado;
- `total_remaining_applicable >= absorbed_excess` cuando ambos existen;
- `NO_VERIFICABLE`: sin absorción/residual determinados, sin fabricar incidencia inexistente.

---

## J7 — `ProjectionHorizon` debe ser autoconsistente físicamente

**BLOQUEANTE.**

El engine comprueba PYE-001, pero un objeto `ProjectionHorizon KNOWN` puede construirse con `parameter.value != horizon_days` o `horizon_end` incompatible con `parameter.applicable_reference_date`.

**Corrección model-level:** para KNOWN, `PYE-001` entero positivo no booleano, `horizon_days == parameter.value` y `horizon_end == parameter.applicable_reference_date + horizon_days`.

---

## Verificaciones limpias

- I1…I8 resueltos.
- CI #538 verde.
- schedule demanda exacto AUTHORIZED+CONFIRMED.
- M09/M10 sin imputación/heurística.
- M07 sin interpretación porcentual.
- no defaults.
- C0, Rules, CRC y decisión humana preservados.

---

## Resultado

**J1…J7 ABIERTOS.**

Siguiente paso: **DEPURAR → repetir Audit 2 Final de implementación**.
