# EIOS — Contrato de Arquitectura UI v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA
**Baseline:** `cacc68d0f5b29c5fb80d3a7ce81b540bcc58b8d4`
**Fecha:** 2026-09-07

## 1. Propósito

Definir la frontera arquitectónica previa al código de UI. Este contrato no crea campos, reglas de negocio, fórmulas ni nuevos identificadores de prueba.

## 2. Capas

```text
Presentation
    ↓
Interaction Controller
    ↓
Authorized Service Boundary
    ↓
Existing Domain Authority
    ↓
Result / Trace
    ↓
Presentation
```

### Presentation
Responsable exclusivamente de renderizado, composición visual, accesibilidad y captura de interacción.

### Interaction Controller
Responsable de coordinar eventos y estados de UI. No calcula resultados de negocio.

### Authorized Service Boundary
Único punto de entrada desde la UI hacia operaciones autorizadas.

### Existing Domain Authority
Contiene las reglas y cálculos ya autorizados por EIOS. Esta capa no se redefine aquí.

### Result / Trace
Transporta resultados y referencias de trazabilidad hacia la presentación sin modificar evidencia histórica.

## 3. Dependencias

Las dependencias deben ser unidireccionales. Presentation no puede importar Domain Authority directamente. Ningún componente puede acceder directamente a persistencia o a reglas de negocio.

## 4. Estado

El estado efímero de interacción pertenece al controlador de UI y comprende únicamente los estados ya definidos por el Functional Contract. No se persiste como dato de dominio.

## 5. Datos

Los datos de entrada y salida se identifican mediante las autoridades documentales existentes. No se permite duplicar modelos semánticos en componentes visuales.

## 6. Errores

Los errores se transportan mediante una representación común de UI. La presentación no interpreta errores para generar decisiones de negocio.

## 7. Trazabilidad

La trazabilidad se conserva como referencia de lectura. La arquitectura no permite que la UI reescriba evidencia histórica.

## 8. STK

La arquitectura no permite que STK sea una fuente de inferencia metodológica para M01–M10. Cualquier ausencia de metodología autorizada debe permanecer explícita.

## 9. Testabilidad

Las fronteras Presentation → Controller → Service deben ser sustituibles/aislables para pruebas futuras. No se crean Test_ID ni se modifica el Plan de Pruebas en este contrato.

## 10. Criterio de conformidad

Una implementación cumple cuando las dependencias respetan la dirección definida, cada interacción tiene autoridad documental identificable y ninguna capa introduce semántica o lógica paralela.

**Siguiente gate: AUDITAR.**