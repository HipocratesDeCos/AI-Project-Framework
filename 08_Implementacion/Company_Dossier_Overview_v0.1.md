# Resumen de documentación recibida por empresa

En **Carga de archivos → Expedientes recibidos**, el selector **Empresa y fecha de corte** filtra los lotes recibidos individualmente. Cada contexto conserva empresa, razón social, naturaleza real/sintética y fecha de corte. No agrupa datos de fechas distintas ni cambia la empresa activa en Propuestas.

Al seleccionar un contexto se muestran archivos y filas guardadas para proveedores, clientes, artículos, inventario, parámetros, compras, ventas, cobros/pagos, saldos contables y PDFs de soporte. Se distingue entre:

- Sin archivos recibidos.
- Archivo sin filas de datos.
- Datos recibidos pendientes de revisión.
- Solo soporte: cifras sin extraer, en el caso de los PDF.

Los recuentos proceden de todos los registros conservados en `received_company_batch.records_json`, no de la vista previa ni del recuento de metadatos. Son filas por archivo, no entidades, facturas ni movimientos únicos. Si existen varios archivos del mismo bloque se indica que deben revisarse posibles solapamientos; no se selecciona automáticamente una versión ni se deduplican datos.

Se cuenta por separado la presencia de stock mínimo, stock de seguridad, punto de pedido y plazo de entrega, tanto en inventario como en archivos de parámetros. Cero es un dato presente; un campo ausente o nulo no lo es. El recuento tampoco acredita que todos los artículos tengan parámetros completos.

El panel solo describe recepción. No determina que todos los bloques sean obligatorios para cualquier empresa ni calcula un porcentaje de preparación. No confirma conciliación financiera, integridad documental, vigencia o admisión. Conserva `PENDING`, `FORBIDDEN` y `decision_authority=false`.

Los paquetes ZIP ya importados en la empresa activa se consultan en **Inicio** y las pantallas de cartera, stock y propuestas. No aparecen como nuevos archivos individuales en este resumen ni necesitan cargarse de nuevo para seguir consultándolos.

El cambio de contexto limpia selecciones, detalle de archivo y resultado de comprobación anteriores. Las casillas siguen siendo una elección expresa para **Comprobar expediente seleccionado**. El botón **Descargar original** permanece disponible en cada fila visible.

Endpoint de lectura local: `GET /api/reception/overviews`, con comprobación de Host como las demás consultas de recepción. No escribe ni altera archivos o datos.
