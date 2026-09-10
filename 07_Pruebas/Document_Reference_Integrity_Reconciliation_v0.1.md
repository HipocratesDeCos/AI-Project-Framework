# EIOS — Reconciliación de integridad de referencias documentales v0.1

**Estado:** CERRADO — MATERIALIZADO — INTEGRADO EN `main` — CI VALIDADO
**Baseline:** `b56d3acc8caa8fbe82adbacb8d296d230691d293`
**Ámbito:** navegación documental activa y prueba de no regresión

## 1. DISEÑAR

Reconciliar referencias que presentan como actuales documentos inexistentes, sin crear fuentes nuevas ni alterar la autoridad o semántica de los conceptos afectados.

Alcance:

- retirar del Manual y Project Context la ruta obsoleta de un Assurance Framework independiente;
- conservar Assurance como principio transversal sujeto a la Salvaguarda, la Matriz de Autoridad y las fuentes especializadas vigentes;
- retirar del Framework Map el archivo de organización vacío y eliminado;
- verificar automáticamente que los inventarios actuales 00–08 resuelven a archivos existentes y que la navegación activa no recupera las referencias retiradas.

## 2. AUDITAR

Evidencia histórica:

- `39381c5` retiró la autoridad asignada al archivo independiente de Assurance en la Matriz de Autoridad;
- `e74757e` retiró la misma referencia de Project Governance y añadió la obligación de actualizar referencias a documentos formalmente retirados;
- `EIOS-BL-001` registró la retirada como reconciliación validada y no autorizó un contrato independiente de Assurance;
- `d98bf89` eliminó `03_LEEME_Como_se_organiza_EIOS.md`; su historial demuestra que solo contenía una línea vacía;
- Charter y Salvaguarda conservan Assurance como concepto transversal vigente.

Hallazgo: Manual, Project Context y Framework Map mantenían referencias de existencia incompatibles con el historial y el árbol actual.

## 3. DEPURAR

- Se corrigen los árboles documentales de Manual y Project Context.
- Se sustituye la atribución a un archivo inexistente por la frontera de autoridad vigente, sin crear una fuente paralela.
- Se elimina del inventario actual del Framework Map el archivo vacío retirado.
- Se materializa `tests/test_document_reference_integrity.py`.

## 4. AUDITAR 2

Resultado:

- `16 passed` en la prueba específica de navegación, inventario y ausencia de documentos retirados;
- `281 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- ninguna modificación en código ejecutable, SQL, reglas, parámetros o contratos de implementación;
- STK permanece fuera de alcance y bloqueado por autoridad cuantitativa.

## 5. CERRAR

La unidad queda cerrada cuando todos los controles de Auditoría 2 sean satisfactorios. La posible creación futura de un Assurance Framework independiente requeriría autoridad y ciclo propios; no se infiere de esta reconciliación.

## 6. MATERIALIZAR

La materialización se limita a tres correcciones de navegación, una aclaración de frontera y una prueba automatizada. No modifica el comportamiento empresarial de EIOS.

## 7. CI

La validación local reproduce el job Python del workflow vigente.

- Materialización: `f8be2a3be9f1f3ec0b149aa3728236c7fb77ada4`.
- Pull request: #40.
- CI del head materializado: run `34519581298` — SUCCESS.
- Integración en `main`: `a6d5fee403d8f929ab776736c5c863c006d0d0d1`.
- CI post-merge: run `34519733041` — SUCCESS.

La unidad queda validada por CI sobre el commit materializado y sobre el merge efectivo en `main`.
