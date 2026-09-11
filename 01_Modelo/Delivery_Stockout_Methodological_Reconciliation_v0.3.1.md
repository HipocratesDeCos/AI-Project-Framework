# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL RECONCILIATION v0.3.1

**Estado:** 🔒 RECONCILIACIÓN CORRECTIVA CERRADA  
**Fecha:** 11/09/2026  
**Base preservada:** metodología ENT v0.3  
**Motivo:** contradicción objetiva de representabilidad detectada en Audit 1 del contrato técnico

---

## 1. Alcance

Esta reconciliación no reabre la lógica empresarial de `R-ENT-001` ni sustituye la metodología v0.3.

Corrige exclusivamente dos puntos de coherencia documental necesarios para materializar físicamente el analizador:

1. tratamiento de `STK depletion_date.state = NOT_EVIDENCED`, estado físicamente alcanzable no enumerado por ENT v0.3;
2. preservación explícita del caso de fecha de entrega pasada ya aprobado en el diseño v0.3 y Audit 2 final, pero resumido de forma incompleta en el documento de cierre.

Política empresarial nueva: **0**.

---

## 2. Evidencia del gap `NOT_EVIDENCED`

STK-M09 autoriza:

```text
NOT_EVIDENCED = existe un valor declarado o una dependencia factual,
pero carece de evidencia suficiente para sostener como cierta
la conclusión que depende de ella.
```

La implementación STK propaga estados de incertidumbre y puede producir físicamente:

```text
StockProjectionResult.depletion_date.state = NOT_EVIDENCED
```

cuando una incertidumbre `NOT_EVIDENCED` impide determinar de forma suficientemente evidenciada la fecha de agotamiento.

La metodología ENT v0.3 enumeró `UNKNOWN`, `CONFLICTING_DATA`, `KNOWN` y `NOT_APPLICABLE`, pero omitió este estado físicamente posible y prohibió otros mapeos implícitos.

La omisión es un gap de cobertura documental, no una autorización para inferir punctualidad.

---

## 3. Reconciliación autorizada

Se cierra explícitamente:

```text
STK depletion_date.state = NOT_EVIDENCED
→ ENT temporal relation = NOT_DETERMINABLE
```

Razón:

- ENT no dispone de una fecha de agotamiento suficientemente evidenciada para ejecutar la comparación normativa;
- `NOT_EVIDENCED` no puede convertirse en una fecha ficticia;
- `NOT_EVIDENCED` no puede convertirse en “no habrá rotura”;
- `NOT_EVIDENCED` no puede producir `NOT_LATE_DEMONSTRATED`;
- ENT ya dispone del estado factual `NOT_DETERMINABLE` para expresar que la relación temporal no puede determinarse.

Las causas, issues y trazas STK se conservan; ENT no las reclasifica causalmente.

---

## 4. No cambio de semántica de delivery evidence

La reconciliación anterior afecta únicamente al `depletion_date` consumido desde STK.

No modifica la precedencia cerrada de `PurchaseSpecificDeliveryTimingEvidence`:

```text
NOT_EVIDENCED    → NOT_EVIDENCED
CONFLICTING_DATA → CONFLICTING_DATA
NOT_DETERMINABLE → NOT_DETERMINABLE
KNOWN            → continuar
```

Por tanto:

```text
STK depletion NOT_EVIDENCED
≠
Delivery evidence NOT_EVIDENCED
```

Los dos estados provienen de dependencias distintas y mantienen efectos ENT distintos conforme a sus autoridades respectivas.

---

## 5. Fecha de entrega pasada

Se confirma como vigente el comportamiento ya aprobado en `Delivery_Stockout_Methodological_Design_v0.3.md` y superado por Audit 2 final:

```text
expected_delivery_date < evaluation_date
```

no se corrige ni se rechaza automáticamente.

Si la semántica de la fecha y su aplicabilidad a la propuesta actual están suficientemente demostradas, ENT conserva la fecha y aplica la comparación ordinaria.

Si existe una fecha evidenciada pero no se demuestra que siga siendo aplicable a la propuesta actual:

```text
NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

La ausencia de este código en el resumen del documento de cierre v0.3 no constituye supersesión de la autoridad ya auditada.

---

## 6. Estados ENT preservados

No se crea ningún estado analítico nuevo.

Continúan siendo:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Y las limitaciones autorizadas relevantes para contrato técnico quedan:

```text
SAME_DAY_ORDER_NOT_DEMONSTRATED
DELIVERY_BEYOND_STK_HORIZON
PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

---

## 7. Fronteras preservadas

Esta reconciliación no:

- modifica STK;
- modifica Supplier;
- crea un parámetro ENT;
- deriva fechas desde lead time;
- cambia `delivery > depletion`;
- cambia la semántica de igualdad;
- extrapola fuera del horizonte;
- crea `Assessment`;
- cambia RDM;
- produce `NEGOCIAR`;
- crea decisión empresarial.

---

## 8. Autoridades de soporte

La reconciliación se apoya en:

- `01_Modelo/STK_M09_Missing_Data_Authority.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Design_v0.3.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Audit_2_Final_v0.3.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- implementación física STK vigente;
- `08_Implementacion/Assessment_Individual_Result_Contract.md` como frontera de no conversión de ausencia a FALSE.

---

## 9. Dictamen

**RECONCILIACIÓN v0.3.1: CERRADA.**

Se autoriza para el contrato técnico exclusivamente:

```text
STK depletion NOT_EVIDENCED → ENT NOT_DETERMINABLE
```

y se confirma la vigencia de:

```text
PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

Sin política empresarial nueva y sin cambio de la condición normativa de `R-ENT-001`.
