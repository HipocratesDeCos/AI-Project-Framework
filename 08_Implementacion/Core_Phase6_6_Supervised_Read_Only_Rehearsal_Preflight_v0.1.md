# EIOS — F6.6 · PREPARACIÓN DE PILOTO SUPERVISADO, SOLO LECTURA

**Fecha:** 17/11/2026. **Base de trabajo:** `main @ 88d2532cd09b646893d58436054309330f21124a`, F6.5 cerrada por CI postmerge #44099634314.  
**Estado:** candidato, hasta validar PR + merge + CI postmerge en SHA exacto.

## 1. DISEÑAR — NO REPETIR LO YA CONSTRUIDO

**El objetivo de esta unidad es comprobar la preparación de un ENSAYO de integración empresarial**, no admitir material empresarial genuino mediante una lista de casillas. No se conecta a servicios reales, no se habilita una compra, una revisión documental auténtica ni una decisión.

Precedentes auditados, que **no se sustituyen ni duplican**:

- **F3.5** ya contiene las fronteras de identidad y autorización externa para la lectura de parámetros.
- **F6.2–F6.5** ya contienen el adaptador externo, validación estructural, custodia sintética y registro de tres proveedores con doble comprobación de vigencia y revocación. El resultado `SYNTHETIC_PROVIDER_ONBOARDING_READY` no es un permiso real.
- `08_Implementacion/First_Operational_Expedient_Admission_Checklist_v0.1.md` enumera el **expediente de Compras/Finanzas** y los requisitos para una eventual admisión OPERATIONAL.
- `08_Implementacion/Finance_Pilot_Supervised_Review_Procedure_v0.1.md` establece **actos humanos especializados de revisión financiera**. Una marca del checklist F6.6 no puede ejecutarlos, reemplazarlos o confirmarlos.
- `eios/core/operational_intake.py`, `operational_admission.py`, QTG/O1 y los contratos de autoridad conservan su frontera independiente. Ni el lector ni el resultado F6.6 los invocan.

**Decisión de arquitectura:** F6.6 reutiliza y amplía únicamente la distribución externa **`eios-onboarding-example==0.1.0` de F6.5**, añadiendo `pilot.py` y `pilot_demo.py`. No se fabrica otro motor, quinto wheel, esquema SQL, registro de autoridades ni API de producción.

## 2. LOS DOCE CONTROLES DE PREPARACIÓN

| ID | Qué debe documentar el ensayo sintético | Qué se exigiría adicionalmente para la empresa real |
| --- | --- | --- |
| `COMPANY_AND_PROJECT_MANDATE` | Empresa ficticia y proyecto declarados, alcance delimitado | Acreditación y autorización de la empresa, firmante y facultades |
| `HOST_IDENTITY_SCOPE` | Sesión y empresa coherentes según el doble F6.3 | IdP corporativo auténtico, relación empresa ↔ usuario corroborada |
| `PINNED_THREE_PROVIDER_REGISTRY` | Tres roles F6.5 con huella/revisión fijadas | Registro y claves de confianza fuera de los datos del expediente |
| `READ_ONLY_BOUNDARY` | Ninguna llamada de escritura o autoridad a EIOS | Credenciales y acceso de solo lectura limitados técnicamente |
| `DOCUMENT_SOURCE_AND_DIGEST` | Documento de prueba conservado, huella y ámbito coherentes | Fuente, identidad del emisor, canal y origen documental verificables |
| `CUSTODY_AND_RETENTION_POLICY` | Custodia local F6.4 y límites declarados | Repositorio seguro, retención, borrado y cumplimiento aplicable |
| `REVIEWER_PERMISSION_SCOPE` | Permiso de revisor sintético específico | Mandato de persona real, periodo, funciones y revocación |
| `TRACE_AND_TRUSTED_TIME` | Instante consciente de zona y rastros sintéticos | Fuente horaria y auditoría inalterables y externas |
| `ACCESS_REVOCATION_REHEARSAL` | Simular revocación y probar rechazo | Baja/revocación aplicable al IdP y a cada permiso real |
| `STOP_AND_INCIDENT_PLAN` | Procedimiento de detener, bloquear, registrar fallo | Responsable y canal de incidentes/rollback de la empresa |
| `PRIVACY_AND_MINIMUM_DATA` | Exclusión de datos personales y secretos reales | Bases jurídicas, minimización, acceso, conservación y acuerdos |
| `OPERATIONAL_ROUTE_FORBIDDEN` | `FORBIDDEN`, sin decisiones, QTG ni escrituras | Cualquier desbloqueo real exige otra autorización y otra vía |

**Naturaleza de la prueba:** los doce requisitos son un inventario de preparación para el *ensayo sintético*, no una nueva lista de requisitos del expediente de compras ni un sustituto de los contratos financieros canónicos.

## 3. CONTRATO IMPLEMENTADO

- `RehearsalChecklistItem(requirement_id, status, support_ref)` solo admite `SYNTHETIC_REHEARSED`, `MISSING` o `UNVERIFIED`. Un requisito ensayado necesita una referencia `SYNTHETIC_...` única. Un requisito faltante o no contrastado NO acepta una referencia de respaldo, para no simular evidencia.
- `RehearsalManifest` exige las doce entradas exactamente en orden canónico, empresa/proyecto/snapshot, revisión y hash del registro F6.5, fecha consciente de zona, referencia de ensayo y observador **identificados inequívocamente como sintéticos**, modo exacto `READ_ONLY_SYNTHETIC_REHEARSAL` y finalidad `SYNTHETIC_TEST_ONLY`.
- `assess_read_only_rehearsal` recibe `PinnedOnboarding`, `ReviewRequest` y el **recibo ya obtenido** mediante F6.5; comprueba la relación exacta empresa/proyecto/snapshot, hash/revisión y documento. Rechaza cualquier `real_* = True`, `production_authorized=True`, `decision_authority=True`, permisos o procedencia promovidos.
- Si todas las entradas se han **ensayado sintéticamente** devuelve `SYNTHETIC_REHEARSAL_COMPLETE`, que NO significa autenticación; con un faltante o `UNVERIFIED`, devuelve `REHEARSAL_INCOMPLETE` preservando cada causa. Nunca se omiten pendientes.
- `PilotRehearsalResult` conserva `missing`, `unverified`, `observed`, hashes deterministas de manifiesto y recibo, referencia de empresa y SIEMPRE `real_pilot_admitted=False`, `real_company_authenticated=False`, `real_document_authenticated=False`, `real_human_authorized=False`, `decision_authority=False`, `production_authorized=False`, `operational_path=FORBIDDEN`.

**Frontera de confianza:** el manifiesto y su estado `SYNTHETIC_REHEARSED` son afirmaciones del integrador de pruebas, no una evidencia independiente de que hubo una persona, inspección real o firma. Los fingerprints demuestran estabilidad de los bytes serializados, no identidad, autenticidad jurídica ni trazabilidad frente a un host comprometido. Un recibo construido manualmente es estructuralmente verificable, no firmado; F6.6 no puede emplearse como permiso.

## 4. AUDITAR → DEPURAR → AUDITAR 2

`tests/test_f6_6_supervised_readonly_rehearsal.py` incluye controles positivos y negativos:

1. Dos empresas distintas, una con 12 ensayos sintéticos completos y otra con faltantes explícitos (revocación sin ensayo, tiempo/traza sin verificar).
2. Ningún caso concede permiso real, siquiera cuando el ensayo sintético está completo.
3. Diferencias de empresa, proyecto, snapshot, revisión/hash, fecha, documento, SHA-256 de fuente y SHA-256 documental.
4. Rechazo de `PRESENTED_OPERATIONAL`, supuesta identidad o revisor auténtico, marca `VERIFIED` o `CONFIRMED_REAL`.
5. Rechazo de requisitos duplicados, ausencia/orden incorrecto y soporte repetido o «real» para requisitos sintéticos.
6. Rechazo de recibos F6.5/F6.3 alterados para declarar autorización humana, documental, empresarial o de producción.
7. El assessment no hace nuevas llamadas a identidad, custodia, permiso ni catálogo y no inicia procesos financieros.

`tools/verify_f6_5_provider_onboarding.py` continúa auditando los **mismos cuatro wheels** F6.2–F6.5; el wheel F6.5 ahora incluye los módulos nuevos, auditados byte a byte. Tras los ensayos F6.5 y en los mismos dos entornos offline externos, ejecuta **`python -I -m eios_onboarding_example.pilot_demo`**. Requiere exactamente una preparación completa y una incompleta, documentos separados, mismos resultados en ambos recorridos y prohibiciones de autoridad real.

La CI de Linux (Python/SQL) y Windows (Python 3.12) ejecuta los mismos verificadores offline, renombrando el paso como `F6.5/F6.6`. Se conservan íntegros los tests de fases anteriores y **no se modifican módulos `eios/`**.

## 5. PUERTA REAL DE PILOTO: PENDIENTE, NO ELUDIBLE

Antes de siquiera intentar un **piloto de lectura supervisada con una empresa**, fuera del ensayo F6.6, deberán obtenerse y verificarse por fuentes auténticas: consentimiento/mandato de la empresa, identificación del responsable, IdP, derechos de acceso y revocación, canal/documentación permitidos, custodia segura, protección de datos, ventanas temporales, supervisión, objetivo concreto y procedimiento de detener y borrar según corresponda.

**Aunque todo lo anterior se llegase a obtener**, la lectura técnica empresarial no autoriza automáticamente el uso OPERATIONAL ni sustituye `First_Operational_Expedient_Admission_Checklist`, `Finance_Pilot_Supervised_Review_Procedure` o la decisión humana y todas sus garantías. La F6.6 presente solo certifica que puede **simularse** el checklist, no que se ha superado su versión real.

## 6. CIERRE Y SIGUIENTE UNIDAD

Cerrar F6.6 únicamente al confirmar pruebas Python/SQL, verificación de wheel externo offline en Linux y Windows, auditoría de diff, merge exacto y CI postintegración satisfactoria sobre HEAD de `main`.

Siguiente posible frente F6.7: validación supervisada de la secuencia *sin datos empresariales reales* contra escenarios de fallo, retirada de permisos y capacidad de detener todo el flujo, o —cuando exista empresa colaboradora, contratación y sistema de confianza— preparar una admisión **externa real con evaluación de seguridad independiente**. No se promoverán fixtures sintéticos alterando etiquetas.
