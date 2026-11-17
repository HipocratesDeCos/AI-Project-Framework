# EIOS — F6.4 · CONEXIÓN EXTERNA Y CUSTODIA DOCUMENTAL DE ESCRITURA ÚNICA

**Fecha:** 17/11/2026. **Baseline auditada:** `main @ 15eebc69a2d81b768b248bf1521e09534c635693`, F6.3 cerrada, CI postmerge #44078784648 SUCCESS Linux/SQL y Windows.
**Estado:** CANDIDATO — hasta pasar CI de PR, revisar diff, fusionar y superar CI de `main` en commit exacto.

## 1. DISEÑAR — BRECHA REAL Y REUTILIZACIÓN

F3.5 ya define proveedores externos de IdP/permisos/clave para *lectura de parámetros*. F6.2 prepara entradas empresariales tipadas. F6.3 conecta tres interfaces separadas: identidad de sesión, documento y permiso de revisión, con doble consulta y control de cambios. Los contratos `eios.core.operational_intake` y `operational_admission` no autentican emisores y no se modifican.

**Brecha real**: F6.3 recibía bytes del proveedor documental simulado, pero no probaba su almacenamiento, su referencia inmutable, recuperación posterior, límites por empresa o resistencia a alteraciones. F6.4 añade **un único proveedor de custodia** fuera del núcleo, sin segundo sistema de identidad ni duplicar F6.3.

Paquete externo y separado: `tests/fixtures/f6_4_custody_consumer/`, distribución `eios-custody-example==0.1.0`, módulos `custody.py` y `demo.py`. Depende de las ruedas exactas y auditadas F6.2/F6.3 y cuatro paquetes neutrales; no contiene `eios/` ni importa módulos del núcleo directamente.

## 2. MATERIALIZAR — CONTRATO DE CUSTODIA LOCAL

- `DocumentBinding` **fijado por el host**: `project_id`, `company_id`, `source_id`, `data_snapshot_id`, `document_ref`, `expected_document_sha256`, `purpose=SYNTHETIC_TEST_ONLY`. Nunca se infiere la confianza a partir del JSON almacenado.
- `SyntheticCustodyVault` requiere una carpeta **existente**, explícitamente suministrada y sin vínculo simbólico en la raíz. El host debe ser dueño de su control de acceso y protección. No se aceptan rutas arbitrarias procedentes de documentos. El nombre de archivo es SHA-256 de los cinco identificadores de ámbito, no del documento; cambiar la huella esperada **no crea una nueva versión** en el mismo ámbito.
- `store_once`: un archivo JSON con metadatos, datos base64 y digest, escrito con `O_CREAT|O_EXCL` y sincronización del descriptor; segundo intento (incluso idéntico) rechazado. Los bytes de entrada se comparan con el hash esperado **antes de escribir**. Límite de documento: 64 KiB; registro: 96 KiB.
- `load_verified`: lectura acotada, rechazo de enlace simbólico y archivo no regular/múltiples enlaces cuando los reporta el sistema, claves JSON duplicadas o extra, versión y procedencia incorrectas, campos de otra empresa y discrepancias entre contenido, metadatos y hash fijado externamente. La recuperación devuelve `DocumentRecord` de F6.3 con `assurance=SYNTHETIC_TEST_DOUBLE`.
- `VaultDocumentProvider`: implementa **la misma firma** `load_document(project_id, company_id, document_ref, reviewed_at)` que ya exige F6.3; rechaza petición ajena y revalida el documento en **cada** lectura. El IdP y los permisos siguen en sus propios proveedores del host.

Cadena demostrada, sin alterar `eios/`:

`Entrada sintética F6.2` → `ReviewRequest F6.3` + `DocumentBinding del host` → `custodia local F6.4` → `VaultDocumentProvider` + `IdP/permiso sintéticos separados` → `review_synthetic_boundary F6.3` → **recibo técnico sintético, sin permiso operacional**.

## 3. AUDITAR Y DEPURAR

`tests/test_f6_4_custody_provider.py` comprueba:
1. Dos empresas sintéticas con recuperaciones y recibos independientes.
2. Escritura única y rechazo de sustitución del documento por otro hash.
3. Comparación de huella fijada por el host antes de escribir y en cada lectura.
4. Rechazo de intercambio de proyecto, empresa, fuente, snapshot y referencia.
5. Archivo alterado, truncado, excedido, JSON con claves duplicadas o inesperadas, `assurance` falsa, metadatos modificados o bytes no concordantes.
6. Raíz ausente/enlace simbólico, archivo enlace simbólico (si el runner lo permite), identidades con segmentos de ruta `../` o separadores de carpetas.
7. Rechazo de un permiso de revisión reemplazado por `AUTHORIZE_PURCHASE`.
8. La existencia de documentos conservados **no cambia** `real_document_authenticated=false`, `real_human_authorized=false`, `decision_authority=false`, `production_authorized=false`, `operational_path=FORBIDDEN`.

`tools/verify_f6_4_custody_portability.py` construye tres wheels independientes F6.2/F6.3/F6.4, audita sus módulos y dependencias exactas, verifica SHA-256 de fuentes y paquetes, usa el ZIP existente F5.10/F6.1 y crea una instalación nueva sin red mediante `pip --no-index --require-hashes`. Ejecuta la demo dos veces fuera del checkout y comprueba mismo resultado, empresas separadas, dos ficheros inmutables y ninguna autoridad.

En CI: se añade una certificación F6.4 **después de F6.3** tanto en el trabajo Linux/SQL como en Windows/Python 3.12. Se conservan todas las pruebas anteriores.

## 4. LÍMITES DE CONFIANZA, SEGURIDAD Y CAPACIDAD

**Cierre técnico de ejemplo ≠ custodia empresarial certificada.** Esta implementación no incluye ni presupone:
- IdP real, empresa jurídica acreditada, sesiones OIDC reales, control de acceso del sistema operativo o permisos humanos verificados.
- Autenticidad del emisor, firma electrónica, sello de tiempo, respaldo independiente ni procedencia documental legal.
- Claves gestionadas, cifrado en reposo, KMS, almacenamiento remoto, WORM certificado, archivos de gran tamaño, PDF/Excel empresarial, retención, auditoría externa, borrado legal o políticas RGPD.
- Protección frente a un administrador que puede alterar archivos, sustituir todo el directorio, modificar la huella confiable, manipular el reloj, cambiar permisos, o suplantar servicios IdP/revisor.

**Detalles técnicos:** `O_EXCL` impide reemplazos cooperativos de un mismo archivo en el instante de creación, pero no convierte el sistema local en WORM regulado. La protección contra cambios de symlink entre comprobación y apertura depende de las garantías del sistema operativo; se utiliza `O_NOFOLLOW` cuando está disponible. La escritura simple sin journal puede dejar restos tras un fallo de energía; un host de producción necesita almacenamiento transaccional, recuperación, registro y control de acceso propios. El hash identifica bytes, **no autor**; la confiabilidad del digest esperado depende de una fuente independiente y segura.

Una integración empresarial real necesitará además un perfil concreto de proveedor IdP, fuente de custodia y servicio de autorizaciones, sus contratos/credenciales con consentimiento, evaluación de seguridad, políticas de conservación y un expediente autorizado. Nada de ello se simula como "real" aquí.

## 5. CERRAR → CI Y CONTINUIDAD

F6.4 solo se cierra cuando pasen:
- Tests Python/SQL previos y nuevos en Linux.
- Instalaciones offline y pruebas F6.4 en Windows.
- Auditoría del diff: archivos limitados a distribución externa, tests, verificador, CI y documentación; ningún módulo canónico modificado.
- Merge con SHA de PR y CI postmerge satisfactoria en el SHA final de `main`.

**Siguiente frente F6.5 recomendado — contrato del onboarding de un proveedor verificable:** seleccionar un sistema corporativo real de identidad y custodia, exigir su fuente de confianza, permisos y revocación y preparar una prueba supervisada bajo autorización explícita, sin activar QTG ni operación real por inferencia. En ausencia de esa empresa se puede diseñar y probar puertos, nunca certificar un piloto real.
