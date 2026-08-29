# MATRIZ DE AUTORIDAD DOCUMENTAL

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.3  
**Estado:** APROBADO  
**Ubicación:** `00_Gobierno/Matriz_Autoridad_Documental.md`

---

# 1. Propósito

La Matriz de Autoridad Documental establece qué documento constituye la fuente oficial de referencia para cada tipo de decisión, definición o conocimiento dentro del proyecto EIOS.

Su objetivo es:

- evitar que diferentes documentos definan de forma distinta un mismo concepto;
- garantizar una única interpretación oficial para cada dominio;
- establecer la precedencia documental cuando exista una contradicción;
- preservar la coherencia entre Gobierno, Modelo, Arquitectura, Inteligencia, Motor, Aplicación y Pruebas;
- permitir que EIOS evolucione sin perder trazabilidad ni autoridad documental.

Esta matriz no sustituye al contenido de los documentos.

Determina cuál de ellos tiene autoridad cuando existe una discrepancia.

---

# 2. Principio fundamental

> **Un concepto debe tener una única fuente oficial de autoridad.**

Los demás documentos pueden:

- resumirlo;
- utilizarlo;
- referenciarlo;
- explicarlo desde otra perspectiva;
- implementarlo;
- verificarlo;

pero no deben redefinirlo de forma independiente.

Cuando exista una contradicción, debe prevalecer la fuente oficial definida en esta matriz, aplicando además las reglas específicas de precedencia establecidas en este documento.

---

# 3. Alcance

Esta matriz regula la autoridad documental dentro de EIOS sobre:

- gobierno;
- identidad;
- alcance;
- contexto;
- modelo empresarial;
- arquitectura;
- parámetros;
- configuración;
- reglas;
- evidencia;
- dependencias de reglas;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- resolución de conflictos;
- assurance;
- versionado;
- aplicación;
- operaciones;
- desarrollo;
- pruebas.

No regula:

- la autoridad de los usuarios sobre las decisiones empresariales;
- la configuración concreta de una empresa;
- los permisos de ejecución de la aplicación;
- la legislación aplicable;
- las fuentes externas de datos;
- la decisión final del CEO.

EIOS puede analizar, evaluar, simular, explicar y recomendar.

La decisión empresarial final corresponde al usuario autorizado.

---

# 4. Principios de autoridad

## 4.1 Autoridad por dominio

No existe un único documento que tenga autoridad absoluta sobre todos los aspectos de EIOS.

La autoridad depende del concepto que se esté tratando.

---

## 4.2 Especialización documental

Cada documento debe tener un ámbito de autoridad claramente delimitado.

Un documento especializado puede desarrollar un concepto con mayor profundidad que un documento superior, siempre que:

1. permanezca dentro de su dominio;
2. no contradiga el marco superior aplicable;
3. no redefina silenciosamente conceptos cuya autoridad corresponda a otro documento.

---

## 4.3 No duplicación de autoridad

Un concepto crítico no debe tener dos fuentes oficiales simultáneas.

Si dos documentos pretenden tener autoridad sobre el mismo concepto, debe resolverse primero la autoridad y posteriormente actualizarse la documentación afectada.

---

## 4.4 No corrección automática

Una contradicción documental no debe corregirse automáticamente.

Antes de modificar un documento debe determinarse:

1. cuál es el concepto en conflicto;
2. cuál es su dominio;
3. qué documento tiene autoridad;
4. si la fuente oficial sigue siendo válida;
5. si existe una nueva decisión pendiente de formalización;
6. qué documentos secundarios han quedado obsoletos.

---

## 4.5 Trazabilidad

Toda modificación que cambie una definición con autoridad debe quedar registrada mediante el mecanismo de control de cambios correspondiente.

---

# 5. Niveles de autoridad

La autoridad documental de EIOS se organiza en cinco niveles.

## Nivel A — Gobierno e identidad

Define:

- qué es EIOS;
- identidad oficial;
- propósito;
- visión;
- alcance;
- límites;
- gobierno;
- continuidad;
- autoridad documental.

## Nivel B — Marco arquitectónico y conceptual

Define:

- arquitectura global;
- organización del sistema;
- modelo empresarial;
- relación entre componentes;
- marco congelado del EIOS Vertical MVP.

## Nivel C — Componentes especializados

Define:

- parámetros;
- configuración;
- reglas;
- evidencia;
- dependencias;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- resolución de conflictos;
- versionado.

## Nivel D — Implementación

Define:

- motor;
- SQL;
- aplicación;
- operación;
- desarrollo;
- interfaces técnicas.

## Nivel E — Verificación

Define:

- pruebas;
- validación;
- criterios de aceptación;
- evidencia de funcionamiento.

---

# 6. Matriz principal de autoridad

| Dominio | Fuente oficial | Autoridad sobre |
|---|---|---|
| Identidad del proyecto | `00_Gobierno/Project_Charter.md` | Nombre oficial, propósito, visión, alcance y límites |
| Contexto y continuidad | `00_Gobierno/Project_Context.md` | Estado del proyecto, contexto y continuidad |
| Gobierno del proyecto | `00_Gobierno/Project_Governance.md` | Gobierno, control y evolución del proyecto |
| Autoridad documental | `00_Gobierno/Matriz_Autoridad_Documental.md` | Precedencia y resolución de contradicciones documentales |
| Marco del Vertical MVP | `00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md` | Marco congelado, principios, límites y arquitectura conceptual del Vertical MVP |
| Modelo empresarial | `05_Motor/Modelo_Empresarial_Decision.md` | Conceptos empresariales, significado y lógica general de la decisión |
| Arquitectura técnica | `03_Arquitectura/Architecture_Blueprint.md` | Arquitectura lógica, componentes técnicos y flujo de datos |
| Mapa arquitectónico | `03_Arquitectura/Master_Project_Map.md` | Organización global de componentes y relaciones arquitectónicas |
| Parámetros | `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` | Definición, identificación, naturaleza y propósito de parámetros |
| Configuración | `02_Parametros/Centro_Parametrizacion.md` | Valores configurables, vigencia, edición, permisos y gobierno de parámetros |
| Reglas | `04_Reglas/Matriz_Reglas_MVP.md` | Condiciones, evaluación y resultados de reglas |
| Evidencia | `04_Reglas/Evidence_Contract.md` | Contrato general de evidencia, criterios de admisibilidad y suficiencia |
| Dependencias | `04_Reglas/Rule_Dependency_Matrix.md` | Dependencias canónicas entre reglas, datos, evidencias, parámetros, componentes y requisitos concretos de evaluabilidad |
| Viability Frontier | `05_Motor/Viability_Frontier.md` | Definición y comportamiento de la frontera de viabilidad |
| Scenario Engine | `05_Motor/Viability_Scenario_Engine.md` | Generación, comparación y versionado de escenarios |
| Decision Twin | `05_Motor/Decision_Twin.md` | Representación de alternativas y estructura de la decisión |
| Negotiation Intelligence | `05_Motor/Negotiation_Intelligence.md` | Inteligencia y análisis de negociación |
| Negotiation Ladder | `05_Motor/Negotiation_Ladder.md` | Estructura, representación y secuencia de negociación |
| Resolución de conflictos | `04_Reglas/Capa_resolucion_conflictos.md` | Resolución de resultados contradictorios entre reglas y evaluaciones |
| Versionado de decisiones | `05_Motor/Decision_Versioning.md` | Identidad, historial y versionado de decisiones |
| SQL | `06_SQL/06_LEEME_SQL.md` | Organización y criterios de implementación SQL |
| Aplicación | `08_Implementacion/` | Construcción e integración de la implementación técnica |
| Operación | `08_Implementacion/` | Criterios de funcionamiento operativo de la implementación |
| Desarrollo | `08_Implementacion/` | Criterios de construcción e implementación |
| Pruebas | `07_Pruebas/` | Verificación y validación del sistema |
| Archivo histórico | `99_Archivo/` | Material histórico, obsoleto o conservado por trazabilidad |

> **Nota:** Las rutas de documentos especializados que todavía no estén creados deberán considerarse referencias reservadas de autoridad futura. No implican que el documento exista actualmente.

---

# 7. Autoridad del Project Charter

El `Project_Charter.md` constituye la autoridad sobre:

- identidad oficial del proyecto;
- propósito;
- visión;
- alcance;
- límites;
- usuarios objetivo;
- objetivos generales.

Ningún documento especializado puede redefinir estos elementos.

Si la identidad o el alcance del proyecto cambian, debe modificarse primero el Project Charter y posteriormente actualizarse la documentación dependiente.

---

# 8. Autoridad de la Salvaguarda EIOS Vertical MVP

La:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

constituye el **marco constitucional del EIOS Vertical MVP** mientras permanezca vigente.

Su función es establecer y proteger:

- principios arquitectónicos;
- límites del Vertical;
- estructura Core + Vertical;
- componentes congelados;
- principios de decisión;
- salvaguardas;
- criterios de no regresión;
- relaciones esenciales entre componentes.

La Salvaguarda no sustituye la autoridad especializada de los documentos que desarrollan cada componente.

Por tanto:

```text
SALVAGUARDA
      │
      ├── establece el marco
      ├── establece límites
      └── establece relaciones esenciales
                  │
                  ▼
        DOCUMENTOS ESPECIALIZADOS
                  │
                  ├── desarrollan
                  ├── concretan
                  └── implementan
```

Un documento especializado no puede contradecir una restricción explícita de la Salvaguarda.

Si una especificación especializada necesita cambiar una decisión congelada por la Salvaguarda, primero debe revisarse y actualizarse formalmente la Salvaguarda.

---

# 9. Autoridad del Modelo Empresarial de Decisión

El `05_Motor/Modelo_Empresarial_Decision.md` constituye la autoridad sobre:

- conceptos empresariales;
- significado de una decisión;
- lógica empresarial general;
- interpretación de resultados;
- relación conceptual entre factores empresariales.

No define por sí mismo:

- valores concretos de parámetros;
- configuración vigente;
- implementación técnica;
- SQL;
- interfaz;
- código.

---

# 10. Autoridad de Parámetros y Configuración

El `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` define qué parámetros existen y qué representan.

El `02_Parametros/Centro_Parametrizacion.md` define cómo se configuran y gobiernan sus valores.

La relación es:

```text
CATÁLOGO DE PARÁMETROS
        │
        ▼
¿Qué parámetros existen?
        │
        ▼
CENTRO DE PARAMETRIZACIÓN
        │
        ▼
¿Qué valores están vigentes?
```

El Centro de Parametrización no puede crear silenciosamente un parámetro que no exista en el Catálogo.

Si se necesita un nuevo parámetro:

1. se incorpora al Catálogo;
2. se define su naturaleza;
3. se determina su gobierno;
4. posteriormente puede configurarse.

---

# 11. Autoridad de Reglas

La `04_Reglas/Matriz_Reglas_MVP.md` constituye la autoridad sobre:

- identificación de reglas;
- condiciones;
- lógica de evaluación;
- resultados;
- prioridad;
- comportamiento definido de cada regla.

Una regla no debe redefinir un parámetro.

Debe utilizar parámetros cuya definición oficial corresponda al Catálogo.

---

# 12. Autoridad de Evidence Contract

El `Evidence_Contract.md` constituye la autoridad sobre el **contrato general de evidencia**:

- naturaleza y estructura contractual de la evidencia;
- criterios generales de admisibilidad;
- criterios generales de suficiencia;
- requisitos mínimos de trazabilidad y demostrabilidad;
- estados y tratamiento general de evidencia insuficiente.

No determina qué evidencias concretas necesita una regla determinada.

La ausencia o insuficiencia de evidencia debe conservar su significado explícito y no puede convertirse por defecto en un resultado de regla.

---

# 13. Autoridad de Rule Dependency Matrix

La `Rule_Dependency_Matrix.md` constituye la **fuente canónica transversal de dependencias** dentro de EIOS.

Su autoridad comprende:

- dependencias entre reglas;
- datos necesarios para cada regla;
- evidencias concretas requeridas por cada regla;
- parámetros implicados en cada dependencia;
- componentes afectados;
- condiciones concretas de evaluabilidad derivadas de dichas dependencias;
- relación estructural entre estas dependencias.

Esta matriz instancia los requisitos de evidencia del contrato general en el contexto de cada regla.

Debe permitir determinar qué ocurre cuando una dependencia crítica no está disponible.

No puede redefinir:

- la definición de un parámetro, cuya autoridad corresponde al Catálogo;
- la condición o resultado de una regla, cuya autoridad corresponde a la Matriz de Reglas;
- los criterios generales de admisibilidad y suficiencia, cuya autoridad corresponde a `Evidence_Contract.md`;
- la resolución de conflictos entre resultados, cuya autoridad corresponde a la CRC.

## 13.1 Relación con matrices y especificaciones especializadas

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` mantiene su función como **matriz especializada de enlace y vista parámetro ↔ regla**. No constituye una segunda fuente canónica de autoridad sobre el grafo transversal de dependencias.

Las especificaciones especializadas, como:

- `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md`;
- `04_Reglas/Especificacion_Reglas_Historico_MVP.md`;

pueden aportar evidencia documental, detalle funcional o determinaciones especializadas sobre relaciones concretas, pero no crean una autoridad paralela sobre el modelo transversal de dependencias.

Cuando una relación especializada deba incorporarse al mapa canónico de dependencias, la `Rule_Dependency_Matrix.md` deberá reflejarla sin alterar la autoridad de la fuente especializada sobre su propio detalle.

Por tanto:

```text
Evidence Contract
       │
       ▼
Rule Dependency Matrix
       │
       ├── datos
       ├── parámetros
       ├── evidencia
       ├── componentes
       └── evaluabilidad
              ▲
              │
   ┌──────────┴──────────┐
   │                     │
Matriz P↔R       Especificaciones
(vista/enlace)    especializadas
```

La existencia de una vista o especificación especializada no duplica la autoridad canónica de la `Rule_Dependency_Matrix.md`.

---

# 14. Autoridad de Viability Frontier

El documento de `Viability_Frontier` constituye la autoridad sobre:

- definición de la frontera de viabilidad;
- condiciones que determinan dicha frontera;
- variables que la modifican;
- interpretación del espacio viable/no viable.

La Viability Frontier no constituye por sí sola una orden de compra.

Una condición `VIABLE` no equivale automáticamente a `COMPRAR`.

La decisión final depende del conjunto de evaluaciones y de la lógica de decisión definida por EIOS.

---

# 15. Autoridad del Scenario Engine

El `Viability_Scenario_Engine.md` constituye la autoridad sobre:

- generación de escenarios;
- variables modificables;
- comparación de escenarios;
- identificación de escenarios;
- versionado de escenarios;
- relación entre escenario y resultado.

Los escenarios deben ser reproducibles y trazables.

Un escenario no debe sobrescribir otro escenario existente.

## 15.1 Frontera de comparación: escenarios vs alternativas

La comparación de **escenarios** pertenece al dominio del Scenario Engine: establece las diferencias y relaciones entre representaciones de escenario y sus resultados, sin convertir por ello un escenario en una alternativa decisional ni seleccionar una alternativa.

La comparación de **alternativas** pertenece al dominio del Decision Twin: recibe alternativas ya disponibles, junto con sus resultados y criterios aplicables, y permite compararlas y analizar sus consecuencias.

Por tanto:

```text
SCENARIO ENGINE
    │
    └── compara escenarios
             │
             ▼
      escenarios / resultados
             │
             ▼
      alternativas viables
             │
             ▼
DECISION TWIN
    │
    └── compara alternativas
        y analiza consecuencias
```

Esta frontera no autoriza:

- al Scenario Engine a seleccionar o recomendar una alternativa;
- al Decision Twin a generar o redefinir escenarios fuera de su representación estructurada;
- a ninguno de los dos a asumir autoridad sobre la consolidación final de la CRC.

---

# 16. Autoridad del Decision Twin

El `Decision_Twin.md` constituye la autoridad sobre la representación estructurada de:

- situación actual;
- alternativa propuesta;
- alternativa modificada;
- escenarios comparados;
- consecuencias;
- resultado de cada alternativa.

El Decision Twin representa alternativas de decisión.

No sustituye la autoridad del CEO.

---

# 17. Autoridad de Negotiation Intelligence

`Negotiation_Intelligence.md` constituye la autoridad sobre:

- análisis de negociación;
- variables negociables;
- trade-offs;
- condiciones de negociación;
- oportunidades de mejora;
- evaluación de propuestas.

---

# 18. Autoridad de Negotiation Ladder

`Negotiation_Ladder.md` constituye la autoridad sobre:

- estructura de negociación;
- representación de movimientos y condiciones negociadoras;
- secuencia de negociación;
- organización de escalones y transiciones;
- representación de alternativas, fallback y walk-away.

La Negotiation Ladder no puede modificar por sí misma las reglas de decisión empresarial.

---

# 19. Autoridad de Resolución de Conflictos

`04_Reglas/Capa_resolucion_conflictos.md` constituye la autoridad sobre cómo resolver resultados incompatibles entre:

- reglas;
- evaluaciones;
- bloqueos;
- excepciones;
- condiciones.

La resolución de conflictos debe conservar trazabilidad.

---

# 20. Autoridad de Versionado de Decisiones

`Decision_Versioning.md` constituye la autoridad sobre:

- identidad de una decisión;
- versiones;
- historial;
- relación entre decisiones sucesivas;
- trazabilidad temporal.

Una nueva decisión no debe borrar la existencia de una decisión anterior.

---

# 21. Autoridad de Implementación

Los documentos de implementación constituyen autoridad sobre cómo se construye y ejecuta técnicamente EIOS.

La implementación no puede redefinir unilateralmente:

- reglas empresariales;
- parámetros;
- decisiones congeladas;
- autoridad documental.

Si la implementación requiere modificar una definición funcional, debe escalarse el cambio al documento que tenga autoridad sobre dicha definición.

---

# 22. Autoridad de Pruebas

La carpeta `07_Pruebas/` constituye la referencia para:

- pruebas;
- validaciones;
- criterios de aceptación;
- resultados de verificación;
- evidencia de funcionamiento.

Una prueba puede demostrar que una implementación cumple una especificación, pero no puede modificar la especificación por sí misma.

---

# 23. Precedencia ante conflictos

Cuando dos documentos entren en conflicto se aplicará el siguiente procedimiento:

```text
1. IDENTIFICAR EL CONCEPTO
        ↓
2. IDENTIFICAR SU DOMINIO
        ↓
3. CONSULTAR ESTA MATRIZ
        ↓
4. IDENTIFICAR LA FUENTE OFICIAL
        ↓
5. COMPROBAR SI EXISTE UNA DECISIÓN CONGELADA
        ↓
6. APLICAR LA FUENTE DE MAYOR AUTORIDAD
        ↓
7. ACTUALIZAR LOS DOCUMENTOS SECUNDARIOS
        ↓
8. REGISTRAR EL CAMBIO
```

No debe resolverse una contradicción simplemente utilizando el documento más reciente.

La antigüedad no determina por sí sola la autoridad.

---

# 24. Relación entre documentos de gobierno

Los documentos de gobierno deben entenderse así:

```text
PROJECT CHARTER
      │
      ├── identidad
      ├── propósito
      ├── alcance
      └── límites
              │
              ▼
PROJECT CONTEXT
      │
      └── continuidad y estado
              │
              ▼
PROJECT GOVERNANCE
      │
      └── reglas de gobierno
              │
              ▼
MATRIZ DE AUTORIDAD
      │
      └── quién tiene autoridad
              │
              ▼
SALVAGUARDA VERTICAL MVP
      │
      └── qué está congelado
              │
              ▼
DOCUMENTOS ESPECIALIZADOS
      │
      └── cómo se desarrolla cada dominio
```

El `Manual_Maestro_Proyecto_EIOS.md` actúa como documento de orientación y navegación, no como autoridad paralela.

---

# 25. Reglas de mantenimiento

La Matriz deberá actualizarse cuando:

- se cree un nuevo documento con autoridad;
- se modifique la autoridad de un documento;
- se elimine un documento oficial;
- se cambie una ruta oficial;
- se cree un nuevo dominio de autoridad;
- se produzca una decisión estructural que afecte a la precedencia documental.

No debe actualizarse por simples cambios de redacción en documentos subordinados.

---

# 26. Control de documentos futuros

Una ruta incluida en esta matriz puede encontrarse en uno de estos estados:

### EXISTENTE

El documento está creado y constituye la fuente oficial.

### RESERVADA

La autoridad está definida, pero el documento todavía no existe.

### OBSOLETA

El documento existió, pero ya no constituye fuente oficial.

### SUSTITUIDA

La autoridad ha pasado formalmente a otro documento.

Una referencia reservada no debe interpretarse como un documento existente.

---

# 27. Regla de no regresión documental

Una modificación de estructura documental no debe reducir la trazabilidad existente.

No se debe:

- eliminar una fuente oficial sin designar sustituta;
- crear dos fuentes oficiales para el mismo concepto;
- mover un documento sin actualizar las referencias;
- convertir una decisión congelada en una recomendación informal;
- introducir lógica contradictoria en documentos subordinados.

---

# 28. Estado de la Matriz

**Versión:** 2.3  
**Estado:** APROBADO  
**Ámbito:** Gobierno documental EIOS  
**Carácter:** Fuente oficial de autoridad y precedencia documental

La Matriz define la autoridad necesaria para evitar ambigüedad cuando los documentos especializados sean creados.

---

# 29. Principio final

> **Cuando exista una duda sobre qué documento manda, no se interpreta: se consulta la Matriz de Autoridad Documental.**

La Matriz constituye el mecanismo oficial para preservar una única fuente de verdad documental dentro de EIOS.
