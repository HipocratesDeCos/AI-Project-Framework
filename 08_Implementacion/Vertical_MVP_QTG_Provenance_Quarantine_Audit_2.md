# EIOS — Vertical MVP QTG Provenance Quarantine · Audit 2

**Baseline:** `main @ fe03a6da407490705207f579bcd45a4b384d8bc2`  
**Contrato auditado:** `Vertical_MVP_QTG_Provenance_Quarantine_Contract_v0.1.md`  
**Rama:** `fix/vertical-mvp-qtg-provenance-quarantine`  
**Resultado:** SUPERADA — 0 BLOQUEADORES.

## 1. Revisión de consistencia

Audit 2 confirma que el contrato depurado distingue correctamente:

- **QTG como dominio/evaluador cerrado**, que permanece intacto;
- **integración QTG provenance-safe en Vertical MVP**, que permanece bloqueada por ausencia de `Decision Input Package` físico, agregado y trazable;
- **frontera provisional `quality_invoker`**, que es el único objeto de cuarentena de esta unidad.

No se redefine Quality & Trust ni se afirma que QTG deje de existir arquitectónicamente.

## 2. Contraste transversal

### BL-003

Compatible: BL-003 mantiene QTG bloqueado mientras no exista su paquete de entrada físico y trazable. Retirar el callable genérico elimina una vía que permitía contradecir ese bloqueo.

### Quality & Trust Implementation Contract

Compatible: el contrato QTG exige una entrada identificada y trazable. La unidad no modifica estados, confianza, precedencia, evidencia ni evaluación.

### Opaque Result Provenance Quarantine

Compatible y evolutivo: aquella unidad eliminó resultados crudos y dejó expresamente pendiente la construcción de invocadores realmente provenance-safe. La unidad actual no revierte ese cierre; elimina únicamente la provisionalidad QTG que no ha podido adquirir productor autorizado.

### Vertical MVP / Execution Boundary

Compatible: se conserva `MVP_CAPABILITY_ORDER`, `ExecutionPlan`, `execute_plan(...)`, agregación de estados y fail-closed de ejecución vacía. No se modifica ninguna otra capacidad.

### Otras fronteras provenance-safe

No se altera PRICE, TCO, C0/Rules, Decision Twin, Scenario Coordination, NI ni Ladder. Sus productores/invocadores cerrados siguen disponibles.

## 3. Revisión de alternativas descartadas

Se descartan por inseguras o no autorizadas:

1. **Mantener `quality_invoker` y confiar en el caller** → no demuestra procedencia.
2. **Validar solo `capability == "QTG"`** → valida etiqueta, no entrada ni contexto.
3. **Exigir `trace_references` no vacíos** → referencias opacas no prueban por sí solas el `Decision Input Package` ni su pertenencia contextual.
4. **Ignorar silenciosamente `quality_invoker`** → fail-open de compatibilidad y ocultación del defecto.
5. **Emitir QTG `NOT_EVALUABLE`/`BLOCKED` artificial** → inventa semántica no autorizada.
6. **Eliminar `QTG` de `MVP_CAPABILITY_ORDER`** → altera arquitectura, innecesario para la cuarentena.
7. **Crear ahora un productor QTG o `DecisionInputPackage`** → inventa arquitectura/material ausente.

La retirada de la firma provisional es la corrección mínima que satisface el baseline actual.

## 4. Revisión del delta pre-materialización

Comparación rama ↔ `main`:

- `ahead=3`;
- `behind=0`;
- únicamente dos documentos nuevos;
- ningún archivo de producción modificado;
- ningún test modificado todavía;
- ninguna autoridad funcional alterada antes de cierre.

## 5. Invariantes para materialización

La implementación queda autorizada únicamente si cumple simultáneamente:

- retirar `quality_invoker` de `run_mvp_execution(...)`;
- retirar `quality_invoker` de `run_vertical_mvp_support(...)`;
- retirar el registro `QTG -> quality_invoker` de la composición genérica;
- mantener `QTG` en `MVP_CAPABILITY_ORDER`;
- actualizar tests que hoy legitiman el callable QTG genérico;
- añadir prueba explícita de rechazo por keyword antiguo en ambas fronteras;
- no tocar `eios/quality/`;
- no crear productor QTG;
- no crear `Decision Input Package`;
- no cambiar ninguna otra frontera provenance-safe.

Si aparece un consumidor adicional durante la suite completa, solo podrá modificarse para retirar el uso del parámetro inseguro; cualquier necesidad funcional adicional bloqueará la unidad y exigirá nuevo diseño.

## 6. Dictamen

**AUDIT 2: SUPERADA — 0 BLOQUEADORES.**

El contrato puede pasar a CERRAR y posteriormente MATERIALIZAR dentro del alcance exacto anterior.
