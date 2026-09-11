# EIOS — STK Implementation Contract · Audit 2 Final v0.13

**Estado:** NO SUPERADA — DEPURACIÓN N1…N5 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.14  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.14 resuelve M1…M4 y conserva resueltos A…L. La auditoría independiente sobre el texto resultante detecta **5 huecos técnicos** restantes de ausencia, vigencia y no doble conteo.

Ninguno requiere nueva decisión empresarial.

**DICTAMEN:** NO CERRAR v0.14. Resolver N1…N5 y repetir Audit 2 Final completa.

---

## 2. N1 — `HistoricalDemandPolicy` debe poder representar política/configuración no evidenciada

**Tipo:** BLOQUEANTE M09 / IMPLEMENTABILIDAD.

La política histórica contiene `period_calendar_ref` y `source_ref` obligatorios pero no tiene estado propio. Si el método histórico está seleccionado y `STK-006`, el calendario o la política de ventana no pueden demostrarse, una implementación literal tendría que inventar referencias o no podría construir el input necesario para producir `UNKNOWN / NOT_EVIDENCED`.

**Corrección requerida:** `HistoricalDemandPolicy` incorpora `state: StockDataState`, `issue_refs`, y hace opcionales `period_calendar_ref/source_ref` cuando la política no es `KNOWN`.

Para `KNOWN` exige:

- `parameter_id == STK-006` y parámetro `KNOWN`;
- calendario y fuente no nulos;
- `required_periods` completo, único, no solapado y consistente con el parámetro;
- cualquier `extended_applicable_to` debe ser `>= evaluation_date` y requiere `applicability_source_ref`;
- trazabilidad suficiente.

Una política no `KNOWN` no genera periodos implícitos ni permite reducir la ventana.

---

## 3. N2 — `resulting_ledger` M08 no puede perder asignaciones activas previas

**Tipo:** BLOQUEANTE DE NO REUTILIZACIÓN.

v0.14 valida el ledger de entrada y exige plan exacto, pero no declara que el ledger resultante de una absorción válida preserve todas las asignaciones activas previas. Una implementación podría devolver solo las nuevas entradas y, en la siguiente evaluación, reutilizar cantidades que ya estaban asignadas antes.

**Corrección requerida para `APLICABLE_Y_VALIDADA`:**

- `resulting_ledger` es `KNOWN`, misma fecha/ámbito/artículo que el snapshot de entrada;
- contiene **cada entry activa de entrada exactamente una vez e inalterada**;
- añade exactamente las nuevas entries producidas por el plan;
- todo `allocation_entry_id` es único en el resultado;
- la suma nueva por `confirmed_demand_id` coincide con el plan;
- ninguna entry activa previa se elimina, modifica o sustituye dentro del cálculo STK;
- si no existe nueva asignación, el ledger resultante es semánticamente igual al de entrada.

La liberación/caducidad de asignaciones sigue siendo autoridad aguas arriba, no del motor STK.

---

## 4. N3 — Forecast `KNOWN` exige intervalo temporal completamente determinado

**Tipo:** BLOQUEANTE TEMPORAL.

`AuthorizedForecastRate` declara `applicable_from/to` opcionales y exige un “intervalo válido”, pero no cierra si `KNOWN` permite un extremo nulo. Una vigencia abierta por omisión permitiría consumir el forecast en fechas futuras sin demostrar horizonte suficiente.

**Corrección requerida:** para `AuthorizedForecastRate.state == KNOWN`:

```text
reference_date != null
applicable_from != null
applicable_to != null
applicable_from <= reference_date <= applicable_to
```

y toda fecha consumidora debe pertenecer también a ese intervalo. `horizon_ref`, fuente y versión son obligatorios. Un extremo temporal ausente produce estado no determinado, no vigencia abierta.

`DemandRateResult` `KNOWN` hereda el mismo intervalo demostrable.

---

## 5. N4 — Reserva ya descontada en `stock_committed` no puede volver a salir en M05

**Tipo:** BLOQUEANTE DE DOBLE CONTEO OPENING↔M05.

La autoridad de entrada define `stock_committed` como stock físico ya reservado/asignado a obligaciones. M05 admite `RESERVATION` como salida futura. Si una obligación ya forma parte de `stock_committed`, el opening `stock_available` ya la ha descontado; volver a restarla como `RESERVATION` duplica la misma obligación.

v0.14 protege demanda comercial confirmada mediante `demand_segment_id`, pero no las reservas/obligaciones no comerciales.

**Corrección requerida:**

1. `StockAvailabilityResult` conserva la composición `committed_components` evidenciada —o, como mínimo, los `commitment_id` necesarios para reconciliación— además de la composición comercial agregada.
2. `ProjectionMovement` incorpora `commitment_id: str | null`.
3. `RESERVATION` `KNOWN` exige `commitment_id` estable y trazable.
4. Un `commitment_id` ya presente en opening no puede volver a contribuir como salida M05.
5. Para cualquier otra salida que corresponda a una obligación ya materializada en `stock_committed`, el adaptador debe preservar el mismo `commitment_id`; si no puede demostrarse la no duplicación, no se presenta una proyección completa `KNOWN`.
6. Una nueva reserva surgida después de `evaluation_date` puede participar si su identidad no está en opening y cumple temporalidad/evidencia.

Esto no elimina M05 `RESERVATION`; evita restar dos veces la misma obligación.

---

## 6. N5 — `NO_VERIFICABLE` de pedido M08 necesita incidencias trazables

**Tipo:** BLOQUEANTE M08/M09 DE TRAZABILIDAD.

`ConfirmedDemandRecord` usa `applicability_state`, no `StockDataState`, y por tanto no hereda automáticamente `issue_refs` de §4. Sin un campo físico, `NO_VERIFICABLE` puede indicar que falta evidencia pero no referenciar la ausencia/contradicción registrada.

**Corrección requerida:** añadir `issue_refs: tuple[DataIssueRef, ...]` al registro. Para `NO_VERIFICABLE`, cuando exista registro M09/M10 de la causa, debe conservarse. Una contradicción material que impide validar el pedido referencia `DataIssueRef(CONTRADICTION)`; ausencia registrada referencia `MISSING_DATA`.

---

## 7. Verificaciones sin nuevo bloqueo

- M1…M4: resueltos en v0.14.
- Gate temporal M05 correcto: incertidumbre fuera del horizonte no contamina.
- R-STK-001: no se inventan dependencias RDM pendientes.
- M07: referencia por punto y M08 composición confirmada permanecen correctas.
- M08: `NO_APLICABLE` exige prueba y `APLICABLE_Y_VALIDADA` exige exceso real.
- M10: contradicción físicamente referenciable.
- C0/Parametrización/Rules/CRC/MED: fronteras intactas.

---

## 8. Resultado

- A…M: resueltos.
- N1…N5: abiertos en v0.14.

**Siguiente paso:** DEPURAR v0.15 → repetir Audit 2 Final completa.