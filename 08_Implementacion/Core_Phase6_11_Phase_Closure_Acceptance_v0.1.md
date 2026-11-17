# EIOS — F6.11 · CIERRE Y ACEPTACIÓN FORMAL DE FASE 6

**Fecha:** 17/11/2026  
**Base auditada:** `main @ 85697d8d1268b874261d1fa5f0bcd69a291aef3b`

## 1. OBJETIVO

F6.11 no añade una nueva capacidad funcional. Su objetivo es convertir el cierre de Fase 6 en una condición **reproducible, auditable y bloqueante**.

La auditoría previa confirma que F6.1–F6.10 ya cubren las fronteras materiales previstas para esta fase:

- portabilidad Windows offline;
- adaptador externo multiempresa;
- identidad/documentación/revisor externos;
- custodia sintética write-once;
- onboarding y registro de proveedores;
- ensayo supervisado read-only;
- safe-stop ante pérdida de confianza;
- recuperación segura;
- journal de integridad del ciclo;
- retry/idempotencia tras reinicio o pérdida de ACK.

No se detecta una frontera funcional adicional que justifique prolongar la fase.

## 2. MATERIALIZACIÓN

Se añade `phase6_acceptance_manifest_v0.1.json` como inventario canónico de aceptación de Fase 6 y `tools/verify_f6_phase6_closure.py` como gate ejecutable.

El gate exige:

1. presencia ordenada de F6.1–F6.10;
2. presencia de contratos, tests y verificadores declarados;
3. inventario de módulos externos;
4. gates Linux y Windows presentes en CI;
5. ausencia de módulos F6 filtrados al núcleo canónico `eios/`;
6. mantenimiento de las prohibiciones de autoridad.

## 3. CONDICIONES DE AUTORIDAD

El cierre de Fase 6 **no cambia el estatus operacional**.

Se mantienen obligatoriamente:

- `synthetic_only=true`
- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

Cerrar F6 significa que la **arquitectura técnica sintética de despliegue externo** está cerrada para esta fase. No significa que exista autenticación empresarial real, custodia enterprise, un piloto real admitido ni autorización para producción.

## 4. PRUEBAS ADVERSARIAS

F6.11 debe rechazar el cierre si:

- falta cualquier unidad F6.1–F6.10;
- falta un artefacto declarado;
- desaparece un gate Linux o Windows;
- se promociona cualquier bandera de autoridad;
- aparece un módulo F6 dentro de `eios/`;
- se altera el orden/inventario de unidades.

## 5. CRITERIO DE CIERRE

F6.11 queda cerrada únicamente si:

- el verificador de aceptación devuelve `F6_11_PHASE6_CLOSURE_ACCEPTANCE_PASS`;
- Python y SQL permanecen verdes;
- la matriz F6 externa Linux permanece verde;
- Windows Python 3.12 offline permanece verde;
- el diff no modifica código del núcleo `eios/`;
- PR y post-merge CI quedan verdes sobre sus SHA exactos.

## 6. RESULTADO ESPERADO

Tras F6.11, la **Fase 6 queda formalmente cerrada** y no deben añadirse F6.12, F6.13, etc. salvo que una auditoría posterior descubra una regresión o una frontera material que pertenezca inequívocamente a esta fase.
