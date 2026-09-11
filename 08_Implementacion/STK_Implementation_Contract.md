# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.12  
**Estado:** DEPURADO K1…K8 — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2  
**Catálogo físico de parámetros:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**.

STK materializa únicamente semántica, relaciones y cálculos previamente autorizados. No crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisiones automáticas.

STK produce métricas, estados y evidencia operativa. Rules conserva `R-STK-001…004`; CRC conserva resolución de conflictos; MED conserva integración; la decisión final permanece en la persona autorizada.

La implementación ejecutable permanece bloqueada hasta superar `AUDIT 2 FINAL → CERRAR`.

---

## 3. Frontera C0 y paquete físico

STK reutiliza `DecisionContext` y no modifica `PurchaseOperation`, `Evidence`, `EvidenceValidation`, `Rule`, `Assessment` ni `Trace`.

`PurchaseOperation.quantity` no se convierte automáticamente en cantidad STK normalizada porque C0 no contiene la unidad base objetivo ni el ámbito operativo STK.

Paquete previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

`eios.stock` puede importar contratos estables de `eios.core`; `eios.core` no depende de `eios.stock`.

---

## 4. Estados y principio `state ↔ payload`

Estados de datos STK:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

Reglas transversales:

1. `KNOWN` exige todos los campos materiales requeridos por la semántica concreta, valor finito cuando sea cuantitativo y trazabilidad suficiente.
2. Un campo empresarial que puede estar ausente se representa físicamente como opcional; la implementación no fabrica valores para satisfacer el esquema.
3. Para un valor singular, `state != KNOWN` implica que no se presenta un valor cuantitativo determinado como si fuese verdadero. Las alternativas contradictorias se conservan mediante referencias de conflicto, no seleccionando una.
4. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
5. `NOT_APPLICABLE` significa exclusión demostrada por la semántica vigente; no equivale a ausencia.
6. Un cero `KNOWN` requiere evidencia explícita suficiente.

Estados específicos pueden extender esta taxonomía sin redefinirla, por ejemplo `UNBOUNDED` de M04 o `NO_EXISTE / NO_APLICABLE / APLICABLE_Y_VALIDADA / NO_VERIFICABLE` de M08.

---

## 5. Ámbito empresarial STK

```text
StockScope
├── company_id: str
└── operational_scope_id: str
```

- `company_id` identifica el ámbito empresarial utilizado por el Centro de Parametrización.
- `operational_scope_id` identifica la organización/unidad operativa concreta a la que pertenecen stock y consumo.
- Ambos son referencias canónicas suministradas aguas arriba; STK no inventa jerarquías, relaciones padre-hijo, redistribuciones entre centros ni equivalencias de ámbito.
- Si la organización no distingue una subunidad operativa, el adaptador puede utilizar la referencia canónica que la autoridad de datos defina para el ámbito empresarial completo; STK no la deduce.

Toda combinación cuantitativa STK exige compatibilidad de ámbito, además de artículo, unidad y fecha cuando corresponda.

---

## 6. Contexto e identidad

```text
StockComputationContext
├── decision_context: DecisionContext
├── scope: StockScope
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

```text
StockResultIdentity
├── decision_id: str
├── scenario_id: str
├── rules_version: str
├── parameters_version: str
├── data_snapshot_id: str
├── company_id: str
├── operational_scope_id: str
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

Los cinco identificadores C0 se derivan sin transformación de `DecisionContext`. Ámbito, artículo, fecha, unidad y versión metodológica proceden del contexto STK. Los consumidores exigen afinidad exacta de identidad.

Método de demanda:

- `AUTHORIZED_FORECAST` exige `forecast_version != null`;
- `HISTORICAL_CONSUMPTION` exige `forecast_version == null`;
- no se arrastra una versión de forecast a una evaluación histórica por disponibilidad técnica.

---

## 7. Colecciones evidenciadas

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` con fuente o traza suficiente significa **vacío evidenciado**. Una colección ausente no se materializa como tupla vacía `KNOWN`.

Cuando `state != KNOWN`, `items` no se utiliza para calcular un resultado determinado; puede conservarse evidencia parcial únicamente con semántica explícita de diagnóstico, no como suma parcial silenciosa.

---

## 8. Magnitud física normalizada

```text
NormalizedQuantity
├── scope: StockScope
├── article_id: str
├── value: Decimal | null
├── unit: str
├── source_unit: str | null
├── normalization_ref: str | null
├── state: StockDataState
├── source_ref: str | null
├── effective_date: date | null
└── trace_refs: tuple[str, ...]
```

Representa magnitud física, no saldo analítico ni umbral empresarial.

`KNOWN` exige:

- `value` finito y no negativo;
- `unit == context.base_unit` cuando se consume en un cálculo STK;
- ámbito y artículo compatibles;
- `effective_date` cuando la operación requiera vigencia puntual;
- fuente o traza suficiente;
- `source_unit` conocido;
- si `source_unit != unit`, `normalization_ref` obligatorio y reproducible.

Una conversión no demostrada impide `KNOWN`. `state != KNOWN` permite `value/source_ref/effective_date/source_unit/normalization_ref` nulos cuando precisamente faltan esos datos.

---

## 9. Umbral cuantitativo autorizado M07

```text
AuthorizedQuantityThreshold
├── scope: StockScope
├── article_id: str
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── applicable_reference_date: date
├── authority_ref: str | null
├── authority_version: str | null
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

`KNOWN` exige valor finito no negativo, ámbito/artículo/unidad compatibles, propósito correcto, `authority_ref`, `authority_version`, fuente/traza y fecha exactamente aplicable a la referencia consumidora.

Un umbral no adquiere vigencia futura por inferencia y no representa inventario físico. En estado no determinado las referencias cuya evidencia falte pueden ser nulas; no se inventan IDs de autoridad.

---

## 10. Valores autorizados M02/M03 sin fórmula implícita

M02 y M03 se materializan como valores ya autorizados externamente; STK no los calcula.

```text
AuthorizedStockPolicyQuantity
├── concept: STOCK_MINIMUM | SAFETY_STOCK
├── scope: StockScope
├── article_id: str
├── quantity: Decimal | null
├── unit: str
├── state: StockDataState
├── policy_ref: str | null
├── policy_version: str | null
├── derivation_ref: str | null
├── valid_from: date | null
├── valid_to: date | null
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `KNOWN` exige cantidad finita/no negativa, unidad base compatible, ámbito/artículo correctos, política/versión, `derivation_ref`, vigencia, fuente y trazabilidad;
2. `derivation_ref` referencia el artefacto autorizado que permite reconstruir las variables/evidencias exigidas por M02/M03 —demanda esperada, `lead_time`, variabilidad, protección/servicio y método/fórmula cuando correspondan— sin duplicar ese artefacto dentro de STK;
3. `valid_to`, si existe, debe ser `>= valid_from`;
4. solo se consume cuando `valid_from <= reference_date` y, cuando exista, `reference_date <= valid_to`;
5. ausencia/insuficiencia → `UNKNOWN / NOT_EVIDENCED`, nunca cero;
6. `STOCK_MINIMUM` y `SAFETY_STOCK` no son equivalentes ni se componen implícitamente;
7. el contenedor no crea fórmula, consumidor de regla ni valida los valores iniciales `STK-001/002`.

---

## 11. Parámetros configurados e IDs canónicos

Los IDs físicos consumidos por `eios.stock` son exclusivamente los IDs del catálogo:

```text
STK-001 … STK-006
PYE-001 … PYE-006
```

La notación documental `P-STK-* / P-PYE-*` utilizada en matrices de relación **no** se utiliza como `parameter_id` físico.

```text
ConfiguredParameterValue
├── parameter_id: str
├── company_id: str
├── value: Decimal | int | bool | null
├── unit: str | null
├── state: StockDataState
├── parameters_version: str
├── applicable_reference_date: date
├── configuration_ref: str | null
├── source_ref: str | null
├── normalization_ref: str | null
└── trace_refs: tuple[str, ...]
```

STK consume configuración ya resuelta por el Centro de Parametrización; no reimplementa `valid_from/valid_to`, zonas horarias ni selección efectiva.

`KNOWN` exige:

- `company_id == context.scope.company_id`;
- `parameters_version == DecisionContext.parameters_version`;
- `configuration_ref` y fuente/traza;
- fecha aplicable coincidente con la requerida por el cálculo;
- valor no nulo del tipo esperado;
- unidad autorizada/normalizada cuando corresponda.

Sin fallback a valores iniciales del catálogo.

---

## 12. Frontera PYE v0.1

La función técnica queda cerrada así:

- `PYE-001` **sí es operativo** como configuración del horizonte M05 conforme a §13.
- `PYE-002` y `PYE-003` **no son gates configurables operativos en v0.1**. M06 determina elegibilidad de pedido pendiente/tránsito mediante evidencia, estado y temporalidad. Sus valores iniciales `Sí` no incluyen movimientos incondicionalmente y un eventual valor configurado no altera v0.1 hasta una extensión contractual autorizada.
- `PYE-004` no es operativo en v0.1: el motor no deriva `effective_date` desde `lead_time`; consume fechas evidenciadas.
- `PYE-005` no transforma ventas en consumo o demanda.
- `PYE-006` no actúa como umbral de `R-STK-001`.

Una futura activación de `PYE-002…006` exige autoridad contractual específica; no se infiere por nombre o valor.

---

## 13. Horizonte M05 — `PYE-001`

```text
ProjectionHorizon
├── parameter: ConfiguredParameterValue   # parameter_id == "PYE-001"
├── horizon_days: int | null
├── horizon_end: date | null
├── state: StockDataState
└── trace_refs: tuple[str, ...]
```

Para `KNOWN`:

- parámetro `PYE-001` `KNOWN` y aplicable a `evaluation_date`;
- entero positivo y no booleano;
- unidad autorizada/normalizada a días;
- `horizon_days == parameter.value` normalizado;
- `horizon_end = evaluation_date + horizon_days` días naturales;
- la granularidad v0.1 es diaria y queda versionada por `methodology_version`.

Los movimientos contribuyentes cumplen `evaluation_date < effective_date <= horizon_end`.

`90 días` del catálogo no es default. Si `PYE-001` no está evidenciado/configurado, la proyección completa no es `KNOWN`.

---

## 14. Composición de compromiso de apertura

```text
StockCommitmentComponent
├── commitment_id: str
├── demand_segment_id: str | null
├── confirmed_demand_id: str | null
├── scope: StockScope
├── article_id: str
├── quantity: Decimal
├── unit: str
├── source_unit: str | null
├── normalization_ref: str | null
├── effective_date: date
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Cantidad finita/no negativa; mismo ámbito/artículo/unidad/fecha que `stock_committed`; `commitment_id` único. Si la unidad fuente difiere, exige `normalization_ref`.

Cuando representa reserva/asignación vinculada a demanda comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios, estables y trazables. Un compromiso no comercial no recibe IDs inventados.

Una composición `KNOWN` suma exactamente `stock_committed.value`.

---

## 15. Demanda confirmada ya incorporada

```text
IncorporatedDemandQuantity
├── confirmed_demand_id: str
├── quantity: Decimal
├── unit: str
├── demand_segment_ids: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

Se agrega por pedido preservando segmentos. Cantidad finita/no negativa; unidad única; segmentos no vacíos y sin duplicados.

---

## 16. Disponibilidad de stock

```text
StockAvailabilityInput
├── context: StockComputationContext
├── stock_on_hand: NormalizedQuantity
├── stock_committed: NormalizedQuantity
└── committed_components: CollectionEnvelope[StockCommitmentComponent]
```

Para resultado `KNOWN`:

- on-hand y committed `KNOWN`;
- ámbito/artículo/unidad = contexto;
- `effective_date == evaluation_date` en ambas cantidades;
- composición `KNOWN`, trazable, compatible, sin IDs/segmentos duplicados y suma exacta.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

```text
StockAvailabilityResult
├── identity: StockResultIdentity
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── unit: str
├── state: StockDataState
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
└── trace_refs: tuple[str, ...]
```

El déficit no se oculta. No existe tolerancia implícita de antigüedad.

---

## 17. Consumo M01 — frontera mensual canónica

STK v0.1 consume periodos mensuales ya clasificados como **consumo real** conforme a M01; no clasifica ventas, compras o salidas genéricas como consumo.

```text
ConsumptionPeriod
├── scope: StockScope
├── article_id: str
├── period_id: str
├── period_start: date
├── period_end: date
├── evidenced_days: int | null
├── quantity: Decimal | null
├── unit: str
├── state: StockDataState
├── methodology_version: str
├── aggregation_ref: str | null
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

`aggregation_ref`/trazas deben permitir reconstruir los registros fuente, cantidad/unidad fuente y conversiones aplicadas. STK no necesita duplicar esos registros dentro del periodo.

`KNOWN` exige:

- ámbito/artículo/unidad compatibles;
- `quantity` finita y no negativa;
- periodo válido y completo;
- `evidenced_days == (period_end - period_start).days + 1`;
- `methodology_version` aplicable;
- agregación/normalización/fuente trazables.

Periodo sin evidencia suficiente → `UNKNOWN / NOT_EVIDENCED`. Cero solo con evidencia explícita de consumo cero.

---

## 18. Política histórica de demanda

```text
RequiredPeriodSpec
├── period_id: str
├── period_start: date
└── period_end: date
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue   # parameter_id == "STK-006"
├── required_periods: tuple[RequiredPeriodSpec, ...]
├── period_calendar_ref: str
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

`STK-006` `KNOWN`, aplicable a `evaluation_date`, versión correcta, entero positivo no booleano y unidad autorizada/normalizada a meses/periodos mensuales. Número de periodos coincidente; IDs únicos; intervalos válidos/no solapados; calendario trazable. No se generan meses implícitamente. Extensión futura solo con autoridad trazable.

---

## 19. Demanda histórica

`HistoricalDemandInput = context + policy + CollectionEnvelope[ConsumptionPeriod]`.

Resultado `KNOWN` solo con colección `KNOWN`, correspondencia exacta uno-a-uno de IDs/intervalos, periodos completos, homogéneos, mismo ámbito y no contradictorios.

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta, rellena ni duplica la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
forecast_version = null
```

---

## 20. Demanda común y forecast autorizado

```text
DemandRateResult
├── identity: StockResultIdentity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand: Decimal | null
├── unit: str
├── state: StockDataState
├── reference_date: date
├── applicable_from: date | null
├── applicable_to: date | null
├── applicability_source_ref: str | null
├── window_or_horizon: str | null
├── source_ref: str | null
├── forecast_version: str | null
└── trace_refs: tuple[str, ...]
```

Para forecast `KNOWN`:

```text
context.forecast_version != null
context.forecast_version == forecast.forecast_version
identity.forecast_version == forecast.forecast_version
DemandRateResult.forecast_version == forecast.forecast_version
```

Además exige mismo ámbito/artículo/unidad, tasa finita/no negativa, horizonte/aplicabilidad, fuente y traza.

Histórico: todas las referencias de forecast son nulas.

No existe forecasting interno, ventas→demanda ni fallback entre métodos.

**Frontera de proyección:** `DemandRateResult` no se expande automáticamente a un calendario M05 en v0.1. La proyección solo descuenta movimientos futuros explícitos y autorizados. Una futura transformación tasa/forecast→calendario deberá cerrar su propia política de calendarización y reconciliación con demanda confirmada.

---

## 21. Cobertura M04

```text
CoverageState = FINITE | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

La tasa debe ser aplicable a `evaluation_date` y compartir identidad/ámbito.

```text
coverage_days = stock_available / daily_demand    # daily_demand > 0
```

Cero confirmado/evidenciado/aplicable → `UNBOUNDED`, `coverage_days = null`. No se representa infinito numérico.

```text
CoverageResult
├── identity: StockResultIdentity
├── coverage_days: Decimal | null
├── state: CoverageState
├── demand: DemandRateResult
└── trace_refs: tuple[str, ...]
```

---

## 22. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id: str
├── supply_identity: str | null
├── supplier_id: str | null
├── supply_document_ref: str | null
├── confirmed_demand_id: str | null
├── demand_segment_id: str | null
├── scenario_id: str | null
├── scope: StockScope
├── article_id: str
├── direction: INFLOW | OUTFLOW
├── quantity: Decimal | null
├── unit: str | null
├── source_unit: str | null
├── normalization_ref: str | null
├── effective_date: date | null
├── state: StockDataState
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Dirección autorizada:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Movimiento `KNOWN` contribuyente exige ID único, cantidad finita/no negativa, ámbito/artículo/unidad compatibles, fuente/traza, normalización demostrada cuando proceda y:

```text
evaluation_date < effective_date <= horizon_end
```

Sin cutoff intradía ni roll-forward.

`NOT_APPLICABLE` evidenciado no contribuye/contamina; `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA` propaga incertidumbre desde su fecha conocida y, si no existe fecha demostrable, desde `evaluation_date`.

Para `AUTHORIZED_DEMAND` comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios. Un segmento no se repite entre movimientos ni coincide con uno incorporado en opening.

Para `PENDING_ORDER | IN_TRANSIT` `KNOWN`, además son obligatorios:

- `supply_identity` estable;
- `supplier_id`;
- `supply_document_ref`;
- fecha prevista evidenciada (`effective_date`);
- cantidad/unidad/fuente/trazas.

La misma cantidad no puede estar simultáneamente pendiente y en tránsito. Parcialidades usan identidades/segmentos de suministro distinguibles. Recepción confirmada sale M06 y no produce un segundo incremento.

`PROPOSED_PURCHASE` exige escenario coincidente, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 23. Proyección M05

```text
StockProjectionInput
├── context: StockComputationContext
├── opening: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon: ProjectionHorizon
└── scenario_id: str
```

Para proyección completa `KNOWN`:

- escenario coincide con `DecisionContext.scenario_id`;
- `horizon` `KNOWN` y derivado de `PYE-001`;
- opening `KNOWN` e identidad compatible;
- movimientos y colección satisfacen §22;
- ningún `demand_segment_id` confirmado existe simultáneamente en opening y M05.

Para cada día natural futuro desde `evaluation_date + 1` hasta `horizon_end` inclusive:

```text
closing_stock_date = previous_closing_stock
                   + sum(known inflows effective_date == date)
                   - sum(known outflows effective_date == date)
```

No existe orden intradía. Saldo negativo se conserva.

```text
ProjectionPoint
├── reference_date: date
├── projected_stock: Decimal | null
├── state: StockDataState
└── trace_refs: tuple[str, ...]
```

```text
StockProjectionResult
├── identity: StockResultIdentity
├── horizon: ProjectionHorizon
├── points: tuple[ProjectionPoint, ...]
├── minimum_projected_stock: Decimal | null
├── depletion_date: date | null
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── state: StockDataState
└── trace_refs: tuple[str, ...]
```

La composición acumulada de demanda confirmada parte de opening y añade exclusivamente segmentos M05 contabilizados, agregados por pedido.

Incertidumbre fechada contamina desde su fecha; sin fecha demostrable, desde evaluación. Datos posteriores no restauran `KNOWN` sin una resolución autorizada.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Opening cero `KNOWN` → `depletion_date = evaluation_date`; en otro caso, primera fecha futura determinada con cierre `<= 0`.

---

## 24. Frontera R-STK-001 / M02 / M03

STK entrega métricas/evidencia, no decisiones. M02/M03 se representan mediante `AuthorizedStockPolicyQuantity`, pero v0.1 no calcula sus valores ni crea relaciones de regla no demostradas. Ausencia ≠ cero. Valores iniciales no son defaults.

---

## 25. Referencia de stock M07

```text
StockReferenceValue
├── identity: StockResultIdentity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date: date
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

`CURRENT_AVAILABLE` deriva exclusivamente de `StockAvailabilityResult`, fecha = evaluación, valor no negativo y conserva demanda confirmada ya descontada en committed.

`PROJECTED` deriva de un `ProjectionPoint` concreto de M05, puede ser negativo y conserva la composición acumulada hasta esa fecha. No se vuelve a sumar M06 ni propuesta.

---

## 26. Base máximo y tolerancia M07

`StockMaximumBasis` tiene ramas mutuamente exclusivas:

- `DIRECT_QUANTITY` → `AuthorizedQuantityThreshold` purpose `STOCK_MAXIMUM`;
- `COVERAGE_MAXIMUM` → `ConfiguredParameterValue(parameter_id="STK-004") + DemandRateResult`.

Todo debe ser `KNOWN`, mismo ámbito/artículo/unidad y aplicable a `stock_reference.reference_date`.

Cobertura máxima exige parámetro efectivo, unidad días normalizada, demanda > 0 y aplicable a la fecha:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`ExcessToleranceBasis` tiene ramas mutuamente exclusivas:

- `QUANTITY` → `AuthorizedQuantityThreshold` purpose `EXCESS_TOLERANCE`;
- `RATE` → `ConfiguredParameterValue(parameter_id="STK-005")` normalizado/trazado para la fecha de referencia.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

Sin inferencia porcentual por valor o nombre.

---

## 27. Exceso M07

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados:

```text
NO_EXCESS
WITHIN_TOLERANCE
EXCESS
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Clasificación determinada:

- `stock_reference <= stock_maximum` → `NO_EXCESS`, exceso 0;
- `stock_maximum < stock_reference <= excess_threshold` → `WITHIN_TOLERANCE`, exceso 0;
- `stock_reference > excess_threshold` → `EXCESS`.

Los ceros anteriores son calculados con entradas `KNOWN`; nunca sustituyen ausencia.

M07 conserva identidad, referencia/fecha, composición incorporada de demanda confirmada, máximo, tolerancia, umbral, exceso y trazas.

Únicas relaciones parámetro↔regla confirmadas:

- `STK-004 → R-STK-002` directa;
- `STK-004 → R-STK-003` derivada;
- `STK-005 → R-STK-003` derivada.

---

## 28. M08 — demanda confirmada

```text
ConfirmedDemandRecord
├── confirmed_demand_id: str
├── order_id: str | null
├── customer_id: str | null
├── scope: StockScope
├── article_id: str
├── pending_quantity: NormalizedQuantity
├── order_date: date | null
├── confirmation_date: date | null
├── expected_delivery_date: date | null
├── business_status: str | null
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref: str | null
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo colección `KNOWN` vacía/trazada significa `NO_EXISTE`.

Para `APLICABLE_Y_VALIDADA` son obligatorios todos los campos empresariales mínimos de M08 y:

```text
pending_quantity.state == KNOWN
pending_quantity.scope == allocation_scope.scope
pending_quantity.effective_date == allocation_scope.evaluation_date
order_date <= confirmation_date <= allocation_scope.evaluation_date
expected_delivery_date > allocation_scope.excess_reference_date
expected_delivery_date <= allocation_scope.horizon_end
```

La desigualdad respecto a `excess_reference_date` es estricta porque v0.1 no posee cutoff intradía. Una entrega anterior o igual al exceso proyectado no corrige M05 ex post mediante M08.

`NO_VERIFICABLE` permite que los campos cuya evidencia falta sean nulos; no se fabrican fechas, IDs empresariales o cantidades.

---

## 29. Ledger M08 activo y evidenciado

```text
AllocationLedgerEntry
├── allocation_entry_id: str
├── confirmed_demand_id: str
├── allocated_quantity: Decimal
├── unit: str
├── decision_id: str
├── scenario_id: str
├── excess_reference_date: date
├── allocation_result_ref: str
└── trace_refs: tuple[str, ...]
```

`allocated_quantity` es finita y estrictamente positiva; unidad compatible; referencias no vacías.

```text
AllocationLedgerSnapshot
├── reference_date: date
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── entries: tuple[AllocationLedgerEntry, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Reglas:

1. solo `KNOWN + entries=()` con fuente/traza significa “sin asignaciones activas evidenciadas”;
2. `state != KNOWN` no se interpreta como suma cero y bloquea absorción determinada;
3. `KNOWN` exige `reference_date == allocation_scope.evaluation_date`, fuente/traza y `allocation_entry_id` único;
4. el snapshot contiene únicamente asignaciones activas que todavía reservan cantidad pendiente contra reutilización en esa fecha;
5. histórico liberado/consumido se conserva aguas arriba, no se suma como activo;
6. cada entry conserva decisión, escenario, fecha de exceso y resultado original;
7. STK consume el snapshot y no implementa persistencia ni decide liberaciones históricas.

---

## 30. Plan M08 sin prioridad implícita

```text
DemandAllocation
├── confirmed_demand_id: str
├── quantity_to_apply: Decimal
├── unit: str
├── allocation_source_ref: str
└── trace_refs: tuple[str, ...]
```

`quantity_to_apply` finita y estrictamente positiva. No existe prioridad implícita entre pedidos.

---

## 31. Reconciliación opening/M05/M08

Para cada pedido aplicable:

```text
incorporated_before_M08
= cantidad del confirmed_demand_id ya incorporada
  en stock_reference.incorporated_confirmed_demand

already_allocated
= suma activa del confirmed_demand_id
  en AllocationLedgerSnapshot KNOWN

remaining_allocatable
= pending_quantity
  - incorporated_before_M08
  - already_allocated
```

Misma unidad; cantidades >= 0; `incorporated_before_M08 + already_allocated <= pending_quantity`.

Si se supera `pending_quantity`, no se aplica suelo cero: existe inconsistencia/contradicción y M08 no produce absorción determinada. Una misma cantidad no se usa dos veces entre opening, M05 y M08.

---

## 32. Alcance y absorción M08

```text
AllocationScope
├── identity: StockResultIdentity
├── scope: StockScope
├── article_id: str
├── evaluation_date: date
├── excess_reference_date: date
├── horizon_end: date
├── horizon_source_ref: str
└── trace_refs: tuple[str, ...]
```

Debe ser compatible con `ExcessResult`/identidad STK. Horizonte explícito y trazable.

Solo pedidos `APLICABLE_Y_VALIDADA`, mismo ámbito/artículo/unidad, pending `KNOWN` vigente y entrega estrictamente posterior al exceso y dentro del horizonte participan. IDs únicos. Ledger/plan solo usan IDs presentes. Plan no supera `remaining_allocatable`. Colección o ledger no `KNOWN` hace M08 no determinable. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Materialización por pedido exige:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si `absorbed_excess == 0`, plan vacío. Si `absorbed_excess > 0`, plan ausente/incompleto/sobreasignado bloquea el reparto.

El nuevo ledger añade entries únicas y trazables para las asignaciones del plan. M08 conserva exceso original, total aplicable, absorbido, residual, plan, ledger resultante, identidad y trazas; no reescribe M07.

---

## 33. M09 — ausencia

No existe imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default.

Cada resultado no determinado conserva estado, fuente esperada/referencias disponibles y trazas suficientes para identificar qué dependencia impidió el cálculo.

Un objeto no puede marcarse `KNOWN` mediante valores sintéticos destinados únicamente a satisfacer el esquema físico.

---

## 34. M10 — contradicciones

`CONFLICTING_DATA` bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad arbitraria.

Una resolución externa autorizada conserva evidencia original, autoridad aplicada y nueva evaluación trazable. STK no selecciona una fuente conflictiva por sí mismo.

---

## 35. Error estructural vs incertidumbre empresarial

Se rechaza estructuralmente, entre otros:

- Decimal no finito;
- cantidad física `KNOWN` negativa;
- `KNOWN` sin payload material obligatorio;
- payload cuantitativo determinado presentado bajo un estado no determinado cuando la semántica no lo permite;
- identidad/versiones/ámbitos incompatibles;
- uso físico de IDs `P-STK-*` o `P-PYE-*` como `parameter_id`;
- histórico con `forecast_version` no nula o forecast con versión nula/diferente;
- stock actual de otra fecha/ámbito;
- composición committed incompleta/inconsistente/duplicada;
- conversión de unidad no demostrada;
- periodo M01 `KNOWN` sin agregación/normalización reconstruible;
- M02/M03 `KNOWN` sin política/versionado/derivación/vigencia;
- `PYE-001` inválido o no aplicable;
- ventana histórica inválida;
- movimiento `KNOWN` no estrictamente futuro o fuera de horizonte;
- M06 `KNOWN` sin proveedor/origen/supply identity;
- configuración efectiva incorrecta;
- umbral directo M07 sin autoridad/versionado;
- umbral/demanda fuera de vigencia;
- ramas discriminadas simultáneas;
- pending M08 no vigente;
- fechas comerciales incompatibles o entrega `<= excess_reference_date` para `APLICABLE_Y_VALIDADA`;
- ledger `KNOWN` de otra fecha, sin evidencia, entry duplicada o sin procedencia;
- `incorporated + allocated > pending`;
- plan M08 inválido.

Se representa como incertidumbre empresarial, según autoridad aplicable: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/política/umbral no verificables, movimiento incompleto, demanda no aplicable y M08 no verificable.

---

## 36. Determinismo

- `Decimal`; no NaN/infinito.
- Fechas explícitas; sin reloj implícito.
- Sin redondeo empresarial implícito.
- Sin prioridad M08.
- Sin selección automática de método de demanda.
- Sin calendarización implícita de tasa.
- Misma entrada + identidad + ámbito + versiones + configuración + política + opening/M05 + ledger activo → mismo resultado.

---

## 37. Defaults prohibidos

No se hardcodean ni activan por ausencia:

- 15 % safety stock;
- 30/90 días de cobertura;
- 10 % tolerancia;
- 12 meses de consumo;
- 90 días de horizonte;
- `PYE-002…005 = Sí`;
- 15 días de riesgo.

Ausencia de configuración/política no activa valores iniciales.

---

## 38. Interfaces de autoridad

- Evidence/QTG valida evidencia.
- Centro de Parametrización resuelve configuración y vigencia por `company_id`.
- Adaptadores de datos suministran ámbito operativo y normalización trazable; STK no inventa mappings.
- Políticas M02/M03 suministran valores autorizados y `derivation_ref`; STK no ejecuta fórmulas no autorizadas.
- Rules consume hechos STK; STK no emite `BUY/BLOCK/NEGOTIATE`.
- CRC queda fuera.
- TCO no recibe costes derivados STK v0.1.
- Decision Twin no mezcla escenarios/versiones/ámbitos.
- MED integra sin transferir autoridad.
- `R-STK-004` queda limitado a M08 sobre exceso M07; no se amplía por interpretación.

---

## 39. Invariantes ejecutables

1. No decisión automática; C0 inmutable.
2. Ausencia ≠ cero; `KNOWN` exige payload/traza; vacío evidenciado ≠ ausencia.
3. Ámbito empresarial/operativo forma parte de la identidad STK y no se mezcla.
4. Magnitud física ≠ umbral empresarial.
5. Identidad conserva decision/scenario/rules/parameters/snapshot/company/scope y forecast cuando aplica.
6. IDs físicos de parámetros son `STK-* / PYE-*`, nunca `P-STK-* / P-PYE-*`.
7. Histórico exige forecast nulo; forecast exige versión exacta no nula.
8. M02/M03 se representan sin fórmula; política, versión, derivación y vigencia obligatorias para `KNOWN`.
9. Stock actual pertenece a `evaluation_date` y ámbito; déficit visible.
10. `stock_committed` `KNOWN` tiene composición completa/reconciliada.
11. Demanda confirmada ya descontada en opening queda identificada cuantitativamente.
12. M01 conserva ámbito, metodología y agregación/normalización reconstruible.
13. Histórico/forecast exclusivos; ventas ≠ demanda; sin fallback.
14. `STK-006` usa configuración efectiva y ventana exacta/completa.
15. Coverage consume demanda aplicable; cero demostrado → `UNBOUNDED`.
16. `PYE-001` gobierna horizonte; 90 días no es default.
17. `PYE-002…006` no adquieren función v0.1 no autorizada.
18. `movement_id` único; `supply_identity` evita doble conteo M06.
19. M06 `KNOWN` conserva proveedor/origen documental.
20. Movimiento contribuyente estrictamente futuro; sin cutoff intradía.
21. `demand_segment_id` evita doble uso opening↔M05 y permite parcialidades legítimas.
22. Source kind/dirección compatibles; `NOT_APPLICABLE` no contamina.
23. Tasa no crea calendario; propuesta exige escenario.
24. Proyección diaria; saldo negativo preservado; incertidumbre temporal.
25. Opening cero → `depletion_date=evaluation_date`; mínimo incluye opening.
26. Composición confirmada M05 se acumula por pedido/segmento; M07 la conserva y no reañade entradas.
27. Umbrales directos M07 conservan authority/version; `STK-004/005` solo para fecha resuelta.
28. Coverage maximum exige demanda >0 aplicable; ramas exclusivas; tolerancia RATE trazada.
29. M08 usa pending vigente y entrega estrictamente posterior a excess_reference_date.
30. Ledger ausente ≠ ledger vacío; solo snapshot `KNOWN` puede descontar asignaciones activas.
31. M08 descuenta cantidades ya incorporadas en opening/M05 y ledger activo previo.
32. `incorporated + allocated` nunca supera pending; no suelo cero ante inconsistencia.
33. Ledger conserva decisión, escenario, fecha de exceso y resultado original.
34. M08 no inventa prioridad; plan suma exactamente absorción; no reescribe M07.
35. `R-STK-004` no se amplía fuera de M08/M07.
36. Contradicción no se resuelve heurísticamente.
37. Sin defaults normativos; determinismo.

---

## 40. Pruebas mínimas futuras

Cubrir al menos:

- identidad C0 + company/scope + forecast;
- rechazo de mezcla entre ámbitos;
- IDs físicos `STK/PYE` y rechazo de alias documentales `P-*`;
- estados no determinados construibles sin valores ficticios y `KNOWN` incompleto rechazado;
- M02/M03 `KNOWN/UNKNOWN`, derivation_ref, vigencia y no equivalencia;
- disponibilidad, déficit, composición committed completa/incompleta y normalización;
- M01 periodo `KNOWN`, cero evidenciado, ausencia, metodología/aggregation_ref;
- histórico/forecast, `STK-006`, ventana exacta y aplicabilidad;
- coverage finita/unbounded/unknown;
- `PYE-001` correcto, ausente, 90 no default, tipo bool rechazado;
- no efecto v0.1 de `PYE-002…006` fuera de su frontera cerrada;
- movimientos duplicados/mismo día/fuera de horizonte/NOT_APPLICABLE;
- M06 proveedor/origen/supply identity, pending↔transit, parcialidades;
- propuesta y mezcla de escenarios;
- proyección diaria, opening cero, saldo negativo, incertidumbre temporal;
- M07 umbral directo sin versión/fecha, máximo por cobertura, tolerancia y ramas exclusivas;
- M08 pedido ya incluido opening/M05, pending de otra fecha, entrega `<= excess_reference_date`, ledger ausente vs vacío `KNOWN`, snapshot antiguo, entry duplicada, ledger previo, sobreconsumo, plan inválido y absorción;
- M09/M10;
- no decisión, no defaults y reproducibilidad.

---

## 41. Exclusiones v0.1

Fuera de alcance:

- forecasting interno;
- ventas→demanda;
- expansión automática de una tasa de demanda a calendario M05;
- vigencia futura implícita;
- cutoff intradía;
- tolerancia temporal implícita;
- jerarquías o redistribución entre ámbitos operativos;
- optimización/EOQ;
- fórmula normativa de `stock_minimum/safety_stock`;
- imputación;
- resolución heurística de contradicciones;
- prioridad M08;
- persistencia propia del ledger;
- costes TCO derivados;
- acciones automáticas;
- persistencia SQL STK;
- API externa;
- cambios C0;
- CRC;
- decisión final.

---

## 42. Criterio de cierre contractual

El contrato puede pasar a `CERRADO` únicamente si Audit 2 Final independiente confirma simultáneamente:

1. cobertura implementable de M01…M10 dentro de las fronteras declaradas;
2. ausencia de fórmulas, parámetros o defaults no autorizados;
3. ausencia representable sin valores ficticios;
4. identidad/ámbito/versionado reproducibles;
5. no doble conteo opening/M05/M06/M08;
6. compatibilidad con C0, Centro de Parametrización, Rules, CRC y MED;
7. autoridad humana intacta;
8. cero hallazgos bloqueantes.

Hasta entonces no está autorizada la creación de `eios/stock` ejecutable.
