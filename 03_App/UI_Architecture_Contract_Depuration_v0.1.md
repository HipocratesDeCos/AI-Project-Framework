# EIOS — Depuración del Contrato de Arquitectura UI v0.1

**Estado:** DEPURACIÓN COMPLETADA — 8/8 PASS
**Baseline:** `8067a2a4d6a15d390f6c3cc5257bf42b76a94317`
**Fecha:** 2026-09-07

## Matriz

| ID | Control | Resultado |
|---|---|---|
| UIA-D01 | Presentation queda limitada a renderizado, accesibilidad y captura | PASS |
| UIA-D02 | Controller solo coordina eventos y estados | PASS |
| UIA-D03 | Service Boundary es la única puerta UI→operaciones | PASS |
| UIA-D04 | Domain Authority no se redefine en UI | PASS |
| UIA-D05 | Estado efímero no se persiste como dominio | PASS |
| UIA-D06 | Modelos semánticos no se duplican | PASS |
| UIA-D07 | Trazabilidad es de lectura y STK no infiere M01–M10 | PASS |
| UIA-D08 | Fronteras son aislables sin crear Test_ID ni alterar pruebas | PASS |

## Ajustes de depuración

1. Se fija una única dirección de dependencias.
2. Se prohíben imports directos de Presentation a Domain Authority.
3. El Controller no puede contener cálculos financieros ni reglas de decisión.
4. Toda llamada desde UI a operaciones pasa por Authorized Service Boundary.
5. Los estados UI no forman parte del modelo canónico.
6. Los DTO/modelos de UI no pueden redefinir la semántica del Registry.
7. Trace se trata como referencia inmutable desde UI; STK queda explícitamente fuera de inferencia M01–M10.
8. Las fronteras arquitectónicas quedan preparadas para pruebas futuras sin modificar el Plan de Pruebas.

## Resultado

**DEPURACIÓN: PASS — 8/8.**

Preparado para AUDITAR 2.

`main` no se modifica.