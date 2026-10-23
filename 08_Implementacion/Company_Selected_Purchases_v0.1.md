# Líneas de compra recibidas seleccionadas como historial

## Recorrido

1. Desde Carga de archivos, descargar la plantilla Compras históricas si hace falta. Preparar una fila por línea, con factura, fecha, código de proveedor, SKU, cantidad, unidad, neto de línea sin IVA y moneda.
2. Recibir XLSX/CSV como **Líneas de facturas de compra (sin abonos)** con empresa, razón social, naturaleza ficticia y corte de la empresa activa. Comprobar y guardar en expediente. La recepción por sí sola no cambia el historial utilizado por las propuestas.
3. En Expedientes recibidos, marcar únicamente las partes de compras que se quieran utilizar juntas. Las fichas del proveedor y del artículo deben existir en el catálogo activo; se admiten los artículos y códigos propuestos del catálogo comercial seleccionado. No se unen nombres de proveedor con códigos de forma automática.
4. Abrir **USAR COMPRAS HISTÓRICAS RECIBIDAS → Seleccionar archivos y revisar las últimas compras**. Pulsar **Comprobar las compras marcadas**. Revisar errores, líneas propuestas y referencia neta por unidad. La muestra presenta hasta 100 líneas.
5. Indicar responsable, motivo y confirmar revisión y alcance de referencia. Pulsar **Usar este historial en las propuestas**.
6. En Compras, consultar **LÍNEAS RECIBIDAS SELECCIONADAS**, con búsqueda y páginas de 100 filas. Las facturas documentales originales permanecen en su sección. Las líneas recibidas no se presentan como facturas fiscales completas ni se rellenan IVA o totales brutos inexistentes.
7. Seleccionar artículo en la propuesta de compra o venta. Las referencias comparables incorporan el historial recibido, con fecha, cantidad, precio efectivo y archivo/fila de origen. El mínimo automático del 10 % utiliza su criterio existente de última cantidad única y unidad compatible; los mínimos manuales se conservan.
8. Para deshacer la selección, indicar responsable y motivo y pulsar **Retirar el historial recibido seleccionado**. Se recuperan las referencias documentales originales. Los archivos y las propuestas ya guardadas conservan su contenido y procedencia.

## Contrato y comparabilidad

Entre 1 y 100 archivos, hasta 20.000 líneas combinadas, de una misma empresa ficticia, razón social y corte activos. La recepción ordinaria mantiene su límite por tabla. Solo EUR en esta primera conexión. SKU y proveedor por sus códigos exactos de catálogo; unidad exactamente igual a la ficha. Fecha válida no posterior al corte, cantidad positiva e importe neto finito no negativo. El precio efectivo es neto de la línea dividido por cantidad, conservando el dato como referencia sin atribuir descuentos adicionales ni IVA.

La selección se consulta junto a los registros documentales originales y sustituye a la selección recibida anterior completa; no acumula automáticamente todos los archivos cargados. Incluye todas las partes que quieras mantener. Una factura se identifica por proveedor y número. Si ya existe en los documentos originales, se bloquea su incorporación completa: no se añaden parcialmente líneas ni se sobrescribe aquella factura. Entre los archivos seleccionados se bloquean líneas idénticas y fechas/monedas contradictorias en una misma factura y proveedor. Si una repetición fuera legítima, su distinción o preparación debe resolverse antes; no se asume ni se deduplica automáticamente.

Las referencias de precio de las propuestas conservan el proveedor indicado en la ficha del artículo, unidad y EUR. Las líneas a otros proveedores conocidos se muestran en Compras y como proveedores de origen en Stock, sin sustituir el coste del proveedor de la ficha. Si existen varias líneas en la última fecha comparable, no se elige una arbitrariamente. Para la comparación de coste se conserva el requisito previo de neto positivo; una línea de neto cero se puede consultar sin convertirla en coste comparable demostrado. La línea recibida prevalece como coste sobre el coste de catálogo cuando es la última referencia comparable única.

No se modifica el inventario, la planificación, los saldos, las previsiones o los vencimientos. La cantidad comprada no se transforma en existencia ni acredita recepción. El archivo de líneas no contiene la información necesaria para construir una factura fiscal completa o un calendario de pagos. Los avisos descriptivos de mínimo pueden cambiar por la nueva cantidad de compra, sin ejecutar órdenes ni promover autoridad decisional.

## Persistencia y contexto

`company_purchase_history_selection` conserva revisiones append-only por dataset con archivos, huellas, responsable, motivo y fecha. Los originales siguen en recepción; no se reescriben registros de facturas o líneas documentales. El contexto de propuestas incluye la selección y las huellas actuales de sus fuentes. Las vistas previas quedan ligadas a ese contexto, caducan a los diez minutos y son de un uso. La selección comprueba de nuevo origen, relaciones y contexto bajo transacción. Repetir una selección idéntica es idempotente.

Si una fuente seleccionada cambia, desaparece o resulta incompatible con las fichas/documentos originales actuales, se informa y se ocultan las referencias de última compra hasta revisar o retirar la selección. Tampoco se usa silenciosamente el coste de catálogo como sustituto de un historial recibido que ha dejado de ser válido. La retirada expresa recupera el historial original. Las propuestas guardadas conservan sus valores de referencia y rechazan revisiones que mezclen un contexto posterior distinto.

Se conserva el material ficticio y el alcance de simulación: `decision_authority=false`, `operational_path=FORBIDDEN`. No es admisión, registro fiscal, pago, evidencia validada o autorización de compra/venta.

## Verificación

Cinco pruebas nuevas cubren recepción/vista previa, última cantidad y coste, mínimo automático, propuesta guardada y contexto antiguo, retirada, solapamiento con factura original, duplicados entre partes, contradicciones de cabecera, empresa/corte/unidad/SKU/proveedor incompatibles, proveedor distinto del de ficha, origen cambiado antes/después de seleccionar, ausencia de sustitución silenciosa, confirmación, caducidad, idempotencia, ambigüedad de última fecha y una nueva ficha del catálogo comercial.

Veinte pruebas focales correctas. Recorrido DOM/HTTP con copia de A Monkey y una ficha ficticia de prueba: recepción de CSV, comprobación sin activar, confirmación, 10 unidades y neto 120 EUR → 12 EUR/unidad; consulta en Compras y fichas de compra/venta con procedencia, mínimo automático 1 unidad y ausencia de inventario para esa nueva ficha. Retirada recupera exactamente el historial y existencias anteriores. Registros documentales y bytes originales permanecieron iguales. JavaScript comprobado sintácticamente; revisión visual en navegador pendiente.
