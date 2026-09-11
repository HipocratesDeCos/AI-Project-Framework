# EIOS — STK Implementation Contract · Audit 2 Final v0.6

**Estado:** NO SUPERADA — DEPURACIÓN FINAL DE IDENTIDAD REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.7  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.7 resuelve A1…A9, B1…B13, C1…C7, D1…D4, E1…E3 y F1…F3. La auditoría independiente contra el modelo físico C0 y la disciplina de versionado detecta **2 omisiones de identidad**, ambas técnicas y sin impacto en política empresarial.

**DICTAMEN:** NO CERRAR v0.7. Corregir G1…G2 y repetir Audit 2 Final.

---

## 2. G1 — `rules_version` omitido de `StockResultIdentity`

**Tipo:** BLOQUEANTE.

`DecisionContext` canónico contiene:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

El contrato declara que la identidad STK deriva de `DecisionContext`, pero `StockResultIdentity` v0.7 omite `rules_version`. Aunque el cálculo métrico STK no interprete las reglas, una salida integrada en EIOS debe conservar el contexto canónico completo para reconstruibilidad y para impedir mezcla silenciosa de resultados procedentes de contextos decisionales diferentes.

**Corrección requerida:** incorporar `rules_version: str` a `StockResultIdentity`, derivado sin transformación de `DecisionContext.rules_version`, y exigir su igualdad en todas las comprobaciones de identidad ya definidas.

---

## 3. G2 — `forecast_version` no forma parte de la afinidad de resultados dependientes de forecast

**Tipo:** BLOQUEANTE.

`StockComputationContext` v0.7 contiene `forecast_version`, pero `StockResultIdentity` no la conserva. `DemandRateResult` sí registra la versión, pero resultados posteriores —cobertura y M07 por cobertura— podrían compartir la misma identidad básica pese a haber consumido forecasts diferentes si el control se limita a la identidad.

**Corrección requerida:** incorporar a `StockResultIdentity`:

```text
forecast_version: str | null
```

Reglas:

- se deriva de `StockComputationContext.forecast_version`;
- cuando la evaluación no consume forecast puede ser nula;
- cuando `DemandRateResult.method == AUTHORIZED_FORECAST`, su `forecast_version` debe coincidir con la identidad;
- resultados que consumen esa demanda preservan la misma versión en su identidad/traza;
- no se inventa una versión cuando no existe.

Esta inclusión no convierte Forecast en autoridad STK ni crea un mecanismo paralelo de versionado.

---

## 4. M02/M03 — revisión de alcance

**Resultado:** SIN BLOQUEO.

STK-M02 y M03 autorizan los conceptos `stock_minimum` y `safety_stock`, pero prohíben una fórmula concreta o valores por defecto mientras no exista política cuantitativa autorizada. La v0.7 acierta al no calcularlos automáticamente y al no introducir el 15 %, 30 días u otra equivalencia implícita.

La ausencia de motor cuantitativo M02/M03 en v0.1 no autoriza tratarlos como cero ni impide que una regla futura/externa consuma un valor explícitamente autorizado y trazable.

---

## 5. Resultado

- A1…A9: resueltos.
- B1…B13: resueltos.
- C1…C7: resueltos.
- D1…D4: resueltos.
- E1…E3: resueltos.
- F1…F3: resueltos.
- G1…G2: abiertos en v0.7.
- M02/M03: alcance correctamente limitado.

**Siguiente paso:** DEPURAR v0.8 → Audit 2 Final independiente.
