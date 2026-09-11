# EIOS — STK-M05 · Autoridad metodológica de proyección de stock

**Versión:** 1.0
**Estado:** APROBADO — STK-M05 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

En EIOS, `stock_projection` representa la evolución proyectada del stock de un artículo a partir de una fecha de referencia.

La relación autorizada es:

`projected_stock = current_available_stock + expected_inflows - expected_outflows`

Todas las cantidades se expresan en la unidad base normalizada del artículo y se sitúan dentro de un horizonte temporal explícito.

## 2. Estado inicial, horizonte y trazabilidad

La proyección parte del stock disponible actual válido en una fecha explícita `as_of_date`. Debe conservar el horizonte evaluado, las fuentes utilizadas y la evidencia de cada movimiento futuro.

La política aplicable debe documentar la granularidad temporal, el horizonte y la fecha efectiva de su versión. Esta decisión no valida automáticamente los 90 días de `PYE-001`.

La correspondencia entre `as_of_date` y la identidad técnica canónica `evaluation_date` se declarará en el contrato posterior sin crear fechas paralelas o ambiguas.

## 3. Entradas previstas

Solo se incorporan reposiciones, recepciones u otros movimientos cuando su existencia, cantidad y fecha están suficientemente evidenciadas.

El `lead_time` puede determinar cuándo una reposición evidenciada estará disponible únicamente cuando esté evidenciado y sea aplicable al suministro analizado. Nunca convierte por sí mismo una compra no confirmada en entrada prevista.

Esta decisión fija el criterio evidencial de una entrada, pero no determina todavía cómo se incorporan pedidos pendientes y tránsito ni cómo se evita su doble contabilización; esas reglas permanecen en `STK-M06`.

## 4. Salidas previstas

Las salidas proceden de demanda, consumo, reservas u otras necesidades futuras reconocidas por una fuente autorizada. Cada magnitud conserva su semántica y no se mezcla o sustituye por otra sin una regla documentada.

La política debe identificar la fuente, método, ventana, fecha y transformación aplicados. Los valores iniciales de `PYE-002…PYE-005` permanecen pendientes de validación.

## 5. Ausencia y resultado parcial

Si falta el stock inicial, la fecha, la cantidad o la evidencia necesaria de un movimiento, el elemento correspondiente es `UNKNOWN / NOT_EVIDENCED`. No se sustituye por cero ni se inventa una estimación implícita.

`UNKNOWN / NOT_EVIDENCED ≠ 0`.

Un elemento desconocido no puede omitirse silenciosamente para presentar una proyección como completa. La proyección debe exponer su limitación y trazabilidad; el efecto del dato ausente sobre la evaluabilidad global se cerrará en `STK-M09`.

## 6. Resultados y autoridad decisional

STK-M05 puede identificar escenarios de reducción de stock, aproximación a umbrales o posible agotamiento. La salida es evidencia proyectiva para módulos posteriores de evaluación y para la decisión humana.

La proyección no constituye por sí misma una decisión de compra ni autoriza una reposición. Tampoco valida el umbral de 15 días de `PYE-006`.

## 7. Versionado y vigencia

Cualquier modificación de metodología, horizonte, granularidad, fuentes admitidas o tratamiento temporal debe quedar documentada, versionada, trazable y con fecha efectiva de entrada en vigor.

Una nueva versión no entra en vigor silenciosamente ni reescribe proyecciones históricas. Cada resultado conserva la versión metodológica aplicada.

## 8. Límites y continuidad

Esta decisión no autoriza valores para `PYE-001…006`; incorporación automática de pedidos o tránsito; doble contabilización; imputación de movimientos; decisión automática; ni implementación del motor cuantitativo STK.

`STK-M01…M05` quedan cerrados. `STK-M06…M10` permanecen pendientes y continúan bloqueando el contrato técnico y la implementación cuantitativa STK.
