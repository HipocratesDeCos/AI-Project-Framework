# Familias del catálogo en Stock

Stock utiliza el campo `family` de los artículos del catálogo activo para facilitar la consulta. No calcula ni asigna familias por nombre, proveedor o historial.

- El selector muestra las familias documentadas en orden alfabético y el total de artículos de cada una en el catálogo completo, antes de aplicar los demás filtros.
- «Sin familia documentada» localiza campos ausentes, nulos, vacíos o con espacios. Es un filtro de consulta y no una familia añadida al catálogo.
- «Todas las familias» no limita el listado por este dato.
- La familia se muestra junto a la descripción en cada fila y participa en la búsqueda libre.

La familia se combina con proveedor, búsqueda y avisos. Se mantienen el orden elegido y las páginas de 100 registros. Cambiar el selector vuelve a la primera página y retira el límite exacto que pudiera venir de un historial, igual que los demás filtros de Stock.

Las opciones se reconstruyen a partir del catálogo activo, sin conservar categorías de otro catálogo. Una selección que ya no existe vuelve a «Todas las familias». Comenzar la actualización del estado limpia la selección. «Ver stock» desde un historial y «Ver todo el stock» también limpian la familia para no ocultar el artículo elegido ni limitar el regreso al listado completo.

Los controles se distribuyen en dos columnas y pasan a una en la disposición móvil existente. No se modifican cantidades, reservas, mínimos, planificación, rotación, propuestas ni fuentes seleccionadas.

## Validación

Ejecución DOM del JavaScript completo con 105 artículos: familias documentadas, vacías y nulas; valor literal `missing` sin confundirlo con el filtro de ausentes; páginas de 100/1; combinación con proveedor, avisos y texto; búsqueda por familia; apertura del SKU exacto desde un historial; retirada de opciones al sustituir el catálogo y ausencia de mutaciones documentales.

Comprobación de sintaxis y pruebas Python existentes de catálogo comercial, métricas de stock, inventario seleccionado y orden de carga.
