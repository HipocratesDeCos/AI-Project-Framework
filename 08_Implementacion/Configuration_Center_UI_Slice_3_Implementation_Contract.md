# EIOS — Configuration Center UI Slice 3 — Selected Context Workflow Contract v0.1

**Estado:** DISEÑO  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 92695ad866bf72575f01ac7c203394315418dd27`  
**Dependencias cerradas:** Slice 1 + Slice 2 del Configuration Center UI

## 1. Objeto

Orquestar el flujo de interacción del Configuration Center para un contexto empresa/parámetro/actor ya seleccionado y suministrado por una frontera confiable, conectando el controlador de Slice 1 con los componentes de Slice 2 sin crear productores ausentes.

## 2. Alcance

El workflow puede:

- cargar detalle + histórico del contexto seleccionado;
- mantener un snapshot presentacional de esos datos;
- representar edición local mediante `ConfigurationChangeForm`;
- preparar un cambio delegándolo en `ConfigurationCenterUIController.prepare_change(...)`;
- conservar una `ChangeProposal` únicamente si Slice 1 devuelve `AWAITING_CONFIRMATION`;
- representar confirmación mediante Slice 2;
- cancelar una propuesta pendiente;
- confirmar/aplicar mediante `ConfigurationCenterUIController.confirm_and_apply()`;
- actualizar el detalle local exclusivamente con la `Configuration` realmente devuelta por el backend tras `APPLIED`;
- marcar el histórico como `stale` tras una aplicación hasta un refresh explícito;
- refrescar detalle e histórico cuando no exista confirmación pendiente.

## 3. Exclusiones

Slice 3 no:

- autentica ni resuelve identidad;
- selecciona o enumera empresas;
- lista/busca parámetros globalmente;
- crea contexto autorizado;
- accede directamente a backend de parametrización;
- valida funcionalmente valores;
- escribe en persistencia;
- inventa histórico tras un cambio;
- genera Rules/CRC/excepciones;
- simula impacto;
- produce decisiones de compra.

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

Slice 3 no reemplaza ninguna responsabilidad de Slice 1 o Slice 2.

## 5. Snapshot de workflow

El workflow expondrá un carrier inmutable `ConfigurationWorkflowSnapshot` con:

- `screen: ConfigurationCenterScreen`;
- `data_ready: bool`;
- `history_stale: bool`.

`history_stale` es metadato técnico de frescura local, no inferencia de negocio.

## 6. Carga inicial / refresh

`refresh()`:

1. falla cerrado si existe confirmación pendiente;
2. llama a `controller.load_detail()`;
3. si falla el detalle, no llama al histórico, deja `data_ready=False` y representa el estado/error de Slice 1;
4. si detalle existe, llama a `controller.load_history()`;
5. si histórico falla, conserva el detalle, representa histórico no disponible, `data_ready=False` y estado/error de Slice 1;
6. si ambos son válidos, `data_ready=True`, `history_stale=False` y estado `VIEWING`.

Un histórico vacío `()` sigue siendo carga válida.

## 7. Edición local

`edit(form)`:

- exige `data_ready=True`;
- no llama al backend;
- conserva el formulario exacto;
- produce estado visible `EDITING`;
- no crea propuesta ni confirmación.

## 8. Preparación

`prepare(form)`:

- exige `data_ready=True`;
- crea una `ChangeProposal` exactamente con los campos del formulario;
- delega validación a `controller.prepare_change(...)`;
- solo conserva la propuesta si el resultado es `AWAITING_CONFIRMATION`;
- en fallo descarta cualquier propuesta anterior y representa el código/estado devuelto;
- no altera actor, empresa ni parámetro.

La propuesta retenida por Slice 3 es una copia presentacional exacta de los mismos valores enviados a Slice 1; no constituye autorización propia.

## 9. Confirmación

`confirm()`:

- exige propuesta retenida y `controller.has_pending_confirmation=True`;
- delega exclusivamente en `controller.confirm_and_apply()`;
- consume la propuesta local cualquiera que sea el resultado;
- nunca vuelve a presentar confirmación tras fallo sin nueva preparación.

### 9.1 Resultado `APPLIED`

Si Slice 1 devuelve `APPLIED` con `Configuration`:

- el detalle local sustituye únicamente su campo `configuration` por esa instancia realmente devuelta;
- el formulario se limpia;
- el histórico existente no se modifica ni se inventa una entrada;
- `history_stale=True` hasta `refresh()` satisfactorio;
- el estado visible permanece `APPLIED` aunque el histórico local sea anterior al cambio.

### 9.2 Resultado de fallo

En fallo:

- no se modifica detalle ni histórico;
- se conserva el formulario como entrada editable para una futura corrección;
- no existe panel de confirmación;
- estado/error proceden literalmente del resultado de Slice 1.

## 10. Cancelación

`cancel()`:

- si existe pending en Slice 1, delega en `controller.cancel_pending_change()`;
- limpia propuesta y formulario locales;
- vuelve a `VIEWING` utilizando el snapshot de datos vigente;
- no llama a backend de parametrización directamente.

## 11. Regla anti-refresh durante confirmación

Mientras exista `controller.has_pending_confirmation=True`, `refresh()` debe fallar cerrado mediante error técnico de workflow.

Motivo: los métodos de lectura de Slice 1 actualizan su estado observable; refrescar durante confirmación podría ocultar visualmente `AWAITING_CONFIRMATION` dejando una propuesta pendiente activa.

El usuario/integrador debe cancelar o confirmar antes de refrescar.

## 12. Error técnico de workflow

Las precondiciones internas se expresarán mediante `ConfigurationWorkflowError(RuntimeError)` y no mediante códigos de dominio inventados.

Ejemplos:

- editar/preparar antes de carga válida;
- confirmar sin propuesta pendiente coherente;
- refrescar durante confirmación pendiente.

## 13. Tests obligatorios

- refresh exitoso conserva detalle/histórico y marca datos listos;
- detalle fallido corta el histórico;
- histórico fallido conserva detalle pero `data_ready=False`;
- histórico vacío es válido;
- edit no llama controlador de cambios;
- prepare conserva propuesta solo en `AWAITING_CONFIRMATION`;
- prepare fallido no crea confirmación;
- refresh durante pending falla sin mutar pending;
- cancel limpia pending local/controlador;
- confirm delega una sola vez;
- `APPLIED` actualiza detalle solo desde configuración devuelta;
- `APPLIED` marca histórico stale y no lo altera;
- refresh posterior a `APPLIED` limpia stale;
- confirm fallido no altera snapshots y obliga a nueva preparación;
- workflow no accede a catalogue/repository/authorization/SQL.

## 14. Invariantes

**CCUIS3-I01:** selected context únicamente; no crea selección.  
**CCUIS3-I02:** semántica funcional delegada a Slice 1.  
**CCUIS3-I03:** composición visual delegada a Slice 2.  
**CCUIS3-I04:** pending local solo existe si Slice 1 está `AWAITING_CONFIRMATION`.  
**CCUIS3-I05:** refresh prohibido durante pending.  
**CCUIS3-I06:** `APPLIED` exige configuración real del backend.  
**CCUIS3-I07:** histórico no se inventa; tras apply queda stale.  
**CCUIS3-I08:** fallo no muta snapshots funcionales.  
**CCUIS3-I09:** errores de precondición del workflow no se disfrazan de dominio.  
**CCUIS3-I10:** no decisión de compra.
