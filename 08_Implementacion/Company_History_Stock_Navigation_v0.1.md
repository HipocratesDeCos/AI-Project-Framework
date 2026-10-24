# Del historial de compras y ventas al stock del artículo

Las líneas de facturas originales y las tablas de líneas recibidas incorporan «Ver stock» junto al SKU cuando el código exacto existe en el catálogo de la empresa activa. Esto incluye los historiales consultados desde las carteras. La acción permite revisar existencias y mínimos sin abrir ni cumplimentar una propuesta.

## Recorrido

1. Abrir una factura o las líneas recibidas de un proveedor/cliente.
2. Pulsar «Ver stock» en el artículo.
3. EIOS abre Stock, limita la tabla al SKU exacto y muestra la empresa y el corte documental. No incluye otros artículos cuyo código contenga el mismo texto.
4. Consultar físico, reservado, disponible, mínimo y los demás indicadores existentes, con sus fuentes y unidades. La navegación no convierte las cantidades de la factura en existencias. La ausencia de inventario sigue mostrándose como dato ausente.
5. «Ver todo el stock» retira el límite y devuelve el foco al buscador. Cambiar la búsqueda, proveedor, orden o filtro de avisos también retira el límite exacto y aplica la consulta ordinaria.

Al abrir el artículo se limpian la búsqueda libre, el proveedor y el filtro de avisos, y se vuelve a la primera página para que un filtro anterior no oculte el SKU. Actualizar el estado retira el límite exacto. El botón conserva el dataset desde el que se creó y no navega si la empresa seleccionada o el estado cargado corresponden a otro dataset. No se ofrece para líneas sin SKU conocido; no establece equivalencias por descripción.

No modifica propuestas, fichas, inventario, mínimos ni selecciones de fuentes. No registra compras/ventas, asientos, reservas, cobros o pagos. No cambia las reglas de cálculo ni la autoridad decisional.

## Validación

Ejecución DOM del JavaScript completo: líneas originales y recibidas de compras y ventas; SKU `A` frente a `A-EXTRA`; filtros previos y paginación; regreso al listado y foco; conservación del estado documental; inventario ausente; línea sin SKU y enlace creado en otro dataset. Comprobación de sintaxis y 25 pruebas Python existentes de compras, historiales seleccionados y propuestas de venta.
