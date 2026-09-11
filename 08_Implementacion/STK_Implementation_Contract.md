# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.9  
**Estado:** DEPURADO FINAL DE COMPOSICIÓN — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2

---

## 2. Propósito y frontera

Define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**. Solo materializa semántica, relaciones y cálculos previamente autorizados.

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

Los cinco primeros identificadores canónicos se derivan sin transformación de `DecisionContext`. `forecast_version` se deriva de `StockComputationContext` y solo expresa dependencia de forecast cuando esta existe.

Los consumidores exigen compatibilidad exacta de identidad. No se mezclan resultados entre escenarios, snapshots, reglas, parámetros o forecasts distintos.

---

## 5. Estados STK

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

`state != KNOWN` no presenta valor numérico determinado. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`. Todo `KNOWN` exige fuente o traza. Estos estados no redefinen C0.

---

## 6. Colecciones empresariales

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` trazable significa vacío evidenciado. Vacío desconocido/no evidenciado no significa inexistencia.

---

## 7. Magnitud física normalizada

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

Representa magnitud física, no saldo analítico ni umbral. `KNOWN`: Decimal finito, no negativo, artículo/unidad explícitos y traza. `state != KNOWN → value = null`. Sin conversiones implícitas.

---

## 8. Umbral cuantitativo autorizado

```text
AuthorizedQuantityThreshold
├── article_id: str
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── applicable_reference_date: date
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

`KNOWN` exige valor finito no negativo y traza; artículo/unidad compatibles; purpose correcto; fecha aplicable igual a `stock_reference.reference_date`. Un umbral no adquiere vigencia futura por inferencia y no representa inventario físico.

---

## 9. Contexto STK y método de demanda

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

Invariante de dependencia:

- evaluación `AUTHORIZED_FORECAST` → `forecast_version` obligatoria;
- evaluación `HISTORICAL_CONSUMPTION` → `forecast_version == null`;
- una versión de forecast no se arrastra a una evaluación histórica por disponibilidad técnica.

La elección del método pertenece a la política/configuración autorizada, no a una heurística del motor.

---

## 10. Parámetros configurados y vigencia

STK consume configuración ya resuelta por el Centro de Parametrización; no reimplementa `valid_from/valid_to`, zonas horarias ni selección efectiva.

```text
ConfiguredParameterValue
├── parameter_id: str
├── value: Decimal | int | bool | null
├── unit: str
├── state: StockDataState
├── parameters_version: str
├── applicable_reference_date: date
├── configuration_ref: str
├── source_ref: str
├── normalization_ref: str | null
└── trace_refs: tuple[str, ...]
```

`KNOWN` requiere versión coincidente con `DecisionContext`, configuración efectiva identificada, fecha aplicable coincidente con la requerida y tipo/unidad válidos. No se reutiliza silenciosamente configuración actual para fechas futuras ni valores iniciales como fallback.

---

## 11. Disponibilidad de stock

Para `StockAvailabilityResult.state = KNOWN`, `stock_on_hand` y `stock_committed` deben ser KNOWN, pertenecer al mismo artículo/unidad y tener `effective_date == evaluation_date`.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

La salida conserva `StockResultIdentity`, entradas, resultado, déficit, estado y trazas. El déficit no se oculta. No existe tolerancia implícita de antigüedad.

---

## 12. Consumo M01

```text
ConsumptionPeriod
├── article_id
├── period_id
├── period_start
├── period_end
├── evidenced_days
├── quantity
├── unit
├── state
├── source_ref
└── trace_refs
```

Consumo real, no ventas/forecast. KNOWN exige cantidad no negativa, periodo completo y trazable. Cero solo existe si está evidenciado.

---

## 13. Política histórica de demanda

```text
RequiredPeriodSpec
├── period_id
├── period_start
└── period_end
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue
├── required_periods
├── period_calendar_ref
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref
└── trace_refs
```

`P-STK-006` debe ser KNOWN, aplicable a `evaluation_date`, versión correcta, entero positivo no booleano y unidad autorizada/normalizada como meses o periodos mensuales. Número de periodos coincidente; IDs únicos; intervalos válidos/no solapados; calendario trazable. No se generan meses implícitamente. Extensión futura solo con autoridad trazable.

---

## 14. Demanda histórica

`HistoricalDemandInput = context + policy + CollectionEnvelope[ConsumptionPeriod]`.

Resultado KNOWN solo con colección KNOWN, correspondencia uno-a-uno de IDs e intervalos, periodos completos, homogéneos y no contradictorios.

```text
evidenced_days == (period_end - period_start).days + 1
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta, rellena ni duplica la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
```

Además, para método histórico:

```text
context.forecast_version = null
StockResultIdentity.forecast_version = null
DemandRateResult.forecast_version = null
```

Sin autoridad explícita, la media histórica no adquiere vigencia futura.

---

## 15. Demanda común y forecast autorizado

```text
DemandRateResult
├── identity: StockResultIdentity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand: Decimal | null
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

Forecast autorizado conserva artículo, daily_demand, unidad, horizonte, estado, versión, fuente y trazas.

Para `AUTHORIZED_FORECAST`:

```text
context.forecast_version != null
context.forecast_version == forecast.forecast_version
identity.forecast_version == forecast.forecast_version
DemandRateResult.forecast_version == forecast.forecast_version
```

El horizonte contiene `evaluation_date`; tasa finita no negativa; artículo/unidad compatibles y trazados. Resultados posteriores dependientes conservan la misma versión.

No forecasting interno, ventas→demanda ni fallback entre métodos.

---

## 16. Cobertura M04

La demanda debe ser aplicable a `evaluation_date` y compartir identidad compatible con el stock.

Con demanda KNOWN > 0:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Con cero confirmado/evidenciado/aplicable: `coverage_days = null`, `status = UNBOUNDED`. Sin infinito numérico.

---

## 17. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id: str
├── supply_identity: str | null
├── confirmed_demand_id: str | null
├── scenario_id: str | null
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

Dirección obligatoria:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

`movement_id` único. Movimiento KNOWN contribuyente: cantidad finita no negativa, artículo/unidad compatibles, traza y:

```text
evaluation_date < effective_date <= horizon_end
```

Sin cutoff intradía. Movimiento conocido fuera de horizonte no se desplaza. NOT_APPLICABLE evidenciado no contribuye ni contamina; UNKNOWN/NOT_EVIDENCED/CONFLICTING propagan incertidumbre.

Para `AUTHORIZED_DEMAND` que representa demanda comercial confirmada, `confirmed_demand_id` es obligatorio y trazable. Para otros tipos, ese ID no se inventa.

M06: `supply_identity` obligatorio y único para pendiente/tránsito; parcialidades con identidad de segmento; no coexistencia pendiente+tránsito; sin roll-forward; recepción confirmada sale M06.

PROPOSED_PURCHASE: escenario coincidente, cantidad normalizada, fecha futura en horizonte y traza; no presume aprobación.

---

## 18. Demanda ya incorporada en proyección

Para impedir doble uso M05↔M08:

```text
IncorporatedDemandQuantity
├── confirmed_demand_id: str
├── quantity: Decimal
├── unit: str
└── trace_refs: tuple[str, ...]
```

M05 agrega por `confirmed_demand_id` exclusivamente las cantidades de movimientos `AUTHORIZED_DEMAND` KNOWN efectivamente contabilizados.

Reglas:

1. cantidad agregada finita y no negativa;
2. misma unidad base;
3. cada componente conserva movimiento/fuente en trazas;
4. una demanda no confirmada no recibe un ID inventado;
5. esta estructura registra composición del saldo, no asignación M08 ni decisión.

---

## 19. Proyección M05

```text
StockProjectionInput
├── context
├── opening_availability: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end
├── horizon_source_ref
├── horizon_trace_refs
└── scenario_id
```

Escenario coincidente; horizonte trazable; opening KNOWN e identidad compatible; movimientos contribuyentes estrictamente futuros y dentro del horizonte.

Para cada fecha futura:

```text
closing_stock_date = opening_stock_date
                   + sum(known applicable inflows)
                   - sum(known applicable outflows)
```

Sin orden intradía; movimientos del día se agregan. Saldo negativo se conserva.

Cada punto/proyección conserva además la composición acumulada de `IncorporatedDemandQuantity` efectivamente contabilizada hasta esa fecha.

Incertidumbre fechada contamina desde su fecha; sin fecha, desde evaluación; NOT_APPLICABLE no contamina; un dato conocido posterior no restaura KNOWN.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Opening cero conocido → `depletion_date = evaluation_date`; si no, primera fecha futura determinada con cierre <= 0.

---

## 20. Frontera R-STK-001 / M02 / M03

STK entrega métricas/evidencia, no decisiones. v0.1 no calcula `stock_minimum` ni `safety_stock` mediante fórmula propia porque M02/M03 exigen política cuantitativa explícita no cerrada. Ausencia ≠ cero. Valores iniciales como 15 %, 30 días o P-PYE-006 15 días no son defaults.

---

## 21. Referencia de stock M07

```text
StockReferenceValue
├── identity: StockResultIdentity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date: date
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── source_ref: str
└── trace_refs
```

CURRENT: disponibilidad actual, no negativa, fecha=eval y `incorporated_confirmed_demand=()` salvo evidencia de composición explícita autorizada; STK no la inventa.

PROJECTED: deriva de punto M05 compatible, puede ser negativo y conserva exactamente la composición de demanda confirmada ya contabilizada hasta `reference_date`.

---

## 22. Base de stock máximo M07

```text
StockMaximumBasis
├── kind: DIRECT_QUANTITY | COVERAGE_MAXIMUM
├── direct_threshold: AuthorizedQuantityThreshold | null
├── coverage_maximum: ConfiguredParameterValue | null
├── demand_rate: DemandRateResult | null
├── state
├── source_ref
└── trace_refs
```

Ramas exclusivas. DIRECT: threshold STOCK_MAXIMUM compatible y aplicable a referencia. COVERAGE: `P-STK-004` KNOWN, versión/fecha efectiva coincidentes, unidad días normalizada, demanda KNOWN >0, identidad compatible y aplicable a `stock_reference.reference_date`.

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Cero de demanda no deriva máximo cero. No se reutilizan configuración o demanda fuera de vigencia.

---

## 23. Tolerancia M07

RATE conserva ID `P-STK-005`, tasa normalizada, unidad original, estado, versión, fecha aplicable, configuration_ref, normalization_ref, source/trazas. QUANTITY usa `AuthorizedQuantityThreshold` purpose EXCESS_TOLERANCE.

Ramas exclusivas y aplicables a `stock_reference.reference_date`.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

No se infiere escala porcentual.

---

## 24. Exceso M07

Con entradas KNOWN, compatibles y temporalmente aplicables:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

M07 preserva `StockResultIdentity`, `reference_date`, `stock_reference` —incluida su composición de demanda incorporada—, máximo, tolerancia, umbral, exceso y trazas. No reañade M06/propuesta.

Únicas relaciones parámetro↔regla confirmadas: P-STK-004→R-STK-002; P-STK-004→R-STK-003 derivada; P-STK-005→R-STK-003 derivada.

---

## 25. M08 — demanda confirmada

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

Solo colección KNOWN vacía y trazable significa NO_EXISTE. Solo pending quantity KNOWN absorbe. APLICABLE_Y_VALIDADA exige fecha de entrega evidenciada y compatible con horizonte. Cambios/cancelaciones/parcialidades requieren evidencia vigente.

---

## 26. Ledger y reconciliación M05↔M08

```text
AllocationLedgerEntry
├── confirmed_demand_id
├── allocated_quantity
├── unit
└── trace_refs
```

```text
DemandAllocation
├── confirmed_demand_id
├── quantity_to_apply
├── unit
├── allocation_source_ref
└── trace_refs
```

Para cada pedido aplicable se determinan:

```text
incorporated_in_projection
= cantidad del mismo confirmed_demand_id
  conservada en stock_reference.incorporated_confirmed_demand

already_allocated
= cantidad del mismo confirmed_demand_id en allocation_ledger

remaining_allocatable
= pending_quantity
  - incorporated_in_projection
  - already_allocated
```

Invariantes:

- todas las cantidades comparten unidad;
- `incorporated_in_projection >= 0`;
- `already_allocated >= 0`;
- `incorporated_in_projection + already_allocated <= pending_quantity`;
- si la suma excede la cantidad pendiente, no se aplica suelo cero: se rechaza como inconsistencia/contradicción;
- una misma cantidad no se descuenta dos veces entre M05 y M08;
- no existe prioridad implícita de reparto.

---

## 27. Alcance y absorción M08

`AllocationScope` conserva decision/scenario/article/evaluation_date/excess_reference_date/horizon_end/horizon_source_ref/trazas y debe ser compatible con `StockResultIdentity` y `ExcessResult.reference_date`.

Input: contexto, scope, exceso, colección de demanda confirmada, ledger y plan.

Solo registros APLICABLE_Y_VALIDADA, mismo artículo/unidad, pending KNOWN y entrega dentro del horizonte participan. IDs únicos. Ledger/plan solo IDs presentes. Plan no puede superar `remaining_allocatable`. Colección no KNOWN hace M08 no evaluable. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Materialización por pedido exige:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si absorbed=0, plan vacío. Si absorbed>0, plan ausente/incompleto/sobreasignado bloquea reparto; no se inventa.

Ledger de salida suma solo cantidades del plan. M08 conserva exceso original, total aplicable, absorbido, residual, plan, ledger, identidad y trazas; no reescribe M07.

---

## 28. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. La incertidumbre y fuente esperada se conservan.

---

## 29. M10 — contradicciones

CONFLICTING_DATA bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad. Resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 30. Error estructural vs incertidumbre

Se rechaza estructuralmente, entre otros: Decimal no finito; cantidad física negativa; identidad/versiones incompatibles; histórico con forecast_version no nula; forecast con versión nula/diferente; stock actual de otra fecha; movimiento conocido no estrictamente futuro o fuera de horizonte; IDs incompatibles/duplicados; configuración efectiva incorrecta; ventana histórica inválida; umbral/demanda fuera de vigencia; ramas discriminadas dobles; `incorporated + allocated > pending`; ledger/plan M08 inválidos.

Se representa como incertidumbre: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/umbral no verificables, demanda no temporalmente aplicable, M08 no verificable.

---

## 31. Determinismo

Decimal; no NaN/infinito; fechas explícitas; sin reloj; sin redondeo empresarial implícito; sin prioridad M08; misma entrada + identidad/versiones/configuración + composición M05 → mismo resultado.

---

## 32. Defaults prohibidos

No se hardcodean: 15 % safety stock; 30/90 días; 10 % tolerancia; 12 meses; 90 días de horizonte; PYE-002…005 Sí; 15 días. Ausencia de configuración no activa valores iniciales.

---

## 33. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; Rules consume hechos STK; CRC queda fuera; TCO no recibe costes derivados STK v0.1; Decision Twin no mezcla escenarios/versiones; MED integra sin transferir autoridad. R-STK-004 queda limitado a M08 sobre exceso M07 y no se amplía a cobertura elevada por interpretación.

---

## 34. Invariantes ejecutables

1. No decisión automática; C0 inmutable.
2. Ausencia ≠ cero; KNOWN exige traza; vacío evidenciado ≠ ausencia.
3. Magnitud física ≠ umbral.
4. Identidad conserva decision/scenario/rules/parameters/snapshot y forecast cuando aplica.
5. Histórico exige forecast_version nula; forecast exige versión exacta no nula.
6. Stock actual pertenece a evaluation_date; déficit visible.
7. Demanda histórica/forecast son métodos exclusivos; ventas ≠ demanda; sin fallback.
8. Aplicabilidad temporal de demanda explícita.
9. P-STK-006 versión/fecha/unidad; ventana histórica exacta/completa.
10. Coverage consume demanda aplicable.
11. movement_id único; supply_identity evita doble conteo M06.
12. Movimiento contribuyente estrictamente futuro; sin cutoff intradía.
13. source kind/dirección compatibles; NOT_APPLICABLE no contamina.
14. Tasa no crea calendario; propuesta exige escenario.
15. Horizonte trazable; proyección diaria; saldo negativo preservado; incertidumbre temporal.
16. Opening cero → depletion_date=evaluation_date; mínimo incluye opening.
17. Demanda confirmada incorporada en M05 se conserva cuantitativamente por ID.
18. M07 conserva composición M05 y no reañade entradas.
19. Umbrales directos usan tipo autorizado; P-STK-004/P-STK-005 solo para fecha resuelta.
20. Coverage maximum exige demanda >0 aplicable; ramas exclusivas; tolerancia RATE trazada.
21. M08 descuenta primero cantidad ya incorporada en M05 y luego ledger previo.
22. `incorporated + allocated` nunca supera pending; no suelo cero ante inconsistencia.
23. M08 no inventa prioridad; plan suma exactamente absorción; no reescribe M07.
24. R-STK-004 no se amplía fuera de M08/M07.
25. M02/M03 sin fórmula/default implícito.
26. Contradicción no se resuelve heurísticamente.
27. Sin defaults normativos; determinismo.

---

## 35. Pruebas mínimas futuras

Cubrir al menos: identidad rules/parameters/snapshot/forecast; histórico con forecast_version indebida; forecast sin versión; disponibilidad/snapshot; vacío evidenciado; parámetros efectivos; P-STK-006; ventana histórica; aplicabilidad de demanda; cobertura; movimientos duplicados/mismo día/fuera de horizonte/NOT_APPLICABLE; M06; propuesta; mezcla de contextos; proyección diaria/opening cero/saldo negativo/incertidumbre; composición de demanda confirmada M05; M07 actual/proyectado/umbrales/fechas; M08 pedido ya incluido total/parcialmente en M05, ledger previo, sobreconsumo, plan inválido y absorción; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 36. Exclusiones v0.1

Fuera de alcance: forecasting interno; ventas→demanda; tasa→calendario; vigencia futura implícita; cutoff intradía; tolerancia temporal implícita; optimización/EOQ; fórmula normativa stock_minimum/safety_stock; imputación; resolución heurística; prioridad M08; costes TCO derivados; acciones automáticas; persistencia SQL STK; API externa; cambios C0; CRC; decisión final.

---

## 37. Estado

**Contrato v0.9:** DEPURADO FINAL DE COMPOSICIÓN.  
**Hallazgos A…G:** resueltos.  
**Hallazgos H1…H2:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación.  
**M02/M03:** sin fórmula cuantitativa ni default implícito.  
**Siguiente paso:** AUDIT 2 FINAL independiente.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
