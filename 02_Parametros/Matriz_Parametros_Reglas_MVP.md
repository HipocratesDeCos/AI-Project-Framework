# MATRIZ DE PARÁMETROS Y REGLAS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de validación  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 19/08/2026

---

# 1. PROPÓSITO

Esta matriz establece el vínculo funcional entre los parámetros configurables de EIOS y las reglas empresariales que los utilizan.

Su finalidad es determinar, para cada parámetro:

- qué regla lo utiliza;
- qué función cumple;
- si es crítico;
- si puede ser editable;
- si es específico de empresa;
- si pertenece realmente al MVP;
- si requiere validación adicional.

La matriz no sustituye a la Matriz de Reglas ni al Catálogo de Parámetros. Actúa como documento de enlace entre ambas capas.

---

# 2. PRINCIPIO DE AUTORIDAD

Esta matriz no define por sí misma la autoridad de resolución de conflictos.

La prioridad funcional de una regla no equivale necesariamente a su autoridad.

La resolución de resultados incompatibles corresponde a la Capa de Resolución de Conflictos (CRC) y a los documentos que tengan autoridad sobre dicha materia.

---

# 3. ESTADO DE LA EVIDENCIA

La matriz se construye a partir de los parámetros actualmente definidos en `02_Parametros/Catalogo_Parametros_MVP_v0.2.md` y de la documentación de reglas disponible en el repositorio.

Cuando no exista evidencia documental suficiente para afirmar que un parámetro está conectado a una regla concreta, se marcará como:

**PENDIENTE DE CRUCE CON REGLAS**

No se inventarán relaciones parámetro-regla.

---

# 4. CRITERIOS

| Campo | Significado |
|---|---|
| Parámetro | Identificador oficial del catálogo |
| Regla | Regla que consume el parámetro |
| Función | Papel funcional del parámetro |
| Crítico | Si su modificación puede afectar a una salvaguarda o bloqueo relevante |
| Editable | Si puede ser modificado mediante parametrización ordinaria |
| Empresa | Si puede variar por empresa |
| MVP | Si debe formar parte del MVP |
| Estado | Situación de validación |

---

# 5. MATRIZ DE PARÁMETROS

## 5.1 Precios

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| PRE-001 | Periodo principal de comparación | Pendiente | Ventana histórica | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PRE-002 | Periodo ampliado de comparación | Pendiente | Referencia histórica ampliada | No determinado | Sí | Sí | Pendiente | Pendiente de cruce |
| PRE-003 | Antigüedad máxima de referencia | Pendiente | Validez de referencia | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PRE-004 | Diferencia para activar alerta de precio | Pendiente | Umbral de negociación | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PRE-005 | Diferencia para alerta crítica de precio | Pendiente | Umbral crítico | Sí potencial | Restringida | Sí | Sí | Pendiente de validación |
| PRE-006 | Nº mínimo de compras comparables | Pendiente | Fiabilidad estadística | No determinado | Sí | Sí | Sí | Pendiente de cruce |

## 5.2 Stock

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| STK-001 | Stock mínimo | Pendiente | Umbral de stock | Potencial | Sí | Sí | Sí | Valor pendiente |
| STK-002 | Stock de seguridad | Pendiente | Protección de stock | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| STK-003 | Cobertura mínima | Pendiente | Umbral de cobertura | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| STK-004 | Cobertura máxima | Pendiente | Umbral de exceso | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| STK-005 | Tolerancia de exceso | Pendiente | Tolerancia | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| STK-006 | Periodo para calcular consumo | Pendiente | Ventana de consumo | No determinado | Sí | Sí | Sí | Pendiente de cruce |

## 5.3 Proyección de stock

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| PYE-001 | Horizonte de proyección | Pendiente | Horizonte temporal | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PYE-002 | Considerar pedidos pendientes | Pendiente | Fuente de demanda/oferta | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PYE-003 | Considerar compras en tránsito | Pendiente | Oferta futura | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PYE-004 | Considerar plazo de entrega | Pendiente | Cálculo temporal | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PYE-005 | Considerar ventas históricas | Pendiente | Base de proyección | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PYE-006 | Umbral de riesgo de rotura | Pendiente | Umbral crítico | Potencial | Restringida | Sí | Sí | Pendiente de validación |

## 5.4 Rentabilidad

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| MGE-001 | Margen mínimo | Pendiente | Umbral de aceptación | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| MGE-002 | Margen objetivo | Pendiente | Objetivo económico | No | Sí | Sí | Sí | Pendiente de cruce |
| MGE-003 | Tolerancia de margen | Pendiente | Tolerancia | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| MGE-004 | Margen mínimo absoluto | Pendiente | Umbral monetario | Potencial | Sí | Sí | Sí | Pendiente de cruce |
| MGE-005 | Considerar descuentos | Pendiente | Ajuste económico | No | Sí | Sí | Sí | Pendiente de cruce |
| MGE-006 | Considerar rappels | Pendiente | Ajuste económico | No | Sí | Sí | Sí | Pendiente de cruce |

## 5.5 Finanzas

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| FIN-001 | Horizonte de pagos | Pendiente | Ventana financiera | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| FIN-002 | Tesorería mínima | Pendiente | Límite financiero | Sí | Restringida | Sí | Sí | Pendiente de validación |
| FIN-003 | Fondo de maniobra mínimo | Pendiente | Límite financiero | Sí | Restringida | Sí | Sí | Pendiente de validación |
| FIN-004 | Margen mínimo de seguridad financiera | Pendiente | Protección financiera | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| FIN-005 | Considerar pagos futuros | Pendiente | Flujo financiero | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| FIN-006 | Considerar cobros previstos | Pendiente | Flujo financiero | Alta | Restringida | Sí | Sí | Pendiente de cruce |

## 5.6 Pagos y negociación

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| PAG-001 | Plazo de pago mínimo deseado | Pendiente | Condición de negociación | No determinado | Sí | Sí | Sí | Pendiente de cruce |
| PAG-002 | Plazo de pago objetivo | Pendiente | Objetivo de negociación | No | Sí | Sí | Sí | Pendiente de cruce |
| PAG-003 | Tolerancia de plazo | Pendiente | Tolerancia | No | Sí | Sí | Sí | Pendiente de cruce |
| PAG-004 | Considerar plazo en negociación | Pendiente | Activación funcional | No | Sí | Sí | Sí | Pendiente de cruce |
| PAG-005 | Considerar descuento por pronto pago | Pendiente | Condición económica | No | Sí | Sí | Sí | Pendiente de cruce |

## 5.7 Activación de reglas

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| RGL-001 | Activar reglas de precio | Pendiente | Activación | Potencial | Restringida | Sí | Revisar | Pendiente de autoridad |
| RGL-002 | Activar reglas de stock | Pendiente | Activación | Potencial | Restringida | Sí | Revisar | Pendiente de autoridad |
| RGL-003 | Activar reglas de margen | Pendiente | Activación | Potencial | Restringida | Sí | Revisar | Pendiente de autoridad |
| RGL-004 | Activar reglas financieras | Pendiente | Activación | Sí potencial | No ordinaria | Sí | Revisar | Pendiente de autoridad |
| RGL-005 | Activar reglas de proveedores | Pendiente | Activación | Potencial | Restringida | Sí | Revisar | Pendiente de autoridad |
| RGL-006 | Permitir excepciones | Pendiente | Control de excepciones | Sí potencial | No ordinaria | Sí | Revisar | Pendiente de autoridad |
| RGL-007 | Permitir compra condicionada | Pendiente | Resultado permitido | No determinado | Sí | Sí | Sí | Pendiente de cruce |

## 5.8 Calidad de datos

| ID | Parámetro | Regla | Función | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|---|
| DAT-001 | Antigüedad máxima de datos operativos | Pendiente | Calidad temporal | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| DAT-002 | Antigüedad máxima de referencia de precio | Pendiente | Calidad histórica | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| DAT-003 | Nº mínimo de registros históricos | Pendiente | Suficiencia de evidencia | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| DAT-004 | Permitir evaluación con datos incompletos | Pendiente | Control de suficiencia | Sí | No ordinaria | Sí | No en MVP | Requiere decisión |
| DAT-005 | Mostrar fecha de actualización | Pendiente | Transparencia | No | Sí | Sí | Sí | Pendiente de cruce |
| DAT-006 | Mostrar nivel de fiabilidad | Pendiente | Explicabilidad | No | Sí | Sí | Sí | Pendiente de cruce |
| DAT-007 | Nivel mínimo de fiabilidad para recomendación | Pendiente | Umbral de evidencia | Sí | Restringida | Sí | Sí | Pendiente de cruce |

---

# 6. HALLAZGOS PRELIMINARES

## H-01 — DAT-004

El catálogo actual permite decisión con datos incompletos con advertencia. La Especificación Funcional aprobada establece que la información crítica insuficiente debe conducir a `INFORMACIÓN INSUFICIENTE`.

**Propuesta:** excluir DAT-004 del comportamiento configurable del MVP y mantenerlo únicamente como capacidad futura, salvo decisión documental superior en sentido contrario.

## H-02 — RGL-001 a RGL-007

Los parámetros de activación de reglas y excepciones pueden afectar a la integridad de las salvaguardas.

**Propuesta:** ningún parámetro ordinario debe poder desactivar una regla crítica ni anular una restricción no anulable.

## H-03 — Prioridad vs autoridad

La prioridad numérica del catálogo no debe utilizarse como sustituto de la autoridad de resolución de la CRC.

## H-04 — Valores iniciales

Los valores económicos y operativos actuales son valores de trabajo. No deben considerarse valores empresariales definitivos hasta su validación.

## H-05 — Parámetro sin regla

La columna `Regla` permanecerá pendiente mientras no exista evidencia documental suficiente en la Matriz de Reglas MVP.

---

# 7. DECISIONES PENDIENTES

1. Cruzar cada parámetro con la Matriz de Reglas MVP.
2. Confirmar los parámetros realmente necesarios para el MVP.
3. Confirmar cuáles son críticos.
4. Determinar qué parámetros pueden editarse ordinariamente.
5. Determinar qué parámetros son específicos de empresa.
6. Validar los valores iniciales.
7. Resolver definitivamente DAT-004.
8. Resolver la autoridad de RGL-001 a RGL-007.
9. Eliminar parámetros que no tengan consumidor funcional en el MVP.
10. Clasificar los parámetros restantes como Confirmado, Pendiente de validación, Pendiente de datos, No incluido en MVP o Futuro.

---

# 8. ESTADO

**Estado:** PROPUESTA — pendiente de validación.

Esta matriz no debe considerarse baseline oficial hasta completar el cruce con la Matriz de Reglas MVP y resolver los hallazgos críticos identificados.
