# EIOS — Reference Price Observation: contrato de diseño v0.1

**Base:** `main @ 98d72147b8d8cc1b58963d4e78080140a89adbc3`.
**Estado:** diseñado y auditado; implementación en unidad posterior al diseño.

## DISEÑAR

Capturar `PriceIntelligenceResult` durante la misma invocación PRICE que
entrega `CapabilityExecution` a `run_mvp_execution`. El resultado de precio
podrá consultarse después como observación **sintética de lectura**, ligado al
terminal de referencia que acaba de ejecutar. No se incorpora a O1 ni se
convierte en precio aprobado, techo, orden o autoridad de compra.

La observación debe contener una copia inmutable del resultado tipado, su
huella canónica, el `CapabilityExecution` exacto emitido por el adaptador,
identidad de caso y compra/contexto, huella del terminal y límites sintéticos.
Su publicación requiere que PRICE figure exactamente una vez en el
`ExecutionOutcome` del mismo terminal y que su estado y trazas coincidan con
los capturados. No se admiten resultados desprendidos aportados por el caller.

## AUDITAR

`build_provenanced_price_invoker` congela `PriceIntelligenceInput` y
`PriceIntelligenceAssessmentContext`, valida la igualdad de contexto y de
**todos** los campos de `PurchaseOperation`, ejecuta `run_price_intelligence`
una vez y pasa el resultado a `adapt_price`. El invocador solo devuelve
`CapabilityExecution`; `PriceIntelligenceResult` se pierde en ese punto.

La función existente y su firma pública están cerradas. El nuevo camino debe
compartir la misma validación y producción, manteniendo intacto su retorno.
Un nuevo builder de referencia puede exponer una sesión de captura de un solo
uso y el invocador compatible con O1, sin aceptar un resultado ya producido.
La sesión no debe exponer una observación antes de la ejecución válida.

## DEPURAR

- **No** llamar de nuevo al motor de precios para poblar el visor.
- **No** envolver únicamente el `CapabilityExecution`: carece de `pr_value`,
  `currency`, `pr_status`, suficiencia y limitaciones.
- **No** modificar `ExecutionOutcome` ni la firma del builder actual.
- **No** aceptar un `PriceIntelligenceResult` externo como prueba de ejecución.
- **No** inferir un techo de precio o una decisión a partir de `pr_value`.

La refactorización interna admisible concentra validación y llamada al motor
en una función compartida por ambos builders. Debe demostrar que el builder
existente conserva todos sus resultados y rechazos previos. La captura ocurre
después de producir y adaptar correctamente, con copia defensiva; una segunda
invocación de la sesión observada se rechaza. Cualquier fallo impide publicar
una observación parcial.

## AUDITAR 2 — pruebas de aceptación

1. Caso sintético de referencia: exactamente una producción PRICE; resultado
   tipado y `CapabilityExecution` provienen de esa llamada.
2. Compra, decisión, escenario o snapshot ajenos: rechazo antes de producir.
3. Estado PRICE y trazas del terminal: igualdad exacta con la captura; una
   divergencia impide cerrar la observación.
4. Invocación doble, acceso prematuro, fallo del productor o del adaptador:
   sin observación publicable.
5. Resultados `PR_AVAILABLE`, `PR_LIMITED` y `PR_NOT_JUSTIFIABLE`: conservar
   valor opcional, moneda, suficiencia y limitaciones sin reinterpretación.
6. Builder PRICE existente y suite MVP: sin cambios de contrato ni regresión.

## CERRAR — límite de autoridad

Esta especificación autoriza únicamente el diseño de un artefacto adicional
para producto de referencia. El terminal y su observación conservan
`material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
`operational_path=FORBIDDEN`, `effect_scope=NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. `PR_AVAILABLE` significa que C1 produjo un precio
de referencia bajo su contrato; no otorga autoridad para negociar o comprar.

## MATERIALIZAR / CI

La implementación se realizará en una unidad separada, después de comprobar
que el diseño evita captura desacoplada y repetición del motor. Esta unidad
solo añade el contrato de diseño; la CI del PR confirma que el repositorio
permanece sin regresiones.

## Implementación y auditoría de la unidad siguiente

`eios/core/price_integration.py` comparte la validación de identidad y una
única llamada a `run_price_intelligence` entre el builder antiguo y
`build_reference_observed_price_invoker`. La sesión observada es de un solo
uso, conserva copias defensivas y no publica captura tras un fallo. Su
`reference_case_id` se compara con el terminal.

`execute_reference_business_case_with_price_observation` ejecuta la fachada
de referencia con esa sesión y cierra la observación inmediatamente después.
El cierre verifica la procedencia sintética, la presencia única de PRICE, la
igualdad exacta del `CapabilityExecution`, la identidad del resultado tipado
y sus trazas. El artefacto separado incorpora huellas del terminal, compra,
contexto y resultado PRICE. No se añade al terminal ni a O1.

`tests/test_reference_price_observation.py` cubre las dos variantes, una sola
producción PRICE, rechazo de identidad ajena y segundo uso, estado prematuro,
vínculo de caso y los tres estados funcionales de precio. La repetición de
ambas variantes con y sin observación mantiene exactamente las huellas
terminales originales. Suite local: **2336 passed, 6 warnings**.

La observación aún no se exporta por la CLI ni se representa en HTML. Eso
requerirá una unidad de presentación que valide este artefacto y explicite
que el precio de referencia sintético no es un techo ni una autorización.
