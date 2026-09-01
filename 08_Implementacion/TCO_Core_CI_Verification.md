# TCO Core — CI Verification v0.1

**Contrato:** `08_Implementacion/TCO_Core_Implementation_Contract.md`
**Estado:** PREPARADO — verificación pendiente de implementación

## Objetivo

Definir la cobertura mínima de verificación contractual del TCO Core v0.1 sin crear todavía una implementación física.

## Matriz mínima

| ID | Invariante | Verificación requerida |
|---|---|---|
| TCO-T01 | I-TCO-01 | TCO no produce decisiones MED |
| TCO-T02 | I-TCO-02 | C0/C1/parámetros permanecen sin modificación |
| TCO-T03 | I-TCO-03 | ausencia de dato no se convierte en cero |
| TCO-T04 | I-TCO-04 | monedas incompatibles no se agregan silenciosamente |
| TCO-T05 | I-TCO-05 | coste no atribuible no contribuye al Core |
| TCO-T06 | I-TCO-06 | contradicción de entradas no se corrige silenciosamente |
| TCO-T07 | I-TCO-07 | ausencia de regla/dato no genera estimación implícita |
| TCO-T08 | I-TCO-08 | extensiones de GAP-TCO-01 no entran en el Core |

## Casos funcionales mínimos

1. Propuesta con todos los componentes necesarios y compatibles → TCO determinable.
2. Componente aplicable sin dato → resultado conserva insuficiencia; no se sustituye por cero.
3. Componente no aplicable → no contribuye.
4. Monedas incompatibles sin normalización autorizada → no agregación silenciosa.
5. Cantidad/precio/importe contradictorios → no corrección silenciosa.
6. Coste sin atribución demostrable → no contribuye.
7. Condición de pago presente sin regla financiera TCO → no se convierte automáticamente en coste financiero.
8. Petición de decisión de compra → TCO no la produce.

## Trazabilidad

Cada test deberá poder mapearse a un invariante del Implementation Contract y, cuando exista, a la prueba canónica correspondiente en `07_Pruebas`.

Si una prueba canónica no existe, deberá identificarse como cobertura faltante antes de declarar CI completo.

## Límites

Este documento no constituye implementación, no crea nuevas reglas económicas y no resuelve GAP-TCO-01.
