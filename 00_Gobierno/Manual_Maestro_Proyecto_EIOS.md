# MANUAL MAESTRO DEL PROYECTO EIOS

## EIOS — Enterprise Intelligent Operations System

**Documento:** Manual Maestro del Proyecto EIOS (MMP-EIOS)  
**Versión:** 2.0  
**Estado:** APROBADO  
**Fecha:** 19/08/2026  
**Ubicación oficial:** `00_Gobierno/Manual_Maestro_Proyecto_EIOS.md`

---

# 1. FUNCIÓN DEL MANUAL

El Manual Maestro del Proyecto EIOS (MMP-EIOS) es el **documento maestro de orientación, navegación y continuidad del proyecto**.

Su función es permitir que una persona o una IA pueda recuperar rápidamente:

- qué es EIOS;
- cuál es su propósito;
- cuál es el alcance actual;
- cómo se organiza la documentación;
- dónde se encuentra la autoridad de cada materia;
- cuáles son los principales componentes del sistema;
- cuál es el estado general del proyecto;
- dónde debe continuar el trabajo.

El Manual Maestro **no sustituye** a los documentos que poseen autoridad específica.

No debe utilizarse como segunda fuente normativa ni como repositorio paralelo de toda la lógica funcional del sistema.

---

# 2. AUTORIDAD DEL MANUAL

El Manual Maestro es un documento de **continuidad y navegación**.

Su autoridad está subordinada a la:

`00_Gobierno/Matriz_Autoridad_Documental.md`

Cuando exista una discrepancia entre este documento y un documento con mayor autoridad, prevalece el documento de mayor autoridad.

El Manual puede resumir conceptos de otros documentos, pero no puede redefinirlos.

---

# 3. DOCUMENTOS FUNDAMENTALES

La estructura de gobierno de EIOS se apoya principalmente en:

```text
00_Gobierno/
├── Project_Charter.md
├── Project_Context.md
├── Project_Governance.md
├── Matriz_Autoridad_Documental.md
├── Manual_Maestro_Proyecto_EIOS.md
├── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
└── EIOS_Assurance_Framework.md
```

### Project Charter

Define la identidad, propósito, visión, alcance y límites fundamentales del proyecto.

### Project Context

Conserva el contexto esencial para recuperar la continuidad del proyecto.

### Project Governance

Define las reglas de gobierno del proyecto y de su documentación.

### Matriz de Autoridad Documental

Determina qué documento prevalece cuando existe una discrepancia.

### Manual Maestro

Orienta y conecta la documentación del proyecto.

### Salvaguarda Vertical MVP

Define las restricciones y decisiones congeladas aplicables al Vertical MVP.

### Assurance Framework

Define el marco transversal de assurance.

---

# 4. IDENTIDAD EIOS

**EIOS — Enterprise Intelligent Operations System**

EIOS es un sistema inteligente de apoyo a la decisión empresarial basado en datos.

La arquitectura conceptual se estructura como:

**CORE + VERTICAL**

El Vertical MVP actual se centra en:

**Intelligent Procurement Decision & Negotiation**

El objetivo es ayudar al CEO y al responsable de compras a evaluar, simular, negociar y tomar mejores decisiones de adquisición.

La decisión final corresponde al usuario autorizado.

> **EIOS analiza, evalúa, simula, explica y recomienda. El decisor decide.**

---

# 5. ALCANCE ACTUAL DEL VERTICAL MVP

El núcleo actual comprende:

- decisión de compras;
- evaluación financiera;
- evaluación operativa;
- evaluación de proveedores;
- reglas;
- evidencia;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- Negotiation Ladder;
- resolución de conflictos;
- recomendación explicable;
- trazabilidad de decisiones.

La funcionalidad relacionada con ventas para comerciales permanece actualmente:

**EN STANDBY**

Su eventual incorporación deberá seguir el gobierno documental correspondiente.

---

# 6. MODELO GENERAL DE DECISIÓN

El flujo conceptual actual es:

```text
DATOS
  ↓
EVIDENCIA
  ↓
REGLAS
  ↓
EVALUACIÓN
  ↓
VIABILIDAD
  ↓
ESCENARIOS
  ↓
DECISION TWIN
  ↓
NEGOCIACIÓN
  ↓
RESOLUCIÓN DE CONFLICTOS
  ↓
RECOMENDACIÓN
  ↓
DECISOR
```

Las decisiones empresariales principales del Vertical son:

- 🟢 **COMPRAR**
- 🟡 **NEGOCIAR**
- 🔵 **COMPRAR CONDICIONADO**
- 🔴 **NO COMPRAR**

La definición formal y el comportamiento de estas decisiones corresponden a la documentación funcional y al motor de reglas.

**Información insuficiente** no se considera aquí una quinta decisión empresarial oficial. La insuficiencia de evidencia debe gestionarse mediante los mecanismos de evidencia, confianza, validación y reglas que correspondan.

---

# 7. PRINCIPALES ÁREAS FUNCIONALES

El proyecto contiene o prevé áreas especializadas para:

## Datos

Origen, estructura, calidad, transformación y disponibilidad de los datos.

## Evidencia

Determinación de la suficiencia, calidad, antigüedad y fiabilidad de las referencias utilizadas por EIOS.

## Reglas

Criterios empresariales que permiten evaluar una operación.

## Motor

Procesamiento de datos, reglas, cálculos, escenarios y decisiones.

## Resolución de conflictos

Tratamiento de situaciones en las que diferentes reglas o criterios producen resultados incompatibles.

## Parámetros

Valores configurables que modifican el comportamiento del sistema sin necesidad de alterar el código.

## Negociación

Generación y evaluación de condiciones de negociación.

## Decision Twin

Simulación de diferentes condiciones para estudiar sus consecuencias antes de decidir.

## Assurance

Control transversal de integridad, trazabilidad, explicabilidad y cumplimiento de las salvaguardas.

---

# 8. REFERENCE & CALCULATION FRAMEWORK

El proyecto contempla el:

**Reference & Calculation Framework (RCF)**

Su función es establecer cómo EIOS transforma datos y referencias en información válida para la decisión.

Entre sus aspectos relevantes:

- periodo de referencia;
- fecha;
- antigüedad;
- comparabilidad;
- método de cálculo;
- ponderación;
- límites;
- excepciones;
- calidad de la referencia.

El RCF debe evitar referencias históricas poco representativas y mantener la trazabilidad del origen de los cálculos.

La definición normativa del RCF corresponde al documento especializado que le sea asignado.

---

# 9. PRODUCTOS Y COMPARABILIDAD

EIOS debe distinguir entre:

- producto;
- denominación comercial;
- referencia;
- producto comparable;
- categoría funcional.

El concepto:

**RFP — Referencia Funcional de Producto**

puede utilizarse para agrupar productos que cumplen una función similar o constituyen referencias comparables.

Una RFP no implica que dos productos sean idénticos.

La comparabilidad puede considerar, entre otros:

- funcionalidad;
- características técnicas;
- presentación;
- calidad;
- cantidad;
- marca;
- condiciones comerciales;
- utilización empresarial.

La relación de comparabilidad debe conservar trazabilidad y, cuando corresponda, permitir validación humana.

La definición funcional definitiva pertenece a la documentación especializada correspondiente.

---

# 10. REFERENCIAS Y PRECIOS

EIOS puede trabajar con:

- compras recientes;
- histórico de compras;
- productos comparables;
- proveedores alternativos;
- precios ponderados;
- descuentos;
- rappels;
- condiciones de pago;
- margen;
- precio de venta;
- estrategia empresarial.

La antigüedad de una referencia debe tenerse en cuenta.

Las referencias deben poder clasificarse según su fiabilidad cuando la decisión lo requiera.

El sistema debe evitar presentar una falsa precisión.

Los cálculos específicos de precio y coste corresponden al marco funcional especializado.

---

# 11. PRECIO Y COSTE EFECTIVO

Entre los conceptos funcionales del proyecto se encuentran:

**PMR — Precio Máximo Recomendado**

y

**CEA — Coste Efectivo de Adquisición**

El PMR permite establecer un umbral de referencia para la negociación o decisión.

El CEA permite valorar el coste económico efectivo considerando, cuando proceda:

- precio;
- descuentos;
- rappels;
- condiciones de pago;
- otras variables económicas.

La metodología formal de cálculo debe mantenerse en la documentación especializada correspondiente.

---

# 12. NEGOCIACIÓN DINÁMICA

EIOS debe poder analizar cambios de condiciones durante una negociación.

Ejemplo conceptual:

```text
Oferta inicial
      ↓
Cambio de precio
      ↓
Descuento
      ↓
Rappel
      ↓
Plazo de pago
      ↓
Recalculo
      ↓
Nueva recomendación
```

El sistema debe poder recalcular, cuando corresponda:

- coste efectivo;
- margen;
- referencia histórica;
- PMR;
- impacto financiero;
- recomendación.

La lógica detallada pertenece al componente especializado de negociación.

---

# 13. STOCK Y SIMULACIÓN TEMPORAL

La fecha de propuesta de compra es relevante.

EIOS debe poder estudiar la evolución futura considerando, cuando existan datos suficientes:

- stock actual;
- demanda;
- ventas;
- entradas previstas;
- pedidos pendientes;
- compras en tránsito;
- fecha de entrega;
- plazo de entrega;
- cantidad comprada.

Conceptualmente:

```text
Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas
```

El objetivo es detectar, entre otros:

- posibles roturas de stock;
- exceso de stock;
- necesidades futuras;
- impacto de una compra.

---

# 14. VIABILIDAD FINANCIERA

La evaluación puede considerar:

- liquidez;
- tesorería;
- pagos previstos;
- fondo de maniobra;
- impacto financiero;
- plazo de pago;
- condiciones comerciales.

Cuando una operación sea inicialmente desfavorable pero pueda hacerse viable mediante determinadas condiciones, EIOS puede presentar:

**COMPRAR CONDICIONADO**

Las alternativas propuestas por EIOS no constituyen órdenes automáticas de actuación.

---

# 15. CONFIGURATION CENTER

El:

**EIOS Configuration Center**

es un componente transversal de parametrización.

Puede centralizar valores como:

- periodos;
- límites;
- tolerancias;
- criterios;
- reglas;
- prioridades;
- excepciones;
- políticas empresariales.

Debe permitir adaptar EIOS a diferentes empresas sin modificar necesariamente el código.

Los parámetros oficiales deben definirse en el catálogo de parámetros correspondiente.

---

# 16. VERSIONADO DE CONFIGURACIÓN

Los cambios de configuración relevantes deben conservar historial.

Debe ser posible conocer qué configuración estaba vigente cuando se produjo una determinada decisión.

Ejemplo conceptual:

```text
Parámetro
   ↓
Versión de configuración
   ↓
Regla
   ↓
Decisión
```

La implementación detallada corresponde a la documentación especializada de parametrización y versionado.

---

# 17. MOTOR DE REGLAS

El motor de reglas debe ser configurable.

Las reglas pueden incluir:

### Reglas de bloqueo

Pueden impedir una recomendación de compra.

### Reglas de recomendación

Pueden modificar o condicionar la recomendación.

### Reglas de excepción

Pueden modificar el efecto de otras reglas bajo determinadas condiciones.

La prioridad, severidad y resolución de conflictos deben estar formalmente definidas.

La autoridad corresponde a la documentación del motor y de resolución de conflictos.

---

# 18. RESOLUCIÓN DE CONFLICTOS

EIOS no debe resolver conflictos mediante una simple suma de señales favorables y desfavorables.

Debe poder considerar:

- prioridad;
- severidad;
- bloqueos;
- excepciones;
- dependencias;
- condiciones;
- conflictos;
- resultado consolidado.

Una regla crítica no debe quedar anulada simplemente por la existencia de varias condiciones favorables.

La definición formal corresponde a la documentación especializada de resolución de conflictos.

---

# 19. EVIDENCIA Y EXPLICABILIDAD

Una recomendación debe poder explicar:

- qué datos se utilizaron;
- qué referencias se utilizaron;
- qué parámetros estaban vigentes;
- qué reglas se activaron;
- qué excepciones se aplicaron;
- qué escenarios se evaluaron;
- qué resultado produjo el motor.

La información debe presentarse de forma clara y proporcional.

El detalle técnico no debe saturar al CEO.

La definición formal de evidencia corresponde al documento especializado que la Matriz de Autoridad Documental establezca como fuente oficial.

---

# 20. DECISION TWIN

El Decision Twin permite estudiar escenarios antes de tomar una decisión.

Puede utilizar variables como:

- precio;
- cantidad;
- descuento;
- rappel;
- plazo de pago;
- fecha de entrega;
- demanda;
- stock;
- margen;
- liquidez.

Su objetivo es responder preguntas como:

> ¿Qué ocurre si modificamos esta condición?

y:

> ¿Qué combinación de condiciones hace viable la operación?

La definición funcional detallada pertenece al documento especializado correspondiente.

---

# 21. NEGOTIATION LADDER

La Negotiation Ladder representa una posible secuencia de negociación.

Conceptualmente:

```text
CONDICIÓN ACTUAL
      ↓
OBJETIVO
      ↓
PRIMERA PROPUESTA
      ↓
CONCESIONES CONTROLADAS
      ↓
LÍMITE
      ↓
ALTERNATIVA
```

La finalidad es proporcionar al decisor una estructura de negociación coherente con la recomendación de EIOS.

La lógica detallada corresponde al dominio de negociación.

---

# 22. ASSURANCE Y SALVAGUARDAS

Assurance actúa transversalmente sobre EIOS.

Debe contribuir a garantizar:

- integridad;
- trazabilidad;
- explicabilidad;
- coherencia;
- auditabilidad;
- control de regresiones.

El Vertical MVP está además sujeto a:

`EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

Las restricciones congeladas de la Salvaguarda no pueden modificarse silenciosamente.

---

# 23. RUTA INICIAL DE DATOS

La ruta:

```text
ERP → Excel → Power BI → SQL Server
```

corresponde a una ruta inicial de trabajo y origen de datos.

No constituye por sí misma la arquitectura técnica definitiva de EIOS.

Actualmente se trabaja habitualmente con SAGE, pero EIOS no debe quedar limitado exclusivamente a SAGE.

La integración automática con ERP queda como evolución futura.

---

# 24. ARQUITECTURA CONCEPTUAL

La arquitectura conceptual de EIOS se estructura como:

```text
EIOS
├── CORE
└── VERTICAL
    └── Intelligent Procurement Decision & Negotiation
```

El CORE contiene capacidades comunes.

El Vertical contiene capacidades específicas del dominio de compras.

Esta separación permite que futuras capacidades verticales puedan incorporarse sin reconstruir el núcleo común.

La arquitectura técnica definitiva debe consultarse en la documentación especializada de arquitectura.

---

# 25. INTERFAZ Y EXPERIENCIA DEL DECISOR

La interfaz debe priorizar:

1. decisión;
2. motivos principales;
3. riesgos;
4. condiciones de negociación;
5. margen;
6. stock;
7. fiabilidad;
8. referencias relevantes.

La información secundaria debe estar disponible bajo demanda.

Principio:

> **Complejidad en el motor; simplicidad en la decisión.**

---

# 26. ESTADO GENERAL DEL PROYECTO

### 🟢 Definido

- identidad EIOS;
- propósito;
- alcance del Vertical MVP;
- CORE + VERTICAL;
- decisión de compras;
- negociación;
- variables principales;
- necesidad de parametrización;
- Configuration Center;
- motor de reglas;
- resolución de conflictos;
- Decision Twin;
- Assurance;
- Salvaguarda Vertical MVP;
- autoridad documental.

### 🟡 En desarrollo / formalización

- Reference & Calculation Framework;
- criterios temporales;
- métodos de comparación;
- fiabilidad de referencias;
- prioridad de reglas;
- resolución de conflictos;
- excepciones;
- parámetros;
- componentes especializados del motor.

### ⚪ Evolución futura

- integración automática con ERP;
- arquitectura técnica definitiva;
- desarrollo completo del MVP;
- ampliaciones verticales.

El estado detallado debe consultarse en los documentos especializados.

---

# 27. CÓMO UTILIZAR ESTE MANUAL

Cuando una persona o IA se incorpore al proyecto:

### Paso 1
Leer `Project_Charter.md` para conocer qué es EIOS.

### Paso 2
Leer `Project_Context.md` para recuperar el contexto actual.

### Paso 3
Leer `Project_Governance.md` para conocer las reglas de gobierno.

### Paso 4
Leer `Matriz_Autoridad_Documental.md` para conocer qué documentos tienen autoridad.

### Paso 5
Leer `EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md` para conocer las restricciones congeladas del Vertical MVP.

### Paso 6
Utilizar este Manual como mapa para localizar la documentación especializada necesaria.

---

# 28. REGLA DE CONTINUIDAD

El proyecto debe poder recuperarse sin depender del historial de una conversación.

Por tanto:

```text
CONVERSACIÓN
     ↓
TRABAJO
     ↓
DECISIÓN
     ↓
DOCUMENTACIÓN
     ↓
GITHUB
     ↓
CONTINUIDAD
```

La conversación es espacio de trabajo.

La documentación oficial es la memoria estructurada del proyecto.

---

# 29. REGLA DE NO DUPLICACIÓN

Si una materia dispone de un documento especializado con autoridad:

**no debe reproducirse íntegramente en este Manual.**

Este Manual debe:

- identificarla;
- resumirla;
- señalar dónde encontrarla;
- mantener el contexto necesario.

La lógica detallada debe permanecer en su fuente oficial.

Esto evita:

- contradicciones;
- duplicación;
- divergencias de versiones;
- mantenimiento innecesario.

---

# 30. REGLA DE ACTUALIZACIÓN DEL MANUAL

El Manual debe actualizarse cuando exista un cambio suficientemente relevante en:

- estructura del proyecto;
- alcance;
- arquitectura conceptual;
- gobierno documental;
- componentes principales;
- estado general;
- rutas de navegación.

No debe actualizarse por cada cambio menor de una regla o parámetro.

Los cambios especializados deben permanecer en sus documentos correspondientes.

---

# 31. CRITERIO FINAL

El Manual Maestro debe responder rápidamente a cinco preguntas:

```text
1. ¿QUÉ ES EIOS?
        ↓
2. ¿QUÉ ESTAMOS CONSTRUYENDO?
        ↓
3. ¿CÓMO ESTÁ ORGANIZADO?
        ↓
4. ¿DÓNDE ESTÁ LA INFORMACIÓN OFICIAL?
        ↓
5. ¿DÓNDE CONTINUAR EL TRABAJO?
```

Si una información no ayuda a responder alguna de estas preguntas o a navegar hacia su fuente oficial, debe evaluarse si realmente pertenece al Manual Maestro.

---

# 32. PRINCIPIO FUNDAMENTAL

> **El Manual Maestro no debe contener todo EIOS.**
>
> **Debe permitir encontrar y comprender EIOS sin perderse.**

Su valor no está en acumular información, sino en proporcionar **continuidad, orientación, navegación y contexto fiable**.
