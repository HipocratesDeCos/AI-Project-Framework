# EIOS — PROJECTION_ONLY Synthetic S5 Implementation Audit v0.1

**Estado:** CERRADO TÉCNICAMENTE — CI PENDIENTE

**Baseline:** `main @ 71ca8cc18bf2ee5d14a1a0f49670cdfaa593f122`

**Unidad:** S5 — soporte documental de tesorería, valoración contextual, verificación de mandato y revisión personal.

## DISEÑAR

Extender exclusivamente la frontera privada sintética desde S1–S4 a S5. Los componentes `treasury_material`, `treasury_mandate` y `treasury_review` se decodifican con schemas estrictos y alimentan únicamente las factorías EIOS ya cerradas:

1. `TreasuryDocumentarySupport`;
2. `TreasuryContextualAssessment`;
3. `TreasuryMandateVerification`;
4. `TreasuryPersonalReview`.

La etapa conserva declaraciones, soportes y revisiones presentadas. No autentica personas/canales, no determina disponibilidad real, no emite `QualityCheck` y no ejecuta Finance/QTG.

## AUDITAR

**A1 — doble integridad documental.** El hash de cada archivo de componente ya está ligado al `ProjectionMockDataset`. Los documentos binarios internos se verifican además mediante base64 estándar estricto, representación canónica exacta y SHA-256 recomputado antes de crear `DocumentaryMaterial`.

**A2 — criterio contextual incorrecto.** La factoría contextual valida que el criterio exista en la preparación, pero S5 necesita una correspondencia más precisa entre etapas. Cada declaración de tesorería debe usar exactamente la referencia/versión que el manifiesto S4 asigna a `INITIAL_TREASURY_SUFFICIENCY`. No se inspecciona ni interpreta el texto del criterio.

**A3 — autoridad sintética.** `case_kind` y `mandate_kind` quedan limitados a `SYNTHETIC`. Referencias de reviewer, verifier, channel o authority son identificadores Mock Data presentados, no prueba de identidad o facultad operacional.

**A4 — resultado de mandato.** El adaptador no acepta un outcome global suministrado. `ACREDITADO_POR_CONTRASTE`, `NO_ACREDITADO` o `INCONCLUYENTE` son derivados exclusivamente por `build_treasury_mandate_verification()` desde sus seis condiciones cerradas.

**A5 — hallazgos sin mandato positivo.** Una revisión personal puede preservar findings aunque el mandato sea inconcluso o negativo. El assurance scope cerrado impide promover esos findings a revisión autorizada. S5 conserva esa distinción sin descartarla ni reinterpretarla.

**A6 — tesorería desconocida.** `available_amount=None` permanece desconocido y produce comparación técnica `None`; no se transforma en cero, saldo disponible ni error técnico.

**A7 — revisión contextual vs revisión personal.** Los metadatos opcionales de reviewer/reviewed_at del soporte y assessment no sustituyen la cadena especializada `TreasuryMandateVerification → TreasuryPersonalReview`. Son responsabilidades distintas y no se fusionan.

**A8 — pertenencia exacta.** Support se construye desde la preparación S4; assessment desde ese support y esa preparación; mandate desde ese assessment; review desde ese assessment y ese mandate. Las factorías cerradas verifican las relaciones de target, compañía, reviewer y review_ref.

**A9 — temporalidad.** Fechas usan ISO canónico; datetimes usan ISO canónico con zona. No se infiere fecha económica desde fecha de descarga, revisión o verificación.

**A10 — parcialidad pública.** `_SyntheticStage5` continúa siendo interno e inmutable; `__all__` permanece vacío y no existe bundle público parcial.

## DEPURAR

Queda expresamente fuera:

- autenticación real del reviewer/verifier o del canal;
- comprobación bancaria o disponibilidad actual;
- inferencia de restricciones, importes, fechas o compañía;
- interpretación del criterio de suficiencia;
- creación de un outcome de mandato desde el adaptador;
- conversión de findings en `QualityCheck`;
- ejecución de Finance Basic, Quality Gate o QTG;
- admisión `PRESENTED_OPERATIONAL`;
- modificación de las cuatro factorías cerradas de tesorería.

Toda documentación adicional o de mandato debe estar explícitamente presentada en los tres componentes S5.

## AUDITAR 2

El delta contra el baseline está confinado a la frontera privada, sus pruebas y este registro. No se modifica ninguna factoría de dominio cerrada.

Las pruebas incorporadas cubren:

- cadena sintética S5 completa;
- base64 no canónico y SHA-256 incorrecto;
- binding obligatorio a `INITIAL_TREASURY_SUFFICIENCY`;
- mandato incompleto conservado como `INCONCLUYENTE`;
- findings personales conservados sin autoridad cuando el mandato no acredita;
- rechazo de promoción operacional en los tres componentes;
- rechazo de identidad de reviewer separada del mandato;
- rechazo de datetime de verificación sin zona;
- preservación de importe de tesorería desconocido;
- ausencia de ejecución Finance/Quality/QTG.

La verificación ejecutable total queda condicionada a CI exact-head.

## CERRAR → MATERIALIZAR → CI

S5 queda cerrada técnicamente dentro de este alcance. La integración exige CI completa satisfactoria sobre el SHA exacto, reconciliación contra `main`, merge protegido y comprobación posterior de equivalencia del árbol/CI disponible.

La siguiente unidad legítima es S6 — inventario y completitud de flujos, mandato especializado y revisión personal. QTG continúa deshabilitado.
