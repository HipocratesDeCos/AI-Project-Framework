# EIOS — ROT002 Sales Activity Window Provenance Audit 2 v0.1

**Baseline:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Objeto:** `08_Implementacion/ROT002_Sales_Activity_Window_Provenance_Contract_v0.1.md`  
**Estado:** AUDIT 2 — SUPERADA  
**Audit 1:** `07_Pruebas/ROT002_Sales_Activity_Window_Provenance_Audit_1_v0.1.md`

## 1. Verificación de la corrección principal

Audit 1 detectó que `PurchaseOperation` no contiene `company_id` y que aceptar una `ResolvedConfiguration(P-ROT-001)` desprendida reabriría una vía de provenance incompleta.

El contrato depurado adopta:

```text
DecisionInputPackage
```

como raíz canónica.

Esto permite reutilizar sin duplicar:

```text
company_id
effective_at
purchase
context
requested_parameter_ids
configurations
missing_parameter_ids
evidence
```

**Resultado:** CORREGIDO.

## 2. P-ROT-001 no desprendida

La frontera pública ya no acepta una resolución separada.

Debe seleccionar P-ROT-001 dentro del propio DIP y exigir:

```text
P-ROT-001 solicitado
P-ROT-001 no missing
exactamente una resolución
company_id coherente
parameters_version coherente
effective_at coherente
vigencia válida
```

**Resultado:** CONFORME.

## 3. Identidad decisional

DIP ya valida la identidad PurchaseOperation ↔ DecisionContext.

El contrato exige revalidación antes de producir/reutilizar el carrier.

No se introducen:

- decision_id alternativo;
- scenario_id alternativo;
- company_id alternativo;
- segundo effective_at.

**Resultado:** CONFORME.

## 4. Semántica temporal

Se conserva exactamente la autoridad aprobada:

```text
evaluation_date = DIP.purchase.operation_date
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 días)
```

Unidad:

```text
días
```

Valor:

```text
entero finito positivo
```

Sin default.

**Resultado:** CONFORME.

## 5. Evidence

El contrato no convierte `configuration_ref` en prueba empresarial y mantiene separado:

```text
configuration_ref → referencia técnica reproducible
Evidence → soporte de evidencia
authority document → autoridad normativa
```

La autoridad especializada `ROT002_Parameter_Configuration_Evidence_Binding_Authority_v0.1.md` autoriza exactamente:

```text
Evidence.source_ref == ResolvedConfiguration.configuration_ref
```

y exige al menos una Evidence `DEMONSTRATED` con `demonstration_ref`.

No crea `source_type` nuevo ni impone igualdad temporal adicional.

**Resultado:** CONFORME — GATE CERRADO.

## 6. Carrier factual

`SalesActivityWindowEvidence` permanece estrictamente factual.

Estados permitidos:

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No contiene resultados oficiales ni estados de Assessment.

**Resultado:** CONFORME.

## 7. ZERO_VALID_SALES_DEMONSTRATED

Se mantiene la prueba positiva de ausencia.

No puede producirse desde:

- cero filas;
- GAP;
- net quantity = 0;
- ventana parcial;
- ausencia de Evidence.

**Resultado:** CONFORME.

## 8. Fronteras de dominio

No se introducen transformaciones:

```text
ventas → demanda
ventas → consumo
ventas → cobertura
ventas → rotación general
```

No se modifica STK.

**Resultado:** CONFORME.

## 9. Rules / CRC

Track A no:

- crea Assessment;
- aplica excepción;
- produce NO COMPRAR;
- asigna R1/R0;
- ejecuta CRC.

El bridge de `R-ROT-002` permanece unidad posterior.

**Resultado:** CONFORME.

## 10. R-ROT-001

No se modifica:

- fórmula;
- métrica;
- numerador;
- denominador;
- ventana;
- threshold;
- dependencias.

**Resultado:** CONFORME.

## 11. No regresión provenance

El contrato adopta el principio ya materializado en otras fronteras EIOS:

```text
resultado desprendido != autoridad suficiente
```

El carrier debe reconstruirse o revalidarse contra DIP + configuración + evidencia + input factual autorizado.

**Resultado:** CONFORME.

## 12. Gates

```text
ROT002-AW-G01 → CLOSED — DIP root
ROT002-AW-G02 → CLOSED — P-ROT-001 inside DIP
ROT002-AW-G03 → CLOSED — identity/scope/effective_at
ROT002-AW-G04 → CLOSED — binding Evidence.source_ref == configuration_ref autorizado
ROT002-AW-G05 → CLOSED — exact inclusive window
ROT002-AW-G06 → CLOSED — source semantics separated
ROT002-AW-G07 → CLOSED — completeness required
ROT002-AW-G08 → CLOSED — Track A states only
ROT002-AW-G09 → CLOSED — provenance-safe reuse
ROT002-AW-G10 → CLOSED — no Rules/CRC/exceptions
```

## 13. Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅ Audit 1
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅ contrato técnico
MATERIALIZAR  ⏳ siguiente unidad
CI            ⏳ después de materialización
```

**0 bloqueadores contractuales para materializar Track A physical carrier + provenance boundary.**

No se autoriza todavía el bridge completo de `R-ROT-002`.
