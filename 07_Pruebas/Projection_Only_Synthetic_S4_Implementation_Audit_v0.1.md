# EIOS — PROJECTION_ONLY Synthetic S4 Implementation Audit v0.1

**Estado:** CERRADO TÉCNICAMENTE — CI PENDIENTE

**Baseline:** `main @ 4e627ec407d25c6e8f36bca969d1737b563742c6`

**Unidad:** S4 — criterios presentados, manifiesto autorizado sintético y preparación financiera de calidad.

## DISEÑAR

Extender exclusivamente la frontera privada del adaptador sintético desde S1–S3 a S4. El componente `projection_criteria` se decodifica con schema estricto y se materializa por las factorías EIOS ya cerradas:

1. `PresentedQualityCriteria[]`;
2. `FinanceQualityPreparation`;
3. `AuthorizedProjectionCriterion[]`;
4. `ProjectionCriteriaManifest` v0.2;
5. validación exacta de preparación contra manifiesto.

La etapa conserva material presentado y autoridad declarada sintética, pero no interpreta el texto de los criterios, no produce `QualityCheck`, no ejecuta Finance/QTG y no convierte un manifiesto válido en permiso operacional.

## AUDITAR

**A1 — integridad documental insuficiente.** El SHA-256 del archivo `projection_criteria` ya queda protegido por `ProjectionMockDataset`, pero cada criterio presenta además bytes base64 y hash propio. Se reutiliza la validación común de base64 estándar, representación canónica exacta y SHA-256 recomputado.

**A2 — seis funciones exactas.** No se replica el catálogo. El schema usa `CriterionFunction` cerrado y la factoría `build_projection_criteria_manifest()` exige exactamente `REQUIRED_FUNCTIONS`, actualmente seis. Ausencias, extras, función duplicada o clave duplicada se rechazan por la autoridad existente.

**A3 — criterio presentado separado de la autorización.** El adaptador no deriva el manifiesto desde los criterios presentados. Ambos conjuntos se reciben explícitamente y `validate_preparation_criteria_against_manifest()` exige igualdad exacta de referencia, versión y hash.

**A4 — revisión documental inexistente.** `FinanceQualityPreparation` admite `review` y `designation`, pero el contrato del dataset de trece componentes no contiene esas cadenas. S4 pasa explícitamente `None` para ambas. Fabricarlas o inferirlas introduciría evidencia no aportada.

**A5 — cobertura negativa.** Una preparación técnicamente válida puede conservar `required_calendar_matches=False`. S4 no transforma conflictos S3 en rechazo técnico ni en conclusión de calidad.

**A6 — autoridad sintética.** `case_kind` del componente solo admite `SYNTHETIC`. `authority_ref` y `authorized_at` describen material sintético presentado; no autentican persona, mandato empresarial ni autorización operacional.

**A7 — temporalidad ambigua.** `authorized_at` debe ser datetime ISO canónico con zona. Se rechazan datetimes naive y representaciones que no round-trip por `isoformat()`.

**A8 — parcialidad pública.** `_SyntheticStage4` es interno, inmutable y conserva el fingerprint del único dataset. `__all__` permanece vacío; no existe todavía bundle público.

## DEPURAR

Quedan expresamente fuera de S4:

- interpretación semántica del contenido de criterios;
- aprobación o autenticación empresarial;
- defaults de funciones o criterios;
- traducción de criterios a estados, scores o checks;
- pago documental review/designation no presente en el dataset;
- ejecución de Finance Basic, Quality Gate, productor o consumidor QTG;
- cualquier modo `OPERATIONAL`;
- salida pública parcial.

La preparación se construye con captura, calendario y cobertura de la misma S3. El manifiesto se construye separadamente desde su declaración explícita y se vincula después por el validador cerrado.

## AUDITAR 2

El delta contra el baseline se limita a:

- `eios/core/_projection_synthetic_foundation.py`;
- `tests/test_projection_synthetic_foundation.py`;
- este registro.

Controles incorporados:

- base64 canónico y hash interno de cada criterio;
- rechazo de hash presentado incorrecto;
- seis funciones exactas del manifiesto v0.2;
- rechazo de divergencia entre material presentado y autorizado;
- rechazo de promoción `PRESENTED_OPERATIONAL`;
- rechazo de `authorized_at` sin zona;
- preservación de cobertura S3 negativa;
- ausencia explícita de review/designation;
- ausencia de llamadas a Finance/Quality/QTG;
- inmutabilidad del agregado interno.

No se modifican `finance_quality_preparation.py`, `projection_criteria_manifest.py` ni otros contratos cerrados. La prueba ejecutable completa queda condicionada a CI exact-head.

## CERRAR → MATERIALIZAR → CI

S4 queda cerrada técnicamente dentro de este alcance. La integración requiere CI exact-head, reconciliación de `main`, merge protegido y comprobación posterior de equivalencia/CI disponible.

La siguiente unidad legítima es S5 — tesorería: soporte documental, valoración contextual, verificación de mandato y revisión personal, reutilizando exclusivamente las cadenas existentes. QTG continúa deshabilitado.
