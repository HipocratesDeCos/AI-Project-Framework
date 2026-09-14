# EIOS-BL-004 — Baseline de continuidad post-provenance quarantine

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA  
**Fecha:** 2026-09-14  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA candidato de referencia:** `d3c462a2536ee20204b9d5c9dce1024e1ca7d31c`  
**Baseline anterior:** `EIOS-BL-003 @ b10c4cde6c4f52af04de0794493432961b745dca`

---

## 1. Objeto

Establecer un nuevo punto formal de recuperación después del avance acumulado desde el SHA histórico de referencia de EIOS-BL-003, con foco en:

- reconciliación posterior del Configuration Center;
- cierre del selected-context E2E;
- cuarentena provenance-safe de QTG en el Vertical MVP;
- reconciliación de Gobierno a BL-003;
- cuarentena de la finalización pública Scenario Stage 2 dependiente de un `ViabilityResult` desprendido;
- cuarentena del wrapper público Decision Twin dependiente de esa frontera Stage 2.

Este Baseline registra estado ya demostrado. No crea autoridad funcional, no declara finalizado el Vertical MVP y no sustituye contratos ni fuentes especializadas.

## 2. Magnitud del delta desde el SHA de referencia de BL-003

Comparación física:

```text
b10c4cde6c4f52af04de0794493432961b745dca
→
d3c462a2536ee20204b9d5c9dce1024e1ca7d31c
```

Resultado verificado:

- `ahead_by = 92` commits;
- `behind_by = 0`;
- el delta incluye el establecimiento e integración del propio artefacto BL-003 y todo el avance posterior hasta PR #144.

La comparación se realiza contra el SHA histórico que BL-003 fija permanentemente como punto de recuperación. No debe interpretarse como “92 commits después del merge del archivo BL-003”.

## 3. Estado relevante incorporado

### 3.1 Gobierno y navegación post-BL-003

Desde el SHA histórico de BL-003 quedan integrados:

- establecimiento e integración del propio `EIOS-BL-003`;
- reconciliación de `Framework_Map.md` y `Master_Project_Map.md` a BL-003;
- reconciliación del estado documental de Configuration Center;
- reconciliación final de `Project_Context.md` y Manual Maestro a BL-003.

BL-004 no modifica retroactivamente el SHA ni el contenido histórico de BL-003.

### 3.2 Configuration Center — Slice 4 y selected-context E2E

Quedan integrados:

- Slice 4 de frontera de aplicación/presentación JSON-safe;
- conformidad E2E del subconjunto ejecutable selected-context;
- reconciliación del lifecycle documental del Configuration Center.

El alcance demostrado continúa limitado a selected-context. No se declaran materializados autenticación/identidad, enumeración de empresas ni descubrimiento/listado global de parámetros sin productor autorizado.

### 3.3 QTG — cuarentena provenance-safe

La vía provisional `quality_invoker` fue retirada del Vertical MVP porque no existe un `Decision Input Package` físico, agregado y trazable que permita acreditar una integración QTG provenance-safe.

Se preservan:

- QTG como capacidad conceptual/canónica;
- `eios/quality/` dentro de su frontera propia;
- el bloqueo de integración positiva hasta disponer del productor autorizado requerido.

La cuarentena no equivale a cierre funcional positivo de QTG.

### 3.4 Scenario Stage 2 ↔ Viability Frontier

La finalización pública Scenario Stage 2 que aceptaba un `ViabilityResult` desprendido queda en cuarentena porque tipo + identidad + versiones no acreditan el productor ni la autoridad de las consecuencias VF.

Se preservan:

- `eios/core/viability_frontier.py` y su semántica cerrada;
- O4/O2/O3 internos;
- C0 + Trace provenance-safe;
- el bridge VF→Scenario únicamente como helper interno de coherencia contextual.

No existe actualmente una finalización pública Stage 2 provenance-safe.

### 3.5 Decision Twin

El wrapper público `eios.rules.decision_twin_integration` queda en cuarentena por depender de la frontera Stage 2 bloqueada.

Se preservan sin reapertura:

- Decision Twin core;
- `decision_twin_engine`;
- el comparador descriptivo;
- ausencia de winner, ranking o selección automática.

La cuarentena del wrapper no debe describirse como defecto del Decision Twin core.

## 4. Gates relevantes incorporados

Entre los gates posteriores al SHA histórico de BL-003 se incluyen:

- PR #137 — establecimiento BL-003 — CI #765/#766 SUCCESS;
- PR #138 — reconciliación de navegación BL-003;
- PR #139 — Configuration Center Slice 4;
- PR #140 — selected-context E2E;
- PR #141 — reconciliación lifecycle Configuration Center;
- PR #142 — QTG provenance-safe quarantine;
- PR #143 — reconciliación Project Context/Manual a BL-003;
- PR #144 — Scenario Stage 2 VF provenance quarantine.

El SHA candidato de BL-004 corresponde al `main` resultante de PR #144:

```text
d3c462a2536ee20204b9d5c9dce1024e1ca7d31c
```

PR #144 quedó validado por CI pre-merge #796 y CI post-merge #797, ambas en SUCCESS; #797 validó el SHA exacto candidato de BL-004.

## 5. Capacidades que BL-004 NO declara cerradas

BL-004 no resuelve por inferencia:

- QTG mientras falte un `Decision Input Package` físico, agregado y trazable;
- Scenario Stage 2 público mientras falte un productor VF provenance-safe;
- Decision Twin integration mientras dependa de Stage 2 bloqueado;
- Supplier Risk valorativo mientras falten autoridad y política cuantitativa;
- Rotation mientras falten definición normativa, dependencias, fórmula o umbral autorizados;
- Assurance / Shadow Mode sin fuente autorizada de decisión humana de referencia y su gobierno;
- Profitability / MGE donde falte autoridad cuantitativa especializada;
- autenticación/resolución confiable de identidad del Configuration Center;
- enumeración de empresas autorizadas;
- descubrimiento/listado global de parámetros sin productor autorizado.

## 6. Precisión sobre Rotation

El repositorio ya materializa datos y cálculos de Stock, incluida cobertura (`coverage_days`) y demanda diaria. Esa existencia no autoriza a reinterpretar cobertura como “Rotation” ni a crear un KPI de rotación por inferencia.

Mientras no exista autoridad especializada que defina semántica, fórmula, periodo, dependencias y, cuando aplique, umbral, Rotation continúa bloqueado.

## 7. Autoridad preservada

BL-004 no modifica:

- Matriz de Autoridad Documental;
- Project Charter;
- Salvaguarda del Vertical MVP;
- reglas ni Rule Dependency Matrix;
- parámetros, valores o unidades;
- CRC;
- PRICE;
- TCO;
- C0 provenance;
- VF core;
- O4/O2/O3 internos;
- Decision Twin core;
- NI / Ladder;
- autoridad humana final.

Un Baseline registra un estado demostrado; no crea la autoridad que ese estado no contiene.

## 8. Límites

Este Baseline:

- no declara terminado el MVP;
- no convierte una cuarentena en cierre funcional positivo;
- no inventa productores provenance-safe ausentes;
- no crea fórmulas, umbrales, reglas o parámetros;
- no reabre componentes core cerrados;
- no convierte evidencia en valoración;
- no autoriza un decisor automático;
- no sustituye contratos especializados.

La decisión empresarial final permanece humana.

## 9. Método de establecimiento

```text
DISEÑAR       ✅ — este artefacto inicial
AUDITAR       ⏳
DEPURAR       ⏳
AUDITAR 2     ⏳
CERRAR        ⏳
MATERIALIZAR  ⏳
CI            ⏳
```

## 10. Condición de cierre

BL-004 solo podrá cerrarse si Audit 1 y Audit 2 confirman que:

1. el SHA candidato está realmente en `main` y validado por CI postintegración;
2. el delta desde BL-003 está descrito sin alterar su historia;
3. QTG y Stage 2/Decision Twin integration se presentan como cuarentenas/bloqueos, no como capacidades positivas cerradas;
4. los cores preservados no se presentan como reabiertos;
5. todos los bloqueos transversales relevantes permanecen visibles;
6. no se introduce autoridad funcional nueva.

La integración del propio artefacto BL-004 requerirá además CI pre-merge sobre HEAD exacto, reconciliación `behind=0`, merge protegido por SHA exacto y CI postintegración sobre el SHA integrado.
