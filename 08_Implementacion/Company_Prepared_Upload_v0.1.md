# Prepared company ZIP upload v0.1

The local company screen now offers an assisted import under **Carga de archivos**:

1. Select a prepared documentary ZIP with `company_manifest.json` at its root.
2. **Comprobar paquete** validates the existing documentary contract, file integrity, source references, canonical carriers and catalogue display identifiers before any database write. The preview shows company, cutoff, document count and record counts.
3. **Importar paquete validado** imports exactly the validated bytes through the existing `CompanyDataStore.import_dataset`, then selects that dataset. Reimporting identical content is idempotent. Prior datasets, proposals and contextual reviews are retained.

For the fictional A Monkey company, select `A_Monkey_Datos_Documentados.zip`. The outer `EIOS_A_Monkey_Carga_Documental_Local.zip` is an installation bundle and is not accepted as a documentary dataset. Extract the inner ZIP first.

A separate ordinary-file reception workflow is described in Company_File_Reception_v0.1.md. It never calls this synthetic-only importer for real data.

The existing input contract remains synthetic-only with `operational_path=FORBIDDEN`. This feature does not parse arbitrary PDF/Excel, perform OCR, prove source truth, create financial evidence, or implement real-company operational admission. Inventory/planning assumptions are separate and are not automatically generated for imported datasets. Missing stock stays missing.

Transport limits: 25 MiB uploaded, 100 MiB total uncompressed, 512 ZIP members; only unencrypted STORED/DEFLATE members. Files are never extracted by user-controlled paths. The exact bytes are retained in a single server-memory preview slot, bound to a random ticket expiring after ten minutes. A new preview invalidates the old ticket; success consumes it. The import revalidates the same bytes before the existing transactional persistence boundary.

`POST /api/import/preview` receives raw ZIP bytes, while `POST /api/import/commit` receives a JSON ticket. Both require the existing local-session token and allowed Host; JSON mutation requests retain their 16 KiB limit. The frontend renders metadata with `textContent`, clears previews when files change and displays validation/import errors explicitly.

Tests cover no-write previews, exact-source preservation, idempotent import, invalid/expired/replaced tickets, malformed ZIP, real-material rejection, incomplete catalogue rejection, size/member limits and existing proposal preservation across a new dataset version. DOM/HTTP verification uses a disposable copy of the fictional-company database, including preview of its 35 documents/1160 records, duplicate import and preservation of a saved test proposal. This does not establish pixel-level browser rendering.
