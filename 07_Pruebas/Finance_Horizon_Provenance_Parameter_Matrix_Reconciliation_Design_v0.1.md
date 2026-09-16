# EIOS — Finance Horizon Provenance Parameter Matrix Reconciliation — Design v0.1

## Estado

**Fase:** DISEÑAR  
**Unidad:** FIN-PROV-PARAM-MATRIX-01  
**Baseline:** `main @ 985ec56f64ba143f33048035a510ad28b589d596`  
**Naturaleza:** reconciliación documental; sin cambio funcional ni runtime.

## 1. Hallazgo objetivo

`FIN-PROV-HORIZON-01` quedó cerrado físicamente mediante la frontera provenance-safe de Finance (`Finance_Horizon_Provenance_Contract_v0.1.md` + `ProvenancedFinanceBasicExecution`), integrada por PR #150 y validada por CI #808/#809. La RDM vigente ya reconcilia ese estado como cerrado.

Sin embargo, `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.9.3 conserva tres formulaciones históricas que aún presentan el gap como abierto:

1. la reconciliación `P-FIN-001 → R-FIN-001` afirma que `FIN-PROV-HORIZON-01` permanece abierto;
2. la sección de pendientes lo mantiene como deuda técnica abierta;
3. la sección de estado vuelve a indicar que permanece abierto.

Existe una contradicción documental de estado, no una deuda funcional nueva.

## 2. Objetivo

Reconciliar únicamente el estado físico de `FIN-PROV-HORIZON-01` en la Matriz de Parámetros, alineándola con la implementación y con la RDM vigente.

## 3. Materialización prevista

- `Matriz_Parametros_Reglas_MVP.md` versión `0.9.3 → 0.9.4`;
- sustituir las tres formulaciones obsoletas por referencias explícitas al cierre físico;
- citar la frontera `ProvenancedFinanceBasicExecution`, PR #150 y CI #808/#809;
- preservar la clasificación derivada `P-FIN-001 → R-FIN-001`;
- preservar `P-FIN-001 = 30 días` como valor inicial pendiente de validación empresarial;
- no alterar ninguna otra relación, regla o parámetro.

## 4. Límites

Esta unidad no:

- modifica código Finance;
- modifica tests ejecutables;
- reabre PR #150;
- cambia el contrato de provenance;
- convierte 30 días en política empresarial definitiva;
- altera `P-FIN-002 → R-FIN-003`;
- asigna nuevos consumidores;
- modifica PRE-TEMP-DEP-01 ni RDM v1.5.5;
- modifica C0, CRC, QTG, PRICE, Rotation o arquitectura.

## 5. Invariantes

1. Relación documental cerrada ≠ validación del valor empresarial.
2. Cierre físico de provenance ≠ cambio de semántica de `R-FIN-001`.
3. La Matriz de Parámetros describe el estado vigente; no debe contradecir una frontera física ya integrada y validada.
4. No se completan otros pendientes por proximidad documental.

## 6. Criterio de avance

Solo se materializará tras Audit 1, Depuración y Audit 2 limpios. El delta canónico debe limitarse a `02_Parametros/Matriz_Parametros_Reglas_MVP.md` más los artefactos de control de esta unidad.
