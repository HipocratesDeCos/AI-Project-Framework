# EIOS-BL-006 — Baseline de continuidad post-Provenance Quarantine + Visual Read-Only

**Estado:** 🔒 CERRADO TÉCNICAMENTE — INTEGRACIÓN CONDICIONADA A CI  
**Fecha:** 2026-09-20  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA de referencia:** `d8291cd72c3b96b42add4cabd74ee5ba2eb4c763`  
**Baseline anterior:** `EIOS-BL-005 @ cd0504b9540d37c6523957dccd8cc51acad1b729`

---

## 1. Objeto

Establecer un nuevo punto formal de recuperación después del avance acumulado desde BL-005, sin ampliar autoridad funcional.

BL-006 registra especialmente:

- materialización de la matriz ejecutable de no-regresión de cuarentenas de provenance;
- reauditoría `PAG-READINESS-02`, corrigiendo el diagnóstico del carrier factual de condiciones de pago;
- cierre de U1.2 como composición visual read-only del Vertical MVP;
- conformidad E2E de la cadena visual pública;
- cierre de U1.3 como artefacto HTML inmutable y verificable por `content_sha256`;
- preservación explícita de todos los bloqueos de autoridad/evidencia que siguen abiertos.

Este Baseline resume estado demostrado; no sustituye contratos especializados ni habilita rutas bloqueadas.

## 2. Magnitud física desde BL-005

Comparación:

```text
cd0504b9540d37c6523957dccd8cc51acad1b729
→
d8291cd72c3b96b42add4cabd74ee5ba2eb4c763
```

Resultado verificado:

- `ahead_by = 38`;
- `behind_by = 0`;
- 25 rutas aparecen en el delta físico agregado.

La magnitud incluye la propia materialización/reconciliación de BL-005 y las unidades integradas posteriormente hasta PR #223.

## 3. Estado relevante incorporado

### 3.1 Provenance Quarantine Regression

Existe una matriz ejecutable de no-regresión que protege:

- QTG fuera de la frontera genérica O1/Vertical;
- ausencia de aliases de resultados desprendidos PRICE/TCO/QTG/Twin/Scenario/NI/Ladder;
- Stage 2 público sin exports mientras Viability Frontier provenance siga bloqueado;
- wrapper Decision Twin dependiente sin exports;
- etapas sintéticas S1–S6 privadas;
- superficie S7 atómica.

La matriz no declara provenance positiva de invocadores. Protege únicamente fronteras ya cerradas.

### 3.2 Payment / PAG — diagnóstico vigente

`PAG-READINESS-02` corrige la afirmación histórica de que no existía carrier factual de plazo/condición de pago.

Ahora queda demostrado que:

- Supplier Evidence Core puede preservar hechos `PAYMENT_TERM`;
- la cadena documental de pagos/cuotas conserva vencimientos, asociaciones y localizadores.

Sin embargo continúan abiertos:

- binding EVIDENCE/DATA autorizado hacia `R-PAG-001`;
- semántica canónica de “plazo ofrecido en días”;
- normalización de estructuras multicuota;
- transformación exacta de `P-PAG-003`;
- contradicción de `P-PAG-005` entre control booleano y factor económico;
- productor contrafactual autorizado para `R-PAG-002`.

Por tanto, `R-PAG-001/002` siguen bloqueadas.

### 3.3 U1.2 — Vertical MVP Visual Read-Only Composition

U1.2 materializa la cadena:

```text
VerticalMVPSupportResult
→ present_vertical_mvp_result
→ build_vertical_mvp_view_model
→ render_vertical_mvp_readonly
→ HTML read-only
```

El renderer:

- consume únicamente un Mapping de presentación;
- no importa motores ni modelos de dominio;
- no ejecuta Rules, CRC, Scenario, Twin, PRICE, TCO, Finance, QTG, NI o Ladder;
- no usa JavaScript, networking o persistencia;
- escapa contenido dinámico;
- conserva orden y estados;
- distingue ausencia de resultado favorable;
- presenta CRC como soporte, no decisión humana;
- no crea score, ranking, aprobación ni escenario preferido.

PR #221 validó el HEAD exacto con:

- **1.391 pruebas Python satisfactorias**;
- 8 warnings;
- C0 SQL PASS;
- Decision Versioning SQL PASS;
- Parameter Configuration SQL PASS.

### 3.4 U1.2 — conformidad E2E visual

La conformidad E2E demuestra que objetos contractuales reales de presentación atraviesan las tres fronteras públicas hasta HTML sin pérdida semántica.

Se validaron:

- Rules/CRC + Assessment + evidencia + traza;
- Scenario Support con `NOT_EVALUABLE` y `FAILED`;
- ausencia explícita del bloque no suministrado;
- no mutación entre etapas;
- ausencia de superficies decisionales o ranking.

PR #222 validó el HEAD exacto con:

- **1.395 pruebas Python satisfactorias**;
- 8 warnings;
- las tres validaciones SQL en PASS.

### 3.5 U1.3 — Read-Only Visual Artifact

U1.3 materializa un artefacto de transporte inmutable:

```text
view-model autorizado
→ renderer U1.2
→ UTF-8 bytes
→ content_sha256
→ VerticalMVPReadOnlyArtifact
```

El artefacto expone únicamente:

- `media_type`;
- filename fijo no identificador;
- `size_bytes`;
- `content_sha256`;
- bytes exactos del renderer.

`content_sha256` acredita identidad de contenido renderizado. No es `decision_fingerprint`, `input_fingerprint`, Trace, firma, autenticación ni prueba de provenance.

U1.3 no introduce filesystem, red, servidor, almacenamiento o browser automation.

PR #223 validó el HEAD exacto con:

- **1.403 pruebas Python satisfactorias**;
- 8 warnings;
- C0 SQL PASS;
- Decision Versioning SQL PASS;
- Parameter Configuration SQL PASS.

## 4. Fronteras que BL-006 NO declara cerradas

BL-006 no resuelve ni reinterpreta:

- QTG `OPERATIONAL → O1` sin expediente operacional autorizado;
- Scenario Stage 2 público sin productor Viability Frontier provenance-safe;
- wrapper Decision Twin dependiente de Stage 2;
- productor provenance-safe NI/Ladder;
- Supplier Risk valorativo/scoring;
- Rotation mientras persistan `ROT-G01` y `ROT-G04-A`;
- PAG ejecutable mientras persistan sus gaps semánticos y contrafactuales;
- Historical restante más allá de `R-HIS-002`;
- Data Quality sin productores/política física completa;
- Supplier Alternatives valorativo;
- Discounts & Rappels sin dependencias/parámetros autorizados;
- Assurance/Shadow Mode sin decisión humana de referencia gobernada;
- Profitability/MGE sin aprobación explícita;
- autenticación/identidad, enumeración de empresas y descubrimiento global del Configuration Center;
- serving HTTP, persistencia o ejecución del Vertical desde la capa visual.

## 5. Autoridad preservada

BL-006 no modifica:

- Project Charter;
- Matriz de Autoridad Documental;
- Salvaguarda Vertical MVP;
- Matriz de Reglas / RDM;
- Catálogo de Parámetros;
- motores cerrados;
- CRC;
- autoridad humana final.

No convierte hashes, tipos, HTML, CI verde o invocadores explícitos en autoridad que sus contratos no concedan.

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

- `07_Pruebas/EIOS_BL_006_Audit_1.md`;
- `07_Pruebas/EIOS_BL_006_Depuration.md`;
- `07_Pruebas/EIOS_BL_006_Audit_2.md`.

## 7. Dictamen

El SHA formal de recuperación queda fijado en:

```text
main @ d8291cd72c3b96b42add4cabd74ee5ba2eb4c763
```

Ese SHA representa el estado ejecutable inmediatamente anterior a la materialización documental de BL-006.

BL-006 será considerado integrado únicamente tras CI exact-head, reconciliación de `main`, merge protegido y comprobación de equivalencia del árbol integrado.

**DICTAMEN:** BL-006 queda cerrado técnicamente como baseline de continuidad, sujeto al gate de CI de su materialización documental.
