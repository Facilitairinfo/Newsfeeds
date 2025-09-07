(() => {
  if (window.__fi_loaded) return; window.__fi_loaded = true;

  // ---------- Styles ----------
  const style = document.createElement("style");
  style.textContent = `
    #__fi_toolbar{
      position:fixed;top:0;left:0;right:0;z-index:2147483647;background:#111;color:#fff;
      font:14px system-ui;padding:6px 10px;display:flex;gap:10px;align-items:center;
      box-shadow:0 2px 6px rgba(0,0,0,.25)
    }
    #__fi_toolbar select, #__fi_toolbar button { font-size:13px }
    #__fi_panel{
      position:fixed;top:44px;right:12px;z-index:2147483647;background:#000c;color:#fff;
      padding:8px 10px;border-radius:6px;font:12px system-ui;backdrop-filter:blur(4px);max-width:42vw
    }
    #__fi_panel code{display:block;white-space:nowrap;overflow:auto;max-width:40vw}
    .__fi_badge{display:inline-block;background:#222;border:1px solid #555;border-radius:4px;padding:2px 6px;margin:2px 4px 0 0}
    html.__fi_mode{scroll-padding-top:54px} body{margin-top:44px !important}

    /* Hover marker */
    #__fi_hover_overlay{
      position:absolute;border:2px solid red;background:rgba(255,0,0,0.08);
      pointer-events:none;z-index:2147483645;display:none
    }
    /* Selected item (eerste item) */
    #__fi_item_overlay{
      position:absolute;border:2px solid #ffd000;background:rgba(255,208,0,0.14);
      pointer-events:none;z-index:2147483646;display:none
    }
    /* Alle item-containers */
    .__fi_item_outline{
      position:absolute;border:2px dashed #ffd000;background:transparent;
      pointer-events:none;z-index:2147483646;display:block
    }
    /* Field previews over ALLE items */
    .__fi_field_overlay{
      position:absolute;border:2px solid limegreen;background:rgba(0,255,0,0.18);
      pointer-events:none;z-index:2147483646;display:block
    }
  `;
  document.head.appendChild(style);

  // ---------- Toolbar + Panel ----------
  const tb = document.createElement("div");
  tb.id = "__fi_toolbar";
  tb.innerHTML = `
    <label>Mode:
      <select id="__fi_mode">
        <option value="item">Item</option>
        <option value="title">Titel</option>
        <option value="date">Datum</option>
        <option value="summary">Samenvatting</option>
        <option value="link">Link</option>
        <option value="image">Afbeelding</option>
      </select>
    </label>
    <button id="__fi_preview">Preview</button>
    <button id="__fi_clear">Wissen</button>
    <button id="__fi_done">Klaar</button>
    <span style="margin-left:auto;opacity:.8">FI Selector actief</span>
  `;
  document.body.appendChild(tb);

  const panel = document.createElement("div");
  panel.id = "__fi_panel";
  panel.innerHTML = `
    <div><strong>Selecties:</strong></div>
    <div class="__fi_badge">item: <code id="__fi_item_code">–</code></div>
    <div class="__fi_badge">title: <code id="__fi_title_code">–</code></div>
    <div class="__fi_badge">date: <code id="__fi_date_code">–</code></div>
    <div class="__fi_badge">summary: <code id="__fi_summary_code">–</code></div>
    <div class="__fi_badge">link: <code id="__fi_link_code">–</code></div>
    <div class="__fi_badge">image: <code id="__fi_image_code">–</code></div>
    <div style="margin-top:6px;opacity:.85">Matches: <span id="__fi_counts">–</span></div>
  `;
  document.body.appendChild(panel);

  // ---------- Overlays ----------
  const hoverOverlay = document.createElement("div");
  hoverOverlay.id = "__fi_hover_overlay";
  document.body.appendChild(hoverOverlay);

  const itemOverlay = document.createElement("div");
  itemOverlay.id = "__fi_item_overlay";
  document.body.appendChild(itemOverlay);

  let itemOutlines = [];   // alle item-containers
  let fieldOverlays = [];  // alle field matches

  // ---------- Elements ----------
  document.documentElement.classList.add("__fi_mode");
  const modeEl = document.getElementById("__fi_mode");
  const previewBtn = document.getElementById("__fi_preview");
  const clearBtn = document.getElementById("__fi_clear");
  const doneBtn = document.getElementById("__fi_done");
  const codeEls = {
    item: document.getElementById("__fi_item_code"),
    title: document.getElementById("__fi_title_code"),
    date: document.getElementById("__fi_date_code"),
    summary: document.getElementById("__fi_summary_code"),
    link: document.getElementById("__fi_link_code"),
    image: document.getElementById("__fi_image_code"),
  };
  const countsEl = document.getElementById("__fi_counts");

  // ---------- State ----------
  const state = {
    itemSel: "",
    fields: { title: "", date: "", summary: "", link: "", image: "" }
  };

  // ---------- Helpers ----------
  function rect(el){
    const r = el.getBoundingClientRect();
    return { left: r.left+scrollX, top:r.top+scrollY, width:r.width, height:r.height };
  }
  function placeOverlay(overlay, r) {
    if (!r || r.width<=0 || r.height<=0) { overlay.style.display="none"; return; }
    overlay.style.display="block";
    overlay.style.left = r.left + "px";
    overlay.style.top = r.top + "px";
    overlay.style.width = r.width + "px";
    overlay.style.height = r.height + "px";
  }
  function clearFieldOverlays(){
    fieldOverlays.forEach(d => d.remove());
    fieldOverlays.length = 0;
  }
  function clearItemOutlines(){
    itemOutlines.forEach(d => d.remove());
    itemOutlines.length = 0;
  }
  function addFieldOverlay(r){
    const d = document.createElement("div");
    d.className = "__fi_field_overlay";
    placeOverlay(d, r);
    document.body.appendChild(d);
    fieldOverlays.push(d);
  }
  function addItemOutline(r){
    const d = document.createElement("div");
    d.className = "__fi_item_outline";
    placeOverlay(d, r);
    document.body.appendChild(d);
    itemOutlines.push(d);
  }
  function cssEscapeSegment(s) {
    return s.replace(/([ !"#$%&'()*+,./:;<=>?@[\\\]^`{|}~])/g, "\\$1");
  }
  function buildClassSelector(el) {
    if (!el || el.nodeType !== 1) return "";
    let parts = [];
    let cur = el;
    let depth = 0;
    while (cur && cur.nodeType === 1 && depth++ < 8) {
      let seg = cur.tagName.toLowerCase();
      if (cur.id) { seg += "#" + CSS.escape(cur.id); parts.unshift(seg); break; }
      if (cur.classList && cur.classList.length) {
        const classes = Array.from(cur.classList)
          .filter(c => !/^ng-/.test(c) && !/^js-/.test(c) && !/^is-/.test(c) && !/^has-/.test(c))
          .slice(0,3).map(c => "." + cssEscapeSegment(c)).join("");
        seg += classes;
      }
      parts.unshift(seg);
      cur = cur.parentElement;
    }
    return parts.join(" > ");
  }
  function nthPath(el){
    if (!el || el.nodeType!==1) return "";
    const parts=[];
    let cur=el, depth=0;
    while(cur && cur.nodeType===1 && depth++<8){
      let seg=cur.tagName.toLowerCase();
      if (cur.id){ seg += "#" + CSS.escape(cur.id); parts.unshift(seg); break; }
      let idx=1, sib=cur;
      while((sib=sib.previousElementSibling)) if (sib.tagName===cur.tagName) idx++;
      seg += `:nth-of-type(${idx})`;
      parts.unshift(seg);
      cur=cur.parentElement;
    }
    return parts.join(" > ");
  }
  function qsa(sel){ try { return document.querySelectorAll(sel); } catch { return []; } }

  function generalizeToRepeating(clickedEl) {
    // Kandidaten
    const candidates = new Set();
    const add = s => { if (s) candidates.add(s); };

    // A) class-based pad vanaf klik
    add(buildClassSelector(clickedEl));
    // B) class-based van voorouders
    let a = clickedEl;
    for (let i=0; i<6 && a; i++, a=a.parentElement) add(buildClassSelector(a));
    // C) nth-of-type pad fallback
    add(nthPath(clickedEl));
    let p = clickedEl.parentElement;
    for (let i=0;i<4 && p;i++,p=p.parentElement) add(nthPath(p));

    // D) heuristiek: zoek selectors die 2..200 nodes matchen en de klik bevatten
    let bestSel = "", bestScore = -Infinity, bestCount = 0;
    for (const s of candidates) {
      if (!s) continue;
      let nodes;
      try { nodes = qsa(s); } catch { continue; }
      const n = nodes.length;
      if (n < 2 || n > 400) continue;
      let contains = false;
      nodes.forEach(node => { if (node===clickedEl || node.contains(clickedEl)) contains = true; });
      if (!contains) continue;
      // score: class-based (zonder nth-of-type) preferred, korter preferred, meer matches preferred (tot op zekere hoogte)
      const classPref = s.includes(":nth-of-type(") ? 0 : 1;
      const score = classPref*2000 - s.length + Math.min(n, 100);
      if (score > bestScore) { bestScore = score; bestSel = s; bestCount = n; }
    }

    // Laatste poging: dichtstbijzijnde voorouder die 2+ matcht
    if (!bestSel) {
      let cur = clickedEl;
      while (cur) {
        const s = buildClassSelector(cur) || nthPath(cur);
        let n = 0;
        try { n = qsa(s).length; } catch {}
        if (n >= 2 && n <= 400) { bestSel = s; bestCount = n; break; }
        cur = cur.parentElement;
      }
    }

    return { selector: bestSel, count: bestCount };
  }

  function getRelativeSelector(itemNode, target) {
    if (!itemNode || !target) return "";
    if (itemNode === target) return ":scope";
    const parts = [];
    let cur = target, depth = 0;
    while (cur && cur !== itemNode && depth++ < 8) {
      let seg = cur.tagName.toLowerCase();
      if (cur.id) { seg += "#" + CSS.escape(cur.id); parts.unshift(seg); break; }
      if (cur.classList && cur.classList.length) {
        const classes = Array.from(cur.classList)
          .filter(c => !/^ng-/.test(c) && !/^js-/.test(c) && !/^is-/.test(c) && !/^has-/.test(c))
          .slice(0,3).map(c => "." + cssEscapeSegment(c)).join("");
        seg += classes;
      } else {
        let idx=1, sib=cur;
        while((sib=sib.previousElementSibling)) if (sib.tagName===cur.tagName) idx++;
        seg += `:nth-of-type(${idx})`;
      }
      parts.unshift(seg);
      cur = cur.parentElement;
    }
    return parts.length ? ":scope " + parts.join(" > ") : "";
  }

  function updateCodes() {
    codeEls.item.textContent = state.itemSel || "–";
    codeEls.title.textContent = state.fields.title || "–";
    codeEls.date.textContent = state.fields.date || "–";
    codeEls.summary.textContent = state.fields.summary || "–";
    codeEls.link.textContent = state.fields.link || "–";
    codeEls.image.textContent = state.fields.image || "–";
  }

  function preview() {
    clearFieldOverlays();
    clearItemOutlines();
    countsEl.textContent = "–";

    if (!state.itemSel) {
      itemOverlay.style.display = "none";
      return;
    }

    const items = Array.from(qsa(state.itemSel));
    if (!items.length) {
      itemOverlay.style.display = "none";
      return;
    }

    // Teken alle item-containers (gestippeld), highlight eerste item (geel)
    items.forEach(n => addItemOutline(rect(n)));
    placeOverlay(itemOverlay, rect(items[0]));

    const keys = ["title","date","summary","link","image"];
    const counts = Object.fromEntries(keys.map(k => [k,0]));

    for (const item of items) {
      for (const key of keys) {
        const rel = state.fields[key];
        if (!rel) continue;
        let nodes = [];
        try { nodes = item.querySelectorAll(rel.replace(/^:scope\s*/,"")); } catch {}
        nodes.forEach(n => {
          const r = rect(n);
          if (r.width>0 && r.height>0) { addFieldOverlay(r); counts[key]++; }
        });
      }
    }
    const flags = keys.filter(k => state.fields[k]).map(k => `${k}:${counts[k]}`).join("  ");
    countsEl.textContent = flags || "–";
  }

  // ---------- Events ----------
  document.addEventListener("mousemove", (e) => {
    if (e.target.closest("#__fi_toolbar") || e.target.closest("#__fi_panel")) {
      hoverOverlay.style.display = "none";
      return;
    }
    try { placeOverlay(hoverOverlay, rect(e.target)); } catch { hoverOverlay.style.display="none"; }
  }, true);

  document.addEventListener("click", (e) => {
    if (e.target.closest("#__fi_toolbar") || e.target.closest("#__fi_panel")) return;
    e.preventDefault(); e.stopPropagation();

    const mode = modeEl.value;
    const el = e.target;

    if (mode === "item") {
      const { selector, count } = generalizeToRepeating(el);
      if (!selector) {
        alert("Kon geen herhalend item vinden. Klik op de buitenste kaart/container van een bericht.");
        return;
      }
      state.itemSel = selector;
      updateCodes();
      preview();
      return;
    }

    if (!state.itemSel) {
      alert("Eerst een Item selecteren (Mode: Item). Klik op de kaart/het blok van één bericht.");
      return;
    }

    const items = Array.from(qsa(state.itemSel));
    if (!items.length) {
      alert("De item-selector matcht niets meer. Selecteer Item opnieuw.");
      return;
    }

    // Zoek het item waarin geklikt is (of neem het dichtstbijzijnde)
    let container = el.closest(state.itemSel);
    if (!container) {
      // fallback: kies het dichtstbijzijnde item obv DOM-positie
      container = items.find(n => n.contains(el)) || items[0];
      if (!container || !container.contains(el)) {
        alert("Klik binnen een geselecteerd item.");
        return;
      }
    }

    // Bepaal relatieve selector
    const rel = getRelativeSelector(container, el);
    if (!rel) {
      alert("Kon geen relatieve selector bepalen. Klik op het tekst-element zelf of iets hoger in de structuur.");
      return;
    }

    // Toggle (nogmaals klikken op exact hetzelfde = deselect)
    if (state.fields[mode] && state.fields[mode] === rel) {
      state.fields[mode] = "";
    } else {
      state.fields[mode] = rel;
    }

    updateCodes();
    preview();
  }, true);

  previewBtn.addEventListener("click", () => { preview(); });

  clearBtn.addEventListener("click", () => {
    state.itemSel = "";
    state.fields = { title:"", date:"", summary:"", link:"", image:"" };
    updateCodes();
    clearFieldOverlays();
    clearItemOutlines();
    itemOverlay.style.display = "none";
  });

  doneBtn.addEventListener("click", () => {
    const payload = {
      type: "FI_FEED_DONE",
      selections: {
        item: state.itemSel,
        title: state.fields.title,
        date: state.fields.date,
        summary: state.fields.summary,
        link: state.fields.link,
        image: state.fields.image
      },
      location: location.href
    };
    try { window.opener && window.opener.postMessage(payload, "*"); } catch {}
    try { window.parent && window.parent.postMessage(payload, "*"); } catch {}
    console.log("FI_FEED_DONE", payload);
    alert("Selecties verzonden (zie console/opener).");
  });

  // Op DOM mutaties & viewport events: preview hertekenen
  const mo = new MutationObserver(() => { if (state.itemSel) preview(); });
  mo.observe(document.documentElement, { childList: true, subtree: true, attributes: true });
  window.addEventListener("scroll", () => { if (state.itemSel) preview(); }, true);
  window.addEventListener("resize", () => { if (state.itemSel) preview(); }, true);

  // Populaire cookie/selectie-blockers verbergen
  setTimeout(() => {
    const hide = [".cookie-banner",".cookie-consent","#cookie",".cc-window",".cookie-wrapper",".cookie-notice",".cookie-popup",".cookies","#cookies"];
    for (const s of hide) { const n = document.querySelector(s); if (n) n.style.display = "none"; }
  }, 1200);
})();
