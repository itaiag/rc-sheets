/* NPC generator for ref/npc-generator.html. Data: window.NPC_DATA, built from data/npc_generator.py.
   Book rolls: class 1d12 and alignment 1d6 (p. 155), abilities 3d6 in order (p. 6) and adjustments (p. 9),
   hit dice (p. 7), height and weight (p. 12), maximum age (p. 143), reaction 2d6 (p. 92). The rest is ours.
   The current NPC and the saved list live in localStorage under "rc-sheets:npc-generator". */
(function () {
  var D = window.NPC_DATA, KEY = "rc-sheets:npc-generator";
  var out = document.getElementById("npc-out"), list = document.getElementById("npc-saved");
  var sel = { race: document.getElementById("npc-race"), sex: document.getElementById("npc-sex"),
              kind: document.getElementById("npc-kind") };
  if (!D || !out) return;

  // ---------------------------------------------------------------- dice
  function d(s) { return 1 + Math.floor(Math.random() * s); }
  function roll(n, s) { var t = 0; for (var i = 0; i < n; i++) t += d(s); return t; }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function weighted(items, w) {
    var total = 0, i; for (i = 0; i < items.length; i++) total += w(items[i]);
    var x = Math.random() * total;
    for (i = 0; i < items.length; i++) { x -= w(items[i]); if (x < 0) return items[i]; }
    return items[items.length - 1];
  }
  function band(table, v) { for (var i = 0; i < table.length; i++) if (v >= table[i][0] && v <= table[i][1]) return table[i]; }
  function adj(score) { return band(D.adjust, score)[2]; }
  function money(spec) {  // "3ק6 פ״כ" -> "11 פ״כ"
    var m = /^(\d+)ק(\d+)\s*(.*)$/.exec(spec);
    return m ? roll(+m[1], +m[2]) + " " + m[3] : spec;
  }
  function race(n) { for (var i = 0; i < D.races.length; i++) if (D.races[i].key === n.race) return D.races[i]; }

  // ---------------------------------------------------------------- one generator per field
  var GEN = {
    name: function (n) {
      var N = D.names[n.race];
      n.first = pick(N[n.sex]);
      n.family = pick(N.family);
    },
    age: function (n) {
      var a = weighted(D.ages, function (x) { return x.w; }), r = a.years[n.race], max = race(n).max;
      n.ageBand = a.he;
      n.years = r[0] + Math.floor(Math.random() * (r[1] - r[0] + 1));
      n.maxAge = max[0] + roll(max[1], max[2]);                       // p. 143
      if (n.years >= n.maxAge) n.years = n.maxAge - d(5);
      var wasOld = n.old;
      n.old = a === D.ages[D.ages.length - 1];
      if (!n.hair || n.old !== wasOld) GEN.hair(n);                   // grey hair for most of the old
    },
    body: function (n) {                                                // p. 12
      var row = pick(D.heights[race(n).heights]);
      var coins = +String(n.sex === "f" ? row[2] : row[1]).replace(/,/g, "");
      n.height = row[0];
      n.weight = coins;
    },
    build: function (n) { n.build = pick(D.build); },
    hair: function (n) {
      var color = n.old && Math.random() < 0.8 ? pick(D.hairOld) : pick(D.hairColor);
      n.hair = "שיער " + color + ", " + pick(D.hairStyle);
      var beard = n.sex === "m" && (n.race === "dwarf" || (n.race === "human" && Math.random() < 0.45));
      n.beard = beard ? pick(D.beard) : "";
    },
    eyes: function (n) { n.eyes = "עיניים " + pick(D.eyes); n.face = pick(D.face); },
    mark: function (n) { n.mark = pick(D.marks); },
    habit: function (n) { n.habit = pick(D.habits); },
    trait: function (n) { n.trait = pick(D.traits); },
    want: function (n) { n.want = pick(D.wants); },
    fear: function (n) { n.fear = pick(D.fears); },
    secret: function (n) { n.secret = pick(D.secrets); },
    rumour: function (n) {
      n.rumour = pick(D.rumours);
      n.truth = weighted(D.truth, function (x) { return x[1]; })[0];
    },
    pocket: function (n) { n.pocket = pick(D.pocket); },
    align: function (n) { n.align = band(D.alignment, d(6))[2]; },     // p. 155
    reaction: function (n) { n.reactionRoll = roll(2, 6); },           // p. 92
    abilities: function (n) {                                          // p. 6
      n.abil = D.abilities.map(function () { return roll(3, 6); });
      if (n.kind === "adv") hp(n);
    },
    job: function (n) {
      if (n.kind === "adv") {
        var R = race(n), c = R.cls ? { he: R.cls, hd: R.hd } : (function (b) { return { he: b[2], hd: b[3] }; })(band(D.humanClass, d(12)));
        n.cls = c.he; n.hd = c.hd; n.level = d(6);                     // class p. 155; level ours
        hp(n);
        n.job = ""; n.money = money("3ק6 פ״ז");                       // pocket money, ours
      } else {
        var o = pick(D.occupations);
        n.job = o[0]; n.money = money(o[1]); n.cls = ""; n.level = 0;
      }
    }
  };
  function hp(n) {                                                     // p. 7: hit die + Constitution, at least 1 per die
    if (!n.hd) return;
    var c = adj(n.abil[4]), t = 0;
    for (var i = 0; i < n.level; i++) t += Math.max(1, d(n.hd) + c);
    n.hp = t;
  }

  function fresh() {
    var n = {};
    n.race = sel.race.value || weighted(D.races, function (r) { return r.w; }).key;
    n.sex = sel.sex.value || (Math.random() < 0.5 ? "m" : "f");
    n.kind = sel.kind.value || (Math.random() < 0.25 ? "adv" : "folk");
    n.abil = [10, 10, 10, 10, 10, 10];
    ["name", "age", "body", "build", "eyes", "mark", "habit", "trait", "want", "fear", "secret", "rumour", "pocket",
     "align", "reaction", "abilities", "job"].forEach(function (f) { GEN[f](n); });
    n.id = Date.now().toString(36) + Math.floor(Math.random() * 1e4).toString(36);
    return n;
  }

  // ---------------------------------------------------------------- text
  function g(s, n) { return String(s || "").replace(/\{([^|}]*)\|([^}]*)\}/g, function (_, m, f) { return n.sex === "f" ? f : m; }); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function signed(v) { return v > 0 ? "+" + v : v < 0 ? "−" + (-v) : "0"; }
  function fullName(n) { return g(n.first + " " + n.family, n); }
  function kg(coins) { return Math.round(coins * 0.05); }              // p. 12: a coin is 50 g
  function reactionText(n) { return g(band(D.reactions, n.reactionRoll)[2], n); }
  function line(n) {
    var parts = [g(race(n).he, n), g(n.ageBand, n) + " (" + n.years + ")"];
    parts.push(n.kind === "adv" ? g(n.cls, n) + " בדרגה " + n.level : g(n.job, n));
    parts.push("נטייה: " + n.align);
    return parts.join(" · ");
  }
  function looks(n) {
    return [g(n.build, n), n.hair, n.beard, n.eyes, n.face].filter(Boolean).join(", ");
  }
  function fields(n) {  // [field to reroll, label, text]
    var rows = [
      ["body", "גובה ומשקל", n.height + ", " + kg(n.weight) + " ק״ג (" + n.weight.toLocaleString("en") + " מט׳)"],
      ["look", "מראה", looks(n)],
      ["mark", "סימן היכר", g(n.mark, n)],
      ["habit", "הרגל", g(n.habit, n)],
      ["trait", "אופי", g(n.trait, n)],
      ["want", "רוצה", g(n.want, n)],
      ["fear", "פחד", g(n.fear, n)],
      ["rumour", "שמועה", g(n.rumour, n)],
      ["pocket", "בכיס", g(n.pocket, n) + " · " + n.money],
      ["reaction", "תגובה ראשונה", reactionText(n) + " (בגלגול: " + n.reactionRoll + ")"]
    ];
    if (n.kind === "adv") rows.splice(1, 0, ["job", "נקודות פגיעה", n.hp + " (" + n.level + " קוביות ק" + n.hd + ")"]);
    return rows;
  }
  function abilText(n) {
    return D.abilities.map(function (a, i) { return a + " " + n.abil[i] + (adj(n.abil[i]) ? " (" + signed(adj(n.abil[i])) + ")" : ""); }).join(" · ");
  }
  function asText(n) {
    return [fullName(n), line(n)].concat(fields(n).map(function (r) { return r[1] + ": " + r[2]; }))
      .concat(["תכונות: " + abilText(n), "סוד: " + g(n.secret, n), "השמועה " + n.truth]).join("\n");
  }

  // ---------------------------------------------------------------- HTML
  function rr(f, label) {
    return '<button type="button" class="rr" data-f="' + f + '" title="גלגול מחדש: ' + label + '" aria-label="גלגול מחדש: ' + label + '">↻</button>';
  }
  function abilHtml(n) {
    return '<span class="npc-abil">' + D.abilities.map(function (a, i) {
      var v = adj(n.abil[i]);
      return "<span>" + a + " <b>" + n.abil[i] + "</b>" + (v ? ' <span class="num-ltr">(' + signed(v) + ")</span>" : "") + "</span>";
    }).join("") + "</span>";
  }
  function card(n, saved) {
    var tools = saved
      ? '<p class="npc-tools"><button type="button" class="link" data-act="show" data-id="' + n.id + '">הצגה למעלה</button> · '
        + '<button type="button" class="link" data-act="del" data-id="' + n.id + '">הסרה</button></p>'
      : "";
    var r = function (f, l) { return saved ? "" : rr(f, l); };
    return '<article class="npc">'
      + '<h3 class="npc-name">' + esc(fullName(n)) + r("name", "שם") + "</h3>"
      + '<p class="npc-line">' + esc(line(n)) + r("who", "עיסוק, גיל ונטייה") + "</p>"
      + '<dl class="facts npc-facts">'
      + fields(n).map(function (x) { return "<dt>" + x[1] + "</dt><dd>" + esc(x[2]) + (x[1] === "נקודות פגיעה" ? "" : r(x[0], x[1])) + "</dd>"; }).join("")
      + "<dt>תכונות</dt><dd>" + abilHtml(n) + r("abilities", "תכונות") + "</dd>"
      + '<dt>סוד</dt><dd><details class="npc-secret"><summary>לחיצה לגילוי</summary><p>' + esc(g(n.secret, n)) + r("secret", "סוד") + "</p>"
        + '<p class="note">השמועה ' + esc(n.truth) + "</p></details></dd>"
      + "</dl>" + tools + "</article>";
  }

  // ---------------------------------------------------------------- state
  var state = { cur: null, saved: [] };
  function load() {
    try { var s = JSON.parse(localStorage.getItem(KEY) || "null"); if (s && s.saved) state = s; } catch (e) {}
  }
  function store() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  function draw() {
    out.innerHTML = state.cur ? card(state.cur, false) : "";
    list.innerHTML = state.saved.length
      ? state.saved.map(function (n) {
          return '<li><details><summary><b>' + esc(fullName(n)) + '</b> <span class="npc-line">' + esc(line(n))
            + "</span></summary>" + card(n, true) + "</details></li>";
        }).join("")
      : '<li class="note">עוד לא נשמרו דב״שים. "שמירה ברשימה" מוסיף את הדמות שלמעלה.</li>';
  }

  document.getElementById("npc-new").addEventListener("click", function () { state.cur = fresh(); store(); draw(); });
  document.getElementById("npc-save").addEventListener("click", function () {
    if (!state.cur) return;
    state.saved = state.saved.filter(function (n) { return n.id !== state.cur.id; });
    state.saved.unshift(JSON.parse(JSON.stringify(state.cur)));
    store(); draw();
  });
  var copyBtn = document.getElementById("npc-copy");
  copyBtn.addEventListener("click", function () {
    if (!state.cur || !navigator.clipboard) return;
    navigator.clipboard.writeText(asText(state.cur)).then(function () {
      copyBtn.textContent = "הועתק"; setTimeout(function () { copyBtn.textContent = "העתקה כטקסט"; }, 1500);
    }, function () {});
  });
  out.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".rr");
    if (!b || !state.cur) return;
    var f = b.getAttribute("data-f"), n = state.cur;
    if (f === "look") { GEN.build(n); GEN.hair(n); GEN.eyes(n); }
    else if (f === "who") { GEN.job(n); GEN.age(n); GEN.align(n); }
    else GEN[f](n);
    var det0 = out.querySelector(".npc-secret"), keepOpen = f === "secret" || (det0 && det0.open);
    store(); draw();
    if (keepOpen) { var det = out.querySelector(".npc-secret"); if (det) det.open = true; }
  });
  list.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-act]");
    if (!b) return;
    var id = b.getAttribute("data-id"), act = b.getAttribute("data-act");
    if (act === "del") state.saved = state.saved.filter(function (n) { return n.id !== id; });
    if (act === "show") {
      state.cur = JSON.parse(JSON.stringify(state.saved.filter(function (n) { return n.id === id; })[0]));
      out.scrollIntoView({ block: "start" });
    }
    store(); draw();
  });

  load();
  if (!state.cur) state.cur = fresh();
  draw();
  window.RC_NPC = { fresh: fresh, asText: asText };  // for tests
})();
