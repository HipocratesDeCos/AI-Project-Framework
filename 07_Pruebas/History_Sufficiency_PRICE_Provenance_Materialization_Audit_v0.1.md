# EIOS — History Sufficiency PRICE Provenance · Materialization Audit v0.1

## Estado

**MATERIALIZACIÓN AUDITADA — SIN DESVIACIONES DE ALCANCE**

Unidad: `HIS-PRICE-PROV-01`

Baseline: `main @ 64ffacefc26f2199a9caa81ad58aa227c9dc4125`

Rama: `fix/history-sufficiency-price-provenance-v0.1`

## 1. Método completado

**DISEÑAR ✅ → AUDITAR ✅ → DEPURAR ✅ → AUDITAR 2 ✅ → CERRAR ✅ → MATERIALIZAR ✅**

Pendiente: **CI**.

## 2. Comparación contra baseline

Comparación GitHub antes de este propio artefacto de auditoría:

- estado: `ahead`;
- `ahead_by = 9`;
- `behind_by = 0`;
- merge base exacto: `64ffacefc26f2199a9caa81ad58aa227c9dc4125`;
- 8 ficheros afectados.

No existe divergencia de `main` dentro de la rama auditada.

## 3. Delta materializado

### Documentación metodológica

- `08_Implementacion/History_Sufficiency_PRICE_Provenance_Contract_v0.1.md`;
- `07_Pruebas/History_Sufficiency_PRICE_Provenance_Audit_1_v0.1.md`;
- `07_Pruebas/History_Sufficiency_PRICE_Provenance_Depuration_v0.1.md`;
- `07_Pruebas/History_Sufficiency_PRICE_Provenance_Audit_2_v0.1.md`;
- `07_Pruebas/History_Sufficiency_PRICE_Provenance_Closure_v0.1.md`.

### Código

`eios/rules/pricing.py`:

- incorpora `PriceIntelligenceAssessmentContext`;
- incorpora el productor cerrado `run_price_intelligence`;
- elimina `PriceIntelligenceResult` de la identidad de entrada del bridge;
- elimina `pricing_result` de `evaluate_r_his_002(...)`;
- valida compra/contexto mediante `pricing_input`;
- crea snapshots profundos del input y assessment context;
- reconstruye localmente el resultado PRICE;
- valida la evidencia contra ese resultado reconstruido;
- conserva íntegra la evaluación `n_comparable < P-PRE-006` y el contrato del parámetro.

`eios/rules/orchestrator.py`:

- elimina `PriceIntelligenceResult` del bundle `HistorySufficiencyRuleInputs`;
- incorpora `pricing_assessment_context`;
- pasa el nuevo material C1 al bridge.

### Tests

`tests/test_r_his_002_vertical.py`:

- deja de usar resultados PRICE manuales como entrada válida;
- genera `n_comparable` mediante referencias/evidencias C1 reales;
- cubre TRUE y FALSE;
- preserva ausencia de parámetro y company mismatch;
- cubre evidencia ligada a otro resultado;
- cubre evidencia PRICE `GAP` → `NOT_EVALUABLE`;
- cubre input PRICE de otro contexto;
- verifica ausencia de `pricing_result` en función y dataclass;
- preserva CRC R3 frente a R2.

## 4. Límites comprobados

No se han modificado:

- `eios/pricing/*`;
- `eios/core/price_integration.py`;
- ningún otro fichero `eios/core/*`;
- `eios/mvp.py`;
- Matriz de Reglas;
- Rule Dependency Matrix;
- Catálogo/Matriz de Parámetros;
- CRC;
- PRICE methodology;
- TCO;
- QTG;
- Decision Twin;
- Scenario Engine.

## 5. Semántica comprobada

No se ha modificado:

- `R-HIS-002`;
- su efecto/severidad;
- `P-PRE-006`;
- la condición `n_comparable < P-PRE-006`;
- la metodología que determina `n_comparable`.

El único cambio funcional es la **procedencia del resultado PRICE consumido por Rules**: ahora se reconstruye desde sus inputs C1 validados en lugar de ser inyectado como resultado desprendido.

## 6. Fail closed

Se conserva:

- mismatch estructural → excepción;
- evidencia `DEMONSTRATED` no ligada al resultado reconstruido → excepción;
- evidencia no válida → `NOT_EVALUABLE`;
- ausencia/configuración no utilizable del parámetro → comportamiento vigente;
- error del motor C1 → propagación, sin fallback.

## 7. Dictamen

La materialización coincide con el diseño cerrado y no invade componentes fuera de alcance.

**MATERIALIZACIÓN AUDITADA — SIN DESVIACIONES.**

La unidad puede pasar a **CI / PR**. El cierre físico solo podrá declararse después de CI pre-merge, merge protegido por SHA y CI post-merge exacto del nuevo `main`.
