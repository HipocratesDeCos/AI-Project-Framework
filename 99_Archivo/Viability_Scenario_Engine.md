# Viability_Scenario_Engine

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Motor transversal / nueva propuesta de valor  
**Relación:** [[Viability_Frontier]] + [[Motor_Escenarios]] + CRC + Assurance  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir conceptualmente el motor encargado de:

1. detectar qué condiciones hacen inviable una operación;
2. identificar variables negociables capaces de modificar dichas condiciones;
3. generar escenarios candidatos;
4. validar cada escenario;
5. descartar escenarios imposibles o ilegítimos;
6. comparar las alternativas viables;
7. entregar las mejores alternativas a la posterior estrategia de negociación.

---

## 2. Principio fundamental

El motor no debe buscar simplemente:

> **el escenario con el precio más bajo.**

Debe buscar:

> **las alternativas viables que mejoren la operación sin vulnerar restricciones críticas.**

---

## 3. Entrada

El motor recibe:

- escenario actual;
- variables negociables;
- variables contextuales;
- restricciones críticas;
- parámetros;
- reglas;
- evidencias;
- calidad de datos;
- resultados de CAPA 1–5.

Conceptualmente:

```text
ESCENARIO ACTUAL
      │
      ├── Precio
      ├── Cantidad
      ├── Pago
      ├── Transporte
      ├── Descuentos
      ├── Rappels
      ├── Entrega
      └── otras condiciones
      │
      ▼
VIABILITY SCENARIO ENGINE
```

---

## 4. Paso 1 — Detectar la causa de inviabilidad

Antes de generar alternativas, EIOS debe determinar:

> **¿Por qué el escenario actual no es viable?**

Ejemplo:

```text
S0
  │
  ├── Precio → desfavorable
  ├── Stock → exceso
  ├── Finanzas → riesgo
  └── Proveedor → correcto
              │
              ▼
       CAUSAS DOMINANTES
```

No debe modificar variables a ciegas.

---

## 5. Paso 2 — Identificar variables capaces de modificar la situación

Para cada causa deberá determinarse qué variables pueden influir en ella.

Ejemplo:

```text
RIESGO FINANCIERO
      │
      ├── plazo de pago
      ├── cantidad
      └── precio

EXCESO DE STOCK
      │
      ├── cantidad
      ├── fecha de entrega
      └── fraccionamiento

PRECIO DESFAVORABLE
      │
      ├── precio
      ├── descuento
      ├── rappel
      └── transporte
```

La relación entre causa y variable deberá estar definida por reglas o conocimiento empresarial.

---

## 6. Paso 3 — Generación de escenarios candidatos

El motor genera candidatos modificando una o varias variables negociables.

### Cambio simple

Una variable.

Ejemplo:

```text
Precio: 18,50 → 18,20
```

### Cambio combinado

Varias variables.

Ejemplo:

```text
Precio: 18,50 → 18,40
Pago: 30 → 60 días
```

### Cambio estructural

Una modificación de cantidad, calendario o condición logística.

---

## 7. Regla de modificaciones permitidas

El motor nunca debe modificar una variable que:

- no sea negociable;
- esté protegida por una salvaguarda;
- no tenga una definición válida;
- no disponga de evidencia suficiente para evaluar el resultado.

---

## 8. Límites de búsqueda

La generación de escenarios debe estar acotada.

No debe producir cientos o miles de combinaciones sin utilidad.

Inicialmente deberán existir límites para:

- número máximo de escenarios;
- número máximo de variables modificadas por escenario;
- rango máximo de modificación;
- granularidad de modificación;
- profundidad de combinaciones.

Los parámetros concretos quedan pendientes.

---

## 9. Escenarios imposibles

Un candidato debe descartarse inmediatamente si:

- contradice una condición contractual;
- viola una salvaguarda crítica;
- utiliza un valor imposible;
- genera datos incompatibles;
- depende de una evidencia no válida.

Resultado:

**ESCENARIO DESCARTADO**

La razón debe quedar registrada.

---

## 10. Validación de cada escenario

Cada candidato pasa por:

```text
ESCENARIO
   ↓
QTG
   ↓
CAPA 1
   ↓
CAPA 2
   ↓
CAPA 3
   ↓
CAPA 4
   ↓
CAPA 5
   ↓
REGLAS
   ↓
VIABILITY FRONTIER
```

El escenario no debe considerarse viable antes de completar las evaluaciones necesarias.

---

## 11. Estado del escenario

Cada candidato puede terminar como:

- **VIABLE**
- **VIABLE CON CONDICIONES**
- **NO VIABLE**
- **NO EVALUABLE**
- **DESCARTADO**

Estas categorías no sustituyen a las decisiones oficiales de la CRC.

---

## 12. No evaluable

Si el escenario no puede ser evaluado por falta de evidencia crítica:

> **NO EVALUABLE**

No se debe convertir en:

- viable;
- no viable;
- viable con condiciones.

La incertidumbre debe mantenerse explícita.

---

## 13. Ranking de escenarios

Una vez identificadas las soluciones viables, el motor debe compararlas.

No se utilizará inicialmente un único score opaco.

La comparación deberá conservar dimensiones visibles:

- mejora económica;
- impacto sobre stock;
- impacto financiero;
- riesgo;
- distancia respecto de las condiciones actuales;
- calidad de evidencia;
- esfuerzo de negociación.

---

## 14. Distancia de negociación

El motor deberá poder medir cuánto cambia cada escenario respecto al escenario actual.

Ejemplo conceptual:

```text
S0
Precio 18,50
Pago 30
Cantidad 1.000

S1
Precio 18,40
Pago 30
Cantidad 1.000

S2
Precio 18,40
Pago 60
Cantidad 1.000

S3
Precio 18,50
Pago 90
Cantidad 700
```

S1 requiere una intervención menor que S3.

Pero menor intervención no implica necesariamente mejor alternativa.

---

## 15. Dominancia

Cuando una alternativa es peor que otra en todas las dimensiones relevantes, puede considerarse dominada.

Ejemplo:

```text
S1
CEA peor
TCO peor
Riesgo igual
Negociación igual

S2
CEA mejor
TCO mejor
Riesgo igual
Negociación igual
```

S1 puede descartarse como alternativa dominada.

La metodología definitiva de dominancia queda pendiente de aprobación.

---

## 16. Soluciones equivalentes

Si dos escenarios producen resultados prácticamente equivalentes:

```text
S2 ≈ S4
```

EIOS no debería inventar una diferencia inexistente.

Podrá presentar:

> **Alternativas equivalentes**

y derivarlas a la estrategia de negociación.

---

## 17. Sensibilidad

El motor debe identificar qué variable convierte el escenario en viable.

Ejemplo:

```text
Precio 18,50 → NO VIABLE
Precio 18,40 → NO VIABLE
Precio 18,30 → VIABLE
```

Resultado:

> Sensibilidad alta al precio alrededor de 18,30 €.

Otro:

```text
Pago 30 → NO VIABLE
Pago 45 → NO VIABLE
Pago 60 → VIABLE
```

Resultado:

> Sensibilidad alta al plazo de pago.

---

## 18. Frontera de mínima intervención

El motor debería poder identificar la modificación mínima que atraviesa la frontera.

Ejemplo:

```text
NO VIABLE
     │
     ├── -0,10 € → sigue NO VIABLE
     ├── -0,20 € → sigue NO VIABLE
     └── -0,30 € → VIABLE
```

o:

```text
30 días → no viable
45 días → no viable
60 días → viable
```

Esto será especialmente útil para negociar.

---

## 19. Combinaciones

Una operación puede no ser viable mediante una sola modificación pero sí mediante una combinación.

Ejemplo:

```text
Precio -0,10 €
+
Pago +15 días
=
VIABLE
```

El motor debe poder buscar combinaciones cuando el problema no pueda resolverse mediante una sola variable.

---

## 20. Restricciones de búsqueda

La búsqueda no debe cruzar:

- salvaguardas no negociables;
- límites empresariales;
- condiciones contractuales conocidas;
- restricciones técnicas;
- parámetros de seguridad.

Estas restricciones tienen prioridad sobre la optimización.

---

## 21. Evidencia

Cada escenario candidato deberá poder responder:

- ¿qué datos utilizó?
- ¿qué evidencia respaldó cada cambio?
- ¿qué reglas se evaluaron?
- ¿qué parámetros estaban vigentes?
- ¿qué versión del escenario es?
- ¿por qué fue aceptado o descartado?

Esto conecta directamente con:

[[Viability_Frontier]]

[[Evidence_Contract]]

y el **EIOS Assurance Framework**.

---

## 22. Conservación de escenarios

Todo escenario candidato que haya llegado a evaluación deberá poder conservar su trazabilidad mínima.

Como mínimo:

- `Scenario_ID`
- escenario padre;
- variables modificadas;
- valores anteriores;
- valores nuevos;
- fecha;
- usuario/sistema;
- estado;
- motivo;
- resultados principales.

---

## 23. Resultado del motor

El motor no devuelve todavía una negociación.

Devuelve:

```text
ESCENARIOS VIABLES
        │
        ├── alternativa 1
        ├── alternativa 2
        ├── alternativa 3
        └── ...
        │
        ▼
COMPARACIÓN
        │
        ▼
MEJORES ALTERNATIVAS
```

La futura [[Negotiation_Ladder]] transformará esas alternativas en estrategia.

---

## 24. Relación con CRC

La CRC recibe las alternativas y resultados del motor.

```text
Viability Scenario Engine
          ↓
escenarios viables
          ↓
CRC
          ↓
decisión oficial
```

La CRC mantiene la autoridad sobre la decisión.

---

## 25. Principio de explicabilidad

EIOS deberá poder explicar una alternativa de forma ejecutiva:

> **“Esta combinación hace viable la operación porque elimina el riesgo financiero crítico sin generar exceso de stock.”**

Y deberá poder mostrar el detalle bajo demanda.

---

## 26. Regla de seguridad

> **No generar escenarios que violen restricciones críticas.**

> **No considerar viable un escenario sin evidencia suficiente.**

> **No ocultar escenarios descartados sin registrar el motivo.**

> **No usar un score opaco como única base del ranking.**

> **No confundir una alternativa matemáticamente viable con una recomendación empresarial final.**

---

## 27. Decisiones pendientes

No se cierran todavía:

- algoritmo de generación;
- algoritmo de búsqueda combinatoria;
- granularidad;
- límites;
- función de dominancia;
- ranking definitivo;
- función de coste de negociación;
- priorización de variables;
- número máximo de candidatos;
- optimización matemática;
- integración definitiva con BATNA/ZOPA.

---

## 28. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
