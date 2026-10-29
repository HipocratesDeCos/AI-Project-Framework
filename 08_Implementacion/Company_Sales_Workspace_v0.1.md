# Propuesta de venta: espacio de negociación

La pantalla separa cuatro tareas: seleccionar cliente y artículos, negociar, evaluar y completar el documento. La ficha e historial mantiene sus fuentes y referencias; los importes editables están en el paso 2.

## Condiciones propuestas

Cada línea conserva su cantidad, precio por unidad antes de descuento, descuento porcentual e IVA. La selección del artículo y las búsquedas están en el paso 1; los valores de línea se envían con el mismo contrato al servidor. El cambio de ubicación no cambia las fórmulas de cálculo ni la autoridad del resultado.

Forma de pago y plazo son dos selectores nativos independientes. Se ofrecen transferencia, recibo domiciliado, pagaré, efectivo y otra forma. El plazo puede ser contado/a la vista, 30, 60 o 90 días, o fecha personalizada. Los días se suman a la fecha de propuesta como días de calendario, sin ajustes por festivos. Cambiar el vencimiento manualmente selecciona fecha personalizada. Cambiar la fecha de propuesta recalcula solo un plazo fijo; una fecha personalizada permanece igual y el servidor verifica su coherencia.

La alternativa calculada conserva su vencimiento y el texto íntegro de las condiciones en el detalle del cobro. El contrato existente `payment_terms` recibe la forma, el plazo y el detalle; la fecha sigue enviándose separadamente en `due_date`. No se crea un nuevo mandato bancario ni se registra un cobro.

Los portes distinguen el coste de la empresa y el importe facturado al cliente, con su IVA. No se supone coste cero cuando sigue pendiente de declarar.

## Presentación del resultado

La evaluación se muestra en el paso 3 y recibe foco y desplazamiento después de calcular. Una propuesta no apropiada se destaca en rojo con sus motivos. Los demás resultados conservan el aviso ámbar de validación pendiente; no se inventa aprobación verde. Las alternativas y los indicadores permanecen visibles; el detalle financiero tiene su propio desplegable. Un IVA desconocido se muestra como pendiente, no como cero.

Cualquier edición invalida el resultado anterior y el guardado. Las referencias, la autoridad decisional y la ruta operacional mantienen sus restricciones existentes.

## Validación

- Pruebas Python de propuestas, vista previa y negociación.
- `tests/browser/sales_proposal_workspace.cjs`: prueba HTTP y DOM con jsdom y la base de prueba `SalesNegotiationTest`, servidor en un puerto local libre. Comprueba fechas fin de mes, plazos 30/60/90, fecha manual, formas de pago, resultado rojo, IVA pendiente, aplicación de alternativas, invalidación, guardado, eliminación de líneas y búsqueda. Requiere jsdom accesible mediante `EIOS_JSDOM_MODULE` o resolución normal de Node.
- Ejecutar con `python tests/browser/run_sales_proposal_workspace.py`.
- La prueba utiliza una base temporal y no modifica expedientes de la empresa.
