# Búsqueda en carteras de proveedores y clientes

Las carteras de la empresa activa incorporan búsqueda y páginas de 50 registros, ordenados por razón social y, en caso de empate, por código. El orden y los filtros solo afectan a la consulta.

| Cartera | Campos de búsqueda |
|---|---|
| Proveedores | Código, razón social, persona de contacto y lugar de entrega documentados en la ficha |
| Clientes | Código y razón social |

Se admiten varias palabras, que deben aparecer en el conjunto de campos de la ficha, sin distinguir mayúsculas ni tildes. No se buscan documentos ni artículos desde este filtro: sus buscadores y los historiales conservan su propio alcance.

Cada cartera indica coincidencias respecto al total, intervalo visible y página. «Limpiar búsqueda» restaura la primera página y devuelve el foco al buscador. Se distingue una búsqueda sin coincidencias de una cartera vacía en la versión activa. El filtro no exige historial: también permite localizar empresas sin facturas o sin líneas recibidas seleccionadas.

Al buscar o cambiar de página se oculta el detalle anterior para evitar confundirlo con los resultados visibles. «Ver compras» y «Ver ventas» siguen abriendo el historial de la fila elegida, con facturas originales y líneas recibidas seleccionadas separadas. Los recuentos por empresa comercial se calculan sobre todo el historial correspondiente, no sobre la página de la cartera.

Al actualizar el estado se limpian las búsquedas, páginas y tablas antes de solicitar los datos. Si el dataset en memoria no coincide con el seleccionado, el filtro no devuelve filas. No modifica fichas, selecciones de archivos, propuestas, inventario, cobros/pagos ni autoridad decisional.

## Validación

- JavaScript completo de la página: comprobación de sintaxis y ejecución DOM.
- Caso sintético de 114 proveedores y 101 clientes: páginas de 50/50/14 y 50/50/1; orden, búsqueda por varias palabras y sin tildes, recuentos originales/recibidos, estado vacío, limpieza y foco.
- Ocultación del detalle al filtrar, vaciado durante actualización, exclusión de datos de otro dataset y ausencia de mutaciones del estado documental.
- Pruebas Python existentes de compras seleccionadas, compras documentales, estado de datos y propuestas de venta.
