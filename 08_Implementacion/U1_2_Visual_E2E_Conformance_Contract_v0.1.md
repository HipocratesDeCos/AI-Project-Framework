# EIOS — U1.2 Visual E2E Conformance — Contract v0.1

**Baseline:** `main @ dcb2dec82b201d23b401a1ace984848e63dfc612`

**Estado:** DISEÑADO → AUDITADO → DEPURADO — IMPLEMENTACIÓN DE PRUEBA PENDIENTE

## 1. Propósito

Demostrar la cadena pública completa de presentación U1.2 sin añadir código de producción:

```text
VerticalMVPSupportResult
→ present_vertical_mvp_result
→ build_vertical_mvp_view_model
→ render_vertical_mvp_readonly
→ HTML read-only
```

## 2. Alcance

Se validan dos recorridos independientes:

1. Rules/CRC con Assessment real y traza C0;
2. Scenario Support con estados `NOT_EVALUABLE` y `FAILED`.

No se ejecuta navegador, red, persistencia ni acción empresarial.

## 3. Invariantes

- Application Boundary conserva la semántica recibida.
- View-model no recalcula Rules/CRC ni escenarios.
- Renderer no importa motores ni modelos.
- `NOT_EVALUABLE`, `FAILED`, reglas omitidas, conflictos y trazas llegan al HTML sin reinterpretación.
- Ausencia de Rules o Scenario Support permanece explícita.
- No aparecen score, ranking, mejor escenario, aprobación o autoridad decisional.
- La cadena no modifica el `VerticalMVPSupportResult` fuente.

## 4. Auditoría

No se crea nueva facade porque las tres fronteras públicas ya existen.

La prueba E2E no debe sustituir los tests unitarios existentes; solo demostrar que sus contratos encajan físicamente extremo a extremo.

Se permite construir `VerticalMVPSupportResult` mediante los contratos cerrados usados por las suites existentes. No se permite introducir resultado QTG desprendido ni reabrir cuarentenas de provenance.

## 5. Cierre

La unidad podrá cerrarse si la suite demuestra ambos recorridos sobre APIs públicas integradas y la suite completa/SQL permanecen verdes.

No habilita ejecución del Vertical desde HTML.
