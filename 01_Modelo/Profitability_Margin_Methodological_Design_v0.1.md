# EIOS — RENTABILIDAD / MARGEN · DISEÑO METODOLÓGICO v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Ámbito:** Capacidad analítica transversal de Rentabilidad/Margen (MGE)

---

## 1. Propósito

Definir la frontera metodológica mínima para representar y, cuando exista autoridad suficiente, calcular el impacto de una propuesta de compra sobre la rentabilidad/margen sin crear una nueva capa arquitectónica, sin sustituir PRICE/TCO y sin ejecutar las reglas `R-MGE-001/002/003`.

La capacidad MGE deberá poder proporcionar a las capas posteriores magnitudes económicas trazables de margen y su estado de determinabilidad.

Este documento **no autoriza todavía una fórmula definitiva de margen**.

---

## 2. Autoridades

Se subordina a:

- `03_Arquitectura/Architecture_Blueprint.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `04_Reglas/Evidence_Contract.md`;
- autoridades cerradas de PRICE y TCO.

La similitud semántica entre “precio”, “coste”, “TCO”, “margen” o “rentabilidad” no transfiere autoridad entre dominios.

---

## 3. Posición arquitectónica

El Architecture Blueprint no define una “Capa 6 — Margen”.

Por tanto, MGE se trata como **capacidad analítica de dominio** que puede alimentar Rules/Viability/MED cuando la autoridad lo permita.

No se modifica la secuencia arquitectónica cerrada de capas 0–5.

---

## 4. Frontera de responsabilidad

MGE puede:

- representar precio de venta evidenciado;
- representar una base de coste cuando su definición esté autorizada;
- representar descuentos/rappels cuando su aplicabilidad económica esté demostrada;
- conservar moneda, unidad, cantidad, fecha, fuente y transformación;
- distinguir margen en importe de margen porcentual;
- consumir resultados de PRICE/TCO cuando una política MGE autorizada determine que corresponden;
- comparar un resultado de margen con parámetros MGE confirmados una vez que la metodología de cálculo esté cerrada;
- preservar ausencia, contradicción e insuficiencia.

MGE no puede:

- asumir que precio de compra = coste de margen;
- asumir que TCO = coste de margen;
- elegir gross margin vs markup por convención externa;
- inventar precio de venta;
- inventar descuentos o rappels;
- convertir valores iniciales del catálogo en política definitiva;
- ejecutar R-MGE-001/002/003;
- elegir entre resultados alternativos de una regla;
- producir Assessment/CRC/recomendación/decisión.

---

## 5. Principios

### MGE-P01 — Magnitudes separadas

Mantener separados:

```text
purchase_price
reference_price
acquisition_tco
margin_cost_basis
sale_price
margin_amount
margin_percentage
```

Ninguna igualdad entre ellas se presume.

### MGE-P02 — Margen ≠ markup

No se utilizarán indistintamente “margen porcentual” y “markup”. El denominador de la ratio debe ser una autoridad explícita.

### MGE-P03 — TCO ≠ base de margen por defecto

TCO gobierna coste total atribuible de adquisición. Solo puede intervenir como `margin_cost_basis` si una autoridad MGE lo establece expresamente.

### MGE-P04 — Ausencia ≠ cero

Falta de precio de venta, coste, descuento, rappel o transformación necesaria no se sustituye por cero.

### MGE-P05 — Misma base económica

Toda resta o ratio requiere compatibilidad de moneda, unidad, alcance y referencia temporal. No existe FX implícito ni conversión de unidad implícita.

### MGE-P06 — Cálculo ≠ regla

MGE produce magnitudes analíticas. `R-MGE-001/002/003` pertenecen a Rules y consumen resultados autorizados; MGE no produce su outcome.

---

## 6. MGE-M01 — Identidad del análisis

Toda evaluación de margen debe poder reconstruirse por:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
article_id
company_scope
evaluation_date
methodology_version
```

No se crea un contexto paralelo a `DecisionContext`.

---

## 7. MGE-M02 — Precio de venta

`sale_price` representa el precio de venta económicamente aplicable al objeto y contexto evaluado.

Requisitos mínimos conceptuales:

```text
value
currency
unit_or_basis
applicable_scope
reference_date_or_validity
source_ref
state
```

No se selecciona automáticamente:

- último precio de venta;
- precio medio;
- tarifa;
- precio promocional;
- precio estimado;
- precio histórico.

La fuente/regla de selección del precio de venta permanece pendiente si no está demostrada por autoridad competente.

---

## 8. MGE-M03 — Base de coste para margen

La base de coste se representa como un concepto independiente:

```text
margin_cost_basis
```

Puede provenir de una fuente o resultado autorizado, pero v0.1 **no determina todavía** cuál de las siguientes alternativas es la oficial:

- precio de compra bruto;
- precio de compra neto;
- precio tras descuentos;
- precio tras rappels;
- TCO de adquisición;
- otra base contable/económica autorizada.

La base debe conservar:

```text
value
currency
unit_or_basis
cost_basis_type
source_ref
transformation_ref
state
```

No se puede calcular margen determinado sin una base de coste determinada y autorizada.

---

## 9. MGE-M04 — Descuentos y rappels

La Especificación Funcional y MED reconocen impacto de descuentos/rappels, y el catálogo contiene `MGE-005` y `MGE-006` como valores de trabajo.

Sin embargo, no se ha demostrado todavía que:

- deban aplicarse siempre;
- cómo deben imputarse;
- en qué momento económico;
- qué rappel es atribuible a una operación concreta;
- si ajustan el coste, el ingreso u otra magnitud;
- cómo tratar descuentos condicionales o futuros.

Por tanto:

- se representan como componentes separados y evidenciados;
- no se aplican a la fórmula sin una regla de atribución/autorización;
- `MGE-005/006` no se convierten en comportamiento definitivo por su valor inicial de catálogo.

---

## 10. MGE-M05 — Margen en importe

La existencia funcional de “margen en euros” está autorizada, pero la fórmula depende de cerrar `margin_cost_basis` y `sale_price`.

Relación conceptual mínima, **no aún fórmula normativa cerrada**:

```text
margin_amount = economic_sale_basis - authorized_margin_cost_basis
```

El término `economic_sale_basis` evita asumir que `sale_price` bruto sea siempre la base final sin políticas de descuentos/impuestos u otros ajustes.

Hasta cerrar esas bases, `margin_amount` permanece `NOT_DETERMINABLE`.

---

## 11. MGE-M06 — Margen porcentual

La documentación exige “margen porcentual” pero no demuestra su denominador.

No se autoriza asumir por conocimiento general:

```text
(sale - cost) / sale
```

ni:

```text
(sale - cost) / cost
```

La primera suele corresponder a margin ratio y la segunda a markup, pero EIOS requiere una definición empresarial explícita.

Por tanto, el porcentaje permanece no calculable hasta que el denominador sea autorizado.

---

## 12. MGE-M07 — Parámetros confirmados

Relaciones actualmente demostradas:

```text
P-MGE-001 → R-MGE-001  (margen mínimo)
P-MGE-002 → R-MGE-003  (margen objetivo)
P-MGE-003 → R-MGE-002  (tolerancia)
```

Estos vínculos no autorizan por sí mismos:

- la fórmula de margen;
- la unidad exacta si la regla/parametrización no la demuestra físicamente;
- los valores iniciales 20%, 30% y 3 pp como política definitiva.

`P-MGE-004…006` permanecen pendientes de identificación documental individual.

---

## 13. MGE-M08 — Clasificación analítica respecto a umbrales

Una vez que exista un `margin_percentage` determinado bajo metodología cerrada, MGE podrá potencialmente publicar comparaciones factuales contra parámetros autorizados, por ejemplo:

```text
below_minimum
within_tolerance_to_target
at_or_above_target
```

Pero v0.1 no las materializa como outcomes de regla.

La semántica exacta de “dentro de tolerancia” deberá respetar la regla/parametrización vigente y no se inventa aquí.

---

## 14. MGE-M09 — Estados de datos

Estados conceptuales mínimos:

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_APPLICABLE
NOT_DETERMINABLE
```

Reglas:

- estado no determinado no publica valor económico;
- contradicción conserva todas las evidencias;
- no aplicabilidad requiere exclusión demostrada;
- falta de una política necesaria produce `NOT_DETERMINABLE`, no cero.

Los estados físicos definitivos se cerrarán en contrato técnico posterior.

---

## 15. MGE-M10 — Moneda y unidad

Para calcular un margen:

```text
sale basis.currency == cost basis.currency
sale basis.unit/basis compatible with cost basis.unit/basis
```

Cuando no sean compatibles:

- no se inventa FX;
- no se inventa factor de conversión;
- no se agregan magnitudes silenciosamente.

Una normalización solo puede consumirse si proviene de una autoridad trazable.

---

## 16. MGE-M11 — Temporalidad

El precio de venta y la base de coste deben ser aplicables al contexto temporal de la propuesta.

No se autoriza seleccionar por defecto:

- último valor conocido;
- valor más reciente sin criterio;
- valor histórico medio;
- valor futuro previsto.

La política de vigencia/selección deberá ser explícita.

---

## 17. MGE-M12 — Salida conceptual

```text
profitability_identity
sale_basis
margin_cost_basis
discount_components
rebate_components
margin_amount
margin_percentage
parameter_comparison_refs
unresolved_items
conflicting_items
source_refs
trace_refs
```

No contiene:

```text
Assessment
Rule outcome
Effect
Severity
CRC result
Recommendation
Purchase decision
```

---

## 18. Gaps de autoridad iniciales

| Gap | Materia | Estado inicial |
|---|---|---|
| MGE-G01 | Definición de base económica de venta (`economic_sale_basis`) | OPEN |
| MGE-G02 | Definición de `margin_cost_basis` | OPEN |
| MGE-G03 | Fórmula/denominador de margen porcentual vs markup | OPEN |
| MGE-G04 | Fuente/selección/vigencia de precio de venta | OPEN |
| MGE-G05 | Tratamiento e imputación de descuentos | OPEN |
| MGE-G06 | Tratamiento e imputación de rappels | OPEN |
| MGE-G07 | Consumidor/función exacta P-MGE-004 | OPEN |
| MGE-G08 | Consumidor/función exacta P-MGE-005 | OPEN |
| MGE-G09 | Consumidor/función exacta P-MGE-006 | OPEN |
| MGE-G10 | Política FX/conversión cuando moneda/unidad difieren | OPEN |

---

## 19. Criterio de Audit 1

Audit 1 deberá:

1. recuperar cualquier autoridad histórica existente para MGE-G01…G10;
2. distinguir fórmula empresarial de mera representación de datos;
3. impedir que TCO/PRICE sean reutilizados por semejanza semántica;
4. comprobar si MGE-004/005/006 son parámetros reales, metodológicos o deuda de catálogo;
5. determinar qué parte del core puede cerrarse sin nueva política;
6. agrupar en un único paquete cualquier definición empresarial que requiera autorización humana.

---

## 20. Estado

**DISEÑO v0.1 — PENDIENTE DE AUDIT 1.**

No autoriza código ni cálculo cuantitativo de margen.
