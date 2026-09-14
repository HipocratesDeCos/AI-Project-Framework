# EIOS — Configuration Center UI Slice 3 — Selected Context Workflow Contract v0.1

**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 92695ad866bf72575f01ac7c203394315418dd27`  
**Dependencias cerradas:** Slice 1 + Slice 2 del Configuration Center UI

## 1. Objeto

Orquestar el flujo de interacción del Configuration Center para un contexto empresa/parámetro/actor ya seleccionado y suministrado por una frontera confiable, conectando el controlador de Slice 1 con los componentes de Slice 2 sin crear productores ausentes.

## 2. Alcance

El workflow puede cargar detalle + histórico; mantener snapshot presentacional; representar edición local; preparar un cambio mediante Slice 1; conservar propuesta únicamente cuando estado y pending real sean coherentes; representar confirmación mediante Slice 2; cancelar; confirmar/aplicar; actualizar detalle exclusivamente desde la `Configuration` devuelta por backend; marcar histórico stale tras apply; y refrescar cuando no exista edición ni confirmación activa.

## 3. Exclusiones

Slice 3 no autentica, resuelve identidad, selecciona/enumera empresas, lista/busca parámetros globalmente, crea contexto autorizado, accede directamente al backend de parametrización, valida funcionalmente valores, escribe persistencia, inventa histórico, genera Rules/CRC/excepciones, simula impacto ni produce decisiones de compra.

## 4. Dependencias obligatorias

```text
Trusted upstream integration
        ↓
ConfigurationCenterUIController   (Slice 1)
        ↓
ConfigurationCenterSelectedWorkflow  (Slice 3)
        ↓
build_configuration_center_screen (Slice 2)
```

Slice 3 no reemplaza responsabilidades de Slice 1 o Slice 2.

## 5. Snapshot de workflow

Carrier inmutable `ConfigurationWorkflowSnapshot`:

- `screen: ConfigurationCenterScreen`;
- `data_ready: bool`;
- `history_stale: bool`.

`history_stale` expresa frescura técnica local, no inferencia de negocio.

## 6. Carga inicial / refresh

`refresh()`:

1. falla cerrado si existe confirmación pendiente o formulario/borrador local activo;
2. invalida cualquier snapshot previo que no pueda demostrarse actual durante esta carga;
3. llama a `controller.load_detail()`;
4. si falla detalle: establece detalle e histórico locales a `None`, `data_ready=False`, no llama histórico y representa estado/error de Slice 1;
5. si detalle existe, lo conserva como detalle de esta carga y llama a `controller.load_history()`;
6. si histórico falla: sustituye cualquier histórico previo por `None`, conserva el nuevo detalle, `data_ready=False` y representa estado/error de Slice 1;
7. si ambos son válidos: reemplaza ambos snapshots, `data_ready=True`, `history_stale=False`, estado `VIEWING`.

`history=()` es carga válida. Para refrescar durante una edición local debe ejecutarse antes `cancel()` para descartar explícitamente el borrador.

## 7. Edición local

`edit(form)`:

- exige `data_ready=True`;
- exige que no exista confirmación pendiente en Slice 1;
- no llama al backend;
- conserva el formulario exacto;
- sustituye, cuando proceda, otro borrador local todavía no preparado;
- produce estado visible `EDITING`;
- no crea propuesta ni confirmación.

## 8. Preparación y coherencia de pending

`prepare(form)`:

- exige `data_ready=True`;
- exige que no exista pending previo en Slice 1;
- crea una `ChangeProposal` exacta desde el formulario;
- conserva el formulario como entrada visible;
- delega en `controller.prepare_change(...)`;
- si `result.state == "AWAITING_CONFIRMATION"`, exige también `controller.has_pending_confirmation is True`; solo entonces conserva propuesta y genera confirmación;
- si el resultado no es `AWAITING_CONFIRMATION`, exige `controller.has_pending_confirmation is False`, descarta propuesta y representa estado/error recibido;
- cualquier divergencia estado ↔ pending produce `ConfigurationWorkflowError` y no genera confirmación visual;
- no altera actor, empresa ni parámetro.

La propuesta local es copia presentacional exacta de los valores enviados a Slice 1 y no constituye autorización propia.

## 9. Confirmación y coherencia post-confirm

`confirm()`:

- exige propuesta local y `controller.has_pending_confirmation=True`;
- delega exclusivamente en `controller.confirm_and_apply()`;
- consume la propuesta local cualquiera que sea el resultado;
- exige que, tras la llamada, `controller.has_pending_confirmation=False`; si no, produce `ConfigurationWorkflowError`;
- nunca vuelve a presentar confirmación tras fallo sin nueva preparación.

### 9.1 Resultado `APPLIED`

`APPLIED` solo es coherente si `result.configuration is not None` y el pending ha sido consumido.

Entonces:

- el detalle local sustituye únicamente `configuration` por la instancia realmente devuelta;
- el formulario se limpia;
- el histórico existente no se altera ni se inventa una entrada;
- `history_stale=True` hasta refresh satisfactorio;
- el estado visible permanece `APPLIED`.

Un `APPLIED` sin `Configuration` produce `ConfigurationWorkflowError` y no actualiza snapshot.

### 9.2 Resultado de fallo

En resultado distinto de `APPLIED`:

- no se modifica detalle ni histórico;
- se conserva formulario como entrada editable;
- no existe panel de confirmación;
- estado/error proceden literalmente del resultado de Slice 1;
- `result.configuration`, si apareciera de forma incoherente en un estado no `APPLIED`, no se usa para mutar snapshot.

## 10. Cancelación

`cancel()` es la operación explícita para abandonar tanto un borrador local como una confirmación pendiente:

- si existe pending en Slice 1, delega en `controller.cancel_pending_change()`;
- limpia propuesta y formulario locales;
- verifica que el pending haya quedado consumido;
- vuelve a `VIEWING` cuando existe snapshot válido; si aún no hay datos válidos conserva un estado técnico no operativo sin inventar datos;
- no accede al backend directamente.

## 11. Regla anti-refresh durante edición/confirmación

Mientras exista `controller.has_pending_confirmation=True` **o** un `ConfigurationChangeForm` local activo, `refresh()` falla mediante `ConfigurationWorkflowError` sin alterar pending, borrador ni snapshots.

Esto impide que una lectura o un cambio de snapshot oculte una propuesta todavía aplicable o deje un borrador construido contra datos sustituidos.

## 12. Error técnico de workflow

Las precondiciones/incoherencias internas usan `ConfigurationWorkflowError(RuntimeError)`, nunca códigos de dominio inventados.

Casos mínimos:

- editar/preparar antes de carga válida;
- editar/preparar mientras existe pending;
- confirmar sin propuesta/pending coherentes;
- refrescar durante borrador/pending;
- divergencia estado ↔ pending tras prepare;
- pending no consumido tras confirm/cancel;
- `APPLIED` sin `Configuration`.

## 13. Tests obligatorios

- refresh exitoso conserva detalle/histórico y marca datos listos;
- detalle fallido invalida detalle/histórico previos y corta lectura de histórico;
- histórico fallido conserva nuevo detalle, invalida histórico previo y `data_ready=False`;
- histórico vacío es válido;
- edit no llama controlador de cambios;
- edit/prepare con pending previo fallan cerrado;
- refresh con borrador activo falla sin perder el borrador;
- prepare conserva propuesta solo con `AWAITING_CONFIRMATION` + pending real;
- divergencias estado/pending fallan cerrado;
- prepare fallido no crea confirmación;
- refresh durante pending falla sin mutar pending/snapshots;
- cancel limpia borrador/pending local/controlador;
- confirm delega una sola vez y exige pending consumido;
- `APPLIED` sin configuración falla cerrado;
- `APPLIED` válido actualiza detalle solo desde configuración devuelta;
- `APPLIED` marca histórico stale sin alterarlo;
- refresh posterior a `APPLIED` limpia stale;
- confirm fallido no altera snapshots y obliga a nueva preparación;
- workflow no accede a catalogue/repository/authorization/SQL.

## 14. Invariantes

**CCUIS3-I01:** selected context únicamente; no crea selección.  
**CCUIS3-I02:** semántica funcional delegada a Slice 1.  
**CCUIS3-I03:** composición visual delegada a Slice 2.  
**CCUIS3-I04:** estado de confirmación y pending deben ser coherentes.  
**CCUIS3-I05:** refresh prohibido durante borrador o pending.  
**CCUIS3-I06:** nueva edición/preparación prohibida durante pending.  
**CCUIS3-I07:** `APPLIED` exige configuración real y pending consumido.  
**CCUIS3-I08:** histórico no se inventa; tras apply queda stale.  
**CCUIS3-I09:** refresh fallido no conserva datos previos como actuales; errores internos no se disfrazan de dominio.  
**CCUIS3-I10:** no decisión de compra.
