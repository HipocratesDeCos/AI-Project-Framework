# EIOS — Comparación de lectura de los casos sintéticos 001 y 002 v0.1

## DISEÑAR → AUDITAR

Los runners cerrados generan paquetes distintos: el 001 contiene dos variantes
de una empresa y el 002 una segunda empresa ficticia. La comparación selecciona
solo la variante QTG apta del 001 y el caso 002. No compara el caso negativo 001
como si fuese otra empresa. Ambos terminales conservan `SYNTHETIC`,
`SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, `NO_OPERATIONAL_EFFECT` y autoridad falsa.

La diferencia probada es descriptiva: el 001 terminó su secuencia y presenta
fiabilidad favorable **en sus datos ficticios**; el 002 terminó parcialmente
porque no hay hechos suficientes para determinar esa fiabilidad. `APTO / ALTA`
de QTG no decide ninguna compra. Los importes de empresas diferentes no se
ordenan ni convierten en recomendaciones.

## DEPURAR → AUDITAR 2

La vista requiere que `verify_reference_demo` y
`verify_reference_business_case_002` repitan y validen cada paquete antes de
leer sus terminales y observaciones. Exige la captura de riesgo del proveedor
en el 001. Escapa el contenido dinámico, carece de scripts y presenta la
limitación decisional antes de los datos. El HTML se puede verificar de nuevo
por igualdad exacta con ambos paquetes; una alteración de cualquiera de ellos
impide la comparación.

## CERRAR → MATERIALIZAR → CI

Desde la raíz del repositorio, primero actualizar `main` y crear carpetas
**nuevas** con el código actual. Un paquete 001 anterior puede incluir una
vista de comprador que ya no coincida con su repetición exacta; en tal caso
`verify_reference_demo` lo rechaza y la comparación no se genera.

```powershell
git pull --ff-only origin main
python -m examples.reference_business_case_demo --output-dir reference-compare-001 --with-supplier-risk --with-buyer-preview
python -m examples.reference_business_case_002 --output-dir reference-compare-002 --with-review
python -m examples.reference_business_case_demo --verify-dir reference-compare-001
python -m examples.reference_business_case_002 --verify-dir reference-compare-002
python -m examples.reference_business_case_comparison --case-001-dir reference-compare-001 --case-002-dir reference-compare-002 --output reference-compare-new.html
python -m examples.reference_business_case_comparison --case-001-dir reference-compare-001 --case-002-dir reference-compare-002 --verify reference-compare-new.html
Invoke-Item .\reference-compare-new.html
```

El paquete 001 debe incluir `--with-supplier-risk`; el 002 puede incluir su
revisión HTML, pero no es imprescindible. Cada carpeta y el archivo de salida
deben tener nombres todavía inexistentes. Ejecutar `--verify` antes de
`--output` no crea el HTML.
La comparación es una lectura local; no modifica los paquetes de origen ni
abre la ruta operacional.
