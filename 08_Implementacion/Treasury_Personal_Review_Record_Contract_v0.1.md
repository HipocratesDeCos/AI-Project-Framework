# EIOS — TREASURY-PERSONAL-REVIEW-01 — Revisión personal de tesorería

Fecha: 19/09/2026. Baseline remoto: `50e88900f2f3679847eb5b2d839815fea1f2066b`; CI #886 SUCCESS.
Autoridad: continuación autorizada por el titular tras proponerse expresamente el nuevo objeto técnico.
Estado: diseño auditado; no revisión real, acreditación empresarial ni habilitación QTG.

## DISEÑAR — alcance

Registro inmutable de una revisión humana individual de las condiciones documentales de tesorería del piloto al corte. Se sitúa entre TreasuryDocumentarySupport/TreasuryContextualAssessment y un futuro productor QTG. No reutiliza DocumentaryPaymentHumanReview porque ese objeto gobierna pagos; no modifica ninguno de los dos.

Entrada obligatoria:

- TreasuryContextualAssessment construido, payload/fingerprint completos;
- TreasuryMandateVerification construido, payload/fingerprint completos y vinculado al mismo target;
- review_ref, reviewer_ref y reviewed_at con zona;
- findings tipados sobre el inventario de seis condiciones de tesorería;
- previous_review_ref opcional, sólo como referencia histórica presentada.

Coherencias técnicas:

- reviewer_ref coincide exactamente con el mandato;
- target_review_ref del mandato coincide con review_ref;
- company_scope del mandato coincide con el snapshot de la preparación;
- el validador comprueba la cadena completa contextual target ↔ mandato;
- sólo verification_outcome ACREDITADO_POR_CONTRASTE permite que el registro declare assurance_scope AUTHORIZED_REVIEWER_PRESENTED_FINDINGS. NO_ACREDITADO o INCONCLUYENTE no se rechazan: conservan la revisión con assurance_scope PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FINDINGS y nunca pueden consumirse como comprobación autorizada.

La última regla evita perder hallazgos de una persona sin mandato acreditado, respetando la matriz G02: insuficiencia de designación invalida el uso autorizado, no borra lo observado.

## Hallazgos

Inventario cerrado: SOURCE_CORRESPONDENCE, ECONOMIC_CUTOFF, AMOUNT_SUPPORT, AVAILABILITY, RESTRICTIONS y SOURCE_SUFFICIENCY.

Cada condición aparece como máximo una vez:

- outcome: CONFIRMED_BY_REVIEW, NOT_CONFIRMED o CONFLICT_REPORTED;
- note no vacía;
- locators del documento preservado por TreasuryDocumentarySupport;
- CONFIRMED_BY_REVIEW y NOT_CONFIRMED exigen al menos un locator;
- CONFLICT_REPORTED puede carecer de locator cuando el conflicto sea precisamente soporte insuficiente, conservando la explicación;
- no se aceptan documentos nuevos aquí: cualquier material adicional debe incorporarse antes al registro contextual y provocar nueva identidad.

Condiciones omitidas se exponen como pending_controls. Un registro completo sólo significa seis condiciones observadas; no equivale a suficiencia, corrección o resultado QTG. CONFIRMED_BY_REVIEW no borra comparaciones técnicas negativas, restricciones o declaraciones contradictorias del soporte/contexto.

## Identidad, validación y cambios

Dataclass frozen sin constructor directo, JSON canónico, fingerprint calculado y exportaciones independientes. Conservar assessment y mandate completos, sus fingerprints, findings, pending_controls, referencias y assurance_scope derivado.

Revalidar modelos para rechazar copias/constructores inválidos, referencias con whitespace, timestamps naive, duplicados, localizadores ajenos y previous_review_ref igual a review_ref. No aceptar authorized, verified, satisfied, critical, material, QualityCheck, QualityTrustResult, resultado financiero, callback o resultado global suministrado.

Cambios en preparación, soporte, valoración contextual, mandato, revisor, momento o hallazgos crean nueva identidad. Validador de consumo exige payload/fingerprint completos de assessment y mandate, y vuelve a validar su pertenencia. No reutilizar por IDs coincidentes ni seleccionar la revisión más favorable.

## Frontera de consumo

Este registro sólo establece quién presentó qué hallazgos sobre qué material y si el mandato exacto quedó acreditado por el mecanismo local. No autentica documentos, no verifica disponibilidad bancaria, no corrige snapshot/CashFlow, no promueve Evidence y no llama Finance/QTG.

Un futuro productor podrá examinar hallazgos únicamente si:

1. assurance_scope indica mandato acreditado;
2. inventario y criterios requeridos están cubiertos;
3. observaciones originales, comparaciones y conflictos se conservan;
4. aplicabilidad, necesidad/impacto, criticidad/materialidad y suficiencia están determinadas por fuentes autorizadas;
5. controles/resultados se recomputan, no se suministran.

Incluso entonces, el productor decide controles según contrato propio; esta revisión no es una lista de QualityCheck.

## AUDITAR

A1: rechazar revisiones sin mandato borraría hallazgos útiles. Se conservan con alcance no autorizado/no resuelto.
A2: aceptar mandato acreditado como corrección técnica confundiría autoridad con verdad. Se vinculan, pero no se colapsan.
A3: permitir documentos nuevos rompería la identidad del material preparado. Se exige incorporación previa y nueva cadena.
A4: seis positivos podrían ocultar discrepancias técnicas. Se conserva el assessment/support completos y no se calcula resultado QTG.
A5: compartir outcomes con revisión de pagos no permite reutilizar su objeto. Inventarios, targets y autoridad siguen separados.
A6: previous_review_ref no acredita continuidad ni reemplazo. Se conserva como referencia sin escoger versión favorable.

## DEPURAR

Se deriva assurance_scope del mandato en vez de aceptar un booleano authorized. Se mantiene la revisión no autorizada como declaración, se prohíben documentos laterales y se exige material íntegro. No crear firma, IAM, workflow de aprobación, política de sustitución, Evidence nuevo ni nueva condición financiera.

## AUDITAR 2

PASS: necesidad del objeto confirmada por hueco físico; fronteras con pagos/contexto/mandato claras; hallazgos no borrados; autoridad y corrección separadas; cambios invalidan reutilización; sin salto a QTG.
PASS de componentes cerrados: ningún contrato o código existente se modifica.
PENDIENTE: implementación/pruebas sintéticas; cobertura empresarial real G03; cierre de inventario/criterios G02 y productor/recibo/consumo G04.

## CERRAR → MATERIALIZAR → CI

Cerrar únicamente este diseño. Materializar contrato y auditorías con CI exact-head y post-merge. CI no acredita revisión, revisor, mandato ni tesorería.

Siguiente unidad: implementar registro/validadores y probar mandato acreditado, inconcluyente y negativo; positivos ante discrepancias; findings parciales; localizadores ajenos; cambios de assessment/mandate; aislamiento Finance/QTG. Sólo Mock Data.
