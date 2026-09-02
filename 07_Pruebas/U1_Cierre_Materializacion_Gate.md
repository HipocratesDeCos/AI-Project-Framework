# EIOS — U1 · MATERIALIZACIÓN / GATE CI

**Estado:** MATERIALIZADO EN RAMA · PENDIENTE CI DE INTEGRACIÓN

Baseline: `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`

La Application Boundary U1 y sus pruebas están materializadas en `design/u1-ceo-frontend`.

El workflow existente se activa mediante Pull Request y ejecuta la batería de pytest y validaciones SQL. La integración en `main` queda condicionada a resultado SUCCESS.

No se declara CI verde ni merge hasta disponer del resultado efectivo del workflow.
