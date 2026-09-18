# EIOS — QTG-FIN-G04-01 — Diseño de vinculación de evaluación v0.1

Fecha: 18/09/2026. Baseline remoto: abf497efd9fba1238b695a870d41283670c7013b; CI #859 SUCCESS.
Prioridad confirmada por el titular: piloto financiero acotado, sin ampliación del Vertical.
Estado: diseño de vínculo y condiciones de ejecución auditado; productor QTG operativo no autorizado ni implementado.

## DISEÑAR — alcance

Consumidor: run_provenanced_finance_basic. Fuentes: QTG v0.4; QTG_DIP_G01_Finance_Basic_Intended_Use_v0.1.md; QTG_FIN_Finding_Applicability_Criticality_Matrix_v0.1.md; contratos FIN-DIP-01, DOC-PAY-CAP/REVIEW/ROLE/DESIG/COVER-01 y auditoría DOC-PAY-CHAIN-01.
No modificar QualityCheck, QualityTrustResult, evaluate_quality, motores ni invocadores cerrados. No levantar cuarentena del Vertical ni crear API, repositorio empresarial o esquema SQL.

### A. Preparación vinculada — siguiente implementación legítima

Conservar un registro complementario inmutable de material preparado para el perfil financiero. No es un resultado de calidad ni ejecuta el gate.

| Material recibido | Conservación y obligación de vínculo |
|---|---|
| DocumentaryPaymentCapture construida | Payload completo, fingerprint calculado; incluye FIN-DIP, compra, cinco campos contextuales, snapshot, parámetros, flujos y documentos |
| RequiredInstallmentCalendar explícito | Payload completo, declaración/autoridad y naturaleza; no suplirlo por la colección de bindings |
| RequiredInstallmentCoverage construida | Payload y fingerprint completos; validar pertenencia exacta a captura y calendario; recomputar comparación estructural y contrastar payload antes de conservar |
| DocumentaryPaymentHumanReview opcional | Payload/fingerprint completos; cuando exista, validar pertenencia exacta a captura. Ausencia explícita no equivale a revisión vacía conocida o autorizada |
| DocumentaryReviewerDesignationLink opcional | Payload/fingerprint completos; requiere revisión presentada y validar pertenencia exacta a ella. Ausencia no rellena mandato |
| Material documental de criterios | Referencia/versiones declaradas, contenido íntegro y hash calculado de cada fuente presentada; referencias o hashes aislados no bastan |

La preparación exige captura, calendario, cobertura y material de criterios explícitos. Revisión/designación pueden faltar y se conserva su ausencia; no se asigna por ello aplicabilidad o criticidad QTG. Una designación sin revisión examinada es vínculo técnicamente incoherente y se rechaza.
Los criterios se conservan como documentos presentados, no como programa evaluable ni autorización demostrada por una etiqueta. Conservar su contenido no cierra G02/G03. No recibir listas libres de QualityCheck, estados de salida, resultado financiero/QTG previo o callback de cálculo.
No colapsar naturaleza sintética de calendario, captura y designación en una sola etiqueta operacional. Una marca PRESENTED_OPERATIONAL no autentica una fuente. El registro no realiza revisión, OCR, comparación semántica, resolución de conflictos o autenticación del otorgante.
La identidad de preparación depende de todo el material y sus ausencias explícitas. Exportaciones independientes; mutación posterior del input o de una exportación no cambia el material conservado.

### B. Ejecución QTG — frontera aún condicionada

La futura función ejecutora recibirá preparación construida y obtendrá controles mediante un productor determinista especializado implementado contra fuentes autorizadas, no leyendo un texto libre como política ni confiando en booleanos suministrados.
Antes de invocar evaluate_quality: inventario requerido por el uso cubierto; aplicabilidad, criticidad/materialidad y tratamiento de faltantes determinados con fuentes; soporte suficiente observado y vinculado. Conserva controles omitidos/no determinables como pendientes del productor, sin rellenar defaults de QualityCheck ni emitir un cuarto estado funcional.
Mientras falten esas condiciones no se invoca el gate. Esta imposibilidad de ejecución no se registra como NO_APTO: distingue diseño incompleto de un control crítico necesario que sí haya sido determinado y resulte no evaluable conforme al contrato.
Cuando se cierre el productor, el recibo de ejecución deberá conservar preparación completa/fingerprint, identificación/versiones del productor y contrato usados, controles íntegros producidos y resultado calculado por evaluate_quality. No aceptar QualityTrustResult desprendido ni sustituir ejecución por un recibo con estado suministrado.
No declarar fiable el input completo basándose únicamente en cobertura de las dos cuotas, revisión o designación. También deben cubrirse las condiciones financieras aplicables del perfil: disponibilidad de tesorería, semántica de fuentes, temporalidad y demás requisitos que se determinen sin inventar política.

## Reevaluación y consumo

Cambios en compra/contexto, flujos, parámetros, documentos, calendario/autoridad, revisión, designación, criterios o implementación aplicable requieren nueva preparación/ejecución; no actualizar un resultado anterior ni elegir la revisión más favorable.
La futura validación para consumo contrastará material íntegro y versión aplicable del productor/criterios, recomputará controles/resultado con el productor autorizado y rechazará cualquier discrepancia. Un fingerprint coincidente sin material/origen suficiente no demuestra fiabilidad.
El perfil financiero no acepta un resultado QTG de otro consumidor ni lo convierte en decisión de compra. El consumidor financiero mantiene sus excepciones y estados analíticos cerrados; el diseño no le añade defaults o reconstrucción de pagos.
La integración que condicione ejecución financiera al resultado QTG será una unidad posterior, con decisión explícita sobre estados permitidos y advertencias; no se habilita por cerrar la preparación.

## AUDITAR

A1: revisión ligada a captura no cubre autoridad del calendario. Conservar ambos y validar cobertura para captura/calendario.
A2: resultados separados o callback evaden observación. Prohibirlos y exigir productor especializado determinista antes de gate.
A3: documento de criterios puede contener política no aprobada. Conservarlo como material presentado; no interpretarlo ni aprobarlo automáticamente.
A4: revisión/designación ausentes no deben impedir registrar material ni fabricar éxito. Conservar None y mantener requisitos de ejecución separados.
A5: vínculos técnicos no prueban autorización/suficiencia. No promover declaraciones ni estados financieros a Evidence o QTG.
A6: checks vacíos/parciales pueden producir APTO en el gate cerrado. Completar inventario/criterios antes de invocar, sin modificar el gate.
A7: cambio de criterio/productor también afecta reutilización. Incluir contenido/versiones e invalidar consumo si difieren.

## DEPURAR

Separar cierre de preparación técnica de cierre del productor. No introducir un policy engine genérico, scoring, IAM, firma o garantías de persistencia no demostradas. No exigir datos empresariales reales para probar preparación; no atribuir garantías operativas a Mock Data.
Recomputar cobertura es contraste de una observación estructural ya autorizada, no repetición presentada como autenticación. Revisiones y designaciones se conservan como declaraciones humanas aportadas; el software no rehace su comprobación empresarial.

## AUDITAR 2

PASS de diseño: material completo y pertenencias físicas existentes; sin resultado desprendido; cambios de criterios/contexto contemplados; errores de vínculo siguen siendo técnicos; fuente de política no inventada.
PASS de fronteras: cuarentena y componentes cerrados intactos; sin salto a APTO desde éxitos locales; persistencia, identidad y mandato no declarados resueltos.
PENDIENTE: implementación/pruebas de preparación; cierre del productor G02/G03; contrato ejecutable/recibo/recomputación de ejecución y consumo. G04 completo aún no se declara resuelto: se cierra el diseño de su fundamento físico, no una ejecución inexistente.

## CERRAR → MATERIALIZAR → CI

Esta unidad materializa únicamente este diseño y auditorías. CI sobre HEAD exacto y merge requerida. Su éxito prueba regresión, no suficiencia empresarial.
Siguiente unidad: implementar preparación inmutable sin llamadas a Finance/QTG, con rechazo de cobertura ajena/no reproducible, revisión de otra captura, designación de otra revisión, criterios sólo referenciados sin contenido, exportaciones mutables y cambios de cualquier material. Usar casos sintéticos y conservar faltantes.
