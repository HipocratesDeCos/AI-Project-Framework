# EIOS — FASE 3 · ACTA DE ACEPTACIÓN Y CIERRE TÉCNICO

**Fecha de preparación:** 2026-11-16  
**Rama base:** `main @ 442232e7cbf01c56c3050455689923e9a719b188` (PR #595 / F3.10).  
**Estado de esta acta:** **CONDICIONADO** al cierre de F3.11, la CI de la PR de cierre y la reconciliación de CI postintegración; no se debe marcar el cierre como verificado antes de esos resultados.

## 1. OBJETIVO DE CIERRE: EVITAR SUBFASES INDEFINIDAS

Se establece como ámbito de la **fase 3 técnica** estabilizar las fronteras de la versión de parámetros, identidad/empresa, gobierno de claves, integridad de la ejecución financiera **sintética local** y trazabilidad de movimientos y soportes, sin reescribir el núcleo matemático.

La fase 3 no puede prometer una empresa real autenticada ni operaciones reales sin un proveedor externo real y documentos de una empresa admitidos. El cierre técnico de las partes efectivamente implementadas no es una admisión de empresa ni un cierre de esa dependencia.

## 2. MATRIZ DE ENTREGABLES

| Unidad | Entregable implementado | Evidencia GitHub |
|---|---|---|
| F3.1 | Activación financiera sintética local frente a configuración canónica, antes de calcular | PR #586 |
| F3.2 | Fuente read-only de versiones históricas de activaciones sintéticas, contrato F2.4 | PR #587 |
| F3.3 | Manifiestos de versiones firmados Ed25519; clave pública confiable siempre suministrada **externamente** | PR #588 |
| F3.4 | Verificador de gobierno/ciclo de vida de claves, revisión y checkpoint externo anti-rollback | PR #589 |
| F3.5 | Puertos externos de identidad empresarial, autorización por sujeto/empresa y raíz de gobierno | PR #590 |
| F3.6 | Pruebas adversariales conjuntas F2.4→F3.5: revocación, tenant, evidencia y carreras de cambio de permisos | PR #591 |
| F3.7 | Rechazo de capital circulante de otra empresa, fecha o moneda y no publicación de salidas parciales | PR #592 |
| F3.8 | Verificación completa del inventario de cobros/pagos contra los registros SQLite y orden estable | PR #593 |
| F3.9 | Comprobación de bytes y referencias de soportes del flujo; contenido no revisado | PR #594 |
| F3.10 | Auditoría de vínculos explícitos factura–cuota–flujo, sin inferencia por fechas/importes | PR #595 |
| F3.11 | Correspondencia del saldo inicial con el snapshot conservado y la propuesta; señales de duplicidad de caja/bancos | PR de cierre / CI pendiente |

Cada unidad tiene pruebas negativas y positivas asociadas; el método obligatorio sigue siendo **DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**.

## 3. PROPIEDADES TÉCNICAS QUE SÍ PODEMOS ACEPTAR

En el entorno sintético local y en las suites auditadas:

- Referencias financieras y sus versiones se cotejan antes del análisis; una discrepancia impide presentar una salida completada donde el contrato lo requiere.
- Empresa, fecha, moneda, identidad de los flujos, huellas de documentos y huellas del contexto guardado se comprueban por los consumidores donde corresponden.
- Una coincidencia de importe/vencimiento **no** crea una asociación comercial.
- Una firma Ed25519 correcta **no** acredita la identidad jurídica de su titular cuando la clave no está anclada en una autoridad externa autenticada.
- Un documento conservado sin cambios **no** demuestra que su contenido haya sido revisado o que una factura esté conciliada con su banco.
- Un saldo de la cuenta 572 no es automáticamente tesorería disponible; no se suman sin criterio cuentas padre e hijas 570/572.
- Ninguna de las unidades F3 autoriza compras, pagos o ventas: `decision_authority=False` y `operational_path=FORBIDDEN`.

## 4. FRONTERAS NO RESUELTAS — EXCLUSIONES EXPLÍCITAS

**No deben calificarse como cerradas, ni convertirse en hechos por documentación o tests sintéticos:**

1. **Identidad y autoridad corporativa**: falta conectar un IdP real del host, verificar la vinculación de usuarios con una persona jurídica concreta, conceder/revocar roles mediante procesos autorizados y proporcionar un trust store de claves públicas con procedencia autentificada.
2. **Gobierno externo verificable**: falta proveedor corporativo de historial firmado, claves/firmas de autoridades admitidas, checkpoint externo monotónico resistente a rollback, operaciones de enrolamiento realmente autenticadas.
3. **Datos contables y comerciales externos**: faltan extractos bancarios, saldos 570/572 conciliados, facturas y cuotas con situación a fecha de corte y el inventario completo de cobros/pagos/compromisos, todos atestados por fuentes admisibles.
4. **Admisión de empresa**: falta expediente `PRESENTED_OPERATIONAL` admitido por procedimiento independiente. `REFERENCE_OPERATIONAL_SIMULATION` permanece sintética; no se cambia su etiqueta para habilitar ruta real.
5. **Prueba de piloto**: falta validar expresamente entradas, políticas, recuperación de errores, permisos, conciliación, trazabilidad y aceptación de una empresa real. Las cuentas anuales de 2–3 ejercicios servirán para la evolución financiera histórica, **no** para cerrar estos apartados por sí solas.

Estos son **bloqueos de implantación operacional**, no excusas para añadir subfases técnicas sin un problema reproducible. El próximo trabajo debe depender de proveedores y evidencia reales cuando existan, no de crear otra taxonomía o un segundo motor de conciliación.

## 5. DECISIÓN DE CIERRE Y SIGUIENTE ETAPA

Se permite declarar **FASE 3 — CONSTRUCCIÓN TÉCNICA CERRADA** solamente cuando:

- F3.11 supera sus pruebas y no introduce regresiones.
- La PR de cierre no modifica FIN Basic, PRICE, QTG/Rules ni SQL Server canónico para acomodar los tests.
- La CI Python + 3 controles SQL supera el HEAD exacto de la PR, se integra con guardia de SHA y la CI **postmerge de `main`** también termina `SUCCESS`.
- Se publica en la PR el commit de `main`, número de pruebas y comprobaciones postintegración con la limitación operacional.

El estado que se deberá publicar entonces es:

- `phase_3_technical_implementation=COMPLETE`;
- `phase_3_enterprise_admission=BLOCKED_EXTERNAL_EVIDENCE`;
- `phase_3_corporate_identity=NOT_CONFIGURED`;
- `operational_path=FORBIDDEN`;
- `decision_authority=false`.

**No se abre una F3.12 por defecto.** La siguiente etapa debe centrarse en preparar la incorporación de documentos reales, elegir una empresa piloto/IdP y validar el modelo de negocio, sin confundirlo con la autorización operacional. Si aparece un fallo técnico reproducible, se abrirá como incidencia independiente y no se atribuirá al cierre de una nueva fase.

**Aprobación final pendiente de CI y reconciliación postmerge**, según la política de este proyecto.
