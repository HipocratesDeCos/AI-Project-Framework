# EIOS — ROT002 Sales Activity Window Physical Implementation Audit v0.1

**Baseline:** `main @ 8380023f8976b8f0fd0f6c59805239d5d1f10d5a`  
**Fecha:** 23/09/2026  
**Estado:** AUDIT 2 — SUPERADA  
**Unidad:** carrier físico Track A + revalidación provenance-safe

## 1. Alcance materializado

Se materializan exclusivamente:

```text
SalesActivityWindowEvidence
validate_sales_activity_window_evidence(...)
```

La implementación no produce el carrier desde registros de ventas; únicamente representa y revalida un carrier factual ya construido contra el aggregate canónico.

## 2. Nomenclatura

El modelo físico utiliza exactamente:

```text
activity_state
```

conforme a `Rotation_Methodological_Design_v0.3.md` y a la reconciliación integrada por PR #311.

No se introduce un alias `state`.

**Resultado:** CONFORME.

## 3. Estados Track A

Estados físicos permitidos:

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No aparecen estados de Assessment ni resultados empresariales.

**Resultado:** CONFORME.

## 4. Raíz provenance-safe

La frontera pública consume:

```text
DecisionInputPackage
+
SalesActivityWindowEvidence
```

No acepta públicamente:

```text
ResolvedConfiguration
period_days
company_id
effective_at
DecisionContext separado
PurchaseOperation separado
```

P-ROT-001 se localiza únicamente dentro de `DecisionInputPackage.configurations`.

**Resultado:** CONFORME.

## 5. P-ROT-001

Se revalidan:

- P-ROT-001 solicitada;
- P-ROT-001 no missing;
- exactamente una resolución;
- company_id;
- parameters_version;
- effective_at;
- intervalo de vigencia;
- unidad canónica `días`;
- entero finito positivo.

No existe fallback.

**Resultado:** CONFORME.

## 6. Evidence binding

Se aplica exclusivamente la autoridad:

```text
Evidence.source_ref
==
ResolvedConfiguration(P-ROT-001).configuration_ref
```

y se exige:

```text
Evidence.state == DEMONSTRATED
Evidence.demonstration_ref != None
```

No se inventa un `source_type` obligatorio ni igualdad `captured_at == effective_at`.

El carrier conserva al menos un `evidence_id` de la configuración demostrada.

**Resultado:** CONFORME.

## 7. Ventana temporal

Se revalida:

```text
evaluation_date = PurchaseOperation.operation_date
window_end = operation_date
window_start = operation_date - (period_days - 1 días)
```

La semántica es inclusiva.

**Resultado:** CONFORME.

## 8. Carrier factual

El modelo conserva exactamente:

```text
article_id
evaluation_date
window_start
window_end
window_authority_ref
source_ref
source_semantics_ref
completeness_ref
activity_state
evidence_refs
trace_refs
```

Es frozen y `extra="forbid"`.

**Resultado:** CONFORME.

## 9. Frontera upstream

No se ha creado ningún modelo físico para:

- sales records;
- invoices;
- sales events;
- aggregated sales quantity;
- devoluciones;
- anulaciones;
- abonos;
- completitud upstream.

Motivo: la metodología deja los nombres físicos para contrato posterior y no existe todavía autoridad suficiente para inventarlos.

Por tanto la implementación no deriva `activity_state`.

**Resultado:** CONFORME / GAP EXPLÍCITO CONSERVADO.

## 10. Rules / CRC

No se modifica:

- `eios/rules/catalog.py`;
- rule orchestrator;
- CRC;
- R-ROT-002 executable bridge;
- R-ROT-001.

`ZERO_VALID_SALES_DEMONSTRATED` permanece soporte factual, no Assessment.

**Resultado:** CONFORME.

## 11. Tests

La suite específica cubre:

- caso válido;
- ventana de 1 día;
- valores inválidos de P-ROT-001;
- unidad inválida;
- configuración ausente/no solicitada;
- Evidence GAP/no vinculada;
- mismatches de carrier;
- conservación del evidence_id de configuración;
- campo canónico `activity_state`;
- estados autorizados;
- rechazo de estado desconocido;
- invariantes de ventana y refs;
- ausencia de promoción a rule result.

Se añade además verificación de firma pública para impedir que se incorpore una `ResolvedConfiguration` desprendida.

## 12. Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅ slice física acotada
MATERIALIZAR  ✅
CI            ⏳ PR
```

**0 bloqueadores estáticos para someter la slice a CI.**

Permanece fuera de alcance y pendiente de autoridad/contrato posterior el productor físico upstream de actividad de ventas y, posteriormente, el bridge completo de `R-ROT-002`.
