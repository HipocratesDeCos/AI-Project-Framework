# EIOS — STK · Auditoría de entrada a contrato técnico v0.1

**Estado:** CERRADA — NO GO A CONTRATO TÉCNICO
**Baseline auditado:** `a9b9ab6e52d12afc0df4fb0e8e28f3b6baa38d7e`
**Fecha:** 11/09/2026
**Ámbito:** Stock & Demand Intelligence (`STK-M01…M10`)

---

## 1. Propósito

Determinar si la metodología STK cerrada dispone de autoridad suficiente para pasar a contrato técnico cuantitativo sin inventar semántica, fórmulas, parámetros, relaciones regla ↔ parámetro ni comportamiento de ausencia.

Esta auditoría no crea autoridad empresarial nueva. Solo contrasta la autoridad vigente y clasifica los gaps que siguen bloqueando el contrato.

## 2. Método aplicado

Secuencia obligatoria EIOS:

`DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI`

### DISEÑAR

Se utilizaron como gates mínimos los criterios de entrada declarados por `01_Modelo/Stock_Demand_Methodological_Matrix.md`:

- entradas canónicas;
- unidad de cada magnitud;
- fecha de referencia;
- fórmula de consumo/demanda;
- fórmula de cobertura;
- regla de proyección;
- tratamiento de recepción futura;
- tratamiento de ausencia;
- tratamiento de contradicción;
- relación demostrada regla ↔ parámetro.

### AUDITAR

Se contrastaron, como mínimo:

- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `01_Modelo/Stock_Demand_Methodological_Matrix.md`;
- `01_Modelo/STK_M01_Consumption_Authority.md` … `STK_M10_Contradictions_Authority.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Centro_Parametrizacion.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `03_Arquitectura/Architecture_Blueprint.md`;
- `03_App/UI_Field_Registry_v0.1.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- C0 físico vigente en `eios/core/models.py`.

## 3. Resultado de gates

| Gate | Resultado | Evidencia / dictamen |
|---|---|---|
| Metodología `STK-M01…M10` | PASS | Las diez autoridades metodológicas están cerradas. |
| Unidades de magnitudes STK cerradas | PASS | Las autoridades cuantitativas usan unidad base normalizada cuando procede. |
| Fecha de referencia | PASS CON MAPPING TÉCNICO PENDIENTE | `as_of_date` está autorizado; M04/M05 reservan su correspondencia con `evaluation_date` al contrato. La UI ya conserva fecha de evaluación. |
| Consumo | PASS | M01 define consumo real y suma mensual; ausencia ≠ cero. |
| Demanda | BLOCKER | No existe todavía un método autorizado que determine la demanda usada por STK. Ventas, consumo real y demanda prevista permanecen magnitudes distintas. |
| Cobertura | PASS | M04 autoriza la relación `stock_available / authorized_average_demand_or_consumption_per_time_unit`. |
| Proyección | PASS | M05 autoriza `current_available_stock + expected_inflows - expected_outflows`. |
| Recepciones futuras | PASS | M06 gobierna pedido pendiente, tránsito, fecha evidenciada, transición y no doble conteo. |
| Ausencia | PASS | M09 prohíbe sustitución implícita y propaga incertidumbre. |
| Contradicciones | PASS | M10 conserva evidencias, prohíbe heurística implícita y exige autoridad de resolución. |
| Entradas canónicas de estado de stock | BLOCKER | `stock actual`, `stock comprometido` y `stock disponible` no tienen todavía una composición semántica cerrada y no puede inferirse `stock_available` desde nombres. |
| Regla ↔ parámetro STK/PYE | BLOCKER | La matriz especializada mantiene `P-STK-001…006` y `P-PYE-001…006` pendientes de cruce individual; la RDM prohíbe completar relaciones por similitud nominal. |
| Valores iniciales 15 %, 30/90 días, 10 %, 12 meses, 90/15 días | NO BLOQUEAN POR SÍ SOLOS | Siguen pendientes de validación empresarial y no pueden actuar como defaults normativos. Un contrato parametrizable puede exigir configuración autorizada sin convertir esos valores iniciales en política. |
| Compatibilidad con C0 | PASS CON FRONTERA | C0 no contiene semántica STK y no debe ampliarse silenciosamente. `PurchaseOperation.quantity` puede ser fuente técnica de la cantidad propuesta únicamente mediante mapping contractual explícito. |

## 4. Hallazgo B1 — Estado canónico de stock

El Architecture Blueprint establece simultáneamente:

- `stock físico ≠ stock disponible`;
- stock comprometido separado;
- compras en tránsito separadas;
- stock proyectado temporal.

El Registro Maestro UI conserva `Stock actual` y `Stock comprometido` como campos canónicos, pero su propia versión auditada indicaba metodología pendiente.

Las autoridades M04 y M05 consumen `stock_available`, pero no autorizan su composición. Por tanto, no puede imponerse por inferencia una relación como:

`stock_available = stock_on_hand - stock_committed`

ni cualquier variante que incluya reservas, bloqueos, cuarentena, compromisos, tránsito u otras magnitudes.

**Estado:** BLOCKER DE AUTORIDAD EMPRESARIAL.

## 5. Hallazgo B2 — Demanda utilizada por STK

Las fuentes vigentes distinguen expresamente:

- consumo real;
- ventas históricas;
- demanda histórica;
- demanda prevista.

M01 prohíbe convertir ventas o demanda prevista en consumo real por defecto. M04 exige que la política identifique la magnitud, fuente, ventana, método y transformación del denominador. M05 exige lo mismo para las salidas previstas.

El Centro de Parametrización contempla `método de cálculo de demanda` y utilización de ventas históricas, pero no fija todavía dicho método.

Por tanto, el contrato no puede inventar una fórmula de forecasting ni asumir que ventas históricas, consumo o demanda prevista son intercambiables.

**Estado:** BLOCKER DE AUTORIDAD EMPRESARIAL / CONTRACTUAL.

## 6. Hallazgo B3 — Parámetros y reglas

La autoridad vigente permite demostrar algunas relaciones parciales, por ejemplo:

- `P-STK-004` (cobertura máxima) es candidato documental directo para `R-STK-002`, cuya condición depende de cobertura superior al nivel configurado;
- M07 permite que `coverage_maximum` gobierne el máximo utilizado por exceso, conectándolo de forma derivada con `R-STK-003`;
- `P-STK-005` (tolerancia de exceso) interviene en la metodología M07 que cuantifica el exceso utilizado por `R-STK-003`.

Sin embargo, la matriz canónica de dependencias y la matriz especializada todavía no han materializado el cruce STK/PYE completo. No existe autoridad para asignar por nombre todos los `P-STK-*` o `P-PYE-*` a una regla.

En particular, no debe forzarse un consumidor directo para un parámetro si su función demostrada pertenece a la metodología o a un componente analítico y no a la condición de una regla concreta.

**Estado:** BLOCKER DOCUMENTAL/DEPENDENCIAS, RESOLUBLE SIN FIJAR VALORES NUMÉRICOS.

## 7. DEPURAR

Se eliminan como falsos bloqueadores:

1. **Validar ahora los valores iniciales del catálogo.** No es necesario para diseñar un contrato parametrizable; sí está prohibido utilizarlos como defaults normativos mientras sigan pendientes.
2. **Modificar C0 para añadir STK.** No está autorizado ni es necesario en esta fase. STK debe respetar la frontera C0 y declarar adapters/mappings cuando proceda.
3. **Crear STK-M11.** M01…M10 están metodológicamente cerrados; los gaps actuales pertenecen a entrada contractual y dependencias, no a una nueva unidad metodológica numerada.
4. **Inferir relaciones por prefijo.** El prefijo `STK` o `PYE` no demuestra por sí mismo un consumidor de regla.

## 8. AUDITAR 2

Revisión transversal final:

- no se reabre ninguna autoridad M01…M10;
- no se modifica la Matriz de Reglas;
- no se valida ningún valor empresarial pendiente;
- no se introduce forecasting implícito;
- no se redefine C0;
- no se asignan dependencias por similitud semántica;
- se mantiene `UNKNOWN / NOT_EVIDENCED` cuando falta autoridad o evidencia;
- la autoridad decisional humana permanece intacta.

No se detecta contradicción con Architecture Blueprint, MED, reglas, parámetros, RDM ni C0 al mantener el dictamen `NO GO`.

## 9. CERRAR

La auditoría de entrada queda cerrada con el siguiente dictamen:

**NO GO A CONTRATO TÉCNICO STK.**

Quedan exactamente tres familias de trabajo antes de poder reauditar el gate:

1. cerrar la semántica canónica de `stock_on_hand`, `stock_committed` y `stock_available`;
2. cerrar la política de demanda que STK puede consumir sin confundirla con consumo o ventas;
3. materializar únicamente las relaciones STK/PYE ↔ reglas/dependencias que puedan demostrarse, clasificando explícitamente los parámetros sin consumidor directo.

Una vez resueltos estos tres puntos, deberá ejecutarse una nueva auditoría de entrada. Solo un resultado `GO` autorizará diseñar el contrato técnico STK.

## 10. Frontera de continuidad

Hasta nuevo `GO`:

- no crear `STK_Implementation_Contract`;
- no implementar motor cuantitativo STK;
- no convertir valores iniciales de parámetros en política;
- no modificar C0 por necesidades STK;
- no inventar forecasting, disponibilidad de stock ni relaciones parámetro-regla.

**Estado final:** `CERRADA — NO GO`.
