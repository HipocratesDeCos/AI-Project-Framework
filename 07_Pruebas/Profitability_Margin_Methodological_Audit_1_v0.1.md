# EIOS — RENTABILIDAD / MARGEN · AUDIT 1 METODOLÓGICA v0.1

**Estado:** COMPLETADA — DEPURACIÓN REQUERIDA / AUTORIDAD EMPRESARIAL PARCIALMENTE PENDIENTE  
**Fecha:** 11/09/2026  
**Objeto:** `01_Modelo/Profitability_Margin_Methodological_Design_v0.1.md`

---

## 1. Dictamen

La documentación vigente autoriza la **existencia funcional** de:

- precio de venta;
- margen en euros;
- margen porcentual;
- margen mínimo;
- margen objetivo;
- tolerancia;
- impacto de descuentos y rappels.

También confirma:

```text
P-MGE-001 → R-MGE-001
P-MGE-002 → R-MGE-003
P-MGE-003 → R-MGE-002
```

Pero **no existe autoridad suficiente para calcular todavía el margen** porque no están cerradas la base de venta, la base de coste ni el denominador del porcentaje.

No se encuentra una metodología MGE histórica ni un contrato técnico cerrado que resuelva estos puntos.

---

## 2. Hallazgos

### MGE-A1-01 — MGE no constituye una nueva capa arquitectónica

El Architecture Blueprint cierra capas 0–5 y después Viability Frontier. Rentabilidad aparece como dimensión empresarial, no como “Capa 6”.

**Corrección:** mantener MGE como capacidad analítica de dominio/transversal que entrega magnitudes a Rules/MED/Viability.

**Estado:** RESUELTO EN DISEÑO.

---

### MGE-A1-02 — No existe fórmula autorizada de margen en importe

Especificación Funcional y MED exigen margen en euros, pero remiten la metodología concreta a otra capa y no fijan la fórmula.

La expresión conceptual `sale basis - cost basis` es estructuralmente razonable, pero no basta para determinar qué magnitudes representan ambas bases.

**MGE-G01/G02:** OPEN.

---

### MGE-A1-03 — “Margen porcentual” no tiene denominador autorizado

No existe evidencia para decidir entre:

```text
(sale - cost) / sale
```

y
```text
(sale - cost) / cost
```

La primera y la segunda no son equivalentes. Adoptar una por conocimiento general introduciría política no autorizada.

**MGE-G03:** OPEN — REQUIERE AUTORIDAD EMPRESARIAL.

---

### MGE-A1-04 — TCO no es base de margen por defecto

TCO Core calcula coste total atribuible de adquisición y preserva su propia frontera de autoridad.

Su contrato no establece:

```text
TCO == margin_cost_basis
```

Ni la existencia de un resultado TCO permite a MGE apropiarse de él como coste sin política explícita.

**Resultado:** prohibición confirmada de equivalencia implícita.

---

### MGE-A1-05 — PRICE tampoco define la base de margen

Price Intelligence gobierna PR de compra y comparabilidad histórica. No gobierna precio de venta ni base de rentabilidad.

`PR`, `purchase_operation.unit_price` y `sale_price` son conceptos distintos.

**Resultado:** separación confirmada.

---

### MGE-A1-06 — Fuente/selección del precio de venta no está cerrada

La documentación reconoce `precio de venta`, pero no autoriza seleccionar automáticamente:

- tarifa;
- último precio vendido;
- promedio;
- precio contractual;
- precio promocional;
- forecast;
- precio estándar.

**MGE-G04:** OPEN — REQUIERE POLÍTICA DE FUENTE/APLICABILIDAD o input ya autorizado externamente.

---

### MGE-A1-07 — Descuentos y rappels están reconocidos, pero no tienen regla de atribución MGE

MED/Especificación Funcional indican que deben poder considerarse. El catálogo contiene MGE-005/006 como valores de trabajo.

No se ha demostrado:

- si ajustan coste o ingreso;
- si se usan siempre;
- si un rappel futuro/condicional puede atribuirse a esta operación;
- cómo prorratear una bonificación por volumen/periodo;
- qué hacer si su consecución es incierta.

**MGE-G05/G06:** OPEN.

---

### MGE-A1-08 — MGE-004/005/006 no tienen consumidor individual demostrado

La Matriz P→R v0.9 mantiene:

```text
P-MGE-004 a P-MGE-006 → Pendiente de identificación documental individual
```

Por tanto:

- MGE-004 (€5 absoluto) no puede insertarse en R-MGE-001 por coincidencia temática;
- MGE-005/006 no pueden convertirse en switches operativos de descuentos/rappels;
- sus valores iniciales no son política definitiva.

**MGE-G07/G08/G09:** OPEN.

---

### MGE-A1-09 — Los valores 20% / 30% / 3 pp son valores de trabajo

El Catálogo v0.3 declara sus valores iniciales sujetos a validación real.

Las relaciones parámetro→regla están confirmadas, pero no la adopción empresarial definitiva de esos valores para todas las empresas.

**Corrección:** MGE debe consumir configuración vigente/versionada; nunca hardcodear 20/30/3.

---

### MGE-A1-10 — FX/conversión no necesita una política propia para cerrar el core

Puede cerrarse una regla metodológica negativa:

> si venta y coste no son monetaria/unidad comparables y no existe normalización autorizada, el margen es no determinable.

No es necesario inventar un motor FX MGE.

**MGE-G10:** CERRABLE como `NO IMPLICIT FX/UNIT CONVERSION`; la conversión concreta permanece externa.

---

### MGE-A1-11 — R-MGE no debe ejecutarse dentro del cálculo de margen

`R-MGE-001/002/003` tienen condiciones y resultados propios, algunos con outcomes alternativos según resolubilidad/contexto.

La capacidad MGE no debe decidir:

- `NO COMPRAR` vs `NEGOCIAR`;
- `NEGOCIAR` vs `COMPRAR CONDICIONADO`;
- escalado R1→R0;
- severidad efectiva.

**Resultado:** MGE entrega magnitudes/estados; Rules produce Assessment.

---

## 3. Qué puede cerrarse sin nueva política

Puede cerrarse metodológicamente:

1. identidad/versionado del análisis;
2. representación trazable de venta y coste;
3. separación PRICE/TCO/MGE;
4. estado explícito de ausencia/contradicción/no determinabilidad;
5. compatibilidad obligatoria de moneda/unidad;
6. no FX/conversión implícita;
7. no hardcodeo de parámetros;
8. no outcomes de regla;
9. no decisión/recomendación.

---

## 4. Qué no puede cerrarse sin autoridad empresarial

Permanece materialmente bloqueado:

1. **MGE-G01:** base económica de venta;
2. **MGE-G02:** base de coste;
3. **MGE-G03:** denominador del margen porcentual;
4. **MGE-G04:** fuente/aplicabilidad del precio de venta;
5. **MGE-G05:** atribución de descuentos;
6. **MGE-G06:** atribución de rappels.

Estos seis puntos afectan directamente al valor de margen y no pueden resolverse como simple detalle técnico.

---

## 5. Decisión de depuración

Depurar a v0.2 con dos subfronteras explícitas:

```text
Profitability Evidence
    → representa bases y evidencia

Authorized Margin Calculation
    → solo existe cuando G01…G06 estén autorizados
```

Los gaps G07…G09 de parámetros no bloquean la representación/calculadora si esos parámetros no se consumen hasta tener relación autorizada.

G10 se cierra negativamente: no conversión implícita.

---

## 6. Siguiente paso

1. materializar diseño depurado v0.2;
2. ejecutar Audit 2 estructural;
3. preparar un único paquete conservador de autoridad empresarial para MGE-G01…G06;
4. **no implementar código antes de dicha autorización**.

---

## 7. Dictamen

**AUDIT 1: SUPERADA CON DEPURACIÓN OBLIGATORIA.**

No existe autorización para una fórmula cuantitativa MGE todavía.
