# EIOS — FRAMEWORK MAP

## Índice Maestro del Framework

**Versión:** 2.0  
**Estado:** APROBADO  
**Función:** Índice maestro de la estructura documental EIOS  
**Ubicación:** `03_Arquitectura/Framework_Map.md`

---

# 1. PROPÓSITO

Este documento constituye el mapa maestro de navegación del Framework EIOS.

Su función es identificar la estructura documental oficial del proyecto y facilitar la localización de cada dominio.

No desarrolla conceptos, reglas ni especificaciones.

---

# 2. ESTRUCTURA OFICIAL

## 00 — GOBIERNO

`00_Gobierno/`

Documentación de gobierno, autoridad, contexto, control y salvaguarda del proyecto.

### Documentos actuales

- `Project_Charter.md`
- `Project_Context.md`
- `Project_Governance.md`
- `Matriz_Autoridad_Documental.md`
- `Manual_Maestro_Proyecto_EIOS.md`
- `EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

---

## 01 — MODELO

`01_Modelo/`

Documentación correspondiente al dominio de modelo.

### Documentos actuales

- `01_LEEME_Que_necesita_la_empresa.md`
- `Especificacion_funcional.md`

---

## 02 — PARÁMETROS

`02_Parametros/`

Documentación correspondiente al catálogo y parametrización.

### Documentos actuales

- `Catalogo_Parametros_MVP_v0.2.md`
- `Centro_Parametrizacion.md`

---

## 03 — ARQUITECTURA

`03_Arquitectura/`

Documentación correspondiente a la organización arquitectónica y mapa del Framework.

### Documentos actuales

- `03_LEEME_Como_se_organiza_EIOS.md`
- `Architecture_Blueprint.md`
- `Framework_Map.md`
- `Master_Project_Map.md`

---

## 04 — REGLAS

`04_Reglas/`

Documentación correspondiente al sistema de reglas y resolución de conflictos.

### Documentos actuales

- `Capa_resolucion_conflictos.md`
- `Matriz_Reglas_MVP.md`

---

## 05 — MOTOR

`05_Motor/`

Documentación correspondiente al motor y comportamiento decisional.

### Documentos actuales

- `04_LEEME_Como_piensa_y_decide_EIOS.md`
- `05_LEEME_Como_se_presenta.md`
- `Modelo_Empresarial_Decision.md`

---

## 06 — SQL

`06_SQL/`

Documentación correspondiente al dominio SQL.

### Documentos actuales

- `06_LEEME_Como_funciona_en_produccion.md`

---

## 07 — PRUEBAS

`07_Pruebas/`

Documentación correspondiente a pruebas y verificación.

### Documentos actuales

- `07_LEEME_Como_se_construye.md`

---

## 99 — ARCHIVO

`99_Archivo/`

Repositorio histórico de documentación sustituida, obsoleta o conservada por trazabilidad.

### Contenido

El contenido histórico se mantiene fuera del Framework operativo y no constituye autoridad sobre el diseño vigente de EIOS.

---

# 3. NODO DE GOBIERNO ACTIVO

El nodo de Gobierno constituye actualmente el nivel superior de control documental del proyecto.

Su estructura de autoridad se encuentra definida por:

`Matriz_Autoridad_Documental.md`

La Salvaguarda oficial vigente del EIOS Vertical MVP es:

`EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

---

# 4. REGLA DE NAVEGACIÓN

La estructura numérica de carpetas establece la organización documental del Framework.

La autoridad de cada documento no viene determinada únicamente por su posición en la estructura.

La autoridad documental se determina mediante:

`00_Gobierno/Matriz_Autoridad_Documental.md`

---

# 5. ESTADO DEL FRAMEWORK

**Framework:** EIOS  
**Baseline vigente:** EIOS Vertical MVP  
**Estado:** En desarrollo  
**Gobierno:** Activo  
**Salvaguarda Vertical MVP:** Vigente

---

# 6. REGLA DEL FRAMEWORK MAP

Este documento tiene carácter exclusivamente estructural y de navegación.

No debe utilizarse para:

- definir reglas de negocio;
- definir parámetros;
- definir arquitectura detallada;
- definir lógica decisional;
- sustituir documentos especializados;
- establecer autoridad documental.

Cuando exista una contradicción entre este documento y un documento especializado, prevalece la autoridad definida en `Matriz_Autoridad_Documental.md`.

---

# 7. PRINCIPIO FINAL

> El Framework Map muestra dónde está cada cosa; la Matriz de Autoridad determina qué documento manda.
