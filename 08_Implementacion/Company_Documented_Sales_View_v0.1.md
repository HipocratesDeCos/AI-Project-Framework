# Consulta de ventas documentadas v0.1

En **Cartera de Clientes**, cada cliente de la empresa activa tiene un botón **Ver ventas**. La tabla muestra sus facturas documentadas hasta el corte, con fecha, neto, IVA, total, pendiente al corte, moneda y referencias de origen. **Ver líneas** muestra SKU si está documentado, descripción, cantidad, unidad si consta, precio unitario, neto y fuentes. El buscador global abre directamente las ventas del cliente seleccionado.

`company_sales.documented_sales` consulta sólo la versión documental solicitada. Incluye cabeceras cuyo cliente existe en esa versión, cuya referencia coincide con el identificador y que constan como `ISSUED_BY_CUTOFF` con fecha documental válida no posterior al corte. No utiliza fechas de previsiones para convertir documentos planificados en ventas históricas. Las exclusiones y líneas sin cabecera válida se contabilizan en la pantalla.

Las líneas se unen por referencia exacta de factura; una declaración de cliente contradictoria se excluye con aviso. Las discrepancias de moneda entre línea y cabecera se conservan y señalan. Los importes ausentes o no finitos se muestran como desconocidos, nunca como cero. No se agregan importes entre monedas.

La descripción no se usa para inferir un SKU o unidad. La ausencia de vínculo al catálogo se hace visible, sin afectar existencias ni generar demanda. El pendiente es el documentado al corte, no una afirmación sobre cobros posteriores. La consulta es de sólo lectura y no crea propuestas, movimientos ni autoridad decisional.

Los archivos de ventas recibidos mediante mapeo continúan en **Expedientes recibidos** hasta su admisión; no se mezclan con las facturas de la empresa activa. A Monkey ya contiene 9 facturas y 24 líneas consultables; no hace falta volver a cargarlas.

Pruebas: aislamiento por dataset/cliente, exclusión de fechas futuras y documentos no emitidos, referencias huérfanas, importes desconocidos, discrepancias de moneda, orden y preservación de fuentes/SKU/unidad ausentes. Prueba DOM/HTTP con los 8 clientes, 9 facturas y 24 líneas del expediente ficticio, filtrado por cliente, consulta de líneas y fuentes, búsqueda y limpieza al refrescar la versión. La prueba DOM no verifica el aspecto visual exacto.
