# EIOS — QTG-FIN-PREP-01 — Auditoría de implementación v0.1

Fecha: 18/09/2026. Baseline: 4ec1dc195d7118d82ed6ff7c7e7c025ea7462872; CI #861 SUCCESS.

## DISEÑAR

Materializar únicamente la preparación vinculada de QTG_Finance_Evaluation_Binding_Design_v0.1.md, PR #175. Conservar captura/calendario/cobertura completos, revisión/designación opcionales y documentos de criterios íntegros. No implementar la ejecución, recibo de resultado o integración financiera QTG.

## AUDITAR

A1: coverage puede corresponder a otra captura o autoridad de calendario. Validar pertenencia completa y recomputar comparación estructural, contrastando payload y fingerprint.
A2: revisión/designación pueden pertenecer a otra cadena. Usar validadores cerrados de captura→revisión→designación; rechazar designación sin revisión.
A3: ausencia no es una colección conocida/positiva. Conservar None y fingerprints None para revisión/designación ausentes; no asignar criticidad/aplicabilidad por ausencia.
A4: referencia/hash de criterio no conserva política usada. Exigir bytes no vacíos, referencia y versión explícitas; revalidar copias/bypass y rechazar referencia/versiones duplicadas.
A5: contenido de criterios no demuestra aprobación. Conservarlo como presentado sin interpretación, ejecución, defaults QualityCheck ni traducción a estados QTG.
A6: registros positivos no resuelven cobertura negativa. Conservar ambos; no emitir resultado global.
A7: mutable input/export puede cambiar retrospectivamente material. Conservar JSON canónico en bytes con exportaciones independientes y fingerprint calculado sobre conjunto completo.

## DEPURAR

Salida limitada a BOUND_PRESENTED_MATERIAL_ONLY, consumidor run_provenanced_finance_basic. No recibe resultado previo ni callback, no llama Finance/QTG, no autentica documentos, revisores, otorgantes o autoridad del criterio. Conservar naturezas originales por separado.
Una preparación válida puede contener cobertura negativa, condiciones pendientes o ausencia de revisión/designación. Validez de construcción significa vinculación técnica, no permiso para ejecutar analítica ni APTO.
Las pruebas usan material sintético sustituto explícito y documentos de criterios Mock Data, no los bytes de PDF aportados ni prueba empresarial. Recomputación de cobertura es reproducibilidad estructural, no autenticación.

## AUDITAR 2

17 pruebas específicas satisfactorias: material completo/ausencias, documentos de criterio y hashes calculados, registros opcionales con pendientes, cuatro tipos de vínculo ajeno, designación sin revisión, cobertura falsificada no reproducible, criterios vacíos/colecciones inválidas/hash suelto/bypass/bytes inválidos/referencia vacía, duplicados, inmutabilidad y sensibilidad a contenido/versiones, cobertura negativa con positivos locales sin llamadas a motores.
PASS técnico para fundamento físico G04. No modifica componentes cerrados ni levanta cuarentena. Pendientes: criterios completos G02 y soporte suficiente G03; ejecución/recomputación/recibo/consumo QTG aún no materializados. G04 completo no se declara cerrado.
Suite completa local: 1097 pruebas satisfactorias con pytest 8.4.2, seis avisos (cinco previos y uno esperado en la nueva prueba de bypass de bytes). SQL no ejecutado localmente: verificar su paso en CI.

## CERRAR → MATERIALIZAR → CI

Cierre técnico condicionado a CI completa sobre HEAD exacto y merge. Material: eios/core/finance_quality_preparation.py, tests/test_finance_quality_preparation.py y esta auditoría.
Siguiente unidad: precisar criterios/soporte suficientes de entradas financieras necesarias para el piloto, en particular disponibilidad de tesorería y temporalidad aplicable, usando autoridades existentes antes de proponer nueva política. No fabricar productor positivo desde material presentado.
