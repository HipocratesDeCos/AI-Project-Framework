# EIOS — O2 · CONTRATO SCENARIO ENGINE

**Estado:** DISEÑO — NO CERRADO  
**Baseline de entrada:** `06e8270545f57c904f99229430a9be4575901015`  
**Ámbito:** Scenario Engine para hipótesis controladas  

## 1. Propósito

Definir el contrato mínimo de un Scenario Engine que permita crear y versionar hipótesis de simulación sin modificar la operación real, sus evidencias, reglas, parámetros estructurales ni resultados históricos.

## 2. Frontera

O2 transforma una operación/resultado base y un conjunto de cambios autorizados en una representación versionada de escenario.

O2 **no** decide, recomienda, compra, negocia, puntúa alternativas ni sustituye CRC, Decision Twin u O1.

## 3. Entrada conceptual

`ScenarioBase + AuthorizedScenarioChanges + DecisionContext`

Cada cambio debe identificar:

- variable;
- valor base;
- valor simulado;
- unidad cuando aplique;
- autorización;
- origen.

## 4. Salida conceptual

`ScenarioVersion` debe conservar, como mínimo:

- `scenario_id`;
- `parent_scenario_id` cuando exista;
- `decision_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`;
- conjunto ordenado de cambios;
- fingerprint determinista;
- estado de evaluación, inicialmente independiente del resultado de negocio.

## 5. Invariantes

1. Un escenario no muta su escenario padre.
2. Crear un escenario no modifica `PurchaseOperation`.
3. Crear un escenario no modifica evidencias, reglas ni parámetros estructurales.
4. Cambios no autorizados deben rechazarse explícitamente.
5. `NOT_EVALUABLE` no puede convertirse en resultado negativo por ausencia de datos.
6. La identidad y el versionado del contexto deben preservarse.
7. El orden de entrada no debe alterar el fingerprint de un mismo conjunto de cambios.
8. El escenario es una hipótesis, no una decisión empresarial.
9. La creación/versionado del escenario no ejecuta automáticamente capacidades analíticas no incluidas en O2.
10. No se introduce scoring ni ranking decisional.

## 6. Estados

- `DRAFT`: hipótesis creada pero no validada.
- `VALID`: cambios autorizados y contexto coherente.
- `INVALID`: la hipótesis incumple el contrato.
- `EVALUATED`: reservado para una futura integración explícita; no implica cálculo dentro de O2.

## 7. Determinismo

Para el mismo contexto y el mismo conjunto normalizado de cambios, la representación canónica y su fingerprint deben ser idénticos.

La identidad debe distinguir escenarios materialmente diferentes y permitir reconstruir su linaje.

## 8. Separación con O1

O1 orquesta resultados ya producidos y construye el `DecisionSupportPackage`. O2 crea la representación controlada de hipótesis que podrá ser consumida posteriormente por capacidades autorizadas.

O2 no altera el contrato cerrado de O1.

## 9. Criterio de cierre

El diseño solo podrá pasar a implementación cuando la auditoría confirme que:

- la autoridad permanece en el decisor humano;
- no existe mutación de datos reales;
- identidad/versionado son suficientes;
- la normalización es determinista;
- la frontera con O1, Twin, CRC y capacidades analíticas es inequívoca.

**Siguiente etapa obligatoria:** AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
