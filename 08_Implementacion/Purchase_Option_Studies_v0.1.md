# Estudios independientes de las propuestas de negociación

Fecha: 06/11/2026. Cambio: EIOS-CHG-006.

## Decisión autorizada

El usuario solicita analizar tanto Mi propuesta como Propuesta del proveedor
antes de decidir qué negociar o acordar. Los nombres no implican quién inicia
la negociación ni aceptación de la otra parte. Se retiran del borrador los
recuadros naranjas de Sin guardar y Compra sin confirmar, que describían el
estado normal del proceso y no un problema accionable.

## Comportamiento

- Cada columna activada se analiza con sus propios precios, descuentos, IVA,
  portes, vencimientos y calendario. Ambas comparten empresa y versión documental,
  proveedor, artículo, cantidad, fecha del pedido y supuestos de stock declarados.
- La comparación muestra desembolso, dinero mínimo y falta para reserva. Los
  botones Ver mi estudio y Ver estudio del proveedor eligen el análisis detallado.
  La síntesis, gráfica y alternativas identifican la opción seleccionada.
- El calendario de Organizar los pagos pertenece a esa opción. Cambiar de opción
  conserva sus filas. Una opción sin cuotas utiliza la hipótesis existente de pago
  único, expresamente identificada; no hereda las cuotas de la otra.
- Seleccionar una opción permite estudiarla y guardarla como base. No acredita
  aceptación ni autoriza la compra. La selección se identifica antes de guardar.
  Sustituye la preferencia implícita por Mi propuesta cuando ambas estaban activas.
- Las alternativas sugeridas preparan hipótesis en Mi propuesta; no reescriben
  las condiciones recibidas del proveedor. Los cambios de cantidad afectan a la
  cantidad compartida y requieren recalcular ambos escenarios.
- Guardar conserva los dos estudios independientes que estén activados, con la
  opción principal identificada. Consultar otra opción guardada no cambia la
  propuesta principal ni la eventual declaración de acuerdo.
- El informe incluye ambos estudios, calendarios, síntesis, alternativas y fuentes
  conservadas. La copia a borrador conserva la selección y los dos calendarios,
  y mantiene la confirmación nueva de los supuestos de stock.
- Los estudios antiguos que no conservaron análisis independientes lo explican.
  No se reconstruye el pasado con datos actuales.

## Contrato y validación

Se reutilizan las APIs de cotización, previsión y guardado. No hay endpoints,
dependencias, decisiones empresariales ni estados operacionales nuevos.

`negotiation_selected_slot` identifica la opción principal. El servidor exige
que exista entre las opciones activas y que sus importes, impuestos, portes,
vencimiento y cuotas coincidan con la propuesta principal. Un desacuerdo impide
guardar. Los clientes anteriores sin selección explícita mantienen su contrato.

Las entradas de `negotiation_at_save.alternatives` conservan su quote, condition,
payment_plan y cash_orientation. Cada patch puede declarar payment_installments;
su ausencia no copia el calendario principal a la otra opción. Los cálculos
se hacen con los validadores y el motor de previsión existentes en el servidor.
No se confía en resultados financieros enviados por el navegador.

Las respuestas de previsión se invalidan al editar, cambiar de empresa o pasar
a consulta histórica. Las condiciones y sus estudios se mantienen enlazados por
slot; una respuesta tardía no cambia el contexto seleccionado.

Los resultados calculados se contrastan por contexto documental, fuente
financiera, activación de parámetros, saldo inicial, reserva, corte y horizonte.
Si cambian durante la comparación, la interfaz pide recalcular y el servidor
rechaza conservar una comparación incoherente. El guardado reutiliza una misma
captura del estado financiero para analizar sus opciones.

## Límites y presentación

Mantener la reserva en un escenario no certifica viabilidad final ni aceptación.
Los indicadores de borrador y cambios sin guardar quedan en la cabecera neutral.
El bloque financiero conserva solo el resultado que requiere interpretación o
una acción; no presenta la falta de confirmación como una incidencia permanente.

Se conservan los campos y cálculos comerciales, la referencia histórica del libro,
los informes anteriores, las fuentes locales y el modo oscuro. La ruta operacional
permanece FORBIDDEN y decision_authority sigue siendo false.

## Verificación

`test_company_purchase_option_studies.py` comprueba cálculos propios, calendarios,
selección coherente, rechazo antes de insertar y conservación financiera.
`purchase_option_studies.cjs` reproduce 13.310 y 14.520 EUR, proveedor que inicia,
consulta de ambos análisis, cambio de cuotas sin mezcla, guardado de proveedor,
informe congelado, copia seleccionada y alternativa que no modifica al proveedor.
Las pruebas existentes de copia, guía, consulta histórica, acuerdos, alternativas
combinadas, tipografía y respuestas tardías comprueban las regresiones relevantes.
