# EIOS — PROV-QUARANTINE-REGRESSION-01 — Contract v0.1

**Baseline:** `main @ 6066d2e969fa0455b4a85e5db44602ad54df092a`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO — MATERIALIZACIÓN AUTORIZADA

## 1. Propósito

Convertir en una única matriz de regresión ejecutable las cuarentenas y fronteras de procedencia que ya están cerradas documentalmente.

Esta unidad **no crea nuevas cuarentenas** y no cambia APIs. Verifica que una refactorización futura no pueda reintroducir silenciosamente rutas ya eliminadas.

## 2. Superficies protegidas

### 2.1 O1 genérico

`run_mvp_execution(...)` debe:

- conservar `QTG` en `MVP_CAPABILITY_ORDER` como capacidad arquitectónica;
- no aceptar `quality_invoker`, receipt, consumption, envelope ni resultado QTG desprendido;
- no aceptar resultados crudos desprendidos de PRICE, TCO, Decision Twin, Scenario Coordination, NI o Ladder;
- conservar los invocadores explícitos actualmente autorizados.

La ausencia de QTG en la firma genérica es una cuarentena de integración, no una eliminación conceptual de QTG.

### 2.2 Vertical MVP genérico

`run_vertical_mvp_support(...)` debe preservar las mismas exclusiones de resultados desprendidos y no exponer una vía QTG genérica.

### 2.3 Scenario Stage 2

`eios.rules.scenario_integration` debe mantener superficie pública vacía mientras no exista productor VF provenance-safe.

### 2.4 Decision Twin dependiente

`eios.rules.decision_twin_integration` debe mantener superficie pública vacía mientras dependa de Stage 2/VF bloqueado.

Esto no afecta al core/comparator de Decision Twin.

### 2.5 Adapter semántico sintético

Las etapas S1–S6 deben permanecer privadas.

La única superficie pública del adapter S7 queda limitada a:

- `ProjectionOnlySyntheticMaterialBundle`;
- `SyntheticSemanticAdapterError`;
- `SCHEMA_VERSION`;
- `build_projection_only_synthetic_material_bundle`.

## 3. AUDITAR

### A1 — test demasiado amplio

Prohibir cualquier nuevo parámetro futuro sería convertir el test en autoridad arquitectónica.

**Depuración:** se congelan exclusivamente nombres y superficies ya explícitamente cerrados por contratos de cuarentena.

### A2 — confundir invoker con provenance

El test no declarará provenance-safe a PRICE/TCO/NI/Ladder por aceptar invocadores.

**Depuración:** solo verifica que no vuelvan resultados crudos desprendidos.

### A3 — borrar QTG de arquitectura

Excluir QTG de `MVP_CAPABILITY_ORDER` falsearía la diferencia entre capacidad canónica e integración genérica bloqueada.

**Depuración:** se exige simultáneamente QTG en el orden canónico y ausencia de entrada QTG en la firma genérica.

### A4 — confundir módulos Stage2/DecisionTwin con cores

La cuarentena afecta a wrappers públicos, no a cores cerrados.

**Depuración:** se comprueba `__all__ == []` en los módulos concretos, sin bloquear imports/core engines.

### A5 — privatización sintética incompleta

Exportar accidentalmente `_build_synthetic_stageN` permitiría saltarse la atomicidad S7.

**Depuración:** se congela el inventario público del adapter y el `__all__` vacío de la foundation privada.

### A6 — test que impida una reapertura autorizada

Una futura reapertura legítima deberá modificar contrato + test de forma explícita en su propio ciclo EIOS.

**Depuración:** el test funciona como gate deliberado, no como prohibición permanente.

## 4. AUDITAR 2 — criterios de aceptación

1. cero cambios de producción;
2. una suite de regresión central nueva;
3. O1/Vertical sin QTG genérico;
4. O1/Vertical sin aliases de resultados desprendidos;
5. QTG preservado en orden canónico;
6. Stage 2 y wrapper Decision Twin continúan sin exports públicos;
7. S1–S6 sintéticos continúan privados;
8. S7 mantiene inventario público exacto;
9. ninguna afirmación de decisión, autenticación o autoridad empresarial nueva.

## 5. CERRAR → MATERIALIZAR → CI

Material autorizado:

- este contrato;
- `tests/test_provenance_quarantine_regression.py`;
- auditoría de implementación.

La unidad queda integrada solo con CI exact-head, reconciliación de `main`, merge protegido por SHA y verificación postintegración disponible.
