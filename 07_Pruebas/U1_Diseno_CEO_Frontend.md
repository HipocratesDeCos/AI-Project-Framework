# EIOS — U1 · CEO FRONTEND / INTERACCIÓN OPERATIVA

**Estado:** 🟡 DISEÑO — NO IMPLEMENTADO
**Baseline:** `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`
**Rama:** `design/u1-ceo-frontend`

## 1. Propósito

Definir la capa de interacción mediante la cual un CEO o usuario autorizado introduce información, revisa su calidad y contexto, solicita una operación EIOS y recibe resultados de soporte a la decisión.

U1 es una **capa de presentación y aplicación**, no una nueva autoridad analítica.

## 2. Arquitectura

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

El frontend no accederá directamente a motores internos para tomar decisiones.

## 3. Flujo principal

1. Crear nueva operación.
2. Introducir datos de compra.
3. Revisar datos obligatorios y formatos.
4. Adjuntar/referenciar evidencia autorizada.
5. Revisar contexto, versiones y snapshot.
6. Ejecutar la operación mediante la frontera de aplicación.
7. Mostrar estado de ejecución.
8. Mostrar resultados y limitaciones.
9. Mostrar escenarios y comparaciones cuando existan.
10. Presentar el paquete de soporte a decisión.
11. Mantener explícita la decisión final humana.

## 4. Pantallas MVP

### U1.1 Inicio / Dashboard

Debe mostrar operaciones recientes, estado de ejecución y accesos a nueva operación.

### U1.2 Nueva operación

Formulario estructurado para los datos autorizados de `PurchaseOperation`.

No se crearán campos que representen autoridad inexistente.

### U1.3 Evidencia

Carga/referencia y estado de validación de evidencia.

La UI debe distinguir claramente ausencia de evidencia, evidencia inválida y evidencia suficiente.

### U1.4 Contexto

Presentación de `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id` cuando correspondan.

No se añadirá `decision_version` como sustituto no autorizado.

### U1.5 Ejecución

Estado técnico visible: READY, RUNNING, COMPLETED, BLOCKED, PARTIALLY_COMPLETED, NOT_EVALUABLE, FAILED.

Nunca presentar un estado técnico como decisión empresarial.

### U1.6 Resultado ejecutivo

Vista orientada al CEO con:

- resultado de soporte;
- principales evidencias;
- advertencias;
- limitaciones;
- costes relevantes;
- escenarios disponibles;
- trazabilidad accesible.

### U1.7 Escenarios

Presentación de escenarios autorizados y sus resultados derivados.

No seleccionar automáticamente el mejor escenario.

### U1.8 Comparación

Comparación descriptiva de alternativas/escenarios cuando exista un `Decision Twin` válido.

No debe existir botón o comportamiento equivalente a selección automática de alternativa.

## 5. Principios UX

La interfaz debe priorizar:

- claridad ejecutiva;
- baja carga cognitiva;
- trazabilidad bajo demanda;
- separación entre dato introducido y resultado calculado;
- separación entre resultado técnico y decisión empresarial;
- visibilidad de incertidumbre;
- estados explícitos;
- prevención de acciones irreversibles.

La estética no puede ocultar limitaciones ni convertir una ausencia de resultado en un valor negativo.

## 6. Autoridad

U1 no puede:

- modificar reglas;
- modificar parámetros autorizados;
- alterar evidencia histórica;
- cambiar resultados de motores;
- crear ranking empresarial;
- aprobar/rechazar compras automáticamente;
- negociar automáticamente;
- convertir una recomendación técnica en decisión;
- crear una segunda identidad o versionado de decisión.

El usuario conserva la decisión empresarial final.

## 7. Entrada de datos

Los formularios deben validar estructura y formato antes de enviar datos a la frontera de aplicación.

La validación de UI no sustituye C0 ni QTG.

Debe distinguirse:

```text
ERROR DE FORMULARIO
        ≠
ERROR DE VALIDACIÓN DE DOMINIO
        ≠
NOT_EVALUABLE
        ≠
FAILED
```

## 8. Presentación de resultados

El resultado debe conservar:

- identidad;
- contexto/versiones;
- estado;
- evidencia y trazabilidad compatibles;
- limitaciones;
- resultados derivados.

La UI no debe recalcular resultados para presentarlos.

## 9. Escenarios y O4

U1 podrá presentar parámetros autorizados para generar escenarios cuando O4 esté integrado contractualmente.

La UI no debe construir combinaciones por su cuenta ni duplicar la lógica de O4.

Flujo futuro:

```text
U1 → Application Boundary → O4 → O2 → O3
```

## 10. Seguridad de interacción

Toda acción que pueda modificar una operación debe mostrar claramente su alcance antes de confirmarse.

Las acciones de decisión empresarial no deben confundirse con acciones técnicas como guardar, recalcular o ejecutar.

## 11. Responsive / dispositivos

El MVP deberá funcionar correctamente en escritorio y tablet. La vista móvil podrá ser una adaptación posterior, sin alterar la semántica contractual.

## 12. Accesibilidad

Mínimos de diseño:

- navegación por teclado;
- etiquetas explícitas;
- estados no dependientes exclusivamente del color;
- mensajes de error asociados al campo;
- contraste suficiente;
- tamaños legibles;
- lenguaje ejecutivo claro.

## 13. Fuera de alcance

U1 MVP no incluye:

- autonomía decisional;
- optimización;
- ranking automático;
- ejecución de compras;
- negociación automática;
- modificación directa de motores;
- administración de reglas desde el frontend;
- edición de parámetros maestros;
- API pública;
- persistencia nueva;
- autenticación/SSO empresarial no especificada.

## 14. Criterios para AUDITORÍA

Antes de materializar U1 deben auditarse:

1. frontera U1 → O1;
2. correspondencia de campos con `PurchaseOperation`;
3. autoridad de DecisionContext;
4. estados O1;
5. evidencia/QTG;
6. presentación de TCO/PRICE;
7. escenarios O2/O3/O4;
8. Decision Twin;
9. ausencia de decisiones automáticas;
10. accesibilidad y estados de error;
11. trazabilidad visible;
12. ausencia de autoridad paralela.

**No se autoriza implementación por este documento.**