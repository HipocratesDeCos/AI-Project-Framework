# Inicio: datos que consulta EIOS

La vista **Inicio** añade un resumen de la empresa y corte seleccionados, separado en catálogo/precios, existencias, compras, ventas, clientes/proveedores, balance/tesorería y parámetros. Cada bloque ofrece acceso al apartado relacionado y a Carga de archivos. La lista de archivos seleccionados se puede desplegar cuando sus nombres están disponibles en las referencias consultadas.

## Qué significan los estados

- **Documentos y referencias originales**: el bloque consulta la versión documental. No equivale a datos operacionales admitidos.
- **Referencias recibidas seleccionadas**: existe una selección explícita para ese recorrido. Puede complementar o sustituir determinadas referencias originales según el módulo, sin crear operaciones contables.
- **Selección retirada**: el módulo vuelve a sus referencias anteriores según su funcionamiento existente.
- **Revisar origen**: una selección de inventario, historial o tarifa ha perdido integridad o compatibilidad. No se presentan sus líneas como referencias seleccionadas válidas.
- **Recibido, sin referencias seleccionadas**: hay archivos ordinarios de ese bloque, pero no referencias originales ni selección que utilizar en ese recorrido.
- **Sin referencias**: no hay referencias del bloque representadas en esta consulta. No implica que no exista documentación fuera del expediente consultado.

Los recuentos de archivos ordinarios coinciden exactamente en código y razón social, naturaleza real/sintética y fecha de corte. Incluyen archivos ya seleccionados: no son un recuento de archivos pendientes ni de entidades únicas. El catálogo comercial adicional tiene su incorporación separada. Si no se puede clasificar información guardada de la empresa, se avisa y no se incorpora al recuento por corte.

## Lectura de los bloques

El catálogo muestra artículos consultables y tarifas vinculadas; la vigencia del precio se comprueba en la fecha de cada propuesta. El inventario cuenta físico comparable con SKU y unidad del catálogo, y disponible únicamente cuando está informado. Un físico o disponible de cero es conocido, no un dato ausente.

Compras y ventas separan facturas originales consultables de líneas recibidas seleccionadas. No se suman ambos recuentos como si fueran facturas equivalentes. La comparación comercial mantiene los filtros de proveedor/cliente, SKU, unidad y EUR de los recorridos existentes.

Clientes y proveedores reflejan las fichas consultadas. Recibir maestros no las sustituye automáticamente; el catálogo adicional puede contener proveedores declarados por nombre, sin validación fiscal.

Balance y tesorería muestran recuentos de registros originales, sin sumar importes ni declarar conciliación, liquidez disponible o viabilidad. Recibir nuevos saldos, previsiones o cuotas no los añade automáticamente al análisis financiero.

Parámetros distingue valores preparados de la activación financiera conservada para el corte. Señala si faltan margen mínimo, margen objetivo, horizonte o tesorería mínima. Un cero preparado no se confunde con ausencia; este resumen no vuelve a validar el parámetro ni afirma que todos estén conectados al motor. La activación financiera conserva sus propios valores y no se sustituye por los valores preparados posteriores.

## Actualización y límites

El resumen se consulta al abrir Inicio, con **Actualizar estado de datos** y al refrescar la empresa tras una selección o retirada. La tarjeta de parámetros también se actualiza al consultar o guardar su configuración. Cambiar de empresa limpia el resumen y descarta respuestas de una empresa anterior.

Los bloques describen referencias y configuración; no conceden autoridad ni confirman suficiencia documental o viabilidad. La consulta del resumen usa lecturas de base de datos y no modifica archivos, registros, selecciones, propuestas ni huellas de contexto. Se mantienen `decision_authority=false` y `operational_path=FORBIDDEN`.
