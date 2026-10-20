# Consulta de artículos del expediente recibido

En **Carga de archivos → Expedientes recibidos**:

1. Filtrar por empresa y fecha de corte.
2. Marcar expresamente los archivos que se desea consultar: catálogo de artículos, proveedores, líneas de compra, inventario, parámetros y ventas, según estén disponibles.
3. Pulsar **Consultar artículos seleccionados** y elegir el SKU.

La consulta lee todos los registros guardados de esos lotes, no solo las veinte filas de vista previa. Incluye los SKU que aparezcan en inventario o movimientos aunque no se haya seleccionado su ficha; en ese caso señala la ausencia de catálogo, sin inferir nombres por descripción.

## Datos mostrados

- Fichas de artículo seleccionadas, conservando versiones contradictorias.
- Última línea de compra por proveedor, unidad y moneda: fecha, cantidad de esa línea, precio neto efectivo y fuentes.
- Inventario: físicas, reservadas y disponibles, con filas de origen.
- Parámetros declarados en inventario y/o archivo separado de stock.
- Historial de líneas de compra y venta con factura, contraparte, cantidad, unidad, neto, moneda y procedencia.

El precio neto efectivo se deriva como `net_amount / quantity` usando Decimal. No es necesariamente el precio de tarifa de la factura. La pantalla muestra hasta seis decimales; no convierte monedas, unidades, embalajes o impuestos.

## Ambigüedades y límites

La referencia de última compra requiere una ficha de artículo coherente, proveedor documentado sin contradicciones, unidad coincidente y una sola línea en la última fecha dentro de cada proveedor/unidad/moneda. Si existen varias líneas en esa fecha, incluso de una misma factura, no suma cantidades ni elige una por orden de archivo. Si la factura presenta fechas o monedas contradictorias, tampoco ofrece referencia única. Las líneas de origen permanecen consultables.

El resumen de stock requiere una única fila de inventario con unidad coincidente con el catálogo. Varias filas o archivos, aunque sean idénticos, no se suman ni se elige una versión: pueden representar alternativas o almacenes sin identificar. Las reservas ausentes son desconocidas, no cero. Las ventas históricas no se restan de un inventario ya documentado ni se proyecta consumo automáticamente.

Los parámetros se muestran con su procedencia, sin resolver contradicciones ni activar reglas. La opción **Comprobar expediente seleccionado** sigue siendo la revisión cruzada de referencias y conflictos del conjunto de archivos; esta consulta no la sustituye ni concilia saldos financieros.

La selección no admite documentación para decisiones ni modifica la empresa activa, propuestas, stock u originales. Mantiene `PENDING`, `FORBIDDEN`, `decision_authority=false`, tanto para datos reales como sintéticos. Cambiar una casilla o el contexto invalida la consulta y sus respuestas pendientes para evitar mostrar un resultado de una selección anterior.

## Interfaz técnica

`POST /api/reception/articles`, protegido por Host local y token de sesión:

- `batch_ids`: selección explícita de 1–100 lotes de una misma empresa, razón social, naturaleza y corte.
- Sin `article_id`: índice de SKU documentados y estado de catálogo.
- Con `article_id`: detalle del SKU exacto dentro de esa selección; rechaza los que no constan.

La validación de selección se comparte con la comprobación de expediente. Operación de lectura sobre `received_company_batch`; no persiste nuevas evaluaciones ni decisiones.
