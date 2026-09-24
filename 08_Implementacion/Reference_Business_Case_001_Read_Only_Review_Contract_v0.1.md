# Reference Business Case 001 — Read Only Review v0.1

## DISEÑAR

Una página HTML local compara los artefactos terminales JSON de las variantes
`negative` y `qtg-eligible`. Se muestran calidad QTG, ejecución técnica,
secuencia de capacidades, referencias de traza y huellas terminales. La página
no contiene invocadores, JavaScript, formularios, enlaces de acción ni acceso a
admisión operacional.

## AUDITAR

El contrato de arquitectura UI exige presentación sin cálculos de negocio ni
reescritura de evidencias. El visualizador Vertical MVP existente recibe otro
modelo (`VerticalMVPSupportResult`); el terminal de referencia no satisface ese
contrato. El runner de referencia ya emite los dos JSON necesarios.

## DEPURAR

El visor valida huellas terminales, de procedencia y de resultado técnico, y
rechaza violaciones de las invariantes sintéticas. Escapa el contenido dinámico.
`COMPLETED` se identifica expresamente como ejecución técnica y se presenta
separado de la calificación QTG.

## AUDITAR 2

Las pruebas cubren comparación de ambas variantes, manipulación de huella,
declaración operacional aun con huella recalculada, trazas escapadas e identidad
duplicada. Los JSON son la fuente de los datos; la vista no recalcula QTG.

## CERRAR

La vista es una inspección local del material `SYNTHETIC`, con política
`SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, alcance `NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. Una huella válida permite comprobar consistencia
del archivo, pero no autentica su origen ni autoriza decisiones.

## MATERIALIZAR

```powershell
python -m examples.reference_business_case_001 --variant negative --output reference-negative-result.json
python -m examples.reference_business_case_001 --variant qtg-eligible --output reference-result.json
python -m examples.reference_business_case_review --negative reference-negative-result.json --qtg-eligible reference-result.json --output reference-review.html
```

Abrir `reference-review.html` en el navegador local para inspeccionar la
comparación. No se requiere servicio web ni dependencias adicionales.

## CI

Ejecutar `python -m pytest -q tests/test_reference_business_case_review.py` y
la suite del repositorio antes de integrar.
