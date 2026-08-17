# Motor_Escenarios

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Naturaleza:** Motor transversal  
**Versión:** 0.1  
**Estado:** PROPUESTA — nota conceptual pendiente de aprobación

---

## 1. Propósito

Definir conceptualmente el motor transversal que conserva escenarios de negociación y provoca el recálculo de las áreas afectadas.

---

## 2. Principio fundamental

Cada cambio relevante de la negociación genera un escenario nuevo.

```text
S0 → oferta inicial
S1 → descuento
S2 → rappel
S3 → cantidad
S4 → plazo
```

Los escenarios anteriores nunca se sobrescriben.

---

## 3. Función

El motor debe:

1. conservar el escenario;
2. identificar las variables modificadas;
3. determinar las capas afectadas;
4. provocar el recálculo correspondiente;
5. conservar trazabilidad;
6. permitir comparar escenarios.

---

## 4. Propagación conceptual

```text
CAMBIO EN NEGOCIACIÓN
        │
        ▼
MOTOR DE ESCENARIOS
        │
 ┌──────┼──────┬──────┬──────┐
 ▼      ▼      ▼      ▼      ▼
CEA    TCO   STOCK  FINANZAS PROVEEDOR
 │      │      │       │       │
 └──────┴──────┴───────┴───────┘
                 │
                 ▼
            RECOMENDACIÓN
```

No todos los cambios afectan a todas las áreas.

---

## 5. Ejemplos

### Cambio de precio

Puede afectar a:

- CEA;
- TCO;
- margen;
- recomendación.

### Cambio de cantidad

Puede afectar a:

- CEA;
- TCO;
- stock;
- finanzas;
- proveedor.

### Cambio de plazo de pago

Puede afectar principalmente a:

- finanzas;
- recomendación.

### Cambio de transporte

Puede afectar a:

- TCO;
- CEA cuando corresponda;
- recomendación.

---

## 6. Regla de no compensación automática

EIOS no debe compensar automáticamente un bloqueo crítico mediante una suma de condiciones favorables.

La resolución debe respetar la lógica de reglas y conflictos.

---

## 7. Trazabilidad mínima

Cada escenario debería conservar conceptualmente:

- `Scenario_ID`
- escenario anterior;
- fecha;
- variable modificada;
- valor anterior;
- valor nuevo;
- usuario;
- capas afectadas;
- resultado del recálculo;
- recomendación resultante.

---

## 8. Relaciones

- [[CEA_Coste_Efectivo]]
- [[TCO_00_Principios]]
- [[TCO_01_Precio]]
- [[TCO_02_Descuentos]]
- [[TCO_03_Rappels]]
- [[TCO_04_Transporte]]
- [[TCO_11_Fronteras]]
- [[CAPA_03_Stock]]
- [[CAPA_04_Finanzas]]
- [[CAPA_05_Proveedor]]

---

## 9. Estado

**PROPUESTA v0.1 — pendiente de aprobación.**
