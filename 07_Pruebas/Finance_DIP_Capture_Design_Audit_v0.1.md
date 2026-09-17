# FIN-DIP-01 — Diseño, auditoría y materialización

Baseline: `c42614c583298003706f9557c65e717b8ce8b67f`.
Contrato: `08_Implementacion/Finance_DIP_Capture_Contract_v0.1.md`.

## DISEÑAR
Captura separada del FinanceBasicInput completo junto con DIP base construido mediante el Centro. Sin modificar módulos cerrados ni ejecutar Finance Basic antes de QTG.

## AUDITAR
Fuentes: FIN-AUTH-01/05/07; Finance Basic v0.3/v0.3.1; Horizon Provenance; DIP-AGG-01; perfil QTG-DIP-G01-FIN; modelos y código finance/provenance, finance/engine, rules/finance y Centro.
Riesgos identificados: snapshot duplicado, contextos parcialmente comparados, defaults que oculten ausencia, mínimos numéricamente iguales con distinta moneda, ejecución del motor para validar input y falsa certificación de pagos de compra.

## DEPURAR
El snapshot procede exclusivamente del FinanceBasicInput; se compara contexto completo. None no se hidrata. Se exige selección explícita y binding de P-FIN-001 y del mínimo suministrado P-FIN-002. Unidad euro implica moneda EUR solo para ese binding. Validación de captura sin ejecución analítica, con límites de pagos/origen explícitos.

## AUDITAR 2
El contrato depurado preserva los modelos existentes y su semántica; campos y referencias completas capturados; no cambia la representación DIP previa. No crea política de umbrales, default financiero, transformación de pagos ni estado QTG. SUPERADA en este alcance.

## CERRAR
Contrato técnico de captura cerrado para materialización, condicionado a verificación física/CI antes de declarar integración. Ningún cierre del productor QTG.

## MATERIALIZAR / CI
Materializado `eios/core/finance_decision_input_package.py`, contrato, este registro y suite de aceptación. Ningún módulo existente modificado.
Revisión del delta: captura completa del FinanceBasicInput; snapshot derivado del mismo input; contexto completo comparado antes de lecturas; selecciones explícitas P-FIN-001/P-FIN-002; None y estados conservados; fingerprint sobre material completo; ningún motor ni gate importado para ejecución.
La validación de unidad monetaria se limita al binding del mínimo P-FIN-002 expresado en euros; no restringe globalmente Finance Basic ni introduce FX.
Resultado de auditoría de materialización: SUPERADA dentro del contrato, sin desviaciones identificadas.
Suite local final: 996 pruebas aprobadas, incluidas 30 nuevas. Los avisos pertenecen a tests existentes.
Las pruebas cubren revalidación, cinco campos contextuales, horizonte y mínimo incorrectos/ausentes, fechas, None y cero, moneda/unidad, sensibilidad de identidad, mutación durante/después de lectura y compatibilidad con la frontera financiera pública existente.
CI Python + SQL pendiente sobre HEAD exacto. CI de documentos anteriores no valida este nuevo delta. Cierre integrado condicionado a CI premerge y postmerge SUCCESS.

## Continuidad
Se completa físicamente la captura financiera del perfil seleccionado; no se certifican pagos de compra ni completitud de la colección empresarial.
QTG sigue en cuarentena. G02, el resto de G03 y G04 permanecen pendientes. Siguiente unidad: contrato de procedencia/asociación de pagos de compra desde una fuente verificable, sin transformar el importe/plazo en flujos por inferencia.
