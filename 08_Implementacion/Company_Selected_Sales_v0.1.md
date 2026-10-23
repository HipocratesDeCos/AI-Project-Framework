# Historial de ventas recibido como referencia comercial

## Recorrido

1. Recibe Excel o CSV como **Líneas de facturas de venta**, con la empresa ficticia activa y su fecha de corte. Usa los códigos exactos de cliente y SKU de las fichas activas. El neto de línea ya debe incluir los descuentos y excluir el IVA.
2. Marca exclusivamente sus archivos de ventas en **Expedientes recibidos**. Incluye todas las partes que quieras mantener en la selección.
3. En **USAR VENTAS HISTÓRICAS RECIBIDAS**, pulsa **Comprobar las ventas marcadas**. Revisa la muestra, los errores y las referencias de archivo/fila.
4. Indica responsable y motivo, confirma la revisión y pulsa **Usar este historial en las propuestas**. Recibir el archivo sin este paso no cambia las referencias comerciales activas.
5. Consulta las líneas seleccionadas en el bloque separado del menú **Ventas**. Busca por factura, cliente, SKU o archivo; la tabla muestra hasta 100 líneas por página.
6. En **Propuestas de venta**, elige cliente y artículo. El historial combina las referencias originales comparables y las líneas recibidas seleccionadas. Usa la misma unidad y EUR, sin convertir embalajes o monedas.
7. El precio neto efectivo es neto/cantidad; los descuentos recibidos no se aplican de nuevo. La fecha más reciente determina las referencias actuales: si sus precios difieren, no se promedian ni se elige uno arbitrariamente. La cantidad solo se completa si hay una única línea en la última fecha. El comercial puede elegir otra referencia visible para negociar.
8. Puedes retirar la selección con responsable y motivo. Se recupera el historial original; las propuestas guardadas mantienen sus propias referencias.

## Integridad y alcance

- Revisión por empresa, razón social, naturaleza sintética y corte exactos; cliente conocido, SKU del catálogo activo, unidad exacta, fecha hasta el corte, cantidad positiva y neto no negativo.
- Bloquea facturas del mismo cliente ya existentes en los documentos originales. No admite completar parcialmente una factura original mediante una nueva selección. También bloquea números de línea duplicados entre archivos, líneas idénticas sin número y fechas/monedas contradictorias por cliente/factura.
- El número de línea es recomendable para distinguir líneas legítimas con igual contenido. Las descripciones y datos opcionales de descuento e IVA se conservan; la selección comercial no afirma que la factura fiscal esté completa ni sustituye la conciliación de cuotas.
- Máximo 100 archivos y 20.000 líneas combinadas. La muestra de revisión y la página de consulta son de 100 líneas. La comprobación caduca a los diez minutos y se revalida antes de confirmar.
- Cada selección sustituye la selección recibida anterior completa. Confirmar la misma selección vigente no la duplica. Se conserva un historial de revisiones y retiradas, sin sobrescribir los archivos originales.
- Las referencias quedan incorporadas a la huella del contexto de la propuesta. Cambiar o retirar la selección invalida solicitudes con un contexto anterior. Si cambian los bytes de origen o las relaciones activas, se muestra un aviso y no se rellena un precio histórico por defecto, tampoco un precio anterior silencioso. Debe revisarse o retirarse la selección.
- Las líneas recibidas se muestran aparte de las facturas documentales; no se convierten en facturas emitidas, salidas de almacén, cobros, vencimientos ni antecedentes de impago. La conciliación de cuotas y preparación de cobros tiene su propio recorrido.
- Disponible para la empresa sintética de pruebas. Se mantienen `decision_authority=false` y `operational_path=FORBIDDEN`; no se habilita admisión operacional.

## Consulta de las condiciones históricas

En la tabla de líneas recibidas de **Ventas**, la muestra de selección de **Carga de archivos** y el historial por cliente/artículo de **Propuestas de venta**, el desplegable **Ver condiciones y origen** distingue precio unitario antes de descuento (sin IVA), descuento porcentual, descuento total de línea, neto de línea, tipo de IVA declarado e IVA documentado de línea. Solo muestra valores aportados; no deduce cuotas de IVA para presentarlas como documentadas. Un cero explícito se conserva y los campos ausentes indican **No aportado**. La procedencia incluye archivo o documento, hoja, fila o página si existen.

Las descripciones de las líneas recibidas se muestran junto al SKU y pueden buscarse. El botón **Proponer este precio** sigue trasladando el precio neto por unidad y deja el nuevo descuento a cero: las condiciones históricas se consultan como referencia y no se vuelven a aplicar. Los descuentos en porcentaje y euros representan el mismo descuento de línea. No se trasladan automáticamente IVA ni condiciones de cobro. La misma consulta conserva campos explícitos compatibles de las líneas documentales originales cuando estén disponibles.

## Consulta desde Cartera de Clientes

La cartera distingue **Facturas originales al corte** de **Líneas recibidas seleccionadas**. Al pulsar **Ver ventas**, la ficha muestra ambos recuentos y mantiene separadas la tabla de facturas y la consulta de líneas recibidas del cliente exacto. Un cliente puede tener líneas recibidas seleccionadas aunque no tenga facturas originales en esa versión; no se presenta entonces como si careciera de todo historial.

La consulta recibida permite buscar factura, SKU, descripción o archivo, ordena por fecha de más reciente a más antigua y muestra 100 líneas por página. Reutiliza el detalle **Ver condiciones y origen** de Ventas: cantidad, unidad, neto, precio neto por unidad, descuentos e IVA aportados y archivo/hoja/fila. **Revisar archivos recibidos** abre Carga de archivos para consultar y recuperar los originales.

Solo se muestran las líneas de una selección vigente de esta empresa y del cliente elegido. Si el historial está retirado o su origen requiere revisión, no se reutilizan líneas anteriores y se conserva el mensaje de estado. Al refrescar o cambiar la empresa se limpia la ficha recibida; el filtro de búsqueda se reinicia al elegir otro cliente. Los recuentos no suman líneas y facturas como entidades equivalentes ni dan por completa una factura. Esta consulta no modifica registros, vínculos, propuestas, existencias, cobros ni referencias de impago.
