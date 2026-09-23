# EIOS — ROT002 Parameter Configuration Evidence Binding Authority v0.1

**Baseline de autorización:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Estado:** AUTORIZADO  
**Gate:** `ROT002-AW-EVID-G01`  
**Ámbito:** binding Evidence ↔ ResolvedConfiguration(P-ROT-001)

## 1. Autoridad humana

Se autoriza expresamente el binding y la semántica propuestos en:

`01_Modelo/ROT002_Parameter_Configuration_Evidence_Binding_Proposal_v0.1.md`.

La autorización cubre exclusivamente la demostración técnica de que una `Evidence` del `DecisionInputPackage` corresponde a la resolución concreta de `P-ROT-001`.

## 2. Binding canónico

Queda autorizado:

```text
Evidence.source_ref
==
ResolvedConfiguration(P-ROT-001).configuration_ref
```

La igualdad identifica la Evidence aplicable a esa configuración resuelta concreta.

## 3. Suficiencia mínima

La configuración queda demostrada para esta frontera cuando existe al menos una Evidence vinculada que cumple:

```text
evidence.source_ref == resolution.configuration_ref
evidence.state == "DEMONSTRATED"
evidence.demonstration_ref is not None
```

`demonstration_ref` mantiene la semántica ya establecida por C0/Evidence Contract.

## 4. GAP y ausencia

No demuestran configuración:

- ausencia de Evidence vinculada;
- Evidence con `state = GAP`;
- `configuration_ref` sin Evidence;
- Configuration existente sin Evidence correspondiente.

No se introduce fallback.

## 5. source_type

No se autoriza un literal nuevo ni obligatorio de `source_type`.

El campo debe seguir siendo válido conforme a C0, pero esta autoridad no crea un catálogo de fuentes.

## 6. captured_at

No se autoriza:

```text
Evidence.captured_at == ResolvedConfiguration.effective_at.date()
```

ni otra equivalencia temporal adicional.

La vigencia de la configuración se valida por:

```text
Configuration.valid_from
Configuration.valid_to
ResolvedConfiguration.effective_at
DecisionInputPackage.effective_at
```

## 7. demonstration_ref

No se exige:

```text
Evidence.demonstration_ref == configuration_ref
```

Solo se conserva el invariante C0:

```text
DEMONSTRATED → demonstration_ref requerido
```

## 8. Evidencias múltiples

La suficiencia mínima se cumple con al menos una Evidence vinculada y DEMONSTRATED.

Esta autoridad no redefine la resolución general de contradicciones entre evidencias; cualquier contradicción material debe conservarse conforme a la autoridad correspondiente.

## 9. Orden de validación

El binding solo puede aplicarse después de validar:

```text
resolution.parameter_id == "P-ROT-001"
resolution.company_id == DIP.company_id
resolution.parameters_version == DIP.context.parameters_version
resolution.effective_at == DIP.effective_at
configuration vigente
```

## 10. No alcance

Esta autoridad no crea:

- nuevo EvidenceState;
- nuevo EvidenceValidationStatus;
- nuevo source_type;
- nuevo parámetro;
- nueva regla;
- Assessment;
- CRC;
- excepción;
- decisión;
- score/ranking.

## 11. Gate

```text
ROT002-AW-EVID-G01 → CLOSED
```

## 12. Estado

**ROT002-AW-EVID-G01 — AUTORIZADO Y CERRADO EN SU ALCANCE.**
