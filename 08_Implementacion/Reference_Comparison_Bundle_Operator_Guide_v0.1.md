# EIOS — Guía para generar la comparación sintética · v0.1

Esta guía parte de la raíz de `C:\proyectos\AI-Project-Framework` en PowerShell. El paquete reúne dos empresas ficticias para revisar resultados de prueba. No utiliza documentos empresariales reales ni autoriza una compra.

## 1. Actualizar el código

```powershell
cd C:\proyectos\AI-Project-Framework
git switch main
git pull --ff-only origin main
```

Si `git pull` informa de cambios locales que impiden avanzar, conserve esos archivos y resuelva ese estado antes de continuar. No borre los paquetes generados para actualizar el código.

## 2. Generar el paquete en una carpeta nueva

```powershell
python -m examples.reference_business_case_comparison_bundle --output-dir reference-comparison-2026-09-27-01
```

Elija otro nombre, por ejemplo con el sufijo `-02`, si esa carpeta ya existe. El comando no sobrescribe un directorio previo. Crea `comparison.html`, `case-001` y `case-002` en la carpeta indicada.

## 3. Verificar y abrir

```powershell
python -m examples.reference_business_case_comparison_bundle --verify-dir reference-comparison-2026-09-27-01
Invoke-Item .\reference-comparison-2026-09-27-01\comparison.html
```

La primera orden comprueba el inventario, repite ambos casos con el código y los datos de prueba actuales y compara el HTML generado. No modifica el paquete. La segunda abre la página inicial en el navegador.

| Archivo | Para qué sirve |
|---|---|
| `comparison.html` | Presenta las diferencias principales y enlaza las dos revisiones. |
| `case-001/reference-buyer-preview.html` | Explica las dos variantes de calidad de entrada de la primera empresa ficticia. |
| `case-002/reference-review.html` | Explica el resultado parcial y lo que queda sin determinar en la segunda empresa ficticia. |

Las páginas se pueden leer localmente, sin servidor. Los JSON de cada carpeta conservan los resultados y observaciones verificables; las páginas son vistas de solo lectura.

## 4. Interpretar el resultado

«Apta para esta prueba» califica la entrada sintética; «completada» o «completada parcialmente» describe la ejecución técnica. La fiabilidad del proveedor del caso 002 sigue sin determinarse. Ninguno de esos estados aprueba una compra. Ambos expedientes permanecen `SYNTHETIC`, con política `SYNTHETIC_TEST_ONLY`, ruta operacional `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT` y autoridad decisional `false`.

Un HTML generado antes de actualizar `main` no se reescribe solo. Genere otra carpeta para ver la versión nueva; una verificación que falla después de actualizar puede indicar que el paquete antiguo ya no coincide con el código o los datos de prueba actuales, sin identificar por sí sola cuál cambió. La verificación tampoco autentica documentos externos.
