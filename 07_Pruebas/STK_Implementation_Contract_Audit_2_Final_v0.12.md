# EIOS — STK Implementation Contract · Audit 2 Final v0.12

**Estado:** NO SUPERADA — DEPURACIÓN M1…M4 REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.13  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.13 resuelve L1…L5 y conserva resueltos A…K. La auditoría independiente se ha ejecutado sobre el contrato resultante, cruzándolo con STK-M09, STK-M10, STK-M05 y STK-M08, además de C0, parametrización y fronteras de reglas.

Persisten **4 bloqueos técnicos finales**. No requieren nueva decisión empresarial.

**DICTAMEN:** NO CERRAR v0.13. Resolver M1…M4 y repetir Audit 2 Final completa.

---

## 2. M1 — `CONFLICTING_DATA` necesita una referencia física a la contradicción preservada

**Tipo:** BLOQUEANTE M10.

El contrato prohíbe la resolución heurística y afirma que los conflictos conservan referencias, pero no define una representación material que permita a `models.py` exigirla.

STK-M10 obliga a preservar todas las evidencias implicadas y reconstruir artículo, variable, ámbito, momento comparable, fuentes, valores/estados, fechas, versiones, módulos/evaluaciones afectados y, cuando exista resolución posterior, la autoridad aplicada.

**Corrección requerida:** introducir una referencia de incidencia/contradicción equivalente a:

```text
DataIssueRef
├── issue_id: str
├── issue_type: MISSING_DATA | CONTRADICTION
├── issue_record_ref: str
├── evidence_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

El `issue_record_ref` apunta a un registro/artefacto trazable que conserva el detalle M09/M10; STK no duplica persistencia ni resuelve la contradicción.

Reglas mínimas:

- todo resultado `CONFLICTING_DATA` conserva al menos una incidencia `CONTRADICTION`;
- una contradicción no resuelta exige al menos dos `evidence_refs` distintos;
- un resultado `UNKNOWN / NOT_EVIDENCED` puede conservar una incidencia `MISSING_DATA` cuando exista registro de la ausencia;
- una resolución externa no elimina la incidencia histórica: la nueva evaluación referencia autoridad/resolución aguas arriba;
- la incidencia no constituye conflicto CRC ni contradicción documental.

---

## 3. M2 — Forecast no evidenciado no puede exigir una fecha fuente inventada

**Tipo:** BLOQUEANTE M09 / STATE↔PAYLOAD.

`AuthorizedForecastRate.reference_date` sigue siendo obligatoria en v0.13. Si el forecast esperado existe conceptualmente pero falta su fecha de referencia o no puede verificarse, el contrato obligaría a inventar una fecha para representar `UNKNOWN / NOT_EVIDENCED`.

**Corrección requerida:**

- `AuthorizedForecastRate.reference_date: date | null`;
- `KNOWN` exige fecha no nula y coherente con aplicabilidad;
- estado no determinado puede dejarla nula y conservar `DataIssueRef`/trazas;
- `DemandRateResult.reference_date` puede seguir siendo la fecha de referencia del cálculo cuando sea conocida por contexto, pero nunca debe copiar una fecha fuente inexistente como si estuviera evidenciada.

---

## 4. M3 — `NO_APLICABLE` M08 exige exclusión demostrada; ausencia produce `NO_VERIFICABLE`

**Tipo:** BLOQUEANTE M08/M09.

v0.13 permite campos nulos en `NO_VERIFICABLE`, pero no cierra el invariante de `NO_APLICABLE`. Sin él, una implementación podría clasificar como no aplicable un pedido cuyo artículo, fecha, cantidad o estado simplemente faltan.

STK-M08 y M09 son explícitos: `NO_APLICABLE` requiere evidencia de que el pedido no corresponde, queda fuera de horizonte, no conserva cantidad pendiente aplicable o no existe exceso; la falta de evidencia que impide determinar esa exclusión es `NO_VERIFICABLE`.

**Corrección requerida:**

- `NO_APLICABLE` solo cuando la causa de exclusión puede demostrarse con campos/evidencia suficientes;
- conservar `applicability_source_ref` y trazas de la causa;
- si la ausencia impide decidir aplicabilidad → `NO_VERIFICABLE`;
- `APLICABLE_Y_VALIDADA` exige `ExcessResult.state == EXCESS` y todos los requisitos de cantidad/fecha/evidencia;
- un exceso `NO_EXCESS/WITHIN_TOLERANCE` hace M08 no aplicable, nunca absorción validada.

---

## 5. M4 — Incertidumbre fuera del horizonte no debe contaminar una proyección a la que no aplica

**Tipo:** BLOQUEANTE M05/M09.

v0.13 establece que movimientos no determinados contaminan desde su fecha conocida y, sin fecha, desde `evaluation_date`. Falta cerrar el caso en que la **fecha está evidenciada y está fuera del horizonte**, pero la cantidad u otro atributo permanece desconocido.

Un evento cuya fecha demostrada está después de `horizon_end` no puede afectar el saldo de ese horizonte; propagar su incertidumbre dentro de la proyección sería tan incorrecto como omitir una incertidumbre que sí puede afectarla.

**Corrección requerida:** el gate temporal se evalúa antes de propagar incertidumbre cuantitativa:

- `effective_date > horizon_end` evidenciada → movimiento fuera del horizonte; no contribuye ni contamina esa proyección;
- `effective_date <= evaluation_date` → no es movimiento futuro de M05 v0.1 y no contribuye al horizonte futuro; se conserva trazable sin roll-forward;
- `evaluation_date < effective_date <= horizon_end` → si faltan cantidad/evidencia, la incertidumbre se propaga desde esa fecha;
- `effective_date` no demostrable → la incertidumbre puede afectar desde `evaluation_date` y se propaga conservadoramente;
- STK no desplaza fechas ni convierte automáticamente el registro fuente en `NOT_APPLICABLE`; el resultado de proyección registra su exclusión temporal trazable.

---

## 6. Verificaciones sin nuevo bloqueo

- L1…L5: resueltos en v0.13.
- R-STK-001: no se inventa una dependencia DATA/COMPONENT pendiente en RDM.
- R-STK-002: la cobertura proyectada no se inventa; M04 v0.1 permanece sobre stock disponible actual hasta autoridad adicional.
- M01…M03: reconstruibilidad preservada.
- M04: cero evidenciado → UNBOUNDED.
- M05/M06: horizonte `PYE-001`, cutoff diario, proveedor/origen y supply identity preservados.
- M07: composición por punto, autoridad/versiones y ramas exclusivas preservadas.
- M08: horizonte común, ledger aislado y reconciliación opening/M05/ledger preservados.
- C0/Rules/CRC/MED: fronteras intactas.

---

## 7. Resultado

- A…L: resueltos.
- M1…M4: abiertos en v0.13.

**Siguiente paso:** DEPURAR v0.14 → repetir Audit 2 Final completa.