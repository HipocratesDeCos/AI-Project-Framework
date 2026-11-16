# EIOS — F5.2 · VÍNCULO ESTRICTO DE VERSIONES EN TCO (OPT-IN)

**Fecha:** 2026-11-16
**Baseline:** `main @ 42d4387a79c4cda27f90ad937ee009b019586263`, F5.1 integrada y CI postmerge #43943934502 SUCCESS.
**Alcance:** endurecer el adaptador de TCO, sin modificar `calculate_tco`, el esquema físico `TCOInput`, el Motor neutral ni la ruta pública histórica.

## 1. DISEÑAR

La auditoría F5.1 constató:

- PRICE compara el contexto completo de cinco campos y todos los campos de compra antes de ejecutar.
- El invocador TCO existente comprueba todos los campos de la compra y solo `decision_id` / `scenario_id` del contexto, ya que `TCOInput` no guarda el resto de versiones.
- La ausencia de verificación explícita de `rules_version`, `parameters_version` y `data_snapshot_id` no permite atribuir al adaptador TCO una correspondencia contextual completa.

No se introduce un segundo Motor, versión de TCO, autoridad documental o nuevo resultado. Se añade una fábrica **optativa** en `eios/core/tco_integration.py`:

`build_context_checked_tco_invoker(payload=TCOInput, expected_context=DecisionContext)`

**Responsabilidad del llamante:** suministrar y autenticar, por los mecanismos del proyecto, el `expected_context` recibido. Esta fábrica no certifica la fuente ni aporta firma/autorización; únicamente coteja la igualdad exacta de su contenido con el contexto de ejecución.

## 2. AUDITAR — CONTRATO

1. Exige `TCOInput` y `DecisionContext` tipados; congela mediante copias profundas los dos objetos al construir el invocador.
2. En la construcción rechaza el origen si `purchase_operation.decision_id` o `scenario_id` difiere del contexto esperado.
3. Antes de ejecutar comprueba TODOS los campos declarados en `DecisionContext.model_fields` frente a la instantánea congelada (incluye reglas, parámetros y fuente de datos).
4. Si cualquiera difiere, falla cerrado ANTES de `calculate_tco` y conserva el nombre de campo rechazado. Dentro del límite público `run_mvp_execution` se traduce al estado técnico `FAILED`.
5. Con contexto válido conserva **el mismo productor `_produce_bound_tco` y adaptador `adapt_tco`**. No se recalculan importes con otras fórmulas.
6. `build_provenanced_tco_invoker` sigue existiendo sin cambios para los consumidores heredados; no se modifica su comportamiento ni se obliga a migrarlo sin una evaluación de compatibilidad.

## 3. DEPURAR — PRUEBAS

`tests/test_f5_2_tco_context_checked_invoker.py` cubre resultado completo con paridad respecto a la ruta histórica, todos los campos de contexto adversarios, inexistencia de cálculo ante drift, protección frente a modificaciones de entradas tras construir, discrepancias de identidad desde el origen, desviaciones de compra, estados de costes incompletos y compatibilidad de la API antigua.

**Sin cambios en:** `eios/kernel/`, `eios/tco/engine.py`, `eios/tco/models.py`, SQL Server, PRICE, QTG, O1, fuentes de datos, pantallas, dependencias o ruedas de distribución.

## 4. AUDITAR 2 — LÍMITES DE AUTORIDAD Y REUTILIZACIÓN

- **Verificación de correspondencia ≠ autenticación de origen:** un contexto falsificado pero internamente coherente puede seguir siendo aceptado si el llamante no valida fuentes. Ningún dato operacional se admite automáticamente.
- La nueva fábrica es un límite de aplicación sectorial de **Compras**, no una API genérica para Ventas ni un módulo dentro del paquete mínimo `eios-kernel`.
- No se puede afirmar que todos los consumidores históricos hayan adoptado la ruta estricta. Su migración requiere un plan verificable, sin alterar decisiones ya cerradas.
- Los resultados técnicos no autorizan compras: `decision_authority=False` y `operational_path=FORBIDDEN` siguen siendo invariables del núcleo neutral.
- **Siguiente paso F5.3:** estudiar si TCO debe seguir como capacidad exclusiva de Compras o admite un paquete opcional con contrato independiente, sin esconder ni reescribir la lógica financiera.

## 5. CERRAR → MATERIALIZAR → CI

Cierre solo con revisión del diff, tests Python completos, tres controles SQL y pruebas de distribución F4 en CI de PR sobre HEAD exacto, merge controlado y CI postintegración sobre SHA exacto de `main`. Hasta entonces, no anunciar el contrato como estable.
