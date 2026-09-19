# EIOS — TREASURY-MANDATE-RECORD-01 — Contrato técnico del contraste manual

Fecha: 19/09/2026. Baseline remoto: `ea77ef8268fb04ae93ecd9e8314015f8de8ca7e4`; CI #882 SUCCESS.
Estado: diseño técnico auditado; sin implementación, canal real, comprobación ejecutada ni habilitación QTG.

## DISEÑAR — propósito y entrada

Materializa únicamente un recibo inmutable del procedimiento TREASURY-MANDATE-VERIFY-01. Debe enlazar el mandato de tesorería presentado con la revisión/material financiero exactos para los que se pretende utilizar. No sustituye Evidence, DocumentaryReviewerDesignationLink ni crea IAM, firma electrónica, directorio corporativo o repositorio de comunicaciones.

Entrada mínima:

| Grupo | Campos y obligación |
|---|---|
| Identidad del acto | verification_ref y purpose_scope no vacíos; purpose_scope canónico TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT |
| Objetivo | company_scope, reviewer_ref, mandate_ref y target_review_ref no vacíos; payload y fingerprint completos del TreasuryContextualAssessment o material especializado futuro al que se vincula |
| Ejecutor | verifier_ref y verified_at aportados juntos; datetime con zona; son identidad declarada del acto, no autenticación automática |
| Canal | channel_ref, channel_kind declarado y recognition_basis no vacíos; reconocimiento PREVIOUSLY_RECOGNIZED o INDEPENDENTLY_SUPPORTED; soporte documental íntegro de reconocimiento/contraste |
| Mandato | documentos íntegros con referencias únicas, bytes y hashes calculados; naturaleza SYNTHETIC o PRESENTED_OPERATIONAL separada |
| Observaciones | inventario exacto de seis condiciones; outcome individual, explicación y localizadores tipados por origen |

No almacenar dirección de correo, teléfono, credenciales, tokens, claves, códigos de acceso o datos bancarios como campos del contrato. channel_ref debe ser una referencia opaca/reproducible al canal gobernado, no el secreto ni el contenido completo de la comunicación. Los documentos conservados deben limitarse al soporte necesario y no contener secretos; esta validación semántica sigue siendo responsabilidad del acto supervisado, no del constructor.

## Inventario y observación individual

Inventario cerrado para este procedimiento:

1. PERSON_IDENTITY;
2. COMPANY_RELATION;
3. GRANTOR_AUTHORITY;
4. TREASURY_SCOPE;
5. VALIDITY_AND_KNOWN_CHANGES;
6. TARGET_CONTEXT_BINDING.

Cada condición aparece como máximo una vez y contiene:

- outcome: CONFIRMED_BY_CONTRAST, NOT_CONFIRMED_BY_CONTRAST o CONFLICT_REPORTED;
- note no vacía, sin reemplazar hechos desconocidos por negativos;
- locators no vacíos para CONFIRMED_BY_CONTRAST y NOT_CONFIRMED_BY_CONTRAST;
- locators opcionales para CONFLICT_REPORTED, conservando la falta si el conflicto procede precisamente de soporte incompleto;
- origen del locator: MANDATE_DOCUMENT, CHANNEL_RECOGNITION_SUPPORT o CONTRAST_SUPPORT;
- document_ref, página positiva y sección no vacía, pertenecientes al conjunto conservado del origen declarado.

La omisión de una condición permanece en pending_conditions; no se crea una observación por defecto. NOT_CONFIRMED_BY_CONTRAST sólo se usa cuando el soporte permite afirmar incumplimiento. Falta, imposibilidad de contraste o duda se representan mediante omisión o CONFLICT_REPORTED según exista conflicto observado.

## Derivación determinista del resultado local

El constructor no recibe un resultado global. Lo deriva así:

| Material observado | verification_outcome |
|---|---|
| Alguna condición NOT_CONFIRMED_BY_CONTRAST | NO_ACREDITADO |
| Sin anterior, pero existe condición omitida o CONFLICT_REPORTED | INCONCLUYENTE |
| Las seis condiciones están presentes y CONFIRMED_BY_CONTRAST | ACREDITADO_POR_CONTRASTE |

La precedencia NO_ACREDITADO sobre INCONCLUYENTE conserva un incumplimiento demostrado aunque coexistan faltantes; pending_conditions y conflictos siguen visibles. Estos valores son locales al mandato. No son Evidence.state, QualityCheck, QualityTrustResult, autorización de pago ni juicio de corrección financiera.

## Pertenencia, coherencia y errores técnicos

- target material debe ser un TreasuryContextualAssessment construido; conservar payload/fingerprint completos y validar su cadena exacta con preparación y soporte de tesorería cuando se proporcionen al validador de consumo;
- company_scope y reviewer_ref deben coincidir con el objetivo declarado que el material vinculado exponga cuando esos campos existan; si el material actual no contiene una revisión de tesorería personal identificada, target_review_ref sigue siendo una referencia presentada y el registro no afirma que la revisión exista;
- ningún documento puede repetirse o compartir referencia entre orígenes;
- revalidar todos los modelos tipados para rechazar model_construct/model_copy inválidos, whitespace, bytes vacíos, páginas no positivas y timestamps naive;
- no aceptar fingerprints suministrados, resultado global, QualityCheck, estado QTG, flags authorized/verified, callback o función de comprobación;
- problemas de construcción/pertenencia son errores técnicos, no NO_ACREDITADO.

La limitación sobre target_review_ref es deliberada: el contrato conserva el vínculo solicitado, pero no inventa un modelo de revisión de tesorería ni atribuye persona al TreasuryContextualAssessment existente. Una futura revisión especializada deberá incorporarse mediante ciclo propio antes de consumo automático.

## Inmutabilidad y reutilización

Material JSON canónico, dataclass frozen sin constructor directo, fingerprint calculado, exportaciones independientes y recuperación exacta de bytes por origen/referencia. Cambiar cualquier objetivo, canal, soporte, documento, observación, actor o momento cambia la identidad.

Validador para consumo exige igualdad completa de payload y fingerprint del target; no basta company_scope, reviewer_ref, IDs, fechas o hashes coincidentes. Cambios del material o mandato exigen un nuevo contraste. No actualizar retroactivamente ni escoger el registro más favorable.

## AUDITAR

A1: aceptar outcome global permitiría fabricar acreditación. Se deriva únicamente del inventario individual.
A2: CONFIRMED sin soporte localizable sería una afirmación desnuda. Se exigen localizadores preservados.
A3: contacto/canal y secreto no deben almacenarse como lo mismo. Se conserva referencia opaca, base de reconocimiento y soporte mínimo, prohibiendo secretos como campos.
A4: el target actual no identifica una revisión personal de tesorería. Se conserva esa limitación y no se fuerza una relación ficticia con la revisión de pagos.
A5: ausencia no prueba incumplimiento. Se separan pending/CONFLICT_REPORTED de NOT_CONFIRMED.
A6: seis confirmaciones sintéticas pueden derivar el resultado local, pero siguen siendo SYNTHETIC y nunca acreditación empresarial.
A7: vincular sólo por fingerprint o IDs permitiría reciclaje. Se exige material íntegro y recomprobación de pertenencia.

## DEPURAR

Se elimina cualquier booleano authorized/verified y toda posibilidad de suministrar el resultado. Se separan tres orígenes documentales, se mantiene naturaleza por conjunto y se explicita la carencia de revisión personal de tesorería en el modelo actual. No se prescribe proveedor, API, doble firma, formato de comunicación, plazo o política de protección de datos inexistente.

## AUDITAR 2

PASS: resultado local determinista; ausencia/conflicto/incumplimiento diferenciados; soporte y canal no circulares; material exacto e identidad de cambios; secretos excluidos de campos; ninguna promoción a QTG/Evidence.
PASS de fronteras: no modifica componentes cerrados ni extiende DocumentaryReviewerDesignationLink; no afirma que DESIG-2026-004-v2 o cualquier Mock Data sea real.
PENDIENTE: implementación y pruebas sintéticas; diseño posterior de revisión personal de tesorería si se requiere consumo automatizado; canal y comprobación empresariales reales; G02/G03/G04 completos.

## CERRAR → MATERIALIZAR → CI

Cerrar sólo este diseño técnico. Materializar el contrato con auditorías; CI exact-head y post-merge antes de comunicar integración. CI no valida canales, personas ni mandatos.

Siguiente unidad: implementar el recibo y validadores con casos ACREDITADO_POR_CONTRASTE, NO_ACREDITADO e INCONCLUYENTE sintéticos; comprobar colisiones, localizadores ajenos, secretos como campos prohibidos, objetivo modificado y aislamiento Finance/QTG. No ejecutar contraste real.
