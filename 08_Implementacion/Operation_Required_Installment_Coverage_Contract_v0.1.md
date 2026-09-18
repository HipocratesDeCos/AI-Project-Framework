# EIOS — DOC-PAY-COVER-01 — Cobertura requerida de cuotas v0.1

Fecha: 18/09/2026. Baseline remoto verificado: 4f2f161a5d6752186d2773b930dc511e1997a61a, CI #853 SUCCESS.
Fuente de autoridad de alcance: definición explícita del titular para COMPRA-2026-001, PED-2026-015 y CONF-015.
Estado: diseño acotado auditado; comprobador ejecutable pendiente. Material sintético, sin autorización QTG positiva.

## DISEÑAR

Se fija el calendario requerido de este caso de prueba. No se crea una política general de fraccionamiento, IVA, anticipo o liquidación para otras compras.

| Identidad local de cuota | Importe exigible | Moneda | Vencimiento | Soporte declarado | Naturaleza |
|---|---|---|---|---|---|
| PED-2026-015 / cuota 1 | 605.00 | EUR | 2026-09-30 | PDF pág. 2 Condiciones de Pago y pág. 3 Ratificación de Calendario | Obligación futura pendiente; anticipo 50% |
| PED-2026-015 / cuota 2 | 605.00 | EUR | 2026-10-30 | Mismos soportes | Obligación futura pendiente; liquidación 50% |

Total requerido: 1210.00 EUR; base documental 1000.00 + IVA documental 210.00. No calcular ni inferir pagos desde quantity × unit_price. La identidad local coincide con el fixture sintético existente.
Las referencias COMPRA-2026-001, PED-2026-015, versión 1 y CONF-015 delimitan el caso. Una captura con referencias distintas no satisface este calendario por tener importes iguales.

## Cobertura frente a proyección

Interpretación completa del calendario declarado exige ambas cuotas, cada una vinculada a un único flujo PAYMENT, con importe, moneda y vencimiento exactos. Cuota omitida impide declarar cobertura completa, aunque la otra cuota sea correcta o la suma de flujos coincida accidentalmente con el total.
El calendario completo debe conservarse independientemente del horizonte. Finance Basic puede proyectar solo la primera cuota en 30 días y ambas en 60 conforme a sus fechas; no se modifica su filtrado cerrado. Que una cuota quede fuera del horizonte no equivale a que no exista o a que la captura del calendario pueda omitirla.
Esta completitud concierne al calendario declarado de esta operación sintética, no a todos los pagos de la empresa ni a obligaciones desconocidas.

## Deduplicación y matching

Pedido y confirmación son dos soportes de las mismas dos obligaciones, no cuatro obligaciones. Cada binding de cuota conserva ambos soportes/localizadores disponibles y un único flow_id; no ejecutar creación de flujos por cada página o documento.
El futuro comprobador recibe captura documental construida y calendario requerido explícito; examina bindings y flujos ya conservados. No realiza ingesta PDF, no fusiona silenciosamente registros duplicados, no inventa cuotas ni corrige importe/moneda/fecha.
Matching requiere referencias de operación/pedido/confirmación y versión del caso, identidad de cuota, flujo PAYMENT asociado, importe Decimal exacto, moneda EUR exacta y vencimiento exacto. Dos cuotas de 605 EUR no son intercambiables: monto/moneda solos no identifican la obligación.
flow_id identifica un registro financiero, no acredita por sí mismo identidad económica universal. Un registro adicional con otro ID que represente la misma obligación no se admite como una tercera cuota de este calendario. Si no se puede determinar qué representa un flujo adicional, no se presume que pertenece a esta compra ni que es inocuo: se conserva como limitación a examinar, sin afirmar deduplicación económica universal.
Los rechazos por duplicidad estructural de DOC-PAY-CAP-01 permanecen intactos. La cobertura complementaria no convierte excepciones técnicas en NO_APTO.

## Secuencia y estados

La secuencia declarada queda satisfecha por vencimientos: 2026-09-30 precede a 2026-10-30. No exigir que el orden físico de tupla sea cronológico si la identidad y fechas son correctas; no usar posición para suplir una identidad ausente.
No hay soporte de ejecución: no inferir transacciones bancarias, pago realizado, anticipación efectiva ni orden real de ejecución. La alternativa de precedencia por ejecución no se evalúa con estas obligaciones futuras.
Los estados originales de CashFlow y hallazgos humanos se conservan. Una coincidencia estructural no eleva NOT_EVIDENCED a DEMONSTRATED y no autentica el documento o al revisor.

## Vínculo complementario y consumo

El futuro registro conserva calendario declarado completo, fuente/autoridad de esa declaración, naturaleza sintética, captura documental completa y fingerprint calculado, así como observaciones individuales de cuotas presentes/ausentes, discrepancias y asociaciones no determinables.
El resultado describe únicamente cobertura del calendario declarado y correspondencia estructural observada. No introduce un cuarto estado QTG, no emite autorización de pago, no revisa contenidos ni sustituye DOC-PAY-REVIEW-01.
Si cambia cualquier cuota requerida, referencia, flujo, binding, documento o contexto, el material examinado cambia y no se reutiliza la comprobación anterior como comprobación del nuevo conjunto. No aceptar resultado desprendido, hash suministrado o callback opaco.

## AUDITAR

A1: igualdad de importe/moneda es ambigua entre estas cuotas. Incorporar identidad de cuota y vencimiento exacto al matching.
A2: sumar 1210 EUR no basta; una cuota duplicada puede ocultar la ausente. Exigir conjunto de identidades requerido y relación uno a uno con PAYMENT.
A3: dos fuentes no son dos obligaciones adicionales. Conservar corroboración sin multiplicar flujos; no declarar implementada una ingesta inexistente.
A4: horizonte no define completitud del calendario. Conservar las dos cuotas sin modificar proyección financiera.
A5: pendiente de pago no demuestra ejecución. Comprobar la precedencia disponible por vencimiento, no inventar fecha de pago.
A6: declaración del titular precisa necesidad del caso, pero no demuestra autorización humana ni suficiencia documental operativa. Mantener SYNTHETIC y los límites QTG.

## DEPURAR

Se incorporan estas precisiones sin reabrir contratos/código cerrados. No exigir orden de almacenamiento, conversión FX, umbral monetario ni heurística de prioridad entre documentos. El total procede del caso documentado, no de una nueva regla fiscal o de inferencia del precio de compra.
El requisito de cobertura de las dos cuotas resuelve la necesidad declarada de este caso; no resuelve identificación económica de todos los flujos adicionales ni verificación real de condiciones de pago.

## AUDITAR 2

PASS de diseño: calendario finito, criterio de cobertura exacto y deduplicación de soportes definidos; matching desambiguado por identidad/fecha; estados y proyección financiera intactos.
PASS de fronteras: futuro no convertido en pago ejecutado; datos sintéticos no promovidos a acreditación; sin integración positiva QTG ni autenticación ficticia.
PENDIENTE: implementación y CI del comprobador complementario; observación suficiente G03 y binding del resultado QTG G04; otros controles necesarios del perfil Finance Basic.

## CERRAR → MATERIALIZAR → CI

Se cierra el diseño de cobertura requerida para este caso sintético. Esta unidad materializa únicamente el contrato y auditorías. CI requerida sobre HEAD exacto antes y después de integrar; su éxito no certifica pagos ni fuentes empresariales.
Siguiente unidad: implementar y probar comprobación complementaria del calendario recibido, manteniendo los registros cerrados. Casos mínimos: ambas cuotas, cuota ausente, total coincidente con identidad incorrecta, importe/moneda/fecha distintos, referencias ajenas, dos soportes/una obligación, orden físico invertido, cambio de calendario/captura, datos no evidenciados y ausencia de llamadas al motor/QTG.
