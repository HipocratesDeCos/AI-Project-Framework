# EIOS — O3 · DISEÑO DE EVALUACIÓN CONTROLADA DE ESCENARIOS

**Estado:** DISEÑO — NO IMPLEMENTADO
**Baseline:** `81742aa7eab2edaa4eadd6d1888922e420d4ece4`
**Rama:** `design/o3-scenario-evaluation`

## 1. Objetivo

Definir, sin implementación todavía, una integración controlada que permita pasar de un `ScenarioVersion` válido a resultados reevaluados por las autoridades analíticas existentes.

O3 no crea un nuevo motor de reglas ni un nuevo motor de viabilidad.

## 2. Problema que resuelve

O2 materializa hipótesis versionadas, pero su contrato reserva `EVALUATED` para una futura integración explícita. La evaluación posterior no debe introducirse implícitamente dentro de O2.

O3 estudiará esa frontera de forma separada.

## 3. Flujo propuesto

```text
ScenarioVersion VALID
        ↓
contexto/versiones preservados
        ↓
evaluación autorizada
        ↓
Assessment existentes
        ↓
Viability Frontier existente
        ↓
Scenario Evaluation Result
```

La evaluación no modifica el escenario, la operación real, las evidencias originales, las reglas ni los parámetros.

## 4. Autoridades

- `Scenario Engine`: identidad, linaje y representación del escenario.
- `Assessment`: evaluación individual de reglas.
- `Viability Frontier`: determinación de viabilidad.
- `QTG`: controles de calidad cuando contractual y funcionalmente corresponda.
- `Decision Twin`: comparación descriptiva posterior.
- `O1/O2`: conservan sus fronteras actuales.
- Decisor humano: única autoridad sobre la decisión empresarial.

Ningún componente O3 podrá seleccionar, comprar, aprobar, rechazar, negociar, puntuar u optimizar.

## 5. Entrada mínima candidata

O3 deberá consumir únicamente:

- un `ScenarioVersion` válido;
- `DecisionContext` asociado;
- reglas y parámetros ya autorizados;
- evidencia autorizada disponible;
- dependencias canónicas existentes.

No se crearán versiones paralelas de reglas, parámetros, evidencia, snapshot o decisión.

## 6. Salida mínima candidata

La salida deberá distinguir como mínimo:

- escenario evaluado;
- estado técnico de evaluación;
- resultados de `Assessment` producidos;
- resultado de `Viability Frontier` cuando sea evaluable;
- limitaciones o elementos no evaluables;
- referencias de trazabilidad compatibles;
- contexto/versiones utilizados.

Un resultado ausente, `NOT_EVALUABLE` o fallo técnico nunca se reinterpretará como resultado empresarial negativo.

## 7. EVALUATED

`EVALUATED` solo podrá utilizarse cuando exista evidencia de que la evaluación contractual completa del alcance O3 terminó correctamente.

No significará `VIABLE`, `COMPRAR`, `NEGOCIAR` ni ninguna otra decisión empresarial.

## 8. Inmutabilidad

La evaluación debe ser derivada y no mutante:

```text
OPERACIÓN REAL       → no modificar
SCENARIO VERSION     → no modificar
EVIDENCE              → no modificar
RULES                 → no modificar
PARAMETERS            → no modificar
ASSESSMENTS HISTÓRICOS→ no modificar
```

Los nuevos resultados constituirán resultados de la evaluación del escenario, no sustituciones silenciosas de resultados históricos.

## 9. Determinismo y reproducibilidad

La evaluación deberá conservar el `DecisionContext` del escenario y las referencias de entrada necesarias para reconstruir qué se evaluó.

No se definirá todavía un nuevo fingerprint hasta demostrar que el existente de C0/O2 no es suficiente para el alcance concreto.

## 10. Fuera de alcance

Este diseño no autoriza todavía:

- generación automática de escenarios;
- búsqueda exhaustiva;
- optimización;
- ranking;
- selección;
- recomendación empresarial;
- negociación automática;
- persistencia;
- API;
- cambios SQL;
- modificación de `DecisionContext`;
- modificación del contrato O2.

## 11. Preguntas de auditoría obligatorias

Antes de pasar a implementación deberán resolverse explícitamente:

1. ¿Qué evaluadores concretos se consideran parte de O3?
2. ¿Cómo se representa un resultado parcial sin contaminar `EVALUATED`?
3. ¿Cómo se preserva la identidad y trazabilidad sin crear un segundo sistema de versionado?
4. ¿Cómo se evita mutar resultados históricos?
5. ¿Qué evidencia puede reutilizarse y cuál requiere nueva referencia?
6. ¿Cómo se distingue fallo técnico de resultado de negocio?
7. ¿La salida debe ser consumible por O1 sin ampliar su autoridad?
8. ¿Qué pruebas mínimas demuestran estas fronteras?

## 12. Criterio de avance

O3 no avanzará a implementación hasta completar:

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**

Este documento materializa únicamente la etapa **DISEÑAR** y no modifica `main`.