# EIOS — Quality & Trust Implementation Contract

## 1. Identidad

**Documento:** Quality & Trust Implementation Contract  
**Versión:** 0.4  
**Estado:** CERRADO  
**Baseline de referencia:** EIOS-BL-001  
**Autoridad conceptual:** `03_Arquitectura/Architecture_Blueprint.md`  
**Arquitectura funcional:** `03_Arquitectura/DSS_Functional_Architecture.md`

---

## 2. Propósito

Define la frontera técnica mínima para materializar `Quality & Trust Gate` como capacidad de control previo a la evaluación analítica.

No constituye un motor de decisión ni una autoridad sobre reglas, parámetros, viabilidad, negociación, CRC o decisión empresarial.

Su función es determinar si el conjunto de entrada dispone de calidad y confianza suficientes para continuar hacia las capas posteriores, preservando las incertidumbres y contradicciones relevantes.

---

## 3. Autoridad y precedencia

La arquitectura estructural reconoce `Quality & Trust Gate` como capacidad Core.

La arquitectura funcional lo sitúa inmediatamente después del `Decision Input Package` y antes de las capas analíticas.

La definición de criterios generales de evidencia permanece bajo `04_Reglas/Evidence_Contract.md`.

Las dependencias concretas de reglas permanecen bajo `04_Reglas/Rule_Dependency_Matrix.md`.

Este contrato no sustituye ninguna de esas autoridades.

---

## 4. Entrada

La implementación recibe una representación de `Decision Input Package` ya identificada y trazable.

El contrato no crea un nuevo repositorio de datos ni redefine `InputContract`, `DecisionContext`, `Evidence` o `Trace`.

La entrada debe permitir identificar, cuando corresponda:

- datos de la propuesta;
- evidencia asociada;
- datos empresariales disponibles;
- parametrización vigente disponible;
- identidad contextual de la evaluación.

---

## 5. Controles mínimos

La implementación deberá poder evaluar, según disponibilidad y aplicabilidad:

- existencia;
- integridad;
- validez;
- consistencia interna;
- consistencia entre fuentes;
- temporalidad;
- semántica;
- trazabilidad;
- contradicciones críticas;
- modificaciones humanas relevantes.

La mera presencia de un campo no implica que el dato sea fiable.

---

## 6. Estados de salida

Los estados funcionales autorizados son exclusivamente:

```text
APTO
APTO_CON_ADVERTENCIAS
NO_APTO
```

No se introducen estados adicionales por implementación.

La salida de Quality & Trust no es una evaluación de regla y no equivale a `TRUE` o `FALSE`.

---

## 7. Confianza

La representación funcional reconoce tres niveles:

```text
ALTA
MEDIA
BAJA
```

La implementación no debe convertir un nivel de confianza en una decisión empresarial.

La confianza se determina cualitativamente mediante la matriz normativa de este contrato; no se utilizarán fórmulas, pesos, scores ni promedios salvo que una especificación posterior los autorice expresamente.

### 7.1 Criterios cualitativos

**ALTA** requiere, como mínimo:

- condiciones críticas evaluables y satisfechas;
- evidencia suficiente para las condiciones aplicables;
- ausencia de contradicciones críticas no resueltas;
- temporalidad y semántica suficientes para el uso previsto;
- trazabilidad suficiente del conjunto evaluado;
- ausencia de limitaciones relevantes que deban comunicarse como advertencia.

**MEDIA** corresponde cuando no existe una deficiencia crítica que impida continuar, pero existe al menos una limitación relevante no crítica, incertidumbre acotada o advertencia que reduce la solidez del conjunto.

**BAJA** corresponde cuando existen limitaciones relevantes de evidencia, temporalidad, consistencia, trazabilidad u otras propiedades de calidad que reducen materialmente la fiabilidad, aunque el resultado global no quede necesariamente bloqueado.

La confianza debe poder explicarse mediante las condiciones observadas; no constituye una puntuación empresarial.

---

## 8. Incertidumbre y ausencia

La implementación no puede convertir silenciosamente:

```text
ausencia → 0
ausencia → FALSE
incertidumbre → certeza
contradicción → valor único arbitrario
```

Una deficiencia crítica debe conservarse como condición explícita del resultado de Quality & Trust.

La semántica `GAP ≠ FALSE` del Evidence Contract permanece intacta.

---

## 9. Matriz normativa de estado global

La determinación del estado global utiliza precedencia cualitativa y no scoring.

### 9.1 Definición de condición crítica

Una condición es **crítica** cuando su incumplimiento, ausencia no evaluable o contradicción impide considerar suficientemente fiable una condición necesaria para continuar el procesamiento analítico, o cuando puede alterar materialmente la interpretación del conjunto de entrada.

La criticidad se atribuye al hallazgo concreto y a su contexto de aplicabilidad; ningún control se considera universalmente crítico por su mera identidad.

### 9.2 Precedencia

La precedencia normativa es:

```text
NO_APTO
    >
APTO_CON_ADVERTENCIAS
    >
APTO
```

Se aplica de la siguiente manera:

| Condición observada | Estado global |
|---|---|
| Existe al menos una condición crítica no satisfecha, no evaluable o una contradicción crítica no resuelta que afecta a una condición necesaria | `NO_APTO` |
| No existe condición crítica bloqueante, pero existe al menos una limitación o incidencia relevante no crítica | `APTO_CON_ADVERTENCIAS` |
| No existen incidencias relevantes y las condiciones aplicables se encuentran suficientemente satisfechas | `APTO` |

### 9.3 Ausencia de información crítica

Cuando una condición crítica necesaria no pueda evaluarse por ausencia de información suficiente, la ausencia **no se interpreta como cumplimiento**.

Si esa ausencia impide considerar fiable el conjunto para continuar, el estado global será `NO_APTO`.

Si la información ausente no es crítica para la continuación, podrá constituir una advertencia según corresponda.

### 9.4 Contradicciones

Una contradicción crítica no resuelta que afecte a una condición necesaria conduce a `NO_APTO`.

Una contradicción no crítica que no impida continuar conduce, como máximo, a `APTO_CON_ADVERTENCIAS`.

Quality & Trust no resuelve la contradicción mediante prioridad arbitraria, promedio, último valor, score u otra heurística no autorizada.

### 9.5 Combinaciones estado/confianza

Para evitar ambigüedad, las combinaciones normativas se restringen así:

| Estado global | Confianza autorizada | Criterio |
|---|---|---|
| `APTO` | `ALTA` | Condiciones aplicables satisfechas, sin limitaciones relevantes ni advertencias pendientes. |
| `APTO_CON_ADVERTENCIAS` | `MEDIA` o `BAJA` | No existe bloqueo crítico, pero sí una o más limitaciones relevantes no críticas. |
| `NO_APTO` | `BAJA` | Existe insuficiencia o condición crítica que impide continuar con confianza suficiente. |

No se autoriza `APTO + MEDIA`, porque la existencia de una limitación relevante incompatible con `ALTA` debe reflejarse en el estado mediante `APTO_CON_ADVERTENCIAS`.

No se autoriza `APTO + BAJA`.

No se autoriza `NO_APTO + ALTA` ni `NO_APTO + MEDIA`.

La matriz es normativa y determinista; no constituye scoring.

---

## 10. Contradicciones

Cuando existan fuentes contradictorias, la contradicción debe conservarse y hacerse visible.

Quality & Trust no resuelve mediante prioridad arbitraria, promedio, último valor, score u otra heurística no autorizada.

La resolución de conflictos entre resultados de reglas pertenece a `Capa_resolucion_conflictos.md` y CRC según corresponda.

---

## 11. Evidencia

Quality & Trust puede comprobar propiedades de calidad, integridad, consistencia y trazabilidad de la evidencia disponible.

No redefine los criterios generales de admisibilidad del `Evidence Contract`.

No determina qué evidencia concreta necesita una regla; esa responsabilidad permanece en la RDM y en las autoridades de reglas.

No modifica objetos `Evidence` ni genera un segundo sistema de evidencia.

---

## 12. Relación con C0

Quality & Trust precede funcionalmente al procesamiento analítico, pero no sustituye C0.

No modifica:

- `InputContract`;
- `DecisionContext`;
- `Evidence`;
- `EvidenceValidation`;
- `Rule`;
- `Assessment`;
- `Trace`.

---

## 13. Criterios de cierre

El contrato se considera cerrado cuando:

- los estados y confianza están limitados a los valores autorizados;
- la precedencia es determinista;
- la incertidumbre y ausencia no se convierten silenciosamente en certeza;
- las contradicciones no se resuelven mediante heurísticas no autorizadas;
- QTG no adquiere autoridad sobre reglas, parámetros, evidencia, C0 o decisión empresarial;
- la implementación y los tests reflejan estas invariantes;
- la CI del repositorio resulta satisfactoria.

**Estado de cierre:** CERRADO.
