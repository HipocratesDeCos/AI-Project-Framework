# TCO_01_Precio

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.2  
**Estado:** PROPUESTA — limpieza de arquitectura

---

## 1. Propósito

Definir la relación del precio con TCO y con el CEA dentro de EIOS.

---

## 2. Principio

El precio nominal constituye una entrada fundamental de la operación.

Debe permanecer separado de:

- [[CEA_Coste_Efectivo]]
- [[PR_Precio_Referencia]]
- [[PO_Precio_Objetivo]]
- [[PMR_Precio_Maximo]]

---

## 3. Relación arquitectónica

```text
PRECIO
  │
  ├── inteligencia de precio
  │      ├── PR
  │      ├── PO
  │      └── PMR
  │
  └── condiciones económicas
         │
         ▼
        CEA

PRECIO + costes directos de adquisición
         │
         ▼
        TCO
```

CEA y TCO no son equivalentes.

---

## 4. Escenarios

Cualquier cambio relevante del precio durante una negociación debe pasar por:

[[Motor_Escenarios]]

El escenario anterior se conserva y el nuevo escenario se recalcula.

---

## 5. Relaciones

- [[CEA_Coste_Efectivo]]
- [[TCO_00_Principios]]
- [[TCO_02_Descuentos]]
- [[TCO_03_Rappels]]
- [[TCO_11_Fronteras]]
- [[Motor_Escenarios]]

---

## 6. Estado

**PROPUESTA v0.2 — pendiente de aprobación.**
