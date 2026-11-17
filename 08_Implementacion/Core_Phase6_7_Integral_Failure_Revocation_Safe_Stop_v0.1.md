# EIOS — F6.7 · FALLOS INTEGRALES, REVOCACIÓN Y PARADA SEGURA

**Fecha:** 17/11/2026. **Base:** F6.6 cerrada en `main @ 59560a9d83cd131267ab68a64b4c9312a38646ae`.

## 1. DISEÑO

F6.7 no vuelve a implementar las comprobaciones unitarias ya existentes. F6.3 ya rechaza cambios de identidad, documento o permiso entre lecturas; F6.4 verifica custodia y huella; F6.5 valida vigencia, revocación y pin del registro antes y después de cada llamada; F6.6 conserva una preparación sintética sin autoridad.

La necesidad restante es **integral**: demostrar que un resultado F6.6 previamente correcto deja de ser reutilizable cuando el estado externo cambia.

Se añade únicamente al paquete externo `eios-onboarding-example==0.1.0`:

- `safe_stop.py`: revalidación fresca de toda la cadena antes de reutilizar un resultado F6.6.
- `safe_stop_demo.py`: un caso sano y un caso con revocación sobrevenida.
- pruebas adversarias integrales.

No se modifica `eios/`, QTG, O1, admisión operacional, PRICE, Finance ni contratos canónicos.

## 2. CONTRATO

`revalidate_before_rehearsal_reuse(...)` exige un resultado F6.6 completo y vuelve a ejecutar F6.5, que a su vez vuelve a recorrer F6.3 y F6.4.

Si la cadena permanece idéntica, el único estado permitido es:

`SYNTHETIC_CHAIN_REVALIDATED`

y continúa con:

- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

Si aparece cualquier cambio o fallo, devuelve:

`SAFE_STOPPED`

con:

- etapa del fallo;
- código/motivo conservado;
- `previous_result_invalidated=true`;
- `fresh_revalidation_passed=false`;
- autoridad operacional siempre denegada.

No existe fallback que reconstruya un recibo favorable usando el resultado anterior.

## 3. PRUEBAS INTEGRALES

F6.7 cubre después de un éxito previo:

1. revocación/revisión del registro de proveedores;
2. caducidad/cambio de proveedor;
3. alteración del documento custodiado;
4. cambio inesperado de empresa, proyecto o snapshot;
5. interrupción de un proveedor;
6. revocación del permiso entre comprobaciones;
7. estabilidad determinista del motivo de parada;
8. cadena sin cambios, que solo puede revalidarse como sintética.

La finalidad es probar la **propagación del fallo hasta la salida final**, no duplicar las pruebas aisladas F6.3–F6.6.

## 4. CRITERIO DE CIERRE

F6.7 solo se cerrará si:

- pasan tests nuevos y regresión completa;
- el wheel externo auditado incluye exactamente los nuevos módulos;
- la demo F6.7 se ejecuta en instalación offline independiente en Linux y Windows;
- el diff permanece fuera del núcleo canónico;
- CI de PR es satisfactoria en el SHA exacto;
- el merge se realiza sobre ese SHA;
- CI postmerge en el nuevo `main` finaliza satisfactoriamente.

F6.7 sigue siendo exclusivamente sintética. No autentica una empresa real ni habilita una ruta operacional.
