# Revisión documental de calidad en propuestas de venta

## Recorrido

En **Propuestas de venta → Evaluación de la propuesta → Calidad y cobertura de datos**, pulsa **Abrir revisión de datos y soportes**. El panel también está disponible directamente antes del documento de oferta.

1. **Movimientos y soportes.** Por defecto aparecen discrepancias y pendientes. Cada movimiento permite consultar su fila de origen y las cuotas localizadas. El cruce técnico exige referencia inequívoca, pendiente al corte, moneda y vencimiento coincidentes. No sustituye pendiente desconocido por importe original. Las exportaciones repetidas de una misma cuota solo se agrupan si sus hechos comparables coinciden.
2. **Asociar soporte.** Busca un documento recibido o fila, consulta o descarga el original, selecciona el movimiento y explica lo contrastado. La asociación queda en borrador hasta guardar. Un vínculo no oculta una discrepancia técnica ni acredita el pago.
3. **Cobertura.** Declara periodo y fuentes revisadas. Las cuotas positivas o de pendiente desconocido no localizadas en el calendario aparecen por separado. No se admite declarar cobertura completa con cuotas sin localizar dentro del periodo, ni sin movimientos utilizables. Otros cobros y pagos no documentados no pueden detectarse por inferencia.
4. **Saldo inicial.** Selecciona un extracto, arqueo o soporte independiente e introduce el saldo leído. El valor no se copia del saldo contable. EIOS compara importes y conserva diferencias. No admite el mismo archivo de saldos como soporte independiente. Los datos estructurados conocidos de cuenta, saldo, corte y moneda deben coincidir con la observación.
5. **Guardar.** Indica responsable y conclusión y confirma el alcance. Se conservan fecha, versión, fuentes y huellas. Después evalúa de nuevo la propuesta. Se mantienen precios y cantidades. Un cambio en las fuentes deja la revisión anterior como histórica; no la reutiliza como vigente.

## Selección y alcance

Se usan los archivos financieros efectivos de la empresa, última fecha de corte y últimas versiones, o la excepción manual vigente del panel de tesorería. Los soportes recibidos deben pertenecer a la misma entidad sintética y corte. No se extrae ni verifica automáticamente el contenido de un PDF: su lectura es una declaración humana registrada.

La pantalla distingue coincidencia técnica, discrepancia, pendiente y revisión declarada. La cobertura del calendario y el contraste del saldo se conservan separadamente. Un registro de revisión no ejecuta el circuito formal de calidad, no promueve `NOT_EVIDENCED` a `DEMONSTRATED`, no modifica `opening_treasury_reconciled` y no concede autoridad comercial. Se mantienen `decision_authority=false`, `operational_path=FORBIDDEN` y `quality_evaluation_status=NOT_EXECUTED`.

En una propuesta sin aplazamiento, la tarjeta de crédito es informativa. Puede mencionar deudas históricas sin presentar esta venta como financiación. La condición a la vista tampoco demuestra que se haya recibido la transferencia. Las ventas aplazadas conservan las comprobaciones previas de vencidos.

## Verificación

Pruebas Python: cruces, duplicados, discrepancias, cobertura, observaciones independientes, versiones, ofertas congeladas y crédito a la vista/aplazado.

Prueba HTTP y DOM: `EIOS_JSDOM_MODULE=/ruta/a/jsdom python tests/browser/run_sales_quality.py`. Recorre consulta de origen, vínculo documental, saldo observado, cobertura, guardado e historial, y confirma que no se promueve evidencia financiera. También se verifican los recorridos existentes de tesorería y propuestas.
