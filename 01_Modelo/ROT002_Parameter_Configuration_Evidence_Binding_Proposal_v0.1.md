# EIOS — ROT002 Parameter Configuration Evidence Binding Proposal v0.1

**Baseline:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA / NO VIGENTE  
**Gate:** `ROT002-AW-EVID-G01`  
**Ámbito:** binding Evidence ↔ ResolvedConfiguration(P-ROT-001)

## 1. Problema

La autoridad de P-ROT-001 exige:

```text
ResolvedConfiguration(P-ROT-001)
+
Evidence de configuración
```

El Evidence Contract define:

```text
Evidence
├── evidence_id
├── source_type
├── source_ref
├── captured_at
├── state
└── demonstration_ref
```

pero no determina qué relación concreta prueba que una Evidence corresponde a una configuración de parámetro específica.

No debe inventarse esa relación dentro del código.

## 2. Propuesta de binding mínimo

Se propone utilizar la referencia técnica ya existente:

```text
ResolvedConfiguration.configuration_ref
```

como referencia concreta de origen en C0:

```text
Evidence.source_ref
```

La relación propuesta es:

```text
Evidence.source_ref
==
ResolvedConfiguration(P-ROT-001).configuration_ref
```

Esta igualdad identifica la Evidence aplicable a esa resolución concreta.

## 3. Suficiencia mínima propuesta

La configuración se considera evidenciada para esta frontera técnica cuando existe al menos una Evidence del DIP que cumple simultáneamente:

```text
evidence.source_ref == resolution.configuration_ref
evidence.state == DEMONSTRATED
evidence.demonstration_ref != None
```

La última condición ya es un invariante de C0 para Evidence DEMONSTRATED.

No se crea un nuevo estado de Evidence.

## 4. Ausencia de evidencia

Si no existe ninguna Evidence que cumpla el binding:

```text
configuration evidence = NOT DEMONSTRATED
```

La frontera ROT no puede producir una ventana autorizada concluyente.

No se sustituye por:

- `configuration_ref` sin Evidence;
- existencia de Configuration;
- valor por defecto;
- otra evidencia no vinculada.

## 5. source_type

No se propone un literal obligatorio de `source_type`.

Motivo:

- Evidence Contract no define un catálogo universal;
- crear `PARAMETER_CONFIGURATION` u otro literal sería autoridad adicional innecesaria;
- `source_ref` ya identifica la resolución concreta.

`source_type` deberá seguir siendo válido conforme a C0, pero esta autoridad no le asigna un valor nuevo.

## 6. captured_at

No se propone igualdad:

```text
Evidence.captured_at == DIP.effective_at.date()
```

ni otra política temporal adicional.

La vigencia de la configuración ya se valida mediante:

```text
Configuration.valid_from
Configuration.valid_to
ResolvedConfiguration.effective_at
DIP.effective_at
```

Una futura autoridad podrá imponer temporalidad adicional a Evidence si fuese necesaria.

## 7. demonstration_ref

`demonstration_ref` permanece bajo Evidence Contract.

Esta propuesta no prescribe su contenido, salvo el requisito físico existente:

```text
DEMONSTRATED → demonstration_ref requerido
```

No se propone:

```text
demonstration_ref == configuration_ref
```

## 8. Evidencias múltiples

Si existen varias evidencias con el mismo `source_ref`, la frontera puede considerar satisfecho el requisito si al menos una es `DEMONSTRATED` y válida conforme a C0.

Esta propuesta no crea una regla general de resolución de contradicciones entre evidencias.

Si otra autoridad detecta contradicción material, debe conservarse conforme al Evidence Contract.

## 9. Scope

La relación solo se utiliza después de haber validado:

```text
resolution.parameter_id == P-ROT-001
resolution.company_id == DIP.company_id
resolution.parameters_version == DIP.context.parameters_version
resolution.effective_at == DIP.effective_at
configuration vigente
```

Por tanto, el binding no sustituye las validaciones de identidad/configuración.

## 10. No alcance

No se autoriza:

- nuevo source_type;
- nuevo EvidenceState;
- nuevo EvidenceValidationStatus;
- nueva tabla;
- nuevo parámetro;
- nuevo rule result;
- Assessment;
- CRC;
- excepciones;
- ranking/scoring;
- inferencia de ventas.

## 11. Regla propuesta

```text
matching_evidence =
    [e for e in DIP.evidence
     if e.source_ref == resolution.configuration_ref]

configuration_evidenced =
    any(e.state == "DEMONSTRATED"
        and e.demonstration_ref is not None
        for e in matching_evidence)
```

Esta expresión describe exclusivamente el binding/suficiencia mínima propuestos.

## 12. Decisión humana requerida

Para cerrar `ROT002-AW-EVID-G01` se requiere aprobar o corregir expresamente:

1. `Evidence.source_ref == ResolvedConfiguration.configuration_ref` como binding canónico;
2. al menos una Evidence `DEMONSTRATED` vinculada como suficiencia mínima;
3. no imponer un `source_type` nuevo;
4. no imponer igualdad `captured_at == effective_at`;
5. mantener `demonstration_ref` bajo el contrato C0 existente.

## 13. Estado

**ROT002 Parameter Configuration Evidence Binding Proposal v0.1 — PROPUESTA / NO VIGENTE.**
