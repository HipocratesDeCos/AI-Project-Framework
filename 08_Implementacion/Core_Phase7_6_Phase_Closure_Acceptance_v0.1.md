# EIOS — F7.6 · CIERRE Y ACEPTACIÓN FORMAL DE FASE 7

**Fecha:** 18/11/2026  
**Base auditada:** `main @ 6de352fda51dd95431e6778d41530f9531949ff9`

## 1. OBJETIVO

F7.6 no añade una capacidad funcional. Convierte el cierre de Fase 7 en una condición reproducible, auditable y bloqueante.

La auditoría posterior a F7.5 concluye que las fronteras materiales de lifecycle y release previstas para la fase ya están cubiertas:

- F7.1 — superficie pública estable;
- F7.2 — compatibilidad exacta de releases;
- F7.3 — upgrade/migración con fail-closed y rollback anchor;
- F7.4 — deprecación y retirada controlada;
- F7.5 — identidad inmutable y content-addressed de release candidata.

No se detecta una frontera funcional adicional que justifique F7.7.

## 2. LO QUE QUEDA FUERA

No se incorpora a F7:

- firma criptográfica del distribuidor o PKI;
- una release futura 0.2.0 inventada;
- admisión operacional;
- autenticación empresarial real;
- piloto productivo;
- autorización automática de decisiones.

Estos frentes requieren contexto o infraestructura que hoy no existe y no deben simularse para prolongar la fase.

## 3. MATERIALIZACIÓN

Se añaden:

- `phase7_acceptance_manifest_v0.1.json`;
- `tools/verify_f7_phase7_closure.py`;
- pruebas adversarias;
- gate CI F7.6.

El cierre exige presencia ordenada de F7.1–F7.5, políticas asociadas, gates Linux/Windows y ausencia de gobierno F7 filtrado al núcleo `eios/`.

## 4. AUTORIDAD

El cierre mantiene:

- `synthetic_only=true`
- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

Una release candidate técnicamente identificada no equivale a producción autorizada.

## 5. PRUEBAS ADVERSARIAS

F7.6 rechaza el cierre si:

- falta una unidad F7.1–F7.5;
- falta una política declarada;
- desaparece el gate de identidad Linux o Windows;
- se altera el orden de unidades;
- se eleva autoridad;
- aparece lógica de gobierno F7 dentro de `eios/`.

## 6. CRITERIO DE CIERRE

F7 queda formalmente cerrada únicamente si:

- `F7_6_PHASE7_CLOSURE_ACCEPTANCE_PASS`;
- Python/SQL permanecen verdes;
- F4–F7.5 permanecen verdes;
- Windows Python 3.12 permanece verde;
- no se modifica código de `eios/`;
- PR y CI post-merge son verdes sobre SHA exactos.

## 7. RESULTADO

Tras F7.6 no deben abrirse F7.7, F7.8, etc. salvo que una auditoría futura descubra una regresión o una frontera material inequívocamente perteneciente a lifecycle/release governance.

El siguiente trabajo del proyecto deberá pertenecer a una fase distinta y responder a un nuevo objetivo técnico o de producto.
