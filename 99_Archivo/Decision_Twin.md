# Decision_Twin

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Modelo transversal de la operación / nueva propuesta de valor  
**Relación:** [[Viability_Frontier]] + [[Viability_Scenario_Engine]] + [[Negotiation_Ladder]] + [[Motor_Escenarios]] + CRC + Assurance  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir conceptualmente el **Decision Twin** como una representación dinámica de una operación de compra que permite simular cómo cambia su viabilidad cuando se modifican sus condiciones.

El Decision Twin responde:

> **¿Qué pasa con la operación si cambio una o varias variables?**

No es un gemelo digital de toda la empresa.

Es un **gemelo de decisión de la operación concreta**.

---

## 2. Principio fundamental

El Decision Twin debe representar, en un estado reproducible:

- condiciones de la propuesta;
- datos relevantes;
- evidencias;
- parámetros;
- resultados de CAPA 1–5;
- escenarios;
- restricciones;
- viabilidad;
- recomendación;
- estrategia de negociación.

---

## 3. Representación conceptual

```text
                    DECISION TWIN
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
      PRECIO           STOCK           FINANZAS
        │                │                │
        ▼                ▼                ▼
       TCO             DEMANDA          LIQUIDEZ
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                     PROVEEDOR
                         │
                         ▼
                       RIESGO
                         │
                         ▼
                  VIABILIDAD
                         │
                         ▼
                   NEGOCIACIÓN
                         │
                         ▼
                    DECISIÓN
```

---

## 4. Estado inicial

Toda operación comienza con:

**S0 — escenario base**

Debe contener al menos:

- producto;
- RFP;
- proveedor;
- cantidad;
- unidad;
- precio;
- descuentos;
- rappels;
- plazo de pago;
- fecha;
- transporte;
- seguro;
- entrega;
- datos de stock;
- datos de demanda;
- situación financiera relevante;
- condiciones del proveedor;
- evidencias;
- parámetros aplicables.

---

## 5. Variables modificables

El Decision Twin debe permitir modificar variables que el modelo haya clasificado como negociables.

Ejemplos:

- precio;
- cantidad;
- descuento;
- rappel;
- plazo de pago;
- transporte;
- seguro;
- fecha de entrega;
- fraccionamiento;
- garantías;
- otras condiciones comerciales.

---

## 6. Variables no modificables

El usuario no debe poder convertir en “variable negociable” algo que el modelo haya definido como:

- salvaguarda;
- restricción crítica;
- dato histórico;
- hecho consumado;
- condición contractual fija;
- variable no disponible para negociación.

---

## 7. Pregunta what-if

La función principal del Decision Twin será:

```text
¿QUÉ PASA SI...?
```

Ejemplos:

> ¿Qué pasa si el proveedor baja 0,30 €?

> ¿Qué pasa si concede 60 días?

> ¿Qué pasa si compro 700 unidades?

> ¿Qué pasa si entrega en dos lotes?

> ¿Qué pasa si mantiene el precio pero elimina el transporte?

Cada cambio genera un escenario nuevo.

---

## 8. Recálculo

Toda modificación relevante debe provocar:

```text
CAMBIO
  ↓
NUEVO ESCENARIO
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
VIABILITY FRONTIER
  ↓
CRC
```

No todos los cambios afectan a todas las capas.

---

## 9. Comparación de escenarios

El Decision Twin debe permitir comparar:

```text
S0 — situación actual
S1 — menor precio
S2 — mayor plazo
S3 — menor cantidad
S4 — combinación
```

Y mostrar las diferencias:

- precio;
- CEA;
- TCO;
- cobertura;
- stock;
- liquidez;
- riesgo;
- viabilidad;
- estrategia de negociación.

---

## 10. Delta de decisión

Una capacidad importante será mostrar:

> **¿Qué ha cambiado realmente respecto al escenario anterior?**

Ejemplo:

```text
S0 → S1

Precio:
18,50 € → 18,30 €

Pago:
30 → 60 días

Stock:
138 → 126 días

Liquidez:
RIESGO → ACEPTABLE

Viabilidad:
NO VIABLE → VIABLE
```

El CEO debe poder comprender el efecto de la modificación sin revisar todos los cálculos.

---

## 11. Sensibilidad

El Decision Twin debe poder identificar qué variables tienen mayor impacto sobre la decisión.

Ejemplo:

```text
VARIABLE             IMPACTO

Precio               ALTO
Plazo de pago        MUY ALTO
Cantidad             ALTO
Transporte           MEDIO
Rappel               BAJO
```

La clasificación definitiva será metodológica y deberá validarse con casos reales.

---

## 12. Frontera de Viabilidad

El Decision Twin consume:

[[Viability_Frontier]]

para determinar si cada escenario:

- está dentro;
- está fuera;
- está en el límite;
- no puede evaluarse.

---

## 13. Motor de escenarios

El Decision Twin utiliza:

[[Viability_Scenario_Engine]]

para generar y evaluar escenarios candidatos.

El Decision Twin conserva la representación y permite explorarlos.

---

## 14. Negotiation Ladder

Cuando existen escenarios viables, el Decision Twin alimenta:

[[Negotiation_Ladder]]

para construir:

- objetivo;
- primera petición;
- concesiones;
- fallback;
- walk-away.

---

## 15. Simulación combinatoria

El Decision Twin podrá explorar combinaciones.

Ejemplo:

```text
Precio -0,10 €
+
Pago +30 días
+
Cantidad -100
```

y comparar el resultado con:

```text
Precio -0,30 €
```

El objetivo no es explorar combinaciones infinitas.

La búsqueda estará limitada por parámetros de seguridad y relevancia.

---

## 16. Escenario manual

El usuario podrá introducir manualmente una modificación:

```text
Precio = 18,20 €
Pago = 60 días
Cantidad = 800
```

EIOS recalculará el escenario.

Esto permite utilizar el sistema durante una negociación real.

---

## 17. Escenario sugerido por EIOS

EIOS también podrá proponer:

> “Prueba con 18,30 € + 60 días.”

La sugerencia debe estar respaldada por:

- evidencia;
- reglas;
- viabilidad;
- impacto;
- confianza.

No debe aparecer como una ocurrencia del modelo.

---

## 18. Explicación causal

Cada cambio deberá poder explicar:

```text
CAMBIO
 ↓
EFECTO
 ↓
REGLA AFECTADA
 ↓
RESULTADO
```

Ejemplo:

> Aumentar el plazo de 30 a 60 días reduce el riesgo financiero proyectado y cruza el umbral configurado.

---

## 19. Evidencia

Cada estado del Decision Twin deberá conservar:

- fuente de datos;
- fecha de datos;
- evidencia;
- parámetros;
- reglas;
- escenario;
- versión del método de demanda;
- calidad de datos;
- nivel de confianza.

Esto permite reproducibilidad.

---

## 20. Fecha de referencia

El Decision Twin debe respetar la fecha de decisión.

Para replay histórico:

> no se utilizarán datos posteriores a la fecha de referencia.

Esto evita data leakage.

---

## 21. Snapshot

Cada escenario importante debe poder congelarse como:

**Decision Snapshot**

El snapshot permitirá reconstruir exactamente:

- condiciones;
- resultados;
- evidencias;
- parámetros;
- recomendación.

---

## 22. Interacción con el CEO

La experiencia debe ser inmediata.

Conceptualmente:

```text
                    OPERACIÓN
                      │
                ESTADO ACTUAL
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       VIABLE                NO VIABLE
          │                       │
          │              ¿QUÉ CAMBIAMOS?
          │                       │
          └───────────┬───────────┘
                      ▼
               SIMULAR CAMBIO
                      │
                      ▼
                 NUEVO ESTADO
```

El usuario no debería tener que entender el modelo matemático para utilizarlo.

---

## 23. Vista ejecutiva

La salida principal debería mostrar:

```text
ESTADO
🟡 NEGOCIAR

VIABILIDAD
NO VIABLE

MEJOR ALTERNATIVA
18,30 € + 60 días

IMPACTO
Liquidez: mejora
Stock: adecuado
TCO: -0,20 €/ud

WALK-AWAY
18,40 € con pago <60 días

CONFIANZA
MEDIA-ALTA
```

---

## 24. Vista de detalle

Bajo demanda, el usuario podrá consultar:

- cálculos;
- reglas;
- parámetros;
- evidencias;
- históricos;
- escenarios;
- comparables;
- calidad de datos;
- trazabilidad.

Esto mantiene el principio de comunicación ejecutiva y evita saturación.

---

## 25. Humano en el circuito

El Decision Twin no ejecuta automáticamente una decisión empresarial.

Puede:

- analizar;
- simular;
- comparar;
- recomendar;
- explicar.

La decisión y la aceptación de condiciones corresponden al usuario autorizado.

---

## 26. Override

Si el usuario elige una alternativa diferente a la recomendada:

```text
Recomendación EIOS
        ↓
Decisión humana
        ↓
Motivo
        ↓
Registro
```

El override queda asociado al Decision Snapshot.

---

## 27. Estado y persistencia

Un Decision Twin debe poder pasar por estados:

- BORRADOR;
- EN ANÁLISIS;
- NEGOCIACIÓN;
- VIABLE;
- NO VIABLE;
- CERRADO;
- CANCELADO.

Los estados no deben sobrescribirse históricamente.

---

## 28. Relación con Assurance

El Decision Twin debe ser completamente auditable.

Debe poder reconstruirse:

```text
Snapshot
 ↓
Escenario
 ↓
Datos
 ↓
Evidencias
 ↓
Parámetros
 ↓
Reglas
 ↓
Viabilidad
 ↓
Decisión
```

---

## 29. Regla de seguridad

> **Cada cambio relevante debe crear un nuevo escenario.**

> **No se deben utilizar datos futuros en una simulación histórica.**

> **Una simulación no constituye una decisión empresarial.**

> **Una recomendación del Decision Twin debe estar respaldada por evidencia suficiente.**

> **Los escenarios no deben sobrescribirse.**

> **El usuario mantiene control sobre la decisión final.**

---

## 30. Decisiones pendientes

No se cierran todavía:

- granularidad del snapshot;
- arquitectura técnica;
- persistencia;
- interfaz definitiva;
- número máximo de escenarios simultáneos;
- visualización comparativa;
- cálculo de sensibilidad;
- optimización combinatoria;
- integración con agentes;
- integración con ejecución real de negociación.

---

## 31. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
