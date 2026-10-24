# Descarga del stock filtrado en CSV

«Descargar stock filtrado (CSV)» exporta todos los artículos que cumplen los filtros de Stock, en el mismo orden que la tabla, incluidas las páginas no visibles. Comparte la función de filtrado con la pantalla: texto, proveedor, familia, avisos y, cuando proceda, el SKU exacto abierto desde un historial.

El archivo identifica empresa, dataset y corte en cada fila. Incluye SKU, descripción, familia, proveedores documentados, físico/reservado/disponible, unidad y fecha del inventario, naturaleza documental disponible, mínimo aplicado, origen y aviso del mínimo, archivo/fila de inventario cuando existen y estado de su selección. No suma unidades ni empresas. Una referencia ausente queda vacía.

Se exporta el mínimo aplicado de la consulta (`value`), no el borrador de la casilla (`draft`). La descarga no guarda cambios. Un inventario ausente no se transforma en cero; los ceros documentados sí se conservan. Las naturalezas documentales se copian de sus fuentes cuando están disponibles y no se infieren.

Formato: UTF-8 con BOM, separador punto y coma, campos entre comillas, decimales con coma sin agrupación de miles y fechas DD/MM/YYYY. Compatible con importación en Excel o Google Sheets. Para conservar códigos con ceros iniciales, importar su columna como texto. Las comillas y saltos de línea del contenido se conservan; los textos que podrían interpretarse como fórmulas se neutralizan con apóstrofo. Los campos numéricos reconocidos se mantienen numéricos, incluidos negativos.

La descarga se deshabilita durante la actualización y sin resultados. Antes de generar se comprueba que el estado cargado corresponde al dataset seleccionado. No solicita ni envía archivos a servicios externos; el CSV se genera en el navegador. No crea propuestas, movimientos ni asientos.

## Validación

`python -m unittest tests.test_company_stock_csv -v`

La prueba ejecuta el exportador y filtro reales con Node y vuelve a leer el resultado con el lector CSV de Python: 101 coincidencias más allá de la página visible, filtros, SKU exacto, empresa incorrecta, datos ausentes/cero, decimales/negativos, mínimo aplicado frente a borrador, fechas, naturaleza, referencias, comillas, saltos y texto similar a fórmula.

Comprobación adicional DOM de la página completa con 105 artículos: descarga, nombre de archivo, mensaje de recuento, ausencia de mutaciones y conservación de los recorridos de familias e historial/Stock.
