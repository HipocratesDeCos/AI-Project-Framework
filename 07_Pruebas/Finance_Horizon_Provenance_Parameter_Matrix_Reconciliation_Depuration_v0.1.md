# EIOS — Finance Horizon Provenance Parameter Matrix Reconciliation — Depuration v0.1

## Estado

**Fase:** DEPURAR  
**Unidad:** FIN-PROV-PARAM-MATRIX-01  
**Base:** Design v0.1 + Audit 1 v0.1.

## 1. Formulación depurada

La Matriz de Parámetros debe distinguir dos afirmaciones diferentes:

```text
FIN-PROV-HORIZON-01
→ CERRADO físicamente / provenance-safe
```

frente a:

```text
P-FIN-001 = 30 días
→ valor empresarial definitivo
```

La primera está demostrada. La segunda no.

## 2. Estado físico autorizado

El cierre físico significa que la ejecución Finance:

- recibe la configuración resuelta de `P-FIN-001`;
- valida su identidad y procedencia;
- verifica versión/vigencia/contexto aplicable;
- contrasta el horizonte autorizado con `FinanceBasicInput.horizon_days`;
- rechaza resultados Finance desprendidos o inconsistentes;
- recalcula/valida la ejecución dentro de `ProvenancedFinanceBasicExecution` conforme al contrato cerrado.

No se amplía esta semántica más allá del contrato ya integrado.

## 3. Estado empresarial preservado

El valor inicial de 30 días:

- continúa sujeto a validación empresarial;
- no se fija como constante universal;
- no se convierte en política por esta reconciliación.

## 4. Delta depurado

Solo se autoriza modificar en `Matriz_Parametros_Reglas_MVP.md`:

1. versión `0.9.3 → 0.9.4`;
2. párrafo de reconciliación `P-FIN-001 → R-FIN-001`;
3. mención de `FIN-PROV-HORIZON-01` en pendientes;
4. mención de `FIN-PROV-HORIZON-01` en el estado final.

Las relaciones, filas y restantes pendientes se preservan.

## 5. Resultado

Diseño depurado sin cambio funcional, sin nueva autoridad empresarial y sin reapertura de Finance.
