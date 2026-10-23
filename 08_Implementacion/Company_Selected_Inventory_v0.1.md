# Selección de inventarios recibidos para consulta en propuestas

## Recorrido de pantalla

1. En Carga de archivos, descargar la plantilla Inventario si hace falta. Preparar SKU, unidad y físico, con reservado cuando se conozca. Los códigos son texto y las cantidades valores fijos.
2. Recibir cada XLSX/CSV como **Inventario**, con el mismo código, razón social, naturaleza ficticia y corte de la empresa documental activa. Guardar en expediente. La recepción por sí sola no modifica las existencias de la pantalla activa.
3. En **Expedientes recibidos**, marcar solo los archivos de inventario que se quieran usar juntos. Para un catálogo grande se pueden recibir partes separadas (cada tabla conserva su límite de 5.000 filas). No repetir SKU entre partes ni sumar almacenes sin una preparación explícita previa.
4. En **USAR INVENTARIOS RECIBIDOS EN STOCK Y PROPUESTAS**, pulsar **Ver cambios de los inventarios marcados**. Revisar cantidades anteriores y propuestas de físico, reservado y disponible, unidad, archivo y fila. La muestra contiene hasta 100 filas y muestra los conteos completos de filas y errores.
5. Indicar responsable, motivo y confirmar expresamente el alcance de referencia al corte. Pulsar **Usar estas existencias en Stock y propuestas**.
6. La pantalla se refresca: Stock y las fichas de compra/venta muestran las cantidades seleccionadas con procedencia. Se recalculan los avisos descriptivos de mínimo aplicables a esas cantidades; no se emiten órdenes ni se autoriza una compra.
7. **Retirar la selección de inventario**, con responsable y motivo, restaura las referencias originales del caso. Se conservan los archivos, el historial de selecciones y los valores de las propuestas ya guardadas.

## Validación y semántica

Se admiten entre 1 y 100 archivos distintos, hasta 20.000 filas combinadas. Todos deben ser inventarios de la misma empresa ficticia, razón social y corte documental activos, con bytes íntegros. Cada SKU debe existir en el catálogo activo, incluidos los artículos incorporados mediante catálogo comercial. La unidad debe coincidir exactamente; no se convierten palets, cajas o litros. No se admite un SKU dos veces entre partes, aunque sus cantidades sean iguales.

Físico y reservado, cuando exista, deben ser finitos y no negativos. Disponible se calcula como físico menos reservado, sin confiar en un total aportado. Un reservado ausente conserva reservado y disponible desconocidos. Un reservado mayor que físico produce disponible negativo; no se corrige a cero y el aviso descriptivo conserva ese déficit.

La selección sustituye a la selección recibida anterior completa: no acumula automáticamente todos los inventarios cargados. La vista previa indica cuántos SKU dejan de utilizar aquella selección. Para los SKU no incluidos se mantienen las referencias originales del caso, si existen; nunca se inventan cantidades. Por ello deben marcarse juntas todas las partes que deban usarse. La selección queda ligada a un dataset exacto y no se propaga a otras versiones ni empresas.

Los parámetros mínimo, seguridad, punto de pedido y plazo que estén en la tabla recibida no se activan con este botón. Se conservan los mínimos manuales existentes y el criterio automático previo cuando tenga una compra comparable. La planificación anterior no se reutiliza para el stock recibido: se muestra cobertura pendiente hasta completar su vinculación. No se modifica el motor STK ni se falsifica su etiqueta de origen.

Balances, caja/bancos, previsiones, compras y ventas permanecen intactos. Tampoco se deduce inventario del catálogo comercial, que carece de cantidades. Para un corte distinto hay que preparar la versión documental correspondiente; este botón no mezcla fechas de distintas versiones financieras.

## Persistencia y vigencia del origen

`company_inventory_selection` registra revisiones append-only por dataset con archivos, huellas de origen, responsable, motivo y fecha de selección/retirada. Los originales siguen en `received_company_batch`. `read_inventory` combina la selección vigente con las referencias originales sin sobrescribirlas. El contexto de propuestas incluye la huella de la revisión y el estado actual de sus fuentes, por lo que rechaza formularios antiguos tras una selección, retirada o cambio del origen.

Tickets aleatorios de un uso, ligados al contexto y a los archivos comprobados, con diez minutos de caducidad. Se vuelven a comprobar contexto, integridad y huellas bajo la transacción de selección. Repetir una selección idéntica es idempotente. Si una fuente seleccionada desaparece, cambia de contenido o contexto, se informa de selección no vigente y se ocultan las cantidades, sin recuperar silenciosamente cifras anteriores. La retirada expresa permite volver a las referencias originales.

Los registros documentales, bytes de soporte e inventario sintético inicial no se reescriben. Las propuestas guardadas conservan su contenido y stock de referencia capturado. La recepción y esta selección no constituyen admisión operacional ni evidencia validada; `decision_authority=false` y `operational_path=FORBIDDEN` se conservan.

## Verificación

Cinco pruebas nuevas: recepción/vista previa sin activar, selección y snapshot de oferta, retirada, contexto antiguo, empresa/corte/unidad/SKU incompatibles, partes duplicadas, reserva desconocida, idempotencia, fuente modificada antes/después de seleccionar, recuperación expresa, confirmación, caducidad, planificación no reutilizada, inventario multipartes para una ficha del catálogo comercial y sustitución parcial con retorno a referencias originales.

Recorrido DOM/HTTP contra una copia de A Monkey: recibir CSV, marcar archivo, comparar, confirmar, consultar físico 2/reservado 1/disponible 1 de ATM-BL-05L, comprobar aviso BAJO MÍNIMO y procedencia en Stock, compra y venta, y retirar recuperando el inventario original exacto. Registros y bytes documentales permanecieron idénticos en la copia y la base original. JavaScript comprobado sintácticamente; revisión visual en navegador pendiente.
