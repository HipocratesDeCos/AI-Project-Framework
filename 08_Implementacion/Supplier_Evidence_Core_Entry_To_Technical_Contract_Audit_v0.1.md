# EIOS — SUPPLIER EVIDENCE CORE · ENTRY TO TECHNICAL CONTRACT AUDIT v0.1

**Estado:** SUPERADA — ENTRADA A CONTRATO TÉCNICO AUTORIZABLE  
**Fecha:** 11/09/2026  
**Autoridad metodológica:** `Supplier_Evidence_Core_Methodological_Design_v0.3.md`  
**Cierre metodológico:** `Supplier_Evidence_Core_Methodological_Closure_v0.3.md`

---

## 1. Propósito

Verificar si la metodología cerrada v0.3 contiene suficiente precisión para diseñar un contrato físico sin introducir política empresarial nueva.

---

## 2. Estado físico del repositorio

En `main` no existe actualmente un paquete `eios/supplier`.

Sí existen patrones físicos de dominio separados para:

- `eios/pricing`;
- `eios/tco`;
- `eios/stock`;
- `eios/finance`;
- `eios/quality`.

C0 ya proporciona:

- `PurchaseOperation`;
- `DecisionContext`;
- `Evidence`;
- `Trace`.

No es necesario modificar C0 para materializar Supplier Evidence Core.

---

## 3. Dictamen de suficiencia

La metodología v0.3 es suficiente para diseñar un contrato físico **factual** si se mantiene estrictamente la siguiente frontera:

```text
entrada estructurada
    ↓
validación de identidad / coherencia / trazabilidad
    ↓
normalización factual
    ↓
resultado Supplier Evidence Core
```

No se autoriza:

```text
hechos
    ↓
heurística no documentada
    ↓
valoración de proveedor
```

---

## 4. Decisiones contractuales autorizables sin nueva política

### TC-E01 — Paquete físico separado

Puede materializarse:

```text
eios/supplier/__init__.py
eios/supplier/models.py
eios/supplier/engine.py
tests/test_supplier_evidence_core.py
```

No se modifica C0.

### TC-E02 — DecisionContext canónico

La entrada debe consumir `eios.core.models.DecisionContext`.

No se crea un duplicado de identidad decisional.

### TC-E03 — PurchaseOperation como ancla de proveedor/objeto actual

La entrada puede consumir `PurchaseOperation` para obtener:

```text
current supplier_id
article_id
decision_id
scenario_id
```

Debe validarse coherencia entre `PurchaseOperation` y `DecisionContext` para `decision_id` y `scenario_id`.

### TC-E04 — company_scope separado

C0 no contiene `company_scope`.

Supplier Evidence Core puede recibir `company_scope` como atributo propio del sobre de entrada, sin ampliar C0.

No constituye política empresarial nueva; es identidad de alcance.

### TC-E05 — Evidencia de candidatura como hecho estructurado

El engine no debe inferir aplicabilidad actual a partir de texto libre, antigüedad o historial.

La entrada de candidatura deberá declarar un estado factual estructurado suficiente para distinguir:

```text
CURRENT_OPERATION_DEMONSTRATED
REFERENCE_ONLY
GAP
CONFLICTING_DATA
```

Este estado describe la evidencia/aplicabilidad de dominio y no sustituye `Evidence.state` físico de C0.

Mapeo autorizado:

```text
CURRENT_OPERATION_DEMONSTRATED → EVIDENCED_CANDIDATE
REFERENCE_ONLY                 → NOT_EVIDENCED para candidatura actual
GAP                            → NOT_EVIDENCED
CONFLICTING_DATA               → CONFLICTING_DATA
```

El engine no decide por heurística qué estado de entrada corresponde; únicamente valida y transforma determinísticamente la declaración estructurada.

### TC-E06 — Evidencia y source refs

Todo hecho que pretenda ser demostrado debe conservar referencias reproducibles.

El contrato técnico puede utilizar `evidence_id`, `source_ref` y fechas como referencias sin duplicar el objeto C0 `Evidence` completo.

No podrá fabricar `evidence_id` ni `source_ref` ausentes.

### TC-E07 — Condiciones dimensionales

Las condiciones deben representarse como dimensiones tipadas o registros explícitamente semánticos.

No se autoriza un diccionario opaco que permita mezclar unidades/semánticas sin identificación.

### TC-E08 — Comparabilidad estructural

El engine puede determinar estados estructurales únicamente a partir de atributos explícitos de compatibilidad:

- dimensión;
- semántica/unidad;
- objeto/alcance;
- referencia temporal;
- conflicto.

No puede producir `RULE_COMPARABLE`.

### TC-E09 — Métricas externas

Una métrica externa deberá incluir `usage_authority_ref` para poder representarse como `AUTHORIZED_EXTERNAL_METRIC`.

Sin `usage_authority_ref`, no puede autoelevarse a autorizada.

El engine puede degradarla determinísticamente a `CONTEXT_ONLY_METRIC` si el contrato así lo define.

### TC-E10 — No cálculo de concentración/riesgo/fiabilidad

No existe contrato cuantitativo autorizado para:

- concentración;
- fiabilidad;
- cumplimiento;
- riesgo.

No deben existir funciones que calculen estas métricas.

### TC-E11 — No Rules / Assessment

La salida no es `Assessment` y no ejecuta `Rule`.

No contendrá:

- `rule_id` como resultado;
- `assessment`;
- `outcome` TRUE/FALSE de reglas;
- effect/severity;
- recommendation.

### TC-E12 — Inmutabilidad

Los modelos de entrada/salida propios del dominio deben ser inmutables cuando sea compatible con el patrón del repositorio.

El engine no modifica `DecisionContext`, `PurchaseOperation` ni entradas de proveedor.

---

## 5. Riesgos técnicos a controlar en contrato

### R-TC-01 — Duplicidad de candidatos

Debe impedirse que el mismo `supplier_id` aparezca repetido como candidato para el mismo contexto sin identidad diferenciada de propuesta/oferta.

El contrato deberá definir una clave inequívoca de candidato/propuesta.

### R-TC-02 — Candidato igual al proveedor actual

Debe rechazarse como alternativa.

### R-TC-03 — Objeto incompatible

Una evidencia de candidato para otro `article_id/object_id` no puede convertirse en candidatura de la operación actual.

### R-TC-04 — Source/evidence inconsistentes

Un estado `CURRENT_OPERATION_DEMONSTRATED` no puede carecer de referencias de demostración suficientes.

### R-TC-05 — Métrica autoautorizada

`AUTHORIZED_EXTERNAL_METRIC` sin `usage_authority_ref` debe ser imposible estructuralmente o degradado de forma determinista según contrato.

### R-TC-06 — Comparabilidad normativa accidental

Ningún nombre de campo/salida debe sugerir que la capa ya satisface `R-PROV-002`.

---

## 6. Tests mínimos obligatorios del futuro contrato

El contrato deberá exigir tests para:

1. candidato actual demostrado;
2. candidato histórico/reference-only;
3. GAP de candidatura;
4. candidatura contradictoria;
5. candidato igual al proveedor actual rechazado;
6. objeto incompatible rechazado/no aplicable según contrato;
7. duplicidad de identidad/propuesta;
8. disponibilidad cualitativa sin conversión a cantidad;
9. hecho histórico sin score derivado;
10. métrica externa con autoridad;
11. métrica externa sin autoridad → context only;
12. comparación estructural ≠ rule comparable;
13. conflicto dimensional preservado;
14. ausencia ≠ cero/FALSE;
15. DecisionContext/PurchaseOperation coherentes;
16. no mutación;
17. salida sin campos decisionales.

---

## 7. Gaps que siguen fuera del contrato

No se trasladan a implementación:

- PROV-G02;
- PROV-G03;
- PROV-G04 valoración;
- PROV-G05;
- PROV-G06;
- PROV-G07;
- PROV-G08;
- PROV-G09 impacto.

---

## 8. Dictamen final

**AUDITORÍA DE ENTRADA A CONTRATO TÉCNICO: SUPERADA.**

Puede diseñarse contrato técnico de Supplier Evidence Core sin nueva política empresarial si se respetan TC-E01…TC-E12 y los riesgos R-TC-01…06.

No se autoriza todavía implementación física hasta cerrar y auditar el contrato técnico.
