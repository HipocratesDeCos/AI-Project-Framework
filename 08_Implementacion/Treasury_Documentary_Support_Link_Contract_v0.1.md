# EIOS — FIN-TREASURY-SUPPORT-01 — Soporte de tesorería presentada v0.1

Fecha: 18/09/2026. Baseline remoto: 720a7c6cb1c5d5e83030f1213accf4e07b353558; CI #865 SUCCESS.
Estado: diseño complementario auditado; implementación, suficiencia operativa y QTG pendientes.

## DISEÑAR

Uso: conservar soporte presentado de tesorería para el piloto al corte documental aprobado por FIN-PILOT-CUT-01. Fuentes: FIN-AUTH-02 y QTG-FIN-G04-01. No modificar FinancialSnapshot, FinanceQualityPreparation o motores cerrados.
Registro complementario ligado a FinanceQualityPreparation exacta. No reemplaza una referencia treasury_evidence_ref por autenticación ni corrige el saldo para cuadrar documentación.

| Material | Obligación de conservación |
|---|---|
| Preparación examinada | Payload íntegro y fingerprint calculado; deriva empresa, moneda, as_of_date y available_treasury del snapshot capturado |
| Identidad local | Referencia de registro no vacía; no identidad global de cuenta/empresa |
| Documentos presentados | Referencias únicas, bytes íntegros y hash calculado; naturaleza explícita SYNTHETIC o PRESENTED_OPERATIONAL del soporte |
| Declaración documental | Empresa/referencia documental aportada, moneda, fecha económica representada e importe disponible declarado; valores desconocidos conservados como None |
| Correspondencia empresarial | company_scope objetivo explícito igual al capturado; identidad documental separada y correspondencia declarada, sin resolver por similitud de nombre |
| Soporte de declaración | Localizadores en documentos conservados, página positiva y sección no vacía; localizador no prueba que exista ese contenido |
| Observaciones | Condición, nota, resultado declarado individual y localizadores; persona/fecha de comprobación sólo si se aportan, no generarlos desde fecha de ejecución |

La declaración es una magnitud disponible presentada, no un motor de conciliación ni una suma de cuentas deducidas. No exigir que un extracto incluya cuentas de toda la empresa; si se pretende completitud agregada debe aportarse soporte y criterio. No realizar conversiones FX, compensaciones, interpolación temporal o reconstrucción contable.
Si se aportan persona y momento de comprobación, deben conservarse juntos, con referencia explícita y fecha/hora con zona; no atribuir emisión real o autorización por llenar esos campos. DOC-PAY-ROLE-01 autoriza revisión documental de pagos en su alcance; no extenderlo por inferencia a certificación de tesorería.

## Observación técnica y declaración humana

Inventario declarativo: SOURCE_CORRESPONDENCE, ECONOMIC_CUTOFF, AMOUNT_SUPPORT, AVAILABILITY, RESTRICTIONS, SOURCE_SUFFICIENCY. Resultados locales: DECLARED_CONSISTENT, DECLARED_INCONSISTENT, NOT_ESTABLISHED; omitidos pendientes, sin booleano global.
Declaración consistente exige nota y localizador de soporte. Se rechazan condiciones repetidas, localizadores ajenos, modelos inválidos/copias con bypass y referencias vacías. No se revisa semánticamente el contenido ni se autentica la fuente.
La observación técnica compara importe declarado frente a available_treasury cuando ambos existan, moneda y fecha económica frente a snapshot. Discrepancias se conservan, no se rechaza material sólo por saldo/fecha distintos ni se sobrescribe snapshot. company_scope objetivo ajeno sí es un error técnico de vínculo.
Si falta alguno de los importes, su comparación queda no determinable; None nunca se convierte en cero. Cero explícito es válido. Una coincidencia exacta sigue siendo únicamente concordancia entre valores suministrados.
La fecha de emisión/descarga no sustituye fecha económica desconocida. No aplicar antigüedad máxima, tolerancia de fechas o zona de corte inventadas.

## Disponibilidad y restricciones

Conservar las observaciones de saldos restringidos/no utilizables y exclusiones FIN-AUTH-02: crédito no dispuesto, financiación hipotética, cobros futuros no realizados y activos no monetarios. Su ausencia en una declaración no demuestra que se investigó su inexistencia.
No convertir AMOUNT_SUPPORT consistente en AVAILABILITY o SOURCE_SUFFICIENCY satisfechas. Un saldo contable coincidente no demuestra dinero utilizable. Las observaciones humanas positivas no eliminan discrepancias técnicas, conflictos documentales o requisitos omitidos.
No emitir autorización de saldo, DEMONSTRATED, APTO, confianza o permiso de ejecución. No llamar Finance/QTG ni aceptar resultado previo, lista libre de QualityCheck o callback.
La preparación, los documentos y las declaraciones se conservan inmutables con exportaciones independientes. Cambiar preparación, documento, fecha/importe declarado u observación cambia identidad; validar pertenencia a preparación completa, no a un hash suelto.
La naturaleza de soporte y preparación se mantiene separada; cualquier material sintético permanece visible. PRESENTED_OPERATIONAL no es autenticación. Conservación técnica no demuestra persistencia empresarial.

## AUDITAR

A1: saldo coincidente no acredita disponibilidad. Separar comparación numérica, restricciones y suficiencia.
A2: fecha de extracción no representa automáticamente el corte económico. Conservar fecha económica explícita o desconocida.
A3: modificar preparación cerrada introduciría ciclo de identidad. Usar registro complementario y pertenencia exacta.
A4: mandato para revisar cuotas no autoriza certificar tesorería. Conservar comprobación aportada sin fabricar autorización o extender rol.
A5: valores discrepantes son información, no motivo para corregir input. Conservar ambos; errores de vínculo/modelo se distinguen de hallazgos.
A6: ausencia de restricciones o colección de controles vacía no demuestra suficiencia. Derivar pendientes del inventario y conservar incertidumbre.

## DEPURAR

No introducir conciliador bancario, catálogo contable universal, fuente obligatoria de ERP, firma/IAM o política nueva de criticidad. El registro habilita conservación/pruebas del soporte, no validación positiva del saldo empresarial. Se puede implementar con Mock Data sin solicitar documentos reales.

## AUDITAR 2

PASS de diseño: preparación exacta, bytes íntegros, declaración separada de observación, comparación técnica limitada, cero/None preservados y contradicciones conservadas.
PASS de fronteras: alcance temporal aprobado respetado; modelos cerrados intactos; rol no ampliado; sin QTG, autenticación o transformaciones inventadas.
PENDIENTE: implementación y pruebas del registro; criterios/productor de suficiencia operativa, autorización aplicable a comprobaciones de tesorería cuando se pretendan usar como autorizadas, G02/G03 y ejecución/consumo G04.

## CERRAR → MATERIALIZAR → CI

Cierre únicamente del diseño complementario. Esta unidad añade el presente contrato/auditorías; CI requerida sobre HEAD exacto y merge. No certifica saldo ni piloto real.
Siguiente unidad: implementar registro inmutable y pruebas de empresa objetivo ajena, discrepancias de fecha/moneda/importe, corte desconocido, cero/None, fuente/localizadores ajenos, duplicados/bypass, observaciones incompletas/positivas con discrepancia técnica, mutación/exportaciones, preparación modificada y ausencia de llamadas a Finance/QTG.
