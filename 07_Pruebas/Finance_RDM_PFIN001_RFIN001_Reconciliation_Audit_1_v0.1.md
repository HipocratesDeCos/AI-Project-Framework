# EIOS — Finance · RDM P-FIN-001 → R-FIN-001 Reconciliation — Audit 1 v0.1

**Estado:** AUDITAR — SUPERADA CON 1 AJUSTE DE PRECISIÓN  
**Objeto:** `Finance_RDM_PFIN001_RFIN001_Reconciliation_Design_v0.1.md`

## 1. Contraste de autoridad

La relación está demostrada explícitamente por `01_Modelo/Finance_Basic_Authority_v0.1.md`:

- FIN-AUTH-01 autoriza `P-FIN-001` como horizonte metodológico de Finance Basic;
- FIN-AUTH-01 establece literalmente la cadena `P-FIN-001 → Finance Basic projection horizon → financial_capacity_forecast → R-FIN-001`;
- FIN-AUTH-01 prohíbe reinterpretar `P-FIN-001` como parámetro directo de `R-FIN-001`;
- FIN-AUTH-05 define la proyección cronológica dentro del horizonte autorizado;
- FIN-AUTH-06 define `financial_capacity_forecast` como el mínimo de tesorería proyectada dentro de ese horizonte.

`04_Reglas/Matriz_Reglas_MVP.md` conserva la condición de `R-FIN-001` y no contradice la cadena anterior.

## 2. Contraste de implementación

`08_Implementacion/Finance_Basic_Implementation_Contract_v0.1.md` declara expresamente:

```text
horizon_days es valor ya resuelto de P-FIN-001
```

El código físico es coherente con la transformación cuantitativa:

- `FinanceBasicInput.horizon_days` exige un entero positivo;
- `eios/finance/engine.py` calcula `horizon_end = as_of_date + horizon_days`;
- únicamente los flujos aplicables hasta `horizon_end` participan en la proyección;
- `financial_capacity_forecast` se obtiene como mínimo de tesorería de esa proyección;
- `eios/rules/finance.py` consume `financial_capacity_forecast` en `R-FIN-001` y lo compara con `P-FIN-002`.

La implementación confirma la existencia de la transformación, pero no debe usarse como sustituto de la autoridad documental.

## 3. Clasificación de dependencia

`Dependency_Type = DERIVED` es correcta.

`P-FIN-001` no es el umbral que compara `R-FIN-001`; modifica el dominio temporal del cálculo que produce la magnitud posteriormente consumida por la regla. La transformación está autorizada y documentada, por lo que cumple la definición RDM de dependencia `DERIVED`.

`PARAMETER` directa sería incorrecta y contradiría FIN-AUTH-01.

## 4. Hallazgo A1-01 — deuda de provenance debe quedar identificada, no solo descrita

El diseño distingue correctamente relación documental y binding físico, pero conviene convertir la limitación de runtime en un gap trazable con identificador estable para impedir que la materialización de la arista sea interpretada como cierre provenance-safe.

Se define para esta unidad:

```text
FIN-PROV-HORIZON-01
= ausencia de vínculo físico verificable entre FinanceBasicInput.horizon_days
  y una ResolvedConfiguration/configuration_ref concreta de P-FIN-001
```

Este gap:

- **no invalida** la relación documental `P-FIN-001 → R-FIN-001`;
- **no autoriza** modificar código dentro de esta unidad;
- deberá permanecer visible en las Notes de la arista canónica y en el cierre;
- no debe confundirse con ausencia de `parameters_version`, que sí existe en `DecisionContext`/`FinanceBasicResult`; el déficit es el binding individual del valor de horizonte.

**Severidad:** precisión de provenance.  
**Bloqueador para reconciliación documental:** NO.  
**Bloqueador para declarar binding físico provenance-safe de P-FIN-001:** SÍ.

## 5. Vista especializada parámetro ↔ regla

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` debe reconciliarse porque actualmente deja `P-FIN-001` como pendiente de cruce.

La formulación debe conservar explícitamente que la relación es **derivada/metodológica mediante Finance Basic**, no consumidor directo de la condición de regla.

## 6. Fronteras verificadas

No existe autoridad en esta unidad para:

- validar el valor inicial de 30 días;
- introducir defaults;
- modificar la condición `financial_capacity_forecast < P-FIN-002`;
- añadir binding runtime por inferencia;
- modificar código, tests, Rules, CRC o C0;
- asignar `Criticality` o `Evaluability_Impact`;
- inferir dependencias `DATA`, `EVIDENCE` o `COMPONENT`.

## 7. Dictamen

**AUDIT 1: SUPERADA CON 1 AJUSTE DE PRECISIÓN / 0 BLOQUEADORES DOCUMENTALES.**

DEPURAR debe incorporar el identificador `FIN-PROV-HORIZON-01` y exigir que la futura arista canónica no certifique provenance físico que el runtime todavía no demuestra.