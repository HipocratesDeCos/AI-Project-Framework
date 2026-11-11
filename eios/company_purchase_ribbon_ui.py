"""Reference-led purchase ribbon styling, scoped to purchase presentation."""
CSS='''
[data-view=propuestas] #po-source{display:none}
[data-view=propuestas] .po-ribbons{--ribbon-surface:#fff;--ribbon-chrome:#f8faff;--ribbon-line:#dce4f2;--ribbon-muted:#596b87;--ribbon-ink:#0d1e41;--ribbon-price:#eaf0ff;--ribbon-accent:#1744bf;--ribbon-badge:#eef2fa;position:sticky;top:0;padding:0;margin:0 0 20px;border:1px solid var(--ribbon-line);border-radius:22px;background:var(--ribbon-surface);color:var(--ribbon-ink);box-shadow:0 8px 24px #10264b0a;max-width:100%;overflow:clip}
[data-theme=dark] [data-view=propuestas] .po-ribbons{--ribbon-surface:#121f33;--ribbon-chrome:#0f1b2e;--ribbon-line:#415675;--ribbon-muted:#b5c5df;--ribbon-ink:#e7eefc;--ribbon-price:#20375e;--ribbon-accent:#b5ceff;--ribbon-badge:#243653}
[data-view=propuestas] .po-ribbon-header{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 24px;border-bottom:1px solid var(--ribbon-line);background:var(--ribbon-chrome)}
[data-view=propuestas] .po-ribbon-title{display:grid;grid-template-columns:36px auto;column-gap:12px;align-items:center;white-space:nowrap;min-width:200px;color:var(--ribbon-ink);text-align:left;font-size:14px;letter-spacing:.1em}
[data-view=propuestas] .po-ribbon-title .po-ribbon-pin{grid-row:span 2;box-sizing:border-box;width:36px;height:36px;padding:9px;margin:0;border-radius:11px;background:#0a1a3c;color:white}
[data-view=propuestas] .po-ribbon-title small{grid-column:2;font-size:13px;color:var(--ribbon-muted);letter-spacing:0}
[data-view=propuestas] .po-ribbon-header-meta{display:flex;flex-wrap:wrap;gap:12px 20px;justify-content:flex-end;font-size:14px;color:var(--ribbon-muted);min-width:0}
[data-view=propuestas] .po-ribbon-context-item{display:flex;align-items:center;gap:8px;min-width:0;overflow-wrap:anywhere}
[data-view=propuestas] .po-ribbon-context-item svg{flex-shrink:0}
[data-view=propuestas] .po-ribbon-body{margin:0}
[data-view=propuestas] .po-ribbon-body>summary{display:none}
[data-view=propuestas] .po-identity{display:grid;grid-template-columns:1fr 1.5fr .65fr;align-items:start;gap:20px;padding:22px 24px 10px;border:0;border-radius:0;background:var(--ribbon-surface);min-height:0}
[data-view=propuestas] .po-identity>div{min-width:0}
[data-view=propuestas] .po-identity>div>span:first-child{display:block;margin:0 0 8px;color:var(--ribbon-muted);font-size:12px;letter-spacing:.08em;font-weight:600}
[data-view=propuestas] .po-identity strong{font-family:var(--eios-display);font-size:24px;font-weight:700;line-height:1.4;margin:0;display:inline;overflow-wrap:anywhere}
[data-view=propuestas] .po-ribbon-fiction{display:inline-block;vertical-align:middle;margin-left:9px;border-radius:20px;padding:3px 9px;background:var(--ribbon-badge);color:var(--ribbon-muted);font:600 11px var(--eios-font);letter-spacing:.07em;text-transform:uppercase}
[data-view=propuestas] .po-identity .po-ribbon-sku{display:inline-block;margin-left:12px;border-radius:9px;padding:5px 10px;background:#0a1a3c;color:#fff;font:600 12px var(--eios-font);letter-spacing:.04em}
[data-view=propuestas] .po-metric-ribbon{display:grid;grid-template-columns:.7fr .9fr .7fr 1.65fr 1.2fr 1.15fr;align-items:stretch;gap:0;padding:18px 24px 24px;margin:0;border:0;border-radius:0;background:var(--ribbon-surface);text-align:left;min-height:0}
[data-view=propuestas] .po-metric{border-left:1px solid var(--ribbon-line);padding:8px 15px;min-width:0;text-align:left}
[data-view=propuestas] .po-metric:first-child{border-left:0;padding-left:0}
[data-view=propuestas] .po-metric-label{font-size:12px;letter-spacing:.05em;font-weight:600;color:var(--ribbon-muted);min-height:32px}
[data-view=propuestas] .po-metric-value,[data-view=propuestas] .po-saved-ribbon .po-metric-value{font-family:var(--eios-display);font-size:clamp(30px,3.1vw,46px);font-weight:700;letter-spacing:-.04em;line-height:1.05;margin:0 0 5px;overflow-wrap:anywhere}
[data-view=propuestas] .po-metric-unit{font-size:14px;line-height:1.45;color:var(--ribbon-muted)}
[data-view=propuestas] .po-metric[data-metric=price]{border:1px solid #bed0ff;background:var(--ribbon-price);border-radius:17px;padding:8px 18px}
[data-view=propuestas] .po-metric[data-metric=price] .po-metric-label{color:var(--ribbon-accent)}
[data-view=propuestas] .po-metric[data-metric=discount]{border-left:0;padding-left:20px}
[data-view=propuestas] .po-ribbon-price-line{display:flex;align-items:baseline;gap:6px}
[data-view=propuestas] .po-ribbon-price-line .po-metric-value{min-width:0}
[data-view=propuestas] .po-ribbon-currency{flex-shrink:0;font-family:var(--eios-display);font-size:28px;font-weight:700}
[data-view=propuestas] .po-ribbon-consumption-pending{display:inline-block;margin-top:2px;border-radius:20px;padding:4px 9px;background:#fff1dc;color:#7a3e00;font-size:11px;font-weight:600}
[data-view=propuestas] .po-ribbon-consumption-pending::before{content:'◷ ';font-size:13px}
[data-view=propuestas] .po-ribbon-meta{display:flex;align-items:center;gap:12px;padding:13px 24px;border-top:1px solid var(--ribbon-line);background:var(--ribbon-chrome);font-size:12px;color:var(--ribbon-muted)}
[data-view=propuestas] .po-ribbon-status{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border:1px solid #b6caff;border-radius:20px;background:var(--ribbon-price);color:var(--ribbon-accent);font-size:10px;font-weight:600;letter-spacing:.07em;white-space:nowrap}
[data-view=propuestas] .po-ribbon-status::before{content:'✎';font-size:13px}
[data-view=propuestas] .po-ribbons[data-context=saved] .po-ribbon-status::before{content:'▣'}
[data-view=propuestas] .po-ribbon-source{flex:1;min-width:160px}
[data-view=propuestas] .po-ribbon-meta button{background:transparent;border:0;padding:0;font-weight:600;font-size:13px;text-decoration:none;color:#1553f0;min-height:32px;text-align:left}
[data-view=propuestas] .po-metric-value[data-empty=true]{opacity:.42}
[data-theme=dark] [data-view=propuestas] .po-ribbon-consumption-pending{background:#3f301b;color:#ffd79a}
[data-theme=dark] [data-view=propuestas] .po-ribbon-meta button{color:#b5ceff}
[data-view=propuestas].po-guided .po-step{scroll-margin-top:calc(var(--po-ribbon-height,220px) + 16px)}
[data-view=propuestas].po-guided .po-context{top:calc(var(--po-ribbon-height,220px) + 16px);max-height:calc(100vh - var(--po-ribbon-height,220px) - 32px)}
@media(max-width:1200px){[data-view=propuestas] .po-ribbon-header{padding:14px 18px;flex-wrap:wrap}[data-view=propuestas] .po-ribbon-header-meta{justify-content:flex-start}[data-view=propuestas] .po-identity{padding:18px 18px 8px}[data-view=propuestas] .po-metric-ribbon{padding:14px 18px 18px;grid-template-columns:.7fr .9fr .7fr 1.5fr 1.2fr 1.2fr}[data-view=propuestas] .po-metric{padding:8px 10px}[data-view=propuestas] .po-metric-value,[data-view=propuestas] .po-saved-ribbon .po-metric-value{font-size:34px}[data-view=propuestas] .po-metric-label{font-size:9px}[data-view=propuestas] .po-ribbon-meta{padding:12px 18px}}
@media(max-width:1100px){[data-view=propuestas].po-guided .po-context{position:static;max-height:none}}
@media(max-width:900px){[data-view=propuestas] .po-ribbon-body>summary{display:block;padding:10px 16px;font-size:13px}[data-view=propuestas] .po-ribbon-body[open]{max-height:48vh;overflow:auto}[data-view=propuestas] .po-ribbon-title{min-width:0}[data-view=propuestas] .po-ribbon-header-meta{font-size:11px;gap:8px 16px}[data-view=propuestas] .po-ribbon-header{padding:12px 16px;gap:10px}[data-view=propuestas] .po-identity{grid-template-columns:1fr;gap:12px;padding:12px 16px}[data-view=propuestas] .po-identity>div:last-child{grid-column:auto}[data-view=propuestas] .po-identity strong{font-size:18px}[data-view=propuestas] .po-metric-ribbon{grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:12px 16px}[data-view=propuestas] .po-metric{border:0;padding:8px 0}[data-view=propuestas] .po-metric[data-metric=price]{padding:10px;grid-column:span 2}[data-view=propuestas] .po-metric[data-metric=discount]{padding-left:0}[data-view=propuestas] .po-metric-label{font-size:12px;min-height:26px}[data-view=propuestas] .po-metric-unit{font-size:11px}[data-view=propuestas] .po-ribbon-meta{padding:10px 16px;gap:8px}[data-view=propuestas] .po-ribbon-source{font-size:10px;min-width:150px}[data-view=propuestas].po-guided .po-context{position:static;max-height:none}}
'''

CSS += """
[data-view=propuestas] .po-identity .po-ribbon-supplier-picker{display:block;width:100%;min-width:0;max-width:100%;border:0!important;box-shadow:none!important;background:transparent;color:var(--ribbon-ink,#102748);padding:0 20px 0 0;margin-top:3px;font-family:var(--eios-display);font-size:18px;line-height:1.4;font-weight:400;cursor:pointer;border-radius:0}
[data-view=propuestas] .po-identity .po-ribbon-supplier-picker[hidden],[data-view=propuestas] .po-identity strong[hidden]{display:none!important}
[data-view=propuestas] .po-identity .po-ribbon-supplier-picker:focus-visible{outline:2px solid #1553f0;outline-offset:4px}
[data-view=propuestas] .po-ribbon-supplier-picker option{background:var(--ribbon-surface,#fff);color:var(--ribbon-ink,#102748)}
"""

CSS += "@media(max-width:900px){[data-view=propuestas] .po-identity .po-ribbon-supplier-picker{font-size:12px}}"
