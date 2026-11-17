# EIOS — F6.5 · INCORPORACIÓN CONTROLADA DE PROVEEDORES EXTERNOS

**Fecha:** 17/11/2026. **Baseline:** `main @ 0af0e6e679580d856fda71dc93ade831de1ea13a` (F6.4 cerrada; CI posterior #44085220860 SUCCESS en Linux/SQL y Windows).  
**Estado:** candidato; cierre condicionado a PR, CI completa, auditoría de diff y CI postintegración en commit exacto de `main`.

## 1. DISEÑAR — BRECHA Y REUTILIZACIÓN

- F3.5: frontera de identidad empresarial, permisos de lectura y clave de gobierno para parámetros. **No se duplica su IdP**.
- F6.2: entrada tipada, ámbito y hash de un expediente *sintético*.
- F6.3: puertos independientes `resolve_identity`, `load_document` y `resolve_permission`, comprobados dos veces, siempre sintéticos.
- F6.4: proveedor documental local de escritura única y lectura verificada, **no** un gestor corporativo auténtico.

**Brecha F6.5:** F6.3 aceptaba puertos proporcionados por un host sin una configuración versionada y fijada de *qué proveedor debía atender cada rol y cada empresa*. F6.5 crea **solo en el consumidor externo** la puerta de incorporación que exige un registro de proveedores completo, con versión exacta, empresa/proyecto, fechas de vigencia y capacidad de suspensión.

No se añade una API de autorización al Motor ni se crea un segundo catálogo F5.7/F5.8. El registro de esta unidad gobierna exclusivamente **puertos de integración del host**, no capacidades del núcleo.

## 2. CONTRATO EXTERNO

Distribución independiente: `tests/fixtures/f6_5_onboarding_consumer/`, wheel `eios-onboarding-example==0.1.0`. Solo importa F6.2/F6.3/F6.4; depende de sus versiones exactas y de los cuatro paquetes neutrales.

Se definen objetos inmutables:

| Contrato | Campos esenciales | Invariante |
| --- | --- | --- |
| `ProviderRegistration` | `role`, `provider_id`, `company_id`, `project_id`, `integration_ref`, `api_version`, `valid_from`, `valid_to`, `enabled` | Solo sintético, versión exacta `1.0.0`, vigencia con zona horaria |
| `OnboardingSnapshot` | Proyecto, empresa, revisión entera positiva, tres registros, finalidad `SYNTHETIC_TEST_ONLY` | Tres roles distintos y ordenados, cada uno con ID de proveedor diferente y mismo ámbito empresarial |
| `PinnedOnboarding` | Proyecto, empresa, revisión esperada, SHA-256 esperado | El valor esperado lo proporciona un **host externo confiable**, no el documento ni el propio registro |
| `ProviderEndpoint` | Rol, ID de proveedor, API exacta, objeto del cliente | Tiene el método exigido por F6.3 y el ID coincide con el registro |
| `OnboardingReceipt` | Revisión y hash, roles atendidos y recibo F6.3 | Siempre `real_provider_connected=False`, `production_authorized=False`, `decision_authority=False` |

Los tres roles obligatorios, sin *fallback*, son:
1. `IDENTITY` → `resolve_identity`.
2. `DOCUMENT` → `load_document` del proveedor F6.4.
3. `REVIEW_PERMISSION` → `resolve_permission`.

No se admiten un rol ausente, roles duplicados, IDs de proveedor compartidos, empresas mezcladas, una API inferida por SemVer, un servicio sin su método, registro deshabilitado, vencido o con versión cambiada sin un nuevo `PinnedOnboarding` aprobado fuera de EIOS.

## 3. SECUENCIA Y DETECCIÓN DE CAMBIOS

`review_with_onboarded_providers(...)`:

1. Comprueba tipos, proyecto/empresa, roles exactos, métodos y referencia de fuente del registro.
2. Consulta `registry_source.get_provider_snapshot(project_id, company_id, reviewed_at)` y compara **toda** su configuración con el digest fijado, revisión y ámbito; exige que cada proveedor esté habilitado y vigente en el instante de consulta.
3. Envuelve las llamadas de F6.3 sin sustituir sus validadores: **antes y después** de cada consulta a identidad, documento o permisos vuelve a leer el registro.
4. F6.3 ejecuta su propia doble comprobación de los tres proveedores, integridad del documento y permiso específico. El registro se consulta una vez más **después del recibo**.
5. Únicamente si persiste la misma configuración emite `SYNTHETIC_PROVIDER_ONBOARDING_READY`. Esto significa «preparado para un ensayo sintético», no «empresa autenticada» ni «instalación productiva».

F6.3 sigue rechazando permiso `AUTHORIZE_PURCHASE`, prueba documental falsa o empresa equivocada. El registro, aunque esté «completo», **no puede convertir los test doubles en proveedores verdaderos**.

Una revocación o cambio de proveedor detectados en cualquiera de esas comprobaciones bloquea el resultado. La doble lectura no garantiza transacciones distribuidas ni revocaciones posteriores a la última observación.

## 4. PRUEBAS ADVERSARIAS Y CERTIFICACIÓN FÍSICA

`tests/test_f6_5_provider_onboarding.py`: dos empresas sintéticas; tres IDs separados, ausencia de rol o proveedor de registro; endpoint ajeno o con API incompatible; revisión obsoleta; cambio de huella; proveedor deshabilitado; vencimiento de registro; revocación durante la lectura; empresas cruzadas; orden, identidad y duplicados; falsas declaraciones de autenticidad real; intento de permiso de compra. Todos los casos negativos fallan cerrados.

`tests/fixtures/f6_5_onboarding_consumer/src/eios_onboarding_example/demo.py`: enlaza dos entradas F6.2, documentos de custodia local F6.4 y revisiones F6.3 con registros de tres proveedores distintos por empresa. En ningún caso genera documentación verdadera o autorización humana.

`tools/verify_f6_5_provider_onboarding.py`: extrae y verifica el ZIP neutral F5.10/F6.1, construye **cuatro wheels externos F6.2–F6.5**, compara sus módulos con el código fuente, audita metadatos y dependencias, instala en un entorno virtual ajeno al checkout con `--no-index --require-hashes`, verifica bytes importados y ejecuta dos veces el onboarding sin red. Requiere resultados idénticos, dos empresas y dos registros documentales separados; no acepta ningún campo de autorización productiva.

CI añade un paso F6.5 a los trabajos Linux/SQL y Windows 3.12 existentes, **sin eliminar controles**.

## 5. EXIGENCIAS PARA UN PROVEEDOR EMPRESARIAL VERIFICABLE — FUERA DEL ENSAYO

Una incorporación auténtica requerirá, como mínimo, una empresa y un responsable que aprueben el ámbito y los contratos, más tres sistemas independientes de prueba:

- **Identidad:** IdP corporativo (por ejemplo OIDC con emisor, audiencia, claves públicas y revocación verificables), proceso de alta/baja de usuarios y vinculación legal o contractual de la empresa.
- **Documentación:** canal de entrega y repositorio con control de acceso, conservación y auditoría, referencias y hashes obtenidos de una autoridad/canal realmente independiente; firmas o pruebas de origen según documento.
- **Permisos:** fuente empresarial de autorizaciones separada del documento, con roles explícitos, vigencia, revocación, responsables, segregación de funciones y registro auditable.

También exige reloj y almacenamiento confiables, protección de secretos, transporte cifrado, controles de datos personales, política de retención, recuperación y evidencias de auditoría. **Nada de eso queda acreditado por una prueba técnica con test doubles**. Aquí no se realizan conexiones a internet, se almacenan credenciales ni se recaban datos reales.

El hash del registro es una comprobación de consistencia, **no una firma criptográfica ni origen de confianza**. Quien controle la fuente y la huella esperada puede falsear ambos. `provider_id` e `integration_ref` son etiquetas declaradas; no prueban identidad legal del proveedor.

## 6. CIERRE CONTROLADO Y CONTINUIDAD

Método: **DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**.

Para cerrar F6.5: suite Python+SQL preexistente y pruebas adversarias, certificación física offline en Linux y Windows, diff limitado a tests/fixtures/verificador/CI/documento, merge explícito y CI postmerge sobre `main` exacto.

**Siguiente unidad propuesta F6.6:** procedimiento piloto de conexión supervisada (*read-only*) con una empresa colaboradora, inventario de evidencias mínimas, prueba de revocación y criterios de aceptación/rechazo. Sin empresa colaboradora, se puede crear checklist y probar dobles, pero **no** afirmar una autenticación real ni habilitar `PRESENTED_OPERATIONAL`, QTG/O1 o decisiones con autoridad.
