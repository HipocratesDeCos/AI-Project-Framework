# EIOS — Reference Business Case 001: auditoría de cierre v0.1

**Base auditada:** `main @ 0ccf81c3fa05e173616768c5cd6738aa1963ff0e`.
**Ámbito:** validación de producto con una operación de compra de una empresa
ficticia y dos variantes QTG de material sintético.

## DISEÑAR — criterio de cierre

El caso debe ejecutar el recorrido E2E autorizado, ofrecer dos calidades QTG
distinguibles, conservar identidad y huellas, permitir revisión humana y
repetición local, y mantener cerrada la ruta operacional. Esta auditoría no
declara que los resultados analíticos de negocio estén disponibles en el
artefacto terminal ni que la empresa ficticia represente todos sus procesos.

## AUDITAR — evidencia de implementación

| Capacidad o límite | Fuente verificable | Resultado |
| --- | --- | --- |
| Material físico de referencia | `tests/fixtures/projection_only_semantic_dataset_01/` y `tests/fixtures/reference_business_case_001_qtg_eligible/` | Dos fixtures sintéticos ligados por manifest y hashes de componentes. |
| Ejecución | `examples/reference_business_case_001.py`, `eios/core/reference_simulation_execution.py` | QTG, PRICE, TCO, SUPPLIER_RISK_VALUE, C0, DECISION_TWIN, SCENARIO_COORDINATION, NEGOTIATION_INTELLIGENCE y NEGOTIATION_LADDER. |
| Calidad funcional | `qtg_quality_result` del terminal | `NO_APTO/BAJA` y `APTO/ALTA` respectivamente. |
| Estado técnico | `execution_outcome` | `COMPLETED` en ambas variantes: finalización del recorrido, no aprobación QTG. |
| Procedencia y efecto | `case_provenance` y campos terminales | `SYNTHETIC`, `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, `NO_OPERATIONAL_EFFECT`, `decision_authority=false`. |
| Revisión | `examples/reference_business_case_review.py` | Comparación estática, controles QTG, motivos, evidencias, estados y trazas; huellas e invariantes comprobadas. |
| Paquete y repetición | `examples/reference_business_case_demo.py` | Generación en directorio nuevo; `--verify-dir` compara los tres archivos con una repetición usando el código y fixtures actuales. |

## DEPURAR — alcance real de las afirmaciones

`CapabilityExecution` conserva `capability`, `status`, `result_available`,
`trace_references`, `unresolved_items` y `failure_reason`. No transporta los
objetos analíticos de PRICE, TCO, riesgo, Twin, escenarios o negociación.
El terminal añade QTG, compra, contexto, procedencia y huellas, pero no un
informe con importes recomendados, alternativas clasificadas o decisiones.
La vista solo puede mostrar lo que el terminal preserva; una tabla de estados
no demuestra que todas las conclusiones de negocio hayan sido verificadas.

La negociación usa un wrapper que valida el C0 declarado contra compra y
contexto. Sigue sin probar que el contenido NI se derive causalmente de C0
ni que la invocación separada de C0 haya ejecutado ese mismo binding. La
verificación de repetición tampoco autentica el origen externo de los archivos.

## AUDITAR 2 — comprobaciones

Las pruebas `test_reference_business_case_001.py`,
`test_reference_business_case_review.py` y
`test_reference_business_case_demo.py` cubren secuencia, dos variantes,
límites sintéticos, trazas, revisión y repetición. La suite local en la
unidad precedente terminó con **2330 passed, 6 warnings**; la PR #344 y su
CI concluyeron satisfactoriamente. Esta unidad documental no altera código.

## CERRAR

**Reference Business Case 001 v0.1: cerrado como demostración técnica y de
calidad QTG sintética.** No se declara piloto empresarial, expediente real,
aprobación de compra, autoridad de negociación ni salida operacional.

## MATERIALIZAR — siguiente frontera

El siguiente trabajo de producto debe diseñar cómo conservar y presentar
resultados analíticos sustantivos con sus fuentes y límites, si se desea una
lectura de negocio además de la prueba de ejecución. Primero se auditarán los
contratos públicos de cada productor para ver qué resultado ya está disponible.
Un eventual artefacto nuevo deberá tener identidad, procedencia, vínculo causal
y alcance de autoridad explícitos. No se añadirá un campo inventado al
`ExecutionOutcome` cerrado ni se reconstruirá un resultado a partir de trazas.

## CI

La revisión de esta auditoría documental exige que las referencias de código
y la frontera descrita correspondan a `main`; la CI del PR confirma ausencia
de regresiones.
