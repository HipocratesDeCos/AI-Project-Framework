# Negociación rápida y preparación administrativa separadas

## Comercial

En Propuestas de venta, seleccionar cliente y artículos, negociar precio, descuento, logística y cobro y pulsar Evaluar. El resultado reúne total con IVA, vencimiento y las comprobaciones de margen, crédito aplicable y disponibilidad conjunta por SKU (incluidas líneas repetidas).

La conclusión distingue condiciones dentro de los límites comerciales comprobados, datos de la operación que faltan y condiciones a renegociar. No equivale a viabilidad económica acreditada ni aceptación. En cobro a la vista, el historial general no convierte la propuesta en financiación; recibir la transferencia sigue siendo un hecho distinto. Stock es una referencia al corte, sin reserva ni garantía de disponibilidad actual.

El cobro aplazado conserva las revisiones de riesgo crediticio y cobertura financiera: no se ocultan incidencias relevantes. Una falta de stock pide ajustar cantidad o confirmar reposición y no ofrece como solución escenarios que solo cambien precio.

## Administración

En Carga de archivos → Administración · Preparar datos para las propuestas están selección de caja/bancos/previsiones y revisión documental. Las fuentes automáticas, excepciones manuales y revisiones conservadas se reutilizan por empresa y corte. Los cambios invalidan su vigencia según las huellas existentes. Un botón permite volver a la oferta sin borrar las condiciones introducidas.

En el resultado comercial, fuentes, calidad general y alcance financiero quedan en un extensible cerrado. La conclusión de la operación sigue mostrando los datos determinantes que faltan. Esta separación es de recorrido; no implementa control de acceso por roles.

## Automatización financiera

Cada evaluación envía al motor Finance Basic un escenario separado de cobro único del total con IVA en el vencimiento propuesto cuando están activos horizonte y mínimo financiero. No exige guardar la oferta ni preparar un plan manual para ese escenario. No escribe movimientos, no reserva stock y no combina las ofertas guardadas.

No se añaden pagos de mercancía, logística o regalos sin importe bruto y fecha conocidos. Se muestran las hipótesis y las limitaciones. Si hay un cobro con el mismo importe y vencimiento en la base, la simulación se detiene para evitar una duplicación plausible. Un plan de cuotas o costes adicionales sigue siendo una opción avanzada sobre una oferta guardada.

Se conserva la ejecución real del motor con evidencia NOT_EVIDENCED cuando corresponde; no se elevan estados para obtener un resultado positivo. La orientación comercial mantiene decision_authority=false y operational_path=FORBIDDEN. El resultado financiero no declara capacidad cuando el motor no puede acreditarla. El circuito integral autorizado de ventas no se considera ejecutado.

## Verificación

Pruebas de conclusión comercial, incidencias administrativas conservadas, faltas determinantes, ventas aplazadas, suma de stock por SKU, motor automático con horizonte activo, ausencia de escritura de cobros u ofertas y prevención de duplicados posibles. Recorridos HTTP y DOM verifican ubicación administrativa, conclusión principal, extensible cerrado, conservación de las revisiones y recorridos existentes.
