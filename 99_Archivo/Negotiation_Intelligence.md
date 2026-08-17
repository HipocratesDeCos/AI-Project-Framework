# Negotiation_Intelligence

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Inteligencia estratégica de negociación  
**Relación:** [[Viability_Frontier]] + [[Viability_Scenario_Engine]] + [[Decision_Twin]] + [[Negotiation_Ladder]] + Assurance + CRC  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir la **Negotiation Intelligence** como el componente de EIOS encargado de determinar:

- qué condiciones conviene solicitar;
- qué concesiones puede ofrecer EIOS;
- qué contraprestación debería exigir;
- qué intercambios producen mayor valor;
- qué alternativas son negociablemente plausibles;
- y cuándo una negociación deja de ser conveniente.

No sustituye la decisión del CEO.

---

## 2. Diferenciación respecto a un asistente conversacional

La Negotiation Intelligence no debe limitarse a generar frases como:

> “Pide un descuento del 5 %.”

Debe poder responder:

> **“Pide esta condición porque modifica estas variables, cruza la frontera de viabilidad y produce un resultado superior a las alternativas disponibles.”**

La recomendación debe estar conectada con datos, evidencias, escenarios y reglas.

---

## 3. Principio fundamental

> **No negociar una variable por sí misma; negociar el intercambio de valor entre las partes.**

Ejemplo:

```text
EIOS concede:
+0,20 € de precio

Proveedor concede:
+30 días de pago
```

La decisión debe evaluarse por su efecto empresarial completo.

---

## 4. Objetivo de la negociación

La Negotiation Intelligence debe perseguir inicialmente cuatro objetivos:

1. conseguir una operación viable;
2. preservar el valor económico para la empresa;
3. minimizar concesiones innecesarias;
4. mantener una alternativa de salida.

La maximización de una sola variable no constituye el objetivo.

---

## 5. Variables de negociación

### Variables que EIOS puede solicitar

- reducción de precio;
- descuento;
- rappel;
- ampliación del plazo de pago;
- transporte incluido;
- seguro incluido;
- reducción de cantidad mínima;
- fraccionamiento de entregas;
- adelanto de entrega;
- garantías;
- sustitución;
- condiciones de servicio;
- otras condiciones comerciales.

### Variables que EIOS puede ofrecer

- volumen;
- compromiso de compra;
- mayor permanencia como cliente;
- previsión de demanda;
- flexibilidad de entrega;
- plazo de relación;
- otras contraprestaciones autorizadas.

La disponibilidad de una variable deberá estar definida por la política empresarial.

---

## 6. Valor de una concesión

Toda concesión relevante debe poder representarse desde dos perspectivas:

### Coste para EIOS

¿Qué valor económico, operativo o financiero pierde la empresa?

### Valor potencial para el proveedor

¿Qué valor puede tener esa concesión para la contraparte?

La metodología para estimar el valor para el proveedor queda pendiente de validación.

---

## 7. Intercambio de concesiones

La negociación puede plantearse como intercambio:

```text
CONCESIÓN EIOS
       +
CONCESIÓN PROVEEDOR
       ↓
RESULTADO
```

Ejemplo:

```text
EIOS:
+100 unidades

Proveedor:
-0,30 €/unidad
+30 días de pago
```

La combinación debe evaluarse como un nuevo escenario.

---

## 8. Principio de reciprocidad

Regla:

> **Una concesión relevante de EIOS debería buscar una contraprestación relevante del proveedor cuando sea razonablemente negociable.**

No significa que toda concesión deba tener una compensación explícita.

La reciprocidad es una estrategia, no una obligación matemática.

---

## 9. Coste de concesión

EIOS deberá estimar el impacto de conceder algo.

Ejemplo:

```text
Precio actual: 18,20 €
Precio concedido: 18,40 €

Coste de concesión:
+0,20 €/unidad
```

Pero el coste final debe evaluarse sobre:

- cantidad;
- TCO;
- margen;
- liquidez;
- stock;
- riesgo.

---

## 10. Valor de la contraprestación

Ejemplo:

```text
Coste de EIOS:
+0,20 €/unidad

Contraprestación:
+30 días de pago

Impacto:
mejora financiera proyectada
```

La negociación debe analizar el intercambio completo y no comparar variables aisladas.

---

## 11. Paquetes de negociación

Cuando sea conveniente, EIOS podrá crear paquetes:

### Paquete A

18,20 € + 60 días

### Paquete B

18,40 € + 90 días + transporte incluido

### Paquete C

18,50 € + 90 días + cantidad reducida

Los paquetes se evalúan como escenarios independientes.

---

## 12. Intercambios equivalentes

Dos paquetes pueden ser económicamente diferentes pero empresarialmente equivalentes.

```text
Paquete A → VIABLE
Paquete B → VIABLE

Valor económico ajustado:
A ≈ B
```

En ese caso EIOS no debe inventar una preferencia.

Puede clasificarlos como:

> **alternativas equivalentes**

y utilizar otros factores para seleccionar la estrategia.

---

## 13. Negociabilidad

Se incorpora el concepto:

**NEGOCIABILIDAD**

No equivale a viabilidad.

Una alternativa puede ser:

```text
Viabilidad: ALTA
Negociabilidad: BAJA
```

o:

```text
Viabilidad: MEDIA
Negociabilidad: ALTA
```

La metodología para estimar negociabilidad deberá construirse a partir de evidencia disponible.

---

## 14. Evidencias potenciales de negociabilidad

Cuando exista información suficiente, pueden utilizarse:

- histórico de concesiones del proveedor;
- comportamiento en negociaciones anteriores;
- alternativas de proveedor;
- sensibilidad del proveedor al volumen;
- historial de plazos de pago;
- respuesta histórica a descuentos;
- estacionalidad de la oferta;
- dependencia mutua;
- poder de negociación;
- otras señales disponibles.

No deben presentarse inferencias como hechos confirmados.

---

## 15. BATNA

La Negotiation Intelligence puede utilizar:

**BATNA — Best Alternative to a Negotiated Agreement**

solo cuando exista evidencia suficiente.

Ejemplos:

- proveedor alternativo;
- compra posterior;
- reducción de cantidad;
- utilización de stock;
- aplazamiento;
- otra solución empresarial.

Si la BATNA no está confirmada:

> **BATNA no confirmada**

No debe inventarse.

---

## 16. ZOPA

Cuando exista información suficiente sobre las condiciones aceptables de ambas partes, EIOS podrá estimar:

**ZOPA — Zone of Possible Agreement**

Pero debe distinguir:

- ZOPA conocida;
- ZOPA estimada;
- ZOPA desconocida.

El sistema no debe presentar como hecho un límite del proveedor que no conoce.

---

## 17. Primera petición

Negotiation Intelligence debe recomendar la primera petición utilizando:

- objetivo;
- frontera de viabilidad;
- sensibilidad;
- negociabilidad;
- valor de concesión;
- evidencia histórica;
- BATNA;
- riesgo.

La primera petición debe ser:

> **ambiciosa pero defendible.**

---

## 18. Secuencia de concesiones

La secuencia deberá intentar preservar valor.

Ejemplo:

```text
Petición inicial
     ↓
Concesión pequeña
     ↓
Contraprestación
     ↓
Concesión intermedia
     ↓
Contraprestación
     ↓
Fallback
     ↓
Walk-away
```

Cada escalón debe corresponder a un escenario evaluado.

---

## 19. Concesión mínima necesaria

EIOS debería poder responder:

> **¿Cuál es la menor concesión del proveedor que cruza la frontera de viabilidad?**

Ejemplo:

```text
Pago 45 días → NO VIABLE
Pago 50 días → NO VIABLE
Pago 55 días → VIABLE
```

Resultado:

> Condición mínima estimada: 55 días.

Esta capacidad conecta directamente con Viability Scenario Engine.

---

## 20. Intercambio de mínimo coste

Cuando existan varias formas de cruzar la frontera:

```text
A:
-0,30 € precio

B:
+30 días pago

C:
-200 unidades
```

EIOS debe poder comparar el coste económico y estratégico de cada alternativa.

No existe obligación de que la alternativa más barata sea la mejor.

---

## 21. Sensibilidad negociadora

La Negotiation Intelligence deberá identificar:

> **qué variable tiene mayor capacidad de transformar una operación.**

Ejemplo:

```text
Precio     → impacto medio
Cantidad   → impacto alto
Pago       → impacto muy alto
Transporte → impacto bajo
```

Esto permite concentrar la negociación donde tiene mayor capacidad de cambiar el resultado.

---

## 22. Concesiones asimétricas

Una característica potencialmente diferencial:

> **buscar concesiones de bajo coste para EIOS pero alto valor para el proveedor.**

Ejemplo conceptual:

```text
Coste EIOS: bajo
Valor proveedor: alto
```

Esto puede generar intercambios más eficientes.

La identificación automática de ese valor queda pendiente de metodología y evidencia.

---

## 23. Señales de poder de negociación

La Negotiation Intelligence podrá considerar, cuando existan datos:

- proveedores alternativos;
- dependencia del proveedor;
- dependencia de EIOS;
- concentración;
- urgencia;
- disponibilidad;
- volumen;
- historial;
- BATNA.

No debe convertir estas variables en conclusiones absolutas si la evidencia es débil.

---

## 24. Propuesta de estrategia

La salida esperada podría ser:

```text
ESTRATEGIA RECOMENDADA

1. Solicitar:
   18,00 € + 90 días

2. Si rechaza precio:
   mantener 18,20 € y exigir 60 días

3. Si rechaza plazo:
   reducir cantidad a 700 unidades

4. Fallback:
   18,40 € + 60 días

5. Walk-away:
   >18,40 € con pago <60 días
```

Cada paso debe estar sustentado por escenarios reales.

---

## 25. Negociación adaptativa

Durante una negociación real:

```text
RESPUESTA DEL PROVEEDOR
        ↓
NUEVO ESCENARIO
        ↓
VIABILITY SCENARIO ENGINE
        ↓
RECALCULAR
        ↓
NEGOTIATION INTELLIGENCE
        ↓
SIGUIENTE MOVIMIENTO
```

La ladder puede cambiar dinámicamente.

---

## 26. Decisiones del proveedor

Cuando el proveedor ofrezca una contrapropuesta:

> EIOS no debe evaluar únicamente la concesión aislada.

Debe recalcular:

- CEA;
- TCO;
- stock;
- finanzas;
- riesgo;
- viabilidad;
- robustez;
- estrategia.

---

## 27. Robustez

Una alternativa negociada puede ser viable pero frágil.

Ejemplo:

```text
18,30 € + 60 días
→ VIABLE

18,31 € + 60 días
→ NO VIABLE
```

La alternativa tiene poco margen de viabilidad.

Negotiation Intelligence debería preferir, cuando los demás factores sean comparables, soluciones más robustas.

---

## 28. Confianza de la estrategia

La estrategia deberá indicar su nivel de confianza.

```text
ALTA
MEDIA
BAJA
NO EVALUABLE
```

La confianza depende de:

- calidad de datos;
- evidencia;
- histórico;
- negociabilidad;
- BATNA;
- ZOPA;
- estabilidad de la frontera.

---

## 29. Assurance

Toda recomendación estratégica deberá poder rastrearse:

```text
Estrategia
 ↓
Escenario
 ↓
Viabilidad
 ↓
Reglas
 ↓
Evidencia
 ↓
Datos
```

No debe existir una estrategia que no pueda explicarse.

---

## 30. Relación con Viability Frontier

[[Viability_Frontier]] determina:

> **qué condiciones son viables.**

Negotiation Intelligence determina:

> **qué intercambios conviene intentar para alcanzarlas.**

---

## 31. Relación con Viability Scenario Engine

[[Viability_Scenario_Engine]] genera y evalúa escenarios.

Negotiation Intelligence determina:

- cuáles son negociacionalmente interesantes;
- qué concesiones requieren;
- cómo ordenarlos.

---

## 32. Relación con Decision Twin

[[Decision_Twin]] permite probar:

> “¿Qué pasa si acepto esta contrapropuesta?”

Negotiation Intelligence interpreta el resultado y propone el siguiente movimiento.

---

## 33. Relación con Negotiation Ladder

[[Negotiation_Ladder]] representa la secuencia operativa:

- objetivo;
- primera petición;
- concesión 1;
- concesión 2;
- fallback;
- walk-away.

Negotiation Intelligence es el razonamiento que justifica esa secuencia.

---

## 34. Relación con CRC

Negotiation Intelligence no sustituye a la CRC.

La CRC conserva la decisión empresarial final.

---

## 35. Principios de seguridad

> **No inventar BATNA, ZOPA ni límites del proveedor.**

> **No recomendar concesiones que vulneren salvaguardas críticas.**

> **No recomendar concesiones sin evaluar su impacto.**

> **No confundir viabilidad con negociabilidad.**

> **No presentar una inferencia como evidencia confirmada.**

> **Toda contrapropuesta relevante genera un nuevo escenario.**

---

## 36. Decisiones pendientes

No se cierran todavía:

- fórmula de valor de concesión;
- estimación del valor para el proveedor;
- modelo de negociabilidad;
- estimación de probabilidad de aceptación;
- BATNA probabilística;
- ZOPA;
- señales de poder de negociación;
- función de ranking de estrategias;
- estrategia óptima de concesiones;
- integración con canales de comunicación;
- eventual ejecución automática.

---

## 37. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
