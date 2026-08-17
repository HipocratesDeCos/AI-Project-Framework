# TCO_00_Principios

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.2  
**Estado:** PROPUESTA — corrección arquitectónica pendiente de aprobación

---

## 1. Propósito

Definir los principios conceptuales de la CAPA 2 — TCO y su relación con CEA, CAPA 3 y CAPA 4.

---

## 2. Principio fundamental

El TCO representa el coste directo de adquirir una operación más allá del precio nominal, incorporando los costes directamente atribuibles a la adquisición.

> **TCO no es el contenedor de todos los impactos económicos de una compra.**

---

## 3. Separación obligatoria

EIOS debe mantener separados:

- **Precio**;
- **CEA — Coste Efectivo de Adquisición**;
- **TCO — Total Cost of Ownership**;
- **Stock y demanda**;
- **Finanzas y liquidez**.

Regla:

> **Precio ≠ CEA ≠ TCO**

CEA es un concepto transversal de la operación. No constituye una subcapa de TCO.

---

## 4. Qué representa cada concepto

### Precio

Valor nominal ofertado por el proveedor bajo las condiciones de la propuesta.

### CEA

Coste efectivo derivado del precio y de los beneficios económicos ciertos y aplicables a la operación actual, distinguiendo los beneficios futuros condicionados.

### TCO

Coste directo total necesario para adquirir y recibir la operación, incorporando los componentes directos de adquisición.

---

## 5. Relación conceptual

```text
PROPUESTA DE COMPRA
        │
        ├───────────────┐
        ▼               ▼
     PRECIO            TCO
        │               │
  descuentos/      costes directos
  beneficios          de adquisición
        │               │
        └───────┬───────┘
                ▼
               CEA
        (métrica económica
         de la operación)
```

Esta representación no implica que exista una fórmula universal del tipo `TCO = CEA + ...`.

La metodología matemática definitiva queda pendiente de validación.

---

## 6. Grupo A — TCO directo

En principio:

- precio;
- descuento confirmado cuando corresponda al coste de adquisición;
- rappel ya devengado/aplicable cuando corresponda;
- transporte directamente atribuible;
- seguro directamente atribuible;
- aranceles;
- impuestos no recuperables;
- manipulación directamente asociada;
- inspecciones necesarias;
- merma directamente atribuible;
- otros costes directamente imputables.

---

## 7. Grupo B — costes derivados

Principalmente CAPA 3:

- almacenamiento;
- exceso de stock;
- obsolescencia;
- permanencia;
- devoluciones derivadas del stock;
- incidencias posteriores;
- impacto de la cantidad sobre inventario y cobertura.

---

## 8. Grupo C — finanzas/oportunidad

Principalmente CAPA 4:

- financiación;
- coste de capital;
- liquidez;
- coste de oportunidad;
- impacto financiero proyectado;
- efectos de calendario de caja.

---

## 9. Regla de causalidad

La clasificación debe responder:

> **¿Por qué existe el coste o impacto?**

No únicamente:

> **¿Cuándo se paga?**

Un coste de transporte pagado posteriormente puede seguir siendo CAPA 2 si su causa es la adquisición.

---

## 10. Regla de no duplicación

Un coste debe tener:

- una capa principal;
- una causa;
- una imputación justificable.

La misma cifra no debe utilizarse como coste decisorio duplicado en varias capas.

Una variable puede alimentar varias capas sin que el coste se duplique.

---

## 11. Relación con escenarios

Los cambios relevantes de la negociación generan un nuevo escenario y deben provocar recálculo.

El recálculo puede afectar, según el cambio, a:

- CEA;
- TCO;
- stock;
- finanzas;
- proveedor/riesgo;
- recomendación.

Nunca se sobrescribe un escenario anterior.

---

## 12. Información insuficiente

Si no existe información suficiente para clasificar o cuantificar razonablemente un componente relevante:

**INFORMACIÓN INSUFICIENTE**

No debe inventarse una cifra ni una imputación.

---

## 13. Estado

**PROPUESTA v0.2 — pendiente de aprobación.**
