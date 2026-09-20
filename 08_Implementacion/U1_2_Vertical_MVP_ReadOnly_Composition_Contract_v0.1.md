# EIOS — U1.2 · Vertical MVP Visual Read-Only Composition — Contract v0.1

**Baseline:** `main @ 076828839ebe6004a5052ad5e778cb4c1b1dc62a`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → CERRADO TÉCNICAMENTE — CI PENDIENTE

## 1. Propósito

Cerrar el hueco entre la frontera visual ya materializada:

`present_vertical_mvp_result(...) → build_vertical_mvp_view_model(...)`

y una composición visual utilizable en navegador, sin reabrir U1.1 ni introducir una nueva frontera analítica.

U1.2 es exclusivamente una capa de render read-only sobre un view-model ya producido.

## 2. Frontera autorizada

```text
VerticalMVPSupportResult
        ↓
present_vertical_mvp_result
        ↓
build_vertical_mvp_view_model
        ↓
U1.2 read-only renderer
        ↓
HTML visual
```

El renderer no recibe modelos de dominio, no recibe motores, no recibe invocadores y no construye resultados EIOS.

## 3. Entrada única

La entrada de U1.2 es exclusivamente el `Mapping` producido por `build_vertical_mvp_view_model`.

No se admite como entrada:

- `VerticalMVPSupportResult`;
- `DecisionSupportPackage`;
- `PurchaseOperation`;
- `DecisionContext`;
- callbacks o invocadores;
- resultados PRICE/TCO/QTG/Twin/NI/Ladder desprendidos;
- datos de formulario de operación.

## 4. Salida

La salida visual puede representar únicamente contenido ya existente en el view-model:

- estado técnico de ejecución;
- versión de política;
- fallo técnico y elementos no resueltos;
- capacidades y estados ya producidos;
- disponibilidad y cobertura Rules/CRC;
- resultado consolidado de soporte CRC, sin presentarlo como decisión humana;
- Assessments;
- referencias de traza;
- disponibilidad del soporte de escenarios;
- contexto de ejecución de escenarios;
- registros de escenarios;
- comparación descriptiva de escenarios.

## 5. Reglas de representación

1. `rules_available=false` se muestra como bloque no disponible; nunca como “sin problemas”.
2. `scenario_support_available=false` se muestra como bloque no disponible; nunca como ausencia de riesgo.
3. `NOT_EVALUABLE`, `FAILED`, `BLOCKED`, `PARTIAL` y estados equivalentes se conservan literalmente.
4. Una regla omitida no se presenta como falsa.
5. Un resultado CRC no se etiqueta como aprobación, rechazo o decisión.
6. Una comparación de escenarios no produce “mejor escenario”.
7. No se generan scores, rankings, semáforos decisionales ni recomendaciones nuevas.
8. Los arrays conservan orden.
9. `None/null` no se convierte en cero, vacío favorable o éxito.
10. Todo texto procedente del view-model se renderiza como texto, nunca como HTML confiable.

## 6. Seguridad de presentación

La implementación deberá escapar contenido dinámico o utilizar APIs DOM de texto seguras.

No se permite concatenar contenido dinámico sin escape dentro de HTML ejecutable.

No se permite ejecutar scripts, URLs o markup procedentes del view-model.

## 7. No mutación

El renderer no modifica el view-model recibido.

La composición visual debe poder repetirse sobre la misma entrada produciendo representación equivalente.

## 8. U1.1 permanece cerrado

U1.2 no modifica:

- `eios/frontend/visual/view_model.py`;
- la semántica del `index.html` U1.1;
- el formulario de entrada U1.1;
- U1 Application Boundary.

La composición se materializará como una unidad visual independiente para evitar convertir el shell histórico U1.1 en una superficie con semántica nueva.

## 9. Prohibiciones

Queda fuera:

- ejecución de capacidades;
- acceso directo a Rules, CRC, Scenario, Twin, Price, TCO, Finance, QTG, NI o Ladder;
- networking;
- persistencia;
- autenticación;
- edición de datos;
- aprobación/rechazo;
- recomendación automática;
- orden de compra;
- selección automática de escenario;
- modificación de reglas o parámetros;
- representación operacional de QTG `SYNTHETIC_TEST`.

## 10. Pruebas mínimas

La implementación deberá demostrar:

- render de ejecución completa;
- render de rules ausente;
- render de scenario support ausente;
- conservación literal de `NOT_EVALUABLE`;
- separación de reglas ejecutadas y omitidas;
- ausencia de “best scenario”, score, ranking o aprobación;
- escape de contenido dinámico;
- orden preservado;
- no mutación de la entrada;
- rechazo fail-closed de view-model incompleto;
- ausencia de imports o llamadas a motores.

## 11. Forma técnica depurada

La materialización se realizará mediante una función pura:

`render_vertical_mvp_readonly(view_model: Mapping[str, Any]) -> str`

que devolverá un documento HTML completo y autosuficiente.

Decisiones de implementación:

- sin JavaScript;
- sin networking;
- sin persistencia;
- navegación interna mediante anclas HTML;
- CSS estático embebido;
- contenido dinámico escapado con `html.escape`;
- listas/tablas en el mismo orden recibido;
- `None` representado como “NO DISPONIBLE”, nunca como cero o resultado favorable;
- bloques ausentes representados explícitamente como “NO SUMINISTRADO”;
- estado de ejecución etiquetado como **estado técnico**;
- resultado CRC etiquetado como **resultado de soporte CRC — no decisión humana**;
- comparación de escenarios presentada descriptivamente, sin cálculo adicional;
- validación estructural mínima y fail-closed del view-model esperado.

No se aceptará un template con lógica de negocio ni un renderer que reciba modelos EIOS.

## 12. Criterio de cierre

U1.2 podrá cerrarse cuando exista una composición visual navegable/read-only demostrablemente alimentada solo por el view-model ya autorizado, con pruebas de fidelidad, seguridad y ausencia de autoridad decisional.

No habilita por sí sola ejecución real del Vertical desde navegador.
