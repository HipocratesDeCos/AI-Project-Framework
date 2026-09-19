# EIOS — FLOW-INVENTORY-REVIEW-01 — Mandato y revisión especializada v0.1

Fecha: 19/09/2026. Baseline remoto: `985c8a609d570058d03ebabe3d69198d76020e50`; PR #192 y CI #895/#896 SUCCESS.
Autoridad: aceptación explícita del titular del proyecto de diseñar la revisión especializada y el mandato aplicable al inventario de flujos.
Estado: diseño técnico auditado; no implementa comprobación real, revisión, productor QTG ni ejecución financiera.

## DISEÑAR — propósito y separación obligatoria

Definir dos registros inmutables especializados y encadenados:

1. `FlowInventoryMandateVerification`: conserva el contraste del mandato para revisar un `FinanceFlowCompletenessRecord` concreto y una futura `review_ref` concreta.
2. `FlowInventoryPersonalReview`: conserva los hallazgos que la persona identificada presenta sobre ese registro, vinculados al mandato exacto.

Mandato y revisión no se fusionan. El primero responde a quién puede presentar una comprobación dentro de un alcance; el segundo conserva qué observó. Mandato acreditado no convierte los hallazgos en verdaderos. Hallazgos correctos presentados sin mandato no se borran, pero no pueden consumirse como revisión autorizada.

Fuentes: QTG-PROJECTION-ONLY-01; FIN-FLOW-COMP-01; QTG v0.4; Evidence Contract; QTG-FIN-G02-BASE-01; precedentes TREASURY-MANDATE-VERIFY/RECORD-01 y TREASURY-PERSONAL-REVIEW-01, únicamente como patrón de separación y no como autoridad transferible.

No se modifica ningún objeto existente. No se reutilizan automáticamente mandatos de pagos o tesorería. No se crean `QualityCheck`, resultado QTG, Evidence, firma, IAM, directorio empresarial, workflow de aprobación ni decisión financiera.

## A. `FlowInventoryMandateVerification`

### Entrada y objetivo exacto

El builder recibe:

- `FinanceFlowCompletenessRecord` construido, payload y fingerprint completos;
- `verification_ref`, `company_scope`, `reviewer_ref`, `mandate_ref` y `target_review_ref` no vacíos;
- `verifier_ref` y `verified_at` con zona;
- `channel_ref`, `channel_kind` y `recognition_basis` (`PREVIOUSLY_RECOGNIZED` o `INDEPENDENTLY_SUPPORTED`);
- tres colecciones explícitas y no vacías de documentos: mandato, reconocimiento del canal y soporte del contraste;
- naturaleza del mandato `SYNTHETIC` o `PRESENTED_OPERATIONAL`;
- observaciones tipadas del inventario cerrado.

`purpose_scope` canónico: `FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY`.

`company_scope` debe coincidir con el snapshot contenido en el registro. `target_review_ref` conserva el objetivo futuro sin afirmar que la revisión ya exista. No se almacena correo, teléfono, credenciales, tokens, códigos, claves o contenido excedente de comunicaciones como campos del contrato.

### Condiciones del mandato

Inventario cerrado:

1. `PERSON_IDENTITY` — correspondencia de la persona revisora;
2. `COMPANY_RELATION` — relación con el `company_scope` examinado;
3. `GRANTOR_AUTHORITY` — facultad del otorgante para delegar este alcance;
4. `FLOW_INVENTORY_SCOPE` — mandato explícito para revisar completitud, atributos, horizonte, pertenencia y duplicación de cobros/pagos;
5. `VALIDITY_AND_KNOWN_CHANGES` — vigencia y cambios/revocaciones examinados;
6. `TARGET_RECORD_BINDING` — vínculo con `record_ref`, fingerprint y `target_review_ref` exactos.

Cada condición aparece como máximo una vez:

- `outcome`: `CONFIRMED_BY_CONTRAST`, `NOT_CONFIRMED_BY_CONTRAST` o `CONFLICT_REPORTED`;
- `note` no vacía;
- locators tipados por origen `MANDATE_DOCUMENT`, `CHANNEL_RECOGNITION_SUPPORT` o `CONTRAST_SUPPORT`;
- confirmación o no confirmación exige soporte localizado; conflicto puede carecer de locator cuando el problema sea precisamente soporte incompleto.

La ausencia queda en `pending_conditions`; no equivale a incumplimiento. El resultado local se deriva, nunca se recibe:

| Observación | `verification_outcome` |
|---|---|
| Alguna condición `NOT_CONFIRMED_BY_CONTRAST` | `NO_ACREDITADO` |
| Sin anterior, pero existe condición omitida o `CONFLICT_REPORTED` | `INCONCLUYENTE` |
| Las seis condiciones confirmadas | `ACREDITADO_POR_CONTRASTE` |

Precedencia: `NO_ACREDITADO` sobre `INCONCLUYENTE`. Resultado y alcance son locales; no autorizan pagos, contabilización, modificación del registro, QTG o Finance.

## B. `FlowInventoryPersonalReview`

### Entrada y pertenencia

El builder recibe:

- `FinanceFlowCompletenessRecord` construido y exacto;
- `FlowInventoryMandateVerification` construido y vinculado al mismo record/review objetivo;
- `review_ref`, `reviewer_ref`, `reviewed_at` con zona y `previous_review_ref` opcional;
- tupla explícita de hallazgos tipados.

Coherencias obligatorias:

- `review_ref = target_review_ref` del mandato;
- `reviewer_ref` coincide con el mandato;
- empresa y target completos coinciden;
- el validador recomprueba payload/fingerprint de record y mandato;
- `previous_review_ref` no puede ser la propia revisión y no establece sustitución, continuidad o vigencia.

### Inventario de revisión

Inventario cerrado de nueve condiciones:

1. `PERIMETER_COVERAGE` — perímetros declarados y límites examinados;
2. `SOURCE_COVERAGE` — fuentes/perímetros consultados y soporte de cobertura;
3. `CAPTURED_FLOW_COVERAGE` — todos los `CashFlow` capturados valorados o pendientes visibles;
4. `UNMATCHED_CANDIDATES` — candidatos sin flujo capturado examinados y conservados;
5. `HORIZON_CLASSIFICATION` — dentro, posterior, no futuro, desconocido o conflictivo sin exclusión indebida;
6. `FLOW_ATTRIBUTE_SUPPORT` — importe, moneda, vencimiento y pertenencia económica examinados;
7. `ECONOMIC_DUPLICATION` — riesgo de doble cómputo examinado sin fusión heurística;
8. `PURCHASE_PAYMENT_COHERENCE` — cadena de cuotas de compra conservada, sin asumir que cubre otros flujos;
9. `CONFLICTS_AND_LIMITATIONS` — conflictos, declaraciones incompletas y limitaciones conservados.

Cada condición aparece como máximo una vez y contiene:

- `outcome`: `CONFIRMED_BY_REVIEW`, `NOT_CONFIRMED` o `CONFLICT_REPORTED`;
- `note` no vacía;
- locators tipados a `FLOW_INVENTORY_MATERIAL` o `PAYMENT_CAPTURE` ya conservados en el record/preparación;
- referencias opcionales a `perimeter_ref`, `candidate_ref` y `flow_id`, todas existentes y sin duplicados dentro del hallazgo.

`CONFIRMED_BY_REVIEW` y `NOT_CONFIRMED` exigen al menos un locator o una referencia estructural existente. `CONFLICT_REPORTED` puede carecer de ambos si la nota identifica que el conflicto es ausencia de soporte. El builder valida pertenencia; no interpreta los documentos.

Las condiciones omitidas se publican como `pending_conditions`. Un inventario completo de nueve hallazgos significa únicamente que todas las condiciones fueron abordadas; no demuestra que sus conclusiones sean suficientes ni que los flujos empresariales estén completos.

### Alcance derivado

El builder no recibe `authorized`:

- mandato `ACREDITADO_POR_CONTRASTE` → `AUTHORIZED_REVIEWER_PRESENTED_FLOW_FINDINGS`;
- mandato `NO_ACREDITADO` o `INCONCLUYENTE` → `PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FLOW_FINDINGS`.

Ambos casos conservan los hallazgos. El segundo nunca se consume como comprobación autorizada. El primero acredita solo mandato local; no certifica exactitud o suficiencia del hallazgo.

## Material, identidad y reutilización

Ambos objetos serán dataclasses frozen sin constructor directo, JSON canónico, fingerprint calculado, exportaciones independientes y bytes documentales recuperables solo en el mandato. Revalidarán modelos para rechazar bypass, referencias con whitespace, bytes vacíos, timestamps naive, localizadores ajenos y duplicados.

Cambiar record, perímetro, candidato, flujo, preparación, mandato, canal, soporte, persona, momento, hallazgo o referencia crea identidad nueva. No actualizar retroactivamente, escoger la revisión más favorable ni reutilizar por igualdad parcial de IDs o hashes.

Los validadores para consumo exigirán material íntegro y fingerprints calculados de toda la cadena. Fallos de estructura/pertenencia son errores técnicos, no `NO_ACREDITADO`, `NOT_CONFIRMED` o `NO_APTO`.

## Frontera con el futuro productor QTG

La revisión no produce ni acepta `QualityCheck`, `QualityTrustResult`, `critical`, `material`, `satisfied`, estado financiero, resultado de proyección o callback.

Un futuro productor solo podrá considerar sus hallazgos cuando:

1. el mandato exacto esté `ACREDITADO_POR_CONTRASTE`;
2. record, mandato y revisión pertenezcan a la misma cadena completa;
3. el inventario requerido por `PROJECTION_ONLY` esté cubierto;
4. la suficiencia de fuentes/observaciones esté determinada por autoridad aplicable;
5. pendientes, candidatos no capturados, fechas inciertas, conflictos y duplicidades se conserven;
6. los controles se recomputen mediante productor autorizado.

Incluso nueve `CONFIRMED_BY_REVIEW` no permiten invocar el gate si faltan condiciones, material o criterios del productor. La revisión no modifica `CashFlow.evidence_state`, no elimina `pending_flow_ids`/`unmatched_candidate_refs` y no corrige el record.

## AUDITAR

A1: reutilizar mandato de tesorería o pagos ampliaría autoridad por analogía. Se crea alcance exclusivo de inventario de flujos.

A2: comprobar mandato y revisar en el mismo objeto permitiría que los hallazgos autoacreditasen a su autor. Se separan dos objetos y dos inventarios.

A3: rechazar revisión no autorizada borraría información. Se conserva con alcance no autorizado/no resuelto.

A4: una revisión completa podría confundirse con inventario empresarial completo. Se distingue cobertura de nueve condiciones de suficiencia material y completitud real.

A5: confirmar `CAPTURED_FLOW_COVERAGE` podría ocultar candidatos no capturados. `UNMATCHED_CANDIDATES` permanece condición independiente.

A6: una confirmación de atributos podría resolver implícitamente conflictos o duplicados. Se conservan condiciones separadas y el record íntegro.

A7: revisar pagos de compra podría presentarse como cobertura global. `PURCHASE_PAYMENT_COHERENCE` no sustituye perímetro, fuentes ni otros flujos.

A8: locators sin vínculo permitirían material lateral. Solo pueden referir documentos ya conservados; nuevos documentos exigen nuevo record o mandato según su función.

A9: persona, fecha o canal declarado podrían aparentar autenticación. Solo el resultado derivado del contraste completo determina el alcance local; naturaleza sintética nunca acredita operación real.

A10: positivos humanos podrían convertirse directamente en checks. Se prohíbe traducción o ejecución desde estos registros.

## DEPURAR

Se incorporan A1–A10. Se separan mandato, hallazgo, pertenencia estructural, suficiencia empresarial y futura evaluación QTG. No se impone proveedor, cargo, tecnología, doble firma, plazo universal, umbral monetario, algoritmo de deduplicación o prioridad documental.

El mecanismo manual debe usar canal previamente reconocido o soporte independiente, siguiendo el precedente cerrado; no se valida por el contacto incluido únicamente en el propio mandato. Se conserva material mínimo reproducible y se excluyen secretos como campos.

## AUDITAR 2

PASS de diseño:

- mandato especializado sin extensión de autorizaciones existentes;
- revisión y competencia separadas;
- tres resultados locales de mandato derivados;
- revisión no autorizada conservada sin habilitar consumo;
- nueve condiciones cubren perímetro, omisiones, atributos, horizonte, duplicación y cuotas sin colapsarlas;
- referencias estructurales y documentales vinculadas al record exacto;
- parcialidad, conflicto y ausencia preservados;
- identidades sensibles a cualquier cambio de cadena;
- ningún salto a Evidence, Finance, QTG o decisión.

HALLAZGO: el diseño permite implementar y probar la cadena con Mock Data, pero no identifica un revisor, otorgante, canal o mandato empresarial real. G03 operativo y el productor positivo continúan abiertos.

## CERRAR → MATERIALIZAR → CI

Se cierra únicamente el diseño `FLOW-INVENTORY-REVIEW-01`. Materialización: este contrato documental. CI exact-head y post-merge obligatorias; su éxito no acredita personas, canales, hallazgos ni completitud empresarial.

Siguiente unidad legítima: implementar ambos registros y validadores con pruebas sintéticas de mandato acreditado/no acreditado/inconcluyente, revisión autorizada/no autorizada, parcialidad, positivos ante pendientes/conflictos, referencias ajenas, cambios de target, bypass, mutabilidad y aislamiento Finance/QTG.
