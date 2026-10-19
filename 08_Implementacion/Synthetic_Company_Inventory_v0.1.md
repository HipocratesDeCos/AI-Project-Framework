# Inventario sintético de la empresa ficticia
Comando explícito desde la raíz del repositorio, con EIOS detenido:
```powershell
python -m eios.company_inventory --db ".\data\a_monkey_documentary.sqlite3"
```
Crea un CSV con separador punto y coma y codificación UTF-8 para Excel en data/Inventario_Sintetico_30092026.csv y guarda los valores en una tabla separada de la misma base. Después iniciar la pantalla habitual y recargar el navegador.

Usa exactamente los códigos y unidades de los artículos del dataset elegido. Fecha: la del corte documental (30/09/2026 en A Monkey). Por código ordenado, alterna tres escenarios: sin existencias; disponibilidad intermedia; disponibilidad mayor. Para palets: físico/reservado 0/0, 3/1, 6/2. Para otras unidades documentadas: 0/0, 30/5, 60/10. Son enteros en la unidad original, sin convertir envases ni palets.

Estos valores son NUEVOS SUPUESTOS autorizados para el caso sintético. No proceden de un recuento físico, de compras/ventas ni se presentan como conciliados con el balance. La pantalla identifica su origen y fecha. No se altera el stock null del expediente original, ni se crean compras ni saldos. La demanda, el stock de seguridad y los pedidos pendientes siguen sin confirmación; inventario no equivale a recomendación.

Carga idempotente: repetir exporta los mismos valores sin duplicarlos. Se rechaza sobrescribir un inventario distinto. Si hay varias versiones, indicar --dataset-id. El CSV es una exportación; editarlo no actualiza la base automáticamente. Conservar la base actualizada para trasladar las propuestas e inventario.
