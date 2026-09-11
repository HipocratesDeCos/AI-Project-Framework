# EIOS — STK Implementation Contract · Audit 2 Final v0.9

**Estado:** NO SUPERADA — DEPURACIÓN FINAL DE COMPLETITUD REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.10  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.10 resuelve I1…I3 y conserva resueltos A…H. La revisión completa M01…M10 contra la matriz metodológica, autoridades M02/M03/M07/M08, C0, Centro de Parametrización y RDM detecta **4 huecos físicos restantes**.

Ninguno crea una nueva fórmula, regla o política empresarial. Los cuatro son cierres de representación, vigencia o no doble uso.

**DICTAMEN:** NO CERRAR v0.10. Resolver J1…J4 y repetir Audit 2 Final.

---

## 2. J1 — M02/M03 están metodológicamente cerrados pero no son representables

**Tipo:** BLOQUEANTE DE COMPLETITUD.

La v0.10 acierta al no calcular `stock_minimum` ni `safety_stock`, porque no existe fórmula cuantitativa autorizada. Sin embargo, el contrato tampoco define cómo representar un valor ya autorizado externamente.

M02/M03 exigen que todo valor vigente conserve, como mínimo, artículo, cantidad/unidad, política o método, versión, fecha/vigencia, fuentes y trazabilidad. Omitir por completo esta frontera impide materializar M02/M03 sin inventar posteriormente un tipo ad hoc.

**Corrección requerida:** introducir un contenedor no calculador, equivalente a:

```text
AuthorizedStockPolicyQuantity
├── concept: STOCK_MINIMUM | SAFETY_STOCK
├── article_id: str
├── quantity: Decimal | null
├── unit: str
├── state: StockDataState
├── policy_ref: str
├── policy_version: str
├── valid_from: date
├── valid_to: date | null
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

- no contiene fórmula ni recalcula el valor;
- `KNOWN` exige cantidad finita no negativa, unidad base compatible, política/versión/fuente y vigencia demostrables;
- el consumidor solo puede usarlo si `valid_from <= reference_date <= valid_to` cuando exista `valid_to`;
- ausencia/insuficiencia → `UNKNOWN / NOT_EVIDENCED`, nunca cero;
- `STOCK_MINIMUM` y `SAFETY_STOCK` no son equivalentes y no se componen implícitamente;
- el contenedor no crea consumidor de regla ni valida `STK-001/002` como valores definitivos.

---

## 3. J2 — Umbrales directos M07 no conservan versión de autoridad

**Tipo:** BLOQUEANTE.

`AuthorizedQuantityThreshold` conserva fuente y fecha aplicable, pero M07 exige un máximo/tolerancia explícitos, trazables, **versionados** y autorizados. Un `source_ref` no demuestra por sí mismo qué versión de política produjo el valor.

**Corrección requerida:** añadir al umbral:

```text
authority_ref: str
authority_version: str
```

Un umbral `KNOWN` exige ambos valores no vacíos. Esto no convierte el umbral en parámetro ni crea una nueva autoridad; conserva la versión de la autoridad ya aplicada.

---

## 4. J3 — M08 no puede corregir retroactivamente una referencia proyectada

**Tipo:** BLOQUEANTE.

Para una referencia M07 proyectada en fecha `excess_reference_date`, una demanda confirmada cuya entrega esperada sea anterior o igual a esa fecha debería haber formado parte de la composición/proyección M05 cuando fuese conocida y aplicable. Permitir que M08 la use después como mitigación puede ocultar una proyección incompleta o duplicar una salida temporalmente anterior.

Además, v0.1 no posee cutoff intradía.

**Corrección requerida:** para `APLICABLE_Y_VALIDADA`:

```text
expected_delivery_date > allocation_scope.excess_reference_date
expected_delivery_date <= allocation_scope.horizon_end
```

La desigualdad es estricta por ausencia de orden intradía. Para referencia actual, `excess_reference_date == evaluation_date`, por lo que una entrega del mismo día tampoco se incorpora por inferencia.

Una demanda con entrega `<= excess_reference_date` no puede utilizarse como excepción M08 sobre ese exceso. Si debía afectar a una referencia proyectada, su lugar era M05; su ausencia allí debe permanecer visible, no corregirse ex post mediante M08.

---

## 5. J4 — Ledger M08 debe ser un snapshot activo, único y fechado

**Tipo:** BLOQUEANTE.

La v0.10 conserva procedencia del ledger, pero no impide dos problemas:

1. el mismo registro de asignación puede aparecer duplicado y descontarse dos veces;
2. una asignación histórica ya consumida/liberada por cambios posteriores del pedido podría seguir restándose del `pending_quantity` actual.

M08 exige la cantidad pendiente **en la fecha evaluada** y nuevas evaluaciones ante cambios/cancelaciones/parcialidades.

**Corrección requerida:** representar la entrada como snapshot activo:

```text
AllocationLedgerSnapshot
├── reference_date: date
├── entries: tuple[AllocationLedgerEntry, ...]
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Cada `AllocationLedgerEntry` incorpora además:

```text
allocation_entry_id: str
```

Reglas:

- `snapshot.reference_date == allocation_scope.evaluation_date`;
- el snapshot contiene únicamente asignaciones **activas** que todavía reservan cantidad pendiente contra reutilización en esa fecha;
- histórico liberado/consumido se preserva en trazabilidad aguas arriba, no se suma como activo;
- `allocation_entry_id` es único;
- duplicados no se agregan;
- cada entry conserva decisión, escenario, fecha de exceso y referencia del resultado original;
- la suma activa por pedido se utiliza para `already_allocated`.

STK sigue siendo operación pura: consume el snapshot; no implementa persistencia ni decide cuándo una asignación histórica se libera.

---

## 6. Verificaciones transversales

- R-STK-001…004: sin cambios.
- RDM: no se crean dependencias nuevas por similitud nominal.
- M02/M03: se representan valores autorizados, no se inventan fórmulas ni consumidores.
- M07: versión de autoridad preservada.
- M08: no reescribe M07 ni corrige silenciosamente M05.
- C0: sin modificación.
- Centro de Parametrización: sigue resolviendo vigencia de parámetros; STK no lo duplica.
- Autoridad decisional humana: preservada.

---

## 7. Resultado

- A…I: resueltos.
- J1…J4: abiertos en v0.10.

**Siguiente paso:** DEPURAR v0.11 → Audit 2 Final independiente.
