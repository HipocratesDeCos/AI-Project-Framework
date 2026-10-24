# Alcance visible de los filtros de Stock

Stock distingue ahora dos ámbitos:

- **Selección filtrada:** total de artículos coincidentes en todas las páginas; artículos con aviso de mínimo (`EMPTY`, `LOW`, `LIMIT`) y artículos sin datos suficientes (`UNKNOWN` o estado ausente).
- **Catálogo completo:** recuentos generales existentes, identificados expresamente como tales, aunque una búsqueda no muestre coincidencias.

Son recuentos de artículos, no una suma de cantidades de distintas unidades. Los estados y cálculos del mínimo no cambian. Los avisos conservan la referencia temporal del inventario.

El resumen de filtros indica texto, proveedor, familia, restricción a avisos, SKU exacto del historial y orden elegidos. Cuando no hay restricciones lo indica expresamente. Los nombres se insertan como texto, sin interpretar HTML.

«Limpiar filtros» retira todas las restricciones, incluido el límite de SKU y su regreso al historial, vuelve al orden por SKU y a la primera página y devuelve el foco al buscador. No guarda ni descarta borradores de mínimos: los conserva el estado de edición existente. No modifica documentos ni propuestas. Se deshabilita cuando no hay nada que limpiar y durante la actualización de empresa.

El CSV sigue usando exactamente la selección filtrada completa. Los recuentos de pantalla y descarga parten de los mismos artículos coincidentes.

## Validación

JavaScript completo con 105 artículos: selección de dos artículos con familia ausente, un estado desconocido y cero avisos; contraste con los recuentos globales; resumen de filtros; limpieza desde familia/orden y SKU exacto; retorno del foco; conservación del CSV y de la navegación a historiales. Pruebas Python de exportación, orden de carga, métricas e inventario seleccionado.
