# EIOS — Revisión HTML de la simulación ficticia 002 v0.1

**Resultado:** el paquete técnico 002 puede incluir una página HTML local
de solo lectura. Presenta primero el estado parcial y sus causas, después
la compra ficticia y seis bloques breves de resultados. No sustituye los
nueve JSON ni constituye una interfaz de decisión empresarial.

## DISEÑAR → AUDITAR

La vista se genera a partir del terminal y las ocho observaciones de la
misma ejecución. Antes de renderizar valida cada observación contra el
terminal. Los datos variables se escapan para HTML; no hay JavaScript ni
recursos externos. Mantiene juntos el término técnico y su explicación:

| Etiqueta | Explicación visible |
|---|---|
| `APTO / ALTA` | Calidad de la proyección sintética; no autoriza una compra. |
| `PARTIALLY_COMPLETED` | Terminó la secuencia con fiabilidad del proveedor sin determinar. |
| `INFORMACIÓN INSUFICIENTE` | Falta vincular formalmente un requisito C0; no se oculta tras el estado de la capacidad. |
| `FORBIDDEN` | Sin ruta ni efecto operacional, ni autoridad decisional. |

## DEPURAR → AUDITAR 2

`--with-review` crea `reference-review.html` junto a los nueve JSON. La
verificación repite el caso 002 y compara también el HTML exacto; si se
altera el texto de la revisión, se rechaza el paquete. Sin la opción, el
runner mantiene su formato anterior de nueve JSON. La prueba focalizada
de runner y fuentes 002 dio 20 resultados satisfactorios.

## CERRAR → MATERIALIZAR → CI

Desde la raíz del repositorio, en PowerShell, después de actualizar `main`:

```powershell
python -m examples.reference_business_case_002 --output-dir reference-demo-002-visual --with-review
python -m examples.reference_business_case_002 --verify-dir reference-demo-002-visual
Invoke-Item .\reference-demo-002-visual\reference-review.html
```

La carpeta debe ser nueva. El HTML muestra una empresa **ficticia**; ni
`AUTHORIZED` del contenido negociador ni la etiqueta QTG conceden mandato
real. Se conservan
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Integración sujeta a CI de PR.
