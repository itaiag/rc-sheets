// Site search for the reference pages. The index (window.RC_INDEX) comes from search-index.js, built by
// reference.py: one row per page, section, spell and equipment item: [title, English, kind, path, text].
// Matching is plain substring search over normalised Hebrew (no niqqud, final letters folded, no geresh).
(function () {
  var input = document.getElementById("q");
  var list = document.getElementById("results");
  var toc = document.querySelector(".toc");
  var menu = document.querySelector(".menu");
  if (!input || !list) return;
  var root = input.getAttribute("data-root") || "";
  var FINAL = { "ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ" };

  function norm(s) {
    return String(s).toLowerCase()
      .replace(/[֑-ׇ]/g, "")
      .replace(/[׳״"'`’]/g, "")
      .replace(/[ךםןףץ]/g, function (c) { return FINAL[c]; })
      .replace(/[\-־–—/]/g, " ")
      .replace(/\s+/g, " ").trim();
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  var rows = null;
  function load() {
    if (rows) return rows;
    rows = (window.RC_INDEX || []).map(function (r) {
      return { t: r[0], e: r[1], k: r[2], p: r[3], x: r[4] || "", nt: norm(r[0]), ne: norm(r[1]), nk: norm(r[2]), nx: norm(r[4] || "") };
    });
    return rows;
  }

  // A short piece of the original text around the first match. Normalising only removes or swaps characters
  // one for one, except for removed ones, so the position is found on a normalised copy built char by char.
  function snippet(text, token) {
    var map = [], n = "";
    for (var i = 0; i < text.length; i++) {
      var c = norm(text[i]);
      if (text[i] === " " || /[\-־–—/]/.test(text[i])) c = " ";
      for (var j = 0; j < c.length; j++) { n += c[j]; map.push(i); }
    }
    var at = n.indexOf(token);
    if (at < 0) return esc(text.slice(0, 90)) + (text.length > 90 ? "…" : "");
    var s = map[at], e = map[Math.min(at + token.length - 1, map.length - 1)] + 1;
    var from = Math.max(0, s - 40), to = Math.min(text.length, e + 60);
    return (from > 0 ? "…" : "") + esc(text.slice(from, s)) + "<mark>" + esc(text.slice(s, e)) + "</mark>" +
      esc(text.slice(e, to)) + (to < text.length ? "…" : "");
  }

  function search(q) {
    var nq = norm(q);
    if (!nq) return [];
    var tokens = nq.split(" ");
    var out = [];
    load().forEach(function (r) {
      var score = 0;
      for (var i = 0; i < tokens.length; i++) {
        var t = tokens[i], s = 0;
        if (r.nt.indexOf(t) === 0) s = 30;
        else if (r.nt.indexOf(" " + t) >= 0) s = 24;
        else if (r.nt.indexOf(t) >= 0) s = 18;
        else if (r.ne.indexOf(t) >= 0) s = 15;
        else if (r.nk.indexOf(t) >= 0) s = 4;
        else if (r.nx.indexOf(t) >= 0) s = 1;
        else return;
        score += s;
      }
      if (r.nt === nq || r.ne === nq) score += 60;
      else if (r.nt.indexOf(nq) === 0) score += 20;
      out.push({ r: r, s: score - r.nt.length / 100 });
    });
    out.sort(function (a, b) { return b.s - a.s; });
    return out.slice(0, 20).map(function (o) {
      var r = o.r, inTitle = tokens.every(function (t) { return r.nt.indexOf(t) >= 0 || r.ne.indexOf(t) >= 0; });
      return { r: r, x: inTitle ? "" : snippet(r.x, tokens.filter(function (t) { return r.nx.indexOf(t) >= 0; })[0] || tokens[0]) };
    });
  }

  var active = -1;
  function render() {
    var q = input.value;
    var found = search(q);
    active = -1;
    if (!norm(q)) { list.hidden = true; list.innerHTML = ""; toc.classList.remove("searching"); return; }
    toc.classList.add("searching");
    list.hidden = false;
    if (!found.length) { list.innerHTML = '<li class="none">לא נמצא דבר.</li>'; return; }
    list.innerHTML = found.map(function (f) {
      var en = f.r.e ? ' <span lang="en" dir="ltr" class="k" style="display:inline">' + esc(f.r.e) + "</span>" : "";
      return '<li><a href="' + esc(root + f.r.p) + '"><span class="t">' + esc(f.r.t) + "</span>" + en +
        '<span class="k">' + esc(f.r.k) + "</span>" + (f.x ? '<span class="x">' + f.x + "</span>" : "") + "</a></li>";
    }).join("");
  }
  function move(d) {
    var links = list.querySelectorAll("a");
    if (!links.length) return;
    if (active >= 0) links[active].classList.remove("on");
    active = (active + d + links.length) % links.length;
    links[active].classList.add("on");
    links[active].scrollIntoView({ block: "nearest" });
  }

  input.addEventListener("input", render);
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
    else if (e.key === "Enter") {
      var links = list.querySelectorAll("a");
      if (links.length) { e.preventDefault(); location.href = links[Math.max(active, 0)].href; }
    } else if (e.key === "Escape") {
      if (input.value) { input.value = ""; render(); } else setOpen(false);
    }
  });

  // Phones: the menu and the search live in a full-screen drawer opened from the top bar.
  var menuBtn = document.querySelector(".menu-btn");
  var searchBtn = document.querySelector(".search-btn");
  function setOpen(open) {
    toc.classList.toggle("open", open);
    document.body.classList.toggle("locked", open);
    if (menuBtn) {
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.setAttribute("aria-label", open ? "סגירת התפריט" : "תפריט");
    }
  }
  if (menuBtn) menuBtn.addEventListener("click", function () { setOpen(!toc.classList.contains("open")); });
  if (searchBtn) searchBtn.addEventListener("click", function () { setOpen(true); input.focus(); });
  // Any link in the menu or the results (also same-page anchors): close the drawer and clear the search.
  toc.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".drawer a")) return;
    setOpen(false);
    setTimeout(function () { input.value = ""; render(); }, 0);
  });
  window.matchMedia("(min-width: 56.01rem)").addEventListener("change", function (m) { if (m.matches) setOpen(false); });
  document.addEventListener("keydown", function (e) {
    var tag = (document.activeElement || {}).tagName;
    if (e.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA") {
      e.preventDefault();
      if (!window.matchMedia("(min-width: 56.01rem)").matches) setOpen(true);
      input.focus();
    }
    else if (e.key === "Escape" && toc.classList.contains("open")) setOpen(false);
  });
  var q0 = new URLSearchParams(location.search).get("q");
  if (q0) { input.value = q0; render(); }
})();
