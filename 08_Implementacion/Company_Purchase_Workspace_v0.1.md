# Pantalla guiada de propuestas de compra

La pantalla mantiene los campos, identificadores y acciones del circuito de compra y los presenta en cuatro pasos: proveedor/artículo, precio/cantidad, pagos/portes/entrega y guardado/revisión. La ficha y referencias se muestran a la derecha en escritorio y debajo en pantallas estrechas. La selección de proveedor limita el catálogo de artículos, con búsqueda y filtro de familia existentes.

Los indicadores de precio antes de descuento, descuento, neto, IVA, portes y total proceden de la cotización del servidor. No se introduce una segunda aritmética en el navegador. Portes pendientes permanecen pendientes. La consulta documental muestra empresa, archivo activo y corte.

El guardado abre la revisión existente de precio, stock y contexto financiero. No ejecuta pedidos, reservas ni pagos. El informe y el borrador comercial siguen ligados a la revisión guardada. Las cuotas, referencias documentales y acciones financieras mantienen su comportamiento y fronteras originales.

Validación: recorrido HTTP/DOM de compra con propiedad de campos en el formulario, cálculo de descuento y portes, ocultación de campos no aplicables, edición de cuotas, guardado y apertura de revisión; regresión HTTP/DOM de ventas y pruebas de compras, condiciones comerciales y actualización de empresa.
