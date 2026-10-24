# Buscar cliente en Propuestas de venta

La propuesta incorpora búsqueda por código y razón social. Admite varias palabras sin distinguir mayúsculas ni tildes y muestra las primeras 200 coincidencias, ordenadas por razón social y código, con el recuento completo. No combina clientes de nombres iguales: cada opción identifica su código.

Buscar no selecciona automáticamente un cliente. Si ya existe uno elegido y queda fuera de los resultados o del límite, se conserva en un grupo identificado. Limpiar la búsqueda mantiene el cliente, artículos y condiciones, y devuelve el foco al buscador.

Los eventos del buscador no recargan orientación ni invalidan la evaluación. Enter no envía el formulario. Seleccionar realmente otro cliente mantiene el recorrido existente: invalida la evaluación y actualiza las referencias de las líneas para el nuevo cliente. El buscador no forma parte del payload de la propuesta.

La consulta utiliza solo los clientes del dataset activo. Si el estado cargado corresponde a otra empresa, los controles se deshabilitan. Si se retira del estado la ficha del cliente elegido, se vacía su selección, se invalida la evaluación y se retiran los precios y consultas pendientes de sus líneas para exigir una nueva selección. Una propuesta nueva inicia la búsqueda y selección de cliente vacías, como antes.

## Validación

Ejecución DOM del JavaScript completo con 301 clientes: límite, nombres coincidentes con códigos diferentes, búsqueda por varias palabras sin tildes y por código, ausencia de selección automática, cliente conservado fuera de filtro/límite, condiciones y evaluación intactas al filtrar, recarga al cambiar realmente el cliente, foco, Enter, ficha retirada y cambio de empresa. Comprobación de sintaxis y pruebas Python existentes de propuestas, ventas seleccionadas y orden de carga.
