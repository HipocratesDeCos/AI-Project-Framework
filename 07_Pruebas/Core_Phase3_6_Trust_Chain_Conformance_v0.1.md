# EIOS — F3.6 · CONFORMIDAD DE LA CADENA DE CONFIANZA (SIN DOCUMENTOS EMPRESARIALES)

**Fecha:** 2026-11-16. **Baseline:** `main @ 58ce837e67f78fdd65f906b8ebdc1b812c5eb46f` (F3.5 integrada y validada).

## OBJETIVO Y ALCANCE

Mientras no se dispone de documentos financieros reales ni de un proveedor de identidad corporativa, probar **de extremo a extremo** que los controles ya construidos no se eluden entre capas. Es un esfuerzo de estabilización: no se crea un nuevo motor, un nuevo permiso, una nueva versión, un simulador de empresa ni otra taxonomía de procedencia.

La base ya dispone de:
- **F2.4:** identificación de versión, selección de parámetros, comparación de fingerprint y evidencia por parámetro.
- **F3.3:** autenticidad de manifiestos Ed25519 frente a clave pública previamente confiable.
- **F3.4:** ciclo de vida firmado de la clave, comprobación independiente de revisión/huella y revocación.
- **F3.5:** sesión verificada externamente, empresa/usuario, permiso de lectura, clave raíz de gobierno y doble comprobación.
- **Case Provenance:** `SYNTHETIC_TEST`, `REFERENCE_OPERATIONAL_SIMULATION` y `PRESENTED_OPERATIONAL` mantienen sus restricciones; no se pueden convertir simples pruebas en autoridad operacional.

## DISEÑAR → AUDITAR

Se inspeccionaron los contratos en `eios/parameters/version_binding.py`, `signed_version_source.py`, `key_lifecycle.py`, `company_identity_gate.py` y `eios/core/case_provenance.py`. No se detectó motivo para duplicar la resolución de parámetros, alterar el Motor financiero, crear una segunda taxonomía o integrar una falsa empresa real.

**Estrategia de la unidad:** nueva batería adversarial que utiliza *sin modificarlos* los mismos módulos y fixtures existentes. Incluye cambios de estado durante las lecturas, que las pruebas de cada capa por separado pueden no cubrir en combinación.

## DEPURAR → AUDITAR 2

Archivo `tests/test_phase3_trust_chain_conformance.py`. Tests de integración que exigen rechazar:

- Reutilización de parámetros, evidencias o manifiestos de otra empresa.
- Clave raíz corporativa ajena y permiso de usuario no acreditado.
- Revocación de la clave **durante** la verificación de una firma ya válida.
- Revocación **entre** la primera y la segunda lectura de F2.4, tras consultar el Centro.
- Pérdida de identidad o permisos tras superar la comprobación criptográfica.
- Versión distinta sin documento firmado que la sustente.
- Evidencia C0 faltante o configuración modificada bajo la misma versión.
- Checkpoint independiente ausente o retroceso a historia anterior a la revocación.
- Cambio de clave de gobierno antes de devolver el resultado.
- Permiso vencido y ausencia de proveedor de confianza.
- Tentativas de confundir `approval_ref` o un resultado de lectura con autorización de compra.

Se conserva la prueba positiva de selección íntegra y el estado final **`decision_authority=False`, `operational_path=FORBIDDEN`**.

Solo se generan **claves sintéticas efímeras en memoria** mediante las fixtures de F3.3/F3.4. No hay datos empresariales reales, accesos externos, certificados de autoridad real o secretos comprometidos.

## CIERRE → MATERIALIZAR → CI

Cierre técnico condicionado a:
1. CI de Python completa sobre HEAD de PR, sin errores.
2. Controles SQL Server de C0, Decision Versioning y Centro de Parametrización, sin errores.
3. Auditoría de diff limitada a tests y documentación.
4. Merge controlado + CI postintegración sobre el commit exacto.

**Límite explícito:** estos tests no demuestran la autenticación de una empresa real ni autorizan operaciones reales. No sustituyen la validación financiera con las cuentas anuales cuando estén disponibles. Esta unidad mejora la confianza en los mecanismos del Motor mientras se tramitan esos documentos.
