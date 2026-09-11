# EIOS — STK Implementation Contract · Audit 2 Final v0.15

**Estado:** NO SUPERADA — DEPURACIÓN P1 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.16  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.16 resuelve O1…O5 y conserva resueltos A…N. La auditoría final no detecta nuevos bloqueos en estados, identidad, parámetros, temporalidad, M06, M07, M08, M09 o M10.

Permanece **un único bloqueo de frontera M05**: la autoridad de entrada declara una política de demanda admisible para cobertura y proyección, pero no existe autoridad que permita calendarizar automáticamente la tasa de demanda ni reconciliarla implícitamente con pedidos confirmados.

Este bloqueo **no requiere una nueva decisión empresarial para cerrar el contrato** si la implementación conserva la transformación/reconciliación como entrada autorizada y se niega a inventarla.

**DICTAMEN:** NO CERRAR v0.16. Resolver P1 contractualmente y repetir Audit 2 Final.

---

## 2. P1 — Demanda seleccionada para proyección no puede ignorarse ni calendarizarse implícitamente

**Tipo:** BLOQUEANTE M05 / AUTORIDAD DE DEMANDA.

Fuentes de autoridad:

- `STK_Contract_Entry_Authority.md` cierra una política de demanda **para cobertura y proyección STK**;
- M05 autoriza salidas desde demanda, consumo, reservas u otras necesidades, pero exige fuente, método, ventana, fecha y **transformación**;
- no existe en la autoridad vigente una regla que permita convertir `daily_demand` en una serie de salidas diarias por simple multiplicación/repetición;
- tampoco existe una política que determine si una demanda confirmada de cliente está ya incluida o no en una previsión/base histórica, por lo que sumarla automáticamente puede duplicar demanda.

v0.16 declara correctamente que una tasa no crea calendario, pero después permite una proyección `KNOWN` basada únicamente en movimientos explícitos sin demostrar que la demanda seleccionada haya sido tratada. Eso puede presentar como completa una proyección que silenciosamente omitió la demanda.

### Corrección requerida

Introducir una frontera de entrada equivalente a:

```text
DemandProjectionSchedule
├── selection: DemandMethodSelection
├── demand: DemandRateResult
├── state: StockDataState
├── schedule_from: date
├── schedule_to: date
├── demand_movement_ids: tuple[str, ...]
├── transformation_ref: str | null
├── reconciliation_ref: str | null
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Para `KNOWN`:

1. `selection == context.demand_selection` y ambas son `KNOWN`;
2. `demand` es `KNOWN`, usa la misma selección, ámbito/artículo/unidad/versiones y es aplicable al horizonte correspondiente;
3. `schedule_from == evaluation_date + 1`;
4. `schedule_to == ProjectionHorizon.horizon_end`;
5. `transformation_ref` identifica una transformación externa/autorizada y trazable que materializa la demanda seleccionada como movimientos fechados; STK no inventa esa transformación;
6. `reconciliation_ref` demuestra cómo se ha evitado doble contabilización entre demanda calendarizada y demanda comercial confirmada/reservas explícitas;
7. `demand_movement_ids` es único y corresponde exactamente a los movimientos de demanda incluidos bajo dicha reconciliación;
8. fuente/trazas suficientes.

### Separación semántica de movimientos

El contrato debe distinguir:

- `AUTHORIZED_DEMAND`: movimiento de demanda no confirmado comercialmente, materializado mediante una transformación autorizada del método seleccionado;
- `CONFIRMED_DEMAND`: pedido comercial confirmado, con `confirmed_demand_id + demand_segment_id`, utilizado también para trazabilidad M08.

La composición `incorporated_confirmed_demand` acumula exclusivamente `CONFIRMED_DEMAND`, no demanda genérica.

### Gate de completitud M05

Una proyección completa `KNOWN` exige `DemandProjectionSchedule.state == KNOWN` y correspondencia exacta entre el schedule y los movimientos de demanda de la proyección.

Si la selección de demanda es conocida pero falta transformación/reconciliación autorizada:

- STK no repite la tasa por día;
- STK no omite silenciosamente la demanda;
- la proyección dependiente queda `UNKNOWN / NOT_EVIDENCED` conforme a M09.

Esto permite implementar el contrato sin decidir ahora una política de calendarización que todavía no existe.

---

## 3. Verificaciones sin nuevo bloqueo

- O1: selección de demanda autorizada/versionada — resuelta.
- O2: IDs M08 aportados por plan — resuelta.
- O3: composición exacta opening→M05→M07 — resuelta.
- O4: reconciliación de obligaciones opening↔M05 — resuelta.
- O5: saldo absorbible cero → NO_APLICABLE — resuelta.
- M09/M10 — preservados.
- C0/Parametrización/Rules/CRC/MED — fronteras intactas.

---

## 4. Resultado

- A…O: resueltos.
- P1: abierto en v0.16.

**Siguiente paso:** DEPURAR v0.17 → repetir Audit 2 Final completa.