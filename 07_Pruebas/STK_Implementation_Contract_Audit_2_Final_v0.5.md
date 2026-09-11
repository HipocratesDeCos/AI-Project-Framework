# EIOS — STK Implementation Contract · Audit 2 Final v0.5

**Estado:** NO SUPERADA — DEPURACIÓN FINAL DE CORTE Y PARAMETRIZACIÓN REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.6  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.6 resuelve A1…A9, B1…B13, C1…C7, D1…D4 y E1…E3. El cruce final con STK-M05/M07 y con el Centro de Parametrización materializado detecta **3 ambigüedades físicas restantes**.

No requieren nueva política empresarial. Son cierres técnicos necesarios para evitar doble conteo temporal, confusión entre magnitudes físicas y umbrales de política, y consumo de configuraciones fuera de su vigencia.

**DICTAMEN:** NO CERRAR v0.6. Aplicar depuración F1…F3 y repetir Audit 2 Final.

---

## 2. F1 — Movimiento en `evaluation_date` frente a stock de apertura

**Tipo:** BLOQUEANTE.

M05 parte del stock actual disponible y añade/resta **movimientos futuros**. Con granularidad diaria, admitir `effective_date == evaluation_date` deja indeterminado si el movimiento ya está incorporado en el snapshot de apertura. Sin un corte intradía autorizado, sumarlo podría duplicar la misma realidad operativa.

**Corrección requerida para v0.1:**

- el stock de apertura representa la situación a `evaluation_date`;
- todo movimiento `KNOWN` que contribuya a la proyección debe ser estrictamente futuro:

`evaluation_date < effective_date <= horizon_end`;

- un movimiento fechado en `evaluation_date` no se incorpora por inferencia;
- una futura extensión podría admitirlo únicamente mediante una semántica de cutoff intradía explícita, trazable y autorizada.

Esto no elimina el movimiento: evita decidir técnicamente si ya está o no incluido en el stock de apertura.

---

## 3. F2 — Umbrales empresariales no son cantidades físicas de inventario

**Tipo:** BLOQUEANTE.

v0.6 declara correctamente que `NormalizedQuantity` representa una magnitud física. Sin embargo, `StockMaximumBasis.direct_quantity` y `ExcessToleranceBasis.quantity` reutilizan ese tipo para umbrales/políticas empresariales. Un máximo o tolerancia no es stock físicamente existente.

**Corrección requerida:** introducir una representación especializada equivalente a:

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

Reglas mínimas:

- `KNOWN` exige valor finito, no negativo y trazabilidad;
- artículo/unidad compatibles con el cálculo;
- `purpose` debe coincidir con el consumidor;
- `applicable_reference_date` debe coincidir con `stock_reference.reference_date`;
- no se infiere vigencia futura de un umbral actual;
- esta estructura representa autoridad/configuración de umbral, no cantidad física.

`StockMaximumBasis.direct_quantity` y `ExcessToleranceBasis.quantity` deben consumir este tipo.

---

## 4. F3 — Vigencia temporal de parámetros configurados

**Tipo:** BLOQUEANTE.

v0.6 valida `parameters_version`, pero el Centro de Parametrización cerrado ya materializa configuraciones con `valid_from`, `valid_to` y recuperación histórica mediante `get_configuration_at(...)`. La versión por sí sola no demuestra que el valor concreto sea aplicable a la fecha en que STK lo consume, especialmente para M07 sobre referencias futuras.

STK no debe duplicar ni reinterpretar la lógica de vigencia del Centro de Parametrización.

**Corrección requerida:** `ConfiguredParameterValue` debe conservar una afirmación explícita de aplicabilidad ya resuelta por la autoridad de parametrización, equivalente a:

```text
applicable_reference_date: date
configuration_ref: str
```

Un valor `KNOWN` solo puede consumirse cuando:

- su `parameters_version` coincide con `DecisionContext.parameters_version`;
- `configuration_ref` identifica la configuración/autorización efectiva utilizada;
- `applicable_reference_date` coincide con la fecha para la que el cálculo exige el parámetro.

Aplicaciones mínimas:

- `P-STK-006` para demanda histórica → `applicable_reference_date == evaluation_date`;
- `P-STK-004` y `P-STK-005` en M07 → `applicable_reference_date == stock_reference.reference_date`.

Si no existe configuración resuelta para una fecha futura, STK no reutiliza silenciosamente la configuración actual ni el valor inicial del catálogo.

La resolución `valid_from/valid_to` permanece aguas arriba, bajo el Centro de Parametrización; STK consume el resultado trazable y no introduce política de zonas horarias o selección de configuración.

---

## 5. Verificación de autoridad

F1…F3 no autorizan:

- valores iniciales como defaults;
- creación de nuevos parámetros;
- modificación del Centro de Parametrización;
- cambios en C0;
- forecasting;
- transformación ventas → demanda;
- prioridad M08;
- decisiones automáticas.

Los cambios son exclusivamente de tipado, corte temporal y prueba de vigencia.

---

## 6. Resultado

- A1…A9: resueltos.
- B1…B13: resueltos.
- C1…C7: resueltos.
- D1…D4: resueltos.
- E1…E3: resueltos.
- F1…F3: abiertos en v0.6.

**Siguiente paso:** DEPURAR v0.7 → repetir Audit 2 Final.
