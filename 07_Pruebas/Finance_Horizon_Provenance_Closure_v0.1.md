# EIOS — Finance Horizon Provenance — Closure v0.1

## Estado

**CERRAR — 🔒 CONTRATO TÉCNICO CERRADO / MATERIALIZACIÓN AUTORIZADA**

**Baseline:** `main @ 595b45296ae507d7d5224bdb7739bfb4184421a8`  
**Audit 2:** SUPERADA — 0 bloqueadores

---

## 1. Decisión de cierre

Queda cerrado el contrato técnico para resolver `FIN-PROV-HORIZON-01` mediante una frontera de ejecución Finance Basic provenance-safe.

La frontera autorizada es:

```text
FinanceBasicInput
+ ResolvedConfiguration(P-FIN-001)
        ↓
run_provenanced_finance_basic
        ↓
ProvenancedFinanceBasicExecution
        ↓
revalidación obligatoria
        ↓
Rules FIN
```

---

## 2. Invariantes cerradas

La implementación deberá garantizar:

1. `P-FIN-001` es el único parámetro aceptado como origen de `horizon_days`;
2. `parameters_version`, empresa y fecha coinciden con el contexto Finance Basic;
3. la configuración está vigente en `effective_at`;
4. la unidad es exactamente `días`;
5. el valor es finito, entero y estrictamente positivo;
6. el valor coincide exactamente con `FinanceBasicInput.horizon_days`;
7. la producción provenance-safe calcula internamente el `FinanceBasicResult`;
8. la reutilización revalida la resolución y vuelve a calcular el resultado;
9. Rules no acepta el par desprendido `FinanceBasicInput + FinanceBasicResult` en los bridges FIN;
10. una violación de provenance falla técnicamente antes de Rules y no crea una política de evaluabilidad.

---

## 3. Semántica Finance preservada

No se modifica:

```text
financial_capacity_forecast
=
minimum_projected_treasury_within_authorized_horizon
```

ni:

```text
R-FIN-001:
financial_capacity_forecast < P-FIN-002
```

ni:

```text
R-FIN-003:
financial_safety_margin_pct < P-FIN-004
```

El valor inicial de 30 días no queda validado como política empresarial.

---

## 4. Autoridad preservada

La unidad no crea autoridad nueva para:

- `Assessment.NOT_EVALUABLE` por ausencia/incoherencia de `P-FIN-001`;
- una arista RDM adicional `P-FIN-001 → R-FIN-003`;
- defaults de horizonte;
- nuevos parámetros;
- nuevas reglas;
- nuevas fórmulas;
- cambios en severidad, efecto o CRC.

`Criticality` y `Evaluability_Impact` permanecen donde la RDM los mantiene.

---

## 5. Superficie autorizada

Se autoriza MATERIALIZAR únicamente en:

```text
eios/finance/provenance.py
eios/finance/__init__.py
eios/rules/finance.py
eios/rules/orchestrator.py
tests afectados y tests provenance específicos
```

La necesidad de ampliar superficie por una contradicción no prevista exigiría nueva auditoría antes de hacerlo.

---

## 6. Estado de FIN-PROV-HORIZON-01

El gap **no queda todavía cerrado físicamente por este documento**.

Estado correcto:

```text
Contrato técnico          🔒 CERRADO
Materialización           ⏭️ AUTORIZADA
FIN-PROV-HORIZON-01       🟡 ABIERTO hasta implementación + tests + CI + merge + CI post-merge
```

Solo después de validar la implementación exacta y su integración podrá declararse cerrado el gap físico.

---

## 7. Secuencia EIOS

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ⏭️
CI            ⏭️
```

**Estado de cierre contractual: CERRADO.**