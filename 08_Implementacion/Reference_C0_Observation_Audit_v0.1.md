# EIOS — Reference C0/CRC Observation: auditoría v0.1

**Base auditada:** `main @ f2d475338cbb6f68fb510747f9033abd0fa52a0b`.
**Estado:** frontera diseñada; captura y exportación pendientes.

## DISEÑAR

Determinar cómo conservar el resultado C0/CRC producido para la empresa
ficticia en la misma invocación O1, mostrando `Assessment`, `Trace` y el
resultado consolidado con procedencia y autoridad delimitadas.

## AUDITAR — productor y fuentes

El caso produce antes de O1 un `Assessment` y su `Trace` de `R-DAT-003`
mediante evidencia sintética de requisitos de decisión. El fixture declara el
único requisito `REQ-PROJECTION-QUALITY` como `SATISFIED`; el productor de
suficiencia y la regla generan `status=EVALUABLE`, `outcome=FALSE` y una traza
reproducible. La función `run_provenanced_assessments_vertical` valida la
compra y el contexto, el rule catalog, el hash de entrada, el hash del
Assessment y la reproducción de la traza. Después compone C0, CRC y el
paquete de soporte. El builder público congela los bindings y entrega solo
`c0_capability` a O1; el `RuleSetVerticalResult` completo no se conserva en el
terminal.

La comparación de ambos fixtures mediante la ruta actual confirma que el
`Assessment` y la traza raíz son iguales: `R-DAT-003=FALSE`, C0 `COMPLETED`.
Sin embargo, QTG es `NO_APTO/BAJA` en la variante negativa y `APTO/ALTA` en
la elegible. La declaración sintética de suficiencia C0 se construye por
separado y no se deriva del resultado QTG de esa ejecución. En concreto,
`R-DAT-003=FALSE` no significa que QTG haya aprobado la variante negativa.

CRC recibe `base_result="COMPRAR"` aportado por el caso. En este fixture el
valor es una base sintética del contrato CRC, no mandato empresarial, orden
de compra ni autorización decisional. La condición `FALSE` de la regla
individual y el texto de su razón deben exponerse en contexto, sin presentar
la base ni el consolidado como una acción aprobada.

## DEPURAR — límites de representación

- La traza C0 acredita reproducibilidad de la evaluación suministrada respecto
  de compra, contexto, regla y Assessment; no prueba que el requisito
  `SATISFIED` fue causado por el veredicto QTG de la misma ejecución.
- Una tabla con `COMPLETED` y `COMPRAR` sin el origen de la base y la
  divergencia QTG induciría una lectura de aprobación inexistente.
- La referencia C0 que utiliza negociación verifica procedencia del binding,
  pero no demuestra que la invocación separada de C0 y NI compartan el mismo
  resultado ejecutado. Una observación C0 no debe prometer esa causalidad.
- No reconstruir CRC a partir del estado O1 ni volver a llamar al productor
  para fabricar una vista; tampoco modificar `ExecutionOutcome` o el builder
  cerrado sin contradicción objetiva.

## AUDITAR 2 — contrato mínimo de captura futura

Un builder observado exclusivo del caso congelará bindings y `base_result`,
reutilizará `run_provenanced_assessments_vertical` y capturará una copia
defensiva del `RuleSetVerticalResult` de la **misma invocación** que entrega
`c0_capability` a O1. Usará la sesión de un solo uso compartida, rechazará
segunda llamada y captura tras fallo. El sidecar separado cotejará identidad
de caso, compra y contexto, resultado C0 del terminal, trazas y huellas de
fuentes y resultado. La validación reutilizará
`validate_assessment_trace_binding` para cada binding, sin revaluar una
regla de negocio.

Antes de mostrar el consolidado CRC, la vista deberá decir que
`base_result="COMPRAR"` es un dato sintético suministrado, distinguir el
`outcome=FALSE` de la regla del estado QTG y mostrar ambos QTG por separado.
Pruebas necesarias: una sola composición vertical, integridad del binding,
rechazo de compra/contexto ajenos, segundo uso y fallo, igualdad C0 con O1,
ambos fixtures y persistencia de terminales/PRICE/TCO/Supplier Risk.

## CERRAR

Se cierra únicamente la frontera de diseño. `R-DAT-003=FALSE`, C0
`COMPLETED` y cualquier consolidado sintético carecen de autoridad para
comprar. Continúan `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`,
`NO_OPERATIONAL_EFFECT` y `decision_authority=false`.

## MATERIALIZAR / CI

Esta unidad documental no modifica runtime, fixtures ni terminal. La
implementación y presentación se tratarán en unidades posteriores, con
pruebas propias y CI de sus PR.

## Unidad posterior — captura materializada

`ObservedRulesC0Invoker` reutiliza la sesión compartida de un solo uso.
Congela bindings y `base_result`, ejecuta
`run_provenanced_assessments_vertical` una vez y captura una copia defensiva
de `RuleSetVerticalResult` y del `c0_capability` que se entrega a O1. El
builder público conserva firma y comportamiento. Una validación fallida
consume la sesión y no ofrece captura parcial.

El sidecar C0/CRC lleva huellas de fuentes, resultado y terminal, QTG de la
misma variante, `qtg_c0_derivation_proven=false` y
`crc_base_origin=SUPPLIED_SYNTHETIC_BASE_RESULT`. Valida cada binding con el
contrato público de procedencia, coteja Assessment/Trace, estado C0 y trazas
con O1 e identidad CRC. En ambas variantes conserva `R-DAT-003=FALSE` y
el consolidado sintético `COMPRAR`; el terminal no cambia. La exportación y
el HTML permanecen fuera de esta unidad.
