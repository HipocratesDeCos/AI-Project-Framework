# EIOS — STK Executable Implementation · Audit v0.1

**Estado:** NO SUPERADA — DEPURACIÓN REQUERIDA  
**Implementación auditada:** `eios/stock` materialización inicial  
**Contrato:** STK Implementation Contract v0.17  
**Diseño:** STK Executable Implementation Design v0.3 — CERRADO  
**Fecha:** 11/09/2026

---

## Dictamen

La implementación respeta la arquitectura general, pero la lectura física de `models.py` + `engine.py` descubre **8 hallazgos** que podrían producir falsa certeza o aceptar objetos contractualmente incoherentes.

**NO pasar a CI** hasta resolver I1…I8.

---

## I1 — `NOT_APPLICABLE` puede desaparecer y producir falso `KNOWN`

**BLOQUEANTE.**

`_uncertainty_state()` solo considera UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA. En dependencias obligatorias, `NOT_APPLICABLE` puede quedar ignorado y devolver `KNOWN`.

Casos afectados:

- `HistoricalDemandPolicy/ConsumptionPeriod` requerido `NOT_APPLICABLE` podría acortar de hecho la ventana y producir una tasa KNOWN;
- `DemandProjectionSchedule NOT_APPLICABLE` puede no bloquear una proyección completa;
- otras dependencias obligatorias pueden heredar el mismo fallo.

**Corrección:** helpers de propagación deben distinguir “incertidumbre” de “dependencia obligatoria no aplicable”. Para resultados con `StockDataState`, `NOT_APPLICABLE` se conserva cuando la operación entera queda demostrablemente no aplicable; cuando el contrato del resultado no admite ese estado, la función no puede producir KNOWN y debe usar el tratamiento específico autorizado, nunca ignorarlo.

En histórico/proyección: cualquier required period/policy/schedule no KNOWN impide resultado KNOWN.

---

## I2 — M08 `NO_VERIFICABLE` puede fallar por falta de issue record persistido

**BLOQUEANTE.**

`ConfirmedDemandAbsorptionResult` exige `issue_refs` no vacío para `NO_VERIFICABLE`, pero M09 solo exige conservar el registro cuando exista; el engine no puede inventar `issue_record_ref`.

Una entrada UNKNOWN válida sin artefacto de incidencia persistido puede terminar en `ValidationError` en lugar de resultado no verificable.

**Corrección:** `NO_VERIFICABLE` no publica absorción/residual; preserva incidencias cuando existan, pero no obliga al engine a fabricar una referencia inexistente.

---

## I3 — Pedido `APLICABLE_Y_VALIDADA` fuera del horizonte se excluye silenciosamente

**BLOQUEANTE.**

En M08, una orden ya marcada `APLICABLE_Y_VALIDADA` debe cumplir:

`excess_reference_date < expected_delivery_date <= horizon_end`.

El engine actual hace `continue` si no cumple, convirtiendo una incoherencia contractual en exclusión silenciosa.

**Corrección:** registro `APLICABLE_Y_VALIDADA` que incumple esa ventana es error estructural/incompatibilidad del payload. `NO_APLICABLE` debe venir explícitamente demostrado por su estado/fuente, no inferirse reescribiendo un APLICABLE.

---

## I4 — `AllocationScope.horizon` no se reconcilia completamente con identidad

**BLOQUEANTE.**

Se valida que horizon sea KNOWN, pero no que:

- company/parameters_version coincidan con identity;
- fecha de parámetro = evaluation_date;
- `PYE-001` sea el parámetro físico;
- `horizon_end == evaluation_date + horizon_days`.

**Corrección:** validar los mismos invariantes usados al construir `ProjectionHorizon` antes de M08.

---

## I5 — `DemandRateResult` permite combinaciones semánticamente imposibles

**BLOQUEANTE.**

El modelo KNOWN valida tasa/fechas pero no impide:

- `method != selection.method`;
- histórico con `forecast_version != None`;
- forecast con versión nula;
- identidad forecast incoherente con resultado.

El engine crea objetos correctos, pero el contrato público permite instanciarlos incorrectamente.

**Corrección:** endurecer validación model-level de método/selección/forecast.

---

## I6 — `DemandProjectionSchedule` no exige selección idéntica a su `DemandRateResult`

**BLOQUEANTE.**

Un schedule KNOWN puede construirse con `selection A` y `demand.selection B`; el engine detecta parte vía contexto, pero el objeto contractual en sí es incoherente.

**Corrección:** KNOWN exige `selection == demand.selection` y `demand.method == selection.method`.

---

## I7 — `ExcessResult` no protege la copia exacta de composición confirmada

**BLOQUEANTE.**

El contrato exige:

`ExcessResult.incorporated_confirmed_demand == stock_reference.incorporated_confirmed_demand`.

El engine lo respeta, pero el modelo permite construir un `ExcessResult` divergente.

**Corrección:** invariante model-level de igualdad exacta.

---

## I8 — Ledger KNOWN no valida entries contra su scope/article

**BLOQUEANTE.**

`AllocationLedgerSnapshot` valida IDs únicos pero no que cada entry pertenezca al mismo `scope/article`. M08 lo comprueba tarde; otros consumidores podrían aceptar un snapshot físicamente inconsistente.

**Corrección:** snapshot KNOWN exige cada entry con scope/article coincidente y unidad/identidad no vacías conforme a su propio tipo.

---

## Sin bloqueo

- C0 no se modifica.
- No hay Rules/CRC/decisión automática.
- No hay SQL/API/persistencia.
- No se hardcodean valores de catálogo.
- Schedule no se genera desde tasa.
- M06 usa supply identity.
- M07 no convierte 10 → 10 % heurísticamente.
- M08 no prioriza pedidos ni genera IDs.

---

## Resultado

**I1…I8 ABIERTOS.**

Siguiente paso: **DEPURAR implementación → AUDIT 2 de implementación**.
