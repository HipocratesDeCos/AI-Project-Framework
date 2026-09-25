# EIOS — Reference Decision Twin Observation: auditoría v0.1

**Base auditada:** `main @ 7c5c019182155fa4885174e2a9283b1d5685f285`.
**Estado:** frontera de captura diseñada; runtime sin cambios.

## DISEÑAR

Evaluar una observación de `DecisionTwinComparison` producida en la misma
invocación que entrega `DECISION_TWIN` a O1. Conservar la comparación
estructural de alternativas sintéticas y sus límites, sin generar preferencia
ni decisión.

## AUDITAR — material exacto y productor

`build_provenanced_decision_twin_invoker` congela preparación O4/O2/O3 y
alternativas ligadas a entradas de escenario. Al invocarse, comprueba el
contexto raíz frente a la preparación, exige dos alternativas con referencias
y escenarios únicos, reconstruye Stage 2 con el wrapper de procedencia y
produce `DecisionTwinComparison`. `adapt_twin` reduce a estado O1, trazas y
atributos ausentes. El objeto de comparación completo no queda en el
terminal.

El caso de referencia representa `REF-BUSINESS-001-ALT-1` y `ALT-2`, cada
una sobre un escenario hijo con un binding C0 propio. La comparación actual
reporta `viability=VIABLE` en ambas; `results` contiene `R-DAT-003=FALSE` y
estado `COMPLETED` en ambas; `conditions={}`, `consequences={}` y
`risk_refs=()` en ambas. `differences=()`, `missing_attributes=()`,
`viability_differences=()` y `consequence_differences=()`. Las trazas son las
de los dos escenarios hijos. El resultado no contiene cantidades/precios
comparados ni ranking de alternativas.

## DEPURAR — interpretaciones improcedentes

- `VIABLE` describe el resultado del productor Stage 2 bajo los inputs
  sintéticos disponibles. No concede viabilidad económica empresarial ni
  autorización de compra, especialmente con QTG `NO_APTO` en una variante.
- Las dos representaciones sin diferencia en los atributos incluidos no
  implican equivalencia comercial universal; riesgos y consecuencias están
  vacíos porque el fixture no los aporta.
- `representation_ref` es una etiqueta transitoria, no identidad persistida
  ni alternativa seleccionada. La comparación no puntúa ni prefiere.
- Decision Twin y Scenario Coordination reconstruyen Stage 2 por separado.
  Coincidir en trazas y fuentes no demuestra que hayan compartido una única
  evaluación Stage 2 en memoria.
- No ejecutar otra vez Stage 2 para producir un HTML ni reconstruir
  `DecisionTwinComparison` desde el `CapabilityExecution` terminal.

## AUDITAR 2 — contrato mínimo de observación

Un invocador observado congelará preparación y alternativas, reutilizará la
misma producción y el mismo adaptador del builder cerrado y capturará copias
defensivas del resultado de **su** única llamada O1. Se rechazará segundo
uso, captura prematura y fallo. Antes del productor se comparará toda la
compra raíz del fixture, pues el wrapper actual comprueba decisión/escenario
pero no cantidad, precio o moneda frente a una compra fuente completa.

El sidecar separado vinculará fuentes, compra/contexto, comparación, trazas,
estado O1 y terminal mediante huellas y procedencia sintética. La futura
vista etiquetará alternativas como representaciones, expresará los
atributos presentes y ausentes y dirá que no hay selección ni ranking.
Pruebas: producción única, rechazo de identidad ajena antes del productor,
resultado parcial si faltan atributos, igualdad con O1, trazas y terminales
de ambas variantes sin cambio; regresión de las observaciones existentes.

## CERRAR

Se cierra la frontera de diseño de una comparación descriptiva sin autoridad.
Permanecen `SYNTHETIC`, `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`,
`NO_OPERATIONAL_EFFECT` y `decision_authority=false`.

## MATERIALIZAR / CI

Esta unidad solo añade la auditoría. La captura y exportación requieren
unidades separadas y CI satisfactoria antes de integración.

## Unidad posterior — captura materializada

`ObservedDecisionTwinInvoker` congela compra raíz, preparación y
alternativas. Antes de producir comprueba cada campo de la compra contra el
fixture, reutiliza `build_provenanced_decision_twin_comparison` y `adapt_twin`
y captura resultado y `CapabilityExecution` de la misma llamada O1 con la
sesión común de un solo uso. Mantiene intacto el `__all__` público cerrado de
Decision Twin y la firma del builder existente.

El sidecar separado guarda fuentes, huellas, comparación, trazas, ejecución
O1 y terminal sintético. Declara `STRUCTURAL_DESCRIPTIVE_ONLY` y
`selected_alternative=null`. Su validador coteja compra y contexto raíz,
referencias únicas, estado y trazas O1, diferencias, faltantes y huellas.
No se exporta ni representa en HTML durante esta unidad de captura.
