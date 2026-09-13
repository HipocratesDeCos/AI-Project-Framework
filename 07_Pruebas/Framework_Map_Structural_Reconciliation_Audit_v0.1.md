# EIOS — Framework Map Structural Reconciliation Audit v0.1

**Estado:** AUDIT 2 SUPERADA — AUTORIZADA MATERIALIZACIÓN DOCUMENTAL  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 87d357fc487c450df796c51a303122bcb8d93700`  
**Documento auditado:** `03_Arquitectura/Framework_Map.md` v3.2

---

## 1. Objeto

Auditar si `Framework_Map.md` sigue cumpliendo su función declarada de índice maestro de navegación del Framework EIOS después del crecimiento materializado entre `EIOS-BL-001` y `EIOS-BL-002`.

La auditoría es exclusivamente estructural/documental. No evalúa ni redefine lógica empresarial.

---

## 2. Autoridad aplicable

Se contrastan:

- `00_Gobierno/Project_Governance.md`;
- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `03_Arquitectura/Master_Project_Map.md`;
- `03_Arquitectura/Framework_Map.md`;
- árbol físico de `main`;
- `00_Gobierno/Baselines/EIOS-BL-002.md`.

La Matriz de Autoridad establece que `Framework_Map.md` es índice documental, no fuente funcional. `Master_Project_Map.md` define la organización global y los documentos especializados conservan la autoridad de cada dominio.

---

## 3. Hallazgos de Audit 1

### FM-G01 — `03_App/` omitido — HALLAZGO CONFIRMADO

El árbol físico contiene `03_App/` con especificaciones y ciclos documentales de UI, pero Framework Map v3.2 no representa ese dominio.

Impacto: navegación incompleta.

### FM-G02 — inventario `01_Modelo/` materialmente incompleto — HALLAZGO CONFIRMADO

v3.2 enumera únicamente:

- `Especificacion_funcional.md`;
- `Stock_Demand_Methodological_Matrix.md`.

El árbol actual contiene además familias metodológicas de Price Intelligence, STK, Delivery Stockout, Finance Basic, Supplier Evidence/Risk, Rotation, Viability Frontier y otras.

Impacto: el listado deja de ser un índice fiable.

### FM-G03 — inventario `08_Implementacion/` materialmente incompleto — HALLAZGO CONFIRMADO

v3.2 enumera 20 contratos/artefactos, mientras la carpeta física contiene muchas unidades posteriores, auditorías, cierres, reconciliaciones y contratos de provenance.

Impacto: navegar exclusivamente por el índice oculta material vigente.

### FM-G04 — Baselines no representados — HALLAZGO CONFIRMADO

`00_Gobierno/Baselines/` contiene actualmente `EIOS-BL-001.md` y `EIOS-BL-002.md`, pero v3.2 no expone el nodo de Baselines.

Impacto: pérdida de una ruta esencial de recuperación formal.

### FM-G05 — ejecutables y CI insuficientemente explicitados — HALLAZGO PARCIAL

v3.2 menciona `eios/` y `tests/` al describir implementación, pero no integra claramente en el mapa operativo:

- `eios/` — implementación ejecutable;
- `tests/` — pruebas automatizadas;
- `.github/workflows/` — CI;
- `.github/sql/` — validaciones SQL de CI.

No son nuevas autoridades documentales, pero sí nodos físicos relevantes de navegación técnica.

### FM-G06 — modelo de mantenimiento demasiado frágil — HALLAZGO CONFIRMADO

La enumeración manual exhaustiva de archivos en dominios de alta evolución obliga a modificar el Framework Map por cada artefacto especializado. Esto contradice su carácter de mapa/índice y aumenta la obsolescencia documental.

---

## 4. Depuración de diseño

Se descartan dos soluciones:

1. **enumerar todos los archivos actuales**: volvería a quedar obsoleto con nuevos PR;
2. **eliminar todas las anclas documentales**: reduciría demasiado la utilidad de navegación.

Solución depurada:

- mantener el mapa por dominios físicos;
- listar únicamente **anclas canónicas o de navegación**;
- para dominios de alta evolución, declarar que el inventario exhaustivo corresponde al árbol físico de la carpeta;
- incorporar `03_App/`;
- incorporar `00_Gobierno/Baselines/`;
- distinguir documentación (`07_Pruebas/`, `08_Implementacion/`) de ejecutables (`eios/`, `tests/`) y CI (`.github/`);
- no asignar nueva autoridad a ninguna ruta.

---

## 5. Audit 2

La solución depurada se contrasta contra los límites de autoridad.

### Autoridad funcional

PASS — el mapa no redefine parámetros, reglas, evidencia, motor, negociación, CRC, Assurance ni decisión humana.

### Matriz de Autoridad

PASS — mantiene expresamente que la autoridad se resuelve mediante `Matriz_Autoridad_Documental.md` y fuentes especializadas.

### Master Project Map

PASS — conserva su frontera: Framework Map responde “dónde está”; Master Project Map responde “cómo se organiza”.

### Baselines

PASS — BL-002 se incorpora únicamente como nodo de continuidad, no como autoridad funcional.

### `03_App/`

PASS — se representa como documentación de interfaz/aplicación sin elevarla sobre arquitectura o fuentes especializadas.

### Ejecutables y CI

PASS — `eios/`, `tests/` y `.github/` se identifican como materialización/verificación técnica, no como fuentes de autoridad empresarial.

### No regresión

PASS — se eliminan listados incompletos, no documentos ni referencias críticas.

**DICTAMEN AUDIT 2:** SUPERADA — 0 bloqueadores.

---

## 6. Cierre

Se autoriza exclusivamente:

- actualizar `03_Arquitectura/Framework_Map.md` a v3.3;
- sustituir inventarios exhaustivos obsoletos por anclas estables + regla de inventario físico;
- incorporar nodos omitidos demostrados.

No se autoriza:

- modificar lógica empresarial;
- cambiar autoridad documental;
- alterar rutas físicas;
- renombrar carpetas;
- reabrir componentes cerrados;
- modificar código, tests, SQL o CI.

---

## 7. Gate

Tras materializar v3.3 deberá cumplirse:

```text
DISEÑAR      ✅
AUDITAR      ✅
DEPURAR      ✅
AUDITAR 2    ✅
CERRAR       ✅
MATERIALIZAR ⏳
CI           ⏳
```

La reconciliación solo quedará cerrada tras CI del HEAD exacto, reconciliación pre-merge, merge protegido y CI postintegración.
