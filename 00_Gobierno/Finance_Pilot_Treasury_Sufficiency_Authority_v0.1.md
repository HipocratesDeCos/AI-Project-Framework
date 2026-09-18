# EIOS — FIN-PILOT-TREASURY-SUFF-01 — Base de suficiencia de tesorería

Fecha: 18/09/2026. Baseline remoto: `0a75ec1d1f0f2ef34448d63ae7a42465d8ee5b7a`; CI #869 SUCCESS.
Autoridad: aceptación explícita del titular del proyecto de la propuesta de cinco criterios para la proyección de tesorería del piloto al corte documental.
Estado: base metodológica aprobada y auditada; no habilita el productor QTG.

## DISEÑAR — alcance y precedencia

Uso: preparar entradas para `run_provenanced_finance_basic`, en el piloto al corte `snapshot.as_of_date`. La base se refiere a presentar una proyección determinada de tesorería, no a disponibilidad actual, decisión de compra o ejecución de pagos.
Fuentes: FIN-AUTH-02/05, FIN-PILOT-CUT-01, contrato QTG v0.4 §§5/7/8/9, perfil QTG-DIP-G01-FIN, matriz QTG-FIN-G02-BASE-01 y contrato FIN-TREASURY-SUPPORT-01 implementado mediante PR #179.
No sustituye semántica analítica, admisibilidad general de Evidence ni los criterios de los demás dominios.

## Base aprobada

| Aspecto | Criterio | Consumo y límite |
|---|---|---|
| Tesorería inicial | Necesaria para presentar una proyección determinada; desconocida no equivale a cero | Conservar None y estados del motor. Un saldo cero puede ser válido si dispone de soporte suficiente |
| Soporte suficiente | Debe acreditar empresa, moneda, fecha económica, importe utilizable y restricciones | Coincidencia de campos, referencia, hash, locator o declaración positiva no acredita por sí sola esa suficiencia |
| Deficiencia bloqueante | Falta o contradicción no resuelta que impida acreditar esa tesorería inicial | NO_APTO / BAJA para este uso, según QTG §9; conservar ausencia como no evaluable, no como FALSE |
| Revisión humana | Si se utiliza como comprobación autorizada, exige mandato explícito para tesorería | La autoridad para revisar pagos no se extiende automáticamente; persona/fecha declaradas tampoco prueban mandato |
| Datos opcionales | Su ausencia no bloquea automáticamente toda la evaluación | Determinar magnitud afectada y relevancia; no asignar por defecto inaplicabilidad, criticidad o materialidad |

La criticidad se justifica por la afectación concreta a la tesorería inicial necesaria, no por el nombre de cualquiera de las seis condiciones del registro. Una incidencia documental sin ese impacto no se recodifica universalmente como crítica.
La combinación NO_APTO / BAJA deriva del contrato cerrado; esta base no produce un resultado empresarial ni un nuevo estado QTG. Si el criterio o la observación de aplicabilidad/impacto aún no se puede determinar, permanece pendiente el productor, sin inventar un control ni un cuarto estado.

## Suficiencia y restricciones

FIN-AUTH-02 mantiene fuera de tesorería disponible los saldos restringidos/no utilizables, crédito no dispuesto, financiación hipotética, cobros futuros y activos no monetarios. Una omisión de restricciones no demuestra su inexistencia. No se prescribe un banco, catálogo de cuentas, procedimiento de conciliación, número universal de documentos o fórmula de agregación.
La fuente debe soportar el corte económico declarado; su fecha de descarga/emisión no lo sustituye. No se aprueba interpolación, normalización FX, reconstrucción de saldo ni actualización automática. Una revisión posterior puede examinar ese corte, sin certificar disponibilidad actual.
La naturaleza SYNTHETIC conserva el uso exclusivo de pruebas. PRESENTED_OPERATIONAL expresa naturaleza presentada, no autenticidad, integridad empresarial, autorización o suficiencia demostrada.

## AUDITAR

A1: tesorería inicial necesaria para esta proyección no implica bloqueo universal de todas las magnitudes Finance Basic. Delimitar consumidor y pretensión.
A2: soporte presentado y tres comparaciones técnicas no prueban las cinco propiedades económicas requeridas. Conservar G03 abierto.
A3: restricciones omitidas y observaciones positivas no justifican disponibilidad; no promover a DEMONSTRATED ni modificar CashFlow.
A4: mandato de pagos no acredita competencia para tesorería. La aprobación de metodología no designa a una persona ni crea un mandato operativo.
A5: optional no equivale a irrelevante; advertencias y MEDIA/BAJA siguen necesitando determinaciones contextuales. No inventar umbral monetario.
A6: un fallo de construcción/binding sigue siendo error técnico, no NO_APTO.

## DEPURAR

Se conservan las cinco determinaciones aprobadas, con aplicación contextual y separación de metodología, material presentado y comprobación suficiente. No fijar critical=True por identidad del control ni critical=False ante incertidumbre. No convertir falta de acreditación en cero o incumplimiento económico demostrado.

## AUDITAR 2

PASS documental: precedencia QTG respetada; NO_APTO/BAJA limitado a la deficiencia necesaria indicada; ausencia preservada; fuente/corte y restricciones separados de coincidencia; mandato condicionado al uso de revisión autorizada; datos opcionales sin tratamiento global por defecto.
PASS de fronteras: ningún componente cerrado modificado, sin ejecución Finance/QTG, sin levantamiento de cuarentenas ni acreditación operativa desde Mock Data.

## CERRAR → MATERIALIZAR → CI

Se cierra exclusivamente la base autorizada de suficiencia de tesorería, no G02/G03/G04 integrales. Materialización: este documento y sus auditorías. Verificar CI del HEAD documental exacto y post-merge antes de comunicar integración; los identificadores reales quedan en el registro PR/Actions.

## Siguiente unidad legítima

Diseñar el registro de evaluación contextual que vincule preparación y complemento de tesorería exactos, criterios utilizados y observaciones que justifiquen aplicabilidad, necesidad/impacto y suficiencia. Reutilizar material físico sin aceptar checks libres, resultado QTG previo o callback opaco. Toda determinación sigue distinguida de una declaración y requiere soporte admisible; el diseño no debe fabricar un verificador ni autorización. No se implementará consumo positivo hasta cubrir inventario requerido y observaciones suficientes.
