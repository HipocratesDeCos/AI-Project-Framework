# Recepción del libro empresarial ampliado

La recepción conjunta incorpora campos opcionales declarados: correo de proveedor, dirección/provincia/código postal/país del cliente, subfamilia y procedencia del artículo, precio unitario y soportes de compra, origen de venta y contraparte/soporte de los pagos. Se conservan las claves canónicas internas. Las cabeceras se comparan sin diferencias de acentos, puntuación, mayúsculas o saltos de línea, rechazando ambigüedades. Las columnas nuevas sin mapeo previo se reconocen únicamente por nombres explícitos.

`08_Referencias_Precios` se recibe como `price_reference`, separado de `sale_price`. SKU, coste y PVP son obligatorios; unidad, origen y fecha son opcionales. Una referencia sin unidad no acredita cobertura para la unidad del catálogo. No se presupone moneda, vigencia ni tarifa activa. El detalle de artículos muestra clasificación y referencias, con procedencia y cobertura por unidad.

Las fórmulas no se ejecutan. Solo el precio unitario de compra y el coste/PVP de referencia pueden utilizar resultados numéricos guardados en el XLSX. Se rechazan caches ausentes y se conservan avisos de procedencia. El precio de compra debe coincidir con neto/cantidad, con tolerancia de 0,005 por unidad. Los demás campos siguen requiriendo valores fijos.

Una casilla desmarcada por defecto permite conservar correcciones como nueva recepción. Sin marcarla siguen bloqueándose conflictos; al marcarla se conservan originales y se registra `supersedes_received_batches`. Las selecciones/versions previas y datos operacionales no se modifican. La comprobación y confirmación mantienen el control de caducidad, snapshot, identidad y transacción atómica. Repetir la misma recepción es idempotente incluso si existen versiones anteriores distintas.

Validación: 54 pruebas de recepción, libro, campos ampliados, consulta de artículos, perfiles y cobertura; prueba HTTP y DOM del adjunto completo con 11 bloques, consulta de referencias y clasificación, navegación y encabezado, invalidación de la opción de revisión y conservación del dataset activo. Los archivos privados no se incluyen en el repositorio.

La validación es estructural y de referencias: no acredita conciliación financiera global, admisión operacional ni autoridad decisional.
