# VIABILITY SCENARIO ENGINE

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Contrato documental
**Tipo de cambio:** Documentación exclusivamente
**Baseline de diseño:** EIOS Vertical MVP

---

## 1. Propósito

`Viability Scenario Engine` es el componente especializado que representa y recalcula escenarios hipotéticos derivados de una operación base, utilizando únicamente hipótesis y variables de escenario autorizadas.

Su función es desarrollar escenarios posteriores al resultado base de `Viability Frontier` y someterlos nuevamente al flujo de evaluación y viabilidad correspondiente.

No constituye un segundo motor de reglas, una autoridad de parámetros, una matriz de dependencias, un motor de viabilidad, un motor de decisión, un motor de negociación ni una autoridad de decisión empresarial.

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
    NUEVO ESCENARIO
            ↓
       RECÁLCULO
            ↓
        ASSESSMENT
            ↓
   VIABILITY FRONTIER
            ↓
 DECISION TWIN / NEGOCIACIÓN
            ↓
           CRC
```

El `Scenario Engine` se sitúa después del resultado base de `Viability Frontier` y antes de las capas posteriores de comparación, negociación y resolución.

---

## 3. Autoridad

El `Scenario Engine` no crea autoridad normativa propia.

Consume las reglas, parámetros, dependencias, resultados de evaluación y restricciones de viabilidad ya autorizados por sus respectivas autoridades.

Su autoridad se limita a representar escenarios, modificar hipótesis autorizadas, provocar su recalculación, conservar versiones y mantener la trazabilidad correspondiente.

No puede crear ni modificar reglas, parámetros, dependencias, restricciones normativas ni decisiones.

---

## 4. Escenario y operación real

Un escenario representa una hipótesis alternativa respecto de una operación o escenario precedente.

```text
OPERACIÓN REAL ≠ ESCENARIO
ESCENARIO ≠ ALTERNATIVA
ALTERNATIVA ≠ DECISIÓN
```

La creación o modificación de un escenario nunca sobrescribe la operación real.

Todo cambio relevante genera un nuevo escenario; un escenario posterior no sobrescribe un escenario precedente.

---

## 5. Variables de escenario

Una variable de escenario representa un valor hipotético utilizado para la simulación.

```text
VARIABLE DE ESCENARIO ≠ PARÁMETRO
```

Las variables de escenario pueden incluir, cuando estén formalmente autorizadas, conceptos como:

- precio;
- cantidad;
- descuento;
- rappel;
- plazo de pago;
- condiciones financieras;
- entrega;
- plazo de entrega;
- condiciones logísticas;
- otras variables negociables autorizadas.

La existencia de una variable en esta categoría no constituye por sí sola autorización universal para modificarla en cualquier escenario.

---

## 6. Parámetros

El `Scenario Engine` utiliza la parametrización vigente y no la modifica como mecanismo de simulación.

Por tanto:

```text
modificar una hipótesis de escenario
        ≠
modificar la configuración de EIOS
```

Una hipótesis como `precio = X` constituye un valor simulado del escenario y no una modificación del parámetro que configure el comportamiento del sistema.

---

## 7. RDM y recalculación

La `Rule_Dependency_Matrix` conserva exclusivamente su autoridad sobre las dependencias canónicas demostradas.

```text
Scenario Engine
      ↓
modifica hipótesis autorizada
      ↓
provoca / solicita recalculación
      ↓
RDM
      ↓
determina dependencias CONFIRMED existentes
      ↓
evaluadores correspondientes
      ↓
Assessment
```

El `Scenario Engine`:

- no descubre dependencias;
- no crea dependencias;
- no modifica la RDM;
- no decide qué reglas están relacionadas;
- no convierte una hipótesis en una dependencia nueva.

La recalculación se limita a las dependencias y evaluaciones autorizadas por las autoridades existentes.

---

## 8. Ciclo de escenario

El ciclo funcional mínimo es:

```text
ESCENARIO BASE
      ↓
HIPÓTESIS AUTORIZADA
      ↓
NUEVO ESCENARIO
      ↓
RECALCULACIÓN
      ↓
EVALUACIÓN DE REGLAS
      ↓
ASSESSMENT
      ↓
VIABILITY FRONTIER
      ↓
RESULTADO DEL ESCENARIO
```

El resultado del escenario vuelve a utilizar los contratos existentes de evaluación y viabilidad; no crea una semántica paralela.

---

## 9. Assessment

Cada escenario puede producir nuevos `Assessment` cuando las hipótesis modificadas afecten a las evaluaciones correspondientes.

`Assessment` continúa representando exclusivamente el resultado individual de evaluar una regla.

```text
Scenario Engine ≠ Assessment
```

El `Scenario Engine` no modifica directamente un `Assessment` existente ni altera la semántica de `TRUE`, `FALSE` o `None`.

---

## 10. Evidence

El `Scenario Engine` no constituye una autoridad alternativa sobre evidencia.

Una hipótesis de escenario no sustituye, altera ni inventa la evidencia que sustenta una evaluación.

```text
Scenario Input ≠ Evidence
```

La evidencia permanece vinculada al proceso de evaluación y trazabilidad correspondiente.

---

## 11. Viability Frontier

La determinación de viabilidad permanece bajo la autoridad de `Viability Frontier`.

```text
Scenario
   ↓
Assessment
   ↓
Viability Frontier
   ↓
Viability Result
```

El `Scenario Engine` no determina por sí mismo `VIABLE`, `VIABLE CON CONDICIONES`, `NOT_VIABLE` o `NOT_EVALUABLE`.

En particular:

```text
Scenario Engine ≠ Viability Frontier
VIABLE ≠ COMPRAR
NOT_EVALUABLE ≠ NOT_VIABLE
```

---

## 12. Alternativas y Decision Twin

No todo escenario constituye una alternativa.

La secuencia funcional es:

```text
ESCENARIOS
    ↓
VIABILITY
    ↓
ALTERNATIVAS VIABLES
    ↓
DECISION TWIN
```

El `Scenario Engine` no determina cuál escenario es mejor, preferible u óptimo, ni realiza selección decisional.

---

## 13. Negotiation

Una variable negociable dentro de un escenario sigue siendo una hipótesis de simulación.

```text
VARIABLE NEGOCIABLE
        ≠
CONCESIÓN NEGOCIADORA
```

El `Scenario Engine` puede representar condiciones hipotéticas que posteriormente sean relevantes para negociación, pero no crea estrategia, concesiones ni decisiones de negociación.

---

## 14. CRC

La resolución y consolidación posterior permanecen bajo la autoridad de `CRC`.

El `Scenario Engine` no:

- resuelve conflictos;
- aplica la jerarquía de resolución de CRC;
- compensa restricciones;
- consolida recomendaciones incompatibles;
- genera una recomendación empresarial;
- adopta una decisión.

```text
Scenario Engine ≠ CRC
```

---

## 15. Generación algorítmica

**PENDIENTE DE ESPECIFICACIÓN:** la documentación autoriza la creación de escenarios, pero no establece un algoritmo general de generación automática.

Por tanto, este contrato no define:

- heurísticas;
- búsqueda exhaustiva;
- combinaciones automáticas;
- reglas de poda;
- profundidad de exploración;
- número máximo de escenarios;
- orden de generación.

No se introduce ninguna de estas políticas por inferencia.

---

## 16. Priorización y selección

**PENDIENTE DE ESPECIFICACIÓN:** no se establece una política general de priorización de escenarios.

El `Scenario Engine` no atribuye puntuaciones, preferencias u órdenes decisionales propios a los escenarios.

La comparación y selección posterior permanece fuera de su autoridad.

---

## 17. Optimización

La optimización no forma parte de la autoridad del `Scenario Engine` en el MVP.

No se introducen objetivos de minimización, maximización, optimización matemática ni búsqueda de una solución óptima.

```text
Scenario Engine ≠ Optimization Engine
```

---

## 18. Versionado y trazabilidad

El escenario debe conservar su identidad, relación con el escenario precedente, versión y trazabilidad funcional conforme a las autoridades arquitectónicas existentes.

Los nombres de campos, esquema físico, API, persistencia y modelo de datos **no quedan definidos por este contrato** y permanecen `PENDIENTE DE ESPECIFICACIÓN`.

Por tanto, este documento no constituye autorización para introducir campos concretos en `models.py` ni para establecer una API o esquema de persistencia.

---

## 19. Invariantes

```text
OPERACIÓN REAL ≠ ESCENARIO
ESCENARIO ≠ ALTERNATIVA
VARIABLE DE ESCENARIO ≠ PARÁMETRO
SCENARIO ENGINE ≠ RDM
SCENARIO ENGINE ≠ ASSESSMENT
SCENARIO ENGINE ≠ EVIDENCE AUTHORITY
SCENARIO ENGINE ≠ VIABILITY FRONTIER
SCENARIO ENGINE ≠ DECISION TWIN
SCENARIO ENGINE ≠ NEGOTIATION
SCENARIO ENGINE ≠ CRC
VIABLE ≠ COMPRAR
NOT_EVALUABLE ≠ NOT_VIABLE
```

---

## 20. Límites explícitos

El `Scenario Engine` no puede:

- crear o modificar reglas;
- crear o modificar dependencias;
- modificar parámetros como mecanismo de simulación;
- crear restricciones normativas;
- determinar viabilidad por sí mismo;
- transformar `NOT_EVALUABLE` en `NOT_VIABLE`;
- seleccionar la alternativa empresarial;
- optimizar;
- negociar;
- recomendar;
- decidir.

---

## 21. Pendiente de especificación

Queda expresamente fuera del alcance cerrado de este contrato:

```text
🟡 algoritmo de generación automática
🟡 priorización
🟡 combinación automática
🟡 poda
🟡 número y profundidad de escenarios
🟡 criterios de selección decisional
🟡 optimización, si alguna autoridad futura la autorizase
🟡 esquema físico
🟡 persistencia
🟡 API
🟡 modelo de datos
```

La ausencia de especificación no se resuelve mediante inferencia dentro de este contrato.

---

## 22. Tipo de cambio

Este documento constituye **documentación exclusivamente**.

No introduce cambios en:

- `models.py`;
- `validation.py`;
- tests;
- reglas;
- parámetros;
- `Rule_Dependency_Matrix`;
- `Assessment Contract`;
- `Evidence Contract`;
- `Viability_Frontier`;
- `Decision Twin`;
- `CRC`.

No autoriza implementación técnica ni nuevas políticas algorítmicas.
