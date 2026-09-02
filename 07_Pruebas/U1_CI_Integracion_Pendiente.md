# U1 — GATE DE INTEGRACIÓN CI

La validación CI de la rama de diseño se ejecutará mediante el Pull Request hacia `main`, porque el workflow del repositorio está configurado para `pull_request` y `main`.

El gate exige éxito de pytest y de las validaciones SQL existentes antes del merge.

No se declara integración en `main` hasta superar este gate.
