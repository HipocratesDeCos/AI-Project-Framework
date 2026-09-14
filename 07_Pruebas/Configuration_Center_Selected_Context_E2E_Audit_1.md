# EIOS — Configuration Center Selected-Context E2E — Audit 1

**Fecha:** 2026-09-14  
**Baseline auditado:** `38fdfe7da01be21b0e56f5fdd6c577996045cee6`  
**Dictamen:** APTO PARA DEPURACIÓN — 4 precisiones, 0 bloqueos

## 1. Fuentes contrastadas

- `eios/parameters/center.py`;
- `tests/test_parameter_configuration.py`;
- `eios/frontend/visual/configuration_center.py`;
- `eios/frontend/visual/configuration_center_components.py`;
- `eios/frontend/visual/configuration_center_workflow.py`;
- `eios/frontend/application_boundary.py`;
- contratos/cierres Slices 1–4.

## 2. Verificaciones limpias

- `ParameterConfigurationCenter` admite puertos explícitos de catálogo, autorización y repositorio, por lo que esos dobles son arquitectónicamente legítimos;
- el backend real revalida en `apply_change()`;
- Slice 1 revalida además antes de invocar `apply_change()`;
- el repositorio contractual debe repetir el control de conflicto dentro de la escritura atómica;
- Slice 3 limpia el formulario tras `APPLIED`, permitiendo refresh posterior;
- tras fallo de confirmación Slice 3 conserva el formulario y consume la propuesta/pending, conforme al contrato.

## 3. Hallazgos y depuración requerida

### A1 — reloj determinista del repositorio de prueba

El `FakeRepository` existente en `test_parameter_configuration.py` usa una constante global `NOW`. Reutilizarlo directamente haría la prueba dependiente de su fixture y dificultaría distinguir el instante efectivo del escenario E2E.

**Depuración:** crear un repositorio E2E local con `effective_now` explícito e inmutable para cada escenario. No modifica producción.

### A2 — creación positiva debe evitar semántica de “edición in-place” inexistente

El backend actual rechaza intervalos solapados y no contiene una operación que cierre automáticamente la configuración vigente.

**Depuración:** el caso positivo parte de repositorio vacío y crea la primera configuración con `valid_from == effective_now`. No se simulará sustitución de una configuración activa.

### A3 — conflicto concurrente debe distinguir la escritura externa de la escritura EIOS rechazada

Si se inserta una configuración externa después de `prepare()`, el repositorio ya no estará vacío. Un simple `len(configurations) == 1` no basta para demostrar qué ocurrió.

**Depuración:** el puerto de prueba tendrá `inject_external_configuration(...)` y contadores separados para `atomic_apply_calls`. El escenario debe demostrar:

- una configuración externa inyectada;
- `atomic_apply_calls` no aumenta por la solicitud rechazada si la revalidación previa detecta el conflicto;
- no se genera histórico de la solicitud EIOS rechazada.

### A4 — revocación debe probar no escritura, no solo estado visual

El estado `FORBIDDEN` por sí solo no demuestra que la persistencia permaneció intacta.

**Depuración:** verificar simultáneamente:

- `atomic_apply_calls == 0`;
- configuraciones del repositorio vacías;
- histórico vacío;
- `controller.has_pending_confirmation == False`;
- confirmación ausente y formulario retenido en el snapshot/payload.

## 4. Límites revalidados

La unidad no debe:

- importar ni modificar internals privados de Slices 1–4;
- monkeypatchar métodos de producción;
- seleccionar empresas/parámetros dinámicamente;
- introducir cierre automático de vigencias;
- afirmar autenticación;
- modificar código de producción.

## 5. Dictamen

No existe bloqueo. Incorporando A1–A4, la prueba será una conformidad E2E real del subconjunto selected-context y no una simulación de capacidades inexistentes.
