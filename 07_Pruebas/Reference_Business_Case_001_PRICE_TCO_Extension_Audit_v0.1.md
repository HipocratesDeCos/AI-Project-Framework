# EIOS — Reference Business Case 001 · PRICE + TCO Extension Audit v0.1

**Baseline:** `main @ fdc9d414fa9bc7b878642634d7fa2ca27d8e4cc5`  
**Fecha:** 23/09/2026  
**Estado:** MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Propósito

Ampliar `REF-BUSINESS-001` desde:

```text
QTG → C0
```

hasta:

```text
QTG → PRICE → TCO → C0
```

utilizando exclusivamente builders provenance-safe ya existentes.

No se modifica código de producción.

## 2. PRICE

Se construye un `PriceIntelligenceInput` ligado a la PurchaseOperation y al
DecisionContext exactos del bundle.

Material sintético de referencia:

- dos transacciones históricas sintéticas;
- mismo article_id que la operación;
- cantidades 8 y 12;
- precios unitarios 19,50 EUR y 21,00 EUR;
- evidencias validadas;
- temporalidad declarada ELIGIBLE;
- representatividad demostrada para el ensayo;
- suficiencia explícita y ligada a referencias/trazas.

No se suministra un `PriceIntelligenceResult` desprendido.

La capacidad entra mediante:

`build_provenanced_price_invoker(...)`

El resultado esperado es una capacidad PRICE `COMPLETED`.

## 3. TCO

Se construye `TCOInput` desde la PurchaseOperation exacta del caso.

No se suministra un `TCOResult` desprendido.

La capacidad entra mediante:

`build_provenanced_tco_invoker(...)`

Sin componentes atribuibles incompletos, el resultado esperado es TCO
`COMPLETED`.

## 4. C0

Se mantiene la cadena cerrada en la unidad anterior:

```text
DecisionEvidenceSufficiencyProducer
→ R-DAT-003
→ Assessment
→ Trace
→ AssessmentTraceBinding
→ build_provenanced_rules_engine_c0_invoker
```

No vuelve a introducirse ningún stub.

## 5. QTG

La extensión no altera el material QTG físico.

Se conserva deliberadamente:

```text
status     = NO_APTO
confidence = BAJA
```

La presencia de PRICE/TCO/C0 completos no transforma ni oculta el resultado
de calidad.

## 6. Outcome esperado

La frontera genérica MVP ejecuta:

```text
PRICE → TCO → C0
```

y la fachada de simulación conserva QTG delante:

```text
QTG → PRICE → TCO → C0
```

El `ExecutionOutcome` técnico puede ser `COMPLETED` porque las capacidades
MVP invocadas han terminado, aunque el resultado funcional QTG ligado al caso
sea `NO_APTO`.

Esto no constituye aprobación de compra ni decisión empresarial.

## 7. Salvaguardas

Se mantienen:

- `case_kind = REFERENCE_OPERATIONAL_SIMULATION`;
- `material_nature = SYNTHETIC`;
- `qtg_mode_policy = SYNTHETIC_TEST_ONLY`;
- `operational_path = FORBIDDEN`;
- `operational_effect = false`;
- `decision_authority = false`.

PRICE y TCO reciben copias ligadas al runtime exacto.

Una mutación de PurchaseOperation/DecisionContext debe seguir fallando cerrado
en sus builders especializados.

## 8. No autorizado

Esta unidad no:

- añade resultados raw a `run_mvp_execution`;
- modifica PRICE;
- modifica TCO;
- modifica QTG;
- modifica C0;
- crea nueva semántica de precios;
- crea nueva semántica de coste;
- declara que las referencias sintéticas representan mercado real;
- promociona el caso a operacional.

## 9. Materialización

Se modifica únicamente:

- `tests/test_reference_business_case_001.py`;

y se añade este documento.

## 10. Criterio de cierre

CI debe demostrar simultáneamente:

- PRICE provenance-safe `COMPLETED`;
- TCO provenance-safe `COMPLETED`;
- C0 provenance-safe `COMPLETED`;
- orden terminal `QTG → PRICE → TCO → C0`;
- outcome técnico `COMPLETED`;
- QTG sigue `NO_APTO/BAJA`;
- efecto operacional y autoridad decisional permanecen falsos.

## 11. Continuidad

Después de este cierre, las siguientes expansiones legítimas serán:

1. Supplier Risk/Value;
2. Scenario/VF;
3. Decision Twin;
4. Negotiation Intelligence;
5. Negotiation Ladder.

Scenario Coordination deberá revisarse especialmente porque el facade Vertical
actual contiene un invoker interno que explícitamente no certifica por sí solo
provenance. No se reutilizará esa vía como si fuese una garantía positiva.
