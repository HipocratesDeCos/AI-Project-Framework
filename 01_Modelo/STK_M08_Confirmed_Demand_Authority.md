# EIOS — STK-M08 · Autoridad metodológica de pedido confirmado y absorción de exceso

**Versión:** 1.0
**Estado:** APROBADO — STK-M08 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

STK-M08 representa la existencia de demanda comercial firme y suficientemente evidenciada que absorberá total o parcialmente un exceso identificado por STK-M07.

Es una excepción contextual evidenciada. No elimina, modifica ni recalcula retroactivamente el exceso original.

## 2. Pedido confirmado y evidencia mínima

Un pedido solo es `CONFIRMED_ORDER` cuando existe evidencia verificable y vigente que identifica como mínimo:

- `Pedido_ID`;
- cliente;
- artículo;
- cantidad comprometida;
- fecha del pedido;
- fecha de confirmación;
- estado vigente;
- fecha prevista de entrega;
- fuente de la evidencia.

La mera indicación `Pedido_Confirmado = Sí` no constituye evidencia suficiente.

## 3. Cantidad aplicable

Solo es absorbible la cantidad confirmada del mismo artículo normalizado que permanece pendiente de servir y cuya entrega es aplicable al horizonte temporal evaluado.

La unidad del pedido y del exceso debe ser la misma unidad base normalizada. La política debe conservar el horizonte, fecha de referencia, estado y evidencia utilizados.

Cada asignación conserva `Pedido_ID`, cantidad aplicada y escenario de exceso. Una misma cantidad pendiente de servir no puede asignarse más de una vez al mismo o a distintos excesos.

## 4. Relaciones cuantitativas

`absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)`

`residual_excess = max(0, excess_quantity - absorbed_excess)`

Se preservan conjuntamente `excess_quantity`, `absorbed_excess` y `residual_excess`.

- Si `absorbed_excess = 0`, el pedido no mitiga el exceso.
- Si `0 < absorbed_excess < excess_quantity`, el exceso queda parcialmente mitigado.
- Si `absorbed_excess = excess_quantity`, queda totalmente absorbido por demanda confirmada.

La absorción nunca puede exceder el exceso original ni la cantidad confirmada aplicable pendiente de servir.

## 5. Estados empresariales

- `NO_EXISTE`: no existe pedido confirmado relacionado y esa ausencia está determinada.
- `NO_APLICABLE`: existe pedido evidenciado, pero no corresponde al mismo artículo, no queda cantidad pendiente aplicable, queda fuera del horizonte o no existe un exceso al que aplicar la excepción.
- `APLICABLE_Y_VALIDADA`: existe pedido confirmado vigente, compatible y evidenciado, y la absorción se calcula con entradas determinables.
- `NO_VERIFICABLE`: falta evidencia requerida, existen contradicciones materiales o no puede demostrarse la vigencia.

`NO_VERIFICABLE` se corresponde con `NOT_VERIFIABLE`; `NO_APLICABLE`, con `NOT_APPLICABLE`. Ninguno puede reducir el exceso.

## 6. Cambios, cancelaciones y parcialidad

Cancelaciones, modificaciones, entregas parciales y cambios de fecha requieren evidencia vigente y una nueva evaluación trazable. La cantidad aplicable es siempre la pendiente de servir en la fecha evaluada.

Una entrega ya servida no se reutiliza como absorción futura. Un cambio no reescribe evaluaciones históricas y conserva versión, fecha efectiva y fuente.

## 7. Ausencia, contradicción y autoridad

Si falta evidencia, existen contradicciones materiales o el pedido no está vigente, la excepción es `NO_VERIFICABLE` o `NO_APLICABLE`, según corresponda, y no reduce el exceso.

STK-M08 constituye evidencia de mitigación. No equivale a autorización de compra, cancelación, reducción de stock ni otra decisión automática.

La interpretación posterior corresponde a las reglas de evaluación de EIOS y a la autoridad decisional humana.

## 8. Continuidad

`STK-M01…M08` quedan cerrados. `STK-M09…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
