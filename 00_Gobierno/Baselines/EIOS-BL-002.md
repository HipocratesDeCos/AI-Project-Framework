# EIOS-BL-002 — Baseline de continuidad post-8.5

**Estado:** ESTABLECIDO E INTEGRADO — CI PRE/POST SUCCESS  
**Fecha:** 2026-09-13  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA de referencia:** `1ada9415d0ef885f55419e4775c5976d3e75d08e`  
**Baseline anterior:** `EIOS-BL-001 @ 59daf6d2fbb70e9aebde98190f04a86a59cd3b14`  
**Reconciliación postintegración:** `EIOS-CHG-002`

---

## 1. Objeto

Establecer un punto formal de continuidad tras el avance acumulado posterior a `EIOS-BL-001`, sin declarar finalizado el Vertical MVP ni convertir este documento en una nueva fuente de autoridad funcional.

Este Baseline registra un estado ya materializado y validado del repositorio. La autoridad sobre cada dominio permanece en los documentos especializados definidos por `00_Gobierno/Matriz_Autoridad_Documental.md`.

La actualización `EIOS-CHG-002` no modifica el contenido ni el SHA de referencia del Baseline: reconcilia exclusivamente el estado de integración del propio artefacto después de haberse completado los gates que figuraban como pendientes en su materialización inicial.

---

## 2. Magnitud del delta desde BL-001

La comparación física:

```text
59daf6d2fbb70e9aebde98190f04a86a59cd3b14
→
1ada9415d0ef885f55419e4775c5976d3e75d08e
```

demuestra:

- `ahead_by = 1010` commits;
- `behind_by = 0`;
- ampliación sustancial de metodología, contratos, implementación, pruebas, UI, provenance y reconciliaciones;
- mantenimiento de la rama `main` como línea de integración vigente.

El volumen del cambio justifica un nuevo punto formal de recuperación del proyecto.

---

## 3. Capacidades y fronteras cerradas relevantes

Sin sustituir a sus cierres especializados, el SHA de referencia contiene materializadas y reconciliadas, entre otras, las siguientes unidades:

- C0 / motor de reglas en su alcance cerrado;
- Assessment y fronteras de provenance asociadas;
- Price Intelligence;
- TCO Core;
- Stock / STK ejecutable en su alcance autorizado;
- Delivery Stockout Analyzer;
- Finance Basic;
- Supplier Evidence Core;
- Viability Frontier;
- Scenario Engine y coordinación de escenarios en sus fronteras cerradas;
- Decision Twin y comparación;
- Negotiation Intelligence;
- Negotiation Ladder;
- CRC-MVP;
- Decision Versioning;
- E2E Execution Boundary;
- UI / Visual Frontend U1.1 en su alcance exclusivamente representacional.

La inclusión de una unidad en esta lista significa únicamente que existe evidencia especializada de cierre/materialización dentro del estado referenciado; no amplía su semántica ni su autoridad.

---

## 4. Reconciliaciones posteriores relevantes

El estado de referencia incorpora, entre otras, reconciliaciones de continuidad y gobierno para:

- provenance-safe invocation de TCO;
- cuarentena de resultados opacos en Negotiation Intelligence / Negotiation Ladder;
- cuarentena de Scenario Coordination;
- migración documental `GAP-ID-01` a identificadores canónicos `P-*` / `R-*`;
- estado post-F3 del Decision Log;
- R-ENT-001 Assessment Bridge;
- R-ENT-001 Vertical Integration, registrando el scope breach histórico de PR #78 y su adopción posterior auditada por Rules Engine Provenance Boundary Migration;
- U1.1 Visual Frontend postintegración.

Estas reconciliaciones no reabren los componentes cerrados ni legitiman retroactivamente cambios que hubieran excedido su autoridad original.

---

## 5. Gates CI recientes de continuidad

El tramo final previo a este Baseline fue verificado mediante CI sobre los SHAs exactos correspondientes. Entre los gates más recientes:

- CI #732 — SUCCESS — Assessment Bridge postintegración;
- CI #734 — SUCCESS — R-ENT-001 Vertical Integration governance reconciliation postintegración;
- CI #736 — SUCCESS — U1.1 Visual Frontend postintegración.

El SHA de referencia de BL-002 es precisamente el `main` validado por CI #736:

```text
1ada9415d0ef885f55419e4775c5976d3e75d08e
```

### Gate del artefacto BL-002

La materialización del propio Baseline completó posteriormente sus gates de integración:

- PR #125 — `docs(governance): establish EIOS-BL-002 continuity baseline`;
- HEAD de PR: `2996c1b90fcd26bb676f07b2069b6d7aec93ee1d`;
- CI #737 — SUCCESS sobre el HEAD exacto de la PR;
- merge protegido de PR #125 → `87d357fc487c450df796c51a303122bcb8d93700`;
- CI #738 — SUCCESS postintegración sobre ese SHA exacto de `main`.

Estos gates cierran la integración del artefacto documental; **no cambian el SHA de referencia del Baseline**, que continúa siendo `1ada9415...`.

---

## 6. Frentes expresamente NO cerrados por este Baseline

BL-002 no elimina ni resuelve por inferencia los siguientes bloqueos:

### Quality & Trust Gate

Permanece sin demostrarse un productor físico de `Decision Input Package` agregado, trazable y autorizado que permita declarar cerrada una frontera provenance-safe completa para QTG.

### Supplier Risk valorativo

`Supplier Evidence Core` está cerrado como núcleo factual, pero no autoriza métricas, scoring, ranking, umbrales ni política decisional de Supplier Risk. Los gaps de valoración y reglas continúan separados de la evidencia factual.

### Rotation

`Rotation Track A` permanece cerrado únicamente en metodología factual y declara explícitamente que no autoriza contrato técnico mientras falten:

- `ROT-G01` — autoridad del periodo configurado;
- `ROT-G04-A` — dependencias canónicas de `R-ROT-002`.

Track B permanece bloqueado adicionalmente por fórmula, umbral y dependencias de `R-ROT-001`.

### Assurance / Shadow Mode

La Salvaguarda define Assurance de forma transversal, pero no existe una fuente especializada única que autorice inventar A03–A10. En particular, Shadow Mode / piloto no puede materializarse como comparación decisional real sin una fuente autorizada de decisión humana de referencia y su correspondiente gobierno.

---

## 7. Límites del Baseline

Este Baseline:

- no declara terminado el MVP;
- no autoriza una orden de compra automática;
- no crea un decisor artificial;
- no crea parámetros, umbrales o políticas empresariales;
- no modifica reglas de negocio;
- no sustituye contratos, cierres ni matrices especializadas;
- no transforma evidencia factual en valoración de riesgo;
- no habilita componentes expresamente bloqueados por falta de autoridad.

La decisión empresarial final permanece en la frontera humana definida por la Salvaguarda y la arquitectura vigente.

---

## 8. Ciclo de establecimiento

### DISEÑAR — ✅

Definido como Baseline de continuidad y recuperación, no como cambio funcional.

### AUDITAR — ✅

Contrastados:

- `EIOS-BL-001`;
- `Project_Governance.md` y sus reglas de Baseline;
- `Matriz_Autoridad_Documental.md`;
- Salvaguarda Vertical MVP;
- `main @ 1ada9415d0ef885f55419e4775c5976d3e75d08e`;
- delta físico desde BL-001;
- cierres y reconciliaciones recientes;
- bloqueos metodológicos y de autoridad aún vigentes.

### DEPURAR — ✅

Se eliminan del alcance cualquier formulación equivalente a “MVP completo”, “Assurance completo” o “Supplier Risk implementado”. BL-002 se limita al estado demostrado.

### AUDITAR 2 — ✅

No se detecta introducción de nueva lógica empresarial ni contradicción con las fuentes de autoridad. Los bloqueos se conservan explícitamente.

**DICTAMEN:** SUPERADA — 0 bloqueadores documentales.

### CERRAR — ✅

Autorizada exclusivamente la materialización de `EIOS-BL-002.md` como registro de continuidad.

### MATERIALIZAR — ✅

Artefacto:

```text
00_Gobierno/Baselines/EIOS-BL-002.md
```

### CI — ✅

Completado para el artefacto documental:

- CI #737 — SUCCESS en el HEAD exacto de PR #125;
- reconciliación pre-merge compatible;
- merge protegido → `87d357fc487c450df796c51a303122bcb8d93700`;
- CI #738 — SUCCESS postintegración.

---

## 9. Criterio de validez

`EIOS-BL-002` queda asociado permanentemente al estado técnico y documental:

```text
main @ 1ada9415d0ef885f55419e4775c5976d3e75d08e
```

Los gates de establecimiento e integración del artefacto se completaron satisfactoriamente mediante PR #125, CI #737 y CI postintegración #738.

Por tanto:

- el artefacto `EIOS-BL-002.md` está integrado;
- el Baseline está formalmente establecido;
- su SHA de referencia no cambia por esta reconciliación;
- los avances posteriores de `main` no modifican retroactivamente el estado fijado por BL-002;
- para continuidad operativa actual debe consultarse además `00_Gobierno/Project_Context.md` y verificarse el `main` vivo.

---

## 10. Reconciliación postintegración — EIOS-CHG-002

Esta sección documenta exclusivamente el cierre del estado de integración que había quedado pendiente en la versión inicial del artefacto.

**Cambio:** `PENDIENTE DE CI DEL ARTEFACTO` → `ESTABLECIDO E INTEGRADO — CI PRE/POST SUCCESS`.

**Evidencia:** PR #125, CI #737, merge `87d357fc487c450df796c51a303122bcb8d93700`, CI #738.

**Impacto funcional:** ninguno.

**Impacto sobre autoridad:** ninguno.

**Impacto sobre el SHA de referencia:** ninguno.
