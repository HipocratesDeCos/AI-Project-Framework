# EIOS — FRAMEWORK MAP

## Índice Maestro del Framework

**Versión:** 2.3  
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

Documentación de gobierno, autoridad, contexto, control, trazabilidad y salvaguarda del proyecto.

### Documentos actuales

- `Project_Charter.md`
- `Project_Context.md`
- `Project_Governance.md`
- `Matriz_Autoridad_Documental.md`
- `Manual_Maestro_Proyecto_EIOS.md`
- `EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`
- `Especificacion_Evidencia_Trazabilidad_F3.md`
- `Registro_Evidencias_Trazabilidad_F3.md`

---

## 01 — MODELO

`01_Modelo/`

Documentación correspondiente al dominio de modelo funcional y empresarial.

### Documentos actuales

- `Especificacion_funcional.md`

Los documentos históricos o sustituidos se conservan en `99_Archivo/`.

---

## 02 — PARÁMETROS

`02_Parametros/`

Documentación correspondiente al catálogo, gobierno, decisiones y relaciones de parametrización.

### Documentos actuales

- `Catalogo_Parametros_MVP_v0.3.md`
- `Centro_Parametrizacion.md`
- `Decision_Log_Parametros_MVP.md`
- `Matriz_Parametros_Reglas_MVP.md`

---

## 03 — ARQUITECTURA

`03_Arquitectura/`

Documentación correspondiente a la organización arquitectónica y mapa del Framework.

### Documentos actuales

- `03_LEEME_Como_se_organiza_EIOS.md`
- `Architecture_Blueprint.md`
- `DSS_Functional_Architecture.md`
- `Framework_Map.md`
- `Master_Project_Map.md`

---

## 04 — REGLAS

`04_Reglas/`

Documentación correspondiente al sistema de reglas, evidencia, dependencias y resolución de conflictos.

### Documentos actuales

- `Capa_resolucion_conflictos.md`
- `Evidence_Contract.md`
- `Especificacion_Reglas_Configuracion_Pagos_MVP.md`
- `Especificacion_Reglas_Historico_MVP.md`
- `Matriz_Reglas_MVP.md`
- `Reglas_MVP.md`
- `Rule_Dependency_Matrix.md`

---

## 05 — MOTOR

`05_Motor/`

Documentación correspondiente al motor y comportamiento decisional.

### Documentos actuales

- `Modelo_Empresarial_Decision.md`
- `Viability_Frontier.md`
- `Viability_Scenario_Engine.md`
- `Decision_Twin.md`
- `Decision_Versioning.md`
- `Negotiation_Intelligence.md`
- `Negotiation_Ladder.md`

---

## 06 — SQL

`06_SQL/`

Dominio correspondiente a la implementación y persistencia SQL, bajo la autoridad documental específica definida para este dominio.

### Documentos actuales

- `06_LEEME_SQL.md`
- `Modelo_Fisico_SQL_Server_C0.md`
- `Decision_Versioning_Physical_Model.md`
- `001_C0_Schema.sql`
- `002_Decision_Versioning_Schema.sql`

Los artefactos de validación SQL de CI se mantienen en `.github/sql/` y forman parte del mecanismo de verificación, no del índice documental de `06_SQL`:

- `.github/sql/validate_c0_schema.sql`
- `.github/sql/validate_decision_versioning_schema.sql`

`06_LEEME_SQL.md` constituye el contrato documental del dominio SQL y establece su organización y criterios de implementación. La existencia de este documento no atribuye a SQL autoridad funcional, decisional, de versionado ni de reconstrucción semántica.

---

## 07 — PRUEBAS

`07_Pruebas/`

Documentación correspondiente a pruebas y verificación.

### Documentos actuales

- `Plan_Pruebas_MVP.md`
- `Matriz_Trazabilidad_Ejecutable.md`

`Matriz_Trazabilidad_Ejecutable.md` materializa la estructura de trazabilidad ejecutable entre requisitos verificables, fuentes autorizadas, artefactos físicos, dependencias, estados y condiciones de ejecución. No crea una autoridad funcional ni una taxonomía paralela de pruebas.

---

## 08 — IMPLEMENTACIÓN

`08_Implementacion/`

Documentación correspondiente a la materialización técnica controlada del diseño y sus contratos de implementación.

### Documentos actuales

- `Assessment_Individual_Result_Contract.md`
- `C0_CI_Verification.md`
- `Decision_Versioning_Implementation_Contract.md`

La implementación ejecutable se encuentra materializada adicionalmente en `eios/` y verificada mediante `tests/`.

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
