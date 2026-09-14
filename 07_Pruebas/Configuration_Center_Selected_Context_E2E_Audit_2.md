# EIOS — Configuration Center Selected-Context E2E — Audit 2

**Fecha:** 2026-09-14  
**Baseline funcional:** `main @ 4399f22c605c057690e643e3429ef016c74049c4`  
**Contrato depurado:** `6c3b0eb870c2b99346515b8367f17067b12171cf`  
**Dictamen:** SUPERADA — 0 bloqueos

## 1. Objeto

Auditar el contrato E2E depurado tras A1–A4 antes de autorizar su cierre y materialización test-only.

## 2. Fronteras contrastadas

Se contrastó el contrato contra las implementaciones cerradas de:

- `eios/parameters/center.py`;
- `eios/frontend/visual/configuration_center.py`;
- `eios/frontend/visual/configuration_center_components.py`;
- `eios/frontend/visual/configuration_center_workflow.py`;
- `eios/frontend/application_boundary.py`.

La cadena propuesta usa instancias reales de `ParameterConfigurationCenter` y Slices 1–4. Los únicos dobles son los puertos de catálogo, autorización y repositorio que el propio backend define como interfaces de integración.

## 3. Verificación de A1–A4

### A1 — reloj determinista

RESUELTO. El contrato exige un repositorio E2E local con `effective_now` explícito e inmutable por escenario. No depende de `NOW` ni de fixtures temporales de otros tests.

### A2 — creación positiva sin semántica inventada

RESUELTO. El caso positivo parte de repositorio vacío y crea la primera configuración con `valid_from == effective_now`. No se modela edición in-place, sustitución ni cierre automático de una configuración activa.

### A3 — conflicto concurrente trazable

RESUELTO. El contrato separa:

- configuración externa inyectada mediante un método exclusivo del doble de prueba;
- contador `atomic_apply_calls` de la solicitud EIOS;
- histórico de la solicitud EIOS.

La comprobación requerida demuestra que la configuración externa puede existir sin que la solicitud EIOS rechazada alcance escritura atómica o genere histórico propio.

### A4 — revocación con prueba de no escritura

RESUELTO. El escenario exige conjuntamente:

- `FORBIDDEN / UNAUTHORIZED_CHANGE`;
- `atomic_apply_calls == 0`;
- repositorio sin configuraciones;
- histórico vacío;
- pending consumido;
- confirmación ausente;
- formulario retenido.

El estado visual deja de ser la única evidencia de rechazo.

## 4. Coherencia con producción cerrada

### 4.1 Backend

`ParameterConfigurationCenter.validate_change()` comprueba autorización, vigencia, validación de valor y solapes. `apply_change()` vuelve a validar antes de delegar al repositorio. El contrato E2E no evita ni sustituye estas comprobaciones.

### 4.2 Slice 1

`ConfigurationCenterUIController.confirm_and_apply()` consume el pending antes de la escritura, revalida y vuelve a pasar por `apply_change()`. Por ello:

- una revocación entre prepare/confirm debe terminar en `FORBIDDEN`;
- un solape aparecido entre prepare/confirm debe terminar en `CONFLICT`;
- en ambos casos no debe quedar pending oculto.

### 4.3 Slice 2

La confirmación solo existe en estado `AWAITING_CONFIRMATION`. Histórico vacío válido y histórico no disponible siguen siendo estados distintos.

### 4.4 Slice 3

Tras `APPLIED`, el workflow conserva el histórico previo y marca `history_stale=True`; solo un refresh real puede incorporar el histórico recién persistido. Tras fallo de confirmación mantiene el formulario y elimina la propuesta/pending.

### 4.5 Slice 4

`present_configuration_center_snapshot()` solo proyecta el snapshot público y serializa datetimes a ISO. La prueba puede verificar JSON-safety sin convertir Slice 4 en certificador de procedencia o revalidador.

## 5. Autoridad y no alcance

La prueba no introduce:

- autenticación o resolución de identidad;
- selección/enumeración de empresas;
- descubrimiento global de parámetros;
- tecnología web;
- Rules/CRC;
- simulación de impacto;
- QTG;
- decisión de compra;
- semántica de cierre automático de vigencias.

No se detecta ampliación de autoridad.

## 6. Integridad de rama antes de materialización

Comparación contra `main @ 4399f22c605c057690e643e3429ef016c74049c4`:

- `ahead = 3`;
- `behind = 0`;
- cambios presentes: únicamente contrato E2E + Audit 1;
- código de producción modificado: **0 archivos**.

## 7. Dictamen

**AUDIT 2 SUPERADA — 0 BLOQUEOS.**

Se autoriza cerrar el contrato y materializar exclusivamente el test E2E y su documentación de cierre/auditoría. Si la materialización revela una contradicción objetiva en producción, no se corregirá dentro de esta unidad: se registrará como hallazgo y se abrirá ciclo propio.
