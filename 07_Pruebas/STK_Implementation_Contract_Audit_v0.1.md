# EIOS — STK Implementation Contract · Audit 1 v0.1

**Estado:** AUDITADO — REQUIERE DEPURACIÓN  
**Baseline auditado:** `d782471dd0e08a30a628de56bf2e54c37c6dfb16`  
**Fecha:** 11/09/2026  
**Objeto:** `08_Implementacion/STK_Implementation_Contract.md` v0.1

---

## 1. Dictamen

El diseño es coherente con la frontera STK y conserva adecuadamente los principios principales:

- C0 no se modifica;
- ausencia ≠ cero;
- ventas ≠ demanda;
- no existen defaults normativos hardcodeados;
- M06 no debe duplicarse;
- M08 no reescribe M07;
- STK no decide;
- Decimal, fechas y versiones son explícitos;
- la proyección no inventa movimientos a partir de una tasa de demanda.

No obstante, Audit 1 identifica **9 hallazgos**, de los cuales **7 son bloqueantes de cierre contractual** y 2 son precisiones preventivas.

**Resultado:** NO CERRAR todavía.

---

## 2. Hallazgo A1 — Orden intradía arbitrario en proyección

**Severidad:** BLOQUEANTE.

El diseño ordena movimientos por `effective_date` y posteriormente por `movement_id`.

`movement_id` es una identidad técnica y no posee autoridad empresarial para decidir si, dentro de una misma fecha, una salida ocurre antes o después de una entrada.

Esto podría alterar artificialmente:

- `minimum_projected_stock`;
- `depletion_date`;
- la evidencia consumida posteriormente por `R-STK-001`.

### Corrección requerida

La granularidad v0.1 debe permanecer **diaria**. Todos los movimientos de una misma fecha deben agregarse antes de calcular el cierre de esa fecha:

`closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date`

STK v0.1 no puede afirmar un agotamiento intradía sin una fuente temporal más granular y una futura extensión autorizada.

---

## 3. Hallazgo A2 — Colección vacía ≠ ausencia de datos

**Severidad:** BLOQUEANTE.

Tuplas/listas vacías de:

- movimientos logísticos;
- consumos;
- demanda confirmada;

no distinguen entre:

- evidencia de que no existe ningún registro aplicable;
- ausencia de información;
- consulta no realizada;
- fuente no evidenciada.

Esto contradice M09 si una colección vacía se interpreta silenciosamente como cero elementos reales.

### Corrección requerida

Toda colección empresarial relevante debe tener estado de colección explícito, por ejemplo:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Solo `KNOWN + items=()` puede significar conjunto vacío evidenciado.

`NO_EXISTE` de M08 no puede deducirse de una lista vacía cuya completitud no está evidenciada.

---

## 4. Hallazgo A3 — Falta identidad de suministro separada de movement_id

**Severidad:** BLOQUEANTE.

`ProjectionMovement.movement_id` identifica el evento técnico, pero no demuestra que dos eventos representen la misma cantidad logística.

M06 exige conservar la identidad del suministro para impedir que una misma cantidad se compute simultáneamente como `PENDING_ORDER` e `IN_TRANSIT`.

### Corrección requerida

Los movimientos M06 deben incluir `supply_identity` obligatorio. La proyección debe rechazar o clasificar como contradicción una misma `supply_identity` activa simultáneamente como pendiente y tránsito para la misma cantidad evaluada.

`movement_id` sigue siendo identidad de evento, no identidad económica/logística del suministro.

---

## 5. Hallazgo A4 — Ventana histórica delega demasiada autoridad a expected_window_days

**Severidad:** BLOQUEANTE.

`expected_window_days` suministrado libremente por el caller podría hacer pasar como completa una ventana que no corresponde a la política vigente.

Además, M01 no autoriza asumir meses naturales concretos.

### Corrección requerida

No derivar meses naturales ni introducir calendarios implícitos. La ventana histórica debe declarar:

- `required_period_count` procedente de configuración autorizada;
- cada `ConsumptionPeriod` debe declarar `evidenced_days`;
- número de periodos recibidos = número requerido;
- periodos no solapados y `KNOWN`;
- denominador = suma de `evidenced_days` de esos periodos completos.

La implementación no decide por sí sola cuántos días tiene un periodo empresarial.

---

## 6. Hallazgo A5 — Evidencia insuficiente para valor KNOWN

**Severidad:** BLOQUEANTE.

`NormalizedQuantity` permite conceptualmente `KNOWN` con `source_ref = null` y sin `trace_refs`.

Las autoridades M01…M10 exigen demostrabilidad/trazabilidad suficiente para considerar una entrada utilizable.

### Corrección requerida

Todo valor `KNOWN` consumido por STK debe conservar al menos una referencia trazable (`source_ref` o `trace_refs`).

Si existe un valor declarado sin soporte suficiente, el estado correcto es `NOT_EVIDENCED`.

La validación técnica no decide si una evidencia es legítima globalmente; solo impide representar como `KNOWN` una magnitud huérfana de trazabilidad.

---

## 7. Hallazgo A6 — Cobertura UNBOUNDED / NOT_APPLICABLE no tiene representación física inequívoca

**Severidad:** BLOQUEANTE.

El contrato declara:

- `coverage_state = UNBOUNDED`;
- semántica empresarial `NOT_APPLICABLE` respecto de cobertura finita.

Pero la estructura de salida no define cómo conservar ambas dimensiones sin colapsarlas.

### Corrección requerida

Usar una única semántica física inequívoca:

- `status = UNBOUNDED`;
- `coverage_days = null`;
- `reason = CONFIRMED_ZERO_DEMAND`.

No reutilizar `NOT_APPLICABLE` como segundo estado simultáneo del mismo resultado.

Esto materializa M04 sin introducir infinito numérico.

---

## 8. Hallazgo A7 — Puntos proyectados posteriores a una entrada no resuelta

**Severidad:** BLOQUEANTE.

El contrato permite conservar movimientos conocidos aunque exista un movimiento requerido no determinado, pero no especifica si los puntos posteriores pueden seguir pareciendo `KNOWN`.

Una omisión no evidenciada podría hacer que el stock posterior pareciera determinado cuando no lo es.

### Corrección requerida

Cada `ProjectionPoint` debe tener estado propio.

Desde la primera fecha que contiene un movimiento requerido no determinado, el cierre de esa fecha y todos los puntos dependientes posteriores no pueden ser `KNOWN` salvo que exista una regla autorizada que demuestre independencia.

Los movimientos conocidos se conservan para trazabilidad, pero no restauran certeza por sí solos.

---

## 9. Hallazgo A8 — Forecast debe cubrir la fecha utilizada

**Severidad:** PRECISIÓN PREVENTIVA.

Un `AuthorizedDemandForecast` tiene horizonte, pero no se exige expresamente que el cálculo que lo consume esté dentro de dicho horizonte.

### Corrección requerida

Cobertura y cualquier cálculo dependiente solo consumen un forecast cuando `evaluation_date` está dentro de su horizonte válido. Una proyección futura requiere además que el forecast/movimiento utilizado cubra la fecha correspondiente.

---

## 10. Hallazgo A9 — Recepción prevista anterior a evaluation_date

**Severidad:** PRECISIÓN PREVENTIVA.

Un pedido pendiente/en tránsito puede conservar una fecha prevista ya vencida. M06 no autoriza trasladar silenciosamente esa fecha al futuro.

### Corrección requerida

Un movimiento futuro M06 con `effective_date < evaluation_date` no puede incorporarse como entrada futura determinada. Debe requerir una fecha vigente/evidenciada o permanecer no determinado para la proyección futura.

No se realiza `roll-forward` automático.

---

## 11. Elementos expresamente considerados correctos

Audit 1 confirma que **no deben cambiarse**:

1. C0 permanece intacto.
2. `PurchaseOperation.quantity` no se convierte automáticamente en cantidad propuesta STK.
3. La tasa histórica no genera automáticamente un calendario de salidas futuras.
4. Los valores iniciales del catálogo no son defaults normativos.
5. El stock proyectado puede ser negativo.
6. M07 no vuelve a sumar M06 cuando consume M05.
7. La tasa de tolerancia debe venir tipada y no inferirse del número.
8. M08 preserva exceso original, absorbido y residual.
9. M10 no introduce heurísticas de resolución.
10. STK no produce resultados decisionales finales.

---

## 12. Resultado de Audit 1

| Área | Resultado |
|---|---|
| Autoridad | PASS |
| C0 | PASS |
| Estados de ausencia | PASS CON CORRECCIÓN A2/A5 |
| Demanda | PASS CON CORRECCIÓN A4/A8 |
| Cobertura | PASS CON CORRECCIÓN A6 |
| Proyección | REQUIERE DEPURACIÓN A1/A7/A9 |
| M06 | REQUIERE DEPURACIÓN A2/A3/A9 |
| Exceso | PASS |
| M08 | PASS CON CORRECCIÓN A2 |
| M09/M10 | PASS |
| Defaults | PASS |
| Decisión humana | PASS |

**Hallazgos bloqueantes:** 7.  
**Precisiones preventivas:** 2.  
**Dictamen:** DEPURAR y ejecutar Audit 2 antes de cerrar.
