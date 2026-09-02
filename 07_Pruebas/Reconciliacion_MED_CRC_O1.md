# EIOS — RECONCILIACIÓN MED ↔ CRC ↔ O1

**Fecha:** 2026-09-02  
**Estado:** CERRADO — RECONCILIADO — SIN CAMBIO FUNCIONAL  
**Tipo:** Auditoría transversal documental y de autoridad

---

## 1. Propósito

Reconciliar las responsabilidades del **Modelo Empresarial de Decisión (MED)**, la **Capa de Resolución de Conflictos (CRC)** y **O1 — Orquestación Operacional**, evitando solapamientos de autoridad y sin introducir una nueva capacidad funcional.

## 2. Resultado de la auditoría

La lectura conjunta de los contratos existentes permite establecer la siguiente separación:

```text
MED
Modelo empresarial / semántica del proceso de decisión
        │
        ├── define el marco lógico empresarial
        ├── coordina conceptualmente los análisis
        └── construye la recomendación explicable como concepto empresarial

CRC
Autoridad de resolución y consolidación de resultados de reglas
        │
        └── consolida resultados conforme a la jerarquía normativa existente

O1
Orquestación operacional
        │
        └── coordina ejecuciones disponibles y construye Decision Support Package

DECISOR HUMANO
        └── mantiene la decisión empresarial final
```

## 3. MED

El MED mantiene su función como **modelo empresarial de decisión**. Su descripción de coordinación y de construcción de la recomendación no debe interpretarse como una segunda autoridad normativa frente a CRC ni como una autoridad operacional paralela a O1.

El propio MED establece que no sustituye a CRC, que no establece una jerarquía propia de reglas y que no sustituye al decisor humano.

Por tanto:

- MED = semántica y modelo empresarial.
- MED ≠ segunda CRC.
- MED ≠ autoridad de aprobación.
- MED ≠ ejecución de compra.
- MED ≠ orquestador físico paralelo a O1.

## 4. CRC

CRC conserva exclusivamente la responsabilidad de resolver y consolidar resultados de reglas conforme a su autoridad documental.

CRC:

- recibe resultados ya producidos;
- aplica la precedencia definida;
- conserva la distinción entre efecto y severidad;
- produce el resultado consolidado;
- no ejecuta la compra;
- no sustituye al decisor humano;
- no se convierte en un orquestador general.

Los resultados de negociación procedentes de NI/NL no deben reinterpretarse como efectos R0/R1/R2/R3 salvo que exista una regla explícita que les atribuya esa semántica.

## 5. O1

O1 materializa la coordinación operacional de resultados disponibles y construye un paquete estructurado de soporte a la decisión.

O1:

- no redefine reglas;
- no sustituye CRC;
- no crea una autoridad de decisión;
- no convierte COMPLETED en aprobación empresarial;
- no inventa resultados ausentes;
- preserva las referencias de trazabilidad compatibles con cada capacidad.

## 6. Frontera MED ↔ CRC ↔ O1

No existe contradicción contractual que obligue a modificar código.

La posible ambigüedad se resuelve interpretando cada artefacto en su nivel correcto:

| Componente | Responsabilidad | Autoridad de decisión empresarial |
|---|---|---:|
| MED | Modelo/semántica empresarial | No |
| CRC | Consolidación normativa de resultados | No sustituye al humano |
| O1 | Orquestación operacional | No |
| Decisor humano | Decisión empresarial final | Sí |

## 7. Relación con NI y NL

Negotiation Intelligence y Negotiation Ladder permanecen como capacidades especializadas de negociación.

```text
NI → contenido/inteligencia de negociación
NL → estructuración de la escalera de negociación
CRC → consolidación normativa cuando corresponda
O1 → coordinación operacional
MED → marco empresarial
Humano → decisión final
```

NL no adquiere autoridad independiente por estructurar propuestas de negociación, y CRC no debe reinterpretar esa salida fuera de su semántica contractual.

## 8. Invariantes preservadas

- No nueva autoridad documental.
- No segunda jerarquía de reglas.
- No paralelización de CRC.
- No paralelización de O1.
- No sustitución del decisor humano.
- No ejecución automática de compras.
- No nueva versión de DecisionContext.
- No nuevo sistema de fingerprint.
- No nuevo sistema de trazabilidad.
- No nueva obligación E2E.
- No modificación funcional de MED, CRC, NI, NL u O1.

## 9. Decisión

**RECONCILIACIÓN SUPERADA.**

La aparente superposición entre MED, CRC y O1 es una cuestión de nivel arquitectónico/semántico, no un defecto de implementación.

No se requiere modificación funcional ni apertura de un nuevo ciclo de materialización.

**Resultado:** continuar con la siguiente auditoría objetiva del perímetro EIOS.
