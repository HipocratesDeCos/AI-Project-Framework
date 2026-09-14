# EIOS — Vertical MVP QTG Provenance Quarantine · Audit 1

**Baseline auditado:** `main @ fe03a6da407490705207f579bcd45a4b384d8bc2`  
**Contrato auditado:** `Vertical_MVP_QTG_Provenance_Quarantine_Contract_v0.1.md`  
**Resultado:** APTO PARA DEPURACIÓN — 0 BLOQUEADORES.

## 1. Fuentes contrastadas

Se ha contrastado el diseño contra:

- `00_Gobierno/Baselines/EIOS-BL-003.md`;
- `03_Arquitectura/Architecture_Blueprint.md`;
- `08_Implementacion/Quality_Trust_Implementation_Contract.md`;
- `08_Implementacion/Vertical_MVP_Opaque_Result_Provenance_Quarantine_Contract_v0.1.md`;
- `08_Implementacion/Vertical_MVP_Orchestration_Composition_Contract_v0.1.md`;
- `eios/quality/gate.py` y `eios/quality/__init__.py`;
- `eios/core/mvp_execution.py`;
- `eios/mvp.py`;
- `tests/test_mvp_execution_service.py`;
- `tests/test_vertical_mvp_support.py`.

## 2. Dictamen del hallazgo

El defecto es real y está localizado en la frontera de composición:

1. QTG existe como evaluador determinista de `QualityCheck` y su contrato de dominio está cerrado.
2. Ese evaluador no produce ni reconstruye `QualityCheck` desde un `Decision Input Package` físico.
3. `QualityTrustResult` tampoco transporta identidad decisional/contextual suficiente para que una capa genérica pueda certificar por sí sola la procedencia.
4. BL-003 mantiene QTG bloqueado precisamente porque no existe todavía el paquete agregado y trazable necesario para un productor provenance-safe.
5. Sin embargo, `quality_invoker` permite que cualquier callable produzca un `CapabilityExecution` QTG y que el Vertical MVP lo publique.

La contradicción no exige modificar la semántica QTG; exige retirar la vía provisional que permite incorporarlo sin productor autorizado.

## 3. Auditoría del diseño

### A1 — Evaluador QTG cerrado ≠ integración QTG habilitada

**Hallazgo:** el contrato debe evitar cualquier formulación que pueda interpretarse como que QTG “no existe”.

**Precisión exigida:** declarar expresamente que `evaluate_quality(...)` permanece cerrado y válido; lo bloqueado es su integración Vertical provenance-safe por falta de productor desde `Decision Input Package`.

### A2 — No eliminar `QTG` del orden canónico

**Hallazgo:** retirar `QTG` de `MVP_CAPABILITY_ORDER` convertiría una cuarentena de integración en una alteración arquitectónica.

**Precisión exigida:** conservar `QTG` en el orden canónico y limitar la corrección a las firmas/composición genéricas.

### A3 — Fail-closed visible, no descarte silencioso

**Hallazgo:** conservar `quality_invoker` y no ejecutarlo escondería errores de consumidores y podría aparentar compatibilidad.

**Precisión exigida:** retirada de firma. El keyword antiguo debe producir el fallo nativo y visible de Python por argumento inesperado.

No se crea error de negocio ni estado QTG artificial.

### A4 — Reapertura futura no puede consistir en restaurar un callable genérico

**Hallazgo:** si una futura unidad simplemente reintrodujera `quality_invoker: CapabilityInvoker`, reaparecería la misma debilidad.

**Precisión exigida:** la cláusula futura debe exigir una frontera cuyo tipo/constructor o función pública esté materialmente vinculada a un productor QTG provenance-safe desde entrada trazable; no basta con volver a habilitar un callable opaco.

### A5 — Consumidores físicos

Los tests actuales contienen consumidores explícitos de `quality_invoker` y deberán reconciliarse. La materialización debe usar la suite completa como detección final de consumidores adicionales; no se autoriza modificar consumidores funcionales ajenos salvo que CI demuestre una dependencia real y esta siga dentro de la misma frontera.

## 4. Contradicciones no detectadas

No se detecta contradicción con:

- estados `APTO / APTO_CON_ADVERTENCIAS / NO_APTO`;
- confianza `ALTA / MEDIA / BAJA`;
- `NOT_EVALUABLE` de capas ajenas;
- final human authority;
- PRICE, TCO, C0/Rules, Decision Twin, Scenario Coordination, NI o Ladder;
- orden canónico de capacidades;
- composición Orchestration→Scenario Coordination.

## 5. Cambios prohibidos por esta unidad

Audit 1 prohíbe:

- modificar `eios/quality/gate.py` para fabricar procedencia;
- añadir `decision_id`, `scenario_id` u otros campos a `QualityTrustResult` como sustituto improvisado del productor;
- inventar `DecisionInputPackage`;
- generar QTG `NOT_EVALUABLE` solo para ocupar su posición en el resultado;
- convertir ausencia de QTG en `NO_APTO`;
- eliminar QTG de `MVP_CAPABILITY_ORDER`;
- alterar otras fronteras provenance-safe cerradas.

## 6. Resultado

**AUDIT 1: SUPERADA PARA DEPURACIÓN — 0 BLOQUEADORES.**

El contrato debe incorporar A1–A5 antes de Audit 2.
