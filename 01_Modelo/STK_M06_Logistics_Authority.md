# EIOS — STK-M06 · Autoridad metodológica de pedidos pendientes y tránsito

**Versión:** 1.0
**Estado:** APROBADO — STK-M06 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

STK-M06 representa cantidades de un artículo cuya compra está formalmente reconocida pero que todavía no se han incorporado al stock disponible.

Se miden en la unidad base normalizada del artículo y solo pueden considerarse entradas futuras cuando su existencia, cantidad y estado están suficientemente evidenciados.

## 2. Estados logísticos mínimos

- `PENDING_ORDER`: compra confirmada cuya recepción aún no consta como iniciada o materializada.
- `IN_TRANSIT`: cantidad cuya expedición o movimiento hacia el destino está suficientemente evidenciado, sin recepción final confirmada.

Estos estados son mutuamente excluyentes para una misma cantidad de un mismo suministro en un mismo instante. La terminología fuente puede mapearse a ellos únicamente mediante una regla documentada y trazable.

## 3. Identidad, evidencia y atributos

Cada entrada debe conservar como mínimo el pedido u origen documental, artículo, cantidad y unidad, proveedor, estado, fecha prevista de recepción y evidencia disponible.

La identidad del suministro y su origen documental deben permitir detectar que dos registros representan la misma cantidad. Sin identidad o referencia suficiente no se suman como entradas independientes.

La fecha prevista puede proceder del compromiso confirmado del proveedor, del pedido autorizado o de otra fuente empresarial reconocida. Nunca se inventa a partir de ausencia de información.

## 4. Uso en proyección y stock actual

Las cantidades STK-M06 no forman parte del stock físico disponible actual. Pueden utilizarse como entradas previstas en STK-M05 únicamente cuando cumplen sus requisitos de evidencia y temporalidad.

La inclusión ocurre en la fecha prevista de recepción evidenciada y conforme a la versión de política aplicable. Una fecha prevista no equivale a recepción confirmada.

Esta autoridad permite la inclusión condicionada por evidencia; no valida los valores iniciales “Sí” de `PYE-002` y `PYE-003` como incorporación incondicional.

## 5. Transiciones y doble contabilización

Un suministro no puede contabilizarse simultáneamente como pedido pendiente y en tránsito. Cuando cambia de estado, se conserva la identidad del suministro, el estado anterior, el nuevo estado, la fecha efectiva del cambio, su evidencia y la versión de política aplicada.

La proyección utiliza una sola representación vigente de cada cantidad. El historial de estados aporta trazabilidad, no cantidades adicionales.

Si una recepción confirmada cubre solo parte de la cantidad, la parte recibida sale de STK-M06 y la cantidad restante solo permanece cuando su estado y evidencia vigentes lo justifican. Cancelaciones, cambios de cantidad o de fecha requieren evidencia y actualización trazable; no se deducen por silencio.

## 6. Recepción confirmada

Cuando una recepción está confirmada y evidenciada, la cantidad correspondiente deja de pertenecer a STK-M06 y pasa al stock recibido o disponible conforme a la política aplicable.

La transición conserva la relación entre pedido, tránsito y recepción. La salida de STK-M06 y el alta en stock no pueden producir dos incrementos proyectivos para la misma cantidad.

## 7. Ausencia y contradicción

Si falta cantidad, estado, referencia documental o evidencia necesaria, la entrada es `UNKNOWN / NOT_EVIDENCED`, nunca cero ni recepción confirmada.

`UNKNOWN / NOT_EVIDENCED ≠ 0`.

Un elemento desconocido no se incorpora silenciosamente a la suma de entradas futuras. Las contradicciones entre fuentes permanecen explícitas y su resolución general se cerrará en `STK-M10`.

## 8. Frontera de autoridad y continuidad

STK-M06 aporta evidencia logística y temporal. No constituye por sí mismo autorización de compra, reposición o decisión empresarial.

Esta decisión no autoriza compras, fechas inferidas, estados inferidos, inclusión sin evidencia, doble conteo ni implementación del motor cuantitativo STK.

`STK-M01…M06` quedan cerrados. `STK-M07…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
