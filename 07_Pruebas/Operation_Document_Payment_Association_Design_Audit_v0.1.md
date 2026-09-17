# EIOS — DOC-PAY-01 — Asociación documental compra/pagos v0.1

Fecha: 17/09/2026.
Baseline inspeccionado: d16d4020f08f12efb0e37fa77646698f129be1ce.
Estado: requisitos de diseño auditados; productor y contrato técnico ejecutable pendientes.

## DISEÑAR
Fuente seleccionada por el titular del proyecto: documentación de la operación.
La selección de fuente habilita este diseño; no declara demostrado ningún documento o pago.
Uso: aportar evidencia de la relación entre PurchaseOperation capturada en FIN-DIP-01 y los CashFlow PAYMENT suministrados a Finance Basic.
Autoridad: Finance_Basic_Authority_v0.1.md, FIN-AUTH-05; Evidence_Contract.md; Finance_DIP_Capture_Contract_v0.1.md; modelos físicos core y finance.
No se modifica C0, Evidence, Finance Basic, Rules ni QTG.

## Obligaciones de la evidencia
| Obligación | Comprobación exigida antes de afirmar el vínculo |
|---|---|
| Identidad de operación | Correspondencia documental comprobable con la compra y el contexto capturados; coincidencia de importe o proveedor aislada no basta |
| Documento recuperable | Identificación estable, versión o material conservado y localización del contenido pertinente; una ruta mutable no garantiza reproducibilidad |
| Condición de pago | Importe exigible, moneda y vencimiento/calendario efectivamente sustentados; distinguir condiciones propuestas de condiciones confirmadas |
| Relación con el flujo | Correspondencia explícita con cada PAYMENT suministrado, conservando su identidad y contenido completo |
| Cuotas y alcance | Identificar pagos parciales y el alcance demostrado; no declarar calendario completo a partir de una cuota |
| Correcciones y conflictos | Conservar modificaciones, sustituciones y contradicciones documentales; no escoger una versión favorable silenciosamente |
| Ausencia | Documento ausente o condición no sustentada conserva el gap; no implica importe cero, pago inmediato o inexistencia de pagos |
| No duplicación | Justificar que una misma obligación/cuota no aparece repetida en distintos flujos; flow_id único sólo prueba unicidad técnica de registros |
| Revisión | Conservar referencia a la comprobación que sustenta la afirmación; no fabricar responsable, fecha, firma o aprobación |

Estos son requisitos de aceptación, no nuevos campos canónicos ni un esquema de facturación.
La forma concreta de identificar obligaciones/cuotas y la correspondencia documental deberán justificarse con un caso representativo antes de cerrar la API del productor.
Un pedido, oferta, contrato o factura sólo sustenta las condiciones efectivamente acreditadas por su contenido y estado; el nombre del documento no acredita confirmación.
Una referencia, hash o estado DEMONSTRATED declarado no verifica por sí mismo autenticidad, vigencia, asociación ni completitud.
No se exige aquí un repositorio documental, OCR, ERP, servicio de firma o API nuevos.

## AUDITAR
A1: CashFlow dispone de flow_id y source_ref, pero no de un vínculo físico con PurchaseOperation.
A2: Evidence transporta referencias y estado, sin verificar por sí misma el contenido externo.
A3: FIN-DIP-01 captura el input completo suministrado, sin acreditar inclusión de pagos de la compra.
A4: Finance Basic computa los flujos recibidos; no genera calendarios ni descuenta la compra por segunda vez.
A5: no existe en el material aportado una operación documental representativa para comprobar correspondencia, revisiones y cuotas.
Resultado: fuente seleccionada y obligaciones definibles; implementación de un productor que afirme demostración todavía no justificable.

## DEPURAR
Se separa selección de fuente de evidencia concreta.
Se separa unicidad de flow_id de unicidad de obligación económica.
No se deduce pago de quantity × unit_price, operation_date, plazo supuesto, TCO o igualdad de importes.
No se obliga a que todos los pagos documentales estén dentro del horizonte: su inclusión/exclusión temporal sigue el contrato financiero existente.
No se traduce gap, conflicto o revisión a criticidad, confianza o estado QTG.
No se identifica confirmación de obligación futura con ejecución bancaria del pago.

## AUDITAR 2
Contraste con FIN-AUTH-05, modelos físicos y captura:
- PASS: no segunda resta ni producción de pagos desde la compra.
- PASS: None, estados financieros y documentos insuficientes no se sustituyen.
- PASS: la documentación no crea IDs globales ni altera modelos cerrados.
- PASS: no se declara completitud empresarial ni autenticidad por referencias.
- PENDIENTE: demostrar el vínculo sobre material documental concreto.
Resultado: requisitos de diseño superados en este alcance; contrato ejecutable y productor no cerrados.

## CERRAR
Se cierra únicamente la definición de obligaciones de evidencia para la fuente seleccionada.
No se cierra la asociación demostrada de una operación, G03 completo, G04 ni QTG.
La siguiente entrada necesaria es un ejemplo documental de operación, que puede estar anonimizado, conservando condiciones de pago y correspondencia con la compra.

## MATERIALIZAR / CI
Materialización de esta unidad: un documento de requisitos; sin cambio ejecutable.
La CI deberá comprobar este delta documental sobre su HEAD exacto. Su éxito no acredita un documento empresarial ni resuelve los pendientes anteriores.
