# TCO — AUDITORÍA DE RECONCILIACIÓN DE GOBERNANZA DE PRUEBAS

**Proyecto:** EIOS — Enterprise Intelligent Operations System  
**Scope:** TCO Core — gobernanza y trazabilidad de pruebas  
**Fase:** AUDITAR  
**Estado:** SUPERADA — sin blockers para el scope de reconciliación  
**Baseline auditado:** `4606b1b10eec14d79d06b389953b68bbfacb599b`  
**Diseño auditado:** `TCO_Test_Governance_Reconciliation_Design.md`  

---

## 1. Objeto de auditoría

Se contrasta el diseño de reconciliación contra:

- `08_Implementacion/TCO_Core_Implementation_Contract.md`;
- `08_Implementacion/TCO_Core_CI_Verification.md`;
- `07_Pruebas/Plan_Pruebas_MVP.md`;
- `07_Pruebas/Matriz_Trazabilidad_Ejecutable.md`;
- `tests/test_tco_core.py`.

La auditoría no evalúa nuevamente la corrección funcional completa del motor TCO: esa verificación física ya está documentada en el contrato y en la matriz CI.

---

## 2. Hallazgos

### A-01 — Separación entre cobertura física y cobertura oficial

**Resultado: CONFIRMADO.**

`TCO_Core_CI_Verification.md` declara explícitamente que la cobertura física TCO está materializada mientras la cobertura oficial específica permanece pendiente. También establece que `TCO-V01 … TCO-V08` son identificadores internos de verificación y no `Test_ID` oficiales.

**Conclusión:** el diseño respeta correctamente la separación entre prueba física y cobertura oficial.

### A-02 — Ausencia de familia TCO en el Plan de Pruebas

**Resultado: CONFIRMADO.**

El `Plan_Pruebas_MVP.md` vigente utiliza la taxonomía `T-[ÁREA]-[NÚMERO]`, pero no define una familia TCO específica en su versión actual.

**Conclusión:** no existe base para asignar nuevos `Test_ID` a TCO durante esta fase.

### A-03 — Regla de no invención de Test_ID

**Resultado: CONFIRMADO.**

`Matriz_Trazabilidad_Ejecutable.md` establece que la matriz no puede crear una taxonomía paralela ni nuevos `Test_ID`; cuando no existe un identificador oficial inequívoco, la relación debe permanecer sin asignación oficial.

**Conclusión:** el scope no debe modificar la matriz ejecutable para simular cobertura oficial.

### A-04 — Cobertura indirecta

**Resultado: CONFIRMADO.**

La matriz CI relaciona algunas invariantes con `T-DAT-002` y `T-RGL-006`, pero las clasifica expresamente como relaciones indirectas y establece que no constituyen cobertura TCO específica.

**Conclusión:** no deben promoverse a `COVERED` sin decisión formal del Plan de Pruebas.

### A-05 — GAP-TCO-02

**Resultado: BLOQUEO LOCAL, NO BLOCKER DEL SCOPE.**

La comprobación de contradicción `cantidad × precio_unitario != importe_total` permanece bloqueada porque el modelo C0 no proporciona un `importe_total` independiente. El contrato TCO registra `GAP-TCO-02` y prohíbe resolverlo mediante duplicación en TCO o modificación implícita de C0.

**Conclusión:** el diseño debe conservar `BLOCKED_BY_GAP` para esta relación y no intentar resolverla mediante pruebas.

### A-06 — GAP-TCO-01

**Resultado: FUERA DE ALCANCE.**

El contrato TCO mantiene fuera del Core las extensiones derivadas/financieras sin especificación normativa suficiente.

**Conclusión:** la reconciliación de pruebas no puede utilizarse para convertir estas extensiones en requisitos implementables.

### A-07 — Correspondencia con pruebas físicas

**Resultado: CONFIRMADO.**

`tests/test_tco_core.py` materializa siete comportamientos coherentes con la matriz CI: cálculo determinable, ausencia sin sustitución por cero, no aplicabilidad, moneda incompatible, atribución obligatoria, no modificación de fuente y exclusión automática de financiación.

**Conclusión:** existe una base física suficiente para una futura trazabilidad oficial, pero la ausencia de `Test_ID` específico impide declararla como cobertura oficial.

---

## 3. Dictamen

**AUDITORÍA SUPERADA.**

No se identifica contradicción entre el diseño propuesto y las autoridades actualmente vigentes.

La brecha real es de **gobernanza de pruebas**, no de implementación TCO Core:

```text
TCO Core físico                 → EXISTE
Pruebas físicas TCO             → EXISTEN
CI física                       → VERIFICADA
Test_ID TCO oficial específico  → NO EXISTE
GAP-TCO-02                      → BLOQUEA I-TCO-06
GAP-TCO-01                      → EXTENSIONES FUERA DEL CORE
```

---

## 4. Consecuencia de gobierno

No procede todavía modificar `Plan_Pruebas_MVP.md` ni crear `Test_ID` nuevos como parte de esta auditoría.

Si el proyecto decide obtener cobertura oficial específica TCO, deberá abrirse un scope posterior de gobernanza sobre el Plan de Pruebas y seguir el ciclo completo:

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**.

La presente auditoría no concede por sí misma autorización para ese cambio.

---

## 5. Siguiente fase

**DEPURAR:** revisar únicamente inconsistencias documentales menores del scope y preparar la Auditoría 2. No modificar implementación, C0, GAP-TCO-01, GAP-TCO-02 ni crear `Test_ID` oficiales.
