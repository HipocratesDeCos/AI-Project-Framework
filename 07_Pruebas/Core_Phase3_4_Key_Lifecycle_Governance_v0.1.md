# EIOS — FASE 3.4 · CICLO DE VIDA DE CLAVES CORPORATIVAS Y REVOCACIÓN

**Fecha:** 2026-11-16  
**Base:** `main @ fb773e010dd44947417a1acd5d2edeb32b4c64f3` (F3.3 integrada y validada).  
**Alcance:** contrato de verificación (solo lectura) del alta, autorización, renovación, suspensión y revocación de claves de firma por empresa. **No** incluye administración real de identidades ni emisión de autorizaciones por EIOS.

## 1. DISEÑAR · Riesgo encontrado

F3.3 verifica criptográficamente un manifiesto usando una clave pública que el host configura. Pero si después la empresa **revoca** esa clave, una instancia que conservara la clave en memoria podría seguir aceptando mensajes firmados antes de la revocación. El repositorio tampoco dispone de registro corporativo de claves, gestor de permisos ni autenticación empresarial comprobada.

**Solución segura de alcance limitado:** un adaptador sobre el mismo puerto `ParameterVersionSource` de F2.4 que verifica **cada vez** el historial de gobierno de la clave, firmado por una autoridad independiente y sujeto a un control anti-rollback separado.

## 2. AUDITAR · Dos fuentes separadas, ninguna inventada por EIOS

El nuevo módulo `eios/parameters/key_lifecycle.py` exige explícitamente tres insumos que proporciona un host externo ya autorizado:

1. **`GovernanceVerificationKey`:** clave pública Ed25519 de gobierno, segregada por `company_id`, identificada por `governance_key_id` y con vigencia. Debe estar anclada fuera de cualquier documento, app o base editable del expediente.
2. **`KeyLifecycleHistoryRepository`:** servicio de lectura del historial completo de eventos de clave, entregado como JSON canónico y firma digital de la autoridad de gobierno. El historial está ordenado y es acumulativo.
3. **`TrustedLifecycleCheckpointSource`:** fuente **independiente** del historial que conserva la última revisión y la huella SHA-256 exacta de sus bytes. La coincidencia de huella y revisión evita aceptar una copia antigua cuando esta fuente ya registra una revocación. La fiabilidad de ese control exige persistencia externa monotónica y segregada de permisos.

También se requiere `SignedVersionRecordRepository` existente de F3.3. EIOS **no** crea tablas, servicios de claves, cuentas, roles ni claves privadas.

Sin gobierno firmado + punto de control verificable, la fuente devuelve error. No existe modo permisivo.

## 3. DEPURAR · Estados y reglas

El historial firmado `EIOS-ISSUER-KEY-LIFECYCLE/v0.1` almacena eventos canónicos e íntegros en secuencia `1..revision`; todos los eventos llevan identidad `key_id`, marca temporal y tipo. Solo se permiten:

| Evento | Desde | Hacia | Condición |
|---|---|---|---|
| `ENROLL` | Sin registro | `PENDING` | Nueva clave pública Ed25519, vigencia explícita; no se admite `approval_ref` |
| `AUTHORIZE` | `PENDING` o `SUSPENDED` | `ACTIVE` | Requiere referencia de aprobación; rechaza una clave caducada |
| `RENEW` | `ACTIVE` | `ACTIVE` | Referencia de aprobación, extensión de vigencia, clave pública inalterada |
| `SUSPEND` | `ACTIVE` | `SUSPENDED` | Referencia de aprobación |
| `REVOKE` | No revocada | `REVOKED` | Referencia de aprobación; **irreversible** |

La **rotación** consiste en dar de alta una clave diferente, aprobarla y revocar la antigua. No se permite reutilizar el mismo `key_id` ni reautorizar uno revocado. La ventana entre los eventos depende de la autoridad que firma la política; EIOS no aprueba sus decisiones.

Las referencias `approval_ref` son *pistas documentales registradas y firmadas por el gobierno*, **no** pruebas independientes de que el aprobador exista o tenga competencia. El origen del documento, aprobador, revocaciones efectivas y permisos sobre el checkpoint pertenecen al host externo.

## 4. AUDITAR 2 · Frontera de ejecución

`GovernedParameterVersionSource` implementa el puerto F2.4:

1. Obtiene último checkpoint externo, historial y firma Ed25519 de gobierno.
2. Comprueba integridad exacta, revisión, emisor/empresa, firmas, vigencia y transiciones de todos los eventos.
3. Rechaza clave no enrolada, pendiente, suspendida, revocada o fuera de vigencia; **una revocación bloquea también firmas históricas** en el modo conservador de esta unidad.
4. Utiliza la clave pública **extraída del historial validado**, no del documento de la compra, para invocar `Ed25519VerifiedParameterVersionSource` de F3.3.
5. Relee historial y checkpoint **después** de verificar el manifiesto y rechaza el cambio `KEY_LIFECYCLE_CHANGED`. F2.4, por su parte, vuelve a consultar la fuente alrededor de la resolución canónica.
6. No publica manifestaciones, revisiones o autorizaciones; la consulta es de solo lectura. Una firma válida no demuestra verdad comercial ni autoriza una compra.

La comparación de dos lecturas detecta cambios observables durante la consulta. **No** proporciona transacciones distribuidas, un reloj incuestionable ni garantía contra una revocación que llegue después de la comprobación final. Tampoco protege si la autoridad de gobierno y el checkpoint se comprometen simultáneamente.

## 5. PRUEBAS

`tests/test_key_lifecycle.py` genera claves de emisor y gobierno efímeras solo en memoria y ensaya integraciones con F3.3/F2.4: autorización válida, clave sin aprobar, suspensión, reautorización, renovación, revocación, imposibilidad de resucitar o reusar ID, rollback de historial, checkpoint viejo o ausente, firma ajena con checkpoint correcto, clave de gobierno ajena, empresa/issuer cruzados, secuencias inválidas, documento caducado/futuro, alteración de selección, evidencia documental faltante, cambio a mitad de consulta y rotación de claves.

**Restricción constante:** `decision_authority=False`, `operational_path=FORBIDDEN`. No se sustituye C0, Finance, QTG, PRICE, Rules ni Decision Versioning, ni se altera ningún esquema SQL.

## 6. CERRAR / MATERIALIZAR / CI

Cierre de F3.4 condicionado a CI Python+SQL satisfactoria en HEAD de PR, auditoría de diff y CI post-merge de `main`. **Esta unidad entrega únicamente la infraestructura verificadora**, no un registro empresarial real.

### Pendiente fuera de F3.4

- Emisor de eventos de gobierno **real** y anclaje seguro de su clave pública.
- Registro corporativo con autenticación de responsables, doble aprobación cuando corresponda, protección de claves privadas, rotación de la autoridad de gobierno, derechos y revocación.
- Checkpoint monotónico empresarial independiente y su procedimiento de recuperación seguro.
- Integración con proveedor real de documentos firmados, identidad de empresa autenticada y evidencia C0 admitida.
- Comprobación del flujo operativo de extremo a extremo antes de autorizarlo.

**Fase 3 global abierta. No habilitar ruta operacional basándose en tests sintéticos.**
