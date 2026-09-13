# EIOS — Configuration Center UI Contract — Audit 1 v0.1

**Fecha:** 2026-09-13  
**Baseline auditado:** `7ddf1a5ccb379749ab51264dcde5507f92bd60f9`  
**Dictamen:** APTO PARA DEPURACIÓN — 4 reajustes requeridos, 0 bloqueos de autoridad

## 1. Fuentes contrastadas

- `02_Parametros/Centro_Parametrizacion.md`
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`
- `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md`
- `03_App/UI_Architecture_Contract_v0.1.md`
- `00_Gobierno/Project_Context.md`
- `00_Gobierno/Matriz_Autoridad_Documental.md`

## 2. Hallazgos

### A1 — Actor no puede ser dato libre de UI — REAJUSTE

El contrato menciona la identidad del actor en confirmación/trazabilidad, pero debe quedar explícito que la UI no puede suministrar o sobrescribir libremente `actor`. Debe provenir del contexto autorizado del servicio o de una frontera de identidad futura autorizada.

### A2 — `company_id` no puede ser ámbito libre — REAJUSTE

La selección empresarial debe limitarse a ámbitos devueltos/autorizados por la frontera. Un campo libre de empresa permitiría intentar acceso cruzado contrario a aislamiento y `INVALID_COMPANY_SCOPE`.

### A3 — Revalidación antes de aplicar — REAJUSTE

Entre carga, edición y confirmación el valor vigente puede cambiar. Sin inventar un mecanismo de locking/versionado, el contrato debe exigir revalidación del cambio contra el estado vigente inmediatamente antes de `apply_change(...)`, delegando el conflicto al servicio.

### A4 — Explicación de impacto sin inferencia — PRECISIÓN

La regla propuesta es correcta, pero debe distinguir explícitamente explicación semántica autorizada de predicción/simulación. La UI puede explicar qué controla el parámetro; no puede afirmar el efecto concreto de una modificación sobre operaciones o recomendaciones sin productor autorizado.

## 3. Fronteras verificadas

- no se crean parámetros;
- no se crean reglas;
- no se modifica CRC;
- no se habilitan excepciones;
- no se implementa simulación avanzada;
- no se escribe SQL directamente;
- no se reabre C0, PRICE, TCO, STK, Finance, Supplier, VF, Scenarios, Twin, NI/Ladder ni Decision Versioning;
- la autoridad decisional humana permanece intacta.

## 4. Dictamen

No existe bloqueo para cerrar el diseño tras incorporar A1–A4. La unidad es representacional/administrativa sobre una capacidad de parametrización ya autorizada y materializada.
