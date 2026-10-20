# Vista Stock: existencias e indicadores

La tabla agrupa seis bloques: artículo/proveedores; existencias; mínimo/aviso; cobertura/entrega; rotación; acción. SKU y descripción se separan. Los proveedores provienen del catálogo y de compras con el mismo SKU, unidad y proveedor coherente entre línea y cabecera hasta el corte; no se enlazan artículos por similitud ni se presuponen exclusividades o disponibilidad comercial actual.

Físico, reservado y disponible aparecen en tres casillas de lectura alineadas, con disponible destacado y unidad común. No se agregan cantidades de diferentes unidades. Fechas de inventario en DD/MM/AAAA sin saltos de línea. El mínimo conserva su ancho de 72 px; la explicación de procedencia se abre en Ver origen, evitando una columna desproporcionada. Columnas con anchos definidos, filas alternas y desplazamiento horizontal en pantallas estrechas mantienen la estructura.

Cobertura y plazo reutilizan la planificación existente, identificada como supuesto sintético con fecha y vigencia. El plazo es supuesto, no un plazo real observado por proveedor. No se recalcula cobertura dividiendo por un consumo inventado.

Rotación se muestra como Pendiente de datos: para obtenerla se necesitan salidas o ventas en cantidades vinculadas al SKU y un stock medio de la misma unidad y período. La base actual no acredita ese stock medio. No se usa la cobertura, stock actual, precio o demanda supuesta como sustituto. El bloque Qué falta explica esta ausencia.

Se conservan edición y guardado de mínimos, filtro de avisos y Preparar propuesta. Las cantidades no son recomendaciones ni autorizaciones de compra. Pruebas: proveedores adicionales documentados, fecha de corte, unidad/proveedor incompatibles y ausencia de rotación inferida. Recorrido DOM/HTTP: seis columnas, tres etiquetas de existencias por artículo, fechas formateadas, proveedores, planificación y rotación pendiente, guardado de mínimos y navegación a propuestas sobre copia desechable.
