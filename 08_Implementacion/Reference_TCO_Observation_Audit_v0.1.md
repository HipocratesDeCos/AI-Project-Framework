# EIOS — Reference TCO Observation: auditoría y diseño v0.1

**Base:** `main @ c2f52d857e624868677974f2f6fa7a4e83ab20d4`.
**Estado:** diseño auditado; implementación pendiente.

## DISEÑAR

Capturar el `TCOResult` que se produjo en la misma invocación TCO del caso
de referencia. Un sidecar separado deberá vincularlo al terminal, compra y
contexto sintéticos. La vista describirá el alcance exacto de los componentes
incluidos, sin presentar un coste total empresarial universal.

## AUDITAR — productor y fixture

`build_provenanced_tco_invoker` congela `TCOInput`, exige igualdad de todos
los campos de `PurchaseOperation`, comprueba identidad decisión/escenario,
ejecuta `calculate_tco` una vez y reduce el resultado con `adapt_tco`.
`TCOResult` conserva valor, moneda, componentes contribuyentes, componentes
sin resolver y limitaciones. `CapabilityExecution` solo conserva estado,
disponibilidad y pendientes: **no tiene referencias de traza TCO**.

El caso actual construye `TCOInput` sin `attributable_costs`. Su operación
sintética declara 10 unidades a 20,50 EUR. El productor devuelve
`value=205.00 EUR`, `contributing_components=(ACQUISITION,)`, ningún
componente sin resolver y `complete=true`. Ese `complete` significa que no
faltan importes entre los componentes aportados al contrato, no que todos los
costes posibles de la empresa estén representados. El propio motor excluye
conversión de divisa, costes financieros, almacenaje, obsolescencia,
devoluciones y las extensiones GAP-TCO-01.

PRICE devuelve un precio de referencia unitario sintético de 20,25 EUR,
mientras este TCO representa 205,00 EUR para la adquisición de 10 unidades.
La vista no debe compararlos como importes homogéneos ni inferir ahorro.

## DEPURAR — riesgos de interpretación y duplicación

- No fabricar `trace_references` desde el nombre de un componente o desde
  la huella del terminal. La observación puede vincular compra/contexto y
  terminal mediante huellas, pero debe declarar `trace_references=[]` si el
  productor y el adaptador no proporcionan trazas.
- No ejecutar `calculate_tco` otra vez para componer el HTML.
- No deducir que costes no informados valgan cero: `attributable_costs=()`
  describe la entrada disponible, no una declaración universal de ausencia.
- No clonar la maquinaria de captura de un solo uso de PRICE. Antes de
  implementar TCO, extraer solo el mecanismo genérico que ambas capacidades
  puedan compartir, sin diluir sus validaciones específicas ni cambiar las
  firmas de los builders cerrados.

## AUDITAR 2 — contrato mínimo propuesto

Una sesión observada TCO, exclusiva del recorrido de referencia, llamará al
productor una sola vez después de validar la misma compra/contexto que el
builder existente. Tras adaptar, conservará copias defensivas de `TCOResult`
y `CapabilityExecution`. Rechazará segundo uso, acceso prematuro y captura
tras fallo. El cierre cotejará identidad de caso, compra, contexto, estado y
pendientes TCO con el terminal único de esa ejecución.

El sidecar incluirá huellas del terminal, compra, contexto, entrada TCO y
resultado; `contributing_components`, `unresolved_components`, `limitations`
y un indicador explícito de que el fixture no aporta costes atribuibles
adicionales. La vista usará la expresión «coste de adquisición modelado» para
este fixture, exhibirá unidad y cantidad y señalará las exclusiones del
alcance. No se añadirá un campo TCO a `ExecutionOutcome`.

Pruebas necesarias: una sola producción, igualdad del estado con O1,
rechazo de compra/escenario ajeno, segundo uso y fallo, conservación de un
resultado incompleto con valor nulo, ausencia de trazas inventadas, y
compatibilidad de los terminales y del modo PRICE ya cerrado.

## CERRAR

Se autoriza el diseño de una observación sintética de TCO, no la afirmación
de que el coste total de propiedad de una empresa real esté calculado.
Permanecen `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, `NO_OPERATIONAL_EFFECT` y
`decision_authority=false`.

## MATERIALIZAR / CI

Esta unidad documental no cambia el runtime. La implementación y su CI
serán una unidad separada, con el mecanismo de captura compartido auditado
antes de exportar o representar TCO.
