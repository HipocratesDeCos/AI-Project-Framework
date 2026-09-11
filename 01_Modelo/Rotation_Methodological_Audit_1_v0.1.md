# EIOS — ROTACIÓN · METHODOLOGICAL AUDIT 1 v0.1

**Estado:** AUDIT 1 COMPLETADA  
**Fecha:** 11/09/2026  
**Baseline:** `main @ f38cbc71c430e35efc0ab5ac97a3baf0bc89db99`

---

## 1. Alcance auditado

Se contrasta `Rotation_Methodological_Design_v0.1.md` contra:

- `01_Modelo/Especificacion_funcional.md`;
- `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.9;
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1;
- `04_Reglas/Reglas_MVP.md` legado;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.4;
- `04_Reglas/Evidence_Contract.md` v1.0.

---

## 2. Hallazgos confirmados

### ROT-A1-01 — No existe metodología canónica de `rotation_metric`

La especificación funcional menciona rotación como información de stock, pero excluye expresamente la metodología detallada de cada indicador.

La Matriz de Reglas define `R-ROT-001` por comparación contra un umbral, pero no define:

- fórmula;
- numerador;
- denominador;
- unidad;
- ventana;
- fuente;
- normalización.

**Dictamen:** GAP REAL.

---

### ROT-A1-02 — El catálogo no contiene parámetros ROT

`Catalogo_Parametros_MVP_v0.3.md` contiene PRE, STK, PYE, MGE, FIN, PAG, RGL y DAT, pero no una familia ROT.

No existe parámetro demostrable para:

- umbral de baja rotación de `R-ROT-001`;
- periodo configurado de `R-ROT-002`.

La matriz parámetro↔regla tampoco contiene relaciones ROT.

`Matriz_Parametros_Reglas_MVP.md` establece G-07:

> una regla que requiera un valor configurable sin disponer del parámetro correspondiente constituye un gap de parametrización.

**Dictamen:** GAP DE PARAMETRIZACIÓN CONFIRMADO.

---

### ROT-A1-03 — RDM no contiene dependencias ROT

`Rule_Dependency_Matrix.md` v1.4 no registra dependencias `R-ROT-001` ni `R-ROT-002`.

No están demostradas formalmente:

- DATA;
- EVIDENCE;
- PARAMETER;
- COMPONENT;
- evaluability impact;
- fallback.

**Dictamen:** NO APTO PARA EVALUACIÓN OPERATIVA.

---

### ROT-A1-04 — STK no autoriza convertir consumo/demanda en rotación

La metodología STK separa consumo, demanda y ventas históricas.

En particular, las ventas históricas no sustituyen consumo o demanda por defecto.

Por simetría de autoridad tampoco puede inferirse:

```text
consumption → rotation
coverage → rotation
historical demand → rotation
```

sin una metodología ROT específica.

**Dictamen:** frontera correcta; no reutilizar STK como fórmula implícita.

---

### ROT-A1-05 — `R-ROT-002` sí tiene semántica empresarial mínima distinguible

La condición vigente es:

> no existen ventas durante el periodo configurado.

Esto permite cerrar conceptualmente una condición booleana de actividad de ventas, siempre que exista:

- una ventana completa y autorizada;
- una fuente de ventas suficientemente evidenciada;
- identidad de artículo/scope;
- evidencia de que la suma/cantidad de ventas en la ventana es exactamente cero.

No permite usar “sin registros” como equivalente a cero.

`Evidence_Contract` confirma:

```text
ausencia de evidencia != FALSE
GAP != FALSE
```

Aplicado a ROT:

```text
sin evidencia de ventas != ventas cero
```

**Dictamen:** semántica metodológica parcialmente cerrable sin inventar fórmula de rotación.

---

### ROT-A1-06 — Excepciones de `R-ROT-002` no están operativamente formalizadas

La Matriz de Reglas enumera como posibilidades:

- pedido confirmado;
- campaña prevista;
- operación estratégica;
- decisión empresarial explícita.

Pero no se demuestra en RDM ni en una especificación ROT:

- dependencia formal con STK-M08;
- contrato de evidencia de campaña;
- definición de operación estratégica;
- mecanismo de override/autoridad aplicable.

**Dictamen:** no aplicar automáticamente ninguna excepción ROT en v0.1.

---

### ROT-A1-07 — `Reglas_MVP.md` no aporta autoridad adicional

El documento legado declara expresamente que no constituye una segunda fuente normativa.

No resuelve ningún gap ROT.

**Dictamen:** sin autoridad recuperable adicional.

---

## 3. Descomposición depurada necesaria

Audit 1 obliga a separar:

### ROT-TRACK-A — Sales inactivity

Sostiene exclusivamente la evidencia necesaria para la condición de `R-ROT-002`:

```text
sales_in_window == 0
```

solo cuando cero está demostrado sobre ventana completa.

No calcula `rotation_metric`.

### ROT-TRACK-B — Rotation metric

Sostendrá `R-ROT-001` únicamente cuando exista autoridad para:

- fórmula;
- unidad;
- ventana;
- umbral;
- dependencias.

Permanece bloqueado.

---

## 4. Contradicciones evitadas

El diseño no debe:

1. usar `P-STK-006` como periodo ROT por coincidencia temporal;
2. usar `P-DAT-*` como umbral ROT;
3. reutilizar cobertura como rotación;
4. inferir stock turnover contable;
5. inferir sales velocity;
6. crear una familia `P-ROT-*` sin decisión documental;
7. convertir ausencia de ventas registradas en cero;
8. activar automáticamente excepciones listadas como “posibles”.

---

## 5. Resultado de Audit 1

| Área | Estado |
|---|---|
| Condición documental R-ROT-001 | EXISTE |
| Métrica R-ROT-001 | GAP |
| Umbral R-ROT-001 | GAP DE PARAMETRIZACIÓN |
| Condición documental R-ROT-002 | EXISTE |
| Semántica cero ventas | CERRABLE |
| Periodo R-ROT-002 | GAP DE PARAMETRIZACIÓN |
| Evidencia específica ROT | GAP RDM |
| Excepciones operativas | GAP |
| Implementación | NO AUTORIZADA |

**AUDIT 1: NO SUPERADA PARA CIERRE GLOBAL.**

El siguiente paso correcto es DEPURAR el diseño separando ROT-TRACK-A y ROT-TRACK-B, sin crear todavía parámetros ni fórmula empresarial.
