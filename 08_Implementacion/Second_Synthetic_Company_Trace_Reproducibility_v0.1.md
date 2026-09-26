# EIOS — Reproducibilidad de trazas del caso 002 v0.1

**Resultado:** las trazas C0 raíz e hijas usan ahora `created_at` a medianoche
UTC de `purchase.operation_date`. Dos reconstrucciones independientes del
material 002 producen payloads de traza idénticos. En una composición local
de las ocho capacidades y QTG, los dos terminales también coincidieron
exactamente, incluido su fingerprint.

## DISEÑAR → AUDITAR

La auditoría de composición demostró `trace_id` estable y `created_at`
variable por el valor por defecto de `Trace`. El ejemplo 001 ya normalizaba
la fecha en su preparador. Se aplica ese mismo criterio únicamente a los
preparadores de prueba del caso 002; no se cambia `Trace`, `build_trace`,
la fachada ni un contrato cerrado.

## DEPURAR → AUDITAR 2

Las pruebas reconstruyen dos veces la traza raíz y los dos inputs hijos, y
comparan sus payloads serializados completos. La suite focalizada de C0,
escenarios, NI y las observaciones 001 dio 21 pruebas satisfactorias.
La composición exploratoria repetida dio terminales y fingerprints iguales;
el estado fue `PARTIALLY_COMPLETED` y la ruta `FORBIDDEN` en ambos.

## CERRAR → MATERIALIZAR → CI

Se modifican solo `tests/test_second_synthetic_company_c0.py` y
`tests/test_second_synthetic_company_scenarios.py`, más este documento.
Todavía no hay runner público 002 ni paquete exportable; el siguiente paso
es extraer las declaraciones 002 de los módulos de test a una fuente única
consumible por el runner y las pruebas. La ejecución sigue siendo
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Integración sujeta a CI de PR.
