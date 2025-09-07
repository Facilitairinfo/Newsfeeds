(() => {
  if (window.__fi_loaded) return; window.__fi_loaded = true;

  const style = document.createElement("style");
  style.textContent = `
    #__fi_toolbar{position:fixed;top:0;left:0;right:0;z-index:2147483647;background:#111;color:#fff;font:14px system-ui;padding:6px 10px;display:flex;gap:10px;align-items:center}
    #__fi_hover_overlay{position:absolute;border:2px solid red;background:rgba(255,0,0,.08);pointer-events:none;z-index:2147483645;display:none}
    #__fi_selected_overlay{position:absolute;border:2px solid red;background:rgba(255,255,0,.25);pointer-events:none;z-index:2147483646;display:none}
    #__fi_panel{position:fixed;top:44px;right:12px;z-index:2147483647;background:#000c;color:#fff;padding:6px 8px;border-radius:6px;max-width:42vw;font:12px system-ui}
    #__fi_panel code{display:block;white-space:nowrap;overflow:auto;max-width:38vw}
    html.__fi_mode{scroll-padding-top:50px} body{margin-top:44px !important}
  `;
  document.head.appendChild(style);

  const tb = document.createElement("div");
  tb.id = "__fi_toolbar";
  tb.innerHTML = `
    <label>Mode:
      <select id="__fi_mode">
        <option value="title">Titel</option>
        <option value="date">Datum</option>
        <option value="summary">Samenvatting</option>
      </select>
    </label>
    <button id="__fi_done">Klaar</button>`;
  document.body.appendChild(tb);

  const panel = document.createElement("div");
  panel.id = "__fi_panel";
  panel.innerHTML = `
    <div><strong>Selecties:</strong></div>
    <div>title: <code id="__fi_sel_title">–</code></div>
    <div>date: <code id="__fi_sel_date">–</code></div>
    <div>summary: <code id="__fi_sel_summary">–</code></div>`;
  document.body.appendChild(panel);

  const hover = document.createElement("div"); hover.id="__fi_hover_overlay"; document.body.appendChild(hover);
  const sel = document.createElement("div"); sel.id="__fi_selected_overlay"; document.body.appendChild(sel);

  document.documentElement.classList.add("__fi_mode");

  const modeEl = document.getElementById("__fi_mode");
  const doneBtn = document.getElementById("__fi_done");
  const selTitle = document.getElementById("__fi_sel_title");
  const selDate = document.getElementById("__fi_sel_date");
  const selSummary = document.getElementById("__fi_sel_summary");

  const selections = { title: "", date: "", summary: "" };

  function getUniqueSelector(el) {
    if (!el || !el.tagName) return "";
    if (el.id) return el.tagName.toLowerCase() + "#" + CSS.escape(el.id);
    const parts = [];
    let cur = el, depth = 0;
    while (cur && cur.nodeType === 1 && depth++ < 10) {
      let part = cur.tagName.toLowerCase();
      if (cur.id) { part += "#" + CSS.escape(cur.id); parts.unshift(part); break; }
      let idx = 1, sib = cur;
      while ((sib = sib.previousElementSibling)) { if (sib.tagName === cur.tagName) idx++; }
      part += ":nth-of-type(" + idx + ")"; parts.unshift(part); cur = cur.parentElement;
    }
    return parts.join(" > ");
  }
  function bbox(el){ const r=el.getBoundingClientRect(); return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height}; }
  function renderOverlay(box, overlayEl, show){
    if (!box || !show) { overlayEl.style.display="none"; return; }
    overlayEl.style.display="block";
    overlayEl.style.left=box.x+"px"; overlayEl.style.top=box.y+"px"; overlayEl.style.width=Math.max(1,box.w)+"px"; overlayEl.style.height=Math.max(1,box.h)+"px";
  }

  document.addEventListener("mousemove", (e)=>{
    if (e.target.closest("#__fi_toolbar") || e.target.closest("#__fi_panel")) { renderOverlay(null, hover, false); return; }
    try { renderOverlay(bbox(e.target), hover, true); } catch(_){ renderOverlay(null, hover, false); }
  }, true);

  document.addEventListener("click", (e)=>{
    if (e.target.closest("#__fi_toolbar") || e.target.closest("#__fi_panel")) return;
    e.preventDefault(); e.stopPropagation();
    const el = e.target;
    const mode = modeEl.value;
    const selector = getUniqueSelector(el);
    selections[mode] = selector;
    if (mode==="title") selTitle.textContent = selector;
    if (mode==="date") selDate.textContent = selector;
    if (mode==="summary") selSummary.textContent = selector;
    renderOverlay(bbox(el), sel, true);
  }, true);

  doneBtn.addEventListener("click", ()=>{
    const payload = { type:"FEED_DONE", selections, location: location.href };
    try { window.opener && window.opener.postMessage(payload, "*"); } catch(_) {}
    try { window.parent && window.parent.postMessage(payload, "*"); } catch(_) {}
    console.log("FEED_DONE", payload);
  }, false);

  setTimeout(()=>{
    const hide = [".cookie-banner",".cookie-consent","#cookie",".cc-window",".cookie-wrapper",".cookie-notice",".cookie-popup",".cookies","#cookies"];
    for (const s of hide) { const n = document.querySelector(s); if (n) n.style.display="none"; }
  }, 1200);
})();
