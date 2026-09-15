# EIOS — Finance · RDM P-FIN-001 → R-FIN-001 Reconciliation — Design v0.1

**Estado:** DISEÑAR — PROPUESTA ACOTADA  
**Baseline:** `main @ 15c75e7b12d21053cf06222e2dcf1eec0e7e7ad7`  
**Ámbito:** dependencia derivada de `P-FIN-001` respecto de `R-FIN-001`

## 1. Hallazgo de partida

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` mantiene `P-FIN-001` como pendiente de identificación documental individual y `04_Reglas/Rule_Dependency_Matrix.md` no representa todavía esta arista.

Sin embargo, `01_Modelo/Finance_Basic_Authority_v0.1.md` FIN-AUTH-01 autoriza expresamente:

```text
P-FIN-001
   ↓
Finance Basic projection horizon
   ↓
financial_capacity_forecast
   ↓
R-FIN-001
```

La misma autoridad especifica que `P-FIN-001` **no** se redefine como parámetro directo de `R-FIN-001`.

Además, `08_Implementacion/Finance_Basic_Implementation_Contract_v0.1.md` declara que `FinanceBasicInput.horizon_days` es el valor ya resuelto de `P-FIN-001`, sin default aportado por Finance Basic; `eios/finance/engine.py` utiliza dicho horizonte para calcular `horizon_end` y, a partir de la proyección dentro de ese horizonte, `financial_capacity_forecast`.

## 2. Relación propuesta

```text
Dependency_ID: DEP-FIN-001-RFIN-001
Rule_ID: R-FIN-001
Dependency_Type: DERIVED
Source_ID: P-FIN-001
Source_Domain: PARAMETER
Function: Horizonte autorizado que acota la proyección financiera de la que deriva financial_capacity_forecast consumida por R-FIN-001
Criticality: PENDING
Evidence_Source: 01_Modelo/Finance_Basic_Authority_v0.1.md
Evidence_Status: CONFIRMED
Evaluability_Impact: PENDING
Fallback: NONE
Affected_Component: NONE
```

## 3. Justificación del tipo DERIVED

`R-FIN-001` no compara directamente un dato contra `P-FIN-001`.

La condición autorizada sigue siendo:

```text
financial_capacity_forecast < P-FIN-002
```

`P-FIN-001` determina aguas arriba el horizonte de la proyección que produce `financial_capacity_forecast`. La transformación está documentada expresamente por FIN-AUTH-01, FIN-AUTH-05 y FIN-AUTH-06.

Por ello, clasificar la arista como `PARAMETER` directa introduciría una semántica que la autoridad prohíbe expresamente.

## 4. Distinción documental vs provenance físico

La confirmación de esta arista demuestra la **relación funcional/documental** entre `P-FIN-001` y `R-FIN-001`.

No demuestra por sí sola que cada ejecución física de Finance Basic haya vinculado `horizon_days` a una `ResolvedConfiguration` concreta mediante una referencia de configuración verificable.

Estado físico observado en el baseline:

- `FinanceBasicInput` contiene `horizon_days: int > 0`;
- `DecisionContext` conserva `parameters_version`;
- el contrato técnico declara que `horizon_days` llega ya resuelto desde `P-FIN-001`;
- el modelo físico no transporta actualmente `parameter_id`, `configuration_ref` ni otro vínculo individual equivalente para ese horizonte;
- `evaluate_r_fin_001` valida `P-FIN-002`, pero no reconstruye ni verifica `P-FIN-001`.

Esta diferencia se registra como deuda separada de provenance runtime. **No bloquea la reconciliación documental**, pero tampoco queda resuelta por ella.

## 5. Fronteras

Esta unidad no autoriza:

- convertir `P-FIN-001` en parámetro directo de `R-FIN-001`;
- validar por inferencia el valor inicial de 30 días;
- modificar `FinanceBasicInput`, `eios/finance/engine.py` o `eios/rules/finance.py`;
- declarar provenance-safe el binding físico de `horizon_days`;
- modificar `P-FIN-002`, la fórmula de `financial_capacity_forecast`, la condición, efecto o severidad de `R-FIN-001`;
- asignar `Criticality` o `Evaluability_Impact` sin autoridad;
- introducir dependencias `DATA`, `EVIDENCE` o `COMPONENT` adicionales;
- modificar CRC, C0, MED u otras capacidades cerradas.

## 6. Materialización prevista

Si las dos auditorías resultan limpias:

1. incorporar `DEP-FIN-001-RFIN-001` a `04_Reglas/Rule_Dependency_Matrix.md` como `DERIVED / CONFIRMED`;
2. reconciliar `02_Parametros/Matriz_Parametros_Reglas_MVP.md` para reflejar `P-FIN-001 → R-FIN-001` como relación derivada;
3. conservar explícitamente la limitación de provenance físico como deuda separada y no como propiedad resuelta por la RDM.

No se modificará código en esta unidad.