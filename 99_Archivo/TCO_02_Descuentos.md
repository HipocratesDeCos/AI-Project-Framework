# TCO_02_Descuentos

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.2  
**Estado:** PROPUESTA — limpieza de arquitectura

---

## 1. Propósito

Definir el tratamiento de los descuentos confirmados y su relación con CEA y escenarios.

---

## 2. Descuento confirmado

Un descuento confirmado y aplicable a la operación puede modificar el:

[[CEA_Coste_Efectivo]]

inmediato.

---

## 3. Descuento condicionado

Un descuento condicionado no debe tratarse como beneficio cierto hasta que se cumpla la condición.

---

## 4. Escenarios

Cuando cambia el descuento:

```text
nuevo descuento
      ↓
[[Motor_Escenarios]]
      ↓
nuevo CEA
      ↓
revisión TCO / recomendación
```

El escenario anterior se conserva.

---

## 5. Relaciones

- [[CEA_Coste_Efectivo]]
- [[TCO_01_Precio]]
- [[TCO_03_Rappels]]
- [[TCO_11_Fronteras]]
- [[Motor_Escenarios]]

---

## 6. Estado

**PROPUESTA v0.2 — pendiente de aprobación.**
