# Conexión documental financiera con la propuesta v0.1

## Resultado
Guardar propuesta abre automáticamente su revisión en la interfaz. La revisión conserva una captura financiera de la empresa/versión seleccionada: situación financiera canónica, magnitudes documentadas de activo/pasivo corriente, movimientos canónicos de cobro/pago con fechas, moneda, importes y estado de evidencia, además de referencias y soportes. Se presenta en pantalla y en el informe imprimible.

Esto conecta datos existentes. No ejecuta todavía Finance Basic ni genera viabilidad o alternativas. Estado explícito NOT_EXECUTED / NOT_EVALUATED; sin autoridad decisoria y FORBIDDEN. La información insuficiente para una proyección se distingue de la falta de integración del Centro, paquete financiero, admisión y pagos de propuesta.

## Lectura y trazabilidad
Se usa exclusivamente el dataset seleccionado; los archivos recibidos pendientes no se activan. Se revalidan FinancialSnapshot, WorkingCapitalInput y CashFlow con los modelos existentes, sin transformar NOT_EVIDENCED en DEMONSTRATED. Se comprueba empresa/corte y compatibilidad de monedas, identidades duplicadas o distintas del registro. Ausencias y errores se conservan como incidencias explícitas, sin cero por defecto.

Solo cash_flow proporciona la lista canónica de movimientos. Cuotas, facturas y previsión diaria no se incorporan de nuevo como movimientos adicionales. Esto evita sumar varias representaciones, pero no demuestra ausencia de duplicados económicos dentro del inventario, su completitud ni conciliación; esos estados permanecen desconocidos.

La captura conserva todos los registros fuente de los tipos seleccionados y su huella. El identificador de revisión v02 incluye esa captura antes de persistir. Se comprueba que el contexto documental no haya cambiado durante la revisión. El informe exporta la captura histórica exacta.

## Fronteras y siguiente integración
No se extrae tesorería disponible sumando saldos 570/572, extractos o arqueos sin conciliación explícita. No se elige un horizonte a partir del último vencimiento ni se usa mínimo cero. Los valores del Centro de Parametrización y la evidencia financiera deben vincularse conforme a FIN-DIP-01 y Finance Horizon Provenance. Los pagos de la propuesta necesitan pertenencia explícita y tratamiento de cuotas, portes, IVA y coincidencias con flujos ya existentes antes de comparar base y compra. No se alteran contratos cerrados, cálculos o Rules.

## Verificación
Pruebas de alcance por empresa, conservación de valores y evidencia, ausencia de suma duplicada de cuotas/previsión diaria, errores canónicos, identidad duplicada, captura persistida e informe histórico y ausencia de defaults. CI Python/SQL y sintaxis/HTTP existentes. Entorno local desconectado: no se ha inspeccionado directamente la base Windows del usuario ni se afirma que sus documentos hayan pasado conciliación.
