# MATRIZ DE AUTORIDAD DOCUMENTAL

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.0  
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
- assurance;
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
| Modelo empresarial | `01_Modelo/Modelo_Empresarial_Decision.md` | Conceptos empresariales, significado y lógica general de la decisión |
| Arquitectura técnica | `03_Arquitectura/Architecture_Blueprint.md` | Arquitectura lógica, componentes técnicos y flujo de datos |
| Mapa arquitectónico | `03_Arquitectura/Master_Project_Map.md` | Organización global de componentes y relaciones arquitectónicas |
| Parámetros | `02_Parametros/Catalogo_Parametros_MVP_v0.2.md` | Definición, identificación, naturaleza y propósito de parámetros |
| Configuración | `02_Parametros/Centro_Parametrizacion.md` | Valores configurables, vigencia, edición, permisos y gobierno de parámetros |
| Reglas | `04_Reglas/Matriz_Reglas_MVP.md` | Condiciones, evaluación y resultados de reglas |
| Evidencia | `04_Reglas/Evidence_Contract.md` | Evidencia requerida y criterios de suficiencia para la evaluación |
| Dependencias | `04_Reglas/Rule_Dependency_Matrix.md` | Dependencias entre reglas, datos, evidencias y componentes |
| Viability Frontier | `05_Motor/Viability_Frontier.md` | Definición y comportamiento de la frontera de viabilidad |
| Scenario Engine | `05_Motor/Scenario_Engine.md` | Generación, comparación y versionado de escenarios |
| Decision Twin | `05_Motor/Decision_Twin.md` | Representación de alternativas y estructura de la decisión |
| Negotiation Intelligence | `05_Motor/Negotiation_Intelligence.md` | Inteligencia y análisis de negociación |
| Negotiation Ladder | `05_Motor/Negotiation_Ladder.md` | Secuencia y estructura de negociación |
| Resolución de conflictos | `05_Motor/Capa_resolucion_conflictos.md` | Resolución de resultados contradictorios entre reglas y evaluaciones |
| Assurance | `00_Gobierno/EIOS_Assurance_Framework.md` | Salvaguardas, controles y garantías transversales del sistema |
| Versionado de decisiones | `05_Motor/Decision_Versioning.md` | Identidad, historial y versionado de decisiones |
| SQL | `06_SQL/06_LEEME_SQL.md` | Organización y criterios de implementación SQL |
| Aplicación | `07_Implementacion/07_LEEME_Implementacion.md` | Construcción e integración de la aplicación |
| Operación | `07_Implementacion/07_LEEME_Implementacion.md` | Criterios de funcionamiento operativo de la implementación |
| Desarrollo | `07_Implementacion/07_LEEME_Implementacion.md` | Criterios de construcción e implementación |
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
      │
      ├── establece límites
      │
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

El `Modelo_Empresarial_Decision.md` constituye la autoridad sobre:

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

El:

`02_Parametros/Catalogo_Parametros_MVP_v0.2.md`

define qué parámetros existen y qué representan.

El:

`02_Parametros/Centro_Parametrizacion.md`

define cómo se configuran y gobiernan sus valores.

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

La:

`04_Reglas/Matriz_Reglas_MVP.md`

constituye la autoridad sobre:

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

El `Evidence_Contract.md` constituye la autoridad sobre:

- evidencia requerida;
- suficiencia de evidencia;
- calidad mínima;
- condiciones de evaluabilidad;
- tratamiento de evidencia insuficiente.

Una regla no puede asumir que un dato está disponible simplemente porque aparece mencionado en otro documento.

La ausencia de evidencia debe conservar su significado explícito.

---

# 13. Autoridad de Rule Dependency Matrix

La `Rule_Dependency_Matrix.md` constituye la autoridad sobre:

- dependencias entre reglas;
- datos necesarios;
- evidencias requeridas;
- parámetros implicados;
- componentes afectados;
- condiciones de evaluabilidad.

Esta matriz debe permitir determinar qué ocurre cuando una dependencia crítica no está disponible.

---

# 14. Autoridad de Viability Frontier

El documento de `Viability_Frontier` constituye la autoridad sobre:

- definición de la frontera de viabilidad;
- condiciones que determinan dicha frontera;
- variables que la modifican;
- interpretación del espacio viable/no viable.

La Viability Frontier no constituye por sí sola una orden de compra.

Una condición:

```text
VIABLE
```

no equivale automáticamente a:

```text
COMPRAR
```

La decisión final depende del conjunto de evaluaciones y de la lógica de decisión definida por EIOS.

---

# 15. Autoridad del Scenario Engine

El `Scenario_Engine.md` constituye la autoridad sobre:

- generación de escenarios;
- variables modificables;
- comparación de escenarios;
- identificación de escenarios;
- versionado de escenarios;
- relación entre escenario y resultado.

Los escenarios deben ser reproducibles y trazables.

Un escenario no debe sobrescribir otro escenario existente.

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
- información relevante para negociar.

Negotiation Intelligence recomienda y explica.

No ejecuta unilateralmente la decisión empresarial.

---

# 18. Autoridad de Negotiation Ladder

`Negotiation_Ladder.md` constituye la autoridad sobre:

- niveles de negociación;
- secuencia de concesiones;
- condiciones de avance;
- límites;
- alternativas;
- escalado negociador.

La Negotiation Ladder debe respetar las restricciones financieras, empresariales y de assurance establecidas por EIOS.

---

# 19. Autoridad de Resolución de Conflictos

La:

`05_Motor/Capa_resolucion_conflictos.md`

constituye la autoridad sobre:

- resolución de resultados incompatibles;
- jerarquía de conflictos;
- severidad;
- motivo dominante;
- efectos de conflicto;
- compra condicionada;
- reglas de salvaguarda;
- resultado consolidado.

La CRC no modifica silenciosamente las reglas que originaron el conflicto.

---

# 20. Autoridad del Assurance Framework

El:

`00_Gobierno/EIOS_Assurance_Framework.md`

constituye la autoridad sobre las salvaguardas y controles transversales que afectan a:

- calidad;
- evidencia;
- trazabilidad;
- explicabilidad;
- integridad;
- seguridad;
- coherencia;
- auditabilidad;
- control de regresiones.

Assurance atraviesa todas las capas.

Ningún componente puede interpretar una condición de Assurance como opcional si está definida como salvaguarda obligatoria.

---

# 21. Autoridad del Versionado de Decisiones

`Decision_Versioning.md` constituye la autoridad sobre:

- identidad de una decisión;
- versiones;
- historial;
- modificaciones;
- relación entre versiones;
- trazabilidad temporal.

Una nueva evaluación no debe sobrescribir silenciosamente una decisión anterior.

---

# 22. Relación oficial entre documentos de Inteligencia

La relación conceptual de los documentos especializados es:

```text
MODELO EMPRESARIAL DE DECISIÓN
            │
            ▼
     CATÁLOGO DE PARÁMETROS
            │
            ▼
  CENTRO DE PARAMETRIZACIÓN
            │
            ▼
      MATRIZ DE REGLAS
            │
            ├──────────────► EVIDENCE CONTRACT
            │
            └──────────────► RULE DEPENDENCY MATRIX
                                │
                                ▼
                       EVALUACIÓN DE REGLAS
                                │
                                ▼
                       VIABILITY FRONTIER
                                │
                                ▼
                         SCENARIO ENGINE
                                │
                                ▼
                         DECISION TWIN
                                │
                                ▼
                    NEGOTIATION INTELLIGENCE
                                │
                                ▼
                       NEGOTIATION LADDER
                                │
                                ▼
                    RESOLUCIÓN DE CONFLICTOS
                                │
                                ▼
                         DECISIÓN EIOS
```

Assurance actúa transversalmente sobre todo el flujo.

Decision Versioning preserva la identidad e historial de las decisiones.

---

# 23. Regla de precedencia

Cuando dos documentos entren en conflicto se aplicará el siguiente procedimiento.

## Paso 1 — Identificar el concepto

Determinar exactamente qué concepto está siendo definido de forma diferente.

Ejemplos:

- nombre del proyecto;
- alcance;
- parámetro financiero;
- regla de stock;
- evidencia;
- resultado de una decisión;
- flujo de datos;
- escenario;
- condición de negociación.

---

## Paso 2 — Identificar el dominio

Determinar si el concepto pertenece a:

- gobierno;
- identidad;
- modelo empresarial;
- arquitectura;
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
- assurance;
- versionado;
- implementación;
- pruebas.

---

## Paso 3 — Consultar la fuente oficial

La fuente indicada en esta Matriz de Autoridad será la referencia principal.

---

## Paso 4 — Comprobar el marco superior

Antes de aceptar una definición especializada debe comprobarse que no contradice:

1. el Project Charter, cuando afecte a identidad o alcance;
2. el Project Governance, cuando afecte a gobierno;
3. la Salvaguarda, cuando afecte al marco congelado del Vertical MVP.

---

## Paso 5 — Determinar la naturaleza de la contradicción

La contradicción puede ser:

- documental;
- obsolescencia;
- error;
- cambio de diseño;
- cambio empresarial;
- cambio arquitectónico;
- decisión todavía no formalizada.

---

## Paso 6 — No corregir automáticamente

No se modificará ningún documento hasta determinar cuál es la definición oficial vigente.

---

## Paso 7 — Registrar la decisión

Cuando la contradicción implique una nueva decisión de diseño o negocio, esta deberá formalizarse antes de actualizar los documentos afectados.

---

# 24. Precedencia especial de la Salvaguarda

La Salvaguarda tiene precedencia sobre los documentos especializados **cuando la contradicción afecte a una restricción o principio expresamente congelado por ella**.

Ejemplo:

```text
Salvaguarda:
EIOS analiza y recomienda; el CEO decide.

Documento especializado:
EIOS ejecuta automáticamente la compra.

Resultado:
CONTRADICCIÓN.
```

El documento especializado deberá corregirse o deberá formalizarse previamente una modificación de la Salvaguarda.

Sin embargo:

```text
Salvaguarda:
Define que existe una CRC.

Documento CRC:
Define exactamente cómo clasifica la severidad.

Resultado:
NO existe contradicción.
```

La CRC tiene autoridad especializada sobre su propia implementación conceptual.

---

# 25. Documentos históricos y obsoletos

Los documentos almacenados en:

`99_Archivo/`

se consideran material histórico.

No constituyen autoridad sobre el estado vigente de EIOS salvo que se consulte expresamente su contenido histórico.

Un documento archivado no puede utilizarse para contradecir una definición vigente.

---

# 26. Referencias cruzadas

Un documento secundario debe referenciar a la fuente oficial cuando utilice un concepto cuya autoridad corresponda a otro documento.

Ejemplo:

```text
El presente documento utiliza el parámetro
FIN_MARGIN_MIN definido oficialmente en:

02_Parametros/Catalogo_Parametros_MVP_v0.2.md
```

No debe duplicarse una definición crítica si puede mantenerse una referencia inequívoca.

---

# 27. Documentos todavía no creados

Una entrada de esta matriz puede reservar autoridad para un documento futuro.

Esto significa:

- el dominio está reconocido;
- la autoridad futura está definida;
- el documento todavía debe construirse.

La existencia de una entrada en esta matriz **no implica que el documento exista actualmente**.

Hasta que el documento sea creado y aprobado, la autoridad deberá resolverse utilizando los documentos actualmente vigentes y la Salvaguarda cuando corresponda.

---

# 28. Regla de no regresión

Una nueva versión documental no puede introducir silenciosamente una definición que contradiga una decisión congelada.

Si se necesita modificar una decisión congelada:

```text
Identificar cambio
      ↓
Evaluar impacto
      ↓
Registrar decisión
      ↓
Actualizar autoridad correspondiente
      ↓
Actualizar documentos dependientes
      ↓
Verificar coherencia
```

---

# 29. Control de cambios

Toda modificación de esta matriz deberá indicar:

- versión;
- fecha;
- motivo;
- cambios realizados;
- documentos afectados.

Las modificaciones relevantes deberán quedar registradas en el historial de Git.

---

# 30. Estado de esta versión

**Versión:** 2.0  
**Estado:** MVP — Propuesta para aprobación

Esta versión actualiza la Matriz de Autoridad Documental para reflejar:

- la estructura documental vigente de GitHub;
- la existencia del EIOS Vertical MVP;
- la Salvaguarda Oficial como marco constitucional del Vertical;
- la separación entre autoridad global y autoridad especializada;
- los nuevos componentes conceptuales del MVP;
- la necesidad de preservar una única fuente oficial por dominio;
- el principio de no corrección automática de contradicciones.

---

# 31. Principio final

> **La documentación de EIOS puede evolucionar. La autoridad debe permanecer clara.**

Cuando exista una duda:

```text
NO asumir
NO duplicar
NO corregir silenciosamente
NO crear una tercera definición

IDENTIFICAR
      ↓
CLASIFICAR
      ↓
CONSULTAR LA AUTORIDAD
      ↓
DECIDIR
      ↓
REGISTRAR
      ↓
ACTUALIZAR
```

La finalidad de esta matriz no es controlar la documentación por sí misma.

Su finalidad es garantizar que **EIOS siempre pueda responder a una pregunta fundamental:**

> **«¿Qué documento tiene autoridad para decir esto?»**
