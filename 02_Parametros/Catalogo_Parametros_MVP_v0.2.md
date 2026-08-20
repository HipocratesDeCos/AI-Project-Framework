# CATÁLOGO DE PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.3  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Última actualización:** 20/08/2026

---

# 1. Propósito

El Catálogo de Parámetros MVP define los valores que pueden ser configurados para adaptar EIOS a las políticas, características y necesidades de cada empresa.

Los valores incluidos son valores iniciales de trabajo y deberán validarse mediante casos reales antes de convertirse en configuración empresarial definitiva.

---

# 2. Principio fundamental

Los parámetros deben permanecer separados de la lógica del motor de decisión.

El motor define cómo funciona una regla.

El parámetro define con qué valor o criterio debe aplicarse esa regla.

Ningún parámetro ordinario puede desactivar una regla crítica, anular una restricción no anulable o habilitar una excepción no autorizada.

---

# 3. Parámetros de referencia de precios

| ID | Parámetro | Valor inicial | Unidad | Afecta a | Estado |
|---|---|---:|---|---|---|
| PRE-001 | Periodo principal de comparación | 3 | meses | Comparación de precios | Pendiente de validación |
| PRE-002 | Periodo ampliado de comparación | 12 | meses | Análisis histórico | Pendiente de validación |
| PRE-003 | Antigüedad máxima de referencia | 12 | meses | Validez histórica | Pendiente de validación |
| PRE-004 | Diferencia para activar alerta de precio | 5 | % | Negociación | Pendiente de validación |
| PRE-005 | Diferencia para alerta crítica de precio | 10 | % | Negociación | Pendiente de validación |
| PRE-006 | Nº mínimo de compras comparables | 2 | operaciones | Fiabilidad | Pendiente de validación |

---

# 4. Parámetros de stock

| ID | Parámetro | Valor inicial | Unidad | Afecta a | Estado |
|---|---|---:|---|---|---|
| STK-001 | Stock mínimo | Pendiente | unidades | Riesgo de rotura | Pendiente de datos |
| STK-002 | Stock de seguridad | 15 | % del consumo | Riesgo | Pendiente de validación |
| STK-003 | Cobertura mínima | 30 | días | Compras | Pendiente de validación |
| STK-004 | Cobertura máxima | 90 | días | Exceso de stock | Pendiente de validación |
| STK-005 | Tolerancia de exceso | 10 | % | Alerta | Pendiente de validación |
| STK-006 | Periodo para calcular consumo | 12 | meses | Proyección | Pendiente de validación |

**Nota:** Los parámetros de stock podrán personalizarse posteriormente por artículo o familia cuando exista información suficiente.

---

# 5. Parámetros de proyección de stock

| ID | Parámetro | Valor inicial | Unidad | Estado |
|---|---|---:|---|---|
| PYE-001 | Horizonte de proyección | 90 | días | Pendiente de validación |
| PYE-002 | Considerar pedidos pendientes | Sí | Sí/No | Pendiente de validación |
| PYE-003 | Considerar compras en tránsito | Sí | Sí/No | Pendiente de validación |
| PYE-004 | Considerar plazo de entrega | Sí | Sí/No | Pendiente de validación |
| PYE-005 | Considerar ventas históricas | Sí | Sí/No | Pendiente de validación |
| PYE-006 | Umbral de riesgo de rotura | 15 | días | Pendiente de validación |

---

# 6. Parámetros de rentabilidad

| ID | Parámetro | Valor inicial | Unidad | Estado |
|---|---|---:|---|---|
| MGE-001 | Margen mínimo | 20 | % | Pendiente de validación |
| MGE-002 | Margen objetivo | 30 | % | Pendiente de validación |
| MGE-003 | Tolerancia de margen | 3 | puntos porcentuales | Pendiente de validación |
| MGE-004 | Margen mínimo absoluto | 5 | € | Pendiente de validación |
| MGE-005 | Considerar descuentos | Sí | Sí/No | Pendiente de validación |
| MGE-006 | Considerar rappels | Sí | Sí/No | Pendiente de validación |

EIOS deberá diferenciar siempre entre margen porcentual y margen en euros.

---

# 7. Parámetros financieros

| ID | Parámetro | Valor inicial | Unidad | Severidad | Editabilidad |
|---|---|---:|---|---|---|
| FIN-001 | Horizonte de pagos | 30 | días | Alta | Restringida |
| FIN-002 | Tesorería mínima | Definida por empresa | € | Crítica | Restringida |
| FIN-003 | Fondo de maniobra mínimo | Definido por empresa | € | Crítica | Restringida |
| FIN-004 | Margen mínimo de seguridad financiera | 10 | % | Alta | Restringida |
| FIN-005 | Considerar pagos futuros | Sí | Sí/No | Crítica | Restringida |
| FIN-006 | Considerar cobros previstos | Sí | Sí/No | Alta | Restringida |

Los parámetros críticos financieros no podrán modificarse mediante parametrización ordinaria sin los controles de autorización, trazabilidad y vigencia correspondientes.

---

# 8. Parámetros de pago y negociación

| ID | Parámetro | Valor inicial | Unidad | Estado |
|---|---|---:|---|---|
| PAG-001 | Plazo de pago mínimo deseado | 60 | días | Pendiente de validación |
| PAG-002 | Plazo de pago objetivo | 90 | días | Pendiente de validación |
| PAG-003 | Tolerancia de plazo | 15 | días | Pendiente de validación |
| PAG-004 | Considerar plazo en negociación | Sí | Sí/No | Pendiente de validación |
| PAG-005 | Considerar descuento por pronto pago | Sí | Sí/No | Pendiente de validación |

---

# 9. Parámetros de reglas

Estos elementos requieren tratamiento diferenciado porque pueden afectar a la activación de reglas y excepciones.

| ID | Parámetro | Valor inicial | Tratamiento MVP |
|---|---|---|---|
| RGL-001 | Activar reglas de precio | Sí | Configurable solo cuando la autoridad documental lo permita |
| RGL-002 | Activar reglas de stock | Sí | Configurable solo cuando la autoridad documental lo permita |
| RGL-003 | Activar reglas de margen | Sí | Configurable solo cuando la autoridad documental lo permita |
| RGL-004 | Activar reglas financieras | Sí | No puede desactivar salvaguardas críticas |
| RGL-005 | Activar reglas de proveedores | Sí | Configurable solo cuando la autoridad documental lo permita |
| RGL-006 | Permitir excepciones | Sí | No habilita excepciones no autorizadas |
| RGL-007 | Permitir compra condicionada | Sí | Pendiente de cruce funcional |

**Principio:** ningún parámetro ordinario puede desactivar una regla crítica, anular una restricción no anulable ni habilitar una excepción no autorizada.

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

**Nota:** la prioridad no constituye autoridad de resolución. La resolución de conflictos corresponde a la CRC y a la autoridad documental aplicable.

---

# 11. Parámetros de calidad de datos

| ID | Parámetro | Valor inicial | Unidad | Tratamiento |
|---|---|---:|---|---|
| DAT-001 | Antigüedad máxima de datos operativos | 6 | semanas | Parámetro de calidad |
| DAT-002 | Antigüedad máxima de referencia de precio | 12 | meses | Parámetro de calidad |
| DAT-003 | Nº mínimo de registros históricos | 2 | operaciones | Parámetro de calidad |
| DAT-004 | Permitir decisión con datos incompletos | No | — | **No incluido como capacidad configurable del MVP** |
| DAT-005 | Mostrar fecha de actualización | Sí | — | Presentación/trazabilidad, no parámetro de decisión |
| DAT-006 | Mostrar nivel de fiabilidad | Sí | — | Calidad/explicabilidad, no parámetro de decisión |
| DAT-007 | Nivel mínimo de fiabilidad para recomendación | Medio | nivel | Parámetro de calidad |

Cuando la información sea insuficiente para sostener una recomendación, EIOS deberá utilizar:

**INFORMACIÓN INSUFICIENTE**

La ausencia de evidencia crítica no podrá convertirse mediante un parámetro ordinario en una recomendación favorable.

---

# 12. Principio de no saturación

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

# 13. Principio de explicabilidad

Cada parámetro de decisión deberá disponer, en la futura interfaz, de:

- nombre;
- valor actual;
- unidad;
- valor estándar;
- descripción;
- efecto de modificarlo.

---

# 14. Principio de parametrización por empresa

Los parámetros deberán poder adaptarse a:

- empresa;
- actividad;
- política comercial;
- política financiera;
- familia de productos;
- artículo, cuando proceda.

La configuración deberá quedar aislada entre empresas.

---

# 15. Clasificación de estado

Cada parámetro deberá clasificarse como:

- Confirmado
- Pendiente de validación
- Pendiente de datos
- No incluido en MVP
- Futuro

Un parámetro sin consumidor funcional o justificación explícita no se considerará parámetro MVP confirmado.

---

# 16. Trazabilidad y cambios críticos

Toda modificación de un parámetro deberá poder relacionarse con:

- valor anterior;
- nuevo valor;
- fecha;
- usuario;
- motivo;
- empresa;
- vigencia;
- estado.

Los parámetros críticos requieren controles específicos de autorización, trazabilidad y vigencia.

---

# 17. Criterio de cierre

El catálogo se considera estructuralmente alineado con las decisiones aprobadas del Decision Log, pero los valores empresariales definitivos y los cruces concretos Parámetro → Regla permanecen sujetos a validación documental y empresarial.

---

# 18. Estado

**Versión:** 0.3  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP
