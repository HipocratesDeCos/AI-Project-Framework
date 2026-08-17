# CEA_Coste_Efectivo

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Concepto transversal  
**Relación:** CAPA 1 / CAPA 2 / Motor de escenarios  
**Versión:** 0.3  
**Estado:** PROPUESTA — limpieza de arquitectura

---

## 1. Propósito

Definir el **CEA — Coste Efectivo de Adquisición** como una métrica económica transversal de la operación.

CEA no es una capa independiente ni una subcapa de TCO.

---

## 2. Principio fundamental

CEA permite valorar el efecto económico de:

- precio;
- descuentos confirmados;
- beneficios económicos ciertos aplicables a la operación.

Debe distinguir:

### CEA inmediato

Beneficios económicos ciertos y aplicables actualmente.

### CEA potencial

Beneficios futuros condicionados cuyo cumplimiento aún no está asegurado.

> Un beneficio futuro condicionado no se utiliza como beneficio cierto para justificar una decisión actual.

---

## 3. Relaciones principales

CEA debe estar conectado conceptualmente con:

- [[TCO_01_Precio]]
- [[TCO_02_Descuentos]]
- [[TCO_03_Rappels]]
- [[TCO_00_Principios]]
- [[TCO_11_Fronteras]]
- [[Motor_Escenarios]]

CEA también se relaciona con:

- [[PR_Precio_Referencia]]
- [[PO_Precio_Objetivo]]
- [[PMR_Precio_Maximo]]

Estas últimas referencias pertenecen al dominio de inteligencia de precio y no deben convertirse en subnodos de TCO.

---

## 4. Relación con Precio

El precio nominal es una entrada del análisis.

CEA puede reflejar el efecto de beneficios económicos confirmados sobre ese precio.

---

## 5. Relación con TCO

CEA y TCO son conceptos distintos.

### CEA

Métrica económica transversal de las condiciones económicas aplicables.

### TCO

Coste directo de adquisición que incorpora los costes adicionales directamente atribuibles.

> **CEA no es una subcategoría de TCO.**

> **TCO no sustituye a CEA.**

Ambos alimentan el motor de decisión.

---

## 6. Relación con escenarios

Cada escenario conserva su propio CEA.

```text
S0 → oferta inicial
S1 → descuento
S2 → rappel
S3 → cantidad
S4 → otras condiciones
```

Los escenarios anteriores nunca se sobrescriben.

---

## 7. Propagación

Un cambio relevante puede afectar simultáneamente a:

```text
CAMBIO
  │
  ├── CEA
  ├── TCO
  ├── STOCK
  ├── FINANZAS
  └── PROVEEDOR/RIESGO
        │
        ▼
     Motor_Escenarios
        │
        ▼
    RECOMENDACIÓN
```

No todos los cambios afectan a todas las capas.

---

## 8. Estado

**PROPUESTA v0.3 — pendiente de aprobación.**
