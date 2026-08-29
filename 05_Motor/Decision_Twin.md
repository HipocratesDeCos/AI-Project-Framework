# DECISION TWIN

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Contrato documental  
**Tipo de cambio:** Documentación exclusivamente  
**Baseline:** EIOS Vertical MVP

---

## 1. Propósito

`Decision Twin` es el componente especializado que representa una alternativa de decisión concreta y permite comparar alternativas ya disponibles, junto con sus resultados y consecuencias conocidas.

Su función es proporcionar una representación estructurada de la situación decisional para apoyar el análisis previo a negociación, consolidación y decisión humana.

No constituye un segundo motor de reglas, motor de viabilidad, motor de escenarios, autoridad de parámetros, matriz de dependencias, motor de negociación, autoridad de resolución ni decisor empresarial.

---

## 2. Posición arquitectónica

```text
DATOS / EVIDENCIA
       ↓
REGLAS / ASSESSMENT
       ↓
VIABILITY FRONTIER
       ↓
SCENARIO ENGINE
       ↓
ESCENARIOS EVALUADOS
       ↓
ALTERNATIVAS
       ↓
DECISION TWIN
       ↓
NEGOTIATION / CRC
       ↓
DECISOR HUMANO
```

El `Decision Twin` se sitúa después de la generación/evaluación de escenarios y de la determinación de viabilidad, y antes de las funciones posteriores de negociación y consolidación.

---

## 3. Autoridad

El `Decision Twin` no crea autoridad normativa propia.

Su autoridad se limita a:

- representar alternativas;
- comparar alternativas;
- analizar consecuencias de las alternativas representadas;
- conservar las referencias necesarias para su trazabilidad.

Consume resultados producidos por autoridades anteriores y entrega información estructurada a capas posteriores.

No puede crear ni modificar reglas, parámetros, dependencias, evidencia, resultados individuales, restricciones de viabilidad, escenarios ni decisiones.

---

## 4. Escenario y alternativa

```text
ESCENARIO ≠ ALTERNATIVA
ALTERNATIVA ≠ DECISIÓN
```

El `Scenario Engine` genera, modifica y recalcula escenarios.

El `Decision Twin` recibe escenarios evaluados y representa las alternativas que pueden ser comparadas.

```text
SCENARIO ENGINE
→ escenarios

DECISION TWIN
→ alternativas
```

El `Decision Twin` no genera ni modifica escenarios como mecanismo propio.

---

## 5. Simulación

La arquitectura puede utilizar el término `simulación` para describir la capacidad global del sistema de estudiar hipótesis.

Dentro de este contrato, la modificación de hipótesis y el recálculo pertenecen al flujo del `Scenario Engine`.

Por tanto:

```text
SIMULACIÓN DE HIPÓTESIS
→ Scenario Engine

REPRESENTACIÓN / COMPARACIÓN
→ Decision Twin
```

El `Decision Twin` no se convierte en un segundo motor de escenarios por interpretar la simulación como capacidad propia de modificación de hipótesis.

---

## 6. Situación de referencia

El `Decision Twin` puede representar la situación sobre la que se comparan alternativas.

Conceptualmente:

```text
SITUACIÓN DE REFERENCIA
        ↓
ALTERNATIVAS
        ↓
COMPARACIÓN
```

La representación no altera la operación real ni constituye una nueva operación ejecutada.

---

## 7. Alternativa

Una alternativa es una opción representada para comparación decisional.

Puede derivar de un escenario evaluado o de otra opción formalmente disponible dentro del flujo EIOS.

El `Decision Twin` no autoriza por sí mismo la creación de nuevas alternativas mediante búsqueda, combinación, optimización o exploración automática.

```text
ALTERNATIVA
≠
ESCENARIO
≠
DECISIÓN
```

---

## 8. Resultados asociados

Una alternativa puede estar acompañada por:

- resultados de evaluación;
- resultado de viabilidad;
- consecuencias conocidas;
- referencias de trazabilidad.

El `Decision Twin` consume estos resultados; no los recalcula ni altera su semántica.

---

## 9. Viability Frontier

La determinación de viabilidad permanece bajo la autoridad de `Viability Frontier`.

```text
Assessment
    ↓
Viability Frontier
    ↓
Resultado de viabilidad
    ↓
Decision Twin
```

El `Decision Twin` no determina:

- `VIABLE`;
- `VIABLE CON CONDICIONES`;
- `NOT_VIABLE`;
- `NOT_EVALUABLE`.

```text
VIABLE ≠ COMPRAR
NOT_EVALUABLE ≠ NOT_VIABLE
```

El resultado de viabilidad es un atributo informativo de la alternativa representada, no una decisión empresarial.

---

## 10. Assessment

`Assessment` continúa siendo exclusivamente el resultado individual de evaluar una regla.

```text
Assessment
→ evaluación individual

Decision Twin
→ representación comparativa
```

El `Decision Twin` no crea, modifica ni consolida `Assessment`.

---

## 11. Evidence

La evidencia permanece bajo la autoridad de `Evidence Contract`.

El `Decision Twin` puede mantener referencias hacia la evidencia que sustenta resultados representados, pero no determina su validez, suficiencia o admisibilidad.

```text
Scenario / Alternative Input ≠ Evidence
```

---

## 12. Parámetros

El `Decision Twin` no modifica parámetros.

Debe mantenerse la distinción:

```text
PARÁMETRO
→ configuración autorizada

VALOR DE ALTERNATIVA
→ valor concreto de una opción
```

Una hipótesis o valor perteneciente a una alternativa no altera la configuración del sistema.

---

## 13. Rule Dependency Matrix

La `Rule_Dependency_Matrix` conserva su autoridad sobre las dependencias canónicas demostradas.

El `Decision Twin`:

- no descubre dependencias;
- no crea dependencias;
- no elimina dependencias;
- no modifica la RDM;
- no determina evaluabilidad mediante inferencia propia.

Puede conservar referencias de trazabilidad hacia resultados que dependan de relaciones ya autorizadas.

---

## 14. Comparación de alternativas

La función central del `Decision Twin` es comparar alternativas disponibles.

```text
ALTERNATIVA A
 ├── resultados
 ├── viabilidad
 └── consecuencias

ALTERNATIVA B
 ├── resultados
 ├── viabilidad
 └── consecuencias

        ↓

COMPARACIÓN
```

La comparación puede mostrar:

- diferencias;
- consecuencias;
- ventajas y desventajas;
- condiciones;
- resultados de viabilidad;
- riesgos ya determinados por las autoridades correspondientes;
- trazabilidad.

La comparación no constituye por sí misma selección ni decisión.

---

## 15. Comparación ≠ selección

```text
COMPARAR ≠ SELECCIONAR
SELECCIONAR ≠ DECIDIR
```

El `Decision Twin` no determina automáticamente cuál alternativa es mejor, óptima o preferente.

No se introduce una función de utilidad, ranking o regla de selección por inferencia.

---

## 16. Scoring y optimización

No forma parte de la autoridad del `Decision Twin` ningún sistema de:

- scoring decisional;
- ponderación;
- función de utilidad;
- ranking automático;
- optimización;
- búsqueda de la alternativa óptima.

```text
COMPARACIÓN ≠ SCORING
SCORING ≠ SELECCIÓN
```

Cualquier política futura requerirá una autoridad y especificación independientes.

---

## 17. Alternativa preferente

El concepto de `alternativa preferente` puede aparecer en artefactos posteriores del flujo, pero este contrato no asigna al `Decision Twin` la autoridad para determinarla.

```text
AUTORIDAD PARA DETERMINAR
ALTERNATIVA PREFERENTE
→ PENDIENTE DE ESPECIFICACIÓN
```

El `Decision Twin` proporciona el análisis comparativo necesario para las capas que sí dispongan de autoridad posterior.

---

## 18. Consecuencias

El `Decision Twin` puede representar consecuencias conocidas de una alternativa y compararlas con las correspondientes a otras alternativas.

No inventa consecuencias normativas ni sustituye los cálculos o evaluaciones de las autoridades que las producen.

```text
RESULTADO AUTORIZADO
        ↓
CONSECUENCIA REPRESENTADA
        ↓
COMPARACIÓN
```

---

## 19. Negotiation Intelligence

La frontera funcional es:

```text
Decision Twin
→ alternativas / resultados / consecuencias

Negotiation Intelligence
→ inteligencia negociadora
```

El `Decision Twin` no crea ni determina:

- BATNA;
- ZOPA;
- concesiones;
- fallback;
- walk-away;
- estrategia negociadora.

Una alternativa puede constituir entrada para negociación sin que el Twin realice la negociación.

---

## 20. CRC

La resolución y consolidación permanecen bajo la autoridad de `CRC`.

```text
Decision Twin
→ compara y analiza

CRC
→ consolida y resuelve
```

El `Decision Twin` no:

- resuelve conflictos;
- aplica la jerarquía de resolución de CRC;
- determina el motivo dominante;
- consolida resultados incompatibles;
- genera la recomendación empresarial final;
- adopta una decisión.

---

## 21. Decisor humano

El `Decision Twin` no sustituye al decisor humano.

```text
EIOS analiza
        ↓
compara
        ↓
explica
        ↓
prepara información
        ↓
DECISOR HUMANO
        ↓
DECISIÓN
```

```text
RECOMENDACIÓN ≠ DECISIÓN
DECISION TWIN ≠ DECISOR
```

---

## 22. Trazabilidad

La representación de una alternativa debe conservar las referencias necesarias para reconstruir su procedencia y los resultados utilizados.

Conceptualmente:

```text
ALTERNATIVA
    ↓
ORIGEN / ESCENARIO
    ↓
VIABILITY RESULT
    ↓
ASSESSMENT
    ↓
RULE / EVIDENCE / DATA
```

El esquema físico, nombres de campos, persistencia y API no quedan definidos por este contrato.

---

## 23. Pendiente de especificación

Queda expresamente fuera del alcance cerrado:

```text
🟡 generación automática de alternativas
🟡 algoritmo de comparación
🟡 criterios globales de comparación
🟡 ranking
🟡 scoring
🟡 función de utilidad
🟡 selección automática
🟡 alternativa preferente
🟡 optimización
🟡 número máximo de alternativas
🟡 política de descarte
🟡 modelo físico
🟡 persistencia
🟡 API
🟡 esquema SQL
```

La ausencia de especificación no se resuelve mediante inferencia dentro de este contrato.

---

## 24. Invariantes

```text
DECISION TWIN ≠ SCENARIO ENGINE
DECISION TWIN ≠ VIABILITY FRONTIER
DECISION TWIN ≠ ASSESSMENT
DECISION TWIN ≠ EVIDENCE AUTHORITY
DECISION TWIN ≠ PARAMETER AUTHORITY
DECISION TWIN ≠ RDM
DECISION TWIN ≠ NEGOTIATION
DECISION TWIN ≠ CRC

SCENARIO ≠ ALTERNATIVE
ALTERNATIVE ≠ DECISION

COMPARISON ≠ SELECTION
SELECTION ≠ DECISION

VIABLE ≠ COMPRAR
NOT_EVALUABLE ≠ NOT_VIABLE
```

---

## 25. Tipo de cambio

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
- `Viability_Scenario_Engine`;
- `Negotiation Intelligence`;
- `CRC`.

No autoriza implementación técnica ni nuevas políticas algorítmicas.
