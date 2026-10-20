# Consulta de cobros, pagos y saldos recibidos

En **Carga de archivos → Expedientes recibidos**, filtrar empresa/corte, marcar los archivos de cobros/pagos y saldos y pulsar **Consultar tesorería y saldos seleccionados**. La selección debe pertenecer a una sola empresa, razón social, naturaleza real/sintética y fecha de corte. No cambia la empresa activa ni requiere volver a cargar los paquetes ZIP ya consultables en sus pantallas actuales.

## Consulta y procedencia

Se leen todas las filas conservadas, no solo la vista previa de veinte. La pantalla muestra:

- Sumas nominales de cobros y pagos por moneda, sentido y vencimiento hasta/posterior al corte.
- Cada referencia con vencimiento, contraparte o concepto si consta, importe, moneda y archivo/hoja/fila.
- Saldos por cuenta y moneda, manteniendo su signo, junto a las filas de origen.
- PDFs de soporte seleccionados, identificados como no extraídos ni conciliados automáticamente.

Un vencimiento anterior al corte no acredita que la operación siga pendiente ni que esté impagada. El formato recibido no dispone de estado de liquidación. Las sumas describen los importes seleccionados y no constituyen una previsión de caja, un neto de liquidez ni un veredicto sobre capacidad de compra.

## Repeticiones, contradicciones y ausencia de datos

`flow_id` identifica la referencia de cobro/pago dentro de la selección. Si aparece varias veces, conserva todas las filas y distingue repetición idéntica de datos contradictorios. No selecciona una versión, deduplica ni suma esas referencias. Cada grupo de moneda/sentido/vencimiento afectado muestra importe no determinable; los grupos sin referencias ambiguas siguen mostrando su suma documentada. Una contradicción de moneda, dirección o fecha afecta a todos los grupos en los que figure esa referencia.

Para los saldos, la clave es cuenta y moneda. Una sola fila permite mostrar el saldo documentado. Varias filas, aunque sean iguales, impiden ofrecer un saldo único. No se suman cuentas padre y subcuentas, monedas, activos y pasivos, ni se netean saldos con cobros o pagos. Las filas negativas conservan su signo.

Las sumas usan Decimal con precisión adaptada a los importes y número de filas. Cero es un importe documentado; la ausencia de datos produce una tabla sin datos, no un saldo cero. Una contraparte ausente se muestra como no documentada. No hay inferencia automática de terceros ni conversión de moneda.

## Estado y límites

La operación es de lectura, mantiene `PENDING`, `FORBIDDEN` y `decision_authority=false`. No concilia bancos, arqueos, impuestos, saldos, vencimientos o PDFs; tampoco activa reglas financieras, modifica propuestas ni ejecuta compras. **Comprobar expediente seleccionado** mantiene su alcance previo de referencias y unidades.

Cambiar una casilla o el contexto elimina el detalle financiero y descarta respuestas pendientes de la selección anterior. La consulta de artículos permanece independiente, compartiendo las mismas garantías de selección explícita.

`POST /api/reception/financials` recibe `batch_ids` (1–100 lotes) y requiere Host local y token de sesión. Devuelve filas con procedencia, resúmenes, documentos de soporte, avisos de recepción y alcance; no guarda evaluaciones ni decisiones nuevas.
