# Buscar artículos por familia en Propuestas de venta

Cada línea de la propuesta incorpora búsqueda por SKU, descripción o familia y un selector de familias del catálogo activo. Admite varias palabras, sin distinguir mayúsculas ni tildes. «Sin familia documentada» consulta artículos con familia vacía o ausente; no añade familias al catálogo.

Se muestran las primeras 200 coincidencias ordenadas por SKU, junto con el recuento completo y un aviso para afinar cuando quedan más resultados. Esto evita construir miles de opciones por cada línea. Las referencias de ventas pendientes de ficha se mantienen deshabilitadas y separadas de los artículos del catálogo.

## Selección y condiciones comerciales

Filtrar no selecciona otro artículo ni llama al servicio de orientación. Conserva SKU, cantidad, precio, descuento, IVA y evaluación. Si el SKU ya elegido queda fuera del filtro o de los primeros 200 resultados, aparece en un grupo identificado como artículo conservado, manteniendo su selección.

Seleccionar realmente otro artículo mantiene el recorrido existente de carga de ficha, historial y precio. Los controles de búsqueda no forman parte del payload de la propuesta y sus eventos no invalidan la evaluación ni marcan como editadas las condiciones. Pulsar Enter en la búsqueda no envía el formulario. Cada línea mantiene sus filtros propios; limpiar su búsqueda devuelve el foco al buscador sin borrar el SKU ni las condiciones.

Los controles se vinculan al dataset con el que se crearon. Si cambia la selección de empresa, se deshabilitan hasta la reconstrucción habitual de la propuesta. Una actualización del catálogo dentro del mismo dataset reconstruye las familias y consulta las fichas vigentes, conservando el SKU si sigue disponible. Si se retira su ficha, se invalida la evaluación y se vacía su precio para exigir una nueva selección. No se vinculan referencias por descripción ni se activan fichas pendientes.

## Validación

Ejecución DOM del JavaScript completo con 301 artículos: límite de 200, familia y campos ausentes, búsqueda por varias palabras sin tildes, SKU conservado fuera del filtro/límite, campos comerciales y evaluación intactos, líneas independientes, referencias pendientes deshabilitadas, Enter y cambio de empresa. Comprobación de sintaxis y 20 pruebas Python existentes de propuestas de venta, catálogo comercial, ventas seleccionadas y orden de carga.
