# EIOS — F7.4 · DEPRECATION & SUPPORT LIFECYCLE POLICY

**Fecha:** 18/11/2026  
**Base:** `main @ afbcf7d9a4d1bf3e9657148b8549ff0b4b172f15`

## 1. OBJETIVO

F7.1 fijó la API pública, F7.2 la compatibilidad exacta entre releases y F7.3 el contrato seguro de migración. F7.4 define **cómo puede dejar de soportarse una API pública sin romper consumidores de forma silenciosa**.

## 2. PRINCIPIO CENTRAL

**Una API pública no puede desaparecer de una release a la siguiente sin ciclo de deprecación verificable.**

La retirada silenciosa queda prohibida.

## 3. ESTADOS

Toda API pública parte de:

`ACTIVE`

Una retirada futura debe seguir exclusivamente:

`ACTIVE → DEPRECATED → REMOVAL_ELIGIBLE → REMOVED`

No se admite:

- `ACTIVE → REMOVED`;
- marcar como pública/deprecada una función interna;
- declarar elegible para retirada sin release sucesora certificada;
- retirar sin guía de migración;
- retirar sin regresión de consumidores existentes y tercer dominio;
- retirar ignorando F7.2 o F7.3.

## 4. POR QUÉ NO SE FIJA UN NÚMERO DE MESES

EIOS todavía no tiene una cadencia comercial estable de releases. Un plazo temporal fijo sería arbitrario.

F7.4 utiliza un criterio más fuerte: **evidencia de transición**.

Antes de retirar un símbolo deben existir:

1. registro explícito de deprecación;
2. al menos una release sucesora certificada en la que el símbolo deprecado haya convivido;
3. sustitución declarada o justificación expresa de ausencia de sustitución;
4. guía de migración;
5. evidencia F7.2;
6. regresión de consumidores existentes;
7. regresión del tercer dominio;
8. evidencia compatible con el contrato F7.3.

## 5. ESTADO ACTUAL

Todos los símbolos públicos de la baseline F7.1 permanecen:

`ACTIVE`

El registro de deprecaciones está vacío.

F7.4 **no depreca ni elimina nada**.

## 6. GATE EJECUTABLE

`tools/verify_f7_4_deprecation_lifecycle.py` comprueba:

- identidad exacta de la política;
- estados y transiciones;
- que solo símbolos públicos de F7.1 puedan entrar en ciclo de deprecación;
- que exista sustitución o justificación;
- que exista guía de migración;
- que REMOVAL_ELIGIBLE exija release sucesora y todas las evidencias;
- que ningún símbolo esté preautorizado como REMOVED en esta baseline;
- que no exista escalada de autoridad.

## 7. RELACIÓN CON F7.1–F7.3

- **F7.1** responde: ¿qué es API pública?
- **F7.2** responde: ¿qué releases son compatibles?
- **F7.3** responde: ¿cómo migra una instalación?
- **F7.4** responde: ¿cómo puede retirarse una API sin romper consumidores?

## 8. AUTORIDAD

Sin cambios:

- `production_authorized=false`
- `decision_authority=false`
- `operational_path=FORBIDDEN`

## 9. CRITERIO DE CIERRE

F7.4 queda cerrada si:

- la política de ciclo de vida es ejecutable;
- las retiradas prematuras fallan;
- símbolos internos no pueden entrar en el ciclo público;
- F7.1–F7.3 y regresiones anteriores permanecen verdes;
- Linux y Windows 3.12 permanecen verdes;
- no se modifica `eios/`;
- PR y CI post-merge son verdes sobre SHA exactos.
