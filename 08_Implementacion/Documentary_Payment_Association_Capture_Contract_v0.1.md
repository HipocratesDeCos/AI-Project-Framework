# EIOS — DOC-PAY-CAP-01 — Contrato de captura de asociación documental v0.1

Fecha: 17/09/2026.
Baseline verificado: a36b2967e8645c9f5ed597c1414fd87d78b58c8b.
Estado inicial: diseño técnico auditado; implementación no materializada por esta unidad.
Precedentes: Operation_Document_Payment_Association_Design_Audit_v0.1.md y Documentary_Payment_Synthetic_Case_Audit_v0.1.md.
Fuente seleccionada por el titular: documentación de la operación.

## DISEÑAR — alcance
La siguiente unidad es conservar una asociación documental declarada y comprobar su coherencia con el input financiero capturado. No es un productor de evidencia autenticada ni un productor QTG.
Se reutilizan FinanceDecisionInputPackage, PurchaseOperation, DecisionContext, CashFlow y Evidence existentes, sin añadir campos a esos contratos.
El caso PDF v2 suministra una operación, un pedido versionado, confirmación y dos cuotas. Permite definir la captura y los controles técnicos; no permite declarar válida una compra real.
Autoridades: FIN-AUTH-05, Evidence_Contract v1.0, FIN-DIP-01 y contratos financieros existentes.

## Material que deberá recibir la captura futura
| Entrada | Obligación de conservación |
|---|---|
| FIN-DIP-01 construido | Capturar su payload completo y fingerprint; de ahí proceden compra, contexto y flujos, sin segundo input financiero independiente |
| Material documental suministrado | Conservar bytes exactos y referencia local; digest calculado desde bytes, nunca aceptado como sustituto de ellos |
| Naturaleza del caso | Declaración explícita de material sintético o material presentado como operativo; ninguna categoría acredita autenticidad |
| Referencias documentales | Operación, pedido/versión y confirmación cuando consten; no crear una identidad global de compra |
| Asociación por cuota | Referencia local de obligación/cuota, flow_id de un PAYMENT existente y localizadores al material conservado |
| Alcance declarado | Captura de asociación de las cuotas listadas; no afirmar calendario completo ni todos los flujos de empresa |
| Revisión externa disponible | Conservar referencia aportada si existe; si no existe, None. No generar firma, fecha, responsable o revisión QTG |

Los localizadores deberán identificar documento conservado, página positiva y apartado no vacío. La primera implementación no puede afirmar que el texto de ese apartado confirma un dato sin un mecanismo de revisión demostrado.
En el ejemplo: PDF v2, páginas 2/3, Condiciones de Pago y Ratificación de Calendario. Las referencias de cuotas son PED-2026-015 / cuota 1 y / cuota 2.
Una captura con naturaleza operativa significa material presentado como tal, no evidencia empresarial validada.
La especificación no crea OCR, servicio documental, ERP, credenciales ni una infraestructura de almacenamiento.

## Controles técnicos exigidos
1. Revalidar/capturar el contenido de los tipos existentes; no confiar sólo en isinstance ni en construcciones que omitan validación.
2. Cada binding identifica exactamente un flow_id capturado de tipo PAYMENT; rechazar IDs inexistentes, COLLECTION y repetición del mismo flow_id.
3. Cada referencia local de obligación/cuota aparece una sola vez en la asociación capturada. Rechazar dos bindings con la misma cuota aunque difieran sus flow_id.
4. No exigir cobertura de todos los PAYMENT: pueden corresponder a otras operaciones. Los no asociados se conservan y no se reinterpretan.
5. Conservar importe, moneda, fecha y estado del flujo desde FIN-DIP, sin un segundo CashFlow suministrado que pueda separarse de la captura.
6. Los bytes documentales y los bindings quedan incluidos en la identidad del material. Exportaciones y lecturas futuras deben ser copias independientes.
7. El digest del documento se calcula desde sus bytes. Un cambio documental, de binding, de flujo o de contexto cambia la identidad de la captura.
8. None, estados parciales y conflictos financieros se conservan. El binding no eleva NOT_EVIDENCED a DEMONSTRATED.
9. Cuotas fuera del horizonte pueden asociarse: el motor financiero conserva autoridad sobre inclusión temporal. No borrarlas de la captura.
10. No ejecutar motores, Rules ni QTG durante captura; no aceptar un resultado financiero separado o un callable de comprobación como sustituto de las entradas.
11. No usar la suma de cuotas igual a quantity × unit_price como control universal. El ejemplo contiene impuestos documentados: base 1000 EUR y total exigible 1210 EUR.
12. Asociación vacía significa ninguna asociación suministrada; nunca ausencia demostrada de obligaciones.

La unicidad de referencias locales detecta duplicación declarada, no duplicación económica oculta bajo dos referencias distintas. Ese límite debe permanecer visible al consumidor.
No se define aquí un estado APTO, confianza, criticidad o suficiencia de uso. La captura no certifica inclusión completa de pagos de compra.

## AUDITAR — hallazgos
A1: Un hash sin bytes sólo identifica una afirmación; no permite reproducir el material. Se exige conservación de bytes.
A2: Un segundo input o resultado permitiría desligar los flujos del FIN-DIP. Se toma exclusivamente el material capturado.
A3: Igualar compra y pagos pierde los impuestos documentados del caso. Se prohíbe esa igualdad universal.
A4: flow_id único no detecta una cuota repetida bajo diferentes flow_id. Se añade unicidad de la referencia local declarada, sin afirmar solución económica universal.
A5: Una referencia de revisión autogenerada crearía falsa autoridad. Se conserva la referencia externa sólo cuando esté aportada.
A6: El PDF sintético no demuestra verificación de contenido ni operación real. La salida se presenta como captura de asociación declarada.

## DEPURAR
El contrato se limita a coherencia estructural y preservación del material suministrado.
No convierte páginas/localizadores en prueba automática de que el documento expresa la condición.
No certifica autenticidad, vigencia comercial, corrección de clasificación, totalidad del calendario ni identidad económica universal.
No reemplaza las obligaciones DOC-PAY-01: son requisitos adicionales para un productor que afirme demostración.
No cambia los estados Evidence/CashFlow ni las reglas de cálculo cerradas.

## AUDITAR 2
| Frontera | Resultado del diseño |
|---|---|
| Evidencia real frente a ejemplo sintético | PASS: naturaleza explícita y ninguna elevación automática |
| Compra/contexto/flujo conservados juntos | PASS: referencia y payload del FIN-DIP único |
| Material documental reproducible | PASS de diseño: bytes exigidos; verificación física pendiente |
| Doble cómputo | PASS acotado: unicidad declarada; duplicación económica oculta no resuelta |
| Impuestos y horizonte | PASS: no transformación económica ni calendario inferido |
| Core, Finance, Rules y QTG | PASS: ningún contrato existente redefinido |
| Productor autenticado y suficiencia QTG | PENDIENTES: no cubiertos por esta unidad |

## CERRAR
Se cierra el diseño técnico de captura de asociación declarada para su futura implementación y prueba. No se cierra esa implementación, la verificación documental real o QTG.
Antes de materializar código deben fijarse los tipos/serialización concretos conforme a estas obligaciones y ejecutar las pruebas de aceptación.

## MATERIALIZAR / CI
Esta unidad materializa únicamente el presente contrato y registro de auditorías.
CI documental sobre HEAD exacto requerida antes de integrar; no valida una implementación aún inexistente.
Aceptación futura: caso PDF v2; bindings inexistentes/COLLECTION/duplicados; cuota repetida con distintos flow_id; None/conflictos; bytes modificados y mutación de entradas/exportaciones; cuotas fuera del horizonte; ausencia de ejecución de motores/gate.
Continuidad: implementar captura declarada conforme a este alcance; después, resolver la comprobación documental y determinaciones QTG que sigan pendientes.
