# EIOS — DOC-PAY-TEST-01 — Caso documental sintético

Baseline: main f02cb618cd1a1975f3adbd1744b6a9ec235c69d4.
Fuente: Evidencia_Operacion_EIOS_v2.pdf, tres páginas, aportado como ejemplo sintético.

## DISEÑAR
Unidad de aceptación para las fronteras existentes FIN-DIP-01 y Finance Basic. Transcribir los importes, identidades documentales y vencimientos del ejemplo, con identificación SHA256 del archivo recibido. No crear lector PDF ni productor de evidencia real. La transcripción JSON conserva los hechos relevantes para ejecutar el caso; no contiene el PDF original.
La compra tiene base 1000 EUR; la obligación documental es 1210 EUR. Dos cuotas de 605 EUR, 30/09/2026 y 30/10/2026. La identidad local de cada cuota sirve como flow_id del fixture, no como nueva identidad global EIOS.

## AUDITAR
Se revisaron contenido y presentación de las tres páginas. La v2 corrige revisión QTG ficticia y localización de condiciones. Pedido, confirmación y ficha coinciden. El hash identifica bytes, no autentica al proveedor. El caso sólo ejemplifica un calendario de esta operación; no demuestra todos los flujos de una empresa.

## DEPURAR
Tesorería inicial de 2000 EUR, empresa técnica, supplier_id, DecisionContext y parámetros son setup explícito de pruebas. No se atribuyen al PDF. Horizonte de 30 días: sólo cuota 1 en proyección. Horizonte de 60: ambas cuotas. La captura conserva siempre ambas. None para mínimo y capital circulante se preserva. No se deduce ni resta adicionalmente el pago a partir del precio de compra.
DEMONSTRATED y DETERMINED dentro del fixture describen entradas/resultados sintéticos del motor existente. No significan evidencia empresarial autenticada ni APTO QTG.

## AUDITAR 2
Revisión del delta: sólo fixture, pruebas de integración y este registro. El cálculo esperado es 2000 - 605 = 1395 o 2000 - 605 - 605 = 790, según horizonte. No altera ningún módulo ejecutable ni contrato cerrado. No se afirma que el test detecte duplicación económica entre diferentes flow_id; eso requiere el productor documental pendiente.

## CERRAR
Diseño del caso de aceptación cerrado en este alcance sintético. Materialización y cierre integrado condicionados a pruebas/CI sobre HEAD exacto. Asociación real, contrato ejecutable de productor y QTG no cerrados.

## MATERIALIZAR / CI
Archivos: tests/fixtures/operation_document_payment_case_v2.json y tests/test_operation_document_payment_case.py. Tres casos de aceptación: reconciliación de importes e identidad local y dos horizontes con captura completa y consumo de la frontera financiera pública. La CI verifica Python y SQL; no verifica autenticidad del PDF ni evidencia empresarial.
