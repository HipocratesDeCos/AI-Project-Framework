# EIOS — O4 → O2 → O3 · DISEÑO DE INTEGRACIÓN DE EVALUACIÓN

**Estado:** 🔎 DISEÑO — PENDIENTE DE AUDITORÍA
**Tipo de cambio:** Diseño funcional/técnico controlado
**Baseline:** `accbfa6f7e59b5070539d86a6e65f1ba28653e52`

## 1. Propósito

Definir, sin materializar implementación, la frontera mínima para encadenar candidatos generados por O4 con el versionado controlado de O2 y la evaluación de O3.

El objetivo es permitir que un candidato estructuralmente generado pueda convertirse en un `ScenarioVersion` autorizado y, posteriormente, ser evaluado mediante O3, sin introducir autoridad empresarial nueva.

## 2. Secuencia propuesta

```text
O4
  ↓ candidatos estructurales
O2
  ↓ ScenarioVersion válido
O3
  ↓ ScenarioEvaluationResult
Assessment / Viability Frontier
  ↓ resultados existentes
Resultado de escenario
```

La integración no convierte por sí misma un escenario en alternativa empresarial, recomendación o decisión.

## 3. Responsabilidades

### O4

- Genera candidatos deterministas y finitos.
- Mantiene sus estados técnicos propios.
- No crea identidad/versionado definitivo del escenario.
- No ejecuta O2 ni O3 internamente.

### O2

- Recibe únicamente candidatos compatibles con su contrato de cambios autorizados.
- Crea/versiona la hipótesis mediante su autoridad existente.
- Conserva identidad, lineage, contexto y fingerprint conforme a su contrato.
- No evalúa viabilidad ni selecciona candidatos.

### O3

- Recibe un `ScenarioVersion` válido y el contexto asociado.
- Consume resultados analíticos ya producidos por las autoridades correspondientes.
- Produce `ScenarioEvaluationResult` sin mutar el escenario.
- No selecciona, recomienda, aprueba, rechaza ni negocia.

## 4. Frontera de estados O4

Los estados de O4 se propagan sin reinterpretación empresarial:

- `GENERATED` → candidatos elegibles para procesamiento por O2.
- `EMPTY` → no hay candidato que entregar.
- `BLOCKED` → la generación no puede continuar; no se crea escenario.
- `NOT_EVALUABLE` → no puede determinarse de forma segura el espacio; no se crea escenario.
- `FAILED` → fallo técnico con causa; no se crea escenario a partir del resultado fallido.

La integración no convierte estados técnicos en `VIABLE`, `NOT_VIABLE`, `COMPRAR` ni equivalentes.

## 5. Frontera O4 → O2

Solo candidatos `GENERATED` pueden proponerse a O2.

La integración debe conservar:

- contexto autorizado;
- escenario padre cuando exista;
- cambios canónicos;
- política de generación versionada;
- referencias necesarias para trazabilidad.

O2 mantiene la decisión contractual sobre si los cambios son válidos y autorizados.

Un rechazo de O2 produce un resultado técnico de integración y no una conclusión empresarial.

## 6. Frontera O2 → O3

Solo un `ScenarioVersion` válido puede entrar en O3.

Debe conservarse la correspondencia entre:

```text
candidato O4 → ScenarioVersion O2 → ScenarioEvaluationResult O3
```

El contexto de decisión, `rules_version`, `parameters_version` y `data_snapshot_id` deben permanecer coherentes con las autoridades existentes.

No se crea `decision_version` ni identidad paralela.

## 7. Evaluación

O3 no ejecuta automáticamente motores analíticos que no le correspondan.

Para producir un resultado completo, debe recibir los resultados requeridos de Assessment y Viability Frontier conforme al contrato O3 vigente.

La integración puede transportar o solicitar esos resultados únicamente mediante una futura interfaz explícitamente definida; este documento no autoriza API, persistencia ni SQL.

## 8. Cardinalidad y ejecución

Un lote de candidatos puede contener cero, uno o varios candidatos `GENERATED`.

La integración no puede:

- truncar silenciosamente candidatos;
- seleccionar los mejores;
- rankear;
- puntuar;
- optimizar;
- eliminar candidatos por rentabilidad o preferencia empresarial.

El orden de procesamiento no constituye ranking ni preferencia.

## 9. Trazabilidad

Debe ser posible reconstruir:

```text
contexto
  → generación O4
  → candidato
  → versionado O2
  → evaluación O3
  → resultados Assessment / Viability
```

La integración no crea un sistema paralelo de identidad, fingerprint o trace.

## 10. Errores y resultados parciales

Un fallo en un candidato no debe reinterpretarse automáticamente como fallo empresarial de la operación completa.

La semántica de `PARTIALLY_COMPLETED`, `NOT_EVALUABLE` y `FAILED` permanece bajo O3 cuando corresponda.

La integración debe conservar la distinción entre:

```text
fallo técnico ≠ resultado empresarial negativo
no evaluable ≠ no viable
completado ≠ comprar
```

## 11. Exclusiones

Este diseño no autoriza:

- ranking;
- scoring;
- selección automática;
- recomendación;
- optimización;
- negociación automática;
- decisión empresarial;
- persistencia nueva;
- API nueva;
- SQL nuevo;
- modificación de reglas o parámetros;
- acceso directo del flujo O4 a fuentes empresariales no definidas por sus contratos.

## 12. Punto pendiente

Antes de cualquier implementación deben auditarse especialmente:

1. contrato exacto del adaptador O4 → O2;
2. representación del candidato y cambios autorizados;
3. manejo de lotes y errores individuales;
4. correspondencia de identidad y lineage;
5. condiciones exactas de entrada O3;
6. transporte de Assessment y Viability Frontier;
7. trazabilidad extremo a extremo;
8. ausencia de selección o autoridad empresarial implícita.

**No se autoriza implementación hasta completar Auditoría 1, Depuración y Auditoría 2.**
