# EIOS — U1.1 · DISEÑO DEPURADO — FRONTEND VISUAL CEO

**Estado:** 🟡 DISEÑO DEPURADO — PENDIENTE AUDITORÍA 2
**Baseline:** `c059af68ad489f64d5ff1dfa7bf5f5a113588854`
**Diseño inicial:** `92ba626d64f493fddcf7824c163965e8e23e0bde`
**Auditoría 1:** `64a254983f26240f3a03d4b4bd7a41ae26ff660c`

## Frontera

`CEO → U1.1 Visual Frontend → U1 Application Boundary → O1 → Decision Support Package → U1.1 → CEO`

U1.1 no accede directamente a C0, PRICE, TCO, QTG, O2, O3, O4 ni Decision Twin.

## Semántica visual

Los colores, iconos, posición, tamaño y orden nunca expresan por sí mismos una recomendación empresarial. Todo estado crítico incluye texto explícito.

`NOT_EVALUABLE`, `FAILED`, `BLOCKED` y `PARTIALLY_COMPLETED` mantienen su semántica técnica literal.

## Resultado y decisión

El resultado EIOS se presenta en un bloque separado de cualquier acción humana. No existe botón `COMPRAR`, `APROBAR`, `RECHAZAR`, `NEGOCIAR` ni `ELEGIR MEJOR` conectado a una acción automática.

La decisión humana puede registrarse como una interacción posterior, pero su semántica y autoridad no forman parte del resultado EIOS.

## Identidad y contexto

IDs, fingerprints, snapshots y versiones se muestran como contexto de trazabilidad. La UI no permite editarlos libremente.

## Escenarios

Los escenarios se muestran con identidad, estado, resultados, limitaciones y trazabilidad. El orden de presentación no implica preferencia. No se muestra una puntuación agregada ni una etiqueta de “mejor escenario”.

## Evidencia

La UI muestra el estado proporcionado por EIOS. No recalifica evidencia ni sustituye QTG.

## Responsive

En viewport reducido se conserva el acceso a estados, limitaciones, evidencia y trazabilidad. No se ocultan mediante colapso irreversible.

## Accesibilidad

Todos los estados deben tener texto; navegación por teclado; foco visible; labels; mensajes asociados a campos; orden lógico de lectura; controles con nombre accesible; contraste suficiente; y ausencia de dependencia exclusiva del color.

## Componentes MVP

- `AppShell`
- `ExecutiveDashboard`
- `OperationForm`
- `EvidencePanel`
- `DecisionContextPanel`
- `ExecutionStatus`
- `ExecutiveResult`
- `ScenarioList`
- `TwinComparison`

Los componentes son presentacionales y consumen modelos de boundary. No contienen lógica analítica.

## Fuera de alcance

Framework específico, API pública, persistencia nueva, SSO, ranking, optimización, autonomía decisional y ejecución de compras.

**Criterio: listo para AUDITORÍA 2.**