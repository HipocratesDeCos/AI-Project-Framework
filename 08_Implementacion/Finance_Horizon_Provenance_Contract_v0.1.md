# EIOS — Finance Horizon Provenance Contract v0.1

## Estado

**DISEÑAR — PROPUESTA TÉCNICA ACOTADA**

**Baseline:** `main @ 595b45296ae507d7d5224bdb7739bfb4184421a8`  
**Gap objetivo:** `FIN-PROV-HORIZON-01`

---

## 1. Propósito

Cerrar la frontera física entre `P-FIN-001` y `FinanceBasicInput.horizon_days` sin modificar la metodología cerrada de Finance Basic ni convertir `P-FIN-001` en un umbral decisorio de `R-FIN-001`.

La autoridad vigente establece:

```text
P-FIN-001
   ↓
Finance Basic projection horizon
   ↓
financial_capacity_forecast
```

El contrato técnico existente declara `horizon_days` como valor ya resuelto de `P-FIN-001`, pero el runtime actual permite construir `FinanceBasicInput` con un entero desnudo y posteriormente reutilizar `FinanceBasicInput + FinanceBasicResult` sin demostrar qué `ResolvedConfiguration(P-FIN-001)` originó el horizonte.

---

## 2. Contradicción objetiva

Actualmente:

- `FinanceBasicInput.horizon_days` conserva solo un entero positivo;
- `FinanceBasicResult.parameters_version` conserva la versión contextual, pero no la identidad individual de `P-FIN-001`;
- `eios.rules.finance` valida que resultado, input y `DecisionContext` coincidan, pero no puede demostrar el origen de `horizon_days`;
- `ResolvedConfiguration` ya proporciona `parameter_id`, `company_id`, `value`, `unit`, `parameters_version`, `effective_at` y `configuration_ref` sin crear un segundo sistema de versionado.

Por tanto, el par desprendido `FinanceBasicInput + FinanceBasicResult` no constituye una frontera provenance-safe suficiente para consumidores verticales.

---

## 3. Frontera propuesta

Se introduce una envolvente inmutable:

```text
ProvenancedFinanceBasicExecution
```

que contiene conjuntamente:

- `finance_input: FinanceBasicInput`;
- `finance_result: FinanceBasicResult`;
- `horizon_resolution: ResolvedConfiguration`.

La envolvente se obtiene únicamente mediante una función pública de ejecución provenance-safe:

```text
run_provenanced_finance_basic(
    finance_input,
    horizon_resolution,
) -> ProvenancedFinanceBasicExecution
```

El motor matemático cerrado sigue siendo:

```text
calculate_finance_basic(finance_input)
```

La nueva frontera no modifica sus fórmulas.

---

## 4. Validaciones obligatorias de P-FIN-001

Antes de calcular Finance Basic debe cumplirse:

1. `horizon_resolution.parameter_id == "P-FIN-001"`;
2. `horizon_resolution.parameters_version == finance_input.context.parameters_version`;
3. `horizon_resolution.company_id == finance_input.snapshot.company_scope`;
4. `horizon_resolution.effective_at.date() == finance_input.snapshot.as_of_date`;
5. la configuración debe estar vigente en `horizon_resolution.effective_at`;
6. el valor debe representar un número entero de días estrictamente positivo;
7. la unidad debe corresponder al concepto de días autorizado para `P-FIN-001`;
8. el valor resuelto debe coincidir exactamente con `finance_input.horizon_days`.

No existe fallback a 30 días ni a ningún otro valor.

Un incumplimiento es un **error técnico de frontera** y debe fallar antes de producir evaluación de regla. No se traduce por esta unidad a `Assessment.NOT_EVALUABLE`, porque `Evaluability_Impact` de la arista permanece `PENDING` en la RDM.

---

## 5. Revalidación de la envolvente

La mera existencia de una instancia `ProvenancedFinanceBasicExecution` no debe considerarse suficiente, porque Python permite construir objetos fuera de una factory.

Se define una validación pública:

```text
validate_provenanced_finance_basic_execution(execution)
```

que debe:

- repetir las invariantes de `P-FIN-001`;
- volver a calcular `calculate_finance_basic(execution.finance_input)`;
- exigir igualdad exacta con `execution.finance_result`.

De esta forma, una envolvente construida manualmente con un resultado desprendido o un horizonte incompatible falla antes de llegar a Rules.

---

## 6. Migración de los bridges FIN

`evaluate_r_fin_001` y `evaluate_r_fin_003` dejarán de recibir el par:

```text
FinanceBasicInput + FinanceBasicResult
```

como frontera pública.

Pasarán a recibir:

```text
ProvenancedFinanceBasicExecution
```

La primera operación del bridge será revalidar la envolvente.

Tras esa validación:

- `R-FIN-001` conserva exactamente `financial_capacity_forecast < P-FIN-002`;
- `R-FIN-003` conserva exactamente `financial_safety_margin_pct < P-FIN-004`;
- la validación existente de `P-FIN-002` y `P-FIN-004` no cambia;
- `P-FIN-001` no se añade a `evidence_ids` como evidencia decisoria de la regla;
- no se crea ningún resultado empresarial nuevo.

---

## 7. Migración del orquestador de reglas

Los bundles internos:

```text
FinanceCapacityRuleInputs
FinanceSafetyMarginRuleInputs
```

dejarán de transportar `finance_input` y `finance_result` por separado y transportarán una única `finance_execution` provenance-safe.

No habrá fallback compatible que reconstruya automáticamente una envolvente a partir de un resultado desprendido.

---

## 8. Inmutabilidad

La ejecución provenance-safe debe congelar copias profundas del input y de la resolución antes del cálculo.

Mutaciones externas posteriores no deben cambiar la ejecución ya construida.

Los modelos Pydantic actuales son `frozen`, pero la copia profunda preserva el mismo criterio de snapshot aplicado a otras fronteras provenance-safe del proyecto.

---

## 9. Semántica preservada

Esta unidad no:

- modifica `FIN-AUTH-01…07`;
- valida el valor inicial de 30 días;
- crea un segundo versionado de parámetros;
- altera `ResolvedConfiguration` ni Centro de Parametrización;
- modifica la fórmula de proyección, capacidad, fondo de maniobra o margen;
- convierte `P-FIN-001` en umbral directo de `R-FIN-001` o `R-FIN-003`;
- determina `Criticality` o `Evaluability_Impact` de la RDM;
- modifica severidad, efecto o autoridad de Rules/CRC;
- introduce nuevas reglas, heurísticas, scores, defaults o decisiones;
- modifica C0, PRICE, STK, TCO, QTG, Decision Twin o Scenario.

---

## 10. Compatibilidad y API

`calculate_finance_basic` permanece como motor determinista de bajo nivel para cálculo y tests de metodología.

La frontera Rules/Vertical deja de aceptar resultados Finance Basic desprendidos.

Esto replica el principio ya cerrado en PRICE:

> un motor interno puede existir, pero la frontera de reutilización vertical debe reconstruir o revalidar la procedencia completa necesaria.

---

## 11. Tests obligatorios

La materialización deberá probar al menos:

1. ejecución válida con `P-FIN-001 = 30 días` resuelto para mismo contexto/empresa/fecha;
2. rechazo de parámetro distinto de `P-FIN-001`;
3. rechazo de `parameters_version` distinta;
4. rechazo de `company_scope` distinto;
5. rechazo de `effective_at` en fecha distinta del snapshot;
6. rechazo de configuración no vigente;
7. rechazo de valor no entero, no finito, cero o negativo;
8. rechazo de unidad incompatible;
9. rechazo si `horizon_days` no coincide con el valor resuelto;
10. revalidación que rechaza resultado desprendido/manipulado;
11. `R-FIN-001` mantiene sus resultados con ejecución provenance-safe;
12. `R-FIN-003` mantiene sus resultados con ejecución provenance-safe;
13. el orquestador FIN no acepta ya el par input/result separado;
14. ninguna regresión en Finance Basic ni en la suite completa.

---

## 12. Criterio de cierre

`FIN-PROV-HORIZON-01` solo podrá cerrarse cuando:

1. Audit 1 confirme la frontera y detecte ambigüedades;
2. DEPURAR incorpore sus correcciones;
3. Audit 2 no detecte rutas FIN públicas que consuman un `FinanceBasicResult` desprendido dentro de Rules/Vertical;
4. la implementación y tests respeten el contrato;
5. CI pre-merge sea satisfactoria sobre el head exacto;
6. se integre ese mismo head;
7. CI post-merge sea satisfactoria.
