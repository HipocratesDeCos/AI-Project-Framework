# EIOS — Profitability Provenance Boundary Contract v0.1

**Baseline:** `main @ d3b72e33752bc5111f89f4112f461f505b805247`  
**Autoridad:** `MGE-AUTH v0.1` + `Profitability Core Technical Contract v0.1`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — LISTO PARA MATERIALIZACIÓN

## 1. Propósito

Cerrar la frontera de reutilización de Profitability Core antes de cualquier consumidor downstream.

El motor bajo nivel:

```python
calculate_profitability(payload: ProfitabilityInput) -> ProfitabilityResult
```

permanece válido para cálculo interno y tests.

La frontera de reutilización no debe aceptar un `ProfitabilityResult` desprendido sin demostrar qué `ProfitabilityInput` lo originó.

## 2. Riesgo objetivo

Un resultado desprendido podría:

- pertenecer a otra decisión;
- pertenecer a otro escenario;
- pertenecer a otro snapshot;
- corresponder a otras bases autorizadas;
- estar manipulado;
- haber sido calculado antes de una mutación externa del input;
- conservar números correctos pero provenance incorrecta.

Por tanto:

```text
ProfitabilityResult alone != provenance-safe execution
```

## 3. Frontera propuesta

Se introduce:

```text
ProvenancedProfitabilityExecution
├── profitability_input: ProfitabilityInput
└── profitability_result: ProfitabilityResult
```

API pública:

```python
run_provenanced_profitability(
    profitability_input: ProfitabilityInput,
) -> ProvenancedProfitabilityExecution
```

y:

```python
validate_provenanced_profitability_execution(
    execution: ProvenancedProfitabilityExecution,
) -> None
```

## 4. Ejecución

`run_provenanced_profitability` debe:

1. exigir tipo exacto/compatible `ProfitabilityInput`;
2. hacer snapshot profundo del input;
3. ejecutar `calculate_profitability(snapshot)`;
4. devolver input snapshot + resultado calculado;
5. no aceptar `ProfitabilityResult` aportado externamente.

No existe factory alternativa que acepte result desprendido.

## 5. Revalidación

`validate_provenanced_profitability_execution` debe:

1. exigir `ProvenancedProfitabilityExecution`;
2. volver a ejecutar `calculate_profitability(execution.profitability_input)`;
3. exigir igualdad exacta con `execution.profitability_result`.

Cualquier divergencia:

```text
→ ProfitabilityProvenanceError
```

No se corrige ni se normaliza silenciosamente.

## 6. Inmutabilidad

La ejecución se materializa como `dataclass(frozen=True)`.

La factory realiza copia profunda del input antes de calcular.

Mutaciones externas posteriores sobre objetos originales no deben modificar la ejecución congelada.

## 7. Scope de provenance

Esta frontera demuestra únicamente:

```text
ProfitabilityInput snapshot
        ↓
calculate_profitability
        ↓
ProfitabilityResult exacto
```

No demuestra por sí sola que:

- una fuente ERP sea verdadera;
- una base económica esté autorizada fuera de lo declarado por su `authority_ref`;
- un Rule outcome sea correcto;
- una decisión humana sea correcta.

La validez económica de las bases sigue dependiendo de sus contratos upstream.

## 8. Relación con Rules

Una futura frontera Rules MGE no debe aceptar:

```text
ProfitabilityResult
```

como argumento público desprendido.

Deberá aceptar una ejecución provenance-safe o reconstruir/revalidar desde `ProfitabilityInput`.

Este contrato no implementa ni autoriza R-MGE.

## 9. No-alcance

- Rules;
- CRC;
- parámetros MGE;
- adapters PRICE/TCO;
- persistencia;
- SQL;
- I/O;
- red;
- browser;
- selección de bases.

## 10. Tests obligatorios

1. happy path;
2. snapshot profundo;
3. resultado exacto;
4. revalidación válida;
5. tipo de input incorrecto;
6. tipo de execution incorrecto;
7. resultado manipulado;
8. input interno manipulado mediante bypass;
9. bases internas manipuladas mediante bypass;
10. no aceptación de result desprendido;
11. sin imports Rules/CRC/PRICE/TCO;
12. sin I/O/clock.

## 11. Criterio de cierre

La unidad puede materializarse si Audit 2 confirma:

- no duplica autoridad MGE;
- no crea adapters;
- no ejecuta Rules;
- recomputa exactamente el core;
- protege contra resultado desprendido;
- no introduce estado externo.
