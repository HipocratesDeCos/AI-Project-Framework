# EIOS — O3 · DEPURACIÓN DE EVALUACIÓN CONTROLADA DE ESCENARIOS

**Estado:** DEPURADO
**Baseline:** `81742aa7eab2edaa4eadd6d1888922e420d4ece4`
**Diseño:** `79e28522c09b4c0a7b2ce40ce16641b4a4478b6d`

## 1. Corrección principal

O3 no convertirá `ScenarioVersion.status` en `EVALUATED` como efecto colateral de una operación parcial.

`EVALUATED` queda reservado exclusivamente para una evaluación contractual completa del alcance O3 y no representa ningún resultado empresarial.

## 2. Estado técnico de evaluación

La evaluación O3 debe separar:

```text
NOT_STARTED
RUNNING
COMPLETED
PARTIALLY_COMPLETED
NOT_EVALUABLE
FAILED
```

La semántica es técnica. Ninguno de estos estados equivale a una decisión empresarial.

## 3. Completitud

`COMPLETED` solo podrá utilizarse cuando todas las evaluaciones incluidas en el alcance contractual de esa ejecución hayan terminado sin elementos pendientes que impidan declarar completitud.

`PARTIALLY_COMPLETED` se utilizará cuando existan resultados válidos pero queden evaluaciones o dependencias pendientes.

`NOT_EVALUABLE` se utilizará cuando la base disponible no permita producir una evaluación válida.

`FAILED` representa fallo técnico y requiere una causa explícita; no equivale a `FALSE`, `NOT_VIABLE` ni `NO_COMPRAR`.

## 4. EVALUATED

La marca `EVALUATED` del escenario solo podrá establecerse después de una ejecución O3 `COMPLETED` y únicamente si el contrato de integración que finalmente se apruebe define que dicha marca forma parte de la representación persistente.

Por ahora, este diseño no modifica O2 ni elimina su reserva de `EVALUATED`.

## 5. Evidence

La evidencia existente puede reutilizarse como entrada cuando siga siendo válida para el contexto del escenario.

El escenario no puede alterar el contenido de evidencia ni convertir una hipótesis en evidencia.

Si la hipótesis requiere nueva evidencia, su ausencia se representa como insuficiencia evaluativa; no se inventa evidencia ni se sustituye silenciosamente.

## 6. Assessment

Los nuevos resultados de evaluación son nuevos resultados derivados del escenario. No sobrescriben Assessment históricos.

La semántica continúa siendo:

```text
EVALUABLE     → TRUE | FALSE
NOT_EVALUABLE → None
```

## 7. Viability Frontier

O3 podrá consumir el resultado de `Assessment` y solicitar/determinar el resultado de `Viability Frontier` solo dentro de la integración contractual aprobada.

O3 no replica ninguna lógica de frontera. `VIABLE`, `VIABLE CON CONDICIONES`, `NOT_VIABLE` y `NOT_EVALUABLE` siguen perteneciendo a Frontier.

## 8. Versionado

O3 conservará el `DecisionContext` ya asociado al escenario:

```text
decision_id
scenario_id
rules_version
parameters_version
data_snapshot_id
```

No se crea `decision_version`, ni un fingerprint paralelo de decisión, ni una nueva autoridad de snapshot.

Un futuro identificador específico de evaluación solo podrá introducirse si la implementación demuestra que es necesario para distinguir ejecuciones sin duplicar Decision Versioning.

## 9. Resultado parcial

La salida parcial no puede degradarse a un resultado empresarial.

```text
PARTIALLY_COMPLETED ≠ NOT_VIABLE
NOT_EVALUABLE ≠ NOT_VIABLE
FAILED ≠ NOT_VIABLE
```

## 10. Frontera con O1

O3 puede producir resultados consumibles por O1 únicamente mediante los contratos existentes de resultado y adaptación.

No se modifica O1 por anticipación ni se crea un E2E obligatorio entre todas las capacidades.

## 11. Fuera de alcance reafirmado

No se autoriza con esta depuración:

- generación automática de escenarios;
- ranking;
- scoring;
- optimización;
- selección;
- recomendación;
- negociación automática;
- decisión empresarial;
- persistencia SQL;
- API.

## 12. Resultado de depuración

Los tres puntos detectados en Auditoría quedan resueltos conceptualmente:

1. `EVALUATED` queda condicionado a completitud contractual.
2. Parcial/no evaluable/fallo quedan separados de resultados de negocio.
3. Evidencia y resultados históricos permanecen inmutables y trazables.

La siguiente etapa es **AUDITORÍA 2**, antes de cualquier implementación.