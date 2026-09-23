# EIOS — Viability Frontier Minimal Provenance Producer Authority v0.1

**Baseline:** `main @ 45aae65ee7b8ec793229eef136bccdcecb6f49bc`  
**Fecha:** 23/09/2026  
**Estado:** 🔒 AUTORIZADO — VIGENTE

## 1. Objetivo

Materializar el primer productor físico provenance-safe de consecuencias de Viability Frontier sin inferir H/K/U/S desde:

- R0/R1/R2/R3;
- severidad;
- active_result;
- número de reglas activas;
- GAP;
- dominio funcional.

El productor consumirá exclusivamente `AssessmentTraceBinding` previamente validado.

## 2. Catálogo mínimo VF v0.1

Se autoriza proponer únicamente estas tres consecuencias:

```text
R-FIN-001 → H
R-PAG-002 → K
R-DAT-003 → U
```

Toda regla no listada queda fuera del productor VF v0.1.

Ausencia de mapping ≠ S.

## 3. R-FIN-001 → H

Autoridad documental existente:

- condición: incapacidad prevista de atender pagos;
- resultado: NO COMPRAR;
- efecto: R0 / CRÍTICA;
- bloqueo: Sí;
- explicación: la compra no debe realizarse si compromete obligaciones de pago.

Semántica propuesta:

```text
Assessment EVALUABLE / TRUE
→ FrontierAssessment(
    frontier_class=H,
    evaluated=True,
    satisfied=False,
    solvable=False
)

Assessment EVALUABLE / FALSE
→ FrontierAssessment(
    frontier_class=H,
    evaluated=True,
    satisfied=True,
    solvable=False
)

Assessment NOT_EVALUABLE
→ FrontierAssessment(
    frontier_class=H,
    evaluated=False,
    satisfied=None,
    solvable=None,
    materially_insufficient=True
)
```

`solvable` no participa en la lógica H; se fija `False` solo como valor técnico estable cuando H está evaluada.

## 4. R-PAG-002 → K

Autoridad documental existente:

> La operación puede ser viable únicamente si se amplía el plazo de pago.

Resultado:

```text
COMPRAR CONDICIONADO
```

Semántica propuesta:

```text
Assessment EVALUABLE / TRUE
→ K evaluada, incumplida, solucionable
→ satisfied=False
→ solvable=True

Assessment EVALUABLE / FALSE
→ K evaluada y satisfecha/no activada
→ satisfied=True
→ solvable=True

Assessment NOT_EVALUABLE
→ K no evaluada
→ materially_insufficient=True
```

Para K satisfecha, `solvable=True` es un requisito técnico del carrier y no afirma que exista una remediación pendiente; el campo solo es decisivo cuando `satisfied=False`.

## 5. R-DAT-003 → U

Autoridad documental existente:

> No existe información suficiente para realizar una evaluación fiable.

Semántica propuesta:

```text
Assessment EVALUABLE / TRUE
→ U material
→ materially_insufficient=True

Assessment EVALUABLE / FALSE
→ no se produce consecuencia U

Assessment NOT_EVALUABLE
→ U material
→ materially_insufficient=True
```

La ausencia de una consecuencia U cuando DAT003 es FALSE no elimina el Assessment original ni su Trace; simplemente no activa una función de frontera U.

## 6. Productor

API propuesta:

```text
produce_frontier_assessments(
    purchase,
    context,
    bindings
) -> tuple[FrontierAssessment, ...]
```

Proceso:

1. snapshot de purchase/context/bindings;
2. validar cada binding mediante `validate_assessment_trace_binding(...)`;
3. rechazar rule_id duplicados;
4. aplicar únicamente el catálogo explícito v0.1;
5. construir `FrontierAssessment` con:
   - assessment_id derivado de `assessment_fingerprint`;
   - decision_id;
   - scenario_id;
   - frontier_class autorizada;
   - evaluated;
   - satisfied;
   - solvable;
   - rule_id;
   - trace_reference = Trace.trace_id;
   - materially_insufficient;
   - authority_conflict=False;
6. no producir consecuencias para reglas no autorizadas.

## 7. Identidad

`assessment_id` técnico:

```text
vf:{rule_id}:{assessment_fingerprint}
```

No sustituye al Trace ni crea nueva autoridad normativa.

## 8. ViabilityResult provenance-safe

API propuesta:

```text
evaluate_provenanced_viability(
    purchase,
    context,
    bindings
) -> ViabilityResult
```

Debe:

1. producir internamente las consecuencias VF;
2. llamar `evaluate_viability(...)`;
3. pasar `rules_version`, `parameters_version`, `data_snapshot_id` del contexto exacto;
4. no aceptar `FrontierAssessment` libre;
5. no aceptar `ViabilityResult` desprendido.

## 9. Recuperación Stage 2

Tras materialización y audit:

- `ViabilityResult` producido por esta frontera puede convertirse en input legítimo del bridge VF→Scenario;
- la finalización pública Stage 2 provenance-safe podrá reabrirse únicamente desde:
  `AssessmentTraceBinding + evaluate_provenanced_viability`;
- no se restaurará ningún bypass que acepte `ViabilityResult` arbitrario.

## 10. No alcance

No se autoriza mapping VF para:

- FIN002;
- FIN003;
- STK;
- ROT;
- PRICE;
- MGE;
- PROV;
- COM;
- HIS;
- ENT;
- PAG001;
- cualquier regla no listada.

Tampoco se autoriza:

- score;
- peso;
- mayoría;
- compensación;
- inferencia R0→H general;
- inferencia R1→K general;
- S por defecto;
- conflicto automático;
- recomendación o decisión.

## 11. Tests consolidados

1. FIN001 TRUE → H incumplida;
2. FIN001 FALSE → H satisfecha;
3. FIN001 NOT_EVALUABLE → H no evaluada/materialmente insuficiente;
4. PAG002 TRUE → K incumplida/solucionable;
5. PAG002 FALSE → K satisfecha;
6. PAG002 NOT_EVALUABLE → K no evaluada/materialmente insuficiente;
7. DAT003 TRUE → U;
8. DAT003 FALSE → no U;
9. DAT003 NOT_EVALUABLE → U;
10. rule no catalogada → ignorada para VF;
11. binding manipulado → error técnico;
12. Trace legacy → error técnico;
13. duplicados → error;
14. versiones/contexto ajeno → error;
15. H domina U/K;
16. U domina K;
17. K produce VIABLE_CON_CONDICIONES;
18. ausencia de consecuencias activas → VIABLE;
19. ViabilityResult conserva versiones/snapshot;
20. no API pública que acepte FrontierAssessment libre como provenance-safe.

## 12. Efecto de una autorización única

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR
   - catálogo VF mínimo
   - productor provenance-safe
   - evaluate_provenanced_viability
   - tests
   - reapertura controlada Stage2
→ CI
→ merge
→ CI main
```

## 13. Autorización humana

Autorizado expresamente el 23/09/2026 como autoridad mínima VF v0.1.

La autorización comprende exclusivamente:

- R-FIN-001 → H;
- R-PAG-002 → K;
- R-DAT-003 → U;
- productor desde AssessmentTraceBinding;
- evaluate_provenanced_viability;
- reapertura Stage 2 únicamente mediante reconstrucción interna de VF.

**VF MINIMAL PROVENANCE PRODUCER v0.1 — 🔒 AUTORIZADO / VIGENTE.**
