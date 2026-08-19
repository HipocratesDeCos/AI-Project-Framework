# EIOS — MASTER PROJECT MAP

## Mapa Maestro del Proyecto y de la Arquitectura

**Versión:** 2.0  
**Estado:** APROBADO  
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
                    │ 03 — ARQUITECTURA  │
                    │                     │
                    │ Estructura          │
                    │ Componentes         │
                    │ Relaciones          │
                    └──────────┬──────────┘
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
                    │ persistencia        │
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
                    │     99 — ARCHIVO     │
                    │                     │
                    │ Histórico           │
                    │ Obsoleto            │
                    └─────────────────────┘
```

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
```

Esta secuencia representa una relación de dependencia conceptual y no implica que todos los dominios deban ejecutarse secuencialmente en tiempo de ejecución.

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

El `Framework_Map.md` actúa como índice documental.

Este `Master_Project_Map.md` actúa como mapa global del sistema/proyecto.

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

# 12. ARCHIVO

`99_Archivo/`

Conserva documentación histórica, sustituida u obsoleta por razones de trazabilidad.

Los documentos archivados no constituyen autoridad sobre el diseño vigente salvo indicación expresa.

---

# 13. EIOS VERTICAL MVP

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
      ├── Reglas
      ├── Motor
      ├── SQL
      └── Pruebas
```

La Salvaguarda establece las restricciones y principios que deben respetarse durante la evolución del Vertical MVP.

---

# 14. RELACIÓN CON FRAMEWORK MAP

Los dos documentos cumplen funciones diferentes:

| Documento | Función |
|---|---|
| `Framework_Map.md` | Índice maestro de documentación |
| `Master_Project_Map.md` | Mapa global del sistema y sus relaciones |

El `Framework_Map.md` responde principalmente a:

> **¿Dónde está cada documento?**

El `Master_Project_Map.md` responde principalmente a:

> **¿Cómo se organiza EIOS como sistema/proyecto?**

---

# 15. REGLA DE AUTORIDAD

Este documento no constituye una fuente de autoridad funcional por encima de los documentos especializados.

Cuando exista una contradicción documental, se deberá consultar:

`00_Gobierno/Matriz_Autoridad_Documental.md`

---

# 16. ESTADO

**Framework:** EIOS  
**Baseline:** EIOS Vertical MVP  
**Estado:** En desarrollo  
**Gobierno:** Activo  
**Salvaguarda Vertical MVP:** Vigente  
**Versión del mapa:** 2.0

---

# 17. PRINCIPIO FINAL

> El Master Project Map muestra cómo se estructura EIOS; los documentos especializados definen cada dominio.
