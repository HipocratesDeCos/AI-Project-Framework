# EIOS — STK Implementation Contract · Audit 2 Final v0.10

**Estado:** NO SUPERADA — DEPURACIÓN FINAL DE ESTADOS Y PYE REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.11  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.11 resuelve J1…J4 y conserva resueltos A…I. La auditoría completa vuelve a recorrer M01…M10, autoridad de entrada, C0, Centro de Parametrización, catálogo PYE, especificación STK/PYE↔reglas y fronteras M05/M06/M08/M09.

Persisten **4 bloqueos técnicos**. Ninguno requiere nueva política empresarial, fórmula ni valor. Los cuatro impiden que la implementación pueda preservar literalmente ausencia ≠ cero, autoridad del horizonte y la frontera de parámetros PYE.

**DICTAMEN:** NO CERRAR v0.11. Resolver K1…K4 y repetir Audit 2 Final desde cero.

---

## 2. K1 — Estados no determinados deben ser físicamente representables

**Tipo:** BLOQUEANTE M09 / IMPLEMENTABILIDAD.

El contrato declara correctamente `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA`, pero varias estructuras mantienen obligatorios precisamente los campos que pueden faltar cuando se produce ese estado. Una implementación literal se vería forzada a inventar referencias, versiones, fechas o cantidades para construir el objeto.

Afecta como mínimo a:

- `AuthorizedStockPolicyQuantity`: `quantity`, `policy_ref`, `policy_version`, `valid_from`, `source_ref`;
- `AuthorizedQuantityThreshold`: `value`, `authority_ref`, `authority_version`, `source_ref`;
- `ConfiguredParameterValue`: `value`, `configuration_ref`, `source_ref`;
- `ConsumptionPeriod`: cantidad/evidencia cuando el periodo requerido existe pero no está evidenciado;
- `ProjectionMovement`: cantidad o fecha cuando el movimiento existe pero carece de evidencia suficiente;
- `ConfirmedDemandRecord`: cantidad/fechas/evidencia cuando el pedido resulta `NO_VERIFICABLE`.

**Corrección requerida:**

1. los campos cuyo dato empresarial puede faltar deben ser opcionales físicamente;
2. `KNOWN` o `APLICABLE_Y_VALIDADA` exige todos los campos requeridos por su autoridad;
3. estados no determinados no pueden rellenar dichos campos con cero, fechas sintéticas, IDs ficticios ni defaults;
4. identificadores de contexto que sí se conocen por construcción —artículo, parámetro esperado, fecha objetivo de consumo— pueden seguir siendo obligatorios;
5. cada tipo debe declarar su invariante `state ↔ payload` para impedir tanto ausencia disfrazada de dato como dato cuantitativo presentado bajo estado no determinado.

---

## 3. K2 — Ledger M08 ausente no puede equivaler a ledger vacío

**Tipo:** BLOQUEANTE M08/M09.

`AllocationLedgerSnapshot` v0.11 tiene fecha, entries y fuente, pero no estado de evidencia. Por tanto una implementación podría construir `entries=()` cuando el ledger no fue recuperado y tratar la ausencia como “ninguna asignación activa”. Eso permitiría reutilizar cantidades ya asignadas.

**Corrección requerida:**

`AllocationLedgerSnapshot` debe conservar un estado explícito, al menos:

```text
KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

Reglas:

- solo `KNOWN + entries=()` y trazabilidad suficiente significa “cero asignaciones activas evidenciadas”;
- `state != KNOWN` no autoriza suma cero ni absorción M08 determinada;
- `source_ref` puede ser nula cuando precisamente falta la evidencia, sin inventar referencia;
- `KNOWN` exige `reference_date == evaluation_date`, fuente/traza y unicidad de `allocation_entry_id`;
- el estado no crea persistencia propia ni una política de liberación; STK consume el snapshot aguas arriba.

---

## 4. K3 — El horizonte M05 no puede ser un valor arbitrario al margen de `P-PYE-001`

**Tipo:** BLOQUEANTE DE AUTORIDAD/PARAMETRIZACIÓN.

STK-M05 exige horizonte explícito, documentado, versionado y con fecha efectiva. La especificación STK/PYE cerrada determina además que `P-PYE-001` **configura M05**, aunque no sea consumidor directo de una regla.

v0.11 conserva `horizon_end`, fuente y trazas, pero no exige que el horizonte v0.1 derive de una configuración efectiva de `P-PYE-001`. Esto permitiría que un llamador suministrase cualquier fecha final sin autoridad parametrizada.

**Corrección requerida para v0.1:**

- introducir una frontera `ProjectionHorizon` o equivalente que consuma `ConfiguredParameterValue(P-PYE-001)`;
- el parámetro debe ser `KNOWN`, versión/fecha efectiva correctas, entero positivo no booleano y unidad `días` autorizada/normalizada;
- `horizon_end = evaluation_date + horizon_days` en días naturales; los movimientos contribuyentes siguen cumpliendo `evaluation_date < effective_date <= horizon_end`;
- el valor inicial 90 no es fallback ni default;
- ausencia/no evidencia del parámetro impide presentar una proyección completa como `KNOWN`;
- la granularidad diaria queda identificada por `methodology_version`; STK no crea una segunda política temporal.

---

## 5. K4 — Frontera operativa explícita para `P-PYE-002…006`

**Tipo:** BLOQUEANTE DE AMBIGÜEDAD CONTRACTUAL.

La especificación autorizada clasifica:

- `P-PYE-002/003` como **control metodológico potencial** de M05/M06;
- `P-PYE-004` como control temporal potencial ligado a `lead_time`;
- `P-PYE-005` como no operativo para ventas→demanda sin política posterior;
- `P-PYE-006` sin consumidor directo demostrado para R-STK-001.

v0.11 prohíbe usar sus valores iniciales como defaults, pero no declara si la implementación v0.1 debe consumirlos o ignorarlos. Dos implementaciones compatibles con el texto podrían producir resultados distintos.

**Corrección requerida:** cerrar explícitamente la frontera v0.1 sin inventar semántica:

- `P-PYE-002/003`: **no operativos como gates configurables en v0.1**. M06 determina elegibilidad por evidencia/estado/temporalidad; sus valores iniciales no incluyen ni excluyen movimientos. Una futura activación como controles requiere autoridad contractual adicional;
- `P-PYE-004`: no operativo en v0.1 porque el motor no deriva fechas desde `lead_time`; consume `effective_date` evidenciada;
- `P-PYE-005`: no operativo para transformación ventas→demanda;
- `P-PYE-006`: no operativo como umbral de R-STK-001;
- `P-PYE-001`: sí operativo exclusivamente como configuración del horizonte conforme a K3.

Esto no elimina parámetros del catálogo ni niega su posible función futura; impide comportamiento divergente mientras dicha función no está autorizada con suficiente precisión.

---

## 6. Verificaciones sin nuevo bloqueo

- M02/M03: representación pasiva correcta una vez resuelto K1.
- M04: cero confirmado sigue produciendo `UNBOUNDED / NOT_APPLICABLE` sin infinito numérico.
- M05/M06: cutoff diario estricto y supply identity permanecen correctos.
- M07: máximo/tolerancia conservan versión y fecha aplicable.
- M08: composición opening→M05→M08 y no prioridad siguen correctas; K2 refuerza ausencia del ledger.
- M10: no resolución heurística.
- C0: no se modifica.
- Rules/CRC/MED: sin transferencia de autoridad.
- Autoridad humana: preservada.

---

## 7. Resultado

- A…J: resueltos.
- K1…K4: abiertos en v0.11.

**Siguiente paso:** DEPURAR v0.12 → repetir Audit 2 Final completa.