# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.11  
**Estado:** DEPURADO FINAL DE COMPLETITUD — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2

---

## 2. Propósito y frontera

Define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**. Materializa únicamente semántica, relaciones y cálculos previamente autorizados.

STK no crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisiones automáticas. Rules conserva R-STK-001…004; CRC conserva resolución de conflictos; MED conserva integración; la autoridad decisional final permanece humana.

La implementación ejecutable permanece bloqueada hasta superar `AUDIT 2 FINAL → CERRAR`.

---

## 3. Frontera C0 y paquete físico

STK reutiliza `DecisionContext` y no modifica `PurchaseOperation`, `Evidence`, `EvidenceValidation`, `Rule`, `Assessment` ni `Trace`.

`PurchaseOperation.quantity` no se convierte automáticamente en cantidad STK normalizada porque C0 no contiene la unidad base objetivo.

Paquete previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

Sin dependencias circulares con `eios.core`.

---

## 4. Identidad y temporalidad

La fecha canónica STK es `evaluation_date`. La proyección v0.1 tiene granularidad diaria; no se infiere secuencia intradía.

```text
StockResultIdentity
├── decision_id: str
├── scenario_id: str
├── rules_version: str
├── parameters_version: str
├── data_snapshot_id: str
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

Los identificadores canónicos se derivan sin transformación de `DecisionContext`; `forecast_version` expresa dependencia de forecast cuando existe. Los consumidores exigen compatibilidad exacta de identidad.

---

## 5. Estados y colecciones

Estados STK:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

`state != KNOWN` no presenta valor determinado. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`. Todo `KNOWN` exige fuente o traza.

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` trazable significa vacío evidenciado.

---

## 6. Magnitudes físicas y umbrales

```text
NormalizedQuantity
├── article_id
├── value: Decimal | null
├── unit
├── state
├── source_ref
├── effective_date: date | null
└── trace_refs
```

Representa magnitud física. `KNOWN`: finita, no negativa y trazable. No representa saldo proyectado ni umbral empresarial.

```text
AuthorizedQuantityThreshold
├── article_id
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit
├── state
├── applicable_reference_date
├── authority_ref: str
├── authority_version: str
├── source_ref
└── trace_refs
```

`KNOWN` exige valor finito no negativo, artículo/unidad compatibles, propósito correcto, `authority_ref` y `authority_version` no vacíos y fecha exactamente aplicable a la referencia consumidora. Un umbral no adquiere vigencia futura por inferencia y no representa inventario físico.

---

## 7. Valores autorizados M02/M03 sin fórmula implícita

M02 y M03 se materializan como valores ya autorizados externamente; STK no los calcula.

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

1. `KNOWN` exige cantidad finita y no negativa, unidad base compatible, política/versión/fuente y trazabilidad;
2. `valid_to`, si existe, debe ser `>= valid_from`;
3. un consumidor solo puede utilizar el valor si `valid_from <= reference_date` y, cuando exista, `reference_date <= valid_to`;
4. ausencia o evidencia insuficiente produce `UNKNOWN / NOT_EVIDENCED`, nunca cero;
5. `STOCK_MINIMUM` y `SAFETY_STOCK` no son equivalentes;
6. no se compone uno dentro del otro sin política explícita;
7. este tipo no crea fórmula, consumidor de regla ni valida los valores iniciales `STK-001/002`.

---

## 8. Contexto y método de demanda

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id
├── evaluation_date
├── base_unit
├── methodology_version
└── forecast_version: str | null
```

- `AUTHORIZED_FORECAST` exige `forecast_version != null`.
- `HISTORICAL_CONSUMPTION` exige `forecast_version == null`.
- No se arrastra una versión de forecast a método histórico por disponibilidad técnica.

---

## 9. Parámetros configurados

```text
ConfiguredParameterValue
├── parameter_id
├── value: Decimal | int | bool | null
├── unit
├── state
├── parameters_version
├── applicable_reference_date
├── configuration_ref
├── source_ref
├── normalization_ref: str | null
└── trace_refs
```

STK consume configuración efectiva resuelta por el Centro de Parametrización; no reimplementa vigencia ni zonas horarias. `KNOWN` exige versión coincidente, configuración efectiva identificada, fecha aplicable correcta y tipo/unidad compatibles. Sin fallback a valores iniciales.

---

## 10. Composición de compromiso de apertura

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

Cantidad finita/no negativa; mismo artículo/unidad/fecha que `stock_committed`; `commitment_id` único. Cuando representa reserva/asignación vinculada a demanda comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios, estables y trazables. Un compromiso no comercial no recibe IDs inventados. Una composición `KNOWN` suma exactamente `stock_committed.value`.

---

## 11. Demanda confirmada ya incorporada

```text
IncorporatedDemandQuantity
├── confirmed_demand_id: str
├── quantity: Decimal
├── unit: str
├── demand_segment_ids: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

Se agrega por pedido, preservando segmentos. Cantidad finita/no negativa; unidad única; segmentos sin duplicados.

---

## 12. Disponibilidad de stock

```text
StockAvailabilityInput
├── context
├── stock_on_hand: NormalizedQuantity
├── stock_committed: NormalizedQuantity
└── committed_components: CollectionEnvelope[StockCommitmentComponent]
```

Para resultado `KNOWN`: on-hand y committed KNOWN, artículo/unidad = contexto, ambas fechas = `evaluation_date`, composición KNOWN/trazable, compatible, sin IDs duplicados y suma exacta.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

`StockAvailabilityResult` conserva identidad, entradas, disponible, déficit, composición de demanda confirmada ya incorporada, estado y trazas. Sin tolerancia implícita de antigüedad.

---

## 13. Consumo M01

`ConsumptionPeriod` conserva artículo, ID/intervalo, días evidenciados, cantidad, unidad, estado, fuente y trazas.

Consumo real, no ventas/forecast. `KNOWN` exige cantidad no negativa, periodo completo y trazable. Cero solo si está evidenciado.

---

## 14. Política y demanda histórica

`RequiredPeriodSpec` conserva ID/inicio/fin.

`HistoricalDemandPolicy` conserva `P-STK-006`, periodos requeridos, calendario, eventual extensión de aplicabilidad, fuente y trazas.

`P-STK-006`: `KNOWN`, versión/fecha efectiva correctas, entero positivo no booleano, unidad meses/periodos mensuales autorizada o normalizada. IDs únicos, intervalos válidos/no solapados y calendario trazable. Extensión futura solo con autoridad explícita.

Demanda histórica `KNOWN`: colección KNOWN, correspondencia exacta uno-a-uno de IDs/intervalos, periodos homogéneos y completos:

```text
evidenced_days == (period_end - period_start).days + 1
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta, rellena ni duplica la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
context.forecast_version = null
```

---

## 15. Demanda común y forecast

```text
DemandRateResult
├── identity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand
├── unit
├── state
├── reference_date
├── applicable_from
├── applicable_to
├── applicability_source_ref
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

Forecast KNOWN conserva artículo, tasa, unidad, horizonte, estado, versión, fuente y traza y cumple:

```text
context.forecast_version != null
context.forecast_version == forecast.forecast_version
identity.forecast_version == forecast.forecast_version
DemandRateResult.forecast_version == forecast.forecast_version
```

Histórico: todas las referencias de forecast son nulas. No forecasting interno, ventas→demanda ni fallback.

---

## 16. Cobertura M04

La tasa debe ser aplicable a `evaluation_date` y compartir identidad compatible.

```text
coverage_days = stock_available / daily_demand    # daily_demand > 0
```

Cero confirmado/evidenciado/aplicable → `UNBOUNDED`, `coverage_days = null`. Sin infinito numérico.

---

## 17. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id
├── supply_identity: str | null
├── confirmed_demand_id: str | null
├── demand_segment_id: str | null
├── scenario_id: str | null
├── article_id
├── direction: INFLOW | OUTFLOW
├── quantity
├── unit
├── effective_date
├── state
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref
└── trace_refs
```

Dirección autorizada:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Movimiento KNOWN contribuyente: ID único, cantidad finita/no negativa, artículo/unidad compatibles, traza y `evaluation_date < effective_date <= horizon_end`.

Sin cutoff intradía ni roll-forward. `NOT_APPLICABLE` evidenciado no contribuye/contamina; otros estados no determinados propagan incertidumbre.

Para `AUTHORIZED_DEMAND` comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios. Un segmento no puede repetirse entre movimientos ni coincidir con uno incorporado en opening. Distintos segmentos del mismo pedido son admisibles si están identificados/trazados.

M06 exige `supply_identity` estable/único; parcialidades identificadas; no pendiente+tránsito simultáneo; recepción confirmada sale M06.

`PROPOSED_PURCHASE` exige escenario coincidente, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 18. Proyección M05

`StockProjectionInput` conserva contexto, opening, colección de movimientos, horizonte, fuente/trazas del horizonte y escenario.

Escenario coincidente; horizonte trazable; opening KNOWN e identidad compatible; movimientos KNOWN estrictamente futuros y dentro del horizonte. Ningún `demand_segment_id` confirmado puede existir simultáneamente en opening y movimientos M05.

Para cada fecha futura:

```text
closing_stock_date = opening_stock_date
                   + sum(known applicable inflows)
                   - sum(known applicable outflows)
```

Sin orden intradía. Saldo negativo se conserva. La composición acumulada de demanda confirmada parte de opening y añade exclusivamente segmentos M05 contabilizados, agregados por pedido.

Incertidumbre fechada contamina desde su fecha; sin fecha, desde evaluación; `NOT_APPLICABLE` no contamina; datos posteriores no restauran KNOWN.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Opening cero KNOWN → `depletion_date = evaluation_date`; si no, primera fecha futura determinada con cierre `<= 0`.

---

## 19. Frontera R-STK-001 / M02 / M03

STK entrega métricas/evidencia, no decisiones. M02/M03 se representan mediante `AuthorizedStockPolicyQuantity`, pero v0.1 no calcula sus valores ni crea una relación de regla no demostrada. Ausencia ≠ cero. Valores iniciales no son defaults.

---

## 20. Referencia de stock M07

```text
StockReferenceValue
├── identity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date
├── value
├── unit
├── state
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── source_ref
└── trace_refs
```

`CURRENT_AVAILABLE` deriva de disponibilidad, fecha = evaluación, valor no negativo y conserva demanda confirmada ya descontada en committed. `PROJECTED` deriva de M05, puede ser negativo y conserva composición acumulada sin duplicar segmentos.

---

## 21. Base máximo y tolerancia M07

`StockMaximumBasis` tiene ramas exclusivas:

- `DIRECT_QUANTITY` → `AuthorizedQuantityThreshold` purpose `STOCK_MAXIMUM`;
- `COVERAGE_MAXIMUM` → `P-STK-004 + DemandRateResult`.

Todo debe ser KNOWN, compatible y aplicable a `stock_reference.reference_date`. La rama directa exige `authority_ref/version`; cobertura exige parámetro efectivo, unidad días normalizada, demanda >0 y temporalmente aplicable.

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`ExcessToleranceBasis` tiene ramas exclusivas:

- `QUANTITY` → `AuthorizedQuantityThreshold` purpose `EXCESS_TOLERANCE` con autoridad versionada;
- `RATE` → `P-STK-005` normalizado/trazado para la fecha de referencia.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

Sin inferencia porcentual.

---

## 22. Exceso M07

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

M07 conserva identidad, referencia/fecha, composición incorporada de demanda confirmada, máximo, tolerancia, umbral, exceso y trazas. No reañade M06/propuesta.

Únicas relaciones parámetro↔regla confirmadas: `P-STK-004→R-STK-002`; `P-STK-004→R-STK-003` derivada; `P-STK-005→R-STK-003` derivada.

---

## 23. M08 — demanda confirmada

```text
ConfirmedDemandRecord
├── confirmed_demand_id
├── order_id
├── customer_id
├── article_id
├── pending_quantity: NormalizedQuantity
├── order_date
├── confirmation_date
├── expected_delivery_date
├── business_status
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref
├── source_ref
└── trace_refs
```

Solo colección KNOWN vacía/trazada significa `NO_EXISTE`.

Para `APLICABLE_Y_VALIDADA`:

```text
pending_quantity.state == KNOWN
pending_quantity.effective_date == allocation_scope.evaluation_date
order_date <= confirmation_date <= allocation_scope.evaluation_date
expected_delivery_date > allocation_scope.excess_reference_date
expected_delivery_date <= allocation_scope.horizon_end
```

La desigualdad respecto a `excess_reference_date` es estricta porque v0.1 no posee cutoff intradía. Una entrega anterior o igual a la fecha del exceso proyectado no corrige M05 ex post mediante M08. Cambios/cancelaciones/parcialidades requieren evidencia vigente.

---

## 24. Ledger M08 activo y con procedencia

```text
AllocationLedgerEntry
├── allocation_entry_id: str
├── confirmed_demand_id
├── allocated_quantity
├── unit
├── decision_id
├── scenario_id
├── excess_reference_date
├── allocation_result_ref
└── trace_refs
```

```text
AllocationLedgerSnapshot
├── reference_date: date
├── entries: tuple[AllocationLedgerEntry, ...]
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `snapshot.reference_date == allocation_scope.evaluation_date`;
2. el snapshot contiene únicamente asignaciones activas que todavía reservan cantidad pendiente contra reutilización en esa fecha;
3. histórico liberado/consumido se conserva aguas arriba, no se suma como activo;
4. `allocation_entry_id` es único y duplicados no se agregan;
5. cada entry conserva decisión, escenario, fecha de exceso y referencia del resultado original;
6. STK consume el snapshot y no implementa persistencia ni decide liberaciones históricas.

```text
DemandAllocation
├── confirmed_demand_id
├── quantity_to_apply
├── unit
├── allocation_source_ref
└── trace_refs
```

No existe prioridad implícita.

---

## 25. Reconciliación opening/M05/M08

Para cada pedido aplicable:

```text
incorporated_before_M08
= cantidad del confirmed_demand_id ya incorporada
  en stock_reference.incorporated_confirmed_demand

already_allocated
= suma activa del confirmed_demand_id
  en AllocationLedgerSnapshot

remaining_allocatable
= pending_quantity
  - incorporated_before_M08
  - already_allocated
```

Misma unidad; cantidades >=0; `incorporated_before_M08 + already_allocated <= pending_quantity`. Si excede pending, no se aplica suelo cero: inconsistencia/contradicción. Una misma cantidad no se usa dos veces entre opening, M05 y M08.

---

## 26. Alcance y absorción M08

```text
AllocationScope
├── decision_id
├── scenario_id
├── article_id
├── evaluation_date
├── excess_reference_date
├── horizon_end
├── horizon_source_ref
└── trace_refs
```

Compatible con identidad STK y `ExcessResult.reference_date`; horizonte explícito/trazable.

Solo pedidos `APLICABLE_Y_VALIDADA`, mismo artículo/unidad, pending KNOWN vigente y entrega **posterior al exceso de referencia** y dentro del horizonte participan. IDs únicos. Ledger snapshot/plan solo IDs presentes. Plan no supera `remaining_allocatable`. Colección no KNOWN hace M08 no evaluable. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Materialización por pedido exige:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si absorbed=0, plan vacío. Si absorbed>0, plan ausente/incompleto/sobreasignado bloquea reparto. El nuevo ledger añade entradas únicas y trazables para las asignaciones del plan. M08 conserva exceso original, total aplicable, absorbido, residual, plan, ledger resultante, identidad y trazas; no reescribe M07.

---

## 27. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. La incertidumbre y fuente esperada se conservan y propagan.

---

## 28. M10 — contradicciones

`CONFLICTING_DATA` bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad arbitraria. Una resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 29. Error estructural vs incertidumbre

Se rechaza estructuralmente, entre otros:

- Decimal no finito;
- cantidad física negativa;
- identidad/versiones incompatibles;
- histórico con forecast_version no nula o forecast con versión nula/diferente;
- stock actual de otra fecha;
- composición committed incompleta/inconsistente/duplicada;
- demand_segment_id repetido opening↔M05;
- movimiento KNOWN no estrictamente futuro o fuera de horizonte;
- configuración efectiva incorrecta;
- M02/M03 KNOWN sin política/versionado/vigencia;
- ventana histórica inválida;
- umbral directo M07 sin autoridad/versionado;
- umbral/demanda fuera de vigencia;
- ramas discriminadas simultáneas;
- pending M08 no vigente;
- fechas comerciales incompatibles o entrega `<= excess_reference_date` para APLICABLE_Y_VALIDADA;
- ledger snapshot de otra fecha, entry duplicada o sin procedencia;
- `incorporated + allocated > pending`;
- plan M08 inválido.

Se representa como incertidumbre empresarial: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/política/umbral no verificables, demanda no aplicable temporalmente y M08 no verificable.

---

## 30. Determinismo

Decimal; no NaN/infinito; fechas explícitas; sin reloj; sin redondeo empresarial implícito; sin prioridad M08; misma entrada + identidad/versiones/configuración/política + composición opening/M05 + ledger activo → mismo resultado.

---

## 31. Defaults prohibidos

No se hardcodean: 15 % safety stock; 30/90 días; 10 % tolerancia; 12 meses; 90 días de horizonte; `PYE-002…005 = Sí`; 15 días. Ausencia de configuración/política no activa valores iniciales.

---

## 32. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; políticas M02/M03 suministran valores autorizados sin fórmula STK; Rules consume hechos STK; CRC queda fuera; TCO no recibe costes derivados STK v0.1; Decision Twin no mezcla escenarios/versiones; MED integra sin transferir autoridad. `R-STK-004` queda limitado a M08 sobre exceso M07 y no se amplía por interpretación.

---

## 33. Invariantes ejecutables

1. No decisión automática; C0 inmutable.
2. Ausencia ≠ cero; KNOWN exige traza; vacío evidenciado ≠ ausencia.
3. Magnitud física ≠ umbral.
4. Identidad conserva decision/scenario/rules/parameters/snapshot y forecast cuando aplica.
5. Histórico exige forecast_version nula; forecast exige versión exacta no nula.
6. M02/M03 se representan sin fórmula; concepto, política, versión y vigencia son obligatorios para KNOWN.
7. Stock actual pertenece a evaluation_date; déficit visible.
8. stock_committed KNOWN tiene composición completa y reconciliada.
9. Demanda confirmada ya descontada en opening queda identificada cuantitativamente.
10. Demanda histórica/forecast son métodos exclusivos; ventas ≠ demanda; sin fallback.
11. Aplicabilidad temporal de demanda explícita; P-STK-006 versión/fecha/unidad; ventana exacta/completa.
12. Coverage consume demanda aplicable.
13. movement_id único; supply_identity evita doble conteo M06.
14. Movimiento contribuyente estrictamente futuro; sin cutoff intradía.
15. demand_segment_id evita doble uso opening↔M05 y permite parcialidades legítimas.
16. source kind/dirección compatibles; NOT_APPLICABLE no contamina.
17. Tasa no crea calendario; propuesta exige escenario; horizonte trazable.
18. Proyección diaria; saldo negativo preservado; incertidumbre temporal.
19. Opening cero → depletion_date=evaluation_date; mínimo incluye opening.
20. Composición confirmada M05 se acumula por pedido/segmento; M07 la conserva y no reañade entradas.
21. Umbrales directos M07 conservan authority_ref/version; P-STK-004/P-STK-005 solo para fecha resuelta.
22. Coverage maximum exige demanda >0 aplicable; ramas exclusivas; tolerancia RATE trazada.
23. M08 usa pending vigente y entrega estrictamente posterior a excess_reference_date.
24. M08 descuenta cantidades ya incorporadas en opening/M05 y ledger activo previo.
25. AllocationLedgerSnapshot coincide con evaluation_date y contiene IDs de entrada únicos.
26. incorporated + allocated nunca supera pending; no suelo cero ante inconsistencia.
27. Ledger conserva decisión, escenario, fecha de exceso y resultado original.
28. M08 no inventa prioridad; plan suma exactamente absorción; no reescribe M07.
29. R-STK-004 no se amplía fuera de M08/M07.
30. Contradicción no se resuelve heurísticamente.
31. Sin defaults normativos; determinismo.

---

## 34. Pruebas mínimas futuras

Cubrir al menos: identidad canónica/forecast; M02/M03 KNOWN/UNKNOWN, vigencia y conceptos no equivalentes; disponibilidad/snapshot; composición committed completa/incompleta; segmento duplicado opening↔M05; histórico/forecast; parámetros efectivos; P-STK-006; ventana histórica; cobertura; movimientos duplicados/mismo día/fuera de horizonte/NOT_APPLICABLE; M06; propuesta; mezcla de contextos; proyección diaria/opening cero/saldo negativo/incertidumbre; M07 umbral directo sin versión o fecha incorrecta, máximo por cobertura/tolerancia; M08 pedido ya incluido opening/M05, pending de otra fecha, entrega <= excess_reference_date, ledger snapshot antiguo, entry duplicada, ledger previo, sobreconsumo, plan inválido y absorción; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 35. Exclusiones v0.1

Fuera de alcance: forecasting interno; ventas→demanda; tasa→calendario; vigencia futura implícita; cutoff intradía; tolerancia temporal implícita; optimización/EOQ; fórmula normativa de stock_minimum/safety_stock; imputación; resolución heurística; prioridad M08; persistencia propia del ledger; costes TCO derivados; acciones automáticas; persistencia SQL STK; API externa; cambios C0; CRC; decisión final.

---

## 36. Estado

**Contrato v0.11:** DEPURADO FINAL DE COMPLETITUD.  
**Hallazgos A…I:** resueltos.  
**Hallazgos J1…J4:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación.  
**M02/M03:** representables sin fórmula cuantitativa ni default implícito.  
**Siguiente paso:** AUDIT 2 FINAL independiente.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
