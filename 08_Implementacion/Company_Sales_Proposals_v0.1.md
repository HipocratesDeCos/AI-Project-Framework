# Propuestas de venta v0.1

Primera versión para preparar ofertas sintéticas desde la empresa y versión documental activa. El menú lateral distingue Propuestas de compra y Propuestas de venta; Ventas continúa mostrando facturas históricas.

## Pantalla y datos

El formulario selecciona un cliente y entre 1 y 30 líneas del catálogo, con cantidad, precio antes de descuento, descuento porcentual e IVA explícitos por línea. Añade referencia única por versión, fecha, vigencia, entrega, lugar, cobro previsto, condiciones de cobro y portes facturados al cliente con IVA explícito. Fechas visibles DD/MM/AAAA, importes españoles y moneda EUR. No se deduce IVA de históricos ni se configura una política comercial implícita.

`Calcular oferta` calcula sin guardar; `Guardar propuesta de venta` conserva una oferta completa. Los cálculos monetarios utilizan Decimal, redondeo por línea a céntimos ROUND_HALF_EVEN y el calculador comercial existente. Base e IVA incluyen los portes facturados. El precio de cada línea es anterior al descuento porcentual; no se aplica un segundo descuento global.

## Referencias internas

Se reutiliza `documented_sales`: ventas documentadas emitidas hasta el corte, cliente y SKU exactos, misma unidad y EUR coherente en cabecera y línea. El precio histórico neto se calcula con neto/cantidad positiva; no se toma un precio antes de descuento como precio neto. Las líneas del día más reciente se muestran juntas; no se escoge arbitrariamente una como último precio único.

`purchase_history` aporta compras comparables del proveedor de catálogo, en la misma unidad y EUR. Una única referencia del último día permite calcular margen por línea sobre esa compra histórica: `(neto de venta - cantidad × coste unitario de referencia) / neto de venta × 100`. Varias referencias en el último día, ausencia de coste o neto cero producen margen no calculable. Este margen excluye portes y otros costes y no equivale al margen sobre coste completo ni a una recomendación de precio.

El inventario conserva cantidad física, reservada, disponible, unidad, fecha y naturaleza sintética. Una unidad distinta no se convierte implícitamente. Se avisa si la cantidad agregada por SKU supera el disponible de referencia o falta inventario comparable. Las facturas históricas no se utilizan para deducir stock.

## Persistencia y documento para el cliente

`manual_sales_proposal` conserva identificador, dataset, referencia, fecha de guardado y payload completo. Se guarda cliente, empresa, líneas, condiciones, cálculos y referencias internas, además de la huella del contexto documental. Se comprueba dicha huella con bloqueo de escritura antes de insertar; no se admiten referencias repetidas en el mismo dataset. No hay edición silenciosa: una nueva oferta usa otra referencia.

La primera versión exige naturaleza documental SYNTHETIC y mantiene decision_authority=false y operational_path=FORBIDDEN. Guardar no crea factura, reserva stock, registra un cobro ni modifica propuestas de compra. Los archivos recibidos sin admisión no se mezclan con la empresa activa.

El documento se descarga como HTML imprimible mediante el diálogo de impresión/Guardar PDF del navegador. Usa exclusivamente la oferta guardada, escapa textos y excluye márgenes, compras históricas, inventario, advertencias internas y contexto documental. Está identificado como prueba sintética; no acredita aceptación comercial. El acceso exige dataset e identificador exactos. Los nuevos endpoints POST mantienen el control de Host, token y tamaño del servidor existente.

## Validación

Cinco pruebas nuevas verifican cálculos de varias líneas, margen, persistencia, aislamiento por versión, referencias duplicadas, datos inválidos, comparabilidad, conservación de históricos e inventario, informe congelado y exclusión/escape de datos internos. Suite completa: 2732 pruebas correctas. Sintaxis del JavaScript completo comprobada con Node.

Recorrido DOM/HTTP con SQLite desechable: menú, referencias de cliente y artículo, cálculo sin escritura, guardado, descarga del documento y limpieza del formulario. La inspección visual queda pendiente: la descarga del navegador de pruebas devolvió archivos inválidos. No se modificó la base del usuario.
