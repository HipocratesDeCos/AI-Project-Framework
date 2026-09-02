# EIOS — U1.1 · DISEÑO — FRONTEND VISUAL CEO

**Estado:** 🟡 DISEÑO INICIAL
**Baseline:** `c059af68ad489f64d5ff1dfa7bf5f5a113588854`
**Precedente:** U1 Application Boundary MVP

## Propósito

Materializar la experiencia visual mediante la que un CEO introduce una operación, revisa contexto/evidencia, solicita ejecución y comprende el Decision Support Package.

## Principio arquitectónico

```text
CEO
 ↓
U1.1 Visual Frontend
 ↓
U1 Application Boundary
 ↓
O1
 ↓
Decision Support Package
 ↓
U1.1 Visual Frontend
 ↓
CEO / DECISIÓN HUMANA
```

El frontend visual no accede directamente a motores analíticos.

## Pantallas MVP

1. Dashboard ejecutivo.
2. Nueva operación.
3. Evidencia y calidad.
4. Contexto de decisión.
5. Ejecución y estado.
6. Resultado ejecutivo.
7. Escenarios.
8. Comparación Decision Twin.

## Reglas visuales obligatorias

- Los estados técnicos se muestran literalmente.
- `NOT_EVALUABLE` nunca se representa como negativo.
- `FAILED` nunca se representa como decisión.
- Las limitaciones permanecen visibles.
- Evidencia y trazabilidad son accesibles desde el resultado.
- Los escenarios se presentan sin ranking implícito.
- La decisión humana aparece como una acción separada del resultado EIOS.
- No existen botones de compra, aprobación o negociación automática.

## Formulario CEO

Campos de negocio únicamente. La interfaz no permite editar libremente fingerprints, snapshots, versiones de reglas/parámetros ni identidades técnicas.

Validación local = formato y completitud.
Validación de dominio = contratos EIOS.

## Resultado ejecutivo

La jerarquía visual será:

**Qué sabemos → Qué ha calculado EIOS → Qué falta/qué riesgo existe → Qué escenarios existen → Decisión humana.**

No se generará un “score CEO” adicional.

## Accesibilidad

MVP: teclado, foco visible, labels, mensajes de error asociados, contraste suficiente, estados no dependientes solo del color, responsive y lenguaje comprensible.

## Fuera de alcance

Autonomía decisional, ranking, recomendación automática, ejecución de compra, edición de reglas/parámetros maestros, persistencia nueva y autenticación empresarial.

## Criterios de auditoría

La auditoría deberá verificar frontera U1.1→U1, semántica de estados, ausencia de autoridad paralela, trazabilidad, evidencia, accesibilidad y separación estricta entre resultado EIOS y decisión humana.
