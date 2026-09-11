# EIOS — STK Implementation Contract · Audit 2 Final v0.8

**Estado:** NO SUPERADA — DEPURACIÓN DE COMPOSICIÓN DE OPENING/M08 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.9  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.9 resuelve H1…H2 y todos los hallazgos anteriores. La revisión contra la semántica cerrada de `stock_committed` y STK-M08 detecta tres omisiones físicas finales vinculadas a composición y vigencia.

**DICTAMEN:** NO CERRAR v0.9. Resolver I1…I3 y repetir Audit 2 Final.

---

## 2. I1 — Demanda confirmada ya incorporada en `stock_committed`

**Tipo:** BLOQUEANTE.

La autoridad de entrada define `stock_committed` como parte del stock físico reservada/asignada a obligaciones existentes. Un pedido confirmado no se convierte automáticamente en compromiso, pero sí puede formar parte de él cuando existe una reserva/asignación física evidenciada.

Si M07 parte de `stock_available`, esa cantidad comprometida ya ha sido descontada. M08 no puede volver a utilizar la misma cantidad como absorción del exceso.

v0.9 controla M05↔M08, pero no opening/`stock_committed`↔M08.

**Corrección requerida:** materializar la composición evidenciada de `stock_committed` mediante estructura equivalente a:

```text
StockCommitmentComponent
├── commitment_id: str
├── demand_segment_id: str | null
├── confirmed_demand_id: str | null
├── article_id: str
├── quantity: Decimal
├── unit: str
├── effective_date: date
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

- componentes KNOWN son finitos, no negativos, del mismo artículo/unidad/fecha que el compromiso agregado;
- `commitment_id` es único;
- si el compromiso se vincula a demanda comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios y trazables;
- el mismo `demand_segment_id` no puede aparecer dos veces;
- la suma de componentes debe ser exactamente `stock_committed.value` para poder afirmar composición completa;
- `StockAvailabilityResult` conserva la cantidad de demanda confirmada ya incorporada en opening, agregada por `confirmed_demand_id`.

La composición no convierte todo pedido confirmado en stock comprometido: solo registra reservas/asignaciones físicas ya evidenciadas.

---

## 3. I2 — Segmento de demanda entre opening y M05

**Tipo:** BLOQUEANTE.

Una misma demanda confirmada puede tener una parte ya reservada en opening y otra parte futura todavía no incorporada. El ID de pedido por sí solo no permite distinguir segmentos y prohibiría parcialidades legítimas; permitirlo sin identidad de segmento permitiría doble contabilización.

**Corrección requerida:**

- `ProjectionMovement` de `AUTHORIZED_DEMAND` confirmado incorpora `demand_segment_id` además de `confirmed_demand_id`;
- `demand_segment_id` es estable y trazable para la cantidad concreta representada;
- ningún segmento puede existir simultáneamente en la composición del opening y como movimiento futuro M05;
- distintos segmentos del mismo `confirmed_demand_id` pueden existir si están explícitamente identificados;
- la composición acumulada para M08 continúa agregándose cuantitativamente por `confirmed_demand_id`.

Esto evita doble conteo sin prohibir entregas/parcialidades legítimas.

---

## 4. I3 — Vigencia y trazabilidad de cantidad pendiente / ledger M08

**Tipo:** BLOQUEANTE.

STK-M08 exige que la cantidad aplicable sea la que permanece pendiente de servir **en la fecha evaluada** y que cada asignación conserve Pedido_ID, cantidad aplicada y escenario de exceso.

v0.9 no exige que `pending_quantity.effective_date` coincida con `evaluation_date`; además, un `AllocationLedgerEntry` puede quedar separado del escenario/exceso que originó la asignación.

**Corrección requerida:**

Para un registro `APLICABLE_Y_VALIDADA`:

```text
pending_quantity.effective_date == allocation_scope.evaluation_date
order_date <= confirmation_date <= allocation_scope.evaluation_date
```

La fecha prevista de entrega debe estar evidenciada y ser aplicable al horizonte. Una fecha prevista ya vencida sin evidencia vigente de actualización no se reutiliza silenciosamente como entrega futura.

Cada ledger entry debe conservar, directa o mediante referencia inmutable:

- `confirmed_demand_id`;
- cantidad y unidad asignadas;
- `decision_id`;
- `scenario_id`;
- fecha de referencia del exceso;
- referencia del resultado/asignación original;
- trazas.

El ledger puede agregarse para impedir reutilización entre excesos, pero no puede perder el escenario de procedencia exigido por M08.

---

## 5. Resultado

- A…H: resueltos.
- I1…I3: abiertos en v0.9.

**Siguiente paso:** DEPURAR v0.10 → Audit 2 Final independiente.
