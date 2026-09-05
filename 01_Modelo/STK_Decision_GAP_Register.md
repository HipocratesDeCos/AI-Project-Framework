# EIOS — STK DECISION / GAP REGISTER

**Versión:** 0.2  
**Estado:** CIRCUITO DE DECISIÓN FORMAL — M01 ENTRADA  
**Rama:** `design/stk-quantitative-authority`  
**Baseline de `main`:** `3c4d5cb7e02d5d7d88bb8bcf1a20a3992dc06c38`  
**Fecha:** 05/09/2026

---

## 1. Propósito

Este registro descompone `STK-M01…STK-M10` en decisiones y gaps verificables antes de cualquier implementación cuantitativa.

No crea fórmulas, reglas, parámetros, valores empresariales ni autoridad nueva.

## 2. Regla de continuidad

Este documento es un registro de trabajo de la rama STK. No constituye materialización en `main` ni autorización de implementación.

Mientras exista cualquier gap marcado `BLOQUEA`, STK permanece:

**NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA.**

La ausencia de una decisión no se interpreta como permiso implícito.

## 3. Estado de M01–M10

| GAP | Concepto | Estado | Bloquea |
|---|---|---|---|
| STK-G01 / M01 | Consumo | BLOQUEADO — falta autoridad cuantitativa | Sí |
| STK-G02 / M02 | Stock mínimo | ABIERTO | Sí |
| STK-G03 / M03 | Stock de seguridad | ABIERTO | Sí |
| STK-G04 / M04 | Cobertura | ABIERTO | Sí |
| STK-G05 / M05 | Proyección temporal | ABIERTO — PARCIAL | Sí |
| STK-G06 / M06 | Pedidos pendientes / tránsito | ABIERTO | Sí |
| STK-G07 / M07 | Exceso | ABIERTO | Sí |
| STK-G08 / M08 | Pedido confirmado | ABIERTO | Sí |
| STK-G09 / M09 | Datos ausentes | PARCIAL | Parcial |
| STK-G10 / M10 | Contradicciones | ABIERTO | Sí |

## 4. Ficha de decisión — STK-M01

### Pregunta de autoridad

**¿Qué magnitud constituye `consumption` para STK y qué transformación autorizada debe aplicarse a las fuentes disponibles?**

### Evidencia mínima de cierre

Debe existir una fuente trazable que establezca explícitamente:

1. magnitud canónica;
2. unidad;
3. período de referencia;
4. tratamiento de ausencia, si aplica;
5. transformación/agregación autorizada;
6. fuente de autoridad;
7. vigencia o condición de aplicación, cuando corresponda.

### No inferir

No se permite cerrar M01 mediante equivalencia entre ventas, consumo y demanda; promedios por convención; uso automático de los 12 meses de `STK-006` como fórmula definitiva; imputación de períodos ausentes; ni transformaciones derivadas de práctica habitual no documentada.

### Estado

**M01 — BLOQUEADO POR AUSENCIA DE AUTORIDAD CUANTITATIVA.**

No se modifica ningún parámetro, regla o contrato técnico como consecuencia de este registro.

## 5. Próxima transición válida

`Autoridad M01 → Evidencia trazable → AUDITAR 2 M01 → Cierre M01 → M02`

No procede implementar fórmulas, modificar parámetros como política definitiva, crear reglas nuevas, resolver contradicciones por heurística, crear contrato técnico STK cuantitativo ni abrir una PR de implementación.
