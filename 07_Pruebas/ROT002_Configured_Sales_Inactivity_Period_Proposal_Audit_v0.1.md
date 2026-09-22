# EIOS — ROT002 Configured Sales-Inactivity Period Proposal Audit v0.1

**Baseline de propuesta:** `46dba43c62dbe86076c4ca9ecbdd7e7514238516`  
**Fecha:** 22/09/2026  
**Estado:** AUDIT 2 — SUPERADA CON LÍMITES EXPLÍCITOS  
**Objeto:** auditar `ROT002_Configured_Sales_Inactivity_Period_Authority_Proposal_v0.1.md`.

## 1. Resultado ejecutivo

La propuesta es coherente como mecanismo para someter `ROT-G01` a decisión humana.

No debe interpretarse como cierre de `R-ROT-002` completo.

La propuesta:

- no modifica el Catálogo;
- no modifica código;
- no reutiliza parámetros de otros dominios;
- no fija un valor empresarial;
- no define una fórmula general de rotación;
- no resuelve excepciones;
- no autoriza R0;
- conserva fail-closed.

**Bloqueadores para publicar la propuesta:** 0.  
**Autoridad humana requerida para convertirla en decisión vigente:** sí.

## 2. A1 — Necesidad de configuración dedicada

La Matriz de Reglas exige “periodo configurado”.

No existe `P-ROT-*` vigente y no existe autoridad para mapear P-STK/P-PYE/PRE/DAT.

La creación propuesta de un identificador dedicado es coherente con el principio de no reutilización semántica.

**Resultado:** CONFORME COMO PROPUESTA.

## 3. A2 — Identificador `P-ROT-001`

No se ha encontrado un identificador `P-ROT-*` vigente en el repositorio.

`P-ROT-001` es una nomenclatura **nueva propuesta**, no una variable existente descubierta.

El documento la etiqueta expresamente como sometida a aprobación.

**Resultado:** CONFORME; NO VIGENTE.

## 4. A3 — Unidad días

La elección de días:

- evita clipping mensual implícito;
- permite una ventana exacta;
- es compatible con fechas;
- no fija duración empresarial.

Sin embargo, constituye una decisión metodológica nueva.

Debe ser aprobada expresamente y no puede inferirse de parámetros temporales de otros dominios.

**Resultado:** CONFORME COMO PROPUESTA; REQUIERE AUTORIDAD.

## 5. A4 — Ausencia de default

No fijar 30/90/180/365 ni otro valor evita introducir política empresarial.

Una configuración ausente o inválida debe conservar `NOT_EVALUABLE`.

**Resultado:** CONFORME.

## 6. A5 — Fecha base

La propuesta:

```text
evaluation_date = PurchaseOperation.operation_date
```

elimina una segunda fecha libre, pero constituye una nueva relación semántica.

Debe aprobarse expresamente.

No debe derivarse desde:

- reloj del sistema;
- Evidence.captured_at;
- effective_at de parámetros;
- data_snapshot_id.

**Resultado:** CONFORME COMO PROPUESTA; REQUIERE AUTORIDAD.

## 7. A6 — Ventana inclusiva

La propuesta:

```text
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1)
```

es determinista y evita el off-by-one para un periodo de un día.

Constituye metodología nueva y requiere autorización.

**Resultado:** CONFORME COMO PROPUESTA.

## 8. A7 — SalesActivityWindowEvidence

La propuesta no redefine:

- `source_semantics_ref`;
- `completeness_ref`;
- actividad válida;
- devoluciones;
- anulaciones;
- abonos;
- netting.

Conserva el cierre metodológico Track A.

**Resultado:** CONFORME.

## 9. A8 — Dependencias

La propuesta no declara falsamente cerrado `ROT-G04-A`.

Tras una eventual autorización todavía deberán materializarse/canonizarse:

- relación `PARAMETER`;
- binding de contexto/data;
- evidencia de configuración;
- binding físico exacto a `SalesActivityWindowEvidence`.

**Resultado:** CONFORME.

## 10. A9 — R-ROT-002 y CRC

La Matriz documenta simultáneamente:

```text
Resultado: NO COMPRAR salvo excepción
Effect: R1 — CONDICIONANTE / ALTA
```

La propuesta de periodo no debe decidir por sí sola cómo se materializa esa combinación dentro de CRC.

Antes del core ejecutable deberá existir reconciliación explícita de:

- metadata técnica;
- `active_result`, si procede;
- alcance de excepciones;
- prohibición de escalada R0 por inferencia.

**Resultado:** FUERA DE ROT-G01 / GATE POSTERIOR CONTROLADO.

## 11. A10 — Excepciones

Pedido confirmado, campaña, operación estratégica y decisión empresarial explícita permanecen fuera del Track A factual.

La propuesta no los convierte en campos booleanos ni fallbacks.

**Resultado:** CONFORME.

## 12. A11 — R-ROT-001

No se modifica:

- definición de rotation_metric;
- fórmula;
- numerador;
- denominador;
- ventana;
- threshold.

**Resultado:** CONFORME.

## 13. No regresión

Se mantiene:

```text
absence of rows != ZERO_VALID_SALES_DEMONSTRATED
GAP != zero sales
net quantity zero != no sales
partial coverage != complete coverage
sales != consumption
sales != demand
rotation != coverage
```

## 14. Secuencia autorizable

Si la propuesta recibe aprobación humana:

```text
PROPUESTA
→ AUTHORITY ROT-G01
→ actualizar Catálogo / matrices
→ cerrar dependencia PARAMETER
→ contrato físico de configuración/window binding
→ auditar
→ materializar
→ CI
→ abordar gate técnico de R-ROT-002
```

No saltar directamente desde la aprobación del parámetro al Rule bridge.

## 15. Dictamen

```text
DISEÑAR PROPUESTA  ✅
AUDITAR            ✅
DEPURAR            ✅
AUDITAR 2          ✅
PUBLICABLE         ✅
AUTORIZADA         ⏳ NO
MATERIALIZAR       ⛔ NO
```

**ROT002 CONFIGURED SALES-INACTIVITY PERIOD PROPOSAL v0.1 — APTA PARA DECISIÓN HUMANA.**
