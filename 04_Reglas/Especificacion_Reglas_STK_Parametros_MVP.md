# EIOS — Especificación de relaciones STK/PYE ↔ reglas MVP

**Versión:** 1.0
**Estado:** APROBADO — CRUCE DOCUMENTAL STK/PYE CERRADO
**Fecha:** 11/09/2026
**Autoridad derivada:** `04_Reglas/Matriz_Reglas_MVP.md`, autoridades `STK-M01…M10` y `01_Modelo/STK_Contract_Entry_Authority.md`

---

## 1. Propósito

Determinar, sin inferencia nominal, qué parámetros `P-STK-*` y `P-PYE-*` son consumidos directamente o de forma derivada por las reglas `R-STK-001…004`, y cuáles pertenecen a metodología/configuración sin consumidor directo de regla demostrado.

La especificación no valida valores iniciales del catálogo y no crea reglas ni parámetros nuevos.

---

## 2. Principio de cruce

Una relación solo se confirma cuando la condición de la regla y la metodología autorizada permiten demostrarla.

No se considera relación regla ↔ parámetro el mero hecho de que un parámetro intervenga en un cálculo previo del dominio STK.

Se distinguen:

- **DIRECTA**: la condición de la regla consume el parámetro configurado;
- **DERIVADA**: existe una transformación metodológica documentada que conecta el parámetro con la magnitud evaluada por la regla;
- **SIN CONSUMIDOR DIRECTO DEMOSTRADO**: el parámetro puede gobernar metodología o configuración STK, pero no existe evidencia suficiente para asignarlo a una regla concreta.

---

## 3. Cruce P-STK

| Parámetro | Regla | Tipo | Determinación |
|---|---|---|---|
| `P-STK-001` Stock mínimo | — | Sin consumidor directo demostrado | M02 gobierna `stock_minimum`, pero ninguna condición `R-STK-001…004` vigente declara este parámetro como umbral consumidor directo. No se fuerza a `R-STK-001`. |
| `P-STK-002` Stock de seguridad | — | Sin consumidor directo demostrado | M03 gobierna reserva de incertidumbre; puede alimentar políticas de stock mínimo, pero no existe consumo directo demostrado por una regla STK vigente. |
| `P-STK-003` Cobertura mínima | — | Sin consumidor directo demostrado | M04 reconoce umbral mínimo de cobertura como configuración empresarial, pero las reglas STK vigentes no formulan una condición directa contra ese mínimo. |
| `P-STK-004` Cobertura máxima | `R-STK-002` | DIRECTA | `R-STK-002` se activa cuando la cobertura prevista supera el nivel configurado; M04 identifica `coverage_maximum` como umbral empresarial. |
| `P-STK-004` Cobertura máxima | `R-STK-003` | DERIVADA | M07 autoriza que, cuando el máximo se gobierna mediante `coverage_maximum`, se convierta a cantidad utilizando M04 y la demanda aplicable antes de evaluar exceso. |
| `P-STK-005` Tolerancia de exceso | `R-STK-003` | DERIVADA | M07 incorpora explícitamente `excess_tolerance` al umbral de exceso que cuantifica la condición consumida por `R-STK-003`. |
| `P-STK-006` Periodo para calcular consumo | — | Sin consumidor directo demostrado | Gobierna la ventana de la base histórica autorizada por la autoridad de entrada; no es condición directa de `R-STK-001…004`. |

---

## 4. Cruce P-PYE

| Parámetro | Regla | Tipo | Determinación |
|---|---|---|---|
| `P-PYE-001` Horizonte de proyección | — | Sin consumidor directo demostrado | Configura M05; las reglas consumen resultados proyectados, no el horizonte como condición directa demostrada. |
| `P-PYE-002` Considerar pedidos pendientes | — | Sin consumidor directo demostrado | Control metodológico potencial de M05/M06. `Sí` no autoriza inclusión incondicional: toda entrada requiere evidencia M06. |
| `P-PYE-003` Considerar compras en tránsito | — | Sin consumidor directo demostrado | Control metodológico potencial de M05/M06. `Sí` no autoriza inclusión incondicional. |
| `P-PYE-004` Considerar plazo de entrega | — | Sin consumidor directo demostrado | El `lead_time` puede intervenir en temporalidad M05, pero el booleano del catálogo no constituye por sí mismo condición directa de una regla STK. |
| `P-PYE-005` Considerar ventas históricas | — | Sin consumidor directo demostrado / no operativo como transformación | La autoridad de entrada prohíbe convertir ventas en consumo o demanda automáticamente. El valor inicial `Sí` no activa transformación alguna. |
| `P-PYE-006` Umbral de riesgo de rotura | — | Sin consumidor directo demostrado | `R-STK-001` define riesgo por agotamiento antes de nueva recepción, no por un umbral fijo de 15 días. No se fuerza la relación por similitud nominal. |

---

## 5. Reglas STK sin parámetro directo demostrado

### `R-STK-001 — Riesgo de rotura`

Su condición vigente consume una proyección y la temporalidad de la nueva recepción. Ningún `P-STK-*` o `P-PYE-*` queda confirmado como parámetro directo de la regla en esta versión.

Esto no impide que la proyección haya utilizado configuración metodológica versionada; simplemente evita representar dicha configuración como condición de regla cuando la documentación no lo demuestra.

### `R-STK-004 — Excepción por pedido confirmado`

La excepción depende de evidencia de demanda comercial confirmada y de absorción M08. No existe parámetro `P-STK-*` o `P-PYE-*` que gobierne directamente su condición.

---

## 6. Valores iniciales

Ningún cruce de este documento valida como política definitiva:

- 15 % de seguridad;
- 30/90 días de cobertura;
- 10 % de tolerancia;
- 12 meses de consumo;
- 90 días de horizonte;
- booleanos `Sí` de PYE;
- 15 días de riesgo.

Las relaciones existen con independencia del valor concreto que una configuración empresarial autorizada adopte.

---

## 7. Evaluabilidad

Esta especificación demuestra **existencia y tipo de relación**. No asigna por extrapolación `Criticality` ni `Evaluability_Impact` en la RDM.

Cuando una regla requiera una magnitud calculada y dicha magnitud sea `UNKNOWN / NOT_EVIDENCED`, se conserva la no evaluabilidad conforme a M09, C0 y la política aplicable; ello no autoriza a inventar una criticidad de dependencia individual en la matriz transversal.

---

## 8. No regresión

No se permite:

- asignar `P-STK-001`, `002`, `003` o `006` directamente a una regla sin nueva evidencia;
- asignar `P-PYE-001…006` directamente a una regla por nombre o proximidad semántica;
- utilizar `P-PYE-005` para transformar ventas en demanda sin política posterior autorizada;
- convertir valores iniciales en defaults normativos;
- alterar las condiciones de `R-STK-001…004` desde esta especificación.

---

## 9. Estado

El gap documental `P-STK/P-PYE ↔ reglas` identificado en `STK_Contract_Entry_Audit_v0.1.md` queda **CERRADO**.

Relaciones confirmadas para incorporación a la RDM:

1. `P-STK-004 → R-STK-002` — `PARAMETER` / directa;
2. `P-STK-004 → R-STK-003` — `DERIVED`;
3. `P-STK-005 → R-STK-003` — `DERIVED`.

El resto queda explícitamente clasificado como metodología/configuración sin consumidor directo de regla demostrado, no como pendiente genérico.
