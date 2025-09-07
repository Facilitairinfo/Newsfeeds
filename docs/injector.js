(() => {
  if (window.__fi_loaded) return;
  window.__fi_loaded = true;

  const style = document.createElement("style");
  style.textContent = `
    #__fi_toolbar {
      position: fixed; top: 0; left: 0; right: 0; z-index: 9999999;
      background: #111; color: #fff; font: 14px system-ui;
      padding: 6px 10px; display: flex; gap: 10px; align-items: center;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    #__fi_toolbar select, #__fi_toolbar button { font-size: 13px; }
    .__fi_overlay {
      position: absolute; border: 2px solid limegreen;
      background: rgba(0,255,0,0.2); pointer-events: none;
      z-index: 9999998; display: block;
    }
  `;
  document.head.appendChild(style);

  const toolbar = document.createElement("div");
  toolbar.id = "__fi_toolbar";
  toolbar.innerHTML = `
    <label>Mode:
      <select id="__fi_mode">
        <option value="title">Titel</option>
        <option value="date">Datum</option>
        <option value="summary">Samenvatting</option>
        <option value="image">Afbeelding</option>
      </select>
    </label>
    <button id="__fi_clear">Wissen</button>
    <button id="__fi_done">Klaar</button>
    <span style="margin-left:auto;opacity:.8">FI Selector actief</span>
  `;
  document.body.appendChild(toolbar);

  const modeEl = document.getElementById("__fi_mode");
  const clearBtn = document.getElementById("__fi_clear");
  const doneBtn = document.getElementById("__fi_done");

  const selections = { title: "", date: "", summary: "", image: "" };
  const overlays = {};

  function getSelector(el) {
    if (!el || !el.tagName) return "";
    if (el.id) return el.tagName.toLowerCase() + "#" + CSS.escape(el.id);
    const parts = [];
    let cur = el, depth = 0;
    while (cur && cur.nodeType === 1 && depth++ < 10) {
      let seg = cur.tagName.toLowerCase();
      if (cur.classList && cur.classList.length) {
        const cls = Array.from(cur.classList).slice(0,2).map(c => "." + CSS.escape(c)).join("");
        seg += cls;
      } else {
        let idx = 1, sib = cur;
        while ((sib = sib.previousElementSibling)) if (sib.tagName === cur.tagName) idx++;
        seg += `:nth-of-type(${idx})`;
      }
      parts.unshift(seg);
      cur = cur.parentElement;
    }
    return parts.join(" > ");
  }

  function bbox(el) {
    const r = el.getBoundingClientRect();
    return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height };
  }

  function createOverlay(box) {
    const o = document.createElement("div");
    o.className = "__fi_overlay";
    o.style.left = box.x + "px";
    o.style.top = box.y + "px";
    o.style.width = box.w + "px";
    o.style.height = box.h + "px";
    document.body.appendChild(o);
    return o;
  }

  document.addEventListener("click", (e) => {
    if (e.target.closest("#__fi_toolbar")) return;
    e.preventDefault(); e.stopPropagation();
    const el = e.target;
    const mode = modeEl.value;
    const sel = getSelector(el);
    const box = bbox(el);
    selections[mode] = sel;
    console.log(`Geselecteerd (${mode}):`, sel);

    if (overlays[mode]) overlays[mode].remove();
    overlays[mode] = createOverlay(box);
  }, true);

  clearBtn.addEventListener("click", () => {
    Object.values(overlays).forEach(o => o.remove());
    Object.keys(selections).forEach(k => selections[k] = "");
  });

  doneBtn.addEventListener("click", () => {
    const payload = {
      type: "FI_FEED_DONE",
      selections,
      location: location.href
    };
    try { window.opener && window.opener.postMessage(payload, "*"); } catch {}
    try { window.parent && window.parent.postMessage(payload, "*"); } catch {}
    console.log("FI_FEED_DONE", payload);
    alert("Selecties verzonden.");
  });
})();
