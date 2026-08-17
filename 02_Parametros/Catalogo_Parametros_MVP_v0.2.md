# CATÁLOGO DE PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** En desarrollo  
**Última actualización:** 17/08/2026

---

# 1. Propósito

El Catálogo de Parámetros MVP define los valores que pueden ser configurados para adaptar EIOS a las políticas, características y necesidades de cada empresa.

Los valores incluidos en esta primera versión son valores iniciales de trabajo y deberán validarse mediante casos reales antes de convertirse en configuración definitiva.

---

# 2. Principio fundamental

Los parámetros deben permanecer separados de la lógica del motor de decisión.

El motor define cómo funciona una regla.

El parámetro define con qué valor o criterio debe aplicarse esa regla.

Esto permitirá adaptar EIOS a diferentes empresas sin modificar el núcleo de la aplicación.

---

# 3. Parámetros de referencia de precios

| ID | Parámetro | Valor inicial | Unidad | Afecta a |
|---|---|---:|---|---|
| PRE-001 | Periodo principal de comparación | 3 | meses | Comparación de precios |
| PRE-002 | Periodo ampliado de comparación | 12 | meses | Análisis histórico |
| PRE-003 | Antigüedad máxima de referencia | 12 | meses | Validez histórica |
| PRE-004 | Diferencia para activar alerta de precio | 5 | % | Negociación |
| PRE-005 | Diferencia para alerta crítica de precio | 10 | % | Negociación |
| PRE-006 | Nº mínimo de compras comparables | 2 | operaciones | Fiabilidad |

---

# 4. Parámetros de stock

| ID | Parámetro | Valor inicial | Unidad | Afecta a |
|---|---|---:|---|---|
| STK-001 | Stock mínimo | Pendiente | unidades | Riesgo de rotura |
| STK-002 | Stock de seguridad | 15 | % del consumo | Riesgo |
| STK-003 | Cobertura mínima | 30 | días | Compras |
| STK-004 | Cobertura máxima | 90 | días | Exceso de stock |
| STK-005 | Tolerancia de exceso | 10 | % | Alerta |
| STK-006 | Periodo para calcular consumo | 12 | meses | Proyección |

**Nota:** Los parámetros de stock podrán ser personalizados posteriormente por artículo o familia cuando exista información suficiente.

---

# 5. Parámetros de proyección de stock

| ID | Parámetro | Valor inicial | Unidad |
|---|---|---:|---|
| PYE-001 | Horizonte de proyección | 90 | días |
| PYE-002 | Considerar pedidos pendientes | Sí | Sí/No |
| PYE-003 | Considerar compras en tránsito | Sí | Sí/No |
| PYE-004 | Considerar plazo de entrega | Sí | Sí/No |
| PYE-005 | Considerar ventas históricas | Sí | Sí/No |
| PYE-006 | Umbral de riesgo de rotura | 15 | días |

---

# 6. Parámetros de rentabilidad

| ID | Parámetro | Valor inicial | Unidad |
|---|---|---:|---|
| MGE-001 | Margen mínimo | 20 | % |
| MGE-002 | Margen objetivo | 30 | % |
| MGE-003 | Tolerancia de margen | 3 | puntos porcentuales |
| MGE-004 | Margen mínimo absoluto | 5 | € |
| MGE-005 | Considerar descuentos | Sí | Sí/No |
| MGE-006 | Considerar rappels | Sí | Sí/No |

EIOS deberá diferenciar siempre entre margen porcentual y margen en euros.

---

# 7. Parámetros financieros

| ID | Parámetro | Valor inicial | Unidad | Severidad |
|---|---|---:|---|---|
| FIN-001 | Horizonte de pagos | 30 | días | Alta |
| FIN-002 | Tesorería mínima | Definida por empresa | € | Crítica |
| FIN-003 | Fondo de maniobra mínimo | Definido por empresa | € | Crítica |
| FIN-004 | Margen mínimo de seguridad financiera | 10 | % | Alta |
| FIN-005 | Considerar pagos futuros | Sí | Sí/No | Crítica |
| FIN-006 | Considerar cobros previstos | Sí | Sí/No | Alta |

---

# 8. Parámetros de pago y negociación

| ID | Parámetro | Valor inicial | Unidad |
|---|---|---:|---|
| PAG-001 | Plazo de pago mínimo deseado | 60 | días |
| PAG-002 | Plazo de pago objetivo | 90 | días |
| PAG-003 | Tolerancia de plazo | 15 | días |
| PAG-004 | Considerar plazo en negociación | Sí | Sí/No |
| PAG-005 | Considerar descuento por pronto pago | Sí | Sí/No |

---

# 9. Parámetros de reglas

| ID | Parámetro | Valor inicial |
|---|---|---|
| RGL-001 | Activar reglas de precio | Sí |
| RGL-002 | Activar reglas de stock | Sí |
| RGL-003 | Activar reglas de margen | Sí |
| RGL-004 | Activar reglas financieras | Sí |
| RGL-005 | Activar reglas de proveedores | Sí |
| RGL-006 | Permitir excepciones | Sí |
| RGL-007 | Permitir compra condicionada | Sí |

---

# 10. Prioridad de reglas

| Prioridad | Categoría | Ejemplo |
|---:|---|---|
| 1 | Financiera crítica | Riesgo de no poder pagar |
| 2 | Rentabilidad crítica | Margen insuficiente |
| 3 | Stock crítico | Rotura probable |
| 4 | Precio | Precio excesivo |
| 5 | Condiciones | Plazo de pago desfavorable |
| 6 | Operativa | Otras incidencias |

---

# 11. Parámetros de calidad de datos

| ID | Parámetro | Valor inicial | Unidad |
|---|---|---:|---|
| DAT-001 | Antigüedad máxima de datos operativos | 6 | semanas |
| DAT-002 | Antigüedad máxima de referencia de precio | 12 | meses |
| DAT-003 | Nº mínimo de registros históricos | 2 | operaciones |
| DAT-004 | Permitir decisión con datos incompletos | Sí, con advertencia | — |
| DAT-005 | Mostrar fecha de actualización | Sí | — |
| DAT-006 | Mostrar nivel de fiabilidad | Sí | — |
| DAT-007 | Nivel mínimo de fiabilidad para recomendación | Medio | nivel |

---

# 12. Nivel de fiabilidad

EIOS deberá poder clasificar la calidad de la información disponible como:

- Alta
- Media
- Baja
- Insuficiente

Cuando la información sea insuficiente para sostener una recomendación, EIOS deberá utilizar:

**INFORMACIÓN INSUFICIENTE**

---

# 13. Principio de no saturación

Aunque el catálogo pueda crecer, el usuario final no deberá visualizar todos los parámetros simultáneamente.

El Centro de Parametrización deberá organizarlos por categorías:

- Precios
- Stock
- Proyección
- Rentabilidad
- Finanzas
- Pagos y negociación
- Reglas
- Calidad de datos

---

# 14. Principio de explicabilidad

Cada parámetro deberá disponer, en la futura interfaz, de:

- nombre;
- valor actual;
- unidad;
- valor estándar;
- descripción;
- efecto de modificarlo.

---

# 15. Principio de parametrización por empresa

Los parámetros deberán poder adaptarse a:

- empresa;
- actividad;
- política comercial;
- política financiera;
- familia de productos;
- artículo, cuando proceda.

---

# 16. Estado del catálogo

Este catálogo es una versión MVP inicial.

Los parámetros deberán clasificarse posteriormente como:

- Confirmado
- Pendiente de validación
- Pendiente de datos
- No incluido en MVP
- Futuro

---

# 17. Próximo trabajo

El catálogo deberá cruzarse con la Matriz de Reglas MVP para determinar:

1. qué parámetro utiliza cada regla;
2. qué regla modifica cada parámetro;
3. qué parámetros son críticos;
4. qué parámetros son editables;
5. qué parámetros son específicos de empresa;
6. qué valores necesitan validación;
7. qué parámetros pueden eliminarse para evitar complejidad innecesaria.
