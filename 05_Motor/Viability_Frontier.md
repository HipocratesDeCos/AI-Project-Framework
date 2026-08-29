# VIABILITY FRONTIER

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Contrato documental
**Tipo de cambio:** Documentación exclusivamente
**Baseline de diseño:** EIOS Vertical MVP

---

## 1. Propósito

`Viability Frontier` es el componente especializado que determina el resultado base de viabilidad de una operación a partir de las restricciones de viabilidad ya autorizadas y de los resultados individuales de evaluación disponibles.

Su función es determinar la posición de la operación respecto de la frontera de viabilidad. No constituye un segundo motor de reglas, un motor de resolución de conflictos, un motor de escenarios, un motor de negociación ni una autoridad de decisión empresarial.

---

## 2. Posición arquitectónica

```text
DATOS / PARÁMETROS / ANÁLISIS
            ↓
          REGLAS
            ↓
        ASSESSMENT
            ↓
   VIABILITY FRONTIER
            ↓
    RESULTADO BASE
            ↓
   SCENARIO ENGINE
            ↓
   DECISION TWIN / NEGOCIACIÓN
            ↓
           CRC
            ↓
      RECOMENDACIÓN
            ↓
         DECISOR
```

La Frontier se sitúa después de la evaluación individual de reglas y antes de la generación de escenarios. La resolución consolidada de conflictos permanece fuera de su autoridad.

---

## 3. Autoridad

La Frontier no crea autoridad normativa propia.

Las restricciones, condiciones, efectos, severidades y resultados de las reglas pertenecen a la documentación oficial de reglas.

`Assessment` es el resultado individual de evaluar una regla y constituye la entrada evaluativa de la Frontier.

La RDM conserva exclusivamente su función como matriz de dependencias demostradas entre reglas.

La evidencia permanece bajo el contrato de evidencia y vinculada a la evaluación individual correspondiente.

La CRC conserva la autoridad para resolver conflictos, consolidar resultados incompatibles y realizar la resolución posterior que corresponda.

---

## 4. Entrada conceptual

La Frontier puede utilizar:

- resultados `Assessment` ya producidos;
- identificadores de las reglas correspondientes;
- contexto de la operación necesario para interpretar la frontera;
- restricciones de viabilidad previamente autorizadas por la documentación normativa existente.

La Frontier no determina por sí misma qué reglas son aplicables, no modifica sus condiciones y no crea restricciones nuevas.

---

## 5. Resultado base

La Frontier puede producir el resultado base de viabilidad definido por la arquitectura:

- `VIABLE`
- `VIABLE CON CONDICIONES`
- `NOT_VIABLE`
- `NOT_EVALUABLE`

Estos estados no constituyen recomendaciones empresariales de compra.

En particular:

```text
VIABLE ≠ COMPRAR
VIABLE CON CONDICIONES ≠ COMPRAR CONDICIONADO
NOT_EVALUABLE ≠ NOT_VIABLE
```

`NOT_EVALUABLE` no debe utilizarse como sinónimo de una conclusión desfavorable cuando no existe base evaluativa suficiente.

`NOT_VIABLE` requiere una base evaluativa suficiente y una restricción de viabilidad cuya consecuencia de frontera esté normativamente determinada.

---

## 6. Determinación de frontera

La responsabilidad de la Frontier queda limitada a determinar la posición de la operación respecto de restricciones de viabilidad cuya autoridad ya exista.

No se establece en este contrato una regla general que traduzca automáticamente `R0`, `R1`, `R2` o `R3` en un estado de viabilidad.

Tampoco se establece que una severidad concreta implique por sí misma `NOT_VIABLE`.

El efecto de una regla y su severidad permanecen en la definición normativa de la regla.

---

## 7. Agregación y conflictos

**PENDIENTE DE ESPECIFICACIÓN:** no existe en este contrato una política general de agregación de múltiples resultados `Assessment` cuando su interacción requiera una regla adicional de resolución.

La Frontier no introduce:

- puntuaciones de viabilidad;
- ponderaciones;
- compensaciones automáticas;
- prioridades propias;
- umbrales globales no autorizados;
- jerarquías de resolución nuevas;
- reglas de precedencia propias.

Cuando la determinación requiera resolver conflictos o interacciones cuya política corresponda a una autoridad posterior o todavía no esté especificada, la Frontier no inventará dicha política.

La autoridad existente de resolución y consolidación de conflictos permanece en `CRC`.

---

## 8. Separación respecto de Assessment

`Assessment` representa exclusivamente el resultado individual de evaluar una regla.

La Frontier no vuelve a evaluar la regla ni modifica el significado de:

```text
EVALUABLE     → TRUE | FALSE
NOT_EVALUABLE → None
```

La ausencia de evidencia no se convierte automáticamente en `FALSE` ni en `NOT_VIABLE`.

---

## 9. Separación respecto de Evidence

La Frontier no constituye un repositorio alternativo de evidencia.

La evidencia que sustenta una evaluación permanece vinculada al `Assessment` correspondiente y puede ser recuperada mediante la cadena de trazabilidad autorizada.

No se introduce una segunda autoridad sobre admisibilidad, suficiencia o trazabilidad de evidencia.

---

## 10. Separación respecto de Scenario Engine

La Frontier no crea ni modifica escenarios.

El `Scenario Engine` recibe el resultado base y desarrolla las hipótesis o alternativas que correspondan conforme a su propia autoridad.

La Frontier no optimiza, compara ni selecciona escenarios.

---

## 11. Separación respecto de CRC

La Frontier no sustituye a la Capa de Resolución de Conflictos.

En particular, no realiza por sí misma:

- resolución de conflictos entre reglas;
- aplicación de la jerarquía de resolución de CRC;
- consolidación de recomendaciones incompatibles;
- determinación del motivo dominante de una recomendación final;
- generación de una recomendación empresarial.

La existencia de una situación desfavorable o condicionada no autoriza a la Frontier a emitir `COMPRAR`, `NEGOCIAR`, `COMPRAR CONDICIONADO` o `NO COMPRAR` como recomendación empresarial.

---

## 12. Separación respecto de negociación y decisión

La Frontier no negocia condiciones, no genera estrategias de negociación y no ejecuta decisiones empresariales.

Una operación `VIABLE CON CONDICIONES` no implica por sí misma una instrucción de negociación ni una orden de compra.

La recomendación y la decisión permanecen en las capas posteriores y bajo control humano conforme a la arquitectura autorizada.

---

## 13. Trazabilidad

Todo resultado de Frontier debe conservar trazabilidad hacia los resultados individuales y las reglas que sustentan la determinación, sin duplicar la autoridad de Evidence.

La cadena conceptual es:

```text
Viability Result
      ↓
Assessment
      ↓
Rule
      ↓
Evidence
```

La trazabilidad no modifica las responsabilidades de cada capa.

---

## 14. Elementos expresamente no definidos por este contrato

Este contrato no define:

- nuevas reglas de negocio;
- nuevos parámetros;
- nuevos umbrales;
- fórmulas de viabilidad;
- `Viability Score`;
- ponderaciones;
- mecanismos de compensación;
- una jerarquía paralela a CRC;
- una política general de agregación de múltiples `Assessment`;
- escenarios;
- negociación;
- recomendaciones;
- decisiones de compra.

Cualquier elemento de esta lista que requiera especificación futura deberá ser autorizado documentalmente antes de convertirse en comportamiento técnico.

---

## 15. Estado de especificación

```text
DOMINIO DE VIABILIDAD                  AUTORIZADO
POSICIÓN ARQUITECTÓNICA                AUTORIZADO
ESTADOS DE VIABILIDAD                  AUTORIZADO
ENTRADA DESDE ASSESSMENT               AUTORIZADO
TRAZABILIDAD                           AUTORIZADO
SEPARACIÓN DE EVIDENCE                 AUTORIZADO
SEPARACIÓN DE SCENARIO ENGINE          AUTORIZADO
SEPARACIÓN DE CRC                      AUTORIZADO

AGREGACIÓN GENERAL DE ASSESSMENTS      PENDIENTE DE ESPECIFICACIÓN
FÓRMULAS DE VIABILIDAD                 PENDIENTE / NO DEFINIDO
UMBRAL GLOBAL DE VIABILIDAD            PENDIENTE / NO DEFINIDO
POLÍTICAS ADICIONALES DE CONFLICTO     PENDIENTE / NO DEFINIDO
```

---

## 16. Cierre del contrato

Este documento materializa exclusivamente el diseño contractual cerrado de `Viability Frontier`.

La materialización de este contrato **no introduce cambios técnicos** y no implica modificaciones en:

- `models.py`;
- `validation.py`;
- tests;
- reglas existentes;
- parámetros;
- C0;
- CRC;
- Scenario Engine.

Cualquier implementación futura deberá respetar este perímetro y no podrá convertir los elementos marcados como `PENDIENTE DE ESPECIFICACIÓN` en comportamiento implícito.
