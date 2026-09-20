# EIOS-BL-005 — Depuración

Se incorporan A1–A8 con las siguientes decisiones:

1. sustituir “QTG bloqueado” por dos estados separados:
   - `PROJECTION_ONLY / SYNTHETIC_TEST` cerrado y E2E probado;
   - `PROJECTION_ONLY / OPERATIONAL` bloqueado por expediente operacional ausente;
2. registrar `DIP-AGG-01` como carrier seleccionado, no como trust seal;
3. registrar material envelope, productor, receipt y consumer por sus garantías reales;
4. registrar que bundle/completitud no predeterminan `QualityTrustResult`;
5. preservar Stage 2/VF y Decision Twin dependiente como cuarentenas independientes;
6. preservar NI/Ladder sin atribuir provenance a la mera presencia del invoker;
7. excluir cualquier afirmación de autenticidad externa, atomicidad multi-parámetro o decisión empresarial;
8. fijar el SHA formal anterior a la materialización documental del propio baseline.

No se modifica código, SQL, Rules, parámetros, motores ni APIs.
