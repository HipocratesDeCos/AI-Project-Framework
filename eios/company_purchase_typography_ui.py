"""Bundled IBM Plex Sans and Bricolage Grotesque with reference-led negotiation styling."""
from eios.company_font_assets import CSS as FONT_ASSET_CSS

CSS=FONT_ASSET_CSS+'''
:root{--eios-font:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;--eios-display:"Bricolage Grotesque","IBM Plex Sans",sans-serif}
#purchase-comparison{font-family:var(--eios-font)}
h1,h2,h3,h4,.po-metric-value,.po-column-total strong,.po-alt-total,.po-alt-baseline strong{font-family:var(--eios-display)!important;font-variant-numeric:tabular-nums}
body{font-family:var(--eios-font);font-size:15px;-webkit-font-smoothing:antialiased}button,input,select,textarea{font-family:inherit}#po-conditions{font-family:var(--eios-font)!important}input,select,.metric strong,.po-metric-value{font-variant-numeric:tabular-nums}
#po-conditions .po-negotiation-scroll{background:#fff;border:1px solid #dce5f1;border-radius:16px;padding:3px 8px;box-shadow:0 3px 14px #19375c05}
#po-conditions .po-draft-negotiation{grid-template-columns:minmax(135px,.85fr) minmax(150px,1fr) minmax(185px,1.15fr) minmax(150px,1fr);min-width:680px;grid-template-rows:repeat(12,auto)}
#po-conditions .po-draft-column{grid-row:span 12;padding:8px 12px;border:0;background:transparent;color:#102a43}
#po-conditions .po-label-column{background:transparent}
#po-conditions .po-draft-column[aria-label="MI PROPUESTA"]{background:#eaf0ff;border:1px solid #b8caff;border-radius:15px;box-shadow:0 3px 15px #2d67da09}
#po-conditions .po-draft-column>header{background:transparent;border:0;border-radius:0;padding:8px 2px;margin:0}
#po-conditions .po-draft-column>header h3{font-size:12px;font-weight:700;letter-spacing:.075em;line-height:1.4;min-height:30px;margin:0!important}
#po-conditions .po-draft-column[aria-label="MI PROPUESTA"]>header h3{color:#1055d9}
#po-conditions .po-draft-column>header p{font-size:11px;line-height:1.45;min-height:0;margin:5px 0;color:#577092}
#po-conditions .po-label-column>header{color:#73849b;font-size:11px;letter-spacing:.07em}
#po-conditions .po-check{font-size:11px!important;line-height:1.35;min-height:24px;gap:6px}
#po-conditions .po-check input{width:14px;min-width:14px;height:14px;accent-color:#1d5de1}
#po-conditions .po-aligned-cell{border-top:1px solid #e2e9f3;min-height:48px;padding:7px 0}
#po-conditions .po-row-label{font-size:14px;line-height:1.35;font-weight:650;color:#142c46}
#po-conditions .po-draft-column input:not([type=checkbox]),#po-conditions .po-draft-column select{font-family:var(--eios-font)!important;font-size:15px!important;min-height:38px!important;height:38px;padding:7px 10px!important;border:1px solid #cfdbeb;border-radius:10px;background:#fff;color:#142c46;box-shadow:none;margin-top:0}
#po-conditions .po-draft-column input:focus-visible,#po-conditions .po-draft-column select:focus-visible{outline:2px solid #5d8af5;outline-offset:1px;border-color:#5d8af5}
#po-conditions .po-draft-column[aria-label="PROPUESTA DEL PROVEEDOR"] input:placeholder-shown,#po-conditions .po-draft-column[aria-label="PROPUESTA DEL PROVEEDOR"] input:disabled{border-style:dashed;background:#fff}
#po-conditions .po-draft-column input:disabled,#po-conditions .po-draft-column select:disabled{color:#637b9b}
#po-conditions .po-draft-column .po-net{font-size:16px;font-weight:700;color:#102a43}
#po-conditions .po-book-value{font-size:15px;line-height:1.4;font-weight:400}
#po-conditions [aria-label="Oferta original del libro"] [data-condition-row=shipping],#po-conditions [aria-label="Oferta original del libro"] [data-condition-row=due]{background:transparent}
#po-conditions .po-book-disabled{background:#f5f8fd!important;border-color:#e1e8f1!important}
#po-conditions .po-aligned-cell[data-condition-row=discount] label:first-child{flex-basis:58px}
#po-conditions .po-aligned-cell[data-condition-row=discount] select{font-size:12px!important;padding:5px!important}
#po-conditions .po-column-details>summary{font-size:11px;color:#416691}
#po-conditions .po-aligned-cell[data-condition-row=tax-base]{border-top:2px solid #52627f;margin-top:4px}
#po-conditions .po-tax-value{font-size:15px;font-weight:400;font-variant-numeric:tabular-nums;color:#264463}
#po-conditions .po-row-label[data-condition-row=tax-base],#po-conditions .po-row-label[data-condition-row=tax-amount]{font-weight:400;color:#496486}
#po-conditions .po-column-total,#po-conditions .po-row-label[data-condition-row=total]{background:transparent;border-radius:0;border-top:1px solid #cfdced;padding:12px 0!important}
#po-conditions .po-column-total strong{font-size:clamp(21px,1.8vw,25px);font-weight:750;line-height:1.3;letter-spacing:-.02em;color:#102a43}
#po-conditions .po-row-label[data-condition-row=total]{font-size:12px;font-weight:700;letter-spacing:.04em}
#po-conditions .po-difference{font-size:11px;padding:8px;border-radius:8px;margin:0!important;align-self:stretch}
#po-conditions .po-difference strong{font-size:19px;line-height:1.25}
#po-conditions .po-shared-conditions{background:#f5f8fe;border-color:#dce5f1}
#po-conditions .po-shared-conditions input:not([type=checkbox]){font-size:15px!important}
#po-conditions .po-condition-calendar,#po-conditions .po-calendar-button{height:34px;top:2px;color:#29415d}
#po-conditions .po-condition-date>input{padding-right:34px!important}
@media(max-width:1100px){#po-conditions .po-draft-column{grid-row:span 12}}
'''
