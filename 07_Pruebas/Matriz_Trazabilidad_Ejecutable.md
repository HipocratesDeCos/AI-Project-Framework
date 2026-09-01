# MATRIZ DE TRAZABILIDAD EJECUTABLE

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Diseño documental materializado  
**Dominio:** `07_Pruebas`  
**Naturaleza:** Matriz de trazabilidad ejecutable  

---

## 1. Propósito

Esta matriz establece la relación de trazabilidad entre una fuente documental ya autorizada, un requisito verificable, el caso de prueba correspondiente y, cuando exista, el artefacto físico sobre el que se realiza la comprobación.

Su función es exclusivamente de trazabilidad y verificación.

No constituye una nueva autoridad documental, no crea requisitos, no crea capacidades y no modifica la arquitectura, C0, reglas, parámetros ni el Plan de Pruebas.

La relación canónica es:

```text
Fuente autorizada
        ↓
Requisito verificable
        ↓
Test_ID
        ↓
Artefacto físico probado
        ↓
Resultado / evidencia
```

---

## 2. Perímetro

El perímetro ejecutable se limita a las capacidades físicas ya disponibles y verificables:

- Input / validación;
- `DecisionContext`;
- Evidence;
- Assessment;
- trazabilidad C0;
- reproducibilidad C0;
- integración C0;
- regresión del baseline C0.

Los casos dependientes de capacidades todavía no materializadas permanecen fuera del perímetro ejecutable.

Quedan fuera, entre otros:

- parametrización avanzada;
- motor completo de reglas;
- CRC;
- motor decisional superior;
- explicabilidad decisional superior;
- reconstrucción decisional completa;
- trazabilidad completa del Vertical;
- SQL físico;
- no-regresión del Vertical completo.

---

## 3. Campos y salvaguardas

### 3.1 `Requirement_ID`

Identificador interno de trazabilidad de esta matriz.

No constituye un requisito normativo nuevo ni puede adquirir autoridad propia.

### 3.2 `Fuente autorizada`

Referencia al documento o artefacto documental que ya posee autoridad sobre el concepto que debe verificarse.

La matriz no concede, modifica, sustituye ni resuelve la autoridad de dicha fuente.

### 3.3 `Artefacto físico probado`

Componente físico existente sobre el que se realiza la comprobación, cuando exista.

La existencia de un artefacto físico no le confiere autoridad documental.

### 3.4 `Test_ID`

Identificador oficial del Plan de Pruebas para el caso correspondiente cuando este exista.

La matriz no crea una taxonomía paralela de pruebas ni nuevos casos de prueba. Si no existe todavía un `Test_ID` oficial para una relación trazada, la matriz no lo inventa; la relación permanece sin caso oficial asignado hasta que el Plan de Pruebas lo establezca.

### 3.5 `Dependencia`

Referencia exclusivamente a una dependencia previamente establecida por una autoridad existente.

No puede crear requisitos, capacidades, componentes, relaciones arquitectónicas ni nuevas dependencias normativas.

### 3.6 `Estado`

El estado del caso de prueba es el estado oficial definido por el Plan de Pruebas:

- `PENDIENTE`;
- `APROBADA`;
- `FALLIDA`;
- `BLOQUEADA`;
- `NO APLICA`.

### 3.7 `Condición de ejecución`

Clasificación auxiliar de disponibilidad técnica:

- `EXECUTABLE`;
- `DEPENDENCY_PENDING`.

Esta clasificación nunca sustituye ni modifica el estado oficial del caso.

---

## 4. Salvaguardas semánticas

### 4.1 `Decision_ID`

`Decision_ID` identifica la unidad decisional EIOS dentro del contrato correspondiente.

No identifica al CEO, al aprobador, al decisor humano ni el acto empresarial final.

La matriz solo puede verificar su conservación o coherencia dentro del perímetro C0 que realmente lo materialice.

### 4.2 `Assessment`

`Assessment` representa evaluación.

No equivale a:

```text
Assessment ≠ Recommendation ≠ Human Decision
```

Una prueba sobre `Assessment` no puede interpretarse como prueba de una recomendación empresarial ni de una decisión humana.

### 4.3 `Trace`

La trazabilidad comprobada por esta matriz es trazabilidad de ejecución C0.

Una prueba de reproducibilidad de C0 no permite afirmar por sí sola que una decisión empresarial completa haya sido reconstruida.

---

## 5. Matriz

| Requirement_ID | Fuente autorizada | Requisito verificable | Test_ID | Artefacto físico probado | Dependencia | Estado | Condición de ejecución |
|---|---|---|---|---|---|---|---|
| REQ-C0-001 | Contrato C0 / documentación autorizada aplicable | `decision_id` válido y presente donde el contrato C0 lo exige | — | `PurchaseOperation` / artefacto C0 correspondiente | — | APROBADA | EXECUTABLE |
| REQ-C0-002 | `05_Motor/Decision_Versioning.md` | La identidad de la unidad decisional EIOS se conserva coherentemente durante la ejecución C0 | — | `DecisionContext` / artefacto C0 correspondiente | — | APROBADA | EXECUTABLE |
| REQ-C0-003 | `04_Reglas/Evidence_Contract.md` | `DEMONSTRATED` requiere referencia de demostración | — | `Evidence` | — | APROBADA | EXECUTABLE |
| REQ-C0-004 | `04_Reglas/Evidence_Contract.md` | `GAP` no habilita resultado `TRUE/FALSE` | — | `Evidence` / `Assessment` | — | APROBADA | EXECUTABLE |
| REQ-C0-005 | `04_Reglas/Evidence_Contract.md` | Ausencia de evidencia no equivale a `FALSE` | — | C0 / artefacto correspondiente | — | APROBADA | EXECUTABLE |
| REQ-C0-006 | Contrato de `Assessment` autorizado | `NOT_EVALUABLE` no produce `outcome` decisional | — | `Assessment` | — | APROBADA | EXECUTABLE |
| REQ-C0-007 | Contrato de `Assessment` autorizado | `EVALUABLE` produce un `outcome` conforme al contrato | — | `Assessment` | — | APROBADA | EXECUTABLE |
| REQ-C0-008 | Contrato C0 / documentación de trazabilidad autorizada | El contexto de ejecución C0 se conserva en `Trace` | — | `Trace` | — | APROBADA | EXECUTABLE |
| REQ-C0-009 | Contrato C0 / documentación de reproducibilidad autorizada | El fingerprint de entrada se conserva | — | `Trace` | — | APROBADA | EXECUTABLE |
| REQ-C0-010 | Contrato C0 / documentación de reproducibilidad autorizada | La ejecución C0 es reproducible conforme al contrato físico disponible | — | C0 / `Trace` | — | APROBADA | EXECUTABLE |

**Criterio de cierre de esta matriz:** los diez requisitos anteriores están cubiertos por comprobaciones físicas existentes en `tests/test_c0.py`. La matriz no asigna `Test_ID` cuando el Plan de Pruebas no proporciona un identificador oficial inequívoco para esa relación; por ello se conserva `—` y no se crea una taxonomía paralela.

---

## 6. Regla de interpretación

La matriz debe interpretarse siempre subordinada a las autoridades existentes.

En particular:

```text
Matriz de trazabilidad
        ≠ autoridad funcional
        ≠ autoridad de versionado
        ≠ autoridad de reconstrucción decisional
        ≠ autoridad arquitectónica
        ≠ autoridad de reglas
        ≠ autoridad de parámetros
```

La matriz registra relaciones verificables; no las crea.

---

## 7. Regla de dependencia

Una dependencia solo puede registrarse cuando ya exista en una fuente autorizada.

Si una dependencia no está establecida por una autoridad existente, la matriz no puede inferirla ni convertirla en requisito.

```text
Autoridad existente
        ↓
dependencia ya establecida
        ↓
matriz de trazabilidad
```

Nunca:

```text
matriz
  ↓
Dependencia nueva
  ↓
requisito / arquitectura nueva
```
