# EIOS — DOC-PAY-CAP-01 — Auditoría de materialización

Fecha: 18/09/2026. Baseline remoto: 5ab5597838013b61e98e0266ac98d1ea7d7986ce.
Autoridad: Documentary_Payment_Association_Capture_Contract_v0.1.md.

## DISEÑAR
Tipos locales DocumentaryMaterial (referencia y bytes), DocumentaryLocator (documento/página/apartado), DocumentaryPaymentBinding (cuota/flow_id/localizadores). Captura inmutable por factory, payload JSON canónico con bytes en base64, digest calculado y FIN-DIP completo. No se añaden campos a tipos cerrados.
Naturaleza explícita SYNTHETIC o PRESENTED_OPERATIONAL; esta última es una declaración del aportante, no verificación. Revisión externa opcional None. Identidades documentales locales, no globales.

## AUDITAR
A1: objetos Pydantic pueden construirse sin validar. Se exige model_validate sobre model_dump y comprobación estricta de bytes/página.
A2: coherencia de FIN-DIP y base debe revisarse: comparar payload base, contexto financiero, snapshot y compra/contexto.
A3: unicidad de flow_id no cubre cuota repetida bajo dos IDs. Se requieren dos conjuntos de unicidad.
A4: los localizadores sólo describen contenido declarado; no prueba de texto ni autenticidad.

## DEPURAR
Se incorporan los controles A1–A3. Bytes no vacíos, identificadores sin espacios exteriores, referencias documentales únicas, localizadores con documento conservado. Flujos no asociados y fuera del horizonte permanecen íntegros.
No se exige suma de cuotas igual a importe de compra, ni se cambia el estado de ningún flujo. Captura vacía no demuestra ausencia de pagos. No se ejecutan motores o gate.

## AUDITAR 2
Revisión del delta: sólo módulo nuevo, suite nueva y este registro. Factory sin constructor de importación, material final bytes, exportación independiente y extracción de bytes exactos. Finanzas y contratos previos no modificados.
Se comprueban fuente vacía/tipo incorrecto, bypass de validación, localizadores, flow_id inexistente/COLLECTION, duplicados, cuota repetida bajo distintos IDs, cuotas fuera del horizonte, identidad sensible al material y ausencia de invocación de motor/gate.
Límites: no autenticación de documento; no verificación semántica de página/condiciones; no búsqueda de referencias económicas equivalentes; no juicio QTG. Las pruebas documentales usan bytes sintéticos, no autenticación del PDF aportado.

## CERRAR / MATERIALIZAR / CI
Diseño y revisión física superados para captura declarada; cierre integrado condicionado a CI exacta previa y posterior. No cierre de productor autenticado ni QTG.
Suite local del módulo: 14 casos aprobados. CI completa verifica el delta sobre el baseline remoto reconciliado; la suite local se ejecuta en el checkout disponible, con los precedentes de pruebas conservados.
