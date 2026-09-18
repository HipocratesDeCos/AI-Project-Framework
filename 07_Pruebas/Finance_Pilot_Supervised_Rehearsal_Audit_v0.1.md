# FIN-PILOT-SUPERVISION-REHEARSAL-01

Fecha: 18/09/2026. Base remota: `73f5e31096dbdecd42f26ae3373cf54530de869b`; CI #878 SUCCESS.

## DISEÑAR

Ensayar PR #183 con Mock Data explícitos: captura → cobertura → revisión de pagos → designación presentada → preparación → soporte de tesorería → valoración contextual. No se realiza una revisión real ni se ejecuta Finance/QTG. Los criterios mock son material de prueba, no políticas aprobadas.

## AUDITAR → DEPURAR

Separar completitud local de suficiencia: siete pruebas encadenadas conservan valores/estados originales y prohíben llamadas a invocador financiero y gate. Ensayar cadena completa, cuota ausente, versión de pedido ajena, importe de tesorería desconocido, moneda discrepante/restricción declarada, revisión incompleta y cambio de documento con rechazo de reutilización.

## AUDITAR 2 — cobertura de actos

| Acto | Representación actual | Límite observado |
|---|---|---|
| Material examinado | Payloads íntegros y fingerprints exactos | No autenticidad por hash |
| Calendario/cuotas | Comparación estructural y revisión presentada individual | No verificación del contenido ni identidad económica automática |
| Duplicación | Hallazgo LISTED_DUPLICATION y flujos adicionales visibles | Sin productor que demuestre deduplicación económica de todos los flujos |
| Mandato de pagos | Vínculo de designación/revisión exactos | Observaciones declaradas; no identidad/facultad operativa acreditadas |
| Mandato de tesorería | Documento adicional conservable en valoración contextual | No comprobación especializada de mandato de tesorería; el modelo de pagos no lo sustituye |
| Tesorería al corte | Declaración, comparaciones técnicas y seis observaciones | Disponibilidad/restricciones/origen siguen siendo declaraciones presentadas |
| Justificación contextual | Criterio/version, razones y localizadores conservados | No determinación autorizada de aplicabilidad/impacto/suficiencia por software |
| Cobros/otros flujos | Input completo preservado | Revisión de cuotas no acredita todas las fuentes relevantes |
| Reevaluación | Cambio documental altera toda la cadena; rechazo de vínculo anterior | No recibo QTG ni recomputación de controles de calidad implementados |

Las siete pruebas específicas pasan; regresión local completa: 1162 PASS. No hay cambios de código de producción. La cadena completa y los casos adversos nunca producen resultado operativo. Ningún hallazgo objetivo obliga a reabrir un componente cerrado.

## CERRAR → MATERIALIZAR → CI

Cerrar únicamente ensayo de representabilidad y fronteras. Materializar tests/test_finance_pilot_supervised_rehearsal.py y esta auditoría. CI exact-head y post-merge requerida antes de comunicar integración; sus registros identifican SHA/números reales.

## Pendiente que no debe ocultarse

La infraestructura de conservación ya existe. G03 no se resuelve con otra declaración o más Mock Data: falta especificar la comprobación admisible del mandato de tesorería y de los actos empresariales, y cómo distinguirla técnicamente de una declaración presentada. El piloto real requiere soporte operativo y revisión efectiva; el productor requiere además criterios/inventario completo G02 y ejecución/consumo G04.
Siguiente unidad legítima: delimitar un contrato especializado de comprobación de mandato de tesorería y su soporte verificable, contrastándolo con la designación de pagos existente sin extender su autoridad. Cualquier nuevo mecanismo de autenticación o fuente de confianza debe decidirse explícitamente; no inventar IAM, firmantes ni autorización desde la conversación.
