# EIOS — Finance · RDM P-FIN-002 → R-FIN-003 Reconciliation — Audit 1 v0.1

**Estado:** AUDITAR — SUPERADA CON 1 AJUSTE DE PRECISIÓN  
**Objeto:** `Finance_RDM_PFIN002_RFIN003_Reconciliation_Design_v0.1.md`

## 1. Contraste de autoridad

La relación está demostrada directamente por `01_Modelo/Finance_Basic_Authority_v0.1.md`:

- `treasury_minimum = P-FIN-002`;
- `financial_safety_margin_pct` utiliza `treasury_minimum`;
- la condición cuantitativa ordinaria autorizada para `R-FIN-003` es `financial_safety_margin_pct < P-FIN-004`.

`04_Reglas/Matriz_Reglas_MVP.md` conserva la autoridad sobre la condición y el resultado de `R-FIN-003`.

## 2. Clasificación de dependencia

`Dependency_Type = DERIVED` es correcta.

`P-FIN-002` no es el umbral directo de `R-FIN-003`; participa en una transformación financiera explícitamente documentada y autorizada antes de la comparación con `P-FIN-004`.

No debe registrarse como una segunda dependencia `PARAMETER` directa por mera presencia en el runtime.

## 3. Hallazgo A1-01 — vista especializada parámetro ↔ regla

`Rule_Dependency_Matrix.md`, sección de actualización, exige actualizar las vistas especializadas que correspondan cuando se confirma una dependencia.

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` es precisamente la vista especializada parámetro ↔ regla y actualmente presenta `P-FIN-002` únicamente respecto de `R-FIN-001`.

La materialización debe reconciliar también esa vista, incorporando `R-FIN-003` como relación **derivada**, sin alterar la definición ni el valor de `P-FIN-002`.

**Severidad:** precisión documental.  
**Bloqueador:** NO.

## 4. Fronteras verificadas

No existe autoridad para modificar:

- valores de parámetros;
- fórmula de FIN-AUTH-07;
- efecto/severidad de `R-FIN-003`;
- escalada R1→R0;
- `R-FIN-002`;
- dependencias `EVIDENCE` Finance todavía no canonizadas;
- código, tests o C0.

## 5. Dictamen

**AUDIT 1: SUPERADA CON 1 AJUSTE DE PRECISIÓN / 0 BLOQUEADORES.**

DEPURAR debe limitarse a incorporar la reconciliación de la vista especializada al plan de materialización.
