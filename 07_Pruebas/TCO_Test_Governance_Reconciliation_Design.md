# TCO — DISEÑO DE RECONCILIACIÓN DE GOBERNANZA DE PRUEBAS

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Scope:** TCO Core — gobernanza y trazabilidad de pruebas  
**Fase:** DISEÑAR  
**Estado:** DISEÑO MATERIALIZADO — pendiente de AUDITAR  
**Baseline de partida:** `4606b1b10eec14d79d06b389953b68bbfacb599b`  

---

## 1. Propósito

Determinar, sin modificar todavía el Plan de Pruebas MVP ni la implementación física TCO Core, cómo debe reconciliarse la cobertura física ya materializada de TCO con la gobernanza oficial de pruebas del proyecto.

El objetivo es eliminar una posible brecha de trazabilidad entre:

```text
Contrato TCO Core
        ↓
invariantes I-TCO-01 … I-TCO-08
        ↓
pruebas físicas existentes
        ↓
Plan de Pruebas MVP / Test_ID oficial
        ↓
Matriz de Trazabilidad Ejecutable
```

Este scope no crea autoridad funcional, no crea reglas económicas y no resuelve los GAP-TCO existentes.

---

## 2. Evidencia de partida

En `08_Implementacion/TCO_Core_Implementation_Contract.md` el contrato TCO Core consta como cerrado para implementación, con implementación física y pruebas materializadas. El contrato conserva explícitamente GAP-TCO-01 y GAP-TCO-02 como extensiones no implementadas.

`08_Implementacion/TCO_Core_CI_Verification.md` declara materializada la verificación física específica del core, pero distingue dicha cobertura de la cobertura oficial mediante `Test_ID` del Plan de Pruebas.

El `Plan_Pruebas_MVP.md` vigente es versión 0.3, aprobado, y utiliza la taxonomía oficial `T-[ÁREA]-[NÚMERO]`. No contiene actualmente una familia TCO específica.

La `Matriz_Trazabilidad_Ejecutable.md` establece expresamente que no debe inventar `Test_ID` cuando el Plan de Pruebas no proporcione un identificador oficial inequívoco.

---

## 3. Alcance

### Incluido

1. identificar la cobertura física TCO ya existente;
2. identificar las invariantes contractuales TCO que requieren trazabilidad;
3. comprobar si existe un `Test_ID` oficial aplicable en el Plan vigente;
4. determinar las relaciones que pueden trazarse sin crear nueva autoridad;
5. identificar las relaciones que requieren una decisión posterior sobre el Plan de Pruebas;
6. definir una estrategia de reconciliación documental posterior.

### Excluido

- modificación de `eios/tco`;
- modificación de `tests/test_tco_core.py` salvo que una auditoría posterior demuestre una contradicción real;
- resolución de GAP-TCO-01;
- resolución de GAP-TCO-02;
- modificación de C0;
- incorporación de campos económicos nuevos;
- creación de fórmulas financieras o derivadas;
- creación de nuevos `Test_ID` en esta fase;
- modificación del Plan de Pruebas MVP en esta fase;
- cierre del TCO Core.

---

## 4. Principios de diseño

### P1 — No fabricar cobertura oficial

Una prueba física existente no se convierte automáticamente en un caso oficial del Plan de Pruebas.

### P2 — No fabricar Test_ID

Si el Plan de Pruebas no contiene un identificador inequívoco, la trazabilidad debe permanecer sin asignación oficial hasta que exista una decisión formal.

### P3 — Separar cobertura física de cobertura normativa

```text
PHYSICAL
    ≠
OFFICIAL TEST COVERAGE
```

La ejecución satisfactoria de `tests/test_tco_core.py` demuestra comportamiento físico; no modifica por sí sola el contenido del Plan de Pruebas.

### P4 — Mantener los gaps como gaps

La reconciliación no puede convertir GAP-TCO-01 ni GAP-TCO-02 en requisitos satisfechos.

### P5 — No reabrir implementación cerrada

La existencia de una brecha de gobernanza no implica que deba reconstruirse el motor TCO Core.

---

## 5. Resultado esperado de la auditoría

La auditoría deberá clasificar cada relación TCO en una de estas categorías:

| Estado | Significado |
|---|---|
| `OFFICIAL_COVERAGE` | Existe `Test_ID` oficial inequívoco y la prueba física correspondiente puede trazarse a él. |
| `PHYSICAL_ONLY` | Existe prueba física, pero no existe `Test_ID` oficial inequívoco. |
| `BLOCKED_BY_GAP` | La cobertura está impedida por un GAP explícito del contrato. |
| `NOT_APPLICABLE` | La relación no pertenece al core vigente. |
| `CONTRADICTION` | La documentación oficial y la implementación presentan una contradicción que requiere depuración. |

No se utilizará ningún estado que implique aprobación oficial si esta no existe en la autoridad correspondiente.

---

## 6. Criterio de salida del diseño

El diseño se considerará completo cuando pueda responderse documentalmente:

1. qué pruebas TCO existen físicamente;
2. qué invariantes cubren;
3. cuáles tienen `Test_ID` oficial;
4. cuáles permanecen únicamente como cobertura física;
5. cuáles están bloqueadas por GAP;
6. qué acción documental, si alguna, sería necesaria para obtener cobertura oficial.

La decisión de crear o modificar casos oficiales queda fuera de este diseño y, si fuera necesaria, deberá tratarse como scope gobernado sobre el Plan de Pruebas.

---

## 7. Siguiente fase obligatoria

**AUDITAR:** contrastar este diseño contra el contrato TCO Core, `TCO_Core_CI_Verification.md`, `Plan_Pruebas_MVP.md`, `Matriz_Trazabilidad_Ejecutable.md` y `tests/test_tco_core.py`.

No se realizará modificación adicional hasta completar dicha auditoría.
