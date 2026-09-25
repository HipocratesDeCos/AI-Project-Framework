# Reference Business Case 001 — Demo Command v0.1

## DISEÑAR

Un comando genera el terminal sintético de las variantes `negative` y
`qtg-eligible` y una vista HTML local para revisarlas. Produce tres archivos
en un directorio nuevo indicado por el usuario.

## AUDITAR

`execute_reference_business_case` ya ejecuta ambas variantes de la empresa
ficticia. `render_review` ya comprueba huellas, procedencia, identidad de las
variantes y límites sintéticos, y compone la vista de solo lectura. El comando
reutiliza exactamente ambas funciones y no introduce otro invocador.

## DEPURAR

Se prepara el paquete fuera del directorio final y se mueve al destino solo
después de producir los dos JSON y el HTML. Si el destino existe, se rechaza
sin sobrescribir archivos locales. El directorio padre debe existir.

## AUDITAR 2

Las pruebas leen los tres archivos, verifican las identidades QTG, huellas
representadas y límites operacionales, y comprueban que un directorio existente
no se sustituye. La repetición compara ambos terminales con nuevas ejecuciones
y detecta una vista HTML alterada sin escribir en el directorio. La CLI se
prueba además desde la raíz del repositorio.

## CERRAR

Este comando empaqueta artefactos de validación de producto de naturaleza
`SYNTHETIC`. Su QTG permanece `SYNTHETIC_TEST_ONLY`, la ruta `FORBIDDEN`,
el efecto `NO_OPERATIONAL_EFFECT` y la autoridad decisional `false`.

## MATERIALIZAR

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo
Invoke-Item .\reference-demo\reference-review.html
```

Para repetir la demostración, elegir otro directorio nuevo. Los comandos
individuales siguen disponibles para inspeccionar o regenerar cada variante.

### Verificación de repetición

```powershell
python -m examples.reference_business_case_demo --verify-dir reference-demo
```

La verificación lee los tres archivos sin modificarlos, valida la revisión
frente a ambos terminales y vuelve a ejecutar las mismas dos variantes con los
fixtures y el código actuales. Exige igualdad completa de ambos terminales y
del HTML representado. Una diferencia indica alteración o cambio de versión o
fixture; no demuestra por sí sola cuál fue la causa. La coincidencia es una
prueba de repetición local, no autenticación de origen ni admisión operacional.

## CI

Ejecutar `python -m pytest -q tests/test_reference_business_case_demo.py`
y la suite completa antes de integrar.
