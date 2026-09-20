# EIOS — Post-MGE Functional Gate Intake Addendum v0.1

**Baseline:** `main @ 1e03a092ab752e997d6e07e2cf81204a31a77f12`

## Propósito

Añadir al contrato de continuidad post-BL-007 los gates descubiertos tras cerrar MGE, sin modificar los gates anteriores.

## FIN002

Para declarar `READY_FOR_DESIGN` deben existir:

- semántica exacta de “después de considerar la operación”;
- valor canónico post-operación;
- productor/fuente autorizado;
- identity/provenance hacia PurchaseOperation + DecisionContext;
- `P-FIN-003` resuelto y evidenciado;
- tratamiento fail-closed.

Finance Basic `working_capital` actual no satisface automáticamente este intake.

## STK002

Para declarar `READY_FOR_DESIGN` deben existir:

- cobertura proyectada posterior a la compra;
- productor físico de esa cobertura;
- `P-STK-004` resuelto y evidenciado;
- productor de estado de necesidad justificada;
- semántica de ausencia/indeterminación;
- separación respecto a M07/R-STK-003.

## PRE

Para declarar `READY_FOR_DESIGN` deben existir:

- temporality ligada físicamente a `P-PRE-001`;
- semántica ejecutable de `P-PRE-004`;
- semántica ejecutable de `P-PRE-005`;
- definición autorizada de “precio máximo recomendado”;
- bridge provenance-safe Price Intelligence → Rule.

## Regla

Una instrucción genérica de continuar no sustituye estos materiales cuando el gate exige productor, dato o semántica específica.


## Reconciliación FIN002 — 20/09/2026

El intake FIN002 quedó satisfecho mediante:

- `01_Modelo/FIN002_Post_Operation_Working_Capital_Authority_v0.1.md`;
- `08_Implementacion/R_FIN_002_Technical_Contract_v0.1.md`;
- `PostOperationWorkingCapitalPosition`;
- binding SHA-256 a la `PurchaseOperation` exacta;
- `PostOperationWorkingCapitalEvidence`;
- `ResolvedConfiguration(P-FIN-003) + ParameterConfigurationEvidence`;
- política fail-closed.

Materialización integrada por PR #249 en:

```text
main @ b77b16d5af5d9c1035a01ecb827ebcb4c47d9551
```

CI #1017:

```text
1723 passed
8 warnings
SQL SUCCESS
```

**FIN002 intake: CLOSED / MATERIALIZED / CI VALIDATED.**

Los apartados STK002 y PRE permanecen vigentes sin cambios.


## Reconciliación STK002 — 20/09/2026

El intake STK002 quedó satisfecho mediante:

- `01_Modelo/STK002_Projected_Coverage_Justified_Need_Authority_v0.1.md`;
- `08_Implementacion/R_STK_002_Technical_Contract_v0.1.md`;
- `ProjectedCoverageAfterPurchase`;
- `JustifiedNeedState`;
- binding SHA-256 a la `PurchaseOperation` exacta;
- evidencias separadas de cobertura y necesidad;
- `ResolvedConfiguration(P-STK-004) + ParameterConfigurationEvidence`;
- política fail-closed.

Materialización integrada por PR #252 en:

```text
main @ be13aad7d1dde788ef6e79cf262c1a7e91ed7374
```

CI #1023:

```text
1767 passed
8 warnings
SQL SUCCESS
```

**STK002 intake: CLOSED / MATERIALIZED / CI VALIDATED.**

El apartado PRE permanece vigente sin cambios.


## Reconciliación PRE003 — 20/09/2026

El gate PRE-G04 y el intake específico de R-PRE-003 quedaron satisfechos mediante:

- `01_Modelo/PRE003_Recommended_Price_Ceiling_Authority_v0.1.md`;
- `08_Implementacion/R_PRE_003_Technical_Contract_v0.1.md`;
- `RecommendedPriceCeiling`;
- binding SHA-256 a la `PurchaseOperation` exacta;
- `RecommendedPriceCeilingEvidence`;
- moneda exacta;
- política fail-closed;
- separación física `PR ≠ PMR`.

Materialización integrada por PR #255 en:

```text
main @ a16a6343a43dd72a5676f351ecb28bcfa1b94250
```

CI #1029:

```text
1789 passed
8 warnings
SQL SUCCESS
```

**R-PRE-003 intake: CLOSED / MATERIALIZED / CI VALIDATED.**

Permanecen vigentes:

- PRE-G01 — temporalidad provenance-safe ligada a P-PRE-001 para R-PRE-001;
- PRE-G02 — semántica ejecutable de P-PRE-004 para R-PRE-001;
- PRE-G03 — semántica ejecutable de P-PRE-005 para R-PRE-002;
- PRE-G05 — bridge Price Intelligence → Rules cuando sea aplicable a R-PRE-001/002.

R-PRE-003 no requiere Price Intelligence → Rule en v0.1.
