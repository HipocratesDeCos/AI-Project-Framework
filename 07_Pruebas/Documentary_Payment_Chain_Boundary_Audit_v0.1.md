# EIOS — DOC-PAY-CHAIN-01 — Auditoría transversal de vínculos y límites v0.1

Fecha: 18/09/2026. Baseline remoto: 430a4066e717071e469f2fe30ab2fae7a1aed9b6, CI #857 SUCCESS.

## DISEÑAR

Unidad de verificación transversal de los contratos ya cerrados FIN-DIP-01, DOC-PAY-CAP-01, DOC-PAY-REVIEW-01, DOC-PAY-DESIG-01 y DOC-PAY-COVER-01. Añadir únicamente pruebas que construyen la cadena existente sobre una misma captura y este registro. No añadir productor, integración QTG, API, registro empresarial o arquitectura nuevos.

## AUDITAR

A1: cobertura completa no rellena observaciones humanas o de designación omitidas. Examinar independientemente los inventarios de 13 controles de revisión para dos cuotas y siete condiciones de designación.
A2: todos los registros locales positivos pueden coexistir sin acreditar calidad operativa. Probar que no emiten QualityCheck/QualityTrustResult, autorización ni pago y que no llaman motores.
A3: una revisión declarada positiva puede coexistir con referencia/versiones incorrectas respecto del calendario requerido. No permitir que la declaración oculte esa discrepancia estructural.
A4: un documento cambiado produce otra captura; comprobar rechazo conjunto de reutilización de cobertura, revisión y vínculo de designación anterior sobre el nuevo material.
A5: revisión humana cubre captura, no la autoridad del calendario requerido. Cambiar esa autoridad invalida pertenencia de cobertura aunque la revisión continúe vinculada a la misma captura. El futuro binding QTG debe conservar ambos materiales, no sustituirlos por uno solo.

## DEPURAR

No agregar los éxitos locales en un éxito global. No eliminar hallazgos positivos suministrados para resolver discrepancias: conservar ambos niveles y su límite. No afirmar que los actuales validadores de pertenencia implementan un productor QTG.
Las pruebas usan bytes sustitutos sintéticos y afirmaciones ficticias; no representan revisiones reales, facultades de personas o lectura de los PDF aportados. Se reutiliza el calendario de dos cuotas y las capturas existentes, sin cambiar contratos cerrados.

## AUDITAR 2

Cinco pruebas transversales satisfactorias: cobertura con revisión/designación incompletas; todos los positivos sin resultado operativo; versión de pedido ajena pese a positivos declarados; documento cambiado y rechazo de tres vínculos; autoridad del calendario cambiada con revisión aún vinculada a captura original.
No se ha detectado contradicción que justifique reabrir los componentes cerrados. La semántica limitada de sus salidas es consistente con sus contratos.
Pendientes concretos: G02 para requisitos financieros no determinados, G03 para soporte suficiente de condiciones necesarias y G04 para evaluación/reevaluación QTG vinculada al conjunto completo de material y criterios. La necesidad de las dos cuotas del caso ya está determinada; no se vuelve a pedir su definición.

## CERRAR → MATERIALIZAR → CI

Se cierra esta auditoría transversal condicionada a CI completa sobre HEAD exacto y merge. Material: tests/test_documentary_payment_chain_boundaries.py y este registro; sin cambios al runtime.
Continuidad legítima: diseñar G04 con los vínculos físicos contrastados, preservando captura, calendario requerido, revisión, designación y criterios usados. El diseño de vinculación puede avanzar con Mock Data; levantar cuarentena o certificar calidad empresarial sigue requiriendo cerrar criterios y observación suficiente. No exigir documentos empresariales reales para seguir diseñando/probando.
