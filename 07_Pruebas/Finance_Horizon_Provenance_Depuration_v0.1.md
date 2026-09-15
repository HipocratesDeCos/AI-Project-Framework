# EIOS — Finance Horizon Provenance — Depuration v0.1

## Estado

**DEPURAR — COMPLETADA**

**Origen:** `Finance_Horizon_Provenance_Audit_1_v0.1.md`  
**Hallazgos incorporados:** A1-01, A1-02, A1-03

---

## 1. Frontera técnica depurada

Se mantiene:

```text
FinanceBasicInput
+ ResolvedConfiguration(P-FIN-001)
        ↓
run_provenanced_finance_basic
        ↓
ProvenancedFinanceBasicExecution
```

La envolvente contiene:

```text
finance_input
finance_result
horizon_resolution
```

Todos los elementos se congelan como snapshot de ejecución.

---

## 2. Validación exacta de P-FIN-001

La resolución del horizonte es válida únicamente cuando se cumplen todas estas condiciones:

```text
parameter_id == "P-FIN-001"
parameters_version == finance_input.context.parameters_version
company_id == finance_input.snapshot.company_scope
effective_at.date() == finance_input.snapshot.as_of_date
unit == "días"
value = número finito, entero y > 0
int(value) == finance_input.horizon_days
```

La unidad `días` procede literalmente de `Catalogo_Parametros_MVP_v0.3.md`.

No se aceptan aliases añadidos por implementación.

No se valida ni se inserta el valor `30` por defecto.

---

## 3. Validez temporal revalidada

La configuración subyacente debe cumplir además:

```text
configuration.valid_from <= horizon_resolution.effective_at
```

y, cuando exista `valid_to`:

```text
horizon_resolution.effective_at < configuration.valid_to
```

Una configuración fuera del intervalo o temporalmente incomparable falla como error técnico de provenance.

Esto se comprueba aunque el tipo recibido sea `ResolvedConfiguration`, porque dicho objeto puede instanciarse directamente fuera de `resolve_configuration_for_context`.

---

## 4. Error técnico estable

La implementación puede introducir:

```text
FinanceHorizonProvenanceError(ValueError)
```

para distinguir una violación de esta frontera de un resultado empresarial de Rules.

No produce `Assessment`, no modifica CRC y no determina `Evaluability_Impact`.

---

## 5. Producción provenance-safe

`run_provenanced_finance_basic` debe:

1. exigir tipos correctos;
2. copiar profundamente `FinanceBasicInput` y `ResolvedConfiguration`;
3. validar la resolución de horizonte contra la copia del input;
4. ejecutar `calculate_finance_basic` sobre la copia;
5. devolver la envolvente inmutable.

No acepta un `FinanceBasicResult` aportado por el llamador.

---

## 6. Revalidación antidesprendimiento

`validate_provenanced_finance_basic_execution` debe:

1. comprobar el tipo de envolvente;
2. revalidar `horizon_resolution` contra `finance_input`;
3. recomputar `calculate_finance_basic(finance_input)`;
4. exigir igualdad exacta con `finance_result`.

Una envolvente construida manualmente con un resultado distinto falla.

Una envolvente construida con una resolución diferente pero mismo `parameters_version` falla si el valor/identidad/empresa/fecha/unidad no coincide.

---

## 7. Bridges FIN depurados

Firmas objetivo:

```text
evaluate_r_fin_001(
    purchase,
    context,
    rule,
    finance_execution,
    finance_evidence,
    threshold_resolution,
    parameter_evidence,
)
```

```text
evaluate_r_fin_003(
    purchase,
    context,
    rule,
    finance_execution,
    finance_evidence,
    treasury_minimum_resolution,
    treasury_minimum_evidence,
    margin_resolution,
    margin_evidence,
)
```

Ambos bridges:

```text
validate_provenanced_finance_basic_execution(finance_execution)
```

antes de extraer:

```text
finance_input = finance_execution.finance_input
finance_result = finance_execution.finance_result
```

No existe firma alternativa que acepte el par desprendido.

---

## 8. R-FIN-003 y frontera del productor

La exigencia de `finance_execution` en `R-FIN-003` significa únicamente:

> todo `FinanceBasicResult` consumido por Rules debe proceder de una ejecución Finance Basic físicamente íntegra.

No significa, dentro de esta unidad:

```text
P-FIN-001 = parámetro directo de R-FIN-003
```

ni materializa una nueva dependencia RDM.

La RDM no se modifica.

---

## 9. Orquestador

Los bundles quedan depurados a:

```text
FinanceCapacityRuleInputs(
    finance_execution,
    finance_evidence,
    threshold_resolution,
    parameter_evidence,
)
```

```text
FinanceSafetyMarginRuleInputs(
    finance_execution,
    finance_evidence,
    treasury_minimum_resolution,
    treasury_minimum_evidence,
    margin_resolution,
    margin_evidence,
)
```

El orquestador no construye ni repara provenance; únicamente transporta la envolvente ya válida al bridge, que vuelve a validarla.

---

## 10. Evidencia

Se conserva:

```text
finance_basic_result_ref(FinanceBasicResult)
```

como referencia determinista del resultado analítico.

La identidad individual de `P-FIN-001` queda físicamente conservada en:

```text
finance_execution.horizon_resolution.configuration_ref
```

No se añade `P-FIN-001` a `Assessment.evidence_ids` por esta unidad y no se convierte procedencia técnica en evidencia decisoria de Rules.

---

## 11. Compatibilidad

`calculate_finance_basic` permanece exportado como motor matemático de bajo nivel.

La no regresión se obtiene cerrando los consumidores verticales:

```text
raw engine result
    ≠
objeto aceptable por Rules
```

Solo una `ProvenancedFinanceBasicExecution` revalidada cruza la frontera FIN hacia Rules.

---

## 12. Materialización autorizable tras Audit 2

Si Audit 2 resulta limpio, la implementación queda limitada a:

- `eios/finance/provenance.py`;
- `eios/finance/__init__.py`;
- `eios/rules/finance.py`;
- `eios/rules/orchestrator.py`;
- tests directamente afectados y nuevos tests de provenance.

No modificar `eios/finance/engine.py`, modelos Finance, RDM, CRC ni C0.