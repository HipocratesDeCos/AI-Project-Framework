# EIOS — F6.3 · FRONTERA EXTERNA DE IDENTIDAD, DOCUMENTOS Y PERMISO DE REVISIÓN

**Fecha:** 17/11/2026. **Base:** `main @ bc60e35a0fe76861e1c9e0667e3c1b27d788dfff` (F6.2 cerrada; CI Linux/Windows postmerge #44074266596 SUCCESS).  
**Estado documental:** CANDIDATO. El cierre exige CI PR en SHA exacto, diff auditado, merge controlado y CI postintegración en el nuevo SHA de `main`.

## 1. DISEÑAR — EVITAR CONFUNDIR CINCO COMPROBACIONES

La existencia de un archivo, su SHA-256, la estructura validada, la identidad empresarial y el mandato de quien lo revisa son **hechos independientes**. No se pueden colapsar en un único campo `verified`.

| Comprobación | Responsable y precedente | Qué demuestra | Qué NO demuestra |
| --- | --- | --- | --- |
| 1. JSON, tipado, identidad declarada, versión y hash | Adaptador externo F6.2 | Coherencia de una entrada con su ámbito esperado | Empresa y fuente auténticas |
| 2. Identidad del solicitante y empresa | Servicio IdP externo; principio ya cerrado F3.5 para lectura de parámetros | Solo con un IdP real: sesión corporativa y su alcance | Validez de facturas o permiso de compra |
| 3. Documento, contenido y fuente | Custodia/documentación externa; EIOS preserva bytes y localizadores en otros contratos | Con evidencia auténtica independiente: relación y validez documental | Autoridad humana ni suficiencia financiera |
| 4. Revisor, permiso y vigencia | Directorio empresarial externo; gobierno de permisos F3.5/F5.8 en sus propios ámbitos | Solo con credenciales y permisos empresariales reales: acción permitida | Autoridad de decidir comprar |
| 5. Admisión QTG y decisión | Contratos canónicos `operational_intake` y `operational_admission`, QTG/O1 | Comprobación estructural y evaluación bajo contratos especializados | No se activa por superar 1–4 |

**F6.3 no reemplaza F3.5**, que ya define puertos IdP/permiso/raíz para consulta de parámetros. Tampoco reemplaza `eios.core.operational_admission`, cuya admisibilidad es **estructural** y no autentica emisores. Ningún producto de F6.3 se interpreta como `PRESENTED_OPERATIONAL`.

## 2. MATERIALIZAR — DISTRIBUCIÓN EXTERNA, SIN NUEVO MOTOR

`tests/fixtures/f6_3_documentary_boundary_consumer/` contiene el consumidor de ejemplo **`eios-evidence-boundary-example==0.1.0`** y su `pyproject.toml` propio. Depende exactamente de `eios-company-adapter-example==0.1.0` (F6.2), cuatro módulos neutrales `==0.1.0` y Pydantic. **No incorpora ningún módulo `eios/` en su wheel** y no importa el núcleo canónico directamente.

El contrato de `review_synthetic_boundary` exige:

- **`PreparedExternalCase` F6.2:** identidad del proyecto y empresa, snapshot, origen, hash del JSON de entrada y objeto tipado `SyntheticEquipmentRecord`. Siempre `UNVERIFIED_ADAPTER_RESPONSIBILITY`.
- **`ReviewRequest` del host:** referencia opaca de sesión, expectativas explícitas de empresa/proyecto/fuente/snapshot, hash del JSON, referencia del documento, hash documental fijado por el host y fecha con zona horaria. **No contiene un booleano libre para declarar confianza**.
- **Tres proveedores independientes:** `resolve_identity`, `load_document`, `resolve_permission`. Responden con registros separados y tipados (`IdentityRecord`, `DocumentRecord`, `PermissionRecord`) y se consultan **dos veces**.
- **Comprobación de integridad:** SHA-256 de los bytes documentales comparado tanto con el registro como con la expectativa del host, límite de 64 KiB y correspondencia exacta de empresa, fuente, snapshot y referencia.
- **Permiso específico de ejemplo:** `SYNTHETIC_DOCUMENTARY_SCOPE_REVIEW`; rechazar permiso para comprar, operar o editar catálogo. Exigir identidad del revisor, permiso sobre el mismo documento, vigencia y comprobación de cambio durante la lectura.

Si los tres proveedores de prueba coinciden, se emite exclusivamente `ReviewReceipt.status=SYNTHETIC_BOUNDARY_CHECKS_PASSED`. Los campos de autenticación y permisos **reales** permanecen `False`, `production_authorized=False`, `decision_authority=False`, `operational_path=FORBIDDEN`. Nunca se invoca QTG, O1, PRICE, TCO, decisión ni admisión operacional.

## 3. AUDITAR → DEPURAR → AUDITAR 2

`tests/test_f6_3_external_documentary_boundary.py` verifica las dos empresas sintéticas y ataques sobre:

- Ausencia de cualquiera de los tres proveedores.
- Empresa, proyecto, sesión, fuente, snapshot o documento ajenos.
- JSON técnicamente válido cuyo `expected_source_sha256` no coincide con F6.2.
- Documento alterado, SHA-256 no concordante o expectativa de hash documental cambiada.
- Identidad no vigente, permiso vencido, revisor distinto, permiso inadecuado y referencia de autorización vacía.
- Cambio/revocación entre primera y segunda lectura de identidad, documento o permiso.
- Intentos de pasar etiquetas `PRESENTED_OPERATIONAL`, permisos de compra o campos `real_company_authenticated=true`.
- Cualquier promoción de `PreparedExternalCase` a `production_authorized=true` o una ruta distinta de `FORBIDDEN`.

`tools/verify_f6_3_documentary_boundary.py` usa el kit neutral **específico de la plataforma**, construye los wheels externos F6.2 y F6.3 desde sus fuentes, audita módulos/dependencias/hashes, instala en un entorno nuevo **offline** mediante `--no-index --require-hashes`, verifica bytes importados y ejecuta dos veces `python -I -m eios_evidence_boundary_example.demo` desde carpetas externas al checkout. Los resultados de ambos recorridos deben ser idénticos.

La CI existente de Ubuntu/SQL y de Windows/Python 3.12 ejecuta F6.3 **después de F6.2** y sin quitar ningún control previo.

## 4. FALTA DE AUTENTICACIÓN REAL — LÍMITE EXPLÍCITO

Los tres proveedores que usa el ejemplo son **TEST DOUBLES en memoria**. Los modelos permiten comprobar que la respuesta pertenece al ámbito indicado, pero **no prueban** que la empresa, el revisor, el canal, la fecha ni los documentos sean auténticos. Un adversario que controle todos los proveedores puede devolver una historia falsa y coherente; el doble chequeo no sustituye firma criptográfica, proveedor de identidad confiable, revocación posterior ni transacción distribuida.

La huella del documento no acredita quién lo firmó: el hash esperado debe llegar por un canal externo verdaderamente confiable para poder atribuirle valor de contraste. Aquí también es sintético.

No se entregan ni almacenan documentos empresariales reales, credenciales, certificados, claves, tokens, datos personales identificables ni permisos productivos. No se afirma cumplimiento legal ni se concede permiso de adquisición.

## 5. CIERRE Y CONTINUIDAD

**Cerrar F6.3** exclusivamente al obtener:
1. Tests adversarios y suite Python/SQL existentes satisfactorios.
2. Verificador externo F6.3 en Linux y Windows, sobre el SHA de PR exacto.
3. Diff limitado a fixtures, tests, verificadores, CI y documentación, sin cambiar código canónico.
4. Merge y CI postintegración satisfactoria sobre el HEAD exacto de `main`.

**Siguiente frente propuesto F6.4 — Preparación de un adaptador documental con proveedor real:** seleccionar junto a una empresa colaboradora IdP, canal seguro de entrega/custodia, responsables, permisos, controles de autenticidad y procedimiento de revocación; solo entonces diseñar prueba observacional supervisada. Sin empresa ni autoridades genuinas, F6.4 puede diseñarse pero no certificar una admisión empresarial real.
