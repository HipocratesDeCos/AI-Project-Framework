# EIOS — Demostración sintética de compras v0.1

## DISEÑAR → AUDITAR

Se materializa una vista de lectura local, separada de `reference-review.html`.
Parte de un directorio producido por `examples.reference_business_case_demo`.
La frontera y el inventario de autoridades están en
`Reference_Buyer_Synthetic_Preview_Boundary_Audit_v0.1.md`.

## DEPURAR → AUDITAR 2

Antes de proyectar datos, se ejecuta `verify_reference_demo`: valida ambas
variantes, ocho pares opcionales de capturas, bindings relacionados, HTML
técnico y repetición del fixture exacto. La vista escapa contenido dinámico,
mantiene un aviso sintético visible y carece de formularios, scripts, enlaces
y acciones. Muestra valores solo cuando están presentes; no calcula reglas,
ranking, precio objetivo ni decisiones de compra. Un paquete incompleto o
alterado impide la exportación.

## CERRAR → MATERIALIZAR

```powershell
cd C:\proyectos\AI-Project-Framework
python -m examples.reference_business_case_buyer_preview --demo-dir reference-demo-full --output reference-demo-full\reference-buyer-preview.html
Invoke-Item .\reference-demo-full\reference-buyer-preview.html
```

El comando no reemplaza un archivo existente. `reference-buyer-preview.html`
es una **demostración ficticia de lectura**, no la interfaz operacional que
usaría una empresa cliente. `APTO`, `COMPLETED`, `AUTHORIZED`, los importes y
el consolidado CRC se explican con sus límites de procedencia. La ruta sigue
`FORBIDDEN`, el efecto `NO_OPERATIONAL_EFFECT` y la autoridad decisional
`false`.

## CI

`tests/test_reference_business_case_buyer_preview.py` verifica la vista
completa, el determinismo, ausencia de acciones, ausencia de capturas
opcionales y rechazo de paquetes alterados. Ejecutar la suite antes de
integración.
