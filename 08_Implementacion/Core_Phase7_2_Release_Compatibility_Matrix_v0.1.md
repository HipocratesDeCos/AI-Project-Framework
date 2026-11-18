# EIOS — F7.2 · RELEASE COMPATIBILITY MATRIX

**Fecha:** 18/11/2026  
**Base:** `main @ f4e0b5f112abb109b85ea93ef57502e3840bc222`

## 1. OBJETIVO

F7.1 fijó la API pública actual. F7.2 fija ahora **qué combinación exacta de releases del Motor está certificada para convivir**.

El objetivo es impedir que un cambio de versión, una mezcla parcial de paquetes o una interpretación automática de SemVer se conviertan en una compatibilidad no demostrada.

## 2. POLÍTICA

La matriz aplica:

`DEFAULT = REJECT_UNLISTED`

Por tanto:

- una combinación no listada no es compatible;
- una combinación parcialmente especificada no es compatible;
- una mezcla de versiones no se infiere compatible;
- SemVer no concede compatibilidad;
- instalar correctamente no equivale a estar certificado.

## 3. COMBINACIÓN CERTIFICADA ACTUAL

La única combinación neutral certificada en F7.2 es:

- `eios-kernel==0.1.0`
- `eios-input-contracts==0.1.0`
- `eios-capability-catalog==0.1.0`
- `eios-catalog-governance==0.1.0`

Se vincula expresamente a la baseline F7.1 y a evidencia previa de portabilidad, instalación externa y cierre F6.

## 4. QUÉ OCURRIRÁ CON 0.2.0

Ni:

`0.2.0 / 0.2.0 / 0.2.0 / 0.2.0`

ni:

`0.2.0 / 0.1.0 / 0.1.0 / 0.1.0`

son compatibles por defecto.

Para admitir una nueva combinación será necesario aportar, como mínimo:

1. baseline pública de la release candidata;
2. grafo exacto de dependencias;
3. instalación limpia;
4. regresión de consumidores existentes;
5. regresión del tercer dominio;
6. certificación Linux;
7. certificación Windows Python 3.12;
8. prueba de que no se amplía autoridad operacional.

## 5. GATE

`tools/verify_f7_2_release_compatibility.py` verifica:

- que la matriz solo certifique combinaciones expresas;
- que la combinación certificada coincida exactamente con los `pyproject.toml`;
- que coincida con las versiones de F7.1;
- que no se eleve autoridad;
- que las combinaciones negativas sigan rechazadas;
- que cualquier cambio de versión sin evidencia rompa CI.

## 6. LÍMITES

F7.2 no crea todavía una segunda release real.

Por tanto, no demuestra compatibilidad `0.1.0 → 0.2.0`; demuestra algo previo y necesario: **que una futura 0.2.0 no podrá proclamarse compatible sin evidencia explícita**.

La migración real, cuando exista una release candidata, pertenece a una unidad posterior.

## 7. AUTORIDAD

Sin cambios:

- `production_authorized=false`
- `decision_authority=false`
- `operational_path=FORBIDDEN`

## 8. CRITERIO DE CIERRE

F7.2 queda cerrada si:

- la matriz exacta pasa;
- combinaciones mezcladas y futuras no demostradas son rechazadas;
- cambios de versión sin evidencia fallan;
- Python/SQL y F4–F7.1 permanecen verdes;
- Windows 3.12 permanece verde;
- no se modifica `eios/`;
- PR y CI post-merge son verdes sobre SHA exactos.
