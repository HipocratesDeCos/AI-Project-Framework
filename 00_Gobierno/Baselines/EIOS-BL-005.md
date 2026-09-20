# EIOS-BL-005 — Baseline de continuidad post-PROJECTION_ONLY QTG synthetic chain

**Estado:** 🔒 CERRADO TÉCNICAMENTE — INTEGRACIÓN CONDICIONADA A CI  
**Fecha:** 2026-09-20  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA de referencia:** `cd0504b9540d37c6523957dccd8cc51acad1b729`  
**Baseline anterior:** `EIOS-BL-004 @ d3c462a2536ee20204b9d5c9dce1024e1ca7d31c`

---

## 1. Objeto

Establecer un nuevo punto formal de recuperación después del avance acumulado desde BL-004, preservando con precisión qué cadenas han quedado físicamente cerradas y qué fronteras continúan bloqueadas.

BL-005 registra especialmente:

- cierre de provenance adicional en Finance/Rules y otras fronteras seleccionadas;
- materialización de `DIP-AGG-01` como agregado seleccionado inmutable;
- construcción de la cadena documental/financiera necesaria para `PROJECTION_ONLY`;
- manifiesto, material envelope, productor y consumidor QTG especializados;
- definición separada de modos `SYNTHETIC_TEST` y `OPERATIONAL`;
- contrato de admisión del primer expediente operacional, sin fabricar dicho expediente;
- Mock Dataset estructural y adapter semántico sintético S1–S7;
- fixture semántica física de trece componentes;
- ensayo E2E sintético hasta `ProjectionQualityConsumption`;
- preservación explícita del bloqueo operacional QTG↔O1.

Este Baseline registra estado demostrado. No crea autoridad funcional ni convierte Mock Data en material operacional.

## 2. Magnitud física desde BL-004

Comparación:

```text
d3c462a2536ee20204b9d5c9dce1024e1ca7d31c
→
cd0504b9540d37c6523957dccd8cc51acad1b729
```

Resultado verificado:

- `ahead_by = 270`;
- `behind_by = 0`;
- 214 rutas aparecen en el delta físico agregado.

La magnitud incluye el propio lifecycle posterior de BL-004 y todas las unidades integradas hasta PR #217.

## 3. Estado relevante incorporado

### 3.1 Decision Input Package

`DIP-AGG-01` está físicamente materializado mediante `DecisionInputPackage`.

La garantía demostrada es de agregación seleccionada, revalidación, congelación e identidad de contenido.

Continúan fuera de su garantía:

- autenticación/origen ERP;
- lectura multi-parámetro atómica;
- transformación de fingerprint en prueba de origen;
- adjudicación implícita de criticidad o aplicabilidad QTG.

### 3.2 PROJECTION_ONLY — material de calidad

Quedan físicamente cerradas, en sus contratos especializados:

- cobertura documental de pagos/cuotas;
- `FinanceQualityPreparation`;
- manifiesto de seis funciones `ProjectionCriteriaManifest v0.2`;
- cadena documental/contextual de tesorería;
- mandato y revisión personal de tesorería;
- inventario ampliado de flujos;
- mandato y revisión personal del inventario;
- hallazgo individual por cada cuota requerida;
- `ProjectionMaterialEnvelope` agregado y recomputable.

La presencia de material completo no prejuzga el resultado de calidad.

### 3.3 QTG PROJECTION_ONLY — productor y consumidor aislados

Existe un productor determinista especializado que:

- consume exclusivamente un `ProjectionMaterialEnvelope`;
- recompone fingerprints, pertenencias y naturalezas;
- genera el inventario completo de controles;
- ejecuta el Quality Gate una vez;
- produce un `ProjectionQualityReceipt` recomputable.

Existe además un consumidor especializado que:

- revalida el receipt contra envelope y modo exactos;
- conserva el receipt completo;
- separa `technical_status=VALIDATED` del resultado funcional;
- mantiene `decision_authority=false`.

Emparejamientos cerrados:

```text
SYNTHETIC_TEST ↔ TEST_ONLY
OPERATIONAL    ↔ OPERATIONAL
```

La existencia contractual del segundo emparejamiento no acredita que exista material operacional disponible.

### 3.4 Cadena sintética física S1–S7

El Mock Dataset sintético dispone de:

- loader estructural fail-closed;
- fixture estructural deliberadamente semánticamente incompleta;
- fixture semántica física separada;
- 13 componentes ligados por SHA-256;
- adapter privado S1–S6;
- bundle público atómico S7:
  `ProjectionOnlySyntheticMaterialBundle`.

S7 conserva objetos canónicos, dataset fingerprint, envelope fingerprint y fingerprints/hashes intermedios sin ejecutar Finance Basic ni QTG.

### 3.5 Ensayo sintético QTG E2E

La cadena física demostrada es:

```text
ProjectionMockDataset
→ ProjectionOnlySyntheticMaterialBundle
→ ProjectionMaterialEnvelope
→ ProjectionQualityReceipt(SYNTHETIC_TEST)
→ ProjectionQualityConsumption(TEST_ONLY)
```

El ensayo demuestra dos propiedades distintas:

1. material semánticamente construible puede producir `NO_APTO/BAJA`;
2. una variante Mock Data explícitamente completada puede producir `APTO/ALTA`.

En ambos casos:

- `operational_effect=false`;
- `decision_authority=false`;
- no se ejecuta Finance Basic;
- no existe promoción a operación.

PR #217 validó el head exacto con:

- 1.374 pruebas Python satisfactorias;
- 7 warnings;
- C0 SQL PASS;
- Decision Versioning SQL PASS;
- Parameter Configuration SQL PASS.

### 3.6 Ruta QTG operacional

La ruta operacional permanece bloqueada.

Ya existen:

- contrato de admisión del material `PROJECTION_ONLY / OPERATIONAL`;
- diseño del binding causal QTG↔O1 en dos fases.

Pero no existe un expediente operacional concreto y autorizado que permita ejecutar una prueba positiva sin inventar fuentes, documentos, mandatos, revisores o autenticidad.

Está expresamente prohibido:

- cambiar `SYNTHETIC` por `PRESENTED_OPERATIONAL`;
- fabricar documentos o autoridades;
- completar huecos mediante defaults favorables.

### 3.7 Scenario Stage 2 ↔ Viability Frontier

Permanece la cuarentena pública de Stage 2.

El core Viability Frontier continúa cerrado, pero consume consecuencias H/K/U/S que deben proceder de una autoridad externa identificada. No existe un productor físico provenance-safe que permita derivarlas sin inventar autoridad.

El wrapper público Decision Twin dependiente de esa finalización Stage 2 permanece igualmente en cuarentena. Decision Twin core/comparator no se reabren por ello.

### 3.8 Negotiation Intelligence / Negotiation Ladder

NI y Ladder continúan cerrados como contratos de resultado.

Las fronteras Vertical usan invocadores explícitos en lugar de resultados desprendidos. La presencia de un invocador no prueba por sí sola provenance.

No existe actualmente un productor determinista NI/Ladder autorizado que permita reconstruir su resultado desde la compra completa sin introducir razonamiento o autoridad nuevos.

## 4. Frentes que BL-005 NO declara cerrados

BL-005 no resuelve:

- QTG `OPERATIONAL` ↔ O1 sin expediente operacional autorizado;
- Scenario Stage 2 público sin productor VF provenance-safe;
- wrapper Decision Twin dependiente de Stage 2;
- productor provenance-safe de NI/Ladder;
- Supplier Risk valorativo/scoring;
- Rotation mientras persistan sus gaps de autoridad;
- PAG donde falten carrier/viabilidad contrafactual/semántica de parámetros;
- HIS no materializado más allá de los cierres específicos demostrados;
- DAT sin productores/política física completa;
- PROV Alternatives valorativo;
- COM discounts/rappels sin dependencias/parámetros autorizados;
- Assurance/Shadow Mode sin decisión humana de referencia gobernada;
- Profitability/MGE sin aprobación explícita de política;
- autenticación/identidad, enumeración de empresas y descubrimiento global de parámetros del Configuration Center.

## 5. Autoridad preservada

BL-005 no modifica ni sustituye:

- Project Charter;
- Matriz de Autoridad Documental;
- Salvaguarda Vertical MVP;
- reglas o RDM;
- catálogo/valores de parámetros;
- CRC;
- motores cerrados;
- autoridad humana final.

No convierte CI verde, fingerprints, hashes, referencias o tipos factory-built en autenticación externa que sus contratos no concedan.

## 6. Método

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ✅
CI            ⏳
```

Evidencia:

- `07_Pruebas/EIOS_BL_005_Audit_1.md`;
- `07_Pruebas/EIOS_BL_005_Depuration.md`;
- `07_Pruebas/EIOS_BL_005_Audit_2.md`.

## 7. Dictamen

El SHA formal de recuperación queda fijado en:

```text
main @ cd0504b9540d37c6523957dccd8cc51acad1b729
```

Ese SHA incorpora la integración de PR #217 y representa el estado ejecutable inmediatamente anterior a la materialización documental de BL-005.

BL-005 será considerado integrado únicamente después de CI exact-head, reconciliación de `main`, merge protegido y comprobación postintegración disponible.

**DICTAMEN:** BL-005 queda cerrado técnicamente como baseline de continuidad, sujeto al gate de CI de su propia materialización documental.
