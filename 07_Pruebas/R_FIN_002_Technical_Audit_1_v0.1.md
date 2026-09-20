# EIOS — R-FIN-002 Technical Audit 1 v0.1

## Hallazgos y controles

### F1 — confundir Finance Basic working capital con posición post-operación
Mitigado por carrier separado y ausencia de dependencia a `FinanceBasicResult`.

### F2 — binding débil a compra
Mitigado por SHA-256 de la `PurchaseOperation` completa.

### F3 — Evidence desprendida
Mitigado por hash determinista del carrier completo.

### F4 — parámetro sin vigencia
Mitigado por validación explícita `valid_from <= effective_at < valid_to`.

### F5 — EUR vs €
Solo se acepta alias `€` cuando la moneda del carrier es EUR. No existe FX.

### F6 — threshold negativo
No se rechaza: la autoridad no impone que el fondo de maniobra mínimo sea positivo.

### F7 — igualdad
La condición es estricta `<`; igualdad produce FALSE.

### F8 — R0 configurable
No se materializa switch, downgrade ni excepción.

### F9 — ausencia como cero
Prohibida. Evidence/parameter ausente → NOT_EVALUABLE.

### F10 — decisión dentro de Rule
El evaluator produce Assessment únicamente.

**AUDIT 1: SUPERADA — 0 bloqueadores.**
