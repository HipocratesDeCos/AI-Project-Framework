# EIOS — Negotiation Intelligence Implementation Contract

## 1. Identidad

**Documento:** Negotiation Intelligence Implementation Contract  
**Versión:** 1.1  
**Estado:** IMPLEMENTADO DOCUMENTALMENTE  
**Baseline de diseño:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/Negotiation_Intelligence_Implementation_Contract.md`

## 2. Propósito

Este contrato materializa exclusivamente el subconjunto de `Negotiation Intelligence` suficientemente definido para implementación en el Vertical MVP.

No constituye una nueva autoridad funcional ni amplía la autoridad de `05_Motor/Negotiation_Intelligence.md`.

NI determina y justifica contenido negociador. No decide, aprueba, ejecuta ni activa Strategy.

## 3. Frontera funcional

```text
Autoridades upstream
  ├─ Viability Frontier
  ├─ Scenario Engine
  ├─ Decision Twin
  ├─ Rules / Parameters
  └─ Evidence / Trace
          ↓
Negotiation Intelligence
          ↓
contenido negociador determinado y justificado
          ↓
Negotiation Ladder / capas posteriores
```

NI consume resultados y referencias autorizadas. No sustituye ni recalcula las autoridades upstream.

## 4. Entrada lógica mínima

```text
decision_context
scenario_references
viability_references
decision_twin_references
negotiable_variables
constraints_and_limits_references
evidence_references
prior_negotiation_context
```

Cada referencia debe conservar su identidad y versión de origen cuando ésta exista.

NI no duplica como autoridad los artefactos referenciados.

## 5. Identidad y versionado

El resultado NI debe estar vinculado al contexto decisional correspondiente y reutilizar las identidades autorizadas existentes.

```text
Decision_ID
Decision_Version / estado decisional
Scenario_ID, cuando aplique
Rules_Version, cuando aplique
Parameters_Version, cuando aplique
Data_Snapshot_ID, cuando aplique
```

NI no crea un sistema paralelo de `Decision Versioning`, `Scenario Versioning`, `Trace` o `input_fingerprint`.

`negotiation_result_id` identifica exclusivamente el artefacto NI. No sustituye ni duplica las identidades de las autoridades upstream.

La versión del resultado NI queda determinada por su propia identidad de artefacto y por las identidades/versiones de contexto que referencia; no se crea una segunda autoridad de versionado mediante un campo semánticamente ambiguo.

Un nuevo contexto materialmente diferente genera un nuevo resultado NI; no se sobrescribe retrospectivamente un resultado histórico.

## 6. Contenido negociador

La salida principal es contenido negociador determinado y justificado. Puede incluir, cuando proceda:

```text
objective
opening_request
moves
concessions
counterparts / counterpart_requirements
tradeoffs
packages
alternatives
fallback
conditions
convenience_analysis
```

Estos elementos representan contenido sustantivo. No constituyen una Ladder.

## 7. Epistemología

Toda conclusión material debe conservar su naturaleza cuando resulte relevante:

```text
FACT
OBSERVATION
INFERENCE
ESTIMATE
HYPOTHESIS
RECOMMENDATION
```

La confianza/incertidumbre se conserva como atributo de la afirmación, fundamento o conclusión correspondiente cuando aplique.

No se utiliza un `confidence_score` global como sustituto de la naturaleza epistemológica.

## 8. Justificación y evidencia

El contenido negociador material debe poder rastrearse hasta sus fundamentos.

```text
Evidence / Data
      ↓
Rules / Parameters
      ↓
Scenario / Result
      ↓
Decision Twin / Consequence
      ↓
NI reasoning
      ↓
Negotiation content
```

NI conserva referencias a las fuentes; no redefine Evidence, Rules, Parameters, Scenario Engine, Decision Twin, C0 o Trace.

La calificación epistemológica y su confianza, cuando existan, pertenecen a una única `NIAssertion` asociada al fundamento o conclusión correspondiente. No deben duplicarse en estructuras paralelas del resultado.

Una inferencia no se convierte en hecho por estar respaldada por una referencia.

## 9. Viability Frontier

NI puede consumir resultados y límites de `Viability Frontier` para analizar conveniencia negociadora.

No puede:

- determinar viabilidad;
- crear una frontera;
- modificar una frontera;
- ampliar o reducir límites de viabilidad.

```text
Viability Frontier
        ↓
resultado / límite autorizado
        ↓
NI
        ↓
interpretación negociadora
```

## 10. Scenario Engine

NI puede producir hipótesis, alternativas o necesidades de evaluación.

No crea ni versiona escenarios formales.

Cuando una hipótesis requiera evaluación formal:

```text
NI
 ↓
hipótesis negociadora
 ↓
Scenario Engine
 ↓
Scenario_ID
 ↓
evaluación
 ↓
resultado
 ↓
NI
```

`Scenario_ID` conserva la identidad del Scenario Engine y no se redefine dentro de NI.

## 11. Decision Twin

NI consume resultados y consecuencias del Decision Twin.

No reproduce, recalcula, modifica ni sustituye el Twin.

```text
Decision Twin
      ↓
resultado / consecuencia
      ↓
NI
      ↓
interpretación negociadora
```

## 12. Negotiation Ladder

La frontera es inmutable:

> Negotiation Intelligence determina el contenido negociador; Negotiation Ladder estructura, representa y ordena secuencialmente ese contenido.

Por tanto, este contrato no concede a NI autoridad para crear o gobernar:

```text
ladder_step
sequence_order
transitions
routes
structural ladder levels
```

NI puede determinar sustantivamente movimientos, concesiones, contraprestaciones, condiciones y fallback; Ladder los estructura posteriormente.

## 13. Límites y restricciones

NI puede utilizar límites y restricciones procedentes de fuentes autorizadas y determinar sus implicaciones negociadoras.

No puede:

- crear límites;
- determinar límites;
- modificar límites;
- ampliar límites;
- reducir límites;
- sustituir su autoridad de origen.

Un `walk-away` generado o representado por capas posteriores debe conservar el límite autorizado que lo fundamenta.

## 14. CRC y resolución

NI produce contenido y razonamiento negociador.

No resuelve conflictos entre autoridades ni sustituye `CRC` o la capa de resolución correspondiente.

```text
NI
 ↓
contenido / recomendación
 ↓
resolución posterior
 ↓
autoridad decisional
```

## 15. Strategy y decisión empresarial

```text
Negotiation content ≠ Strategy
Recommendation ≠ Business Decision
Business Decision ≠ Execution
```

El contrato no contiene estados ni acciones que impliquen aprobación empresarial, ejecución, activación de Strategy o decisión humana.

## 16. Salida

La salida mínima de implementación es:

```text
negotiation_result_id
context_references
negotiation_content
justification
traceability_references
```

La justificación utiliza `NIAssertion` como unidad única de contenido epistemológico cuando proceda, incluyendo `epistemic_type`, `confidence` y `source_references` en esa misma unidad.

`negotiation_result_id` identifica el artefacto NI y no sustituye `Decision_ID`, `Scenario_ID` ni ninguna identidad de autoridad upstream.

## 17. Invariantes físicos

1. NI solo determina contenido negociador dentro de sus autoridades.
2. Todo contenido material debe ser justificable.
3. Las referencias upstream conservan su autoridad de origen.
4. NI no crea límites.
5. NI no modifica límites.
6. NI no determina viabilidad.
7. NI no crea escenarios formales.
8. NI no recalcula Decision Twin.
9. NI no redefine Decision Versioning.
10. NI no redefine C0, Trace ni `input_fingerprint`.
11. NI no estructura Ladder.
12. NI no resuelve conflictos de autoridad.
13. NI no gobierna Strategy.
14. NI no aprueba.
15. NI no decide.
16. NI no ejecuta.
17. Hecho, observación, inferencia, estimación e hipótesis permanecen diferenciados.
18. Un nuevo resultado no sobrescribe un resultado histórico.
19. Una hipótesis negociadora no equivale a un escenario formal.
20. Una recomendación no equivale a una decisión empresarial.
21. La calificación epistemológica y la confianza de una afirmación no se duplican en estructuras paralelas del resultado.
22. NI no crea un sistema paralelo de versionado mediante una identidad ambigua distinta de `negotiation_result_id` y las referencias upstream.

## 18. Exclusiones

Quedan fuera de este contrato:

- generación/evaluación formal de escenarios;
- determinación de viabilidad;
- creación/modificación de reglas o parámetros;
- modificación de límites;
- representación estructural de Ladder;
- resolución de conflictos de autoridad;
- aprobación;
- decisión empresarial;
- ejecución;
- gobierno o activación de Strategy.

## 19. Criterios mínimos de test

El contrato deberá comprobar como mínimo:

1. identidad y versionado coherentes;
2. ausencia de mutación de resultados históricos;
3. conservación de referencias upstream;
4. rechazo de creación/modificación de límites;
5. rechazo de escenarios formales creados por NI;
6. rechazo de recalculación/modificación de Decision Twin;
7. separación NI/Ladder;
8. separación recomendación/decisión;
9. separación epistemológica;
10. trazabilidad completa del contenido material;
11. ausencia de segundo fingerprint/Trace;
12. determinismo para entradas y versiones idénticas;
13. ausencia de duplicación de confianza/calificación epistemológica;
14. ausencia de identidad paralela de versionado.

## 20. Cierre de autoridad

Este contrato implementa la autoridad de `05_Motor/Negotiation_Intelligence.md` sin ampliarla.

Cualquier requisito que introduzca autoridad sobre viabilidad, escenarios, Decision Twin, Ladder, CRC, Strategy o decisión empresarial deberá resolverse mediante la autoridad documental correspondiente y no mediante este contrato.
