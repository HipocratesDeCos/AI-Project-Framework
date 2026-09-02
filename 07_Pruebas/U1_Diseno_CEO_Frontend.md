# EIOS — U1 · CEO FRONTEND / INTERACCIÓN OPERATIVA

**Estado:** 🟡 DISEÑO DEPURADO — NO IMPLEMENTADO
**Baseline:** `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`
**Diseño inicial:** `be893119793b2a78b6baac92da42333ecf66f1b8`
**Auditoría 1:** `bdced7a6b22fc63702d7fa37939e302d1e1e39a4`

## 1. Propósito

Definir la capa de interacción mediante la cual un CEO o usuario autorizado introduce información, revisa su calidad y contexto, solicita una operación EIOS y recibe resultados de soporte a la decisión.

U1 es una capa de presentación y aplicación, no una nueva autoridad analítica.

## 2. Frontera contractual U1 → O1

U1 no construye ni modifica directamente identidades técnicas canónicas. Recopila datos de negocio autorizados y los entrega a una Application Boundary que prepara la invocación contractual de O1.

```text
CEO / USUARIO AUTORIZADO
          ↓
       U1 FRONTEND
          ↓
  APPLICATION BOUNDARY
          ↓
          O1
          ↓
 C0 / PRICE / TCO / QTG / O2 / O3 / ...
          ↓
 DECISION SUPPORT PACKAGE
          ↓
       U1 FRONTEND
          ↓
 CEO / DECISIÓN HUMANA
```

La Application Boundary traduce la entrada de UI al contrato autorizado. No introduce `decision_version` ni una segunda identidad/versionado de decisión.

## 3. Datos de entrada

La pantalla de nueva operación se limita a campos autorizados de `PurchaseOperation` y referencias de evidencia admitidas por los contratos existentes.

La UI puede comprobar formato, obligatoriedad y coherencia superficial. C0/QTG mantienen la autoridad sobre validación de dominio y calidad.

```text
UI validation ≠ C0 domain validation ≠ QTG quality gate
```

## 4. Contexto y versionado

`decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id` se tratan como contexto controlado por la aplicación.

La UI puede mostrar estos valores y seleccionar referencias autorizadas, pero no editarlos libremente. No se introduce `decision_version`.

## 5. Máquina de estados visible

Se muestran literalmente READY, RUNNING, COMPLETED, BLOCKED, PARTIALLY_COMPLETED, NOT_EVALUABLE y FAILED.

- `NOT_EVALUABLE` no se presenta como resultado negativo.
- `FAILED` se presenta como fallo técnico, no como decisión empresarial.
- `BLOCKED` indica que la ejecución no puede continuar bajo las condiciones actuales.
- `PARTIALLY_COMPLETED` conserva explícitamente lo que falta.
- ausencia de resultado no equivale a `NO COMPRAR`.

## 6. Evidencia

U1 puede capturar o referenciar evidencia y mostrar su estado. No convierte por sí misma una evidencia en evidencia válida ni sustituye QTG.

La vista distingue como mínimo `AUSENTE`, `NO VÁLIDA`, `SUFICIENTE/VALIDADA` y `CON ADVERTENCIAS`.

## 7. Resultado ejecutivo

La presentación separa visual y semánticamente:

1. Datos introducidos.
2. Resultados derivados.
3. Evidencia/trazabilidad.
4. Limitaciones/advertencias.
5. Decisión humana.

U1 no recalcula TCO, PRICE, QTG, Assessment, Viability ni otros resultados para dibujar la pantalla.

## 8. Escenarios

U1 presenta escenarios ya autorizados y sus resultados. No calcula Cartesian products, no puntúa escenarios y no selecciona el mejor.

Cuando O4 esté integrado contractualmente: `U1 → Application Boundary → O4 → O2 → O3`.

La selección de un escenario para visualizarlo no constituye ranking empresarial.

## 9. Decision Twin

La comparación es descriptiva: diferencias, resultados, condiciones, consecuencias, riesgos y trazabilidad cuando estén disponibles.

No existe una acción de UI que convierta la comparación en selección automática.

## 10. Seguridad de interacción

Toda acción que modifique una operación requiere confirmación explícita y muestra previamente su alcance.

Guardar, ejecutar, recalcular y decidir son acciones semánticamente diferenciadas. Las acciones de decisión empresarial quedan fuera de la autoridad de U1.

## 11. Accesibilidad y presentación

Mínimos MVP: navegación por teclado, etiquetas explícitas, errores asociados al campo, contraste suficiente, estados no dependientes solo del color, tamaños legibles, lenguaje ejecutivo claro y responsive escritorio/tablet.

La estética nunca oculta incertidumbre, limitaciones ni ausencia de resultado.

## 12. Pantallas MVP

1. Dashboard.
2. Nueva operación.
3. Evidencia.
4. Contexto.
5. Ejecución.
6. Resultado ejecutivo.
7. Escenarios.
8. Comparación.

## 13. Fuera de alcance

No incluye autonomía decisional, optimización, ranking automático, ejecución de compras, negociación automática, administración de reglas, edición de parámetros maestros, nueva persistencia, API pública ni SSO empresarial no especificado.

## 14. Criterios para AUDITORÍA 2

Debe verificarse la frontera U1 → Application Boundary → O1, correspondencia con `PurchaseOperation`, preservación de `DecisionContext`, estados O1, evidencia/QTG, TCO/PRICE, O2/O3/O4, Decision Twin, ausencia de decisión automática, accesibilidad, trazabilidad y ausencia de autoridad paralela.

**No se autoriza implementación por este documento.**