# Crear borrador desde un estudio · v0.1

## Problema y comportamiento

Consultar una propuesta guardada dejaba visibles el formulario de negociación y varias representaciones del estudio, lo que mezclaba sus resultados con la edición. «Volver al borrador» no copiaba la propuesta seleccionada.

La consulta pasa a ser un modo explícito: cabecera y cinta con datos del estudio, condiciones de edición ocultas y una única síntesis y colección de opciones. No permite guardar el formulario mientras se consulta el estudio. «Volver a mi formulario» recupera el formulario previo sin copiar condiciones. «Crear borrador desde este estudio» copia explícitamente el estudio seleccionado al formulario; el texto del botón explica que sustituye el formulario de trabajo y conserva el original.

## Copia

El endpoint POST `/api/purchases/draft` usa el estudio persistido de la versión activa y comprueba su huella documental contra la actual. No escribe propuestas ni reconstruye estudios sin contexto/condiciones suficientes. Devuelve proveedor, artículo, cantidad, fecha de pedido, lugar de entrega, condiciones comerciales, ambas columnas de negociación si existen, cuotas y supuestos de stock compatibles. Si no había columnas conservadas, prepara Mi propuesta desde las condiciones base. Propone una referencia nueva, sin sobrescribir la original.

Los metadatos de aceptación no se promocionan: las condiciones copiadas quedan pendientes. Los supuestos de stock se copian con su responsable, referencia y datos, pero requieren nueva confirmación explícita; hasta entonces no se presenta como completada su simulación. Las cuotas se copian con concepto, importe y fecha, sin duplicarlas ni incorporar pagos al libro.

Editar o copiar retira el panel histórico y las duplicaciones, invalida cálculos pendientes y recalcula sobre el borrador actual. Consultar otro estudio cambia la referencia y cinta guardadas. La respuesta de una copia pendiente se descarta si cambia la selección, el expediente o el formulario antes de aplicarla.

## Persistencia y procedencia

`draft_source` identifica versión, estudio, referencia y huella del original. Al guardar, el servidor verifica esa procedencia y su compatibilidad con proveedor/artículo. Crea un identificador nuevo mediante el guardado normal y conserva la relación en el informe imprimible. No cambia el original ni guarda automáticamente al copiar. Un cambio de proveedor/artículo/versionado en pantalla retira la procedencia de la copia; no se atribuyen otros datos al estudio anterior.

La copia no autoriza una compra, no acredita aceptación del proveedor y no modifica los motores ni parámetros.

## Recorrido de uso

1. Propuestas guardadas → Revisar.
2. Crear borrador desde este estudio.
3. Revisar condiciones, cuotas y supuestos copiados; confirmar la declaración de stock si procede.
4. Comparar y aplicar una alternativa. Recalcular y revisar.
5. Guardar la propuesta con su nueva referencia. Consultar el estudio nuevo y el informe.

## Validación

Cinco pruebas específicas de servidor: preparación sin escritura; copia de condiciones/cuotas/stock; identificador y referencia nuevos con original intacto; dos columnas sin aceptación promocionada; rechazo de huellas/contextos/orígenes incompatibles y capturas antiguas insuficientes. Pruebas de síntesis, negociación, caja, cuotas e informe.

Chromium contra la aplicación real: un solo bloque visible de opciones, separación consulta/edición y cintas correspondientes; copia del caso base, nueva confirmación, aplicación de combinación y recálculo; guardado real con procedencia y original idéntico; copia de cuotas; respuesta tardía descartada al seleccionar otro estudio. Regresiones de negociación, revisión y estados.
