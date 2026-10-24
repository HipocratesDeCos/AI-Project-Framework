# Buscar artículos dentro del proveedor de una propuesta de compra

El apartado Artículo incorpora búsqueda por SKU, descripción o familia y un selector de familias, siempre restringidos al proveedor elegido. Admite varias palabras sin distinguir tildes ni mayúsculas. Las familias proceden del catálogo; los artículos sin ese dato se consultan con «Sin familia documentada».

El desplegable muestra las primeras 200 coincidencias ordenadas por SKU, con el recuento total y aviso para afinar cuando hay más. El artículo ya seleccionado se conserva en un grupo explícito si queda fuera del filtro o del límite. La búsqueda no sustituye automáticamente el SKU ni modifica cantidades, precios, descuentos o condiciones. Sus controles no forman parte del envío de la propuesta; filtrar no solicita una nueva cotización. Enter en la búsqueda no envía el formulario.

«Limpiar búsqueda de artículos» retira solo texto y familia y devuelve el foco al buscador, conservando el artículo y los datos de la operación. Elegir realmente otro artículo mantiene la actualización habitual de ficha, compras históricas, existencias y unidad. La ficha muestra ahora la familia documentada del SKU elegido; si falta, conserva «Sin datos».

Cambiar de proveedor limpia los filtros y conserva el comportamiento previo de seleccionar inicialmente su primer artículo. Las opciones y familias no incluyen artículos de otros proveedores. La navegación desde Stock y la búsqueda general pasan el SKU solicitado expresamente, por lo que puede abrirse aunque esté fuera de los primeros 200 resultados.

Los controles comprueban el dataset activo y se deshabilitan si el estado cargado no corresponde a la empresa seleccionada. No se vinculan artículos por descripción ni se modifican fichas, stock, historial o propuestas guardadas.

## Validación

JavaScript completo: 301 artículos de un proveedor y uno de otro; límite de 200, familias y dato ausente, búsqueda por varias palabras sin tildes, conservación de SKU y condiciones, ausencia de recotización al filtrar, familia visible, selección real, apertura desde Stock/búsqueda general fuera del límite, cambio de proveedor y empresa. Comprobación de sintaxis y 15 pruebas Python existentes de pantalla de compra, compras documentales, catálogo comercial y orden de carga.
