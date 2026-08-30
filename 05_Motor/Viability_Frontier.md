# VIABILITY FRONTIER

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.1  
**Estado:** CERRADO — Contrato documental  
**Tipo de cambio:** Documentación exclusivamente  
**Baseline de diseño:** EIOS Vertical MVP

---

# 1. Propósito

`Viability Frontier` es el componente especializado que determina el resultado base de viabilidad de una operación a partir de las restricciones de viabilidad ya autorizadas y de los resultados individuales de evaluación disponibles.

Su función es determinar la posición de la operación respecto de la frontera de viabilidad. No constituye un segundo motor de reglas, un motor de resolución de conflictos, un motor de escenarios, un motor de negociación ni una autoridad de decisión empresarial.

---

# 2. Posición arquitectónica

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

# 3. Autoridad

La Frontier no crea autoridad normativa propia.

Las restricciones, condiciones, efectos, severidades y resultados de las reglas pertenecen a la documentación oficial de reglas.

`Assessment` es el resultado individual de evaluar una regla y constituye la entrada evaluativa de la Frontier.

La RDM conserva exclusivamente su función como matriz de dependencias demostradas entre reglas.

La evidencia permanece bajo el contrato de evidencia y vinculada a la evaluación individual correspondiente.

La CRC conserva la autoridad para resolver conflictos, consolidar resultados incompatibles y realizar la resolución posterior que corresponda.

---

# 4. Entrada conceptual

La Frontier puede utilizar:

- resultados `Assessment` ya producidos;
- identificadores de las reglas correspondientes;
- contexto de la operación necesario para interpretar la frontera;
- restricciones de viabilidad previamente autorizadas por la documentación normativa existente.

La Frontier no determina por sí misma qué reglas son aplicables, no modifica sus condiciones y no crea restricciones nuevas.

---

# 5. Resultado base

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

# 6. Determinación de frontera

La responsabilidad de la Frontier queda limitada a determinar la posición de la operación respecto de restricciones de viabilidad cuya autoridad ya exista.

No se establece una regla que traduzca automáticamente `R0`, `R1`, `R2` o `R3` en un estado de viabilidad. La consecuencia de frontera debe estar explícitamente autorizada por la documentación normativa aplicable.

Tampoco se establece que una severidad concreta implique por sí misma `NOT_VIABLE`.

El efecto de una regla y su severidad permanecen en la definición normativa de la regla.

La Frontier no puede inferir una restricción de viabilidad a partir de:

- un `Assessment` desfavorable considerado aisladamente;
- la severidad;
- la `Criticality` de una dependencia;
- un `GAP` de evidencia;
- el número de resultados desfavorables;
- la existencia de una regla R0/R1/R2/R3 sin consecuencia de frontera explícitamente autorizada.

---

# 7. Modelo formal de frontera

La determinación de frontera se define conceptualmente mediante cuatro clases de resultado:

```text
H = restricción dura autorizada
K = condición de viabilidad autorizada
U = base materialmente insuficiente para concluir
S = señal o información sin consecuencia propia de frontera
```

Estas clases no sustituyen a los códigos normativos de las reglas. Representan únicamente la función que un resultado autorizado puede desempeñar en la determinación de frontera.

## 7.1 Operador de determinación

Para una operación `O`, la Frontier recibe un conjunto de `Assessment` y las consecuencias de frontera previamente autorizadas que correspondan.

El resultado se determina mediante la siguiente precedencia mínima:

```text
1. Existe H incumplida y suficientemente evaluada
       ↓
   NOT_VIABLE

2. No existe H incumplida
   y existe U material que impide una conclusión fiable
       ↓
   NOT_EVALUABLE

3. No existe H incumplida ni U material
   y existe K incumplida pero solucionable
       ↓
   VIABLE CON CONDICIONES

4. No existe H incumplida, U material ni K incumplida
       ↓
   VIABLE
```

Una restricción dura incumplida y suficientemente evaluada es suficiente para `NOT_VIABLE`; una deficiencia de información no puede neutralizarla ni transformarla en una conclusión distinta.

La presencia de `S` no modifica por sí sola el resultado de frontera.

## 7.2 Regla de suficiencia

La Frontier solo puede emitir `NOT_VIABLE` cuando la restricción que produce dicha consecuencia esté:

1. explícitamente autorizada;
2. aplicablemente determinada para la operación;
3. incumplida;
4. suficientemente evaluada.

No puede fabricar la consecuencia mediante inferencia.

## 7.3 Regla de no compensación

Los resultados favorables no compensan automáticamente una restricción dura incumplida.

```text
H incumplida + cualquier cantidad de S favorables
                    ↓
              NOT_VIABLE
```

Los resultados negativos no generan por acumulación una nueva restricción.

```text
n resultados desfavorables
            ≠
   nueva restricción de frontera
```

No existe voto, suma, promedio, puntuación ni ponderación de viabilidad.

## 7.4 Regla de no inferencia

La Frontier no puede realizar ninguna de estas transformaciones por sí misma:

```text
Assessment FALSE       → H
CRITICAL               → H
Criticality CRITICAL   → H
GAP                    → H
R3                     → H
muchos resultados      → H
escenario anterior     → H
```

Solo una autoridad normativa previa puede proporcionar la consecuencia de frontera que habilite la clasificación `H` o `K`.

## 7.5 Redundancia

La cantidad de `Assessment` que describan una misma restricción o una misma causa no incrementa por sí misma el peso de dicha restricción.

```text
3 Assessment desfavorables
        ↓
no equivale a
        ↓
3 bloqueos
```

La Frontier no utiliza el número de resultados para intensificar la viabilidad negativa.

La identificación formal de relaciones causales entre restricciones queda fuera de este contrato y deberá ser autorizada antes de introducir una deduplicación causal automática.

## 7.6 Conflictos

La Frontier aplica únicamente las consecuencias de frontera ya autorizadas.

Cuando dos resultados requieran una política de resolución que no esté definida por sus autoridades correspondientes, la Frontier no inventará una precedencia nueva.

La resolución de conflictos, consolidación de resultados incompatibles y determinación posterior corresponden a `CRC`.

---

# 8. Invariantes de monotonicidad

La Frontier debe conservar las siguientes propiedades.

## 8.1 Información favorable

Añadir información que confirme condiciones favorables, sin activar una restricción dura previamente autorizada, no puede empeorar artificialmente el resultado.

## 8.2 Señales

Añadir señales, independientemente de su número o intensidad descriptiva, no puede modificar por sí mismo el estado de viabilidad.

## 8.3 Reglas informativas

Añadir una regla de efecto meramente informativo no puede convertir por sí misma una operación viable en no viable.

## 8.4 Condiciones no activadas

La mera existencia de una condición autorizada no modifica el resultado. Solo una condición efectivamente incumplida y solucionable puede producir `VIABLE CON CONDICIONES`.

## 8.5 Nueva información que revela una restricción

La viabilidad puede empeorar después de recibir nueva información únicamente cuando dicha información revele o permita determinar una restricción de frontera previamente autorizada que estaba materialmente sin evaluar.

Esto no constituye una violación de monotonicidad: constituye la revelación de una condición normativa preexistente.

## 8.6 Escenarios

Un escenario posterior se evalúa contra su propio estado y no hereda restricciones del escenario precedente por el mero hecho de haber existido.

```text
ESCENARIO A
     ≠
ESCENARIO B
```

El historial se conserva para trazabilidad, no como acumulador normativo.

## 8.7 Redundancia

Añadir resultados redundantes o múltiples manifestaciones de una misma restricción no puede intensificar artificialmente el resultado mediante conteo.

---

# 9. Agregación de múltiples Assessment

Cuando la Frontier reciba múltiples `Assessment` simultáneos, no aplicará una agregación por puntuación ni por mayoría.

La determinación base seguirá exclusivamente la cadena de suficiencia y precedencia definida en la sección 7:

```text
restricción dura autorizada e incumplida
                ↓
          NOT_VIABLE

si no:
base materialmente insuficiente
                ↓
          NOT_EVALUABLE

si no:
condición autorizada incumplida y solucionable
                ↓
     VIABLE CON CONDICIONES

si no:
              VIABLE
```

Esta agregación no otorga a Frontier autoridad para resolver conflictos que pertenezcan a CRC ni para crear consecuencias de frontera no definidas.

---

# 10. Separación respecto de Assessment

`Assessment` representa exclusivamente el resultado individual de evaluar una regla.

La Frontier no vuelve a evaluar la regla ni modifica el significado de:

```text
EVALUABLE     → TRUE | FALSE
NOT_EVALUABLE → None
```

La ausencia de evidencia no se convierte automáticamente en `FALSE` ni en `NOT_VIABLE`.

---

# 11. Separación respecto de Evidence

La Frontier no constituye un repositorio alternativo de evidencia.

La evidencia que sustenta una evaluación permanece vinculada al `Assessment` correspondiente y puede ser recuperada mediante la cadena de trazabilidad autorizada.

No se introduce una segunda autoridad sobre admisibilidad, suficiencia o trazabilidad de evidencia.

---

# 12. Separación respecto de Scenario Engine

La Frontier no crea ni modifica escenarios.

El `Scenario Engine` recibe el resultado base y desarrolla las hipótesis o alternativas que correspondan conforme a su propia autoridad.

La Frontier no optimiza, compara ni selecciona escenarios.

Cada escenario se recalcula contra las reglas, dependencias, evidencia y restricciones autorizadas vigentes para ese escenario, sin heredar restricciones del escenario anterior por mera continuidad histórica.

---

# 13. Separación respecto de CRC

La Frontier no sustituye a la Capa de Resolución de Conflictos.

En particular, no realiza por sí misma:

- resolución de conflictos entre reglas cuando requiera una política no definida;
- aplicación de la jerarquía de resolución de CRC;
- consolidación de recomendaciones incompatibles;
- determinación del motivo dominante de una recomendación final;
- generación de una recomendación empresarial.

La existencia de una situación desfavorable o condicionada no autoriza a la Frontier a emitir `COMPRAR`, `NEGOCIAR`, `COMPRAR CONDICIONADO` o `NO COMPRAR` como recomendación empresarial.

---

# 14. Separación respecto de negociación y decisión

La Frontier no negocia condiciones, no genera estrategias de negociación y no ejecuta decisiones empresariales.

Una operación `VIABLE CON CONDICIONES` no implica por sí misma una instrucción de negociación ni una orden de compra.

La recomendación y la decisión permanecen en las capas posteriores y bajo control humano conforme a la arquitectura autorizada.

---

# 15. Trazabilidad

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

# 16. Elementos expresamente no definidos por este contrato

Este contrato no define:

- nuevas reglas de negocio;
- nuevos parámetros;
- nuevos umbrales;
- fórmulas de viabilidad;
- `Viability Score`;
- ponderaciones;
- mecanismos de compensación;
- una jerarquía paralela a CRC;
- reglas de precedencia propias de CRC;
- escenarios;
- negociación;
- recomendaciones;
- decisiones de compra.

La agregación mínima de múltiples `Assessment` sí queda definida exclusivamente mediante las invariantes y la precedencia de las secciones 7 y 9. Cualquier política adicional que requiera resolver conflictos no definida por dichas secciones deberá ser autorizada documentalmente antes de convertirse en comportamiento técnico.

---

# 17. Estado de especificación

```text
DOMINIO DE VIABILIDAD                  AUTORIZADO
POSICIÓN ARQUITECTÓNICA                AUTORIZADO
ESTADOS DE VIABILIDAD                  AUTORIZADO
ENTRADA DESDE ASSESSMENT               AUTORIZADO
TRAZABILIDAD                           AUTORIZADO
SEPARACIÓN DE EVIDENCE                 AUTORIZADO
SEPARACIÓN DE SCENARIO ENGINE          AUTORIZADO
SEPARACIÓN DE CRC                      AUTORIZADO
INVARIANTES DE NO INFERENCIA           AUTORIZADO
INVARIANTES DE MONOTONICIDAD            AUTORIZADO
AGREGACIÓN MÍNIMA DE ASSESSMENTS       AUTORIZADO

FÓRMULAS DE VIABILIDAD                 PENDIENTE / NO DEFINIDO
UMBRAL GLOBAL DE VIABILIDAD            PENDIENTE / NO DEFINIDO
POLÍTICAS ADICIONALES DE CONFLICTO     PENDIENTE / NO DEFINIDO
IDENTIDAD CAUSAL AUTOMÁTICA            PENDIENTE / NO DEFINIDO
```

---

# 18. Cierre del contrato

Este documento materializa el diseño contractual cerrado de `Viability Frontier` y sus invariantes de frontera y monotonicidad.

La materialización de este contrato **no introduce cambios técnicos** y no implica modificaciones en:

- `models.py`;
- `validation.py`;
- tests;
- reglas existentes;
- parámetros;
- C0;
- CRC;
- Scenario Engine.

Cualquier implementación futura deberá respetar este perímetro y no podrá convertir los elementos marcados como `PENDIENTE / NO DEFINIDO` en comportamiento implícito.
