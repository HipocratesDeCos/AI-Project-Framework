# TCO_07_Impuestos

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.3  
**Estado:** PROPUESTA — pendiente de aprobación

---

## 1. Propósito

Definir cómo debe tratar EIOS los impuestos asociados a una operación de compra dentro del análisis del TCO directo.

---

## 2. Principio fundamental

No todos los impuestos constituyen un coste económico de adquisición para la empresa.

Por tanto:

> **EIOS no debe sumar automáticamente cualquier impuesto al TCO.**

---

## 3. Variable obligatoria de tratamiento

**Tratamiento_Impuesto**

Valores:

- `RECUPERABLE`
- `NO_RECUPERABLE`
- `PARCIALMENTE_RECUPERABLE`
- `DESCONOCIDO`

---

## 4. Impuesto recuperable

Cuando sea recuperable:

→ no debe incorporarse como coste económico directo del TCO.

Puede mantenerse como dato de la operación y para análisis financiero cuando corresponda.

---

## 5. Impuesto no recuperable

Cuando constituya un coste definitivo:

→ **CAPA 2 — TCO directo**

---

## 6. Impuestos parcialmente recuperables

Debe separarse:

- parte recuperable;
- parte no recuperable.

Solo la parte no recuperable puede formar parte del TCO económico directo.

---

## 7. Impuesto incluido en el precio

Si el precio ya incorpora el impuesto correspondiente:

EIOS no debe añadir nuevamente el mismo importe.

---

## 8. Precio sin impuestos

Cuando la oferta se presente sin impuestos:

EIOS debe mantener separadas:

- base;
- impuesto;
- importe total.

---

## 9. Impuesto condicionado o incierto

Si la aplicación depende de una condición todavía no determinada:

- no tratarlo como coste cierto sin base;
- registrar la condición;
- conservar la incertidumbre.

---

## 10. Impuesto y arancel

**Arancel ≠ Impuesto**

Deben mantenerse identificados aunque uno forme parte de la base de cálculo del otro.

---

## 11. Impuesto y TCO

El tratamiento económico del impuesto y el momento de pago deben distinguirse.

La parte no recuperable puede formar parte del TCO directo.

El impacto temporal de caja pertenece al análisis financiero cuando corresponda.

---

## 12. Impuesto y CAPA 3

No debe confundirse con costes posteriores derivados de stock.

---

## 13. Impuesto y CAPA 4

El efecto financiero de pago y liquidez puede pertenecer a CAPA 4, sin convertir automáticamente el impuesto recuperable en coste de TCO.

---

## 14. Trazabilidad

Cuando un impuesto influya en TCO, conservar:

- tratamiento;
- tipo;
- base;
- porcentaje;
- importe;
- parte recuperable;
- parte no recuperable;
- condición;
- fecha;
- operación;
- escenario;
- fuente.

---

## 15. Doble contabilización

Evitar:

- sumar impuestos ya incluidos;
- sumar dos veces;
- tratar recuperables como costes definitivos;
- duplicar el mismo efecto entre capas.

---

## 16. Escenarios

Si cambia una condición fiscal relevante:

- nuevo escenario;
- conservación del anterior;
- recálculo;
- nueva evaluación.

---

## 17. Regla de seguridad

> **La parte no recuperable puede formar parte del TCO directo.**

> **La parte recuperable no debe inflar el coste económico de adquisición.**

> **El tratamiento desconocido debe conservarse como incertidumbre.**

---

## 18. Relaciones estructurales

- [[TCO_06_Aranceles]]
- [[TCO_11_Fronteras]]
- [[Motor_Escenarios]]
- [[CAPA_04_Finanzas]]

---

## 19. Estado

**PROPUESTA v0.3 — pendiente de aprobación.**
