# EIOS — O2 · CONTRATO SCENARIO ENGINE

**Estado:** CERRADO — MATERIALIZADO — CI PENDIENTE  
**Baseline de entrada:** `06e8270545f57c904f99229430a9be4575901015`  
**HEAD materializado:** `5693404be449dece4ddb0dad8c5ebd19667d2b8b`  
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

En la creación/versionado actual de O2 solo se producen `DRAFT`, `VALID` e `INVALID`. `EVALUATED` permanece reservado a una futura integración contractual explícita.

## 7. Determinismo

Para el mismo contexto y el mismo conjunto normalizado de cambios, la representación canónica y su fingerprint deben ser idénticos.

La identidad debe distinguir escenarios materialmente diferentes y permitir reconstruir su linaje.

## 8. Separación con O1

O1 orquesta resultados ya producidos y construye el `DecisionSupportPackage`. O2 crea la representación controlada de hipótesis que podrá ser consumida posteriormente por capacidades autorizadas.

O2 no altera el contrato cerrado de O1.

## 9. Criterio de cierre

El diseño ha sido auditado, depurado, sometido a Auditoría 2 y materializado conforme al alcance definido. La implementación preserva:

- la autoridad en el decisor humano;
- la no mutación de datos reales;
- identidad y versionado suficientes;
- normalización determinista;
- frontera inequívoca con O1, Twin, CRC y capacidades analíticas.

La evidencia CI específica del HEAD materializado aún no está disponible; por ello el contrato queda **cerrado y materializado, pero pendiente de validación CI**.

**Secuencia:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
