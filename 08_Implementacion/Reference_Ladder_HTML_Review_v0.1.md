# EIOS — Revisión HTML de Negotiation Ladder v0.1

**Base:** `main @ 0350948e3e69aa990d4556d67a6291ab4a85e855`  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## DISEÑAR

Presentar en la revisión HTML los JSON Ladder ya exportados para ambas
variantes, sin crear contenido negociador ni cambiar el terminal.

## AUDITAR

La captura de la PR #366 y la exportación de la PR #367 verifican fuentes
C0-bound, estructura, huellas y repetición. La autoridad del fixture es
ficticia. La posición de un paso describe el orden de representación, no una
instrucción para contactar ni negociar con un proveedor.

## DEPURAR

`render_review` exige y valida ambas observaciones antes de construir HTML.
Muestra posición, tipo y referencia de fuente por paso, número de
transiciones y rutas. Escapa todos los valores dinámicos. Expone que la
reproducción NI interna de Ladder no prueba identidad con el invocador NI
separado ni derivación causal del contenido desde C0.

## AUDITAR 2

La demo pasa los sidecars a `render_review` y `--verify-dir` coteja el HTML
además de repetir las capturas y terminales. La vista individual acepta la
pareja `--negative-negotiation-ladder` y
`--qtg-eligible-negotiation-ladder`. Se cubren modos aislado y combinado,
pareja faltante, contenido alterado y huellas terminales sin cambios.

## CERRAR

`SYNTHETIC`, `SYNTHETIC_TEST_ONLY`, `FORBIDDEN`,
`NO_OPERATIONAL_EFFECT`, `decision_authority=false`. La presentación es
descriptiva y de solo lectura.

## MATERIALIZAR

Tras actualizar `main`, crear un directorio nuevo desde la raíz del
repositorio:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-ladder-html --with-negotiation-ladder
Invoke-Item .\reference-demo-ladder-html\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-ladder-html
```

## CI

Suite completa y CI de la PR requeridas antes de integrar.
