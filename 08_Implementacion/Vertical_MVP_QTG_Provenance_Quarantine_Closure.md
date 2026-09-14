# EIOS — Vertical MVP QTG Provenance Quarantine · Closure

**Baseline:** `main @ fe03a6da407490705207f579bcd45a4b384d8bc2`  
**Rama:** `fix/vertical-mvp-qtg-provenance-quarantine`  
**Estado:** 🔒 CERRADO PARA MATERIALIZACIÓN.

## 1. Secuencia completada

- DISEÑAR ✅
- AUDITAR ✅ Audit 1 — 0 bloqueadores
- DEPURAR ✅ A1–A5 incorporados
- AUDITAR 2 ✅ — 0 bloqueadores
- CERRAR ✅
- MATERIALIZAR ⏳
- CI ⏳

## 2. Decisión cerrada

Mientras no exista un `Decision Input Package` físico, agregado y trazable y un productor QTG provenance-safe autorizado, las fronteras genéricas del Vertical MVP no pueden aceptar un `quality_invoker` arbitrario.

La materialización cerrada consiste exclusivamente en:

1. retirar `quality_invoker` de `run_mvp_execution(...)`;
2. retirar `quality_invoker` de `run_vertical_mvp_support(...)`;
3. eliminar su registro/reenvío en esas fronteras;
4. reconciliar tests para que no legitimen QTG mediante callable genérico;
5. demostrar que el keyword antiguo falla explícitamente;
6. conservar `QTG` en `MVP_CAPABILITY_ORDER`.

## 3. No autorizado

No se autoriza:

- modificar `eios/quality/`;
- crear o inferir `Decision Input Package`;
- crear productor QTG;
- introducir estados QTG artificiales;
- cambiar estados/confianza Quality & Trust;
- cambiar otra capacidad Vertical MVP;
- modificar autoridad decisional.

## 4. Condición de integración

Este cierre es de diseño y **no equivale a integración en `main`**.

La unidad solo quedará físicamente cerrada tras:

- materialización auditada;
- suite completa Python + validaciones SQL en CI pre-merge sobre HEAD exacto;
- reconciliación `behind=0` inmediatamente antes del merge;
- merge protegido por SHA exacto;
- CI post-merge sobre el merge SHA exacto en `SUCCESS`.
