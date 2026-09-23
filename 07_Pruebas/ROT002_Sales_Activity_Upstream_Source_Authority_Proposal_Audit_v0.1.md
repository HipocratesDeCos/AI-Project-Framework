# EIOS — ROT002 Sales Activity Upstream Source Authority Proposal Audit v0.1

**Baseline:** `main @ 9caccbdb02459a72d08eaa8b49df3c406fa793ff`  
**Fecha:** 23/09/2026  
**Estado:** AUDIT 2 DE PROPUESTA — APTA PARA AUTORIDAD HUMANA  
**Objeto:** `ROT002_Sales_Activity_Upstream_Source_Authority_Proposal_v0.1.md`

## 1. Coherencia con Rotation Track A

La propuesta conserva los invariantes cerrados:

- ausencia de filas != cero ventas;
- GAP != cero ventas;
- net quantity = 0 != ausencia;
- ventana parcial != completa;
- fuente con semántica identificable;
- ROT no redefine devoluciones/anulaciones/abonos;
- ventas != consumo/demanda;
- Track A no produce Assessment.

**Resultado:** CONFORME.

## 2. Coherencia con SalesActivityWindowEvidence

La propuesta utiliza los campos ya autorizados:

```text
source_ref
source_semantics_ref
completeness_ref
evidence_refs
trace_refs
```

y no modifica:

```text
activity_state
article_id
evaluation_date
window_start
window_end
window_authority_ref
```

**Resultado:** CONFORME.

## 3. Separación de autoridad

Se evita promover una referencia técnica a autoridad:

```text
source_ref != source semantics
source_ref != completeness
```

Esto preserva provenance-safe y evita inferencia desde nombres de sistemas.

**Resultado:** CONFORME.

## 4. Presencia frente a ausencia

La propuesta distingue:

```text
presencia → prueba positiva de al menos un evento válido
ausencia → prueba de cobertura completa + ausencia demostrada
```

La asimetría es coherente con la metodología ROT ya cerrada.

**Resultado:** CONFORME.

## 5. Carrier upstream

`SalesActivitySourceEvidence` se limita a soporte factual y no invade Rules/CRC.

No contiene:

- TRUE/FALSE de regla;
- Assessment;
- NO COMPRAR;
- excepción;
- score/ranking.

**Resultado:** CONFORME COMO PROPUESTA.

## 6. coverage_state

La taxonomía propuesta:

```text
COMPLETE
PARTIAL
NOT_DEMONSTRATED
CONFLICTING
```

no sustituye `Evidence.state` ni `EvidenceValidation.status`.

Solo representa cobertura de la ventana upstream.

**Resultado:** CONFORME COMO PROPUESTA — REQUIERE AUTORIDAD HUMANA.

## 7. Semántica empresarial concreta

La propuesta no determina qué documento comercial constituye venta.

Mantiene explícitamente abiertos:

- factura;
- pedido;
- albarán;
- ticket;
- devolución;
- abono;
- anulación;
- reconocimiento temporal.

**Resultado:** CONFORME — no inventa política empresarial.

## 8. R-ROT-002

No se implementa ni redefine:

```text
No existen ventas durante el periodo configurado.
→ NO COMPRAR salvo excepción.
```

La propuesta se limita a la producción factual previa.

**Resultado:** CONFORME.

## 9. Dictamen

```text
DISEÑAR PROPUESTA  ✅
AUDITAR            ✅
DEPURAR            ✅
AUDITAR 2          ✅
PUBLICABLE         ✅
AUTORIZADA         ⏳ NO
MATERIALIZAR       ⛔ NO
```

**0 bloqueadores para someter la propuesta a autoridad humana.**

No debe escribirse código de `SalesActivitySourceEvidence` hasta autorización expresa.
