# Menú Ventas

Ventas se sitúa debajo de Compras y consulta el historial de facturas de venta de la empresa/versión activa hasta el corte. Reutiliza `documented_sales` y sus reglas de fecha, estado emitido, cliente y vínculos exactos; no añade otra interpretación de las fuentes. Cartera de Clientes conserva su consulta existente.

El listado muestra factura/fecha, cliente, neto, IVA, total, pendiente al corte y moneda. Incluye búsqueda por factura, cliente, SKU o descripción, filtro por cliente y acceso Ver artículos. El detalle conserva cantidades, unidades, precio documentado, neto de línea, moneda y procedencia. No se agregan importes de monedas distintas ni cantidades de unidades distintas.

El pendiente corresponde al corte documental y no acredita cobros posteriores. La consulta no crea ventas, no modifica propuestas ni descuenta stock. Ausencias y exclusiones conservan el tratamiento del servicio existente. Cambiar búsqueda/cliente o refrescar la versión oculta el detalle anterior.

Verificación: pruebas existentes de ventas/pantalla/compras; recorrido DOM/HTTP en base desechable con posición del menú, nueve facturas y veinticuatro líneas de A Monkey, detalle, búsqueda por descripción, filtro de cliente, ausencia de resultados y conservación de Cartera de Clientes. No se modifican contratos del núcleo ni autoridad decisoria.
