# Menú Compras: historial documental

Compras se sitúa debajo de Propuestas y consulta las facturas de compra de la versión documental activa hasta su fecha de corte. El resumen informa de facturas, líneas y proveedores. Búsqueda por factura, proveedor, SKU o descripción y filtro por proveedor. Ver artículos muestra cantidad, unidad, precio documentado, neto de línea, moneda y referencias de origen. No se agregan cantidades de distintas unidades ni importes de monedas distintas.

Los vínculos usan identificadores exactos de factura/proveedor. Se excluyen cabeceras posteriores al corte, con fecha inválida, proveedor sin catálogo o invoice_id incoherente con record_id. Líneas sin cabecera compatible o con otro proveedor no se incorporan; se informa de exclusiones y avisos. Cifras ausentes o no finitas permanecen desconocidas, no cero. Una moneda incompatible en línea conserva un aviso.

La vista no confirma pedidos, recepciones ni pagos; tampoco modifica stock o propuestas. Las facturas históricas son documentación del caso ficticio, no operaciones reales confirmadas. Guardar una propuesta no genera una factura. El seguimiento pedido/recepción/factura/pago será un desarrollo posterior con estados y soporte propios. No se cambia C0, reglas, Finance, QTG ni autoridad decisoria.

Validación: seis pruebas nuevas de cabecera/líneas/procedencia, fecha de corte, proveedor/identificador incompatibles, valores ausentes y separación de versiones. Recorrido DOM/HTTP en copia desechable de A Monkey: menú bajo Propuestas, seis facturas, dieciocho líneas, seis proveedores, búsqueda por SKU, detalle con DOC-016, filtro por proveedor y ausencia de coincidencias. No se crean compras de prueba en la base del usuario.
