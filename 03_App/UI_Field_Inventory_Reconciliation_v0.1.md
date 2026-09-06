# EIOS — Reconciliación Inventario de Campos UI v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA
**Referencia autoritativa:** `UI_Field_Registry_v0.1.md`
**Artefacto auxiliar:** Inventario Excel generado en la conversación
**Fecha:** 2026-09-06

## 1. Regla de autoridad

El `UI_Field_Registry_v0.1.md` es la fuente autoritativa de campos e identificadores UI. El Excel de 98 campos se considera inventario auxiliar y no puede modificar, ampliar ni sustituir el registro maestro.

El registro maestro define los identificadores `UI-*`, estados de campo y restricciones de materialización. En particular, los campos STK con metodología pendiente no autorizan fórmulas M01–M10. fileciteturn121file0

## 2. Resultado preliminar de reconciliación

Se detectan tres tipos de discrepancia que deben controlarse antes de usar el Excel como catálogo de implementación:

1. **Normalización de nombres:** el Excel utiliza nombres descriptivos alternativos frente al nombre canónico del registro maestro (ej.: `Stock actual / stock_on_hand` frente a `Stock actual`).
2. **Granularidad:** el Excel descompone algunos conceptos que el registro maestro mantiene como un único campo, mientras que otros campos del registro maestro no aparecen con idéntico nombre.
3. **Campos derivados:** el Excel contiene variantes conceptuales de resultados y métricas; el registro maestro establece qué es un campo único y qué estado tiene.

## 3. Regla de resolución

- `MATCH`: se conserva el campo canónico del registro maestro.
- `RENOMBRADO`: se mantiene el nombre canónico y se registra el alias como auxiliar.
- `EXTRA_EN_EXCEL`: no se incorpora al registro maestro sin decisión formal.
- `FALTA_EN_EXCEL`: se incorpora al Excel únicamente mediante reconciliación documentada; no implica modificación del registro maestro.
- `AMBIGUO`: no se materializa hasta resolver su semántica.

## 4. Restricción

Esta reconciliación es documental. No crea nuevos `Test_ID`, no modifica el Plan de Pruebas y no concede autoridad cuantitativa STK.

## 5. Gate

Siguiente fase obligatoria: **AUDITAR** la reconciliación antes de cualquier modificación del Registro Maestro o de cualquier implementación basada en el Excel.
