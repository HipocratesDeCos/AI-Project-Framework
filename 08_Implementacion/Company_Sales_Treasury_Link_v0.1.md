# Vínculo de tesorería para propuestas de venta

## Recorrido

Desde Propuesta de venta, abrir «Vincular caja, bancos y previsiones», buscar archivos recibidos y escoger el archivo de saldos contables. Marcar las cuentas 570 y 572 o sus subcuentas, revisar la suma y, si corresponde, seleccionar el calendario de cobros y pagos. Indicar responsable y motivo, confirmar el alcance y pulsar «Vincular estos datos a ventas». Después evaluar de nuevo. Se mantienen cliente, cantidades y precios del formulario.

La selección se prepara una vez por versión de empresa y corte. No hay que volver a subir los soportes recibidos ni teclear un saldo. Si no hay archivos compatibles, la pantalla identifica la empresa y corte esperados; el usuario debe revisar la recepción. Los archivos con razón social equivalente tras normalizar mayúsculas, acentos, espacios y puntuación pueden mostrarse con otro código interno. Se exige confirmación explícita de identidad; no se crea una equivalencia automática ni se cambian los metadatos originales. Las razones sociales distintas, fechas o naturalezas incompatibles siguen excluidas, con diagnóstico visible.

## Contrato y límites

- Solo empresas sintéticas y el mismo corte, en EUR. La identidad coincide exactamente o se confirma expresamente una diferencia de código/escritura de la misma razón social.
- Se selecciona un archivo de saldos y cuentas explícitas. Se rechazan cuentas distintas de 570/572 y subcuentas numéricas, duplicados, saldos negativos, monedas distintas y suma simultánea de padres e hijos. Un saldo cero explícito es válido.
- El responsable declara que las cuentas elegidas son utilizables para la simulación y no contienen importes restringidos. No es una verificación automática de disponibilidad ni de conciliación. No se deduce crédito disponible ni se añaden cobros futuros al saldo inicial.
- El calendario recibido opcional reemplaza los movimientos utilizados en ventas; nunca se añade al calendario base. Cada movimiento mantiene identidad y fila de origen, con evidencia `NOT_EVIDENCED`. Elegir previsión de base utiliza los movimientos documentales originales.
- La selección afecta al contexto financiero de ventas y a su plan de cobros/pagos, no sobrescribe registros documentales ni cambia automáticamente otros consumidores.
- `FinancialSnapshot` recibe la suma decimal y una referencia a la declaración de selección. La huella de la propuesta incluye la selección y sus fuentes. La procedencia aparece en el detalle financiero de la evaluación.
- El motor financiero existente recibe ese saldo y ese calendario; las cuotas nuevas siguen requiriendo declaración y las ya documentadas se reutilizan sin duplicar. La ejecución puede seguir siendo `NOT_EVIDENCED`: ejecutar el cálculo no certifica evidencia, completitud, crédito ni viabilidad.

## Versiones e integridad

Se conserva historial por dataset, responsable, motivo, cuentas, archivos, filas y huellas. Cambio o desaparición de un origen provoca fallo cerrado: no se reutiliza silenciosamente un saldo antiguo. Retirar el vínculo recupera los portadores originales. Ofertas y planes guardados conservan su contenido; no se editan cuando ha cambiado el contexto.

## Verificación

`tests/test_company_sales_treasury.py`: selección, suma 650 + 58.300, sustitución del calendario, rechazo de mezcla de empresas y niveles, confirmación obligatoria, fuente alterada, retirada y conservación del plan anterior. Verifica ejecución del motor con el saldo seleccionado y evidencia pendiente.

`python tests/browser/run_sales_treasury.py`: HTTP y DOM con empresa y archivos temporales, selección en la pantalla y evaluación con tesorería de 58.950 EUR. Comprueba también el rechazo del vínculo antes de confirmar la diferencia de código de empresa y su aceptación tras confirmarla. Requiere Node y jsdom (`EIOS_JSDOM_MODULE` admite ruta al paquete instalado).
