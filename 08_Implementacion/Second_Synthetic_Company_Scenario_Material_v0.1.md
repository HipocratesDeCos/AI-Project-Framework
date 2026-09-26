# EIOS — Escenarios hijos de la empresa ficticia 002 v0.1

**Resultado de prueba:** la compra base de 15 unidades genera dos escenarios
de 16 y 17 unidades. Cada hijo tiene su propio `scenario_id`, compra,
RequirementSet C0, Assessment y Trace. Scenario Coordination construye el
soporte de ambos; Decision Twin ofrece una comparación estructural sin elegir
una alternativa.

## DISEÑAR → AUDITAR

Se reutiliza la preparación O4/O2/O3 con una política de prueba 002 y la
variable controlada `quantity_delta ∈ {1, 2}`. La entrada de cada hijo
clasifica el requisito de calidad como `UNDETERMINED` y evalúa R-DAT-003
sobre la compra hija exacta. Los dos invocadores observados existentes
reconstruyen Stage 2 y sus capturas en llamadas separadas.

## DEPURAR → AUDITAR 2

La prueba comprueba cantidades y trazas distintas, la captura de Scenario
Coordination, las dos referencias `REF-BUSINESS-002-ALT-1/2` de Decision Twin
y la ausencia de un campo de selección en su resultado. Una traza del primer
hijo insertada en el segundo se rechaza por incompatibilidad de escenario.
No se reutiliza una evaluación del caso 001 ni se presenta la comparación
como preferencia, ranking o decisión.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_scenarios.py`. Son capturas
aisladas en prueba, sin terminal E2E ni sidecars 002. Los resultados no
conceden autoridad ni efectos operacionales. La procedencia del bundle raíz
se mantiene en
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

La siguiente fuente para el segundo E2E es contenido sintético de
Negotiation Intelligence y Ladder ligado a la traza C0 raíz. Verificación
local focalizada: trece pruebas satisfactorias (escenarios 002, C0 002 y
observaciones de Scenario Coordination y Twin del caso 001). Integración
sujeta a CI de PR.
