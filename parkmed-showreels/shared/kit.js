/* Parkmed showreels — shared helpers. Everything here is deterministic:
   visuals are pure functions of timeline time, randomness is seeded. */
(function () {
  const KIT = {};

  KIT.rng = function (seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  /* theme: "parkmed" (default) or "ref"; sets data-theme on <html> */
  KIT.theme = function () {
    let v = {};
    try { v = (window.__hyperframes && window.__hyperframes.getVariables && window.__hyperframes.getVariables()) || {}; } catch (e) {}
    const theme = v.theme === "ref" ? "ref" : "parkmed";
    document.documentElement.setAttribute("data-theme", theme);
    return theme;
  };
  KIT.css = function (name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  };

  /* hi-dpi canvas sized in CSS px; drawing uses CSS px coordinates */
  KIT.canvas = function (el, w, h) {
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    el.width = Math.round(w * dpr);
    el.height = Math.round(h * dpr);
    el.style.width = w + "px";
    el.style.height = h + "px";
    const ctx = el.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return ctx;
  };

  /* sample points inside rendered text */
  KIT.textPoints = function (text, font, w, h, step, cx, cy) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const x = c.getContext("2d");
    x.fillStyle = "#000"; x.textAlign = "center"; x.textBaseline = "middle";
    x.font = font; x.fillText(text, w / 2, h / 2);
    const d = x.getImageData(0, 0, w, h).data, pts = [];
    for (let y = 0; y < h; y += step) for (let xx = 0; xx < w; xx += step)
      if (d[(y * w + xx) * 4 + 3] > 128) pts.push([xx - w / 2 + cx, y - h / 2 + cy]);
    return pts;
  };

  /* wrap each character of an element in .ch spans */
  KIT.split = function (el) {
    const txt = el.textContent;
    el.textContent = "";
    return [...txt].map((c) => {
      const s = document.createElement("span");
      s.className = "ch";
      s.style.display = "inline-block";
      s.textContent = c === " " ? " " : c;
      el.appendChild(s);
      return s;
    });
  };

  KIT.clamp = (x) => Math.max(0, Math.min(1, x));
  KIT.ease = {
    out3: (x) => 1 - Math.pow(1 - x, 3),
    out4: (x) => 1 - Math.pow(1 - x, 4),
    inOut3: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    in3: (x) => x * x * x,
  };

  /* timecode for 60 fps */
  KIT.tc = function (t) {
    const f = Math.min(899, Math.floor(t * 60 + 1e-6));
    return `00:00:${String(Math.floor(f / 60)).padStart(2, "0")}:${String(f % 60).padStart(2, "0")}`;
  };

  /* fonts every composition waits for before building its timeline */
  KIT.ready = function (fonts) {
    return Promise.all(fonts.map((f) => document.fonts.load(f))).then(() => document.fonts.ready);
  };

  /* Logo built from its exact artwork layers (parts re-stack to the original). */
  KIT.logoHTML = function (id, w) {
    const h = Math.round((w * 474) / 1083);
    return `<div class="logo-build" id="${id}" style="position:relative;width:${w}px;height:${h}px">` +
      ["park", "med", "bird", "arc", "tagline"].map((p) => `<img class="lg-${p}" src="assets/logo/part-${p}.png" alt="" style="position:absolute;left:0;top:0;width:${w}px;height:${h}px">`).join("") +
      `</div>`;
  };
  KIT.logoBuild = function (tl, sel, t0, speed) {
    const k = speed || 1, root = document.querySelector(sel), q = (p) => root.querySelector(".lg-" + p);
    tl.fromTo(q("park"), { clipPath: "inset(100% 0% 0% 0%)", y: 30 }, { clipPath: "inset(0% 0% 0% 0%)", y: 0, duration: 0.4 * k, ease: "expo.out" }, t0);
    tl.fromTo(q("med"), { clipPath: "inset(100% 0% 0% 0%)", y: 30 }, { clipPath: "inset(0% 0% 0% 0%)", y: 0, duration: 0.4 * k, ease: "expo.out" }, t0 + 0.08 * k);
    tl.fromTo(q("bird"), { scale: 0, transformOrigin: "53.3% 27.2%" }, { scale: 1, duration: 0.35 * k, ease: "back.out(3)" }, t0 + 0.26 * k);
    tl.fromTo(q("arc"), { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.45 * k, ease: "power3.inOut" }, t0 + 0.3 * k);
    tl.fromTo(q("tagline"), { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.4 * k, ease: "power3.out" }, t0 + 0.2 * k);
  };

  window.KIT = KIT;
})();
