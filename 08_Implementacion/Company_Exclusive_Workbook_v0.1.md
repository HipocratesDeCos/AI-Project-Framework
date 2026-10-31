# Expediente activo con un único Excel

## Uso

1. Recibir el libro XLSX con `97_Guia_Carga` desde Carga de archivos, o utilizar uno ya recibido.
2. Abrir **Expediente activo · Un solo Excel** y pulsar **Buscar libros recibidos de esta empresa**.
3. Comprobar archivo y fecha de corte. La lista propone primero el último corte y recepción de la misma entidad sintética.
4. Pulsar **Usar exclusivamente este Excel**. Se vuelven a leer y comprobar todas las hojas guiadas de esos bytes, incluidas las hojas que la recepción hubiera deduplicado contra una versión anterior.
5. EIOS crea y selecciona una versión documental aislada. La cabecera identifica `FUENTE EXCLUSIVA` y el selector identifica la versión `ACTIVO`. Configurar los parámetros de esa versión antes de evaluar propuestas.

La activación es una elección explícita de fuente para simulación, no una admisión operacional ni una validación financiera. Las versiones anteriores se conservan como histórico; no se admiten nuevas propuestas sobre una versión archivada cuando existe un Excel activo de la misma empresa. Los informes y propuestas guardados no se reescriben.

## Alcance de la versión

Se conservan los códigos exactos de cliente/proveedor/SKU, sin renumerar, buscar equivalencias por nombre ni fusionar con los registros de base. Clientes y proveedores mantienen los datos personales normalizados del libro.

Se materializan fichas, existencias y reservas declaradas, mínimos de inventario, líneas históricas y agrupaciones documentales de facturas, cuotas vinculables, saldos contables y movimientos de cobro/pago. Toda fila normalizada queda además conservada con hoja, fila y documento original. Las hojas auxiliares no interpretadas permanecen en el XLSX original.

No se copian catálogos adicionales, inventarios sintéticos previos, referencias seleccionadas, planes o propuestas antiguas. Los mínimos manuales de stock de otras versiones no se recuperan. Si falta un dato, continúa ausente. No se crea fondo de maniobra a partir de otro expediente. Los precios de referencia sin moneda/unidad compatibles no se convierten en una tarifa vigente.

Las facturas se agrupan por sus referencias declaradas. Si una cuota no tiene factura coincidente dentro del libro, su fila se conserva y se añade una incidencia; no se inventa una factura ni se busca en otra versión. Las referencias contradictorias que no pueden representarse inequívocamente impiden la activación.

## Finanzas y procedencia

La selección automática de saldos y previsiones, los soportes de calidad y los candidatos de tarifa se restringen a los lotes y bytes del libro activo. Una recepción posterior ajena no reemplaza sus cifras. Para cambiar la fuente se activa otra versión del libro. Las selecciones de inventario e históricos tampoco pueden introducir lotes ajenos; la incorporación de otro catálogo se rechaza en esta modalidad.

La tesorería inicial solo se deriva de cuentas 572 EUR con desglose utilizable; no se suman niveles padre/hijo ni se añade caja 570 por defecto. La política de tesorería existente permite revisar las cuentas de ese mismo libro. Sin un dato utilizable no se restaura una cifra anterior.

Se mantienen `SYNTHETIC`, `decision_authority=false`, `operational_path=FORBIDDEN` y movimientos `NOT_EVIDENCED`. Conservar, mapear o cruzar filas no acredita conciliación, disponibilidad actual, cobro/pago realizado ni viabilidad.

## Persistencia y comprobaciones

La instantánea y sus registros se insertan en una transacción, junto con el inventario de origen y la marca de expediente activo. La identidad es determinista para el mismo libro/mapeo/alcance; reactivarlo no duplica registros. Se conserva el archivo original y su SHA-256.

Las pruebas cubren exclusión de clientes originales, conservación de códigos, stock e histórico propios, saldos sin sustitución por otra recepción, ausencia de restauración cuando faltan datos, mínimos de origen, rechazo del cliente antiguo, integridad e idempotencia. El recorrido HTTP+DOM cubre búsqueda, activación, cabecera, cartera, versión activa por defecto e histórico conservado.
