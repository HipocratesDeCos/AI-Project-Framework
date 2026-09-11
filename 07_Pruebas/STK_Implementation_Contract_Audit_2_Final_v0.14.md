# EIOS — STK Implementation Contract · Audit 2 Final v0.14

**Estado:** NO SUPERADA — DEPURACIÓN O1…O5 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.15  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.15 resuelve N1…N5 y conserva resueltos A…M. El cruce final contra `STK_Contract_Entry_Authority.md`, M05/M08 y el requisito de determinismo detecta **5 bloqueos técnicos**.

Ninguno requiere nueva decisión empresarial.

**DICTAMEN:** NO CERRAR v0.15. Resolver O1…O5 y repetir Audit 2 Final completa.

---

## 2. O1 — La selección del método de demanda debe ser autoridad explícita y registrada

**Tipo:** BLOQUEANTE DE AUTORIDAD / REPRODUCIBILIDAD.

La autoridad empresarial aprobada exige que cada evaluación identifique explícitamente qué método de demanda utiliza y que la selección entre forecast autorizado y base histórica esté declarada por política/configuración vigente y quede registrada con la evaluación.

v0.15 contiene ambos métodos y reglas de `forecast_version`, pero no una entrada que demuestre **quién autorizó la selección del método**. El llamador podría escoger libremente qué función invocar.

**Corrección requerida:** introducir una estructura equivalente a:

```text
DemandMethodSelection
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST | null
├── state: StockDataState
├── policy_ref: str | null
├── policy_version: str | null
├── applicable_reference_date: date
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

`KNOWN` exige método, política/versionado, fuente/traza y fecha aplicable igual a `evaluation_date`.

`StockComputationContext` incorpora `demand_selection`; `DemandRateResult.method` debe coincidir exactamente. Histórico exige `forecast_version == null`; forecast exige versión no nula. Si la selección no es demostrable, el motor no elige ni hace fallback: el resultado de demanda queda no determinado.

La identidad/traza STK debe impedir mezclar resultados de selecciones diferentes; puede conservar una `demand_selection_ref`/versión estable en `StockResultIdentity` o exigir afinidad explícita equivalente.

---

## 3. O2 — El motor no puede inventar IDs del ledger M08

**Tipo:** BLOQUEANTE DE DETERMINISMO / TRAZABILIDAD.

`resulting_ledger` debe añadir nuevas `AllocationLedgerEntry` con `allocation_entry_id` y `allocation_result_ref`, pero el plan v0.15 no proporciona esos valores. Si el motor genera UUIDs o referencias internas, la misma entrada puede producir salidas distintas y no queda demostrada la procedencia exigida por M08.

**Corrección requerida:** cada `DemandAllocation` aporta:

```text
allocation_entry_id: str
allocation_source_ref: str
```

- `allocation_entry_id` es único en el plan y no colisiona con el ledger activo;
- el nuevo ledger reutiliza exactamente ese ID;
- `AllocationLedgerEntry.allocation_result_ref == DemandAllocation.allocation_source_ref` o una relación contractual equivalente explícita;
- el motor no genera IDs aleatorios ni referencias de procedencia;
- decisión, escenario y fecha de exceso se derivan de `AllocationScope/StockResultIdentity`.

---

## 4. O3 — La composición anti-doble-conteo debe ser igualdad exacta a través de la cadena

**Tipo:** BLOQUEANTE OPENING→M05→M07→M08.

v0.15 conserva composición, pero no cierra todas las igualdades de derivación. M08 depende cuantitativamente de ellas.

**Corrección requerida:**

1. `StockAvailabilityResult.incorporated_confirmed_demand` es **exactamente** la agregación de `committed_components` que tengan `confirmed_demand_id + demand_segment_id`, sumada por pedido y preservando el conjunto exacto de segmentos.
2. En cada `ProjectionPoint`, la composición es exactamente la del opening más los movimientos `AUTHORIZED_DEMAND` confirmados contabilizados hasta esa fecha; ningún segmento se duplica.
3. `StockProjectionResult.incorporated_confirmed_demand_at_horizon` coincide exactamente con el último punto del horizonte.
4. `StockReferenceValue` copia exactamente la composición de availability o del punto origen.
5. `ExcessResult.incorporated_confirmed_demand == stock_reference.incorporated_confirmed_demand`.

No se permite al llamador suministrar manualmente una composición diferente de la derivada.

---

## 5. O4 — Reconciliación de `OTHER_AUTHORIZED_NEED` con opening debe ser físicamente demostrable

**Tipo:** BLOQUEANTE DE DOBLE CONTEO.

v0.15 indica que `OTHER_AUTHORIZED_NEED` debe demostrar no duplicación con `stock_committed`, pero el modelo no conserva una referencia específica a esa comprobación cuando no existe `commitment_id`. El validador no puede diferenciar “necesidad nueva” de “obligación ya descontada” solo por texto.

**Corrección requerida:** añadir a `ProjectionMovement` una referencia equivalente a:

```text
opening_reconciliation_ref: str | null
```

Para `RESERVATION` y `OTHER_AUTHORIZED_NEED` `KNOWN`, la referencia es obligatoria y demuestra el cruce contra la composición de opening.

- `RESERVATION` exige además `commitment_id`.
- Si `OTHER_AUTHORIZED_NEED` corresponde a una obligación identificable, conserva su `commitment_id`; si ese ID ya está en opening, no contribuye otra vez.
- Si es una necesidad nueva sin compromiso previo, la referencia demuestra esa no pertenencia; STK no la deduce por ausencia de ID.

---

## 6. O5 — Cero saldo absorbible M08 es `NO_APLICABLE`, no absorción validada

**Tipo:** BLOQUEANTE DE ESTADO EMPRESARIAL.

Tras descontar opening/M05/ledger puede existir un pedido inicialmente válido pero con `remaining_allocatable == 0`. M08 define `NO_APLICABLE` cuando no queda cantidad pendiente aplicable.

**Corrección requerida:**

- si `ExcessResult.state == EXCESS` pero `total_remaining_applicable == 0`, resultado `NO_APLICABLE`, `absorbed_excess = 0`, `residual_excess = excess_quantity`, plan vacío;
- `APLICABLE_Y_VALIDADA` exige `total_remaining_applicable > 0` y, dado exceso positivo, `absorbed_excess > 0`;
- no se crean nuevas entries de ledger para absorción cero.

---

## 7. Verificaciones sin nuevo bloqueo

- N1…N5: resueltos en v0.15.
- Historical policy puede expresar ausencia sin referencias sintéticas.
- Forecast `KNOWN` tiene intervalo cerrado.
- Reservations de opening están materializadas y disponibles para reconciliación.
- Ledger resultante preserva entradas activas previas.
- M09/M10 incidencias siguen trazables.
- C0/Parametrización/Rules/CRC/MED: fronteras intactas.

---

## 8. Resultado

- A…N: resueltos.
- O1…O5: abiertos en v0.15.

**Siguiente paso:** DEPURAR v0.16 → repetir Audit 2 Final completa.