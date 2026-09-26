# EIOS — Auditoría de composición E2E de la empresa ficticia 002 v0.1

**Dictamen:** la fachada existente acepta una ejecución exploratoria de las
ocho capacidades posteriores a QTG con el bundle 002, pero el material C0
actual no produce payloads reproducibles entre repeticiones. Se debe depurar
esa fecha antes de materializar un runner y un paquete verificable.

## DISEÑAR → AUDITAR

Se revisaron la fachada `run_reference_operational_simulation`, la frontera
`run_mvp_execution`/`execute_plan` y las fuentes 002 de las unidades previas.
Se hizo una invocación **local y efímera**, ensamblando esos materiales desde
sus helpers de prueba. No se guardó un terminal ni se abrió una ruta pública.

| Elemento | Resultado exploratorio | Lectura correcta |
|---|---|---|
| QTG | `APTO / ALTA` en `SYNTHETIC_TEST` y consumo `TEST_ONLY`. | Calidad de la proyección sintética; no satisface por sí sola el requisito C0. |
| PRICE, TCO | `COMPLETED`. | Sus fuentes declaradas se procesaron dentro del alcance de prueba. |
| Supplier Risk/Value | `PARTIALLY_COMPLETED`; `RISK:SUPPLIER-MOCK-002:RELIABILITY:NOT_DETERMINABLE`. | No se conoce la fiabilidad ni hay comparación de valor. |
| C0 | Capacidad `COMPLETED`; su Assessment R-DAT-003 es `TRUE` y CRC conserva `INFORMACIÓN INSUFICIENTE`. | Terminó el cálculo de C0; el resultado semántico sigue siendo insuficiente. |
| Decision Twin, Scenario Coordination, NI, Ladder | `COMPLETED`. | Comparación descriptiva y petición de información sintéticas; no eligen ni ejecutan compra. |
| Terminal | `PARTIALLY_COMPLETED`, ocho resultados O1 y QTG separado; `FORBIDDEN`, sin efecto ni autoridad. | La insuficiencia del proveedor se propaga al estado terminal. |

La secuencia fue `QTG → PRICE → TCO → SUPPLIER_RISK_VALUE → C0 →
DECISION_TWIN → SCENARIO_COORDINATION → NEGOTIATION_INTELLIGENCE →
NEGOTIATION_LADDER`. No hubo fallo de identidad al componer las fuentes.

## DEPURAR → AUDITAR 2

**Bloqueo demostrado:** `build_trace` da un `trace_id` reproducible, pero el
modelo `Trace` asigna `created_at` con la hora actual por defecto. Dos
construcciones consecutivas del C0 raíz 002 devolvieron el mismo `trace_id`
y diferentes `created_at`/payloads. Ocurrió también en los dos hijos.
La fachada incluye esas trazas en resultados de Twin/Scenario y NI/Ladder;
por tanto, no se puede prometer igualdad de terminales y sidecars al repetir
la ejecución tal como está preparado el material de prueba.

La depuración correcta es **fijar `created_at` a una fecha UTC derivada de
`purchase.operation_date` en los preparadores 002** y comprobar una
repetición exacta. El ejemplo 001 ya normaliza esa fecha; no hace falta
modificar `Trace`, la fachada o un contrato cerrado.

También hay una frontera de organización: los materiales 002 viven ahora en
helpers `tests/test_second_synthetic_company_*.py`. Un runner público no
debe importarlos. Antes de materializarlo, extraer las declaraciones
específicas de 002 a un módulo/fixture de ejemplo sin duplicar productores,
y dejar las pruebas como consumidoras de esa fuente única. Las capturas
observadas y sidecars requieren **la misma invocación** del terminal; no
se pueden convertir después desde resultados aislados.

## CERRAR → MATERIALIZAR → CI

Esta unidad cierra la auditoría, no el runner 002. Próxima secuencia:

1. Normalizar fechas de trazas raíz e hijas; probar igualdad del material
   serializado en dos reconstrucciones independientes.
2. Extraer fuentes 002 reutilizables sin importar módulos de pruebas.
3. Ejecutar la fachada con invocadores observados, cerrar sidecars contra
   el terminal y verificar una repetición exacta y una alteración adversa.
4. Presentar explícitamente `PARTIALLY_COMPLETED`, riesgo no determinable y
   `INFORMACIÓN INSUFICIENTE` en el paquete de revisión, sin convertir el
   `APTO` QTG en autorización decisional.

Se conservan
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
No se cambian código ni contratos en esta auditoría. La CI de PR verificará
que el documento no altera la suite.
