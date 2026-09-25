# EIOS — Reference Scenario Coordination Observation Capture v0.1

**Base:** `main @ 9d04c20722bdf2a9b6bd4c61bb617b605194524d`  
**Ruta:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## Diseño

Capturar el paquete O2 producido durante la invocación `SCENARIO_COORDINATION`
del caso de referencia, junto con su `CapabilityExecution`, sus fuentes Stage 2
y las huellas del terminal. Las dos variantes conservan `SYNTHETIC`,
`SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, `NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. La captura no elige escenarios.

## Auditoría y depuración

- El invocador público existente reconstruye Stage 2 desde
  `ProvenancedScenarioAnalyticsInput` y sus `AssessmentTraceBinding`. No se
  admite un `O2SupportPackage` desprendido como entrada.
- Se extrae su productor interno común: la ruta normal adapta el paquete a
  capacidad; la ruta observada usa el mismo productor y adapta el mismo
  paquete una sola vez. La captura solo está disponible tras esa invocación.
- El wrapper observado fija la compra completa y las fuentes con copias
  profundas; rechaza otra compra o contexto y es de uso único.
- La validación coteja identidad del caso, scope, huellas, paquete O2 y
  capacidad terminal; además repite Stage 2 desde las fuentes para detectar
  incluso un paquete inventado cuyas huellas se hayan recalculado.

## Auditoría 2

- Ambos escenarios del fixture terminan `COMPLETED` y declaran viabilidad
  `VIABLE`; esto solo describe soporte sintético, sin recomendación ni
  aprobación QTG.
- `O2Comparison.differences.viability_result` registra los objetos completos
  como diferentes porque contienen distintos `scenario_id`. No se debe
  presentar esa diferencia estructural como diferencia de viabilidad de
  negocio: los dos valores `status` son `VIABLE`.
- El terminal y sus huellas se mantienen idénticos a la ejecución sin
  captura. Las pruebas cubren ambas variantes, manipulación con huellas
  recalculadas, compra o contexto extranjero y uso único.

## Cierre y materialización

La observación es una vista de soporte coordinado y conserva
`selected_scenario=null`. Se materializa en
`eios/core/reference_scenario_coordination_observation.py`,
`eios/rules/scenario_integration.py` y el ejecutable del caso de referencia.
La exportación HTML/JSON queda como unidad posterior. CI decide el cierre.
