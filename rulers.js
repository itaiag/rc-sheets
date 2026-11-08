// Dominion and army (War Machine) sheets: saves what is typed in this browser and recalculates
// everything on every change. Rules: Hebrew Rules Cyclopedia, pp. 117-120 and 138-142.
(() => {
  const doc = document.querySelector(".r-doc");
  if (!doc) return;
  const KIND = doc.dataset.kind;
  const KEY = "rc-sheets:" + (location.pathname.split("/").pop() || KIND);
  let data = {};
  try { data = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { data = {}; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { /* storage blocked */ } };

  // ---------- helpers
  const num = (k) => { const v = parseFloat(String(data[k] ?? "").replace(/,/g, "")); return isFinite(v) ? v : 0; };
  const has = (k) => data[k] != null && String(data[k]).trim() !== "";
  const fmt = (n, plus) => {
    if (!isFinite(n)) return "";
    const r = Math.round(n);
    const s = Math.abs(r).toLocaleString("en-US");
    return r < 0 ? "−" + s : (plus && r > 0 ? "+" + s : s);
  };
  const pct = (n) => (isFinite(n) ? (Math.round(n * 10) / 10).toString() + "%" : "");
  const set = (name, text) => {
    doc.querySelectorAll(`[data-out="${name}"]`).forEach((el) => {
      if (el.tagName === "OUTPUT" || el.tagName === "B" || el.tagName === "P" || el.tagName === "SPAN") el.textContent = text;
    });
  };
  const flag = (name, on) => doc.querySelectorAll(`[data-out="${name}"]`).forEach((el) => el.classList.toggle("on", !!on));
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  // Ability score bonus, p. 9.
  const abil = (v) => (v <= 0 ? 0 : v <= 3 ? -3 : v <= 5 ? -2 : v <= 8 ? -1 : v <= 12 ? 0 : v <= 15 ? 1 : v <= 17 ? 2 : 3);

  // ---------- fields
  const bind = (root) => {
    root.querySelectorAll("[data-key]").forEach((el) => {
      const k = el.dataset.key;
      if (el.type === "checkbox") el.checked = data[k] === true || (data[k] == null && el.defaultChecked);
      else if (data[k] != null) el.value = data[k];
      el.addEventListener(el.type === "checkbox" || el.tagName === "SELECT" ? "change" : "input", () => {
        data[k] = el.type === "checkbox" ? el.checked : el.value;
        if (el.hasAttribute("data-role")) fillPay(el);
        save();
        compute();
      });
    });
  };
  const fillPay = (el) => {
    const pay = doc.querySelector(`[data-key="${el.dataset.key.replace(".role", ".pay")}"]`);
    const opt = el.selectedOptions[0];
    if (pay && opt && opt.dataset.pay && !pay.value) { pay.value = opt.dataset.pay; data[pay.dataset.key] = pay.value; }
  };

  // ---------- dominion
  const BANDS = [ // [min, name, income rule]; p. 141
    [450, "אידיאלי", "up"], [400, "משגשג", "up"], [350, "שופע", "up"], [300, "בריא", "up"],
    [270, "יציב"], [230, "ממוצע"], [200, "לא יציב"],
    [150, "ממרה", 1 / 2], [100, "מורד", 1 / 3], [50, "לוחמני", 1 / 4], [-Infinity, "סוער", 0],
  ];
  const TITLES = ["ברון", "ויקונט", "רוזן", "מרקיז", "דוכס", "ארכידוכס", "נסיך", "מלך", "קיסר"];
  const VISIT = { "ברון": 100, "ויקונט": 150, "רוזן": 300, "מרקיז": 400, "דוכס": 600, "ארכידוכס": 700, "מלך": 1000, "קיסר": 1500 };

  const dominion = () => {
    let fam = 0, res = 0;
    for (let i = 0; i < 6; i++) {
      const f = num(`hex${i}.fam`);
      const r = f * (2 * num(`hex${i}.an`) + num(`hex${i}.veg`) + 3 * num(`hex${i}.min`));
      fam += f; res += r;
      set(`hex${i}.res`, has(`hex${i}.fam`) ? fmt(r) : "");
      flag(`hex${i}.res`, r > 15000);
    }
    set("families", fmt(fam)); set("resInc", fmt(res));
    set("people", fmt(fam * 5)); set("servants", fmt(Math.ceil(fam * 5 * 0.05))); set("muster", fmt(Math.ceil(fam * 5 * 0.1)));
    const g = fam <= 0 ? null : fam <= 100 ? 25 : fam <= 200 ? 20 : fam <= 300 ? 15 : fam <= 400 ? 10 : fam <= 500 ? 5 : -1;
    set("growth", g == null ? "" : g > 0 ? `+${g}% (${fmt(Math.ceil(fam * g / 100))})` : `+1% עד +5% (${fmt(Math.ceil(fam * 0.01))}–${fmt(Math.ceil(fam * 0.05))})`);

    // Confidence level.
    let base = num("conf.roll") + 150;
    for (let i = 0; i < 6; i++) base += num(`conf.ab${i}`);
    let adj = 0;
    for (let i = 0; i < 4; i++) adj += num(`conf.adj${i}`);
    const known = has("conf.roll");
    const conf = known ? Math.max(0, base + adj) : null;
    set("confBase", known ? fmt(base) : ""); set("conf", known ? fmt(conf) : "");
    const band = known ? BANDS.find(([min]) => conf >= min) : null;
    set("confName", band ? band[1] : "");
    const rows = [...doc.querySelectorAll("[data-band]")];
    rows.forEach((tr) => tr.classList.toggle("on", band && tr.querySelector("b").textContent === band[1]));
    const bandRow = band && rows.find((tr) => tr.querySelector("b").textContent === band[1]);
    set("confText", bandRow ? bandRow.lastElementChild.textContent : "ממלאים את גלגול ה-ק100 ואת התכונות של השליט.");

    // Income.
    const rate = has("dom.tax") ? num("dom.tax") : 1;
    let std = fam * 10, tax = fam * rate, rs = res, effect = "";
    if (band && band[2] === "up") { std *= 1.1; tax *= 1.1; rs *= 1.1; effect = "+10%"; }
    else if (band && typeof band[2] === "number") {
      const f = band[2]; std *= f; rs *= f; tax = 0;
      effect = f === 0 ? "אין הכנסה" : `אין מס; ${f === 1 / 2 ? "חצי" : f === 1 / 3 ? "שליש" : "רבע"} מהשאר`;
    }
    const keep = 1 - clamp(num("dom.musterPct"), 0, 100) / 100;
    std *= keep; tax *= keep; rs *= keep;
    const income = std + tax + rs;
    set("std", fmt(std)); set("tax", fmt(tax)); set("res", fmt(rs)); set("confEffect", effect || (known ? "אין" : ""));
    set("income", fmt(income)); set("income2", fmt(income));
    set("xp", fmt(tax + rs) + (tax + rs ? ` (דב״ש ${fmt((tax + rs) / 2)})` : ""));

    // Expenses.
    let staff = 0;
    doc.querySelectorAll('[data-key$=".pay"]').forEach((el) => { staff += num(el.dataset.key); });
    const liege = data["dom.hasLiege"] ? income * 0.2 : 0;
    const tithe = data["dom.tithe"] !== false ? income * 0.1 : 0;
    const high = TITLES.indexOf(data["dom.title"] || "") >= TITLES.indexOf("דוכס");
    const holidays = num("dom.holidays") * fam * (high ? 10 : 5);
    const visit = data["dom.visitor"] ? (VISIT[data["dom.visitor"]] + 50 * num("dom.visitExtra")) * num("dom.visitDays") : 0;
    const exp = liege + tithe + staff + holidays + visit + num("dom.troopsPay") + num("dom.otherPay");
    set("liegePay", fmt(liege)); set("tithePay", fmt(tithe)); set("staffPay", fmt(staff)); set("staffPay2", fmt(staff));
    set("holidayPay", fmt(holidays)); set("visitPay", fmt(visit));
    set("expenses", fmt(exp)); set("expenses2", fmt(exp));
    set("treasuryEnd", fmt(num("dom.treasury") + income - exp));
    set("domName", data["dom.name"] || "");
  };

  // ---------- army
  const CLASSES = [[126, "עלית"], [101, "מצויינת"], [81, "טובה"], [71, "ממוצעת"], [56, "סבירה"], [36, "מתחת לממוצע"], [21, "נמוכה"], [-Infinity, "חסרת אימון"]];
  const FLAGS = ["mnt", "mis", "lng", "mag", "spl", "fly", "spc"];
  const forces = () => Math.max(1, parseInt(data.__forces, 10) || 1);

  const force = (i) => {
    const p = `f${i}.`;
    let N = 0, nameLvl = 0, offN = 0, offL = 0, trN = 0, trL = 0, mvN = 0, mvSum = 0;
    const cnt = Object.fromEntries(FLAGS.map((f) => [f, 0]));
    for (let r = 0; r < 8; r++) {
      const u = `${p}u${r}.`;
      const n = num(u + "n");
      if (!n) continue;
      const lvl = num(u + "lvl");
      N += n;
      if (lvl >= 9) nameLvl += n;
      if (data[u + "role"] === "קצינים") { offN += n; offL += n * lvl; } else { trN += n; trL += n * lvl; }
      if (has(u + "mv")) { mvN += n; mvSum += n * num(u + "mv"); }
      FLAGS.forEach((f) => { if (data[u + f]) cnt[f] += n; });
    }
    const P = (c) => (N ? (100 * c) / N : 0);
    const avgMv = mvN ? mvSum / mvN : 0;
    set(p + "total", N ? fmt(N) : ""); set(p + "avgMv", mvN ? fmt(avgMv) : "");
    FLAGS.forEach((f) => set(`${p}pct.${f}`, N && cnt[f] ? pct(P(cnt[f])) : ""));

    const lead = num(p + "lead.lvl") + ["int", "wis", "cha"].reduce((s, a) => s + abil(num(`${p}lead.${a}`)), 0)
      + 2 * Math.ceil(P(nameLvl) - 1e-9);
    const officersOk = offN * 40 >= trN;
    const exp = (offN && officersOk ? Math.ceil((offL / offN) * 3) : 0) + (trN ? Math.ceil((trL / trN) * 2) : 0)
      + clamp(num(p + "wins"), 0, 10) - clamp(num(p + "routs"), 0, 10);
    const trn = clamp(num(p + "weeks"), 0, 20) + clamp(num(p + "lweeks"), 0, 20) + clamp(num(p + "months"), 0, 12);
    const wq = { "טוב": 10, "מצויין": 15 }[data[p + "wq"]] || 5;
    const eqp = wq + (data[p + "w2"] ? 5 : 0) + (data[p + "ac5"] ? 5 : 0);
    const spc = data[p + "elves"] ? 15 : 2 * Math.ceil(P(cnt.spc) - 1e-9);
    const bfr = lead + exp + trn + eqp + spc;
    const cls = CLASSES.find(([min]) => bfr >= min)[1];
    const bonus = Math.ceil(bfr / 10);
    const conds = [P(cnt.mnt) >= 20, P(cnt.mnt) >= 50, P(cnt.mis) >= 20, P(cnt.lng) >= 20, P(cnt.mag) >= 1, P(cnt.mag) >= 20,
      N > 0 && cnt.mag === N, P(cnt.spl) >= 5, P(cnt.spl) >= 30, P(cnt.fly) >= 1, P(cnt.fly) >= 20, mvN > 0 && avgMv >= 30];
    const count = conds.filter(Boolean).length;
    const br = bfr + bonus * count;
    const show = N > 0 || has(p + "lead.lvl");
    set(p + "lead", show ? fmt(lead) : ""); set(p + "exp", show ? fmt(exp) : ""); set(p + "trn", show ? fmt(trn) : "");
    set(p + "eqp", show ? fmt(eqp) : ""); set(p + "spc", show ? fmt(spc) : "");
    set(p + "bfr", show ? fmt(bfr) : ""); set(p + "cls", show ? cls : "");
    set(p + "bonus", show ? fmt(bonus) : ""); set(p + "count", show ? String(count) : ""); set(p + "br", show ? fmt(br) : "");
    conds.forEach((c, k) => flag(`${p}c${k}`, show && c));
    set(p + "warn", N && !officersOk && offN + trN ? `צריך קצין אחד לפחות לכל 40 חיילים (יש ${offN} ל-${trN}); בלי זה הקצינים לא נספרים בניסיון.` : "");
    set(p + "num", String(i + 1));
    return { name: data[p + "name"] || "", lead: data[p + "lead.name"] || "", N, bfr: show ? bfr : null, cls: show ? cls : "", br: show ? br : null };
  };

  const army = () => {
    const rows = [];
    let total = 0;
    for (let i = 0; i < forces(); i++) {
      const f = force(i);
      total += f.N;
      rows.push(`<tr><td class="c">${i + 1}</td><td>${esc(f.name)}</td><td>${esc(f.lead)}</td><td class="c">${f.N ? fmt(f.N) : ""}</td>`
        + `<td class="c">${f.bfr == null ? "" : fmt(f.bfr)}</td><td>${f.cls}</td><td class="c">${f.br == null ? "" : fmt(f.br)}</td></tr>`);
    }
    const body = doc.querySelector('[data-out="summary"]');
    if (body) body.innerHTML = rows.join("");
    set("sumTroops", total ? fmt(total) : "");
  };
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  const renderForces = () => {
    const holder = doc.querySelector(".r-forces");
    const tpl = document.getElementById("force-tpl").innerHTML;
    holder.innerHTML = "";
    for (let i = 0; i < forces(); i++) holder.insertAdjacentHTML("beforeend", tpl.replaceAll("__I__", i));
    bind(holder);
    holder.querySelectorAll("[data-del-force]").forEach((b) => b.addEventListener("click", () => delForce(+b.dataset.delForce)));
    holder.querySelectorAll("[data-del-force]").forEach((b) => { b.hidden = forces() < 2; });
    const sheets = [...doc.querySelectorAll(".sheet")];
    sheets.forEach((s, n) => { const f = s.querySelector(".foot span:last-child"); if (f) f.textContent = `עמוד ${n + 1} מתוך ${sheets.length}`; });
  };
  const delForce = (i) => {
    const name = data[`f${i}.name`] ? `„${data[`f${i}.name`]}”` : `מספר ${i + 1}`;
    if (!confirm(`למחוק את כוח ${name}?`)) return;
    const n = forces(), next = {};
    Object.entries(data).forEach(([k, v]) => {
      const m = /^f(\d+)\.(.*)$/.exec(k);
      if (!m) { next[k] = v; return; }
      const j = +m[1];
      if (j < i) next[k] = v; else if (j > i) next[`f${j - 1}.${m[2]}`] = v;
    });
    next.__forces = n - 1;
    data = next; save(); renderForces(); compute();
  };

  const compute = () => (KIND === "army" ? army() : dominion());

  // ---------- page buttons
  if (KIND === "army") renderForces();
  bind(KIND === "army" ? doc.querySelector("[data-summary]") : doc);
  const add = document.querySelector("[data-add-force]");
  if (add) add.addEventListener("click", () => {
    data.__forces = forces() + 1; save(); renderForces(); compute();
    const last = doc.querySelectorAll(".r-forces .sheet");
    last[last.length - 1].scrollIntoView({ behavior: "smooth" });
  });
  const clear = document.querySelector("[data-clear-all]");
  if (clear) clear.addEventListener("click", () => {
    if (!confirm("למחוק את כל מה שהוקלד בדף?")) return;
    data = {}; save();
    if (KIND === "army") renderForces();
    doc.querySelectorAll("[data-key]").forEach((el) => {
      if (el.closest("template")) return;
      if (el.type === "checkbox") el.checked = el.defaultChecked; else if (el.tagName === "SELECT") el.selectedIndex = 0; else el.value = "";
    });
    compute();
  });
  compute();
})();
