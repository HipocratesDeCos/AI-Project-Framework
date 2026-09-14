# EIOS-BL-004 — Baseline de continuidad post-QTG/Stage2 quarantine

**Estado:** 🔒 CERRADO — MATERIALIZADO — PENDIENTE CI DEL ARTEFACTO  
**Fecha:** 2026-09-14  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA de referencia:** `d3c462a2536ee20204b9d5c9dce1024e1ca7d31c`  
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

El título se refiere únicamente a estas cuarentenas concretas. BL-004 no pretende certificar ni reconciliar globalmente todas las fronteras provenance de EIOS.

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

**Precisión de navegación:** en el SHA de referencia, `Project_Context.md` v2.3 sigue señalando correctamente BL-003 como punto formal de recuperación más reciente porque BL-004 aún no estaba integrado. Tras la eventual integración del artefacto BL-004, esa referencia quedará desfasada y deberá reconciliarse en una unidad documental posterior, separada y auditable. BL-004 no reescribe `Project_Context.md` dentro de su propia unidad.

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

### 3.5 Wrapper público Decision Twin dependiente de Stage 2

El wrapper público `eios.rules.decision_twin_integration` queda en cuarentena por depender de la frontera Stage 2 bloqueada.

Se preservan sin reapertura:

- Decision Twin core;
- `decision_twin_engine`;
- el comparador descriptivo;
- ausencia de winner, ranking o selección automática.

La cuarentena se limita al wrapper público dependiente. No debe describirse como bloqueo o defecto general de Decision Twin ni como reapertura de su core cerrado.

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

El SHA de referencia de BL-004 corresponde al `main` resultante de PR #144:

```text
d3c462a2536ee20204b9d5c9dce1024e1ca7d31c
```

PR #144 quedó validado por CI pre-merge #796 y CI post-merge #797, ambas en SUCCESS; #797 validó el SHA exacto de referencia de BL-004.

## 5. Capacidades que BL-004 NO declara cerradas

BL-004 no resuelve por inferencia:

- QTG mientras falte un `Decision Input Package` físico, agregado y trazable;
- Scenario Stage 2 público mientras falte un productor VF provenance-safe;
- el wrapper público Decision Twin dependiente mientras dependa de Stage 2 bloqueado;
- Supplier Risk valorativo mientras falten autoridad y política cuantitativa;
- Rotation mientras falten autoridad especializada, dependencias, fórmula o umbral autorizados;
- Assurance / Shadow Mode sin fuente autorizada de decisión humana de referencia y su gobierno;
- Profitability / MGE donde falte autoridad cuantitativa especializada;
- autenticación/resolución confiable de identidad del Configuration Center;
- enumeración de empresas autorizadas;
- descubrimiento/listado global de parámetros sin productor autorizado.

## 6. Precisión sobre Rotation

El estado auditado materializa datos y cálculos de Stock, incluida cobertura (`coverage_days`) y demanda diaria. Esa existencia no autoriza a reinterpretar cobertura como “Rotation” ni a crear un KPI de rotación por inferencia.

No se ha identificado en el estado auditado una autoridad especializada posterior a BL-003 que cierre los gaps ya preservados de Rotation. Mientras falten definición normativa, fórmula, periodo, dependencias y, cuando aplique, umbral autorizados, Rotation continúa bloqueado.

Esta conclusión no convierte una búsqueda textual en autoridad; deriva de la combinación entre los bloqueos expresos de BL-003 y la ausencia de una autoridad posterior identificada que los cierre.

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
- no sustituye contratos especializados;
- no corrige silenciosamente documentos de navegación cuya reconciliación corresponda a una unidad posterior.

La decisión empresarial final permanece humana.

## 9. Método de establecimiento

```text
DISEÑAR       ✅
AUDITAR       ✅ — `07_Pruebas/EIOS_BL_004_Audit_1.md` — 4 precisiones, 0 bloqueos
DEPURAR       ✅ — incorporadas A1–A4
AUDITAR 2     ✅ — `07_Pruebas/EIOS_BL_004_Audit_2.md` — 0 bloqueadores
CERRAR        ✅
MATERIALIZAR  ✅ — `00_Gobierno/Baselines/EIOS-BL-004.md`
CI            ⏳ — artefacto BL-004 todavía no integrado
```

## 10. Dictamen de cierre

Audit 2 confirmó que:

1. `d3c462a2536ee20204b9d5c9dce1024e1ca7d31c` está realmente en `main` y validado por CI postintegración #797 SUCCESS;
2. el delta desde el SHA histórico de BL-003 es físicamente `ahead=92`, `behind=0`;
3. QTG, Scenario Stage 2 público y el wrapper público Decision Twin dependiente se representan como cuarentenas/bloqueos y no como capacidades positivas cerradas;
4. los cores preservados no se presentan como reabiertos;
5. todos los bloqueos transversales relevantes permanecen visibles;
6. la futura divergencia de navegación de `Project_Context.md` queda explícita y fuera del alcance de esta unidad;
7. no se introduce autoridad funcional nueva.

**DICTAMEN:** BL-004 queda cerrado y materializado como nuevo punto formal de recuperación, condicionado exclusivamente a los gates de integración de su propio artefacto.

## 11. Validez e integración

El punto formal de recuperación que BL-004 fija permanece:

```text
main @ d3c462a2536ee20204b9d5c9dce1024e1ca7d31c
```

La integración posterior del artefacto BL-004 no modificará retroactivamente este SHA de referencia.

Restan obligatoriamente para integrar el artefacto:

1. CI pre-merge SUCCESS sobre el HEAD exacto de `docs/eios-bl-004`;
2. reconciliación final con `main` y `behind=0`;
3. merge protegido por SHA exacto;
4. CI postintegración SUCCESS sobre el SHA exacto resultante en `main`.

Hasta completar esos gates, el contenido de BL-004 está cerrado/materializado en rama, pero su artefacto todavía no forma parte de `main`.
