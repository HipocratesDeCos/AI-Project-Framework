# EIOS — U1.1 · CONTRATO DE IMPLEMENTACIÓN — FRONTEND VISUAL CEO

**Estado:** CERRADO — AUTORIZADO PARA IMPLEMENTACIÓN
**Diseño cerrado:** `f19150c043b055f4471a14b11910c5f746476e23`

## 1. Propósito

Materializar una capa visual ejecutiva que permita al CEO introducir una operación y visualizar contexto, evidencia, ejecución y resultados ya producidos por EIOS, sin crear autoridad decisional paralela.

## 2. Frontera

`CEO → U1.1 Visual → U1 Application Boundary → O1`

U1.1 no accede directamente a motores de reglas, TCO, Price Intelligence, QTG, Viability, Negotiation, CRC u otros componentes internos.

## 3. Obligaciones

- Capturar únicamente campos autorizados por U1.
- Presentar estados O1 literalmente y con texto explícito.
- Separar resultado EIOS de decisión humana.
- Presentar evidencia, limitaciones y trazabilidad.
- Mantener identidad, versiones, snapshot y fingerprint como información no editable.
- Mantener escenarios descriptivos sin ranking, score o selección automática.
- Mantener comparación Twin descriptiva.
- Soportar teclado, foco, labels, errores asociados y lectura lógica.
- Ser usable en escritorio y viewport reducido.

## 4. Prohibiciones

No implementar:

- recomendación automática;
- ranking o selección de escenarios;
- aprobación/rechazo automático;
- ejecución automática de compras;
- edición de reglas o parámetros;
- persistencia nueva;
- autenticación/SSO;
- API pública nueva;
- acceso directo a motores;
- score visual que sustituya una autoridad contractual;
- campos paralelos de `decision_version`, `decision_fingerprint` u otras identidades.

## 5. Modelo de presentación

La interfaz trabaja con dos clases de entrada:

1. datos de formulario que pasan por U1;
2. un `DecisionSupportPackage` ya producido, presentado sin recalculación.

La capa visual no modifica el objeto fuente.

## 6. Componentes MVP

- `AppShell`
- `ExecutiveDashboard`
- `OperationForm`
- `EvidencePanel`
- `DecisionContextPanel`
- `ExecutionStatus`
- `ExecutiveResult`
- `ScenarioList`
- `TwinComparison`

## 7. Criterio de aceptación

La materialización es válida cuando las pruebas demuestran captura canónica, rechazo de campos prohibidos, presentación fiel de estados/resultados/evidencia/traza, ausencia de mutación y ausencia de funciones de autoridad decisional paralela.
