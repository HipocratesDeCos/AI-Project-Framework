# EIOS — PROJECTION_ONLY Synthetic S7 Final Bundle Audit v0.1

**Estado:** CERRADO TÉCNICAMENTE — CI PENDIENTE

**Baseline:** `main @ 9dc579afe55c01f46658325784f088ed48d04867`

**Unidad:** S7 — `ProjectionMaterialEnvelope`, bundle público atómico y fixture semántica física completa.

## DISEÑAR

Cerrar el adaptador semántico aprobado en `Projection_Only_Synthetic_Semantic_Adapter_Contract_v0.1` sin reabrir S1–S6.

La única nueva salida pública es:

`ProjectionOnlySyntheticMaterialBundle`

construida exclusivamente por:

`build_projection_only_synthetic_material_bundle(ProjectionMockDataset)`.

La secuencia permanece:

`ProjectionMockDataset → S1…S6 privados → ProjectionMaterialEnvelope → bundle completo`.

No existe API pública para devolver S1–S6 parcialmente construidos.

## AUDITAR

**A1 — duplicar el envelope.** Rechazado. S7 usa `build_projection_material_envelope()` existente y no replica sus reglas de pertenencia, pendientes, naturalezas o trazabilidad.

**A2 — bundle como resultado QTG.** Rechazado. El payload final solo conserva identidad de dataset, fingerprints y alcance de traducción. No contiene `QualityCheck`, `QualityResult`, score, decisión, autorización ni resultado financiero.

**A3 — fingerprint insuficiente.** El fingerprint final liga de forma canónica:
- fingerprint del `ProjectionMockDataset`;
- fingerprint del `ProjectionMaterialEnvelope`;
- fingerprints intermedios de Finance package, captura, cobertura, preparación, manifiesto, cadenas de tesorería y flujos;
- hash canónico del calendario de cuotas, que no dispone de fingerprint propio.

El `FinanceDecisionInputPackage` ya liga PurchaseOperation, DecisionContext, Evidence, snapshot, FinanceBasicInput y resoluciones seleccionadas. El dataset fingerprint liga además los trece bytes fuente y su manifiesto.

**A4 — sustitución de objetos canónicos por payloads.** Rechazado. El bundle conserva referencias a los objetos EIOS construidos por las factorías cerradas y los expone mediante propiedades de solo lectura. El payload del bundle es únicamente el recibo de identidad/fingerprints.

**A5 — construcción parcial tras fallo.** La API pública solo devuelve después de completar S1–S6 y construir satisfactoriamente el envelope. Cualquier error anterior se propaga como `SyntheticSemanticAdapterError`; fallo del envelope se normaliza como `ENVELOPE_REJECTED [S7]`.

**A6 — promoción de naturaleza.** El builder exige que el envelope final conserve material sintético. Todos los schemas físicos S1–S6 siguen limitados a `SYNTHETIC`. El bundle declara `NO_OPERATIONAL_EFFECT`.

**A7 — fixture estructural convertida en semántica.** Rechazado. `projection_only_mock_dataset_01` permanece intacta y debe seguir fallando en traducción semántica. Se añade `projection_only_semantic_dataset_01` con `dataset_id=EIOS-PROJECTION-SEMANTIC-MOCK-001`.

**A8 — fixture semántica no física.** Resuelto. La nueva fixture contiene físicamente los trece componentes y un manifiesto independiente, no se genera mediante defaults del adaptador.

**A9 — integridad de fixture.** Se recomputaron de forma independiente los SHA-256 de los trece archivos físicos y todos coinciden exactamente con `dataset_manifest.json`.

**A10 — datos aparentemente reales.** La fixture usa identificadores `MOCK`, naturaleza `SYNTHETIC`, `NO_OPERATIONAL_EFFECT` y limitaciones explícitas. No representa empresa, persona, mandato, documento u operación reales.

## DEPURAR

Queda fuera de S7:

- modificación de `ProjectionMaterialEnvelope`;
- ejecución de Finance Basic;
- ejecución de reglas;
- ejecución de Quality Gate;
- productor o consumidor QTG;
- autenticación o autoridad empresarial;
- persistencia operacional;
- conversión de la fixture estructural;
- exposición pública de builders S1–S6;
- deducciones, defaults o correcciones de material.

`projection_synthetic_adapter.py` es una frontera de traducción y agregación, no una frontera de decisión.

## AUDITAR 2

Delta contra baseline:

- nuevo `eios/core/projection_synthetic_adapter.py`;
- nueva prueba pública `tests/test_projection_synthetic_adapter.py`;
- nueva fixture física `tests/fixtures/projection_only_semantic_dataset_01/**`;
- este registro.

No se modifica código de dominio cerrado ni `_projection_synthetic_foundation.py`.

Controles materializados:

1. fixture física completa produce bundle atómico;
2. fixture estructural continúa siendo rechazada semánticamente;
3. constructor del bundle está cerrado;
4. solo se acepta `ProjectionMockDataset` validado;
5. misma entrada produce mismo fingerprint;
6. cambio de material cambia dataset, objeto afectado, envelope y bundle;
7. inventario exacto de fingerprints finales;
8. superficie pública no exporta etapas privadas;
9. bundle/envelope no contienen resultado de calidad u operación;
10. prohibición ejecutable de Finance/Quality/QTG;
11. membresía final sin pendientes en la fixture semántica completa;
12. 13/13 hashes físicos verificados contra el manifiesto.

## CERRAR → MATERIALIZAR → CI

S7 queda cerrada técnicamente a falta de CI exact-head.

La integración requiere:

1. PR contra `main @ 9dc579afe55c01f46658325784f088ed48d04867`;
2. suite Python completa;
3. validaciones SQL completas;
4. reconciliación de `main`;
5. merge protegido por SHA;
6. comprobación de equivalencia del árbol integrado y CI post-merge cuando el conector la exponga.

Si CI resulta satisfactoria, el adaptador semántico `PROJECTION_ONLY SYNTHETIC_TEST` quedará completo S1–S7. Esto **no habilita QTG**; solo entrega el material agregado y trazable que faltaba para la siguiente frontera.
