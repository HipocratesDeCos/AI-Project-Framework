# EIOS — Finance Horizon Provenance — Audit 1 v0.1

## Estado

**AUDITAR — SUPERADA CON 3 AJUSTES DE PRECISIÓN / 0 BLOQUEADORES**

**Objeto:** `08_Implementacion/Finance_Horizon_Provenance_Contract_v0.1.md`  
**Baseline:** `main @ 595b45296ae507d7d5224bdb7739bfb4184421a8`

---

## 1. Autoridad metodológica

La propuesta es compatible con `Finance_Basic_Authority_v0.1.md`:

- FIN-AUTH-01 autoriza `P-FIN-001` como horizonte metodológico de Finance Basic;
- FIN-AUTH-01 prohíbe redefinirlo como parámetro directo de `R-FIN-001`;
- FIN-AUTH-05 limita la proyección a `as_of_date < t <= horizon_end`;
- FIN-AUTH-06 deriva `financial_capacity_forecast` del mínimo de tesorería dentro del horizonte;
- FIN-AUTH-07 deriva el margen financiero de `financial_capacity_forecast` sin modificar la autoridad de Rules.

La frontera propuesta valida procedencia antes de evaluación y no altera ninguna fórmula.

**Resultado:** conforme.

---

## 2. Autoridad de parametrización

`Catalogo_Parametros_MVP_v0.3.md` define:

```text
P-FIN-001 | Horizonte de pagos | 30 | días | Alta | Restringida
```

FIN-AUTH-01 mantiene el valor vigente bajo Centro de Parametrización y no valida por sí sola el `30` inicial.

La solución reutiliza `ResolvedConfiguration` y `parameters_version`; no crea un segundo versionado.

**Resultado:** conforme.

---

## 3. Gap físico confirmado

El runtime actual permite:

```text
FinanceBasicInput(horizon_days=<entero desnudo>)
        ↓
calculate_finance_basic(...)
        ↓
FinanceBasicResult
        ↓
evaluate_r_fin_001 / evaluate_r_fin_003
```

Los bridges verifican identidad de decisión/escenario/snapshot/versiones y el hash del resultado, pero no pueden demostrar qué configuración individual de `P-FIN-001` originó `horizon_days`.

`ResolvedConfiguration` ya dispone de la primitiva adecuada:

```text
parameter_id
company_id
value
unit
parameters_version
effective_at
configuration_ref
```

**Resultado:** `FIN-PROV-HORIZON-01` es objetivo y resoluble sin nueva arquitectura base.

---

## 4. Precedente arquitectónico

PRICE ya cerró una frontera equivalente rechazando el consumo vertical de un resultado desprendido y exigiendo reconstrucción/revalidación desde entradas provenance-safe.

La propuesta Finance replica el principio, no la semántica de PRICE.

**Resultado:** compatible con arquitectura vigente.

---

## 5. A1-01 — La unidad debe fijarse exactamente a `días`

El diseño dice que la unidad debe “corresponder al concepto de días”. Esa formulación permitiría aliases inventados (`day`, `days`, `día`, etc.) sin autoridad documental.

La fuente canónica disponible fija literalmente:

```text
Unidad = días
```

### Corrección obligatoria

La materialización debe exigir:

```text
horizon_resolution.unit == "días"
```

sin aliases añadidos por esta unidad.

**Bloqueador:** no, si DEPURAR lo incorpora.

---

## 6. A1-02 — La validez temporal debe revalidarse incluso si existe ResolvedConfiguration

`resolve_configuration_for_context` comprueba vigencia, pero `ResolvedConfiguration` es una dataclass pública y puede instanciarse manualmente.

La revalidación de la envolvente debe comprobar explícitamente:

```text
valid_from <= effective_at < valid_to
```

cuando exista `valid_to`, manejando incompatibilidades de timezone/semántica temporal como error técnico.

No basta con confiar en que el objeto provenga de la factory del Centro.

**Bloqueador:** no, si DEPURAR lo incorpora.

---

## 7. A1-03 — No convertir la validación de producción en nueva dependencia RDM de R-FIN-003

`R-FIN-003` consume un `FinanceBasicResult` cuyo `safety_margin` deriva de `financial_capacity_forecast`. Por ello, todo resultado Finance Basic que cruce a Rules debe ser provenance-safe respecto de su propio horizonte.

Sin embargo, esta unidad no tiene por objeto abrir ni ampliar el mapa RDM de `R-FIN-003`.

### Corrección obligatoria

Debe quedar explícito que:

- `evaluate_r_fin_003` exige una ejecución Finance Basic íntegra porque **no acepta resultados Finance Basic desprendidos**;
- esto es una propiedad de la frontera técnica del productor;
- no se materializa en esta unidad una nueva arista `P-FIN-001 → R-FIN-003`;
- cualquier ampliación RDM requeriría su propio ciclo documental.

**Bloqueador:** no, si DEPURAR lo incorpora.

---

## 8. Evaluabilidad

La RDM mantiene para `DEP-FIN-001-RFIN-001`:

```text
Criticality = PENDING
Evaluability_Impact = PENDING
```

Por ello la propuesta acierta al tratar una incoherencia de provenance como error técnico previo a Rules y no como `Assessment.NOT_EVALUABLE` nuevo.

No se autoriza inferir:

```text
P-FIN-001 ausente → NOT_EVALUABLE
```

como política de regla.

**Resultado:** conforme.

---

## 9. Motor Finance Basic

`calculate_finance_basic` puede permanecer como motor determinista de bajo nivel porque:

- sigue siendo útil para tests metodológicos;
- la frontera que debe cerrarse es la reutilización vertical;
- los bridges FIN dejarán de aceptar el par desprendido `FinanceBasicInput + FinanceBasicResult`;
- la envolvente se revalida y recomputa antes de Rules.

No debe introducirse un fallback que envuelva automáticamente un resultado ya calculado sin verificar su origen.

**Resultado:** conforme.

---

## 10. Evidencia y hash

`finance_basic_result_ref(result)` puede seguir identificando determinísticamente el resultado analítico.

La procedencia de `P-FIN-001` no necesita convertirse en evidencia decisoria adicional de la regla dentro de esta unidad, porque:

- la envolvente conserva `ResolvedConfiguration` completa;
- el bridge revalida la resolución antes de utilizar el resultado;
- el resultado se recomputa y se compara exactamente;
- `P-FIN-001` no se añade a `evidence_ids` ni se presenta como umbral de Rules.

Esto mantiene separadas procedencia técnica y evidencia decisoria.

**Resultado:** conforme.

---

## 11. Superficie afectada autorizada

La materialización puede limitarse a:

- nuevo módulo `eios/finance/provenance.py`;
- export de las nuevas primitivas desde `eios.finance`;
- adaptación de `eios/rules/finance.py`;
- adaptación de `eios/rules/orchestrator.py`;
- tests Finance/Rules/orchestrator estrictamente necesarios;
- documentación de cierre.

No se justifica modificar:

- fórmulas de `eios/finance/engine.py`;
- modelos financieros existentes;
- Centro de Parametrización;
- C0/CRC;
- RDM en esta unidad;
- otros dominios.

---

## 12. Dictamen

```text
Autoridad Finance                ✅
Centro de Parametrización        ✅
Gap físico real                  ✅
Patrón provenance compatible     ✅
Sin nuevo default                ✅
Sin nueva evaluabilidad          ✅
Sin nueva autoridad decisoria    ✅
Ajustes de precisión             3
Bloqueadores                     0
```

**AUDIT 1: SUPERADA CON 3 AJUSTES DE PRECISIÓN / 0 BLOQUEADORES.**