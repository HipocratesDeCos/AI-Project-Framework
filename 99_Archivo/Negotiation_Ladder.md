# Negotiation_Ladder

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Motor estratégico de negociación  
**Relación:** [[Viability_Frontier]] + [[Viability_Scenario_Engine]] + [[Motor_Escenarios]] + CRC + Assurance  
**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir la **Negotiation Ladder EIOS** como mecanismo para transformar las alternativas viables detectadas por el sistema en una estrategia ordenada de negociación.

La Negotiation Ladder responde:

> **¿En qué orden debería intentar conseguir las condiciones que hacen viable y conveniente la operación?**

No sustituye a:

- la Frontera de Viabilidad;
- el Motor de Escenarios;
- la CRC;
- la decisión del CEO.

---

## 2. Principio fundamental

EIOS no debe limitarse a recomendar:

> “Negocia.”

Debe poder proponer:

1. qué pedir primero;
2. qué concesión aceptar después;
3. cuál es la alternativa de respaldo;
4. cuál es el límite de aceptación;
5. cuándo abandonar la negociación.

---

## 3. Estructura básica

```text
OBJETIVO
   ↓
PRIMERA PETICIÓN
   ↓
CONCESIÓN 1
   ↓
CONCESIÓN 2
   ↓
FALLBACK
   ↓
WALK-AWAY
```

Cada escalón debe corresponder a un escenario evaluado y trazable.

---

## 4. Objetivo

El objetivo representa la condición que EIOS intentaría conseguir inicialmente.

Debe apoyarse en:

- precio objetivo;
- CEA;
- TCO;
- stock;
- liquidez;
- riesgo;
- condiciones comerciales;
- alternativas disponibles.

El objetivo no tiene por qué ser el escenario más barato.

Debe ser una condición **ambiciosa pero defendible**.

---

## 5. Primera petición

La primera petición debe establecer la posición inicial de negociación.

Ejemplo conceptual:

```text
Precio objetivo: 18,00 €
Pago: 90 días
Cantidad: 1.000
Transporte: incluido
```

La petición debe poder explicar:

> por qué se propone esa combinación.

No debe ser un número arbitrario.

---

## 6. Concesiones

Cada concesión debe tener un coste económico o estratégico conocido.

Ejemplo:

```text
Petición inicial
18,00 € + 90 días

↓ concesión

18,20 € + 75 días

↓ concesión

18,40 € + 60 días
```

EIOS debe conocer el impacto de cada movimiento sobre la viabilidad.

---

## 7. Principio de reciprocidad

Una concesión del CEO no debe producirse automáticamente.

Regla:

> **Toda concesión relevante debería buscar una contraprestación del proveedor cuando sea negociacionalmente razonable.**

Ejemplo:

```text
EIOS concede:
+0,20 € de precio

A cambio:
+30 días de pago
```

La reciprocidad concreta dependerá del contexto.

---

## 8. Fallback

El fallback es la mejor alternativa negociadora antes de llegar al límite.

Debe ser un escenario realmente viable.

Ejemplo:

> 18,40 € + 60 días + transporte incluido.

No debe utilizarse un fallback que el motor haya clasificado como:

- no viable;
- no evaluable;
- incompatible con una salvaguarda.

---

## 9. Walk-away

El walk-away representa el punto a partir del cual la operación deja de ser aceptable.

No es necesariamente:

> “el precio máximo”.

Puede depender de varias variables.

Ejemplo:

```text
Precio ≤ 18,40 €
Y
Pago ≥ 60 días
Y
Cantidad ≤ 800
```

La combinación completa puede constituir el verdadero límite.

---

## 10. Walk-away multidimensional

Una de las características diferenciales de EIOS debe ser que el límite de negociación pueda ser multidimensional.

Ejemplo:

```text
Si precio = 18,20 €
→ pago mínimo 60 días

Si precio = 18,40 €
→ pago mínimo 75 días

Si pago = 90 días
→ precio máximo 18,60 €
```

Por tanto:

> **El límite no siempre es una cifra; puede ser una función de condiciones.**

---

## 11. Condiciones no negociables

La Negotiation Ladder no puede cruzar:

- salvaguardas financieras críticas;
- restricciones empresariales no anulables;
- condiciones contractuales incompatibles;
- datos críticos no válidos;
- restricciones de seguridad.

Estas condiciones tienen prioridad sobre cualquier objetivo de negociación.

---

## 12. Evidencia

Cada escalón debe poder justificar:

- escenario utilizado;
- datos;
- evidencias;
- reglas;
- parámetros;
- impacto económico;
- impacto sobre stock;
- impacto financiero;
- riesgo;
- nivel de confianza.

La recomendación debe ser reproducible mediante el Assurance Framework.

---

## 13. Calidad de cada escalón

Cada escalón debe tener un estado de confianza:

```text
ALTA
MEDIA
BAJA
NO EVALUABLE
```

Una condición de negociación basada en evidencia baja no debería presentarse como un límite duro.

---

## 14. Tipos de petición

Inicialmente pueden existir:

### Petición económica

Precio, descuento, rappel.

### Petición financiera

Plazo de pago, calendario.

### Petición logística

Entrega, transporte, fraccionamiento.

### Petición de cantidad

Cantidad mínima, cantidad total, lotes.

### Petición de riesgo

Garantías, cobertura, sustitución, condiciones de servicio.

### Petición combinada

Combinación de varias condiciones.

---

## 15. Selección de la primera petición

Cuando existan varias alternativas viables, EIOS deberá considerar:

- valor económico;
- probabilidad estimada de aceptación, cuando exista evidencia;
- impacto de la concesión;
- distancia respecto a las condiciones actuales;
- importancia de la relación con el proveedor;
- riesgo;
- BATNA disponible.

La metodología definitiva para estimar probabilidad de aceptación queda pendiente.

---

## 16. BATNA

La Negotiation Ladder debe poder incorporar la alternativa disponible si no se alcanza un acuerdo.

Ejemplos:

- proveedor alternativo;
- compra posterior;
- reducción de cantidad;
- utilización de stock;
- retraso de compra;
- otra alternativa empresarial.

BATNA no debe inventarse.

Debe existir evidencia suficiente para considerarlo una alternativa real.

---

## 17. ZOPA

Cuando pueda determinarse:

- límite de aceptación de EIOS;
- límite estimado del proveedor;

EIOS podrá analizar la posible:

**ZOPA — Zone of Possible Agreement**

La ZOPA será una herramienta de apoyo, no una verdad absoluta, porque el límite del proveedor puede ser desconocido.

---

## 18. Estrategia adaptativa

La ladder no debe ser necesariamente rígida.

Si el proveedor responde con una nueva condición:

```text
Respuesta proveedor
       ↓
Nuevo escenario
       ↓
Viability Scenario Engine
       ↓
Nueva evaluación
       ↓
Nueva ladder
```

La estrategia debe poder recalcularse durante la negociación.

---

## 19. Ejemplo completo

### Situación inicial

```text
Precio: 18,50 €
Cantidad: 1.000
Pago: 30 días
Transporte: 300 €
```

### Evaluación

**NO VIABLE**

Causas:

- riesgo financiero;
- exceso de stock;
- condiciones comerciales desfavorables.

### Ladder propuesta

#### Objetivo

```text
18,00 €
90 días
1.000 unidades
Transporte incluido
```

#### Primera petición

```text
18,00 €
90 días
1.000 unidades
Transporte incluido
```

#### Concesión 1

```text
18,20 €
75 días
1.000 unidades
Transporte incluido
```

#### Concesión 2

```text
18,40 €
60 días
800 unidades
Transporte incluido
```

#### Fallback

```text
18,40 €
60 días
700 unidades
```

#### Walk-away

```text
No aceptar:
Precio > 18,40 €
cuando pago < 60 días
y cantidad > 800 unidades.
```

---

## 20. Negociación con múltiples variables

EIOS no debe asumir que siempre existe una secuencia lineal.

Puede existir:

```text
                  OPERACIÓN NO VIABLE
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Precio       Pago      Cantidad
              │          │          │
              └────┬─────┴─────┬────┘
                   ▼           ▼
                Ruta A       Ruta B
                   │           │
                   ▼           ▼
                VIABLE       VIABLE
                   │           │
                   └─────┬─────┘
                         ▼
                  MEJOR ESTRATEGIA
```

La mejor ruta no será necesariamente la que produzca el menor precio.

---

## 21. Coste de concesión

EIOS deberá poder representar el coste de cada concesión.

Ejemplo:

```text
Concesión:
+0,20 € de precio

Beneficio obtenido:
+30 días de pago

Resultado:
mejora financiera > coste económico del incremento de precio
```

Esto conecta directamente la negociación con CAPA 4.

---

## 22. Valor de la concesión

Una concesión puede tener distinto valor para las partes.

EIOS debería diferenciar conceptualmente:

**Coste para nosotros**

vs.

**Valor potencial para el proveedor.**

Esta información permitirá diseñar intercambios de concesiones más inteligentes.

La metodología definitiva para estimar el valor para el proveedor queda pendiente.

---

## 23. Respuesta a rechazo

Cuando el proveedor rechace una petición:

```text
RECHAZO
  ↓
registrar respuesta
  ↓
actualizar escenario
  ↓
recalcular viabilidad
  ↓
seleccionar siguiente escalón
```

No debe saltarse automáticamente al walk-away.

---

## 24. Señales de ruptura

La ladder podrá recomendar abandonar la negociación cuando:

- todas las alternativas viables hayan sido rechazadas;
- se haya alcanzado el walk-away;
- exista una restricción crítica no resoluble;
- la BATNA sea superior;
- el riesgo haya aumentado hasta niveles no aceptables.

---

## 25. Resultado para el CEO

La interfaz debe mostrar algo equivalente a:

```text
🟡 NEGOCIAR

OBJETIVO
18,00 € + 90 días

PRIMERA PETICIÓN
18,00 € + 90 días + transporte incluido

CONCESIÓN 1
18,20 € + 75 días

FALLBACK
18,40 € + 60 días + 800 uds

WALK-AWAY
>18,40 € con pago <60 días

BATNA
Proveedor B

Confianza
MEDIA-ALTA
```

La profundidad adicional debe quedar disponible bajo demanda.

---

## 26. Relación con Viability Frontier

[[Viability_Frontier]] define:

> **qué soluciones son viables.**

Negotiation Ladder define:

> **cómo intentar alcanzarlas.**

---

## 27. Relación con Viability Scenario Engine

[[Viability_Scenario_Engine]] genera y evalúa escenarios.

Negotiation Ladder los ordena estratégicamente.

```text
Viability Frontier
        ↓
Scenario Engine
        ↓
Escenarios viables
        ↓
Negotiation Ladder
        ↓
estrategia
```

---

## 28. Relación con CRC

Negotiation Ladder no toma la decisión final.

La CRC mantiene la autoridad sobre:

- COMPRAR;
- NEGOCIAR;
- COMPRAR CONDICIONADO;
- NO COMPRAR;
- INFORMACIÓN INSUFICIENTE.

---

## 29. Relación con Assurance

Cada escalón debe ser auditable.

Debe poder reconstruirse:

```text
Escalón
 ↓
Escenario
 ↓
Evidencia
 ↓
Regla
 ↓
Parámetro
 ↓
Resultado
```

---

## 30. Reglas de seguridad

> **No recomendar concesiones que crucen una salvaguarda crítica.**

> **No presentar como walk-away un límite construido sobre evidencia insuficiente.**

> **No inventar BATNA ni ZOPA.**

> **No recomendar una concesión sin conocer su impacto.**

> **No convertir una alternativa viable en decisión final automáticamente.**

> **Toda modificación durante la negociación genera un nuevo escenario.**

---

## 31. Decisiones pendientes

No se cierran todavía:

- fórmula para seleccionar la primera petición;
- probabilidad de aceptación;
- valor de concesión para el proveedor;
- modelo de BATNA;
- estimación de ZOPA;
- función de coste de concesión;
- número óptimo de escalones;
- estrategia adaptativa;
- integración con comunicación o ejecución automática.

---

## 32. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
