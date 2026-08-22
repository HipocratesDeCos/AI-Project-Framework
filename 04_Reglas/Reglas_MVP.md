# REGLAS MVP — DOCUMENTO LEGADO / REFERENCIA

## EIOS — Enterprise Intelligent Operations System

**Estado:** ALINEADO — documento histórico de referencia  
**Baseline:** EIOS Vertical MVP

> **AVISO DE AUTORIDAD:** La definición oficial y vigente de las reglas MVP se encuentra en `04_Reglas/Matriz_Reglas_MVP.md`. Este documento conserva la regla histórica de pagos únicamente como referencia de migración y no constituye una segunda fuente normativa.

---

# 1. Regla histórica de plazo de pago

La versión histórica utilizaba el identificador `CON-001` y los IDs sin prefijo `PAG-001/PAG-002`.

Esa nomenclatura queda **obsoleta** para el MVP vigente.

La decisión `C-07` de `02_Parametros/Decision_Log_Parametros_MVP.md` establece que no se utilizará `CON-001` como identificador vigente de una regla de plazo de pago.

---

# 2. Equivalencia vigente

La lógica histórica se descompone en las reglas oficiales:

| Identificador histórico | Identificador vigente | Función |
|---|---|---|
| `CON-001` | `R-PAG-001` | Evaluación del plazo ofrecido frente al objetivo |
| `CON-001` | `R-PAG-002` | Condición de compra vinculada al plazo mínimo ante riesgo financiero |

Los parámetros históricos:

| Identificador histórico | Identificador vigente |
|---|---|
| `PAG-001` | `P-PAG-001` |
| `PAG-002` | `P-PAG-002` |
| `PAG-003` | `P-PAG-003` |
| `PAG-004` | `P-PAG-004` |
| `PAG-005` | `P-PAG-005` |

---

# 3. Fuente normativa vigente

Para cualquier implementación, trazabilidad o decisión deberá utilizarse exclusivamente:

1. `04_Reglas/Matriz_Reglas_MVP.md` — definición oficial de `R-PAG-001` y `R-PAG-002`.
2. `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` — relación funcional especializada entre parámetros y reglas.
3. `02_Parametros/Matriz_Parametros_Reglas_MVP.md` — matriz oficial de enlace.
4. `00_Gobierno/Registro_Evidencias_Trazabilidad_F3.md` — evidencia reproducible.
5. `02_Parametros/Decision_Log_Parametros_MVP.md` — decisión `C-07`.

Este documento **no debe utilizarse como fuente de autoridad para crear nuevas relaciones**.

---

# 4. Regla de no inferencia

No se considerará válida ninguna relación parámetro → regla basada únicamente en la coincidencia de nombres, números o familias.

La relación vigente de pagos queda determinada por la cadena documental de `C-07`.

---

# 5. Estado

**Documento:** legado / referencia de migración  
**Regla:** no constituye fuente normativa independiente  
**Regla vigente:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**C-07:** cerrado documental y funcionalmente
