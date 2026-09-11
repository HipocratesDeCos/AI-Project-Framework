# EIOS — STK · Auditoría de entrada a contrato técnico v0.2

**Estado:** CERRADA — GO A DISEÑO DE CONTRATO TÉCNICO
**Baseline auditado:** `stk/entry-reconciliation-v0.2`
**Fecha:** 11/09/2026
**Ámbito:** Stock & Demand Intelligence (`STK-M01…M10` + autoridad de entrada + dependencias)

---

## 1. Propósito

Repetir el gate de entrada a contrato técnico STK después del cierre de los tres bloqueos declarados en v0.1:

1. estado canónico de stock;
2. política de demanda;
3. cruce demostrable STK/PYE ↔ reglas/dependencias.

Esta auditoría determina aptitud para **diseñar el contrato técnico**. No autoriza por sí sola implementación ejecutable.

---

## 2. Fuentes auditadas

- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1;
- `01_Modelo/STK_M01_Consumption_Authority.md` … `STK_M10_Contradictions_Authority.md`;
- `01_Modelo/STK_Contract_Entry_Authority.md` v1.0;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Centro_Parametrizacion.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.9;
- `03_Arquitectura/Architecture_Blueprint.md`;
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1;
- `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` v1.0;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.4;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- C0 físico vigente (`eios/core/models.py`);
- `07_Pruebas/STK_Contract_Entry_Audit_v0.1.md`.

---

## 3. AUDITAR — comprobación de bloqueadores v0.1

### B1 — Estado canónico de stock

**RESUELTO.**

La autoridad empresarial aprobada determina:

- `stock_on_hand` = stock físico evidenciado en la fecha de evaluación;
- `stock_committed` = parte de dicho stock reservada/asignada de forma evidenciada y no libre;
- `stock_available = max(0, stock_on_hand - stock_committed)`;
- si `stock_committed > stock_on_hand`, se conserva `availability_deficit` y no se oculta el déficit.

Pedidos pendientes, tránsito y recepciones futuras no forman parte de `stock_on_hand`.

No existe contradicción con el Architecture Blueprint, que exige `stock físico ≠ stock disponible` y separación de stock comprometido y tránsito.

### B2 — Demanda utilizada por STK

**RESUELTO.**

La autoridad aprobada permite únicamente métodos explícitos, versionados y trazables:

1. previsión externa/autorizada;
2. base histórica derivada de `consumption` real M01.

Para base histórica:

`historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window`

No se reduce silenciosamente una ventana incompleta. Un periodo requerido ausente produce `UNKNOWN / NOT_EVIDENCED`.

Ventas históricas no se transforman automáticamente en consumo o demanda. `P-PYE-005` no autoriza dicha transformación.

### B3 — Parámetros STK/PYE ↔ reglas

**RESUELTO.**

El cruce individual completo determina únicamente tres relaciones de regla confirmadas:

- `P-STK-004 → R-STK-002` — directa;
- `P-STK-004 → R-STK-003` — derivada;
- `P-STK-005 → R-STK-003` — derivada.

El resto de `P-STK/P-PYE` queda expresamente clasificado como configuración o metodología sin consumidor directo demostrado. No permanece como pendiente genérico y no se asigna por similitud nominal.

La RDM v1.4 incorpora las tres relaciones confirmadas y conserva `Criticality` y `Evaluability_Impact` como `PENDING` cuando no existe autoridad documental específica.

---

## 4. Gates de entrada

| Gate | Resultado | Dictamen |
|---|---|---|
| Metodología M01…M10 | PASS | Cerrada y no reabierta. |
| Entradas canónicas | PASS | `stock_on_hand`, `stock_committed`, `stock_available` y resto de entradas tienen semántica suficiente para contrato. |
| Unidad | PASS | Unidad base normalizada exigida en magnitudes cuantitativas. |
| Fecha de referencia | PASS | `evaluation_date` canónica; `as_of_date` deberá mapearse a ella en contrato sin duplicidad semántica. |
| Consumo | PASS | M01. |
| Demanda | PASS | Política de fuente/método cerrada. |
| Cobertura | PASS | M04. |
| Proyección | PASS | M05. |
| Recepción futura / no doble conteo | PASS | M06. |
| Exceso | PASS | M07. |
| Demanda confirmada / absorción | PASS | M08. |
| Ausencia | PASS | M09. |
| Contradicción | PASS | M10. |
| Regla ↔ parámetro | PASS | Cruce especializado + matriz de parámetros + RDM reconciliados. |
| Valores iniciales del catálogo | NO REQUERIDOS PARA EL GATE | Permanecen pendientes; contrato debe exigir configuración vigente sin convertirlos en defaults normativos. |
| Compatibilidad C0 | PASS | No se modifica C0; cualquier mapping debe ser explícito en el contrato STK. |
| Autoridad decisional humana | PASS | Ninguna salida STK constituye decisión final. |

---

## 5. DEPURAR

Se eliminan cuatro ambigüedades:

1. **`stock_on_hand` no significa stock disponible.** La versión v1.1 de la matriz metodológica separa ambas magnitudes.
2. **Demanda no significa ventas.** Ventas requieren una política posterior de transformación si algún día se autorizan como fuente.
3. **Parámetro metodológico no significa parámetro de regla.** El contrato debe conservar esta separación.
4. **Valor inicial no significa default normativo.** El software no debe hardcodear 15 %, 30/90 días, 10 %, 12 meses, 90 días o 15 días como verdad empresarial.

No se detecta necesidad de crear STK-M11 ni un parámetro adicional para superar el gate.

---

## 6. AUDITAR 2

Revisión final contra las fronteras cerradas:

- **Gobierno:** no se crea autoridad paralela; la RDM permanece canónica para dependencias.
- **Reglas:** no se cambia la condición ni resultado de `R-STK-001…004`.
- **Parámetros:** no se valida ningún valor inicial pendiente.
- **Arquitectura:** se preservan stock físico/disponible/comprometido/tránsito y control humano.
- **M01…M10:** ninguna autoridad se reabre o contradice.
- **C0 físico:** no se amplía; `PurchaseOperation.quantity` solo podrá mapearse a `proposed_quantity` mediante contrato explícito.
- **Ausencia:** `UNKNOWN / NOT_EVIDENCED` sigue distinto de cero.
- **Contradicción:** no existe resolución implícita.
- **Forecasting:** no se introduce modelo predictivo ni selección automática de método.
- **Decisión:** STK produce análisis/evidencia; no produce la decisión empresarial final.

**Hallazgos bloqueantes en Audit 2: 0.**

---

## 7. Deuda controlada no bloqueante

Permanecen fuera del gate de contrato STK:

- `Criticality` y `Evaluability_Impact` de dependencias RDM no demostradas individualmente;
- dependencias `DATA`, `EVIDENCE` y `COMPONENT` no necesarias para definir la frontera cuantitativa inicial del contrato;
- validación de valores empresariales concretos del catálogo;
- futura transformación ventas → demanda, actualmente no autorizada;
- reconciliaciones documentales secundarias de UI que no poseen autoridad metodológica.

Estos puntos no autorizan comportamiento implícito y no pueden rellenarse desde el contrato por conveniencia técnica.

---

## 8. CERRAR

**DICTAMEN: GO A DISEÑO DE CONTRATO TÉCNICO STK.**

El contrato técnico queda autorizado para diseñarse bajo las siguientes restricciones:

- implementar exclusivamente metodología y relaciones ya autorizadas;
- ser parametrizable y no hardcodear valores iniciales pendientes;
- mapear `as_of_date` a `evaluation_date` sin crear identidades temporales paralelas;
- conservar trazabilidad de fuentes, versiones y configuración;
- propagar ausencia/contradicción;
- impedir doble conteo logístico;
- mantener reglas, CRC y decisión final fuera de la autoridad del cálculo STK salvo interfaces explícitas ya autorizadas;
- no modificar C0 silenciosamente.

La implementación ejecutable seguirá bloqueada hasta que el contrato técnico complete su propia secuencia:

`DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR`.

---

## 9. Estado final

**STK CONTRACT ENTRY AUDIT v0.2: CERRADA — GO.**

Siguiente unidad autorizada: **DISEÑAR `STK_Implementation_Contract`**.
