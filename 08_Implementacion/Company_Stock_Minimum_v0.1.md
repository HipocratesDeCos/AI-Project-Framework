# Stock mínimo editable y avisos descriptivos

El menú Stock permite guardar un mínimo manual por empresa, artículo y unidad. Se conserva en SQLite junto con la fecha, revisión y registro de valor anterior/nuevo. Se reutiliza entre versiones documentales de la misma empresa si SKU y unidad coinciden; otra empresa o unidad no hereda el valor. No se convierten unidades automáticamente. Sin valor manual, se usa el 10 % de la cantidad de la última compra documentada única hasta el corte del dataset, con unidad coincidente. Unidades indivisibles (ud, uds, unidad, unidades, unit, units, pcs; con punto final opcional) se redondean al entero superior; otras unidades conservan el decimal exacto. Se muestra Automático con cantidad, factura y fecha. Un valor manual, incluido cero, tiene prioridad; vaciar y guardar restablece el automático. Si no hay historial suficiente, queda sin configurar. No se recurre a una compra anterior si la última es ambigua o inválida. Se conserva la procedencia en la respuesta, sin guardar el valor derivado como una modificación manual. El parámetro no modifica inventario, planificación, stock de seguridad ni reglas del decisor.

Los estados usan el disponible del inventario mostrado y su unidad: sin datos suficientes si falta mínimo, disponible o unidad compatible; sin existencias si disponible <= 0; bajo mínimo si disponible < mínimo; en el mínimo si son iguales; sobre mínimo en otro caso. La falta hasta mínimo es max(0, mínimo - disponible), no una recomendación de compra. El contador y filtro incluyen sin existencias, bajo mínimo y en el mínimo. Cada fila conserva la fecha del inventario; datos sintéticos no acreditan stock actual.

POST `/api/stock/minimums` exige token local y dataset existente. Se validan SKU, unidad, cantidad finita no negativa (hasta mil millones), duplicados y revisión esperada. Guardado atómico y control optimista evitan sobrescribir cambios concurrentes. Se envían solo filas modificadas. El historial registra dataset de origen, fecha UTC, revisión y valores; sin autenticación multiusuario no se atribuye identidad a una persona. Los datos importados de parámetros no se admiten ni sustituyen automáticamente esta configuración manual.

Pruebas: límites, ausencia frente a cero, estados y diferencia, persistencia, separación entre empresas y unidades, reutilización en versiones de la misma empresa, cambios concurrentes, historial y ausencia de cambios. Recorrido DOM/HTTP sobre copia desechable de la base: edición, guardado, consulta persistida, filtro, borrado y protección del endpoint. No ejecuta compras ni evaluación de reglas.

Validación adicional: cálculo del 10 %, unidades indivisibles/fraccionables, historial ambiguo o incompatible, selección por fecha, prioridad manual de cero y restablecimiento automático.

## Consulta del mínimo al preparar una propuesta

Cada fila de Stock incluye Preparar propuesta. Selecciona proveedor y SKU en el formulario principal, muestra su mínimo efectivo (manual/automático), estado, diferencia y fecha del inventario. La cantidad, precio y condiciones se introducen expresamente: no se propone comprar la diferencia hasta mínimo. Si hay campos de un borrador cumplimentados, se solicita confirmación en pantalla antes de limpiarlos. Cancelar conserva el borrador. No guarda una propuesta ni ejecuta una compra al navegar. Sin proveedor compatible el botón queda deshabilitado. Guardar mínimos actualiza también el contexto del artículo seleccionado.

Verificación DOM/HTTP: navegación a otro artículo desde Stock, cancelación y aceptación de sustitución de borrador, campos de cantidad/precio vacíos, mínimo visible y recorrido de guardado de mínimos sobre copia desechable de la base.

## Referencia conservada en la propuesta

Las nuevas propuestas conservan `stock_context_at_save`: mínimo efectivo, origen, revisión y procedencia automática, inventario de referencia (o null), corte documental y fecha UTC de guardado. No se modifica después al cambiar los mínimos. La revisión muestra este bloque separado de las consultas de contexto existentes. Las propuestas antiguas sin bloque se identifican expresamente; no se reconstruye su pasado con la configuración actual.

El formulario envía la revisión del mínimo que mostraba. Si no coincide al guardar, se rechaza la propuesta y se indica recargar. Las llamadas anteriores sin este campo siguen admitidas y capturan el contexto de la lectura del servidor. La referencia no evalúa necesidad, tesorería ni conveniencia de compra y conserva `decision_authority=false`.

Pruebas adicionales: mínimo conservado tras cambio y reapertura, revisión del bloque congelado, falta de datos sin inventar existencias y rechazo de revisión obsoleta sin guardar. Recorrido DOM/HTTP: guardar propuesta, cambiar mínimo a 999 y verificar que la revisión conserva el bloque original mientras la ficha muestra el valor nuevo.
