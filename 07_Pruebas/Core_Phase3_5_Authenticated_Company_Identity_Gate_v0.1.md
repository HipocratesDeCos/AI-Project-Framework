# EIOS — F3.5 · FRONTERA DE IDENTIDAD EMPRESARIAL Y PERMISOS DE LECTURA

**Fecha:** 2026-11-16  
**Base examinada:** `main @ 92e2feb624855d417753850a567ea536cd1258a9` (F3.4 integrada con CI).  
**Unidad:** exigir identidad empresarial y permiso del emisor corroborados por proveedores externos ANTES de la lectura de parámetros. No presupone una empresa real configurada.

## DISEÑAR · Riesgo encontrado

F2.4 valida coherencia de las versiones y evidencias; F3.3 valida firmas Ed25519; F3.4 valida gobierno de claves y revocación. **Ninguna** de esas pruebas autentica por sí misma que el solicitante pertenece a una empresa, ni que tenga permiso para leer parámetros, ni que su `expected_company_id` no haya sido suministrado arbitrariamente.

El repositorio **no dispone de un IdP corporativo conectado, una empresa real admitida, un directorio verificable de autorizaciones ni una fuente externa de claves públicas de gobierno**. Una cadena `company_id`, una fila SQLite, una firma válida o un booleano `authenticated=True` no serían suficientes. Esta unidad NO puede sustituir la identidad real de una empresa.

## AUDITAR · Una única ruta autorizable para lectura, sin saltarse F2.4

Módulo `eios/parameters/company_identity_gate.py`.

El punto de entrada `read_authenticated_company_parameter_selection` exige tres puertos independientes del expediente:

1. `AuthenticatedCompanyIdentitySource.resolve_authenticated_identity(session_ref, verification_at)` recibe una referencia opaca de sesión. Un **host confiable** debe verificar en su IdP el acceso a la sesión y devolver `AuthenticatedCompanyIdentity` con empresa, sujeto, proveedor, referencia de identidad y vigencia. El usuario no puede crear una identidad mediante un `company_id` editable.
2. `CompanyIssuerAuthorizationSource.resolve_parameter_read_grant(company_id, subject_id, verification_at)` debe consultar permisos del **host**, separados de la sesión y de la carga del documento. `CompanyIssuerReadGrant` limita el sujeto, empresa, permiso exacto `PARAMETER_VERSION_READ`, emisor, clave y vigencia. No concede permiso para escritura, aprobación de compras o acceso operativo.
3. `TrustedCompanyGovernanceKeySource.get_trusted_governance_key(company_id, verification_at)` entrega una clave de gobierno `GovernanceVerificationKey` previamente fijada fuera del documento. No acepta una clave autorreferida que venga en el manifiesto.

El consumidor proporciona además los puertos **ya existentes** de F3.3/F3.4: repositorio de versiones firmadas, historial de claves firmado y checkpoint independiente de revisión/huella. No se crea ninguna tabla, clase de autenticación alternativa, almacén ni permiso persistido dentro de EIOS.

### Secuencia de seguridad

```text
Sesión opaca → IdP del host (identidad, empresa, vigencia)
                        ↓
              Permiso del host (sujeto/empresa/issuer/key)
                        ↓
              Clave raíz confiable del host
                        ↓
       F3.4: historial firmado + checkpoint + revocación
                        ↓
       F3.3: firma del manifiesto por clave admitida
                        ↓
       F2.4: Centre + evidencia por parámetro + versión
                        ↓
        Relectura de identidad, permiso y clave raíz
                        ↓
        Coincidencia total → recibo de consulta read-only
```

La solicitud puede incluir `requested_company_id`, pero **solo como expectativa que debe coincidir con la empresa devuelta por el IdP**. No determina el ámbito de autorización. `issuer_id` y `key_id` proceden del permiso corroborado externamente, no de una selección del usuario.

Antes de publicar el resultado se vuelven a consultar identidad, permiso y clave raíz. Cualquier discrepancia se rechaza con `COMPANY_AUTHORIZATION_CHANGED`. F3.4 revalida independientemente el historial firmado y su checkpoint antes y después de cada manifiesto; F2.4 repite la lectura alrededor del Centro.

## DEPURAR · Riesgos que se rechazan

`tests/test_company_identity_gate.py` utiliza **exclusivamente proveedores sintéticos en memoria**, claves efímeras generadas en las suites F3.3/F3.4 y sus registros ya existentes.

Se cubren empresa/identidad ajenas, sesión ausente, permisos ausentes, sujeto distinto, permiso de escritura presentado como lectura, emisor o clave ajenos, raíz de gobierno de otra empresa, proveedor omitido, vencimiento, reloj sin zona horaria, cambio de identidad/permiso/raíz durante la selección, revocación del emisor, falta de evidencia documental, divergencia de configuración, aislamiento de dos empresas y conservación de `FORBIDDEN`.

## AUDITAR 2 · Límites de confianza irrenunciables

La validez del resultado depende de que los **tres proveedores externos estén realmente autenticados y correctamente configurados**. Esta unidad no valida directamente un token OIDC/JWT, un certificado mercantil, una relación laboral ni la autoridad jurídica del responsable: dichos trabajos pertenecen al IdP y al servicio empresarial de permisos. Un proveedor falso puede devolver datos falsos; las estructuras tipadas NO le otorgan confianza por sí mismas.

La doble lectura detecta cambios observables; **no garantiza** transacciones distribuidas ni revocaciones que ocurran después de la última comprobación. La integridad del checkpoint de F3.4 sigue dependiendo de un servicio externo monotónico, distinto del historial.

Tampoco se convierte una referencia de documento `identity_ref` o `grant_ref` en evidencia de compra. Ni una sesión autorizada para leer parámetros ni una firma válida habilitan decisiones humanas o autorizaciones de compra.

Se conserva:
- `decision_authority=False`
- `operational_path=FORBIDDEN`
- evidencia C0 y consultas canónicas F2.4, sin atajos.
- aplicación local, reglas, SQL y cálculos sin modificaciones.

## CERRAR → MATERIALIZAR → CI

Se exige CI completa Python y SQL en HEAD de PR, auditoría de diff y reconciliación postintegración.

**Cierre F3.5:** únicamente frontera de integración lista para recibir IdP, permisos y raíz verdaderos; no puede declararse autenticación corporativa real con proveedores de prueba.

**Siguiente hito fuera de F3.5:** decisión concreta sobre un IdP empresarial, vinculación auténtica `empresa ↔ usuario`, fuente verificable de permisos y claves, repositorio firmado corporativo y expediente documental admitido. Hasta entonces, la fase 3 global y la vía operacional permanecen abiertas/bloqueadas.
