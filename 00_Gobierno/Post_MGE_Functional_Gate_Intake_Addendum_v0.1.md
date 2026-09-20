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
