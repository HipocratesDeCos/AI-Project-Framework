# TCO Core — CI Verification v0.1

**Contrato:** `08_Implementacion/TCO_Core_Implementation_Contract.md`  
**Estado:** VERIFICACIÓN FÍSICA MATERIALIZADA — cobertura oficial específica pendiente

## Objetivo

Definir la cobertura mínima de verificación contractual del TCO Core v0.1 sin crear una taxonomía paralela de pruebas ni nuevos `Test_ID` oficiales.

Este documento distingue entre **invariantes contractuales TCO**, **pruebas físicas materializadas** y los **casos oficiales del Plan de Pruebas**. Los identificadores `TCO-Vxx` de esta matriz son requisitos internos de verificación contractual y no constituyen `Test_ID` oficiales.

## Matriz de invariantes

| ID | Invariante | Verificación física | Test_ID oficial |
|---|---|---|---|
| TCO-V01 | I-TCO-01 | Verificado por diseño/API sin decisión MED | Cobertura específica pendiente |
| TCO-V02 | I-TCO-02 | `test_purchase_operation_is_not_modified` | Cobertura específica pendiente |
| TCO-V03 | I-TCO-03 | `test_missing_applicable_cost_is_preserved_as_unresolved` | Relación indirecta: `T-DAT-002` |
| TCO-V04 | I-TCO-04 | `test_incompatible_currency_does_not_aggregate_silently` | Cobertura específica pendiente |
| TCO-V05 | I-TCO-05 | `test_non_attributable_cost_is_rejected` | Cobertura específica pendiente |
| TCO-V06 | I-TCO-06 | Bloqueado por `GAP-TCO-02`: C0 no proporciona `importe_total` independiente | Cobertura específica pendiente |
| TCO-V07 | I-TCO-07 | `test_missing_applicable_cost_is_preserved_as_unresolved` + exclusión de financiación | Relación indirecta: `T-DAT-002` / `T-RGL-006` |
| TCO-V08 | I-TCO-08 | `test_financial_terms_are_not_automatically_added_as_tco_cost` | Cobertura específica pendiente |

Las relaciones marcadas como **indirectas** no constituyen cobertura específica TCO y no permiten declarar el invariante como probado en la matriz oficial.

## Casos físicos TCO materializados

Los siguientes comportamientos están cubiertos por `tests/test_tco_core.py`:

1. Propuesta con componentes válidos y compatibles → TCO determinable.
2. Componente aplicable sin importe → resultado no determinable, sin sustitución por cero.
3. Componente no aplicable → no contribuye.
4. Moneda incompatible → no agregación silenciosa.
5. Coste sin atribución → rechazo en la frontera del contrato.
6. Entrada fuente no modificada.
7. Condición financiera no incorporada automáticamente.

El caso de contradicción `cantidad × precio_unitario != importe_total` no puede ejecutarse con el modelo C0 actual y permanece como `GAP-TCO-02`.

## Trazabilidad

Cada invariante TCO deberá mapearse al Implementation Contract y, cuando exista, al `Test_ID` oficial correspondiente en `07_Pruebas`.

`07_Pruebas/Matriz_Trazabilidad_Ejecutable.md` establece que la matriz no crea una taxonomía paralela de pruebas ni nuevos casos: si no existe un `Test_ID` oficial, la relación permanece sin caso oficial asignado hasta que el Plan de Pruebas lo establezca.

Las pruebas físicas TCO pueden demostrar el comportamiento del código y CI, pero no sustituyen la cobertura oficial del Plan de Pruebas.

## Estado de cobertura

| Estado | Significado |
|---|---|
| COVERED | Existe un `Test_ID` oficial que cubre explícitamente el invariante TCO |
| PHYSICAL | Existe una prueba física TCO, pero todavía no un `Test_ID` oficial específico |
| INDIRECT | Existe una relación con una prueba general, pero no constituye cobertura TCO específica |
| GAP | No existe actualmente prueba suficiente |
| BLOCKED | Una dependencia documental o de modelo impide verificar el invariante |

**Estado actual:** pruebas físicas TCO materializadas y CI satisfecha; cobertura oficial específica TCO pendiente; `I-TCO-06` bloqueado por `GAP-TCO-02`.

## Límites

Este documento no crea nuevas reglas económicas, no crea `Test_ID` oficiales y no resuelve `GAP-TCO-01` ni `GAP-TCO-02`.

La ampliación del Plan de Pruebas deberá seguir la autoridad y el procedimiento definidos por `07_Pruebas` antes de que pueda declararse cobertura oficial específica completa.
