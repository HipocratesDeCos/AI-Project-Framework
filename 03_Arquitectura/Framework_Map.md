# EIOS — FRAMEWORK MAP

## Índice Maestro del Framework

**Versión:** 3.1  
**Estado:** APROBADO — reconciliación post-E2E Execution Boundary  
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

Documentación correspondiente a gobierno, autoridad, contexto, control, trazabilidad y salvaguarda del proyecto.

### Documentos actuales

- `Project_Charter.md`
- `Project_Context.md`
- `Project_Governance.md`
- `Matriz_Autoridad_Documental.md`
- `Manual_Maestro_Proyecto_EIOS.md`
- `EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`
- `Especificacion_Evidencia_Trazabilidad_F3.md`
- `Registro_Evidencias_Trazabilidad_F3.md`

## 01 — MODELO

`01_Modelo/`

### Documentos actuales

- `Especificacion_funcional.md`

## 02 — PARÁMETROS

`02_Parametros/`

### Documentos actuales

- `Catalogo_Parametros_MVP_v0.3.md`
- `Centro_Parametrizacion.md`
- `Decision_Log_Parametros_MVP.md`
- `Matriz_Parametros_Reglas_MVP.md`

## 03 — ARQUITECTURA

`03_Arquitectura/`

### Documentos actuales

- `03_LEEME_Como_se_organiza_EIOS.md`
- `Architecture_Blueprint.md`
- `DSS_Functional_Architecture.md`
- `Framework_Map.md`
- `Master_Project_Map.md`

## 04 — REGLAS

`04_Reglas/`

### Documentos actuales

- `Capa_resolucion_conflictos.md`
- `Evidence_Contract.md`
- `Especificacion_Reglas_Configuracion_Pagos_MVP.md`
- `Especificacion_Reglas_Historico_MVP.md`
- `Matriz_Reglas_MVP.md`
- `Reglas_MVP.md`
- `Rule_Dependency_Matrix.md`

## 05 — MOTOR

`05_Motor/`

### Documentos actuales

- `Modelo_Empresarial_Decision.md`
- `Viability_Frontier.md`
- `Viability_Scenario_Engine.md`
- `Decision_Twin.md`
- `Decision_Versioning.md`
- `Negotiation_Intelligence.md`
- `Negotiation_Ladder.md`

## 06 — SQL

`06_SQL/`

### Documentos actuales

- `06_LEEME_SQL.md`
- `Modelo_Fisico_SQL_Server_C0.md`
- `Decision_Versioning_Physical_Model.md`

### Migraciones SQL actuales

- `001_C0_Schema.sql`
- `002_Decision_Versioning_Schema.sql`
- `003_Centro_Parametrizacion_Schema.sql`

## 07 — PRUEBAS

`07_Pruebas/`

### Documentos actuales

- `Plan_Pruebas_MVP.md`
- `Matriz_Trazabilidad_Ejecutable.md`
- `O1_Cierre_Materializacion.md`
- `O2_Cierre_Materializacion.md`
- `O3_Cierre.md`
- `O3_Cierre_PostMerge.md`
- `O3_Auditoria2_Implementacion_Corregida.md`
- `O4_Cierre_Materializacion.md`
- `O4_Auditoria2_Implementacion.md`
- `Reconciliacion_Decision_Versioning_NI_NL.md`
- `U1_Cierre_Materializacion.md`
- `U1_1_Cierre_Materializacion.md`
- `U1_1_Reconciliacion_PostIntegracion.md`
- `E2E_Diseno_Execution_Boundary.md`
- `E2E_Auditoria_Execution_Boundary.md`
- `E2E_Auditoria2_Execution_Boundary.md`
- `E2E_Auditoria_Implementacion_Execution_Boundary.md`
- `E2E_Auditoria2_Implementacion_Execution_Boundary.md`
- `E2E_Cierre_Execution_Boundary.md`
- `E2E_Cierre_Implementacion_Execution_Boundary.md`
- `E2E_Reconciliacion_PostIntegracion.md`

Estos documentos registran pruebas, auditorías, cierres y reconciliaciones materializadas. No crean una autoridad funcional paralela.

## 08 — IMPLEMENTACIÓN

`08_Implementacion/`

### Contratos actuales

1. `Assessment_Individual_Result_Contract.md`
2. `C0_CI_Verification.md`
3. `CRC_MVP_Implementation_Contract.md`
4. `Centro_Parametrizacion_Implementation_Contract.md`
5. `Decision_Twin_Comparison_Contract.md`
6. `Decision_Twin_Implementation_Contract.md`
7. `Decision_Versioning_Implementation_Contract.md`
8. `Negotiation_Intelligence_Implementation_Contract.md`
9. `Negotiation_Ladder_Implementation_Contract.md`
10. `O4_Controlled_Scenario_Generation_Implementation_Contract.md`
11. `Price_Intelligence_Implementation_Contract.md`
12. `Quality_Trust_Implementation_Contract.md`
13. `Scenario_Evaluation_Implementation_Contract.md`
14. `TCO_Core_CI_Verification.md`
15. `TCO_Core_Implementation_Contract.md`
16. `U1_Frontend_Implementation_Contract.md`
17. `U1_1_Visual_Frontend_Implementation_Contract.md`
18. `Viability_Frontier_Design_Audit.md`
19. `E2E_Execution_Boundary_Implementation_Contract.md`

La implementación ejecutable se encuentra materializada adicionalmente en `eios/` y verificada mediante `tests/`.

## 99 — ARCHIVO

`99_Archivo/`

Repositorio histórico de documentación sustituida, obsoleta o conservada por trazabilidad.

El contenido histórico se mantiene fuera del Framework operativo y no constituye autoridad sobre el diseño vigente de EIOS.

---

# 3. NODO DE GOBIERNO ACTIVO

El nodo de Gobierno constituye actualmente el nivel superior de control documental del proyecto.

Su estructura de autoridad se encuentra definida por:

`00_Gobierno/Matriz_Autoridad_Documental.md`

La Salvaguarda oficial vigente del EIOS Vertical MVP es:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

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
