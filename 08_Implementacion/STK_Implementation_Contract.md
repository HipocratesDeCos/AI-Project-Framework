# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.1  
**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA  
**Baseline:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Ubicación:** `08_Implementacion/STK_Implementation_Contract.md`

---

## 2. Propósito

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**.

Materializa exclusivamente semántica, relaciones y cálculos previamente autorizados. No crea:

- reglas empresariales nuevas;
- parámetros empresariales nuevos;
- valores por defecto normativos;
- forecasting implícito;
- una autoridad paralela de evidencia;
- una nueva identidad decisional;
- una decisión automática de compra, reposición, cancelación o reducción de stock.

La implementación ejecutable permanece bloqueada hasta que este contrato supere:

`DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR`.

---

## 3. Posición arquitectónica

```text
Quality & Trust / evidencia válida
        ↓
Price Intelligence
        ↓
TCO
        ↓
STOCK / DEMANDA (STK)
        ↓
Finanzas / Proveedor / Riesgo
        ↓
Viability Frontier
        ↓
...
        ↓
CRC
        ↓
DECISIÓN HUMANA
```

STK produce **resultados analíticos y evidencia operativa**. No consolida la decisión y no sustituye al Motor de Reglas, CRC, MED o decisor autorizado.

---

## 4. Frontera con C0

STK reutiliza `DecisionContext` y las identidades canónicas existentes. No modifica:

- `InputContract` / `PurchaseOperation`;
- `DecisionContext`;
- `Evidence`;
- `EvidenceValidation`;
- `Rule`;
- `Assessment`;
- `Trace`.

`PurchaseOperation.quantity` **no se considera automáticamente `proposed_quantity` normalizada**, porque C0 no contiene la unidad base objetivo de la cantidad.

Cuando STK deba evaluar el impacto de una cantidad propuesta, recibirá una magnitud especializada normalizada y trazable mediante su propio contrato de entrada, sin añadir campos a C0.

---

## 5. Identidad temporal

La identidad temporal canónica de STK es:

`evaluation_date`

Las referencias metodológicas previas a `as_of_date` se mapean a `evaluation_date`.

Reglas:

1. no existe una segunda fecha de evaluación paralela;
2. todo stock actual, compromiso, demanda, movimiento y parámetro consumido debe ser válido para `evaluation_date` o declarar su propia fecha/horizonte;
3. una proyección puede contener fechas futuras, pero su origen de evaluación sigue siendo `evaluation_date`;
4. un resultado debe conservar la fecha de evaluación con la que fue calculado.

---

## 6. Paquete físico previsto

La materialización técnica deberá residir fuera de C0, en un paquete especializado equivalente a:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

Los nombres físicos finales podrán ajustarse durante la implementación si no cambian la semántica ni la frontera definida por este contrato.

STK debe poder importarse sin crear dependencias circulares con `eios.core`.

---

## 7. Estados STK de dato

Para representar la semántica de M01/M09/M10, los valores especializados STK utilizan un estado explícito:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

Significado:

- `KNOWN`: existe valor utilizable y suficientemente evidenciado para el cálculo correspondiente;
- `UNKNOWN`: el valor no puede determinarse;
- `NOT_EVIDENCED`: existe un valor declarado, pero carece de evidencia suficiente;
- `NOT_APPLICABLE`: existe evidencia de que la magnitud no aplica al caso;
- `CONFLICTING_DATA`: existen fuentes materialmente incompatibles y no resueltas.

Estos estados son especializados del dominio STK. No redefinen `Evidence.state`, `EvidenceValidation.status` ni `Assessment.status` de C0.

### 7.1 Invariante de valor

Un estado distinto de `KNOWN` no puede presentar un valor numérico como si fuera determinado para un cálculo dependiente.

`UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.

`NOT_APPLICABLE` tampoco se utiliza como cero salvo que una metodología concreta autorice un resultado específico, como el tratamiento de cobertura con demanda cero confirmada.

---

## 8. Magnitud cuantitativa normalizada

La interfaz técnica base será equivalente a:

```text
NormalizedQuantity
├── article_id: str
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── source_ref: str | null
├── effective_date: date | null
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `value` debe ser finito;
2. una cantidad física conocida no puede ser negativa;
3. `unit` identifica la unidad base normalizada del artículo;
4. las operaciones entre cantidades exigen mismo `article_id` y misma `unit`;
5. `state != KNOWN` implica `value = null` para la magnitud no determinada;
6. una conversión de unidad se realiza aguas arriba o mediante una transformación explícitamente autorizada; STK v0.1 no inventa factores de conversión.

---

## 9. Contexto técnico STK

La entrada común a los cálculos utiliza una estructura equivalente a:

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

`forecast_version` es obligatorio cuando la demanda consumida proviene de una previsión externa/autorizada.

`parameters_version` y `data_snapshot_id` se reutilizan desde `DecisionContext`; STK no crea sustitutos.

---

## 10. Disponibilidad de stock — M02 / autoridad de entrada

### 10.1 Entrada

```text
StockAvailabilityInput
├── context: StockComputationContext
├── stock_on_hand: NormalizedQuantity
└── stock_committed: NormalizedQuantity
```

### 10.2 Precondiciones

- mismo artículo;
- misma unidad base;
- valores vigentes para `evaluation_date`;
- ambos estados `KNOWN` para obtener un valor numérico determinado.

### 10.3 Cálculo autorizado

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

### 10.4 Salida

```text
StockAvailabilityResult
├── stock_on_hand
├── stock_committed
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── state: StockDataState
└── trace_refs
```

Si una entrada requerida no es `KNOWN`, STK no produce un `stock_available` numérico completo. El estado dependiente conserva la incertidumbre o contradicción aplicable.

Un déficit no se oculta mediante el suelo cero aplicado a `stock_available`.

---

## 11. Consumo histórico — M01

STK puede recibir consumos mensuales ya normalizados:

```text
ConsumptionPeriod
├── article_id
├── period_start: date
├── period_end: date
├── quantity: Decimal | null
├── unit
├── state: StockDataState
├── source_ref
└── trace_refs
```

Reglas:

- representa consumo real, no ventas ni forecast;
- los periodos no se solapan dentro de una misma serie de cálculo;
- la ausencia no se interpreta como consumo cero;
- un cero solo es `KNOWN` cuando está explícitamente evidenciado;
- una serie utilizada para una ventana histórica debe cumplir exactamente la ventana requerida por la política vigente.

STK v0.1 no decide qué registros empresariales equivalen a consumo real; consume datos ya identificados conforme a M01.

---

## 12. Demanda — autoridad de entrada

### 12.1 Métodos físicos permitidos

```text
AUTHORIZED_FORECAST
HISTORICAL_CONSUMPTION
```

No se permiten otros métodos en v0.1 sin extensión contractual.

### 12.2 Demanda histórica

Entrada equivalente:

```text
HistoricalDemandInput
├── context
├── periods: tuple[ConsumptionPeriod, ...]
├── window_start: date
├── window_end: date
└── expected_window_days: int
```

Cálculo:

```text
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

Precondiciones:

1. la ventana está explícita;
2. todos los periodos requeridos están presentes y evidenciados;
3. `evidenced_days_in_window == expected_window_days`;
4. no existen solapamientos temporales;
5. artículo y unidad son homogéneos;
6. no existen contradicciones no resueltas.

Si la ventana requerida no está completa, no se acorta y el resultado no es `KNOWN`.

### 12.3 Previsión externa/autorizada

STK no calcula el modelo de forecasting.

Consume una estructura equivalente a:

```text
AuthorizedDemandForecast
├── article_id
├── daily_demand: Decimal | null
├── unit
├── horizon_start
├── horizon_end
├── state
├── forecast_version
├── source_ref
└── trace_refs
```

El valor debe estar ya expresado como demanda media por día en la unidad base del artículo para ser consumido por cobertura.

No existe fallback automático entre forecast e histórico.

### 12.4 Salida común

```text
DemandRateResult
├── method
├── daily_demand: Decimal | null
├── unit
├── state
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

Las ventas históricas no constituyen un método de demanda autorizado en v0.1.

---

## 13. Cobertura — M04

### 13.1 Entrada

```text
CoverageInput
├── context
├── stock_available_result
└── demand_rate_result
```

### 13.2 Cálculo

Cuando stock y demanda son `KNOWN` y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
```

### 13.3 Demanda cero confirmada

Cuando `daily_demand == 0` y dicho cero es `KNOWN` y evidenciado:

```text
coverage_state = UNBOUNDED
coverage_days = null
```

El resultado conserva además la semántica empresarial `NOT_APPLICABLE` respecto de una cobertura finita.

No se representa infinito numérico.

### 13.4 Estados de cobertura

```text
DETERMINED
UNBOUNDED
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Estos estados describen el resultado de cobertura y no crean una taxonomía global de EIOS.

---

## 14. Movimientos proyectivos — M05/M06

La proyección utiliza movimientos explícitos y fechados. STK v0.1 **no inventa una distribución temporal** a partir de una tasa de demanda.

### 14.1 Movimiento

```text
ProjectionMovement
├── movement_id: str
├── article_id: str
├── direction: INFLOW | OUTFLOW
├── quantity: Decimal | null
├── unit: str
├── effective_date: date | null
├── state: StockDataState
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str
└── trace_refs
```

`OTHER_AUTHORIZED_NEED` exige una referencia de autoridad/fuente; su existencia no permite inventar una necesidad.

### 14.2 Entradas logísticas M06

Para `PENDING_ORDER` e `IN_TRANSIT`:

- debe existir identidad estable de la cantidad/suministro;
- la misma identidad no puede aparecer simultáneamente en ambos estados;
- la fecha de recepción prevista debe estar evidenciada para incorporarse a la proyección;
- recepción confirmada deja de representarse como M06;
- historial de estados no suma cantidades adicionales.

### 14.3 Cantidad propuesta

`PROPOSED_PURCHASE` solo puede incorporarse cuando el escenario evaluado la incluye explícitamente y aporta:

- cantidad normalizada;
- fecha prevista efectiva para el escenario;
- `scenario_id` canónico;
- referencia de origen/traza.

STK no presume que una propuesta está aprobada ni que será recibida.

### 14.4 Demanda y proyección

Una `DemandRateResult` no se convierte automáticamente en una secuencia de `OUTFLOW`.

Para proyectar salidas futuras debe existir un movimiento o calendario de demanda autorizado y fechado, o una futura extensión contractual que defina de forma normativa la transformación tasa → calendario.

Esta restricción evita introducir una hipótesis temporal no autorizada.

---

## 15. Proyección de stock — M05

### 15.1 Entrada

```text
StockProjectionInput
├── context
├── opening_stock_available: Decimal | null
├── opening_state: StockDataState
├── movements: tuple[ProjectionMovement, ...]
├── horizon_end: date
└── scenario_id: str
```

`scenario_id` debe coincidir con `DecisionContext.scenario_id`.

### 15.2 Orden y cálculo

Los movimientos `KNOWN` se ordenan de forma determinista por:

1. `effective_date`;
2. `movement_id` como desempate técnico estable.

Para cada fecha:

```text
projected_stock_t = projected_stock_previous
                  + known_inflows_t
                  - known_outflows_t
```

La proyección conserva valores negativos cuando se produzcan, porque representan déficit/rotura potencial y no deben truncarse silenciosamente.

### 15.3 Movimientos no determinados

Si un movimiento necesario dentro del horizonte es `UNKNOWN`, `NOT_EVIDENCED` o `CONFLICTING_DATA`:

- no se sustituye por cero;
- no se omite silenciosamente;
- el resultado global no se presenta como proyección completa determinada;
- se conservan los movimientos conocidos y la lista de elementos no resueltos para trazabilidad.

### 15.4 Salida

```text
StockProjectionResult
├── state: StockDataState
├── opening_stock_available
├── points: tuple[ProjectionPoint, ...]
├── unresolved_movement_ids
├── minimum_projected_stock: Decimal | null
├── depletion_date: date | null
├── horizon_end
└── trace_refs
```

`depletion_date` solo se produce cuando la proyección necesaria para demostrarla es determinada. Representa la primera fecha en la que el stock proyectado es `<= 0` dentro del horizonte calculado.

---

## 16. Riesgo de rotura — frontera con R-STK-001

STK puede entregar a Motor de Reglas evidencia calculada como:

- `minimum_projected_stock`;
- `depletion_date`;
- próxima recepción evidenciada relevante;
- estado de determinabilidad de la proyección.

STK **no emite** `COMPRAR` ni `COMPRAR CONDICIONADO`.

La comparación normativa de esos resultados para activar `R-STK-001` pertenece al Motor de Reglas y a `Matriz_Reglas_MVP.md`.

El valor inicial `P-PYE-006 = 15 días` no se utiliza como condición oculta de la regla.

---

## 17. Stock máximo para exceso — M07

M07 admite dos bases, siempre explícitas:

```text
DIRECT_QUANTITY
COVERAGE_MAXIMUM
```

### 17.1 Cantidad directa

Una cantidad máxima directa debe recibirse ya normalizada, trazable y autorizada. Este contrato no crea un nuevo parámetro empresarial para ella.

### 17.2 Máximo derivado de cobertura

Cuando la política vigente utilice cobertura máxima:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Precondiciones:

- `coverage_maximum_days` es un valor configurado y vigente, no un default hardcodeado;
- demanda diaria `KNOWN` y compatible;
- mismo artículo y unidad;
- trazabilidad a `parameters_version`.

Si falta el valor vigente o la demanda necesaria, el máximo no es determinable.

---

## 18. Tolerancia de exceso — M07

La tolerancia puede estar expresada explícitamente como:

```text
QUANTITY
RATE
```

Para `RATE`:

```text
excess_tolerance_quantity = stock_maximum * authorized_tolerance_rate
```

La tasa debe recibirse normalizada como proporción no negativa y con trazabilidad a la configuración vigente.

STK no interpreta automáticamente `10` como `10 %`, `0.10` o cualquier otra escala.

---

## 19. Exceso — M07

### 19.1 Entrada

```text
ExcessInput
├── context
├── stock_reference
├── stock_maximum
└── excess_tolerance
```

`stock_reference` puede ser stock actual determinado o un punto determinado de M05. Si procede de M05, STK no vuelve a sumar M06.

### 19.2 Cálculo

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference - excess_threshold)
```

### 19.3 Estados

```text
NO_EXCESS
WITHIN_TOLERANCE
EXCESS
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Reglas:

```text
stock_reference <= stock_maximum
→ NO_EXCESS

stock_maximum < stock_reference <= excess_threshold
→ WITHIN_TOLERANCE

stock_reference > excess_threshold
→ EXCESS
```

Un cero de `excess_quantity` solo es válido cuando las entradas requeridas son determinadas.

---

## 20. Frontera con R-STK-002 y R-STK-003

STK calcula cobertura y exceso. No emite la recomendación oficial de las reglas.

Relaciones confirmadas:

- `P-STK-004 → R-STK-002` directa;
- `P-STK-004 → R-STK-003` derivada mediante M07;
- `P-STK-005 → R-STK-003` derivada mediante M07.

No se incorporan consumidores adicionales por semejanza nominal.

---

## 21. Pedido confirmado y absorción — M08

### 21.1 Estado de aplicabilidad M08

```text
NO_EXISTE
NO_APLICABLE
APLICABLE_Y_VALIDADA
NO_VERIFICABLE
```

### 21.2 Registro físico

```text
ConfirmedDemandRecord
├── confirmed_demand_id: str
├── order_id: str
├── customer_id: str
├── article_id: str
├── pending_quantity: Decimal | null
├── unit: str
├── order_date: date
├── confirmation_date: date
├── expected_delivery_date: date | null
├── business_status: str
├── applicability_state
├── source_ref: str
└── trace_refs
```

Una marca booleana aislada no es suficiente.

`confirmed_demand_id` identifica la cantidad aplicable para impedir reutilización dentro de una misma evaluación.

### 21.3 Cuantificación

Solo registros `APLICABLE_Y_VALIDADA`, del mismo artículo/unidad y con cantidad pendiente determinada, pueden absorber exceso.

```text
confirmed_order_quantity_applicable = suma de cantidades aplicables únicas
absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

La salida conserva conjuntamente:

- `excess_quantity` original;
- `absorbed_excess`;
- `residual_excess`;
- IDs de demanda confirmada utilizados.

Un mismo `confirmed_demand_id` no puede consumirse dos veces en la misma evaluación.

M08 no reescribe M07.

---

## 22. Ausencia — M09

Toda operación debe propagar estados de ausencia sin convertirlos en cero.

La implementación debe conservar, cuando sea posible:

```text
UnresolvedInput
├── field_or_entity
├── state
├── expected_source
├── source_ref
├── evaluation_date
├── affected_operation
└── trace_refs
```

No se implementa imputación en v0.1.

Una futura imputación requeriría una política empresarial específica y una extensión contractual.

---

## 23. Contradicciones — M10

STK v0.1 no resuelve contradicciones por heurística.

Cuando una entrada requerida se encuentre en `CONFLICTING_DATA`:

- se conservan las referencias de las evidencias implicadas;
- el cálculo dependiente no selecciona una fuente;
- no se utiliza promedio, máximo, mínimo, recencia, score ni prioridad arbitraria;
- el resultado dependiente permanece no determinado.

Una resolución externa autorizada puede entregar posteriormente un valor `KNOWN`, conservando referencia a la regla de autoridad aplicada. STK no implementa una autoridad documental paralela.

---

## 24. Errores estructurales frente a incertidumbre empresarial

La implementación debe distinguir:

### Error estructural

Ejemplos:

- cantidad negativa donde no está permitida;
- Decimal no finito;
- artículo incompatible dentro de la misma operación;
- unidad incompatible sin normalización;
- `scenario_id` inconsistente;
- horizonte anterior a `evaluation_date`;
- ID técnico duplicado que impediría determinar identidad única.

Debe rechazarse mediante validación técnica.

### Incertidumbre empresarial

Ejemplos:

- valor desconocido;
- valor no evidenciado;
- contradicción material;
- fecha futura no evidenciada;
- forecast no verificable.

Debe representarse mediante estado y trazabilidad, no mediante una excepción técnica que borre su significado.

---

## 25. Determinismo y Decimal

Los cálculos cuantitativos STK deben:

- usar `Decimal` para cantidades y tasas;
- rechazar `NaN` e infinitos;
- no depender de hora del sistema para su lógica;
- recibir fechas explícitas;
- ordenar movimientos de forma determinista;
- producir el mismo resultado para la misma entrada, contexto y versiones.

No se aplicará redondeo empresarial implícito. Si una salida requiere redondeo futuro, deberá existir política explícita.

---

## 26. Parámetros y defaults

La implementación **no hardcodeará como verdad empresarial**:

- 15 % de stock de seguridad;
- 30 días de cobertura mínima;
- 90 días de cobertura máxima;
- 10 % de tolerancia de exceso;
- 12 meses de consumo;
- 90 días de horizonte;
- booleanos iniciales `PYE-002…005 = Sí`;
- 15 días de riesgo de rotura.

Los valores que intervengan en un cálculo deben recibirse desde una configuración vigente y quedar vinculados a `parameters_version`.

La ausencia de un valor requerido produce un resultado no determinable; no activa el valor inicial del catálogo como fallback.

---

## 27. Interfaces con otros componentes

### Quality & Trust / Evidence

STK consume estados/evidencias ya reconocidos. No redefine admisibilidad global de evidencia.

### Motor de Reglas

Consume resultados STK para evaluar `R-STK-001…004`. STK no produce resultados decisionales de regla.

### CRC

STK no resuelve conflictos entre resultados de reglas.

### TCO

TCO puede consumir impactos derivados de stock solo cuando exista una extensión autorizada; STK v0.1 no inserta costes de exceso dentro de TCO.

### Decision Twin / escenarios

STK puede evaluar distintos `scenario_id`, pero nunca sobrescribe el resultado de otro escenario.

### MED

Coordina el uso de resultados STK en la evaluación global. Consumir STK no transfiere autoridad.

---

## 28. Resultados públicos mínimos

El paquete STK v0.1 deberá exponer, mediante modelos inmutables o equivalentes, resultados suficientes para reconstruir:

1. disponibilidad de stock;
2. tasa de demanda autorizada;
3. cobertura;
4. proyección;
5. exceso;
6. absorción por demanda confirmada;
7. entradas no resueltas / contradicciones;
8. contexto, versiones y trazabilidad.

Ningún resultado público contiene una decisión final de compra.

---

## 29. Invariantes ejecutables

**I-STK-01 — No decisión automática**  
STK no produce directamente `COMPRAR`, `NEGOCIAR`, `COMPRAR CONDICIONADO` o `NO COMPRAR`.

**I-STK-02 — C0 inmutable**  
STK no añade ni modifica campos de C0.

**I-STK-03 — Ausencia ≠ cero**  
Ningún estado ausente/no evidenciado/contradictorio se convierte implícitamente en cero.

**I-STK-04 — Artículo y unidad compatibles**  
No se realizan operaciones cuantitativas entre artículos o unidades incompatibles.

**I-STK-05 — Stock disponible con déficit visible**  
`stock_available` nunca es negativo; si compromiso > físico, `availability_deficit` conserva la diferencia.

**I-STK-06 — Demanda explícita**  
Solo `AUTHORIZED_FORECAST` o `HISTORICAL_CONSUMPTION` son métodos de demanda v0.1.

**I-STK-07 — Ventana histórica completa**  
No se acorta una ventana histórica por ausencia de periodos.

**I-STK-08 — Ventas ≠ demanda**  
No existe transformación automática ventas → consumo/demanda.

**I-STK-09 — Sin fallback de método**  
No se sustituye forecast por histórico ni histórico por forecast automáticamente.

**I-STK-10 — Sin doble conteo M06**  
Una misma identidad de suministro no puede aportar simultáneamente cantidad como pendiente y tránsito.

**I-STK-11 — Proyección explícita**  
Una tasa de demanda no se convierte implícitamente en movimientos futuros fechados.

**I-STK-12 — Cantidad propuesta explícita**  
La cantidad C0 no se considera normalizada ni se incorpora al escenario sin una magnitud STK explícita y trazable.

**I-STK-13 — Proyección no trunca déficit**  
El stock proyectado puede ser negativo; no se corrige a cero.

**I-STK-14 — Exceso no duplicado**  
Si `stock_reference` procede de M05, M07 no vuelve a sumar M06 ni la cantidad propuesta.

**I-STK-15 — Tolerancia tipada**  
Una tolerancia porcentual/proporcional no se interpreta por magnitud numérica; su tipo es explícito.

**I-STK-16 — Demanda confirmada no reutilizable**  
Una misma cantidad confirmada no absorbe más de una vez el exceso en una evaluación.

**I-STK-17 — M08 no reescribe M07**  
Exceso original, absorción y residual permanecen separados.

**I-STK-18 — Contradicción no resuelta por heurística**  
STK no elige automáticamente entre fuentes contradictorias.

**I-STK-19 — Sin defaults normativos**  
Los valores iniciales del catálogo no se usan como fallback silencioso.

**I-STK-20 — Determinismo**  
Misma entrada + mismas versiones + mismo contexto → mismo resultado.

---

## 30. Criterios mínimos de prueba para futura implementación

La implementación deberá cubrir al menos:

- disponibilidad normal;
- compromiso igual al físico;
- compromiso superior al físico con déficit visible;
- ausencia y contradicción en stock;
- consumo histórico completo e incompleto;
- consumo cero evidenciado;
- forecast autorizado y no evidenciado;
- cobertura determinada y `UNBOUNDED`;
- rechazo de unidad/artículo incompatible;
- M06 pendiente, tránsito y duplicidad de identidad;
- proyección con entradas/salidas fechadas;
- proyección negativa y fecha de agotamiento;
- movimiento requerido ausente/no evidenciado;
- cantidad propuesta solo cuando el escenario la incluye explícitamente;
- stock máximo directo y derivado de cobertura;
- tolerancia por cantidad y por tasa;
- `NO_EXCESS`, `WITHIN_TOLERANCE`, `EXCESS`;
- absorción M08 nula, parcial y total;
- no reutilización de demanda confirmada;
- propagación M09;
- bloqueo de contradicción M10;
- no decisión automática;
- no hardcoding de valores iniciales;
- reproducibilidad determinista.

---

## 31. Exclusiones v0.1

Quedan fuera de este contrato:

- forecasting interno avanzado;
- transformación automática ventas → demanda;
- optimización de stock;
- EOQ;
- cálculo normativo de `stock_minimum`;
- cálculo normativo de `safety_stock`;
- imputación de datos ausentes;
- resolución heurística de contradicciones;
- costes TCO derivados del exceso;
- acciones automáticas de reposición, cancelación, devolución o transferencia;
- persistencia SQL específica de STK;
- API externa;
- cambios en C0;
- lógica CRC;
- decisión final.

---

## 32. Estado

**Contrato v0.1:** DISEÑADO — PENDIENTE DE AUDITORÍA.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
