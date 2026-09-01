# TCO Core — CI Verification v0.1

**Contrato:** `08_Implementacion/TCO_Core_Implementation_Contract.md`  
**Estado:** PREPARADO — verificación pendiente de implementación

## Objetivo

Definir la cobertura mínima de verificación contractual del TCO Core v0.1 sin crear una taxonomía paralela de pruebas ni nuevos `Test_ID`.

Este documento distingue entre **invariantes contractuales TCO** y los **casos oficiales del Plan de Pruebas**. Los identificadores `TCO-Vxx` de esta matriz son requisitos internos de verificación contractual y no constituyen `Test_ID` oficiales.

## Matriz de invariantes

| ID | Invariante | Verificación requerida | Test_ID oficial |
|---|---|---|---|
| TCO-V01 | I-TCO-01 | TCO no produce decisiones MED | Cobertura específica pendiente |
| TCO-V02 | I-TCO-02 | C0/C1/parámetros permanecen sin modificación | Cobertura específica pendiente |
| TCO-V03 | I-TCO-03 | ausencia de dato no se convierte en cero | Relación indirecta: `T-DAT-002` |
| TCO-V04 | I-TCO-04 | monedas incompatibles no se agregan silenciosamente | Cobertura específica pendiente |
| TCO-V05 | I-TCO-05 | coste no atribuible no contribuye al Core | Cobertura específica pendiente |
| TCO-V06 | I-TCO-06 | contradicción de entradas no se corrige silenciosamente | Cobertura específica pendiente |
| TCO-V07 | I-TCO-07 | ausencia de regla/dato no genera estimación implícita | Relación indirecta: `T-DAT-002` / `T-RGL-006` |
| TCO-V08 | I-TCO-08 | extensiones de `GAP-TCO-01` no entran en el Core | Cobertura específica pendiente |

Las relaciones marcadas como **indirectas** no constituyen cobertura específica TCO y no permiten declarar el invariante como probado.

## Casos funcionales mínimos a verificar

1. Propuesta con todos los componentes necesarios y compatibles → TCO determinable.
2. Componente aplicable sin dato → el resultado conserva la insuficiencia; no se sustituye por cero.
3. Componente no aplicable → no contribuye.
4. Monedas incompatibles sin normalización autorizada → no agregación silenciosa.
5. Cantidad/precio/importe contradictorios → no corrección silenciosa.
6. Coste sin atribución demostrable → no contribuye.
7. Condición de pago presente sin regla financiera TCO → no se convierte automáticamente en coste financiero.
8. Petición de decisión de compra → TCO no la produce.

Estos casos son **requisitos de cobertura del contrato**, no casos oficiales hasta que el Plan de Pruebas los incorpore mediante `Test_ID` conforme a su propia gobernanza.

## Trazabilidad

Cada invariante TCO deberá mapearse al Implementation Contract y, cuando exista, al `Test_ID` oficial correspondiente en `07_Pruebas`.

`07_Pruebas/Matriz_Trazabilidad_Ejecutable.md` establece que la matriz no crea una taxonomía paralela de pruebas ni nuevos casos: si no existe un `Test_ID` oficial, la relación permanece sin caso oficial asignado hasta que el Plan de Pruebas lo establezca.

Las pruebas generales existentes pueden aportar evidencia relacionada, pero no se considerarán cobertura específica TCO salvo que el caso y su resultado esperado cubran explícitamente el comportamiento TCO.

## Estado de cobertura

| Estado | Significado |
|---|---|
| COVERED | Existe un `Test_ID` oficial que cubre explícitamente el invariante TCO |
| INDIRECT | Existe una relación con una prueba general, pero no constituye cobertura TCO específica |
| GAP | No existe actualmente un `Test_ID` oficial específico |
| BLOCKED | Existe prueba oficial, pero una dependencia impide su ejecución |

Estado actual: **GAP de cobertura específica TCO**. La existencia de esta matriz no permite declarar CI TCO completo.

## Límites

Este documento no constituye implementación, no crea nuevas reglas económicas, no crea `Test_ID` oficiales y no resuelve `GAP-TCO-01`.

La ampliación del Plan de Pruebas deberá seguir la autoridad y el procedimiento definidos por `07_Pruebas` antes de que pueda declararse cobertura específica completa.
