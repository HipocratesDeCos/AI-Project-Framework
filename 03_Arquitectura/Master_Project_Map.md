# EIOS — MASTER PROJECT MAP

## Mapa Maestro del Proyecto y de la Arquitectura

**Versión:** 2.4
**Estado:** APROBADO — reconciliación de continuidad post-EIOS-BL-004
**Función:** Mapa global de estructura y relaciones del sistema EIOS
**Ubicación:** `03_Arquitectura/Master_Project_Map.md`

---

# 1. PROPÓSITO

Este documento representa la estructura global de EIOS como sistema y proyecto.

Su función es mostrar:

- los grandes dominios del sistema;
- la relación entre ellos;
- el flujo conceptual desde gobierno hasta verificación;
- la posición del EIOS Vertical MVP dentro del Framework.

No sustituye a la documentación especializada de cada dominio.

---

# 2. MAPA GLOBAL EIOS

```text
                              EIOS
                               │
                               ▼
                    ┌─────────────────────┐
                    │   00 — GOBIERNO     │
                    │                     │
                    │ Autoridad           │
                    │ Gobierno            │
                    │ Contexto            │
                    │ Salvaguarda         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    01 — MODELO      │
                    │                     │
                    │ Modelo empresarial  │
                    │ Conceptos           │
                    │ Lógica funcional    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  02 — PARÁMETROS    │
                    │                     │
                    │ Catálogo            │
                    │ Parametrización     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 03 — ARQUITECTURA   │
                    │                     │
                    │ Estructura          │
                    │ Componentes         │
                    │ Relaciones          │
                    └──────────┬──────────┘
                               │
                               ├──────────────► 03_App — APLICACIÓN / INTERFAZ
                               │                Especificación · campos · interacción · visual
                               │
                               ▼
                    ┌─────────────────────┐
                    │   04 — REGLAS       │
                    │                     │
                    │ Evaluación          │
                    │ Dependencias        │
                    │ Resolución          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    05 — MOTOR       │
                    │                     │
                    │ Viabilidad          │
                    │ Escenarios          │
                    │ Decision Twin       │
                    │ Negociación         │
                    │ Versionado          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      06 — SQL       │
                    │                     │
                    │ Implementación      │
                    │ Persistencia        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    07 — PRUEBAS     │
                    │                     │
                    │ Verificación        │
                    │ Validación          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 08 — IMPLEMENTACIÓN │
                    │                     │
                    │ Materialización     │
                    │ Integración         │
                    │ Verificación CI     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     99 — ARCHIVO    │
                    │                     │
                    │ Histórico           │
                    │ Obsoleto            │
                    └─────────────────────┘
```

`03_App/` aparece como dominio físico especializado de aplicación/interfaz. Su inclusión en este mapa no lo convierte en fuente de autoridad empresarial ni altera el flujo decisional del motor.

---

# 3. RELACIÓN FUNCIONAL ENTRE DOMINIOS

La relación conceptual principal es:

```text
GOBIERNO
   │
   ▼
MODELO
   │
   ▼
PARÁMETROS
   │
   ▼
ARQUITECTURA
   │
   ▼
REGLAS
   │
   ▼
MOTOR
   │
   ▼
SQL
   │
   ▼
PRUEBAS
   │
   ▼
IMPLEMENTACIÓN
```

Esta secuencia representa una relación de dependencia conceptual y no implica que todos los dominios deban ejecutarse secuencialmente en tiempo de ejecución.

La aplicación/interfaz (`03_App/`) consume y representa estructuras y resultados autorizados, pero no constituye un paso adicional de decisión ni puede crear reglas, parámetros, recomendaciones o autoridad funcional por sí misma.

---

# 4. GOBIERNO

`00_Gobierno/`

Establece el marco dentro del cual se desarrolla EIOS.

Incluye:

- identidad;
- propósito;
- alcance;
- contexto;
- gobierno;
- autoridad documental;
- salvaguarda del EIOS Vertical MVP.

La autoridad documental está determinada por:

`00_Gobierno/Matriz_Autoridad_Documental.md`

La salvaguarda oficial vigente es:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

El contexto de continuidad vigente se consulta en:

`00_Gobierno/Project_Context.md`

---

# 5. MODELO

`01_Modelo/`

Representa el dominio conceptual y funcional de EIOS.

Define el significado empresarial que posteriormente será utilizado por parámetros, reglas y motor.

---

# 6. PARÁMETROS

`02_Parametros/`

Representa los elementos configurables que permiten adaptar el comportamiento de EIOS sin modificar su estructura fundamental.

Su relación principal es:

```text
CATÁLOGO
   │
   ▼
PARAMETRIZACIÓN
   │
   ▼
REGLAS / MOTOR
```

---

# 7. ARQUITECTURA

`03_Arquitectura/`

Representa la organización estructural del sistema.

Incluye los mapas y documentos que describen:

- componentes;
- relaciones;
- estructura;
- organización global.

El `Framework_Map.md` actúa como índice maestro de navegación estructural y documental.

Este `Master_Project_Map.md` actúa como mapa global del sistema/proyecto.

## 7.1 APLICACIÓN E INTERFAZ

`03_App/`

Constituye el dominio físico especializado de especificación de aplicación/interfaz.

Incluye, entre otros, contratos y cierres relativos a:

- arquitectura UI;
- registro de campos;
- mapping campo ↔ componente;
- interacción;
- especificación visual.

`03_App/` no sustituye a `03_Arquitectura/` ni a `08_Implementacion/`.

Su función es describir y gobernar la representación e interacción dentro del alcance autorizado. La aplicación no puede convertir una salida representacional en una decisión empresarial automática ni redefinir la autoridad de los componentes que representa.

---

# 8. REGLAS

`04_Reglas/`

Representa la lógica formal de evaluación de EIOS.

Incluye:

- reglas;
- condiciones;
- dependencias;
- resolución de conflictos.

Las reglas consumen parámetros y evidencia y producen resultados evaluables por el motor.

---

# 9. MOTOR DE DECISIÓN

`05_Motor/`

Representa el núcleo de procesamiento decisional.

Incluye los componentes necesarios para transformar evaluaciones en análisis estructurado de alternativas.

Conceptualmente:

```text
REGLAS
   │
   ▼
EVALUACIÓN
   │
   ▼
VIABILIDAD / ESCENARIOS
   │
   ▼
DECISION TWIN
   │
   ▼
NEGOCIACIÓN / RESULTADOS
```

---

# 10. SQL

`06_SQL/`

Representa la capa de persistencia e implementación SQL del sistema.

Su función es materializar técnicamente las estructuras necesarias para soportar EIOS.

SQL no redefine la lógica empresarial ni la autoridad documental.

---

# 11. PRUEBAS

`07_Pruebas/`

Representa la capa de verificación y validación.

Su función es comprobar que la implementación satisface las especificaciones y criterios establecidos por las fuentes de autoridad correspondientes.

---

# 12. IMPLEMENTACIÓN

`08_Implementacion/`

Representa la capa de materialización técnica controlada de los contratos y diseños autorizados.

Incluye los contratos de implementación, registros de verificación y documentación necesaria para conectar diseño, persistencia, código y CI sin crear autoridad funcional paralela.

La relación con la aplicación/interfaz se mantiene separada:

```text
03_App/            → especificación y gobierno de representación/interacción
08_Implementacion/ → contratos y gobierno de materialización técnica
 eios/              → código ejecutable
 tests/             → verificación automatizada
 .github/           → CI y validaciones técnicas
```

Ninguna de estas capas adquiere autoridad empresarial por el mero hecho de estar implementada o superar CI.

---

# 13. ARCHIVO

`99_Archivo/`

Conserva documentación histórica, sustituida u obsoleta por razones de trazabilidad.

Los documentos archivados no constituyen autoridad sobre el diseño vigente salvo indicación expresa.

---

# 14. EIOS VERTICAL MVP

El EIOS Vertical MVP se encuentra gobernado por la Salvaguarda Vertical MVP.

Su posición dentro del Framework es:

```text
EIOS FRAMEWORK
      │
      ▼
GOBIERNO
      │
      ▼
SALVAGUARDA VERTICAL MVP
      │
      ▼
DOMINIOS EIOS
      │
      ├── Modelo
      ├── Parámetros
      ├── Arquitectura
      ├── Aplicación / interfaz
      ├── Reglas
      ├── Motor
      ├── SQL
      ├── Pruebas
      └── Implementación
```

La Salvaguarda establece las restricciones y principios que deben respetarse durante la evolución del Vertical MVP.

La presencia de un dominio en este mapa no implica que todas sus capacidades estén cerradas ni autoriza a resolver por inferencia bloqueos de autoridad, evidencia o dependencia.

---

# 15. RELACIÓN CON FRAMEWORK MAP

Los dos documentos cumplen funciones diferentes:

| Documento | Función |
|---|---|
| `Framework_Map.md` | Índice maestro de navegación estructural y documental |
| `Master_Project_Map.md` | Mapa global del sistema y sus relaciones |

El `Framework_Map.md` responde principalmente a:

> **¿Dónde está cada dominio y dónde debo buscar su documentación o materialización vigente?**

El `Master_Project_Map.md` responde principalmente a:

> **¿Cómo se organiza EIOS como sistema/proyecto?**

---

# 16. REGLA DE AUTORIDAD

Este documento no constituye una fuente de autoridad funcional por encima de los documentos especializados.

Cuando exista una contradicción documental, se deberá consultar:

`00_Gobierno/Matriz_Autoridad_Documental.md`

Para conocer el estado operativo y de continuidad vigente se deberá consultar:

`00_Gobierno/Project_Context.md`

El punto formal de recuperación más reciente es `EIOS-BL-004 @ d3c462a2536ee20204b9d5c9dce1024e1ca7d31c`, identificado mediante `00_Gobierno/Baselines/`, sin sustituir el estado posterior de `main`.

---

# 17. ESTADO

**Framework:** EIOS  
**Baseline de continuidad vigente:** EIOS-BL-004 @ `d3c462a2536ee20204b9d5c9dce1024e1ca7d31c`  
**Estado:** En desarrollo  
**Gobierno:** Activo  
**Salvaguarda Vertical MVP:** Vigente  
**Versión del mapa:** 2.4

---

# 18. PRINCIPIO FINAL

> El Master Project Map muestra cómo se estructura EIOS; los documentos especializados definen cada dominio. La aplicación representa lo autorizado, no crea autoridad decisional nueva.
