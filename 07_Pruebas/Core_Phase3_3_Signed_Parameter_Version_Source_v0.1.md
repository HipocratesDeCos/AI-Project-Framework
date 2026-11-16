# EIOS — F3.3 · ADAPTADOR DE VERSIONES CON FIRMA DIGITAL VERIFICADA

**Fecha:** 2026-11-16  
**Base verificada:** `main @ 849e6400a8a6e7bac6a3d93f6d7ed9fac4882080` (F3.2).  
**Alcance:** autenticación criptográfica **relativa a una clave pública de confianza suministrada externamente**. No se ha recibido ninguna clave/identidad real ni un emisor empresarial real: esta unidad no constituye admisión operacional.

## DISEÑAR · Hallazgos y frontera

1. `Decision Versioning` guarda una **referencia** `parameters_version`, nunca un certificado de su contenido.
2. F2.4 `ParameterVersionSource` ya comprueba que el manifiesto recibido represente **toda** la selección y coincida con las configuraciones canónicas que lee `ParameterConfigurationCenter`.
3. F3.2 reutiliza el histórico SQLite **sintético y editable**. Un SHA-256 de esa base no puede verificar la identidad del emisor.
4. El repositorio **no** dispone de claves públicas empresariales previamente aprobadas, autoridad corporativa, servicio de gestión/rotación de claves, revocación, autorización de emisores o almacén documental firmado.
5. Por tanto, un componente que se declare a sí mismo `trusted` a partir de la carga del cliente sería un error de seguridad. Se requiere **ancla de confianza fuera de banda**.

## AUDITAR · Decisión técnica

Se implementa un adaptador opcional `Ed25519VerifiedParameterVersionSource` sobre el **mismo** puerto de F2.4, sin otra jerarquía de versiones ni nuevas tablas.

- El proveedor de registros firmado se inyecta mediante el puerto `SignedVersionRecordRepository.get_signed_record(company_id, parameters_version, effective_at)`.
- Una configuración de confianza del **host** suministra un objeto `TrustedIssuerPublicKey`: `company_id`, `issuer_id`, `key_id`, clave pública Ed25519 de 32 bytes y vigencia. La clave **no** debe extraerse del documento recibido ni de una petición editable del usuario.
- La entrada contiene el contenido JSON exacto firmado y su firma separada. **No** se guardan ni se generan claves privadas en la aplicación.
- El adaptador verifica criptográficamente la firma **antes de interpretar el JSON** mediante `cryptography` y la clave pública configurada.
- Rechaza objetos malformados, JSON no canónico/duplicado, campos desconocidos, nombres de emisor/clave/empresa ajenos, versión distinta, fecha distinta, parámetros no canónicos, huella no válida, emisor fuera del periodo de la clave, creación futura y expiración con respecto a un reloj de verificación externo.
- El manifiesto devuelto es el `ParameterVersionManifest` **ya existente**, no una nueva versión. F2.4 sigue ejecutando su doble lectura y la comparación de la selección vigente, incluido el requisito de evidencia documental completa.
- No se modifica `eios/parameters/__init__.py`: importación directa opt-in desde `eios.parameters.signed_version_source`, sin riesgo de ciclo y sin cargar criptografía al iniciar la app local.
- `cryptography>=43,<50` figura en el extra opcional `security` y en el extra `test`; no se convierte en dependencia obligatoria para la aplicación local no autenticada.

## DEPURAR · Pruebas negativas obligatorias

`tests/test_signed_parameter_version_source.py` genera claves efímeras **solo en memoria durante los tests**, sin distribuir certificados falsos:

- Integración positiva con el contrato F2.4 y coincidencia de contenido íntegro.
- Sin registro o sin ancla de confianza → fallo cerrado.
- Firma alterada, clave pública distinta, empresa ajena, `issuer_id`, `key_id`, versión o corte discordantes.
- Firma válida con documento futuro/caducado, clave fuera de su vigencia, estructura inválida, claves JSON duplicadas, campos extra o valores no canónicos.
- Firma correcta sobre un digest no coincidente con el Centro → `VERSION_CONTENT_MISMATCH`.
- Dos empresas con confianza segregada; evidencia C0 faltante, manifiesto cambiante entre dos lecturas y selección incompleta.
- Prohibición de autoridad operacional, escritura de versiones y sustitución de reglas existentes.

## LÍMITES QUE NO DEBEN OMITIRSE

**La verificación criptográfica solo prueba que el contenido corresponde a la clave pública aprobada externamente**. No prueba por sí sola quién controla esa clave, si esa persona representa una empresa, si el emisor estaba autorizado para aprobar la política, si la clave ha sido revocada posteriormente, ni si la documentación comercial es cierta.

Pendientes reales para un piloto empresarial:

1. Obtener una fuente de claves corporativas **realmente verificada**, aprobada de forma independiente y segregada por empresa; definir enrolamiento, rotación, revocación y roles.
2. Conectar un proveedor de artefactos históricos firmados que ya exista bajo responsabilidad empresarial; no inventar versiones ni derivarlas del valor vigente.
3. Autenticar el `expected_company_id` del host, no confiar en el payload de una operación.
4. Validar documentos y evidencia C0 de forma independiente. Una firma válida sobre un manifiesto de parámetros no autoriza una compra.
5. Verificar el comportamiento de lectura y trazabilidad al utilizar el entorno real autorizado.

Hasta completar esos puntos, `decision_authority=False` y `operational_path=FORBIDDEN`. Un resultado positivo en tests sintéticos **no** significa que esté configurada una empresa real.

## CIERRE

Aplicar: **DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**.

Integración solo con CI completa Python + SQL Server **SUCCESS** en el HEAD, revisión limitada de diff, reconciliación post-merge y reporte explícito de que la autenticación corporativa real continúa pendiente.
