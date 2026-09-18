# EIOS — FIN-TREASURY-CONTEXT-01 — Vínculo de valoración contextual

Fecha: 18/09/2026. Baseline remoto: `b6897f5add62cc77b1c85a82f3d14372e001008b`; CI #872 SUCCESS.
Estado: diseño técnico auditado del registro de valoraciones presentadas; no ejecuta QTG ni acredita suficiencia.

## DISEÑAR — fundamento y alcance

Fuentes: FIN-PILOT-TREASURY-SUFF-01 (cinco criterios explícitamente aprobados), FIN-PILOT-CUT-01, FIN-AUTH-02/05, QTG v0.4, QTG-FIN-G04-01 y FIN-TREASURY-SUPPORT-01.
Unidad complementaria para conservar cómo una valoración presentada relaciona una condición de tesorería con el uso de proyección determinada al corte documental. Reutiliza FinanceQualityPreparation y TreasuryDocumentarySupport; no crea un motor de políticas, un verificador empresarial, un esquema SQL o un segundo sistema de Evidence.
El registro no convierte declaraciones de suficiencia en comprobación autorizada. Se limita a pertenencia técnica y conservación de justificaciones y soportes presentados.

### Material y vínculos

| Elemento | Obligación técnica |
|---|---|
| Preparación construida | Conservar payload completo y fingerprint calculado |
| Complemento de tesorería construido | Validar con validate_treasury_support_for_preparation; conservar payload/fingerprint completos, incluidas naturaleza, comparaciones, observaciones y documentos |
| Referencia de valoración | No vacía, sin espacios periféricos; no constituye identidad empresarial |
| Persona y momento aportados | Ambos o ninguno; si existen, referencia no vacía y datetime con zona. No generarlos ni inferir mandato |
| Valoraciones individuales | Condición perteneciente al inventario de seis del complemento, referencia/version de criterio conservado en preparación, justificaciones y enlaces a material presentado |
| Material adicional citado | Documentos explícitos con referencia única, bytes íntegros y hash calculado; naturaleza SYNTHETIC o PRESENTED_OPERATIONAL declarada separadamente. Una etiqueta no prueba autenticidad |

No aceptar solamente hashes, listas de QualityCheck, resultados QTG/financieros previos, callback o campos critical/material/satisfied suministrados para alimentar el gate. Los criterios referenciados deben existir por pareja reference/version en presented_criteria; no aceptar texto libre como nueva política ejecutable.
No asumir que cualquier criterio conservado fue aprobado: la aprobación de FIN-PILOT-TREASURY-SUFF-01 no aprueba por arrastre el resto del material.

### Valoración individual presentada

Cada condición admite como máximo una entrada, con los siguientes campos semánticos:

- condition: uno de SOURCE_CORRESPONDENCE, ECONOMIC_CUTOFF, AMOUNT_SUPPORT, AVAILABILITY, RESTRICTIONS, SOURCE_SUFFICIENCY.
- criterion_reference y criterion_version: pareja presente en preparación.
- applicability: declaración APPLIES, DOES_NOT_APPLY o NOT_DETERMINED, con applicability_reason no vacío.
- necessity: declaración NECESSARY_FOR_DETERMINED_PROJECTION, RELEVANT_NOT_NECESSARY o NOT_DETERMINED, con necessity_reason no vacío. Si applicability no es APPLIES, necessity debe ser NOT_DETERMINED; no inventar necesidad de una condición declarada no aplicable.
- impact_reason: explicación no vacía, preserva dudas; no score ni umbral monetario.
- support_assessment: declaración DECLARED_SUFFICIENT, DECLARED_INSUFFICIENT o NOT_ESTABLISHED, con support_reason no vacío.
- observation_conditions: condiciones observadas realmente presentes en el complemento, sin duplicados; conserva enlace a observaciones originales sin modificar outcomes/notas.
- support_locators: localizadores tipados de documentos conservados, identificando origen TREASURY_SUPPORT o ADDITIONAL_ASSESSMENT_MATERIAL, referencia, página positiva y sección no vacía. No citar documentos de otro registro ni colisionar referencias adicionales con documentos del complemento.

DECLARED_SUFFICIENT requiere al menos un localizador; no obliga a una declaración positiva previa ni borra discrepancias. El locator prueba únicamente pertenencia, no que la página contenga lo afirmado. Una valoración puede discrepar de una observación; se conservan ambas sin reconciliación automática.
No se exige una entrada completa para registrar material: las condiciones omitidas se conservan como pendientes. Una entrada NOT_DETERMINED/NOT_ESTABLISHED queda explícita y no se confunde con omisión, FALSE o éxito.
Las categorías son estados de declaraciones locales, no estados funcionales QTG ni evaluación económica del software. El registro debe exponer assurance_scope BOUND_PRESENTED_CONTEXTUAL_DECLARATIONS_ONLY.

### Identidad, cambios y consumo

Registro inmutable, material canónico íntegro, fingerprint calculado y exportaciones independientes. Cambiar preparación, criterio, complemento, documentos, naturaleza, referencia, persona/momento o cualquier justificación/valoración produce identidad distinta.
Validador de pertenencia exige payload y fingerprint completos tanto de preparación como del complemento exactos. No reutilizar por igualdad de company_scope, fecha o importe; no actualizar una valoración anterior para conservar su identidad ni escoger la más favorable.
La implementación futura reconstruirá modelos tipados al entrar para rechazar model_copy/model_construct inválidos; duplicados, referencias vacías, vínculos ajenos y pares incompletos siguen siendo errores técnicos, no NO_APTO.

## AUDITAR

A1: introducir booleans de calidad suministrados reproduciría checks libres. Se conservan declaraciones contextuales y justificaciones sin conversión a QualityCheck.
A2: suficiencia declarada con locator no es observación autenticada. Alcance explícito, sin promoción a DEMONSTRATED, disponibilidad o autorización.
A3: criterio presente no equivale a aprobado; conservar pareja y contenido existente sin ejecutar política ni aprobarla por etiqueta.
A4: valoración positiva podría ocultar comparación negativa o restricciones. Preservar complemento completo y desacuerdos sin prioridad arbitraria.
A5: persona/fecha no demuestran competencia; mandato de pagos no se extiende a tesorería. Material adicional puede conservar soporte presentado, no validar facultades.
A6: parcialidad puede fabricar APTO en el gate cerrado. No invocarlo desde este registro; omisiones y determinaciones pendientes visibles.
A7: vínculos sólo a la preparación permitirían reciclar valoración tras cambiar restricciones. Validar también complemento exacto completo.

## DEPURAR

Se reduce el alcance a seis condiciones de tesorería y a declaraciones contextualizadas. No imponer criticidad universal, temporalidad de saldo actual, FX, saldo reconstruido, credenciales o infraestructura inexistentes. No expandir este registro a pagos, fondo de maniobra o datos opcionales sin diseño especializado.
Separar completitud del registro de suficiencia de contenido: seis entradas positivas no habilitan ejecución. Fuentes sintéticas siguen limitadas a pruebas; distintas marcas de naturaleza no se colapsan.

## AUDITAR 2

PASS de diseño: relaciones concretas con material físico existente, justificaciones ligadas a criterios/observaciones/documentos, ausencia explícita, identidad por contenido y rechazo de reutilización ajena.
PASS de fronteras: sin cambios a preparación, snapshot, motores, QualityCheck, gate o cuarentenas; sin atribución de autoridad real ni nueva política financiera.
PENDIENTE: implementación/pruebas de conservación y validación; procedimiento suficiente de observación/admisibilidad empresarial; inventario integral G02/G03 y productor/recibo/consumo G04. No se declara resuelto ninguno por seis valoraciones presentadas.

## CERRAR → MATERIALIZAR → CI

Se cierra sólo el diseño del vínculo de valoraciones presentadas. Materialización: este contrato con auditorías. CI del HEAD exacto y post-merge requerida; no acredita suficiencia ni ejecuta valoraciones.
Siguiente unidad: implementar registro y validadores, con pruebas sintéticas de cambio de criterio/complemento, referencias ajenas, declaraciones positivas ante discrepancias, parcialidad, documentos adicionales, errores de modelos copiados y aislamiento de Finance/QTG. No requiere documentos operativos reales para probar el contrato.
