# Company screen layout v0.1

The local `python -m eios.company_app --db <existing-db>` screen follows the approved EIOS visual reference: navy sidebar with white outline icons, dark search bar, light background, article and supplier panels, historical reference alongside proposal entry.

Navigation includes Inicio, Propuestas, Cartera de Proveedores, Cartera de Clientes, Stock and Carga de archivos. The first five show data from the selected documentary dataset. Carga de archivos explicitly states that browser upload is not yet available. Global search locates documented articles, suppliers and customers; article/supplier results select the corresponding proposal context. SKU search uses the documented article ID; no family taxonomy is inferred.

Article reference shows net effective price, quantity, date and invoice for the unique latest historical line. Ties remain unresolved and direct the user to the full history. Availability comes only from the separate synthetic inventory, with unit, date and provenance visible. Missing inventory is not zero. Family, locality and commercial status remain unavailable. PVP, freight and other costs are not inferred or submitted.

The action remains **Guardar propuesta**, pending evaluation, rather than implying that a decision engine is connected. Existing proposal schema, validations, session protection and database are preserved. Only the read API gains dataset-scoped customer records. No order, stock movement or treasury movement is generated.

Validation: existing proposal/history/inventory/planning checks, customer isolation across documentary versions, JavaScript syntax, and DOM interaction against a disposable copy of the fictional-company database (navigation, search, last purchase, inventory, proposal save and persisted total). DOM verification does not establish pixel-level browser rendering.
