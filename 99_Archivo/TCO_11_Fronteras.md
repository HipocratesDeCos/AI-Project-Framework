# TCO_11_Fronteras

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Capa:** CAPA 2 — TCO  
**Versión:** 0.3  
**Estado:** PROPUESTA — limpieza de arquitectura

---

## 1. Propósito

Formalizar la frontera entre CAPA 2, CAPA 3 y CAPA 4 y situar correctamente el CEA como concepto transversal.

---

## 2. Arquitectura conceptual

```text
                    PROPUESTA DE COMPRA
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        CAPA 1 — PRECIO             CAPA 2 — TCO
              │                           │
        PR / PO / PMR               costes directos
              │                           │
              └─────────────┬─────────────┘
                            ▼
                    CEA transversal
                            │
                            ▼
                 [[Motor_Escenarios]]
                            │
                            ▼
                     MOTOR DECISIÓN
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
        CAPA 3           CAPA 4           CAPA 5
        STOCK            FINANZAS        PROVEEDOR
```

CEA no constituye una subcapa de TCO.

---

## 3. Reglas de frontera

### CAPA 2

Costes directos de adquisición.

### CAPA 3

Consecuencias operativas del stock.

### CAPA 4

Consecuencias financieras.

### CAPA 5

Riesgo y relación con proveedor.

---

## 4. Escenarios

Los escenarios se gestionan transversalmente mediante:

[[Motor_Escenarios]]

Un cambio relevante puede afectar a una o varias capas.

No todos los cambios afectan a todas las capas.

---

## 5. Relaciones

- [[CEA_Coste_Efectivo]]
- [[TCO_00_Principios]]
- [[TCO_01_Precio]]
- [[CAPA_03_Stock]]
- [[CAPA_04_Finanzas]]
- [[CAPA_05_Proveedor]]
- [[Motor_Escenarios]]

---

## 6. Estado

**PROPUESTA v0.3 — pendiente de aprobación.**
