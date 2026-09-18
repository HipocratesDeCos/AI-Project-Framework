# EIOS — DOC-PAY-COVER-01 — Auditoría de implementación v0.1

Fecha: 18/09/2026. Baseline: c719602724fe949bd2a9a0ab2221d3355e96b9bf; CI #855 SUCCESS.

## DISEÑAR

Implementar el contrato Operation_Required_Installment_Coverage_Contract_v0.1.md integrado en PR #172. Añadir comprobador complementario, modelos de calendario declarado y pruebas; ningún cambio a modelos/motores/capturas cerrados.
El calendario se recibe explícitamente con fuente/autoridad declaradas, referencias, naturaleza, cuotas, secuencia, soportes y total. No se descubre desde PDF ni se autentica al declarante. El registro conserva calendario completo y captura examinada, exportaciones independientes y fingerprint calculado.

## AUDITAR

A1: total coincidente no demuestra identidad de cuotas. Comparar conjunto requerido y bindings por identidad, cada importe/moneda/fecha y referencias completas, incluidas versión y confirmación.
A2: calendario inválido podría fabricar cobertura. Revalidar modelos copiados, rechazar duplicados de identidad/secuencia, importes no finitos, suma distinta, monedas incompatibles y secuencia de vencimientos incoherente.
A3: dos soportes no deben duplicar flujos. Comprobar soportes asociados al binding, sin crear, fusionar ni corregir flujos financieros.
A4: calendario fuera del horizonte sigue requerido. No filtrar cobertura por horizon_days ni llamar al motor financiero.
A5: estado no evidenciado no cambia por coincidencia estructural. Conservar evidence_state y due_date_evidenced observados; un match no acredita contenido o ejecución.
A6: un pago adicional sin binding podría ser otra compra o alias duplicado. Conservar todos los unassociated_payment_flow_ids, sin atribución económica ni descarte silencioso.
A7: resultado desprendido permite reutilización inválida. Validar pertenencia a captura íntegra/fingerprint y calendario íntegro; cualquier cambio de autoridad, cuota, soporte o contexto cambia material.

## DEPURAR

required_calendar_matches significa exclusivamente correspondencia estructural de las cuotas declaradas, referencias y soportes asociados. No significa completitud económica empresarial, admisibilidad, pago realizado, revisión autorizada ni APTO. Puede ser verdadero mientras existen flujos adicionales sin asociación o estados no evidenciados, que permanecen visibles como límites de la observación.
Salida limitada a DECLARED_CALENDAR_STRUCTURAL_MATCH_ONLY. La naturaleza de calendario y captura se conserva separadamente; PRESENTED_OPERATIONAL no autentica material. El calendario sintético de dos cuotas no se convierte en una política universal de pago.
El orden de almacenamiento no determina secuencia; ésta procede del campo declarado y de fechas estrictamente crecientes. No se evalúa precedencia por ejecución bancaria.
Las excepciones de calendario técnicamente inválido siguen siendo errores técnicos, no NO_APTO. Las discrepancias observadas se registran individualmente; no son nuevos estados QTG.

## AUDITAR 2

22 pruebas específicas satisfactorias con pytest 8.4.2: dos cuotas/dos soportes, omisión de cada cuota, total correcto con identidad incorrecta, discrepancias importe/moneda/fecha/importe desconocido, cuatro referencias ajenas, almacenamiento invertido, soporte no asociado, calendario inválido/duplicado/secuencia/no finito/bypass, pago adicional sin asociación, exportaciones inmutables y rechazo de reutilización sobre material diferente, estados no evidenciados y ausencia de llamadas a Finance/QTG.
Los soportes usados en pruebas son bytes sustitutos explícitamente sintéticos, no los bytes del PDF aportado ni demostración de revisión documental real. El calendario refleja la definición explícita recibida del titular.
Suite completa local: 1075 pruebas satisfactorias con pytest 8.4.2; cinco avisos de pruebas preexistentes. No se declara ejecutada la validación SQL local; se comprobará su paso en CI.
PASS técnico: comparación estructural reproducible del calendario recibido y vínculo exacto a ambos materiales. PENDIENTE: CI completa Python/SQL sobre HEAD y merge, soporte operativo G03, productor/binding específico QTG G04 y demás criterios del perfil financiero.

## CERRAR → MATERIALIZAR → CI

Cierre técnico condicionado a CI completa satisfactoria. Material: eios/core/required_installment_coverage.py, tests/test_required_installment_coverage.py y esta auditoría. No cambia contratos ni componentes cerrados.
La unidad avanza la observación física de cobertura requerida; no levanta QTG ni demuestra inclusión económica universal sin doble cómputo. Continuidad: determinar qué soporte verificable permite consumir cada observación necesaria y precisar el binding completo de evaluación QTG, manteniendo separados datos declarados y evidencia operativa.
