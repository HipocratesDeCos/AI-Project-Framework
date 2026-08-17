# Viability_Frontier

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Concepto transversal / nueva propuesta de valor  
**Relación:** CAPA 1–5 + Motor de Escenarios + CRC + Assurance  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir la **Frontera de Viabilidad EIOS** como el conjunto de condiciones bajo las cuales una operación de compra puede considerarse empresarialmente viable.

La Frontera de Viabilidad no busca encontrar simplemente el precio más bajo.

Busca determinar:

> **qué combinaciones de condiciones permiten realizar la operación sin vulnerar las restricciones críticas de la empresa y manteniendo un nivel aceptable de valor, riesgo y sostenibilidad.**

---

## 2. Problema que resuelve

Una propuesta puede ser desfavorable bajo sus condiciones actuales y, sin embargo, convertirse en viable mediante una modificación negociable.

```text
CONDICIONES ACTUALES
        ↓
NO VIABLE
        ↓
¿Qué tendría que cambiar?
        ↓
ESCENARIOS CANDIDATOS
        ↓
validación de evidencias
        ↓
VIABLE / NO VIABLE
```

---

## 3. Principio fundamental

> **Una operación es viable cuando satisface todas las restricciones críticas aplicables y alcanza un nivel aceptable de valor económico, operativo y de riesgo bajo las condiciones del escenario analizado.**

La viabilidad no se determina mediante una suma simple de puntuaciones.

No se permite que múltiples factores favorables compensen automáticamente una salvaguarda crítica.

---

## 4. Dimensiones de viabilidad

Inicialmente se consideran:

- precio;
- CEA;
- TCO;
- stock / demanda;
- finanzas / liquidez;
- proveedor / riesgo;
- condiciones comerciales.

Cada dimensión puede contener:

- condiciones favorables;
- condiciones desfavorables;
- restricciones;
- incertidumbres;
- variables negociables.

---

## 5. Restricciones críticas

Una restricción crítica es una condición cuya vulneración puede impedir que la operación sea viable.

Ejemplos conceptuales:

- incapacidad prevista para atender pagos;
- dato crítico no fiable;
- unidad de compra incompatible;
- contradicción crítica;
- condición financiera no cumplida;
- salvaguarda empresarial no anulable.

Una restricción crítica no puede compensarse mediante una mejora en otra dimensión.

---

## 6. Variables negociables

Son variables que pueden modificarse durante la negociación y cuyo cambio puede alterar la viabilidad.

Ejemplos iniciales:

- precio;
- cantidad;
- descuento;
- rappel;
- plazo de pago;
- transporte;
- seguro;
- fecha de entrega;
- cantidad mínima;
- condiciones de entrega;
- garantías u otras condiciones comerciales.

---

## 7. Variables contextuales

Son variables que normalmente no constituyen una concesión negociable inmediata, pero afectan a la viabilidad.

Ejemplos:

- demanda;
- stock;
- cobertura;
- rotación;
- situación financiera;
- histórico;
- proveedor;
- riesgo;
- comparabilidad.

Estas variables alimentan la frontera pero no necesariamente pueden modificarse durante la negociación.

---

## 8. Frontera de viabilidad

```text
                 OPERACIÓN
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        PRECIO      STOCK     FINANZAS
          │          │          │
          └──────────┼──────────┘
                     ▼
                 PROVEEDOR
                     │
                     ▼
                   RIESGO
                     │
                     ▼
              VIABILIDAD
```

### Dentro de la frontera
Cumple las restricciones críticas aplicables y alcanza las condiciones mínimas de viabilidad.

### Fuera de la frontera
Incumple una o más condiciones necesarias.

### En la frontera
Es viable, pero una modificación adicional puede hacer que deje de serlo.

---

## 9. La frontera no es un único punto

No debe existir necesariamente un único conjunto de condiciones viables.

Puede existir una región de soluciones:

```text
Escenario A
Precio menor + pago más corto

Escenario B
Precio mayor + pago más largo

Escenario C
Precio igual + cantidad menor

Escenario D
Precio igual + transporte incluido
```

Todos pueden ser viables.

La función de EIOS será identificar y comparar estas alternativas.

---

## 10. Escenario base

Toda evaluación de viabilidad parte de:

**S0 — condiciones actuales de la propuesta.**

El escenario base conserva:

- precio;
- cantidad;
- plazo;
- transporte;
- descuentos;
- rappels;
- condiciones relevantes;
- datos de stock;
- situación financiera;
- proveedor;
- fecha de decisión.

---

## 11. Escenarios candidatos

Cuando la operación no sea viable, EIOS podrá generar escenarios candidatos modificando variables negociables.

```text
S0
Precio 18,50 €
Cantidad 1.000
Pago 30 días
        ↓
NO VIABLE

S1
Precio 18,20 €
Cantidad 1.000
Pago 30 días
        ↓
NO VIABLE

S2
Precio 18,20 €
Cantidad 1.000
Pago 60 días
        ↓
VIABLE

S3
Precio 18,40 €
Cantidad 700
Pago 60 días
        ↓
VIABLE
```

Los escenarios anteriores nunca se sobrescriben.

---

## 12. Regla de modificación mínima

Cuando existan varias formas de hacer viable una operación, EIOS deberá buscar inicialmente la solución que requiera:

> **la menor intervención necesaria sobre las condiciones actuales, siempre que conserve un nivel aceptable de valor y riesgo.**

No significa que la menor modificación sea siempre la mejor solución.

---

## 13. Valor económico

Una alternativa viable no debe evaluarse únicamente por cumplir restricciones.

Entre varias soluciones viables deberán poder compararse:

- CEA;
- TCO;
- margen;
- liquidez;
- impacto sobre stock;
- riesgo;
- condiciones comerciales.

La comparación definitiva será responsabilidad del motor de resolución.

---

## 14. Riesgo

La viabilidad debe considerar el riesgo relevante.

Una operación puede ser económicamente atractiva y, sin embargo, presentar un riesgo no aceptable.

Ejemplo:

```text
CEA        favorable
TCO        favorable
Stock      favorable
Finanzas   favorable
Proveedor  riesgo crítico
             ↓
          NO VIABLE
```

No se permite que el valor económico compense automáticamente un bloqueo crítico.

---

## 15. Liquidez

La viabilidad financiera debe considerar la capacidad prevista para atender las obligaciones derivadas de la operación.

Una operación con buen precio no es viable si compromete una salvaguarda financiera crítica que no puede resolverse.

---

## 16. Stock

La viabilidad de una compra debe considerar el impacto de la cantidad sobre:

- stock proyectado;
- cobertura;
- riesgo de rotura;
- exceso;
- permanencia;
- obsolescencia.

Una mejora de precio no convierte automáticamente una compra excesiva en viable.

---

## 17. Evidencia y legitimidad

Ninguna frontera calculada será considerada legítima si los datos críticos necesarios no cumplen el **Quality & Trust Gate** y el correspondiente **Evidence Contract**.

```text
DATOS
  ↓
EVIDENCIAS
  ↓
QTG
  ↓
EVALUACIÓN DE VIABILIDAD
```

Si una condición crítica no puede evaluarse de forma fiable:

**INFORMACIÓN INSUFICIENTE**

puede prevalecer sobre una falsa afirmación de viabilidad.

---

## 18. Sensibilidad

La Frontera de Viabilidad debe permitir identificar qué variables tienen mayor capacidad para modificar la clasificación.

Ejemplo:

```text
Precio
18,50 → 18,30
NO cambia la viabilidad

Pago
30 → 60 días
CAMBIA a viable

Cantidad
1.000 → 700
CAMBIA a viable
```

Resultado:

> La decisión es especialmente sensible al plazo de pago y a la cantidad.

Esta información será útil para la estrategia de negociación.

---

## 19. Soluciones múltiples

Cuando existan varias soluciones viables, EIOS no debe elegir automáticamente la primera encontrada.

Debe conservar las alternativas y permitir su comparación.

```text
S2 → VIABLE
S3 → VIABLE
S4 → VIABLE
        │
        ▼
COMPARACIÓN
        │
        ▼
MEJOR ALTERNATIVA
```

La metodología para seleccionar la mejor alternativa deberá definirse posteriormente.

---

## 20. Estados de salida de la frontera

### VIABLE
La operación cumple las condiciones aplicables.

### VIABLE CON CONDICIONES
La operación solo es viable si se cumplen determinadas condiciones negociadas.

### NO VIABLE
Existe al menos una restricción no resoluble bajo las alternativas consideradas.

### NO EVALUABLE
La evidencia disponible no permite determinar la viabilidad con suficiente confianza.

---

## 21. Relación con la decisión

La Frontera de Viabilidad no sustituye a la CRC.

La secuencia conceptual será:

```text
DATOS
  ↓
QTG
  ↓
ANÁLISIS
  ↓
FRONTERA DE VIABILIDAD
  ↓
ESCENARIOS VIABLES
  ↓
CRC
  ↓
DECISIÓN
```

La CRC continúa determinando la decisión oficial:

- COMPRAR;
- NEGOCIAR;
- COMPRAR CONDICIONADO;
- NO COMPRAR;
- INFORMACIÓN INSUFICIENTE.

---

## 22. Relación con Negotiation Ladder

La Frontera de Viabilidad será la entrada principal de la futura:

[[Negotiation_Ladder]]

La frontera responde:

> **qué combinaciones son viables.**

La Negotiation Ladder responderá:

> **en qué orden debería intentar conseguirlas.**

---

## 23. Relación con Decision Twin

La Frontera de Viabilidad será una de las salidas principales del futuro:

[[Decision_Twin]]

El Decision Twin permitirá explorar:

> ¿Qué pasa si cambio una o varias condiciones?

---

## 24. Relación con Assurance

La Frontera deberá poder justificar:

- datos utilizados;
- evidencias;
- reglas activadas;
- parámetros;
- escenario;
- restricciones;
- alternativa evaluada;
- motivo de viabilidad o no viabilidad.

La recomendación no debe ser una caja negra.

---

## 25. No optimización ciega

EIOS no debe intentar maximizar una única variable como:

- menor precio;
- mayor margen;
- mayor descuento;
- mayor plazo;
- mayor cantidad.

La solución óptima será una decisión empresarial multidimensional sujeta a restricciones.

---

## 26. Regla de seguridad

> **Una operación no es viable simplemente porque sea barata.**

> **Una operación no es viable simplemente porque tenga margen.**

> **Una operación no es viable simplemente porque resuelva un riesgo de stock.**

> **Una operación es viable cuando satisface las restricciones críticas aplicables y mantiene un nivel aceptable de valor y riesgo.**

---

## 27. Decisiones todavía pendientes

No se cierran todavía:

- fórmula matemática universal de viabilidad;
- función de optimización;
- pesos de factores;
- ranking de alternativas;
- algoritmo de generación de escenarios;
- número máximo de escenarios;
- método para seleccionar la mejor alternativa;
- integración definitiva con PMR;
- integración definitiva con BATNA/ZOPA.

Estas cuestiones deberán resolverse después de validar la arquitectura conceptual.

---

## 28. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
