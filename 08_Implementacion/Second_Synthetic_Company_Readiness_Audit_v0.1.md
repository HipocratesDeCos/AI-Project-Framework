# EIOS — Preparación de una segunda empresa ficticia: auditoría v0.1

**Base:** `main @ 69a83aebf3313794575e77e9627b37fe71448304`  
**Resultado en una frase:** el núcleo admite material sintético identificado por sus propios datos, pero el ejemplo ejecutable y su paquete están cerrados al caso 001. Para probar adaptación hace falta otro expediente sintético completo y su composición explícita.

## Términos para leer esta auditoría

| Término | Significado aquí |
|---|---|
| **Fixture** | Archivos ficticios y reproducibles que sustituyen documentos empresariales reales. |
| **Bundle** | Material canónico construido y vinculado desde una única fixture validada. |
| **QTG** | Control de calidad de la evidencia de entrada; `APTO` no aprueba una compra. |
| **Invocador** | Preparación concreta que entrega material a una capacidad ya existente. |

## DISEÑAR

Comprobar qué se puede reutilizar para un segundo caso sin copiar identidades,
autoridades ni resultados del primero. La meta futura es demostrar que EIOS
puede procesar **otra empresa ficticia** manteniendo la misma procedencia
`SYNTHETIC`, política `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto
`NO_OPERATIONAL_EFFECT` y `decision_authority=false`.

## AUDITAR — mapa de reutilización

| Tramo | Lo que ya existe | Qué exige otro caso |
|---|---|---|
| Cargador `load_projection_mock_dataset` | Valida inventario exacto de 13 componentes, rutas y hashes. | Otro directorio y manifiesto con bytes propios; no modificar el cargador. |
| Adaptador `build_projection_only_synthetic_material_bundle` | Traduce un dataset admitido a material canónico sintético. | Componentes semánticamente completos y ligados a una sola empresa/compra. |
| `classify_reference_operational_simulation` | Vincula bundle y `reference_case_id` explícito, sin efecto. | ID nuevo y vínculo exacto con el nuevo bundle. |
| QTG y fachada de referencia | Consumen bundle, recibo, compra/contexto e invocadores existentes. | Evidencia y preparación propias; no copiar el dictamen `APTO` o `NO_APTO`. |
| Ocho capturas observadas | Vinculan resultado, caso, compra/contexto y terminal de la misma ejecución. | Productores alimentados por fuentes coherentes del nuevo caso. |
| `examples.reference_business_case_001` | Construye las dos variantes y todos los invocadores. | Está fijo a dos directorios, `COMPANY-MOCK-001`, referencias `REF-BUSINESS-001`, fuentes de precio, proveedor, C0, escenarios y negociación. |
| Revisión y `--verify-dir` actuales | Exigen IDs y QTG esperados del caso 001 y repiten exactamente sus fixtures. | Un contrato de revisión/repetición para otro caso, sin relajar el verificador del 001. |

## DEPURAR — límite que no debe ocultarse

Cambiar solo `reference_case_id`, nombres de carpetas o etiquetas HTML no
constituye una segunda empresa. En el ejemplo, C0 y Supplier Risk/Value usan
`REFERENCE_COMPANY_ID`; PRICE contiene referencias ficticias específicas;
Scenario Coordination prepara escenarios hijos; NI/Ladder emplean contenido
y autoridad sintética particulares. Estos materiales deben ser coherentes con
la nueva compra y contexto antes de llamar a los invocadores.

El runner actual rechaza cualquier variante distinta de `negative` o
`qtg-eligible`. La vista actual compara esas dos identidades y calificaciones
esperadas. Mantener ese comportamiento cerrado protege la repetibilidad del
caso 001; otro caso no debe hacerse pasar por él.

## AUDITAR 2 — secuencia para una prueba legítima

1. **Material:** diseñar una segunda fixture empresarial ficticia de 13
   componentes, con identidades, fechas, importes, parámetros, documentos,
   flujos y evidencia internamente coherentes. El cargador y adaptador
   existentes deben aceptarla sin defaults ni cambios de semántica.
2. **Preparación:** inventariar las fuentes adicionales de cada invocador
   (PRICE, TCO, proveedor, C0, Twin, escenarios, NI y Ladder) y declarar
   expresamente cualquier captura que no pueda producirse con ese material.
3. **Ejecución:** reutilizar la fachada y los wrappers observados con la
   nueva procedencia. Rechazar mezclas de empresa, compra, contexto o caso
   antes de emitir un terminal.
4. **Presentación:** verificar y presentar el segundo paquete con su propia
   identidad, conservando visible que toda la evidencia es ficticia.

La primera prueba útil de adaptación es **cargar y construir un segundo
bundle**, antes de prometer ocho capturas o una UI genérica. Si una capacidad
exige un material que no existe, se registra la ausencia y se detiene esa
rama; no se completa con valores inventados durante la ejecución.

## CERRAR

**Preparación parcial, no ejecución demostrada.** El núcleo sintético ofrece
fronteras reutilizables. La composición de material y el empaquetado siguen
siendo específicos del caso 001. La siguiente unidad de implementación será
la fixture 002 y su validación de carga/adaptación; no se abre ningún contrato
cerrado sin una contradicción objetiva ni se admite material operacional.

## MATERIALIZAR → CI

Esta unidad deja la auditoría legible y verificable. No cambia código,
fixtures o resultados. La CI del PR valida su integración documental; la
fixture 002 necesitará su propio ciclo y pruebas físicas.
