# Planificación sintética y cobertura STK
Ejecutar con la pantalla detenida:
```powershell
python -m eios.company_planning --db ".\data\a_monkey_documentary.sqlite3"
python -m eios.company_app --db ".\data\a_monkey_documentary.sqlite3"
```
Requiere el inventario sintético previamente creado. El comando no crea inventario ni compras automáticamente.
Se crean nuevos supuestos en tabla separada, sin alterar el expediente documental: para palets, demanda adicional 0,1 palets/día, plazo 14 días y seguridad 1 palet; para otras unidades documentadas, 1 unidad documentada/día, plazo 7 días y seguridad 10 unidades documentadas. La demanda excluye las reservas existentes para no descontarlas dos veces. Vigencia: fecha de corte más 30 días naturales (hasta 30/10/2026 en este caso). No se deduce demanda de facturas ni se activa una política de cliente real.

La pantalla llama a calculate_stock_availability, use_authorized_forecast y calculate_coverage del motor STK existente, con identidad de dataset/artículo/empresa y referencias de los supuestos. KNOWN corresponde a los valores explícitos del escenario sintético, no a evidencia real. No se cambia el motor ni se promueve admisión, QTG o autoridad decisional.

Cobertura = stock disponible / demanda diaria adicional; demanda cero produce UNBOUNDED y dato faltante no se interpreta como cero. Plazo y seguridad se muestran como contexto; no se presentan como evaluación de reglas ni cantidad recomendada. Pedidos pendientes de recibir: UNKNOWN, nunca lista vacía confirmada. No se ejecutan FIN, PRICE, CRC ni el Decisor en esta pantalla.

La base y propuestas existentes se conservan. Repetir la creación no duplica; no se sobrescriben valores distintos. Si hay varios datasets, usar --dataset-id. Los resultados se refieren a la fecha de corte, no a la fecha actual del ordenador.
