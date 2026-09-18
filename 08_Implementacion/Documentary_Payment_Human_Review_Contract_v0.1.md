# EIOS — DOC-PAY-REVIEW-01 — Revisión humana del contenido documental v0.1

Fecha: 18/09/2026.
Baseline remoto verificado: 14e369d8bb221c62fbfae1cdfbc6d0a243032afc.
Decisión del titular: revisión humana confirmada como mecanismo inicial de comprobación documental.
Estado: diseño y obligaciones auditados; registro ejecutable y revisiones de operaciones pendientes.

## DISEÑAR
Uso acotado: registrar qué ha comprobado una persona sobre el contenido conservado por DocumentaryPaymentCapture.
No autentica proveedor, documento o identidad de revisor, no ejecuta pagos ni produce un estado QTG.
Se conserva DOC-PAY-CAP-01 sin modificar sus campos ni su constructor. La revisión es un registro complementario vinculado a la captura exacta.
Autoridades: Evidence_Contract v1.0, FIN-AUTH-05, DOC-PAY-01 y DOC-PAY-CAP-01; la presente decisión habilita el mecanismo humano, no una nueva política empresarial.

## Registro mínimo para la futura implementación
| Elemento | Obligación |
|---|---|
| Identidad de revisión | Referencia local no vacía; no identidad global EIOS |
| Captura examinada | Payload completo de DocumentaryPaymentCapture e identidad calculada desde el material, no un hash suelto suministrado |
| Persona revisora | Referencia explícita a la persona que realizó la comprobación; no fabricarla ni inferirla de un usuario genérico |
| Momento | Fecha/hora aportada de revisión con zona horaria; no asignar silenciosamente la fecha de ejecución del software |
| Alcance | Hallazgos individuales sobre compra/documentos y cuotas asociadas; la cobertura se inventaría desde la captura |
| Soporte por hallazgo | Documentos/localizadores conservados y nota que explica comparación o imposibilidad de comprobar |
| Resultado por condición | CONFIRMED_BY_REVIEW, NOT_CONFIRMED o CONFLICT_REPORTED; vocabulario local de revisión, no Evidence ni QualityCheck |
| Revisiones anteriores | Referencia opcional a registro previo; no sobrescribirlo ni asumir automáticamente que queda invalidado |

La identidad/nombre declarados en el registro no prueban que la persona lo emitió ni que estaba autorizada. La identificación y designación empresarial del revisor quedan como obligación operativa externa; no se inventa un directorio, autenticación o firma.
La captura sintética mantiene SYNTHETIC al añadir revisión. Confirmar una condición del ejemplo no la convierte en hecho empresarial real.
La referencia external_review_ref de DOC-PAY-CAP-01 no sustituye este registro ni prueba que exista una revisión. No se exige editar la captura cerrada para agregar una referencia que cambiaría su fingerprint.

## Inventario de comprobaciones
| Alcance | Condición a examinar |
|---|---|
| Operación | Correspondencia documental con la compra/contexto capturados: partes, artículo/cantidad y referencias; un importe coincidente no basta |
| Documentos | Correspondencia pedido/versión/confirmación y condiciones efectivamente acordadas frente a propuestas |
| Cada binding de cuota | Identidad de obligación/cuota y asociación con la operación documentada |
| Cada binding de cuota | Importe exigible del PAYMENT comparado con el documento |
| Cada binding de cuota | Moneda del PAYMENT comparada con el documento |
| Cada binding de cuota | Vencimiento del PAYMENT comparado con el calendario documentado |
| Cada binding de cuota | Corroboración y contradicciones entre los soportes revisados |
| Cuotas listadas | Revisión de posible duplicación de la obligación en los flujos suministrados, sin afirmar unicidad empresarial universal |

La cobertura de cada binding se deriva de los bindings presentes, no de una lista arbitraria del revisor. Un control omitido permanece sin revisión; jamás se rellena como confirmado.
Inventario vacío de bindings significa que no hay cuotas asociadas para revisar; no demuestra inexistencia de pagos.
Un hallazgo positivo exige nota y localización del soporte leído. Para ausencia de soporte se registra NOT_CONFIRMED con motivo, sin fabricar página/documento.
El registro debe permitir identificar condiciones o cuotas pendientes aunque algunas hayan sido confirmadas.
Confirmación de condiciones futuras no significa ejecución bancaria.

## Controles técnicos para el registro futuro
- Recibir una captura construida, no un resultado separado ni un callable de revisión.
- Copiar y conservar toda la captura examinada, persona/momento y hallazgos, con exportaciones independientes.
- Referenciar únicamente bindings/documentos de esa captura; rechazar cuota inexistente, localizador ajeno y hallazgo repetido para la misma condición/objetivo.
- Preservar importe, moneda, fecha y estados de los flujos; una revisión no los corrige ni los eleva automáticamente.
- Derivar y publicar controles pendientes a partir del inventario. No emitir un éxito global desde una colección vacía o parcial.
- Conservar conflictos declarados, aunque otra condición esté confirmada; sin agregación implícita a APTO, confianza o criticidad.
- No reinterpretar la suma de pagos como quantity × unit_price. El ejemplo distingue 1000 EUR de base y 1210 EUR exigibles.
- Si cambia documento, compra, flujo o asociación, cambia la captura: la revisión anterior no se reutiliza como revisión del nuevo material.
- Una modificación en los hallazgos/persona/momento cambia la identidad del registro, sin modificar el original.
- Las revisiones contradictorias no se resuelven seleccionando automáticamente la más reciente o favorable.
- Registrar únicamente las comprobaciones suministradas por la persona; la construcción técnica no realiza esa comprobación.

## AUDITAR
A1: atribuir revisión a QTG produciría autoridad ficticia. Se registra referencia humana aportada.
A2: un hash suelto o referencia mutable desligaría revisión y material. Se conserva captura completa examinada.
A3: confirmación global o lista vacía perdería condiciones omitidas. Se exige inventario derivado y pendientes visibles.
A4: añadir external_review_ref al material ya revisado produciría una nueva captura. El registro se mantiene complementario, sin edición circular.
A5: revisión humana de contenido no autentica al proveedor ni valida identidad/autorización. Se separan expresamente esas garantías.
A6: cambios documentales y revisiones contradictorias no tienen política de resolución autorizada. No se inventa una.

## DEPURAR
No se genera una revisión real en esta unidad. No se asigna persona, aprobación, fecha de revisión o firma.
Los estados locales describen hallazgos humanos, sin redefinir DEMONSTRATED/GAP ni estados financieros.
No se exige un calendario empresarial completo a partir de cuotas listadas; la revisión conserva ese límite.
No se implementa transición automática desde hallazgo humano a evidencia admisible para reglas o QTG.

## AUDITAR 2
PASS de diseño: mecanismo humano autorizado; identidad de material completa; hallazgos individuales y pendientes; sin ciclo de edición ni modificaciones de modelos cerrados.
PASS de fronteras: no autenticación ficticia, sin elevación de datos sintéticos, sin juicio QTG ni alteración de cálculos.
PENDIENTE: implementación/CI del registro ejecutable, designación operativa y revisiones efectivas. Persistencia/autenticación no se declaran resueltas.

## CERRAR
Se cierra este diseño documental acotado. No se cierra implementación, revisión real, admisibilidad automática ni productor QTG.
La siguiente unidad es materializar y probar el registro complementario con hallazgos explícitos, cobertura derivada y rechazo de reutilización sobre material diferente.

## MATERIALIZAR / CI
Esta unidad añade únicamente este contrato y registro de auditorías. CI requerida sobre HEAD exacto antes de integrar; su éxito no equivale a una revisión humana de documentos de compra.
Pruebas futuras: ejemplo sintético, controles omitidos, revisión vacía, cuota/localizador ajenos, hallazgo duplicado, captura modificada, conflicto, mutación de exportaciones y naturaleza sintética preservada.
