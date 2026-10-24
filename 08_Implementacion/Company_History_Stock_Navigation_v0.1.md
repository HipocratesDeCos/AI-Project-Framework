# Del historial de compras y ventas al stock del artículo

Las líneas de facturas originales y las tablas de líneas recibidas incorporan «Ver stock» junto al SKU cuando el código exacto existe en el catálogo de la empresa activa. Esto incluye los historiales consultados desde las carteras. La acción permite revisar existencias y mínimos sin abrir ni cumplimentar una propuesta.

## Recorrido

1. Abrir una factura o las líneas recibidas de un proveedor/cliente.
2. Pulsar «Ver stock» en el artículo.
3. EIOS abre Stock, limita la tabla al SKU exacto y muestra la empresa y el corte documental. No incluye otros artículos cuyo código contenga el mismo texto.
4. Consultar físico, reservado, disponible, mínimo y los demás indicadores existentes, con sus fuentes y unidades. La navegación no convierte las cantidades de la factura en existencias. La ausencia de inventario sigue mostrándose como dato ausente.
5. «Volver a Compras/Ventas/Proveedor/Cliente» regresa a la vista desde la que se abrió el artículo y devuelve el foco a su botón «Ver stock». Conserva los filtros, la página y el detalle del historial, sin reconstruir sus tablas. Desde la vista previa de archivos, el regreso se identifica como «Volver a Carga de archivos».
6. «Ver todo el stock» retira el límite y devuelve el foco al buscador. Cambiar la búsqueda, proveedor, orden o filtro de avisos también retira el límite exacto y aplica la consulta ordinaria.

Al abrir el artículo se limpian la búsqueda libre, el proveedor y el filtro de avisos, y se vuelve a la primera página para que un filtro anterior no oculte el SKU. Actualizar el estado retira el límite exacto y el regreso. El botón conserva el dataset desde el que se creó y no navega si la empresa seleccionada o el estado cargado corresponden a otro dataset. El regreso tampoco navega si su botón de origen se ha retirado del DOM o su detalle se ha ocultado. No se ofrece para líneas sin SKU conocido; no establece equivalencias por descripción.

No modifica propuestas, fichas, inventario, mínimos ni selecciones de fuentes. No registra compras/ventas, asientos, reservas, cobros o pagos. No cambia las reglas de cálculo ni la autoridad decisional.

## Validación

Ejecución DOM del JavaScript completo: líneas originales y recibidas de compras y ventas; SKU `A` frente a `A-EXTRA`; filtros previos y paginación; regreso al listado y foco; conservación del estado documental; inventario ausente; línea sin SKU y enlace creado en otro dataset. Se verifica además el regreso desde ambas carteras y ambos menús de facturas, manteniendo búsqueda, página y detalle, y su invalidación ante origen retirado/oculto, limpieza o actualización. Comprobación de sintaxis y pruebas Python existentes de compras, historiales seleccionados, orden de carga y propuestas de venta.
