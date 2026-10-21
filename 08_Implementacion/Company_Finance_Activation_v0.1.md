# Activación financiera local y ejecución documental v0.1

## Alcance
Permite activar expresamente P-FIN-001 (horizonte, entero positivo, días) y P-FIN-002 (mínimo, EUR, no negativo) previamente guardados en Parámetros. Usa ParameterConfigurationCenter y sus puertos sin cambiar el contrato ni Rules. Los demás parámetros continúan como solicitudes preparadas.

## Autorización y vigencia del piloto local
Solo admite datasets declarados SYNTHETIC. La activación requiere revisión preparada vigente, revisión financiera previa, responsable, motivo y confirmación expresa en formulario separado. La identidad es una declaración local registrada, no autenticación corporativa. No acredita autorización para una empresa real ni admisión operacional.

Los valores quedan ligados al corte financiero: intervalo [inicio del día de corte, inicio del día siguiente), UTC. Esta vigencia de resolución no limita la proyección a un día: su horizonte es P-FIN-001. Dos configuraciones y sus historiales se insertan en una transacción BEGIN IMMEDIATE. Se rechazan solapamientos y revisiones preparadas desactualizadas. Una repetición con los mismos valores es idempotente; otros valores para el mismo corte no sobrescriben la activación conservada. Esta primera versión no gestiona correcciones ni sustituciones de activaciones para el mismo corte; esa capacidad requiere un flujo trazable posterior.

Las tablas SQLite locales reproducen los campos contractuales de Configuration/HistoryEntry para la prueba sintética, sin modificar la persistencia SQL Server aprobada. El Centro comprueba catálogo, autorización local explícita, tipado y vigencia.

## Ejecución
Al revisar una propuesta se intenta resolver las dos configuraciones por empresa y corte. No hay valores por defecto. Se construye un FinanceBasicInput desde la situación financiera, working capital y lista completa de cash_flow canónicos vinculados. Se usa el snapshot ID financiero sin renombrarlo al digest del dataset. Se valida empresa, corte, identidad y unicidad de movimientos y no se admite una lista parcial o ausencia de inventario como cero flujos.

build_finance_decision_input_package captura la operación y los datos financieros con las configuraciones del Centro. DecisionContext identifica la selección local mediante la huella de las configuraciones; rules_version=NOT_EXECUTED expresa que no se selecciona ni ejecuta paquete de Rules. No sustituye Decision Versioning.

run_provenanced_finance_basic ejecuta el motor existente. NOT_EVIDENCED y CONFLICTING_DATA se conservan, sin transformar documentos recibidos en evidencia demostrada. El mínimo cero conserva el tratamiento NOT_EVALUABLE del margen porcentual.

## Lo que representa el resultado
SUPPLIED_DOCUMENTARY_CASH_FLOWS_ONLY: analiza la lista documental suministrada. No demuestra conciliación, completitud ni relación de flujos con esta propuesta. No representa aún un escenario sin compra frente a uno con compra, ni añade pagos desde cantidad*precio, total, vencimiento o plazo de formulario. El vínculo documental y calendario de cuotas de la compra sigue pendiente.

La salida mantiene purchase_effect_status=NOT_EVALUATED, viability_status=NOT_EVALUATED, decision_authority=false y operational_path=FORBIDDEN incluso si la proyección documental es DETERMINED. No ejecuta QTG, Rules o decisor ni presenta alternativas viables.

## Interfaz y conservación
La pantalla distingue valores preparados de los dos activados para el corte. La revisión v03 y su informe muestran parámetros, resultado de proyección y limitaciones, y conservan la salida junto con la huella del paquete financiero. Las revisiones históricas no se recalculan al exportarlas.

## Verificación
Activación atómica, historial, idempotencia, ámbito empresarial, rechazo de material real y de sobrescritura/cambio desactualizado, ejecución sin defaults, conservación de evidencia, motor existente con flujos sintéticos demostrados, ausencia de efecto de compra y salida histórica, mínimo cero, HTTP con token y sintaxis JavaScript. CI Python/SQL; entorno local desconectado y revisión visual pendiente.
