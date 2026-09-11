# EIOS — STK Implementation Contract · Audit 2 Final v0.4

**Estado:** NO SUPERADA — DEPURACIÓN TEMPORAL FINAL REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.5  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.5 resuelve A1…A9, B1…B13, C1…C7 y D1…D4. El cruce final contra `STK_Contract_Entry_Authority`, STK-M04, STK-M05, STK-M07, `Stock_Demand_Methodological_Matrix.md` v1.1, `Especificacion_Reglas_STK_Parametros_MVP.md` y el modelo físico C0 confirma además que `R-STK-004` queda limitado a la absorción M08 de exceso M07; no se amplía por interpretación a una excepción genérica de cobertura elevada.

Persisten **3 ambigüedades temporales de implementabilidad**. No requieren política empresarial nueva: materializan la exigencia ya autorizada de que stock, demanda y movimientos sean válidos para la fecha/horizonte evaluados.

**DICTAMEN:** NO CERRAR v0.5. Aplicar una última depuración temporal y repetir Audit 2 Final.

---

## 2. E1 — Vigencia de la tasa de demanda respecto de la fecha evaluada

**Tipo:** BLOQUEANTE.

La autoridad de entrada exige que cada evaluación identifique método, fuente, versión, ventana temporal y **fecha de referencia** de la demanda. STK-M07 exige que, cuando el máximo se derive de cobertura, se utilice la demanda aplicable a la fecha de referencia del stock.

`DemandRateResult` v0.5 conserva identidad y ventana/horizonte, pero no una vigencia explícita consumible por M07 cuando `stock_reference.reference_date` es futura.

**Corrección requerida:**

- incorporar a `DemandRateResult` un intervalo explícito `applicable_from` / `applicable_to` y una referencia de autoridad/traza de esa aplicabilidad;
- forecast autorizado deriva ese intervalo de su horizonte evidenciado;
- demanda histórica solo recibe un intervalo de aplicabilidad cuando esté expresamente definido y trazado por la política/configuración que selecciona esa base; STK no presume vigencia futura de una media histórica;
- cobertura actual exige que `evaluation_date` pertenezca al intervalo;
- M07 por `COVERAGE_MAXIMUM` exige que `stock_reference.reference_date` pertenezca al intervalo de la tasa utilizada.

Ausencia de una aplicabilidad demostrable impide presentar el cálculo dependiente como `KNOWN`.

---

## 3. E2 — Fecha aplicable para todos los movimientos contribuyentes

**Tipo:** BLOQUEANTE.

v0.5 cierra explícitamente la ventana temporal para M06, pero otros `source_kind` conocidos podrían conservar una fecha fuera del horizonte y ser sumados si la implementación interpreta “fecha aplicable” de forma distinta.

**Corrección requerida:** todo `ProjectionMovement` `KNOWN` que contribuya a M05 debe cumplir:

`evaluation_date <= effective_date <= horizon_end`.

Un movimiento conocido fuera del horizonte no se incorpora silenciosamente a la proyección. Su tratamiento como fuera de alcance/no aplicable debe estar explícitamente evidenciado, no inferido mediante desplazamiento de fecha.

---

## 4. E3 — Stock actual debe pertenecer al mismo instante de evaluación

**Tipo:** BLOQUEANTE.

La autoridad empresarial define `stock_on_hand`, `stock_committed` y `stock_available` para la **misma fecha de evaluación**. v0.5 solo exige “vigencia compatible”, mientras `NormalizedQuantity.effective_date` puede ser nula.

**Corrección requerida para v0.1:** para producir `StockAvailabilityResult.state = KNOWN`:

- `stock_on_hand.effective_date == context.evaluation_date`;
- `stock_committed.effective_date == context.evaluation_date`;
- artículo y unidad coinciden;
- ambas magnitudes están evidenciadas y trazadas.

STK v0.1 no inventa una regla de tolerancia de antigüedad ni considera vigente un snapshot de otra fecha por inferencia. Si una futura política autoriza semántica `as-of` distinta, deberá extender el contrato de forma explícita.

---

## 5. Verificación transversal R-STK-004

**Resultado:** SIN BLOQUEO.

La matriz STK especializada v1.1 define `R-STK-004` como pedido confirmado que absorbe total/parcialmente exceso y declara M08 como su base metodológica. La especificación especializada STK/PYE confirma que la regla depende de demanda comercial confirmada y absorción M08, sin parámetro directo.

Por tanto:

- no se amplía M08 a cobertura elevada;
- no se modifica la Matriz de Reglas desde el contrato técnico;
- la discrepancia de redacción más amplia en una vista general no autoriza alcance adicional frente a la autoridad especializada cerrada.

---

## 6. Resultado

- A1…A9: resueltos.
- B1…B13: resueltos.
- C1…C7: resueltos.
- D1…D4: resueltos.
- E1…E3: abiertos en v0.5.
- Frontera R-STK-004: verificada sin ampliación de alcance.

**Siguiente paso:** DEPURACIÓN TEMPORAL FINAL → Audit 2 Final independiente.
