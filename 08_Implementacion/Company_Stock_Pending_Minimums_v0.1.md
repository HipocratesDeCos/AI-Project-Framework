# Revisión de mínimos editados sin guardar

Stock muestra un recuento global de artículos cuyo borrador de mínimo difiere del valor aplicado, independiente de filtros y páginas. Un desplegable permite revisar SKU, descripción, mínimo aplicado, edición sin guardar y unidad.

El panel se actualiza al editar una casilla y al reconstruir el listado. Cambiar filtros o páginas no retira los borradores del estado de edición. Volver al valor aplicado elimina el artículo del recuento. Cero es un valor explícito; una casilla vacía se presenta como «Volver al automático». La ausencia de mínimo aplicado se muestra como «Sin configurar».

El listado se limita a 100 filas y conserva el recuento total. Si se superan 100 ediciones, recuerda el límite existente de 100 cambios por operación de guardado; no divide ni guarda lotes automáticamente.

La revisión solo lee los borradores. Los avisos y el CSV siguen usando los valores aplicados hasta el guardado. No se añaden operaciones de escritura ni se modifica la validación del servidor. Empezar una actualización vacía el panel; si el dataset cargado no coincide con el seleccionado, no muestra borradores de la otra empresa.

## Validación

Ejecución DOM de la página completa con 105 artículos: edición, conservación al filtrar y limpiar filtros, vuelta al valor aplicado, cero, petición de automático, resumen de 105 cambios con 100 filas visibles y exclusión al cambiar de empresa. Comprobación de sintaxis y pruebas Python existentes de mínimos, métricas, CSV y orden de carga. El recorrido historial/Stock conserva su comportamiento.
