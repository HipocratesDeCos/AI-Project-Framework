# EIOS — Finance Horizon Provenance — Audit 2 v0.1

## Estado

**AUDITAR 2 — SUPERADA / 0 BLOQUEADORES**

**Objeto:** contrato v0.1 + Audit 1 + depuración v0.1  
**Baseline:** `main @ 595b45296ae507d7d5224bdb7739bfb4184421a8`

---

## 1. Autoridad metodológica

La solución depurada no modifica `FIN-AUTH-01…07`.

Se conserva exactamente:

```text
P-FIN-001
   ↓
Finance Basic projection horizon
   ↓
financial_capacity_forecast
   ↓
R-FIN-001
```

`P-FIN-001` continúa siendo un parámetro metodológico del productor Finance Basic, no un umbral directo de la condición de `R-FIN-001`.

La proyección sigue limitada por el horizonte autorizado y `financial_capacity_forecast` continúa siendo el mínimo de tesorería proyectada dentro de dicho horizonte.

**Resultado:** conforme.

---

## 2. Parametrización y valor empresarial

La implementación propuesta consume exclusivamente una `ResolvedConfiguration` existente.

No crea:

- nuevos valores;
- defaults;
- un segundo `parameters_version`;
- una copia paralela del Centro de Parametrización;
- una política implícita de 30 días.

La única unidad aceptada será literalmente:

```text
días
```

según el catálogo vigente.

El valor 30 continúa sin quedar validado como política empresarial por esta unidad.

**Resultado:** conforme.

---

## 3. Integridad temporal y contextual

La validación depurada exige simultáneamente:

```text
parameter_id = P-FIN-001
parameters_version = DecisionContext.parameters_version
company_id = FinancialSnapshot.company_scope
effective_at.date() = FinancialSnapshot.as_of_date
valid_from <= effective_at < valid_to   # cuando valid_to exista
unit = días
value entero positivo y finito
value = FinanceBasicInput.horizon_days
```

Esto impide que una coincidencia de `parameters_version` o un entero desnudo sea utilizada como sustituto del origen individual del horizonte.

**Resultado:** conforme.

---

## 4. Frontera antidesprendimiento

La nueva frontera no aceptará un `FinanceBasicResult` proporcionado por el llamador durante la producción provenance-safe.

```text
FinanceBasicInput
+ ResolvedConfiguration(P-FIN-001)
        ↓
validación
        ↓
calculate_finance_basic
        ↓
ProvenancedFinanceBasicExecution
```

Además, cualquier ejecución reutilizada será revalidada mediante:

```text
validate_provenanced_finance_basic_execution
```

que vuelve a:

1. comprobar la resolución de `P-FIN-001`;
2. recalcular Finance Basic;
3. exigir igualdad exacta con el resultado transportado.

Por tanto, construir manualmente una envolvente no permite introducir un resultado desprendido sin detección.

**Resultado:** conforme.

---

## 5. Revisión de consumidores Rules

Los consumidores FIN públicos identificados en Rules son:

- `evaluate_r_fin_001`;
- `evaluate_r_fin_003`;
- los bundles `FinanceCapacityRuleInputs` y `FinanceSafetyMarginRuleInputs` del orquestador de reglas.

La materialización autorizada elimina en esas fronteras el transporte separado:

```text
FinanceBasicInput + FinanceBasicResult
```

y lo sustituye por:

```text
ProvenancedFinanceBasicExecution
```

Los bridges revalidarán la envolvente antes de ejecutar su lógica existente.

No queda autorizada una firma alternativa de compatibilidad que siga aceptando resultados desprendidos.

**Resultado:** conforme.

---

## 6. R-FIN-001

Después de validar la ejecución Finance Basic, la regla mantiene exactamente:

```text
financial_capacity_forecast < P-FIN-002
```

No cambian:

- resolución de `P-FIN-002`;
- evidencia de `P-FIN-002`;
- evidencia del resultado Finance Basic;
- `Assessment.status`;
- `Assessment.outcome`;
- severidad;
- efecto R0;
- CRC.

`P-FIN-001` no se añade como evidencia decisoria de la regla.

**Resultado:** conforme.

---

## 7. R-FIN-003

La exigencia de una ejecución Finance Basic provenance-safe protege la integridad del producto analítico completo.

No se interpreta ni materializa como una nueva relación canónica:

```text
P-FIN-001 → R-FIN-003
```

La condición de la regla permanece:

```text
financial_safety_margin_pct < P-FIN-004
```

La relación `P-FIN-002 → R-FIN-003` y la relación directa `P-FIN-004 → R-FIN-003` permanecen sin cambios.

**Resultado:** conforme.

---

## 8. Evaluabilidad y tratamiento del error

La RDM conserva:

```text
DEP-FIN-001-RFIN-001
Criticality = PENDING
Evaluability_Impact = PENDING
```

Por ello una violación de provenance de horizonte no puede transformarse por esta unidad en un nuevo resultado empresarial.

El comportamiento correcto es:

```text
provenance incoherente
→ error técnico de frontera
→ no se ejecuta Rules con ese objeto
```

No se introduce:

```text
P-FIN-001 ausente/inválida → Assessment.NOT_EVALUABLE
```

como política no autorizada.

**Resultado:** conforme.

---

## 9. Evidencia y trazabilidad

`finance_basic_result_ref(result)` sigue siendo una referencia determinista del resultado.

La procedencia individual del horizonte queda materialmente conservada en:

```text
ProvenancedFinanceBasicExecution.horizon_resolution
ProvenancedFinanceBasicExecution.horizon_resolution.configuration_ref
```

La revalidación demuestra que el resultado transportado corresponde al input cuyo `horizon_days` coincide con esa resolución.

Esto cierra la falta física que motivó `FIN-PROV-HORIZON-01` sin ampliar `Assessment.evidence_ids`.

**Resultado:** conforme.

---

## 10. Compatibilidad con fronteras cerradas

No se detectan contradicciones contra:

- Finance Basic Methodological Closure;
- Finance Basic Implementation Contract;
- Centro de Parametrización / `ResolvedConfiguration`;
- Rules;
- RDM;
- Evidence Contract;
- C0;
- CRC;
- PRICE provenance-safe boundary;
- Scenario / Decision Twin;
- STK / TCO / VF.

El precedente PRICE confirma el principio arquitectónico de reconstruir o revalidar en la frontera de reutilización en lugar de confiar en resultados desprendidos.

No se copia semántica de PRICE dentro de Finance.

---

## 11. Superficie de materialización

Se autoriza exclusivamente:

```text
eios/finance/provenance.py
eios/finance/__init__.py
eios/rules/finance.py
eios/rules/orchestrator.py
tests directamente afectados
documentación de cierre
```

No se autoriza modificar:

```text
eios/finance/engine.py
eios/finance/models.py
eios/parameters/*
Rule_Dependency_Matrix.md
C0
CRC
otros dominios
```

salvo contradicción objetiva descubierta durante materialización, en cuyo caso deberá detenerse esa ampliación y reabrir auditoría antes de actuar.

---

## 12. Invariantes de tests

La materialización debe demostrar al menos:

- caso positivo con resolución válida de P-FIN-001;
- rechazo de parameter_id, versión, empresa, fecha, vigencia, unidad o valor incompatibles;
- rechazo de horizonte no entero/no positivo/no finito;
- rechazo si el valor no coincide con `horizon_days`;
- rechazo de una envolvente manual con resultado diferente del recalculado;
- conservación de resultados y evidence_ids de R-FIN-001;
- conservación de resultados y evidence_ids de R-FIN-003;
- cierre del orquestador al nuevo bundle provenance-safe;
- suite completa sin regresiones.

---

## 13. Dictamen

```text
Autoridad metodológica          ✅
Parametrización                 ✅
Identidad individual P-FIN-001 ✅
Vigencia temporal               ✅
Antidesprendimiento             ✅
R-FIN-001 sin cambio semántico  ✅
R-FIN-003 sin nueva arista RDM  ✅
Evaluabilidad no inventada      ✅
C0 / CRC intactos               ✅
Superficie acotada              ✅
Bloqueadores                    0
```

**AUDIT 2: SUPERADA — 0 BLOQUEADORES.**

Se autoriza pasar a CERRAR el contrato técnico y posteriormente a MATERIALIZAR.