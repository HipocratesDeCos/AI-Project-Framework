# EIOS — PROV Supplier Alternatives Approval & Correction Audit v0.1

**Fecha:** 22/09/2026  
**Estado:** SUPERADA  
**Autoridad:** `01_Modelo/PROV_Supplier_Alternatives_Authority_v0.1.md`

## A1 — Supplier Evidence preservado

Supplier Evidence continúa limitado a hechos y candidaturas evidenciadas.

No se ha promovido ninguna diferencia estructural a preferencia, mejora significativa, ranking o recomendación.

## A2 — TRUE positivo y FALSE exhaustivo

Para ambas reglas:

- TRUE puede demostrarse con una candidatura suficiente;
- FALSE exige cobertura COMPLETE;
- FALSE exige resolver todo el universo aplicable;
- cualquier hueco de determinación impide FALSE.

Esto evita transformar búsqueda incompleta en ausencia demostrada.

## A3 — Independencia de reglas

R-PROV-001 y R-PROV-002 no consumen el Assessment de la otra regla como autoridad.

Cada una conserva una reconstrucción propia y trazable.

## A4 — Comparabilidad y significancia

Se mantienen separadas:

```text
STRUCTURALLY_COMPARABLE
COMPARABLE
SIGNIFICANT_IMPROVEMENT
```

No existe promoción automática entre ellas.

## A5 — Provenance

La autoridad exige identidad estricta por operación, candidato, proveedor, decisión, escenario, snapshot y versión de parámetros.

Un mismatch debe fallar cerrado.

## A6 — Semántica no inventada

No se introducen:

- thresholds;
- scores;
- pesos;
- ranking;
- proveedor ganador;
- recomendación automática;
- inferencia semántica por LLM.

## Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅ semántica autorizada
MATERIALIZAR  ⏳ siguiente unidad
CI            ⏳
```

**0 bloqueadores para materializar el core provenance-safe de R-PROV-001 / R-PROV-002.**
