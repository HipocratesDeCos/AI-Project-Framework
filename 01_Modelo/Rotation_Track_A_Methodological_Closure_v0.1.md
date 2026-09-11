# EIOS — ROTACIÓN · TRACK A METHODOLOGICAL CLOSURE v0.1

**Estado:** 🔒 CERRADO METODOLÓGICAMENTE — NO APTO PARA IMPLEMENTACIÓN  
**Fecha:** 11/09/2026  
**Objeto:** Sales Activity Window para `R-ROT-002`

---

## 1. Alcance cerrado

Queda cerrada únicamente la metodología factual necesaria para determinar si existe evidencia suficiente de actividad o inactividad de ventas de un artículo en una ventana autorizada.

No queda cerrada la métrica general de rotación de `R-ROT-001`.

---

## 2. Semántica cerrada

### `ZERO_VALID_SALES_DEMONSTRATED`

Solo puede declararse cuando una fuente autorizada, con semántica identificada y cobertura suficiente de toda la ventana, demuestra que no existió ningún evento de venta válido del artículo en dicho periodo.

### `SALES_ACTIVITY_PRESENT`

Puede declararse cuando existe al menos una venta válida demostrada dentro de la misma ventana y scope.

### Estados de insuficiencia

Se conservan separadamente:

- `NOT_EVIDENCED`;
- `CONFLICTING_DATA`;
- `NOT_DETERMINABLE`.

Ninguno equivale a cero ventas.

---

## 3. Invariantes cerrados

1. ausencia de filas != cero ventas;
2. `GAP` != cero ventas;
3. net sales quantity = 0 != ausencia de ventas;
4. ventana parcial != ventana completa;
5. la ventana requiere autoridad/configuración identificable;
6. la fuente requiere semántica identificable;
7. ROT no redefine devoluciones/anulaciones/abonos;
8. ventas != consumo;
9. ventas != demanda;
10. rotación != cobertura;
11. Track A no aplica excepciones;
12. Track A no produce Assessment ni decisión.

---

## 4. Frontera con R-ROT-002

Track A entrega soporte factual para evaluar la condición:

> “No existen ventas durante el periodo configurado.”

No decide:

- si la regla debe producir NO COMPRAR;
- si debe escalar a R0;
- si aplica una excepción;
- cómo resuelve CRC;
- la decisión humana final.

---

## 5. Gaps abiertos que bloquean implementación

### `ROT-G01` — periodo configurado

No existe parámetro/autoridad demostrada para la ventana exigida por `R-ROT-002`.

### `ROT-G04-A` — dependencias canónicas

RDM no contiene todavía las dependencias DATA/EVIDENCE/PARAMETER necesarias para `R-ROT-002`.

Por tanto, este cierre **no autoriza contrato técnico ni código**.

---

## 6. Track B permanece abierto

`R-ROT-001` continúa bloqueada por:

- `ROT-G02` — definición/fórmula de `rotation_metric`;
- `ROT-G03` — umbral de baja rotación;
- `ROT-G04` — dependencias canónicas.

No se adopta ninguna fórmula estándar por inferencia.

---

## 7. Secuencia completada

Para Track A:

```text
DISEÑAR ✅
AUDITAR ✅
DEPURAR ✅
AUDITAR 2 ✅
CERRAR ✅ (metodología factual)
MATERIALIZAR IMPLEMENTACIÓN ⛔
CI IMPLEMENTACIÓN ⛔
```

El bloqueo posterior es objetivo y documental, no técnico.

---

## 8. Dictamen

**ROT-TRACK-A — METODOLOGÍA CERRADA.**

**Contrato técnico:** NO AUTORIZADO.  
**Implementación:** NO AUTORIZADA.  
**Track B:** ABIERTO / BLOQUEADO POR AUTORIDAD.  
**Política empresarial nueva introducida:** 0.
