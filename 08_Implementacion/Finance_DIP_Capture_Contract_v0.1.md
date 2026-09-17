# EIOS — FIN-DIP-01 — Finance input capture v0.1

Baseline: `c42614c583298003706f9557c65e717b8ce8b67f`.
Estado: contrato técnico depurado y Audit 2 superada; integración pendiente.
Uso: QTG-DIP-G01-FIN, preparación de entradas para Finance Basic.

## Autoridad y alcance
FIN-AUTH-01/05/07, contratos Finance Basic v0.3 + corrección v0.3.1, Finance Horizon Provenance, DIP-AGG-01 y perfil QTG Finance Basic gobiernan este subconjunto.
Se añade una captura financiera separada; no se cambia DIP-AGG-01 ni modelos, firmas, cálculos, Rules o QTG cerrados.
No constituye un contrato de productor QTG ni acredita origen ERP, pagos de compra o clasificación contable.

## Entrada y composición
`build_finance_decision_input_package` recibe purchase, context, evidence, finance_input completo, company_id, effective_at, requested_parameter_ids y ParameterConfigurationCenter.
No recibe un DIP preconstruido, resultados analíticos ni configuraciones desprendidas.
Revalida/copia profundamente FinanceBasicInput y contexto antes de consultar el Centro.
Reutiliza build_decision_input_package con el snapshot del input financiero; no acepta un segundo snapshot independiente.
Captura todos los campos FinanceBasicInput, incluidos cash_flows, horizon_days, treasury_minimum y working_capital_input, con sus estados y None.
Una colección vacía conserva el valor del FinanceBasicInput explícitamente suministrado; no se fabrica desde la ausencia de captura del DIP anterior.

## Vínculos y errores técnicos
- Los cinco campos finance_input.context coinciden con el contexto raíz revalidado.
- Empresa/snapshot y propuesta/contexto cumplen el contrato DIP existente.
- requested_parameter_ids contiene P-FIN-001 explícitamente. Su configuración debe estar disponible; ausencia/omisión es error técnico, sin fallback.
- Horizonte: parámetros/empresa/instante/vigencia según DIP y Finance Horizon Provenance; effective_at.date() = snapshot.as_of_date; unidad exacta días; valor Decimal finito, positivo e integral, igual a horizon_days.
- Si treasury_minimum no es None, se selecciona explícitamente P-FIN-002 y su configuración debe estar disponible; valor numérico finito y no negativo, exactamente igual al mínimo suministrado, unidad EUR/€ conforme al bridge FIN vigente.
- P-FIN-002 expresa euros: este binding de mínimo suministrado exige snapshot.currency = EUR. No se convierte moneda ni se igualan magnitudes de unidades incompatibles. No es una restricción global de Finance Basic o del DIP.
- Si treasury_minimum es None se conserva None, aun cuando P-FIN-002 esté seleccionada y disponible. No se hidrata ni se inventa un mínimo; esa configuración sigue capturada en el DIP base.
- Un mínimo cero correctamente vinculado es aceptado por la captura; su indicador porcentual continúa NOT_EVALUABLE según el motor, que aquí no se ejecuta.
- Configuraciones adicionales seleccionadas conservan presentes/ausentes explícitos del DIP.
- Error de repositorio, configuración desconocida o vínculo inválido se propaga como error técnico, no NO_APTO ni Assessment.

## Captura, identidad y acceso
`FinanceDecisionInputPackage` conserva el DIP base inmutable y material canónico inmutable del agregado financiero.
Claves canónicas exactas: schema_version, decision_input_package, finance_input. schema_version = FIN-DIP-01/v0.1.
Canonización: JSON UTF-8, ensure_ascii=False, claves ordenadas, separadores compactos, Decimal mediante format(value, "f"), fechas/instantes isoformat, None y orden de colecciones preservados, sin IDs/timestamps aleatorios.
Fingerprint SHA-256 cubre el agregado completo. No sustituye el fingerprint DIP base, Trace C0 ni Decision Versioning; no firma ni demuestra origen.
Propiedades devuelven modelos reconstruidos/copias; no exponen referencias mutables internas. No hay constructor de importación externo.
Se expone el DIP base, el input financiero, la resolución del horizonte y, solo si existe mínimo suministrado, su resolución vinculada.
La evaluación/revalidación financiera posterior mantiene las fronteras públicas cerradas; este módulo no llama motores para validar una captura previa a QTG.

## Información conservada sin nuevo juicio
Estados NOT_EVIDENCED/CONFLICTING_DATA, flujos con moneda/fecha desconocida y working capital ausente o incompatible se conservan según los modelos existentes. No se corrige su semántica ni se interpreta su efecto QTG.
No se rechaza un working_capital_input incompatible que el modelo permite y cuyo tratamiento pertenece al motor.
No se genera pago desde precio*cantidad, fecha de operación o plazo; no se deduce pertenencia por flow_id/source_ref/importe.
La captura de toda la colección suministrada no demuestra que incluya todos los flujos empresariales ni los pagos de la compra.

## Aceptación
Pruebas de reconstrucción integral; contextos diferentes; modelos creados sin validación; selección/configuración omitida, ausente o incorrecta; horizonte inválido; mínimo distinto, no numérico o moneda/unidad incompatible; None preservado y cero aceptado; errores del Centro; mutaciones antes/durante/después de lecturas; sensibilidad del fingerprint al flujo, mínimo, working capital y metadatos; ausencia de ejecución analítica/QTG y de fabricación de pagos.
Suite Python completa y CI SQL sobre HEAD exacto; CI postmerge antes de cierre integrado.

## Gate
La materialización puede realizarse después del ciclo de auditoría de este contrato. El perfil físico de captura financiera queda entonces cerrado solo dentro de estas garantías.
QTG-DIP-G02/G03/G04 no quedan resueltos íntegramente: procedencia de pagos, observaciones de calidad y criticidad/applicabilidad siguen pendientes.
