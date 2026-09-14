# EIOS — FRAMEWORK MAP

## Índice Maestro del Framework

**Versión:** 3.3.2  
**Estado:** APROBADO — reconciliación de continuidad post-EIOS-BL-003  
**Función:** Índice maestro de navegación de la estructura documental y técnica EIOS  
**Ubicación:** `03_Arquitectura/Framework_Map.md`

---

# 1. PROPÓSITO

Este documento constituye el mapa maestro de navegación del Framework EIOS.

Su función es responder principalmente a:

> **¿Dónde está cada dominio y dónde debo buscar su documentación o materialización vigente?**

No desarrolla conceptos, reglas, metodologías ni especificaciones funcionales.

No sustituye a:

- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `03_Arquitectura/Master_Project_Map.md`;
- las fuentes especializadas de cada dominio.

---

# 2. REGLA DE INVENTARIO

EIOS contiene dominios de alta evolución documental. Por ello, este mapa **no pretende enumerar todos los archivos existentes**.

La regla de navegación es:

```text
FRAMEWORK MAP
      ↓
identifica dominio / carpeta / anclas
      ↓
ÁRBOL FÍSICO DE LA CARPETA
      ↓
inventario exhaustivo vigente
      ↓
MATRIZ DE AUTORIDAD
      ↓
fuente oficial aplicable
```

Las listas de este documento son **anclas de navegación**, no inventarios exhaustivos ni una segunda fuente de autoridad.

La interfaz documental estable de este mapa conserva secciones `## 00 — …` a `## 08 — …`. Esta estructura permite que las verificaciones automáticas comprueben que las anclas declaradas existen físicamente sin obligar a convertir el mapa en un catálogo exhaustivo.

---

# 3. MAPA FÍSICO OPERATIVO

```text
AI-Project-Framework/
│
├── 00_Gobierno/        Gobierno, autoridad, continuidad y Baselines
├── 01_Modelo/          Metodología y modelo funcional especializado
├── 02_Parametros/      Parámetros y parametrización
├── 03_App/             Contratos y especificaciones de interfaz/aplicación
├── 03_Arquitectura/    Arquitectura y mapas del sistema
├── 04_Reglas/          Reglas, evidencia, dependencias y CRC
├── 05_Motor/           Viabilidad, escenarios, Twin, negociación y versionado
├── 06_SQL/             Modelos y migraciones SQL
├── 07_Pruebas/         Auditorías, pruebas, cierres y reconciliaciones
├── 08_Implementacion/  Contratos y gobierno de implementación técnica
├── 99_Archivo/         Histórico / obsoleto
│
├── eios/               Implementación ejecutable
├── tests/              Suite automatizada
└── .github/            CI y validaciones automatizadas
```

Otros directorios auxiliares pueden existir en el repositorio. Su presencia física no les concede autoridad funcional.

---

## 00 — GOBIERNO

`00_Gobierno/`

Gobierno, identidad, contexto, autoridad, trazabilidad y salvaguarda del proyecto.

### Anclas verificables

- `Project_Charter.md`
- `Project_Context.md`
- `Project_Governance.md`
- `Matriz_Autoridad_Documental.md`
- `Manual_Maestro_Proyecto_EIOS.md`
- `EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`
- `Especificacion_Evidencia_Trazabilidad_F3.md`
- `Registro_Evidencias_Trazabilidad_F3.md`
- `Baselines/EIOS-BL-001.md`
- `Baselines/EIOS-BL-002.md`
- `Baselines/EIOS-BL-003.md`

Los Baselines fijan puntos formales de continuidad asociados a SHAs concretos. No sustituyen la autoridad especializada de los componentes que resumen.

## 01 — MODELO

`01_Modelo/`

Dominio metodológico y funcional especializado.

Incluye, entre otras familias vigentes o históricamente trazables dentro del árbol físico:

- Price Intelligence;
- Stock / Demand;
- Delivery Stockout;
- Finance Basic;
- Supplier Evidence / Supplier Risk;
- Rotation;
- Viability Frontier;
- especificación funcional general.

### Anclas verificables

- `Especificacion_funcional.md`
- `Price_Intelligence_Methodological_Matrix.md`
- `Stock_Demand_Methodological_Matrix.md`
- `Delivery_Stockout_Methodological_Closure_v0.3.md`
- `Finance_Basic_Methodological_Closure_v0.3.md`
- `Supplier_Evidence_Core_Methodological_Closure_v0.3.md`
- `Rotation_Track_A_Methodological_Closure_v0.1.md`
- `Viability_Frontier_Methodological_Matrix.md`

El estado y autoridad de cada familia debe resolverse en sus documentos especializados; aparecer en este mapa no implica que una unidad esté implementada ni desbloqueada.

## 02 — PARÁMETROS

`02_Parametros/`

Parámetros, configuración y trazabilidad de cambios parametrizables.

### Anclas verificables

- `Catalogo_Parametros_MVP_v0.3.md`
- `Centro_Parametrizacion.md`
- `Decision_Log_Parametros_MVP.md`
- `Matriz_Parametros_Reglas_MVP.md`

La autoridad exacta de parámetros/configuración se determina mediante `00_Gobierno/Matriz_Autoridad_Documental.md`.

## 03 — ARQUITECTURA

`03_Arquitectura/`

Arquitectura lógica, estructura global y mapas de navegación.

### Anclas verificables

- `Architecture_Blueprint.md`
- `DSS_Functional_Architecture.md`
- `Framework_Map.md`
- `Master_Project_Map.md`

| Documento | Función |
|---|---|
| `Framework_Map.md` | ¿Dónde está cada dominio/documento? |
| `Master_Project_Map.md` | ¿Cómo se organiza EIOS como sistema/proyecto? |
| `Architecture_Blueprint.md` | Arquitectura lógica/técnica autorizada |

### Aplicación e interfaz — `03_App/`

`03_App/` es un dominio físico adicional de aplicación/interfaz que no se confunde con `03_Arquitectura/`.

Contiene ciclos documentales para arquitectura de UI, inventario/registro de campos, mapping campo ↔ componente, interacción y especificación visual.

Anclas de navegación de aplicación:

- UI visual: `UI_EIOS_Visual_Specification_v0.1.md`
- arquitectura UI: `UI_Architecture_Contract_v0.1.md`
- registro de campos: `UI_Field_Registry_v0.1.md`
- mapping: `UI_Field_Component_Mapping_v0.2.md`
- interacción: `UI_Interaction_Functional_Contract_v0.1.md`

Las auditorías, depuraciones y cierres asociados se consultan físicamente en `03_App/` cuando se evalúe una unidad concreta.

## 04 — REGLAS

`04_Reglas/`

Reglas, evidencia, dependencias y resolución de conflictos.

### Anclas verificables

- `Matriz_Reglas_MVP.md`
- `Evidence_Contract.md`
- `Rule_Dependency_Matrix.md`
- `Capa_resolucion_conflictos.md`

Las especificaciones especializadas de reglas presentes en el árbol físico desarrollan relaciones concretas sin crear por ello una segunda autoridad transversal.

`Reglas_MVP.md` puede conservar función histórica/de referencia según el gobierno vigente; no sustituye a la Matriz de Reglas como fuente oficial cuando exista discrepancia.

## 05 — MOTOR

`05_Motor/`

Componentes especializados del procesamiento decisional y representacional.

### Anclas verificables

- `Modelo_Empresarial_Decision.md`
- `Viability_Frontier.md`
- `Viability_Scenario_Engine.md`
- `Decision_Twin.md`
- `Decision_Versioning.md`
- `Negotiation_Intelligence.md`
- `Negotiation_Ladder.md`

Estas fuentes no convierten EIOS en decisor empresarial automático. La frontera humana permanece vigente.

## 06 — SQL

`06_SQL/`

Persistencia y materialización SQL.

### Anclas verificables

- `06_LEEME_SQL.md`
- `Modelo_Fisico_SQL_Server_C0.md`
- `Decision_Versioning_Physical_Model.md`
- `001_C0_Schema.sql`
- `002_Decision_Versioning_Schema.sql`
- `003_Centro_Parametrizacion_Schema.sql`

El inventario exhaustivo debe consultarse en la carpeta física.

## 07 — PRUEBAS

`07_Pruebas/`

Concentra evidencia documental de diseño de pruebas, auditorías 1/2, depuraciones, cierres, gates, reconciliaciones postintegración y trazabilidad ejecutable.

### Anclas verificables

- `Plan_Pruebas_MVP.md`
- `Matriz_Trazabilidad_Ejecutable.md`
- `Framework_Map_Structural_Reconciliation_Audit_v0.1.md`

Los numerosos artefactos de auditoría/cierre se consultan mediante el inventario físico del directorio para evitar que este mapa quede obsoleto con cada unidad cerrada.

`07_Pruebas/` verifica; no crea por sí misma autoridad funcional paralela.

## 08 — IMPLEMENTACIÓN

`08_Implementacion/`

Contratos, auditorías, cierres y reconciliaciones de materialización técnica.

### Anclas verificables

- `Price_Intelligence_Implementation_Contract.md`
- `Quality_Trust_Implementation_Contract.md`
- `TCO_Core_Implementation_Contract.md`
- `Viability_Frontier_Implementation_Contract.md`
- `E2E_Execution_Boundary_Implementation_Contract.md`

El dominio incluye además familias de Assessment/provenance, C0/Rules, Parameter Configuration, STK, Delivery Stockout, Finance Basic, Supplier Evidence Core, Scenario/O2–O4, Decision Twin, Negotiation Intelligence/Ladder, CRC, Decision Versioning, UI/U1/U1.1 y reconciliaciones de provenance/postintegración.

No se mantiene aquí una enumeración exhaustiva de contratos, porque su inventario canónico operativo es el árbol físico de `08_Implementacion/`.

La existencia de un archivo en esta carpeta no implica por sí sola que esté cerrado; debe consultarse su estado y ciclo documental concreto.

## 99 — ARCHIVO

`99_Archivo/`

Material histórico, sustituido u obsoleto conservado por trazabilidad.

El contenido archivado no constituye autoridad sobre el diseño vigente salvo decisión expresa de gobierno.

---

# 4. IMPLEMENTACIÓN EJECUTABLE

`eios/`

Código ejecutable materializado conforme a contratos autorizados.

Regla:

> El código implementa autoridad existente; no crea silenciosamente autoridad empresarial nueva.

Para determinar la legitimidad de una capacidad debe trazarse:

```text
fuente funcional / metodológica
        ↓
contrato de implementación
        ↓
código
        ↓
pruebas
        ↓
CI / reconciliación
```

---

# 5. TESTS AUTOMATIZADOS

`tests/`

Suite automatizada que verifica comportamiento y regresiones.

No sustituye a `07_Pruebas/`: ambos cumplen funciones complementarias.

```text
07_Pruebas/ → evidencia documental de verificación
 tests/      → verificación automatizada ejecutable
```

Un test puede demostrar conformidad, pero no redefinir la especificación que prueba.

---

# 6. CI Y VALIDACIONES

`.github/`

Materializa automatización de integración continua y validaciones técnicas.

Rutas relevantes:

- workflow: `.github/workflows/tests.yml`
- validaciones SQL: `.github/sql/`

La CI es un gate técnico. Un `SUCCESS` no sustituye a la autoridad metodológica, funcional o documental que deba existir antes de implementar.

---

# 7. SUBÁRBOLES Y COPIAS AUXILIARES

La presencia de un subárbol, copia, exportación o material auxiliar dentro del repositorio no lo convierte automáticamente en fuente oficial.

En particular, ante cualquier duplicación aparente debe aplicarse:

```text
Matriz_Autoridad_Documental.md
        ↓
fuente oficial vigente
        ↓
documento especializado
```

No debe resolverse autoridad por similitud de nombres ni por la fecha más reciente de una copia auxiliar.

---

# 8. NODO DE GOBIERNO ACTIVO

La autoridad y precedencia documental se determinan mediante:

`00_Gobierno/Matriz_Autoridad_Documental.md`

La Salvaguarda vigente del Vertical MVP es:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

El punto formal de continuidad más reciente es:

`00_Gobierno/Baselines/EIOS-BL-003.md`

El Baseline no sustituye a las fuentes especializadas.

---

# 9. REGLA DE NAVEGACIÓN Y AUTORIDAD

La estructura de carpetas permite localizar conocimiento y materialización.

La autoridad **no** se deriva únicamente de ubicación, antigüedad, nombre del archivo, existencia de código, existencia de tests o CI verde.

La autoridad se resuelve mediante el gobierno documental y las fuentes especializadas aplicables.

---

# 10. MANTENIMIENTO DEL MAPA

Framework Map debe actualizarse cuando cambie de forma relevante:

- la estructura de dominios;
- una ruta de navegación principal;
- una fuente/ancla estructural;
- la ubicación de una capacidad principal.

No debe actualizarse por cada nuevo artefacto de auditoría, cierre, reconciliación o test si la ruta de dominio permanece estable.

Esta regla evita convertir el mapa en un inventario manual frágil.

---

# 11. ESTADO DEL FRAMEWORK

**Framework:** EIOS  
**Baseline de continuidad vigente:** EIOS-BL-003  
**Estado:** En desarrollo  
**Gobierno:** Activo  
**Salvaguarda Vertical MVP:** Vigente  
**Versión del mapa:** 3.3.2

---

# 12. PRINCIPIO FINAL

> **Framework Map indica dónde buscar. La Matriz de Autoridad determina qué fuente manda. Los documentos especializados definen el contenido. El código y las pruebas materializan y verifican lo autorizado.**