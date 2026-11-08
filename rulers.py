"""Dominion and army (War Machine) sheets for rulers, with fill-in fields and automatic
calculations (rulers.js). Rules and Hebrew terms follow the Hebrew Rules Cyclopedia:
War Machine pp. 117-120, specialists p. 133, stronghold staff and dominions pp. 138-142."""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = (HERE / "rulers.js").read_text(encoding="utf-8")
FOOT = "חוקי המבוכים והדרקונים (Rules Cyclopedia), דפי שליטה בעברית"

TITLES = ["ברון", "ויקונט", "רוזן", "מרקיז", "דוכס", "ארכידוכס", "נסיך", "מלך", "קיסר"]
HEX_TYPES = ["מיושב", "איזור ספר", "מרחבים"]

# Staff roles: (name, monthly pay in gp, note). Pay 5 = "officials without a listed cost".
OFFICIALS = [
    ("נציב", 4000, "מנהל את הדומיניון כשהשליט איננו; כפוף לשליט בלבד"),
    ("ראש המשמר", 4000, "4,000+; לוחם מדרגה 9 ומעלה; שומר על השליט והאוצר"),
    ("יועץ המבצר", 2000, "כל ענייני הצבא של המבצר; לוחם מדרגה 5–9"),
    ("השופט העליון", 2000, "שופט בשם השליט; ממונה על השופטים והשריפים"),
    ("חכם", 2000, "יועץ לידע עתיק ומעורפל"),
    ("מגיסט", 3000, "3,000+, או 250 פ״ז לדרגה; קוסם מדרגה 9 ומעלה"),
    ("הדייל הראשי", 1000, "ענייני היום-יום: מזון, ניקיון, משק הבית"),
    ("יועץ ארטילריה", 750, "כלי מצור; לוחם מדרגה 3–5"),
    ("מהנדס", 750, "בנייה: מהנדס לכל 100,000 פ״ז של בנייה"),
    ("איש הדת", 500, "הכוהן הראשי; משרת רק אם משולם המעשר"),
    ("מנהל החשבונות", 500, "רישומי מסים, מעשרות ומתנות"),
    ("כרוז", 300, "300–500; סמלים, הכרזות, נימוסי חצר"),
    ("מנהל אחוזה", 5, "ממונה על חלק אחד של המבצר"),
    ("חדרן", 5, "ניקיון והגשת אוכל"),
    ("חצרן", 5, "הסוסים והאורוות"),
    ("שופט", 5, "שופט נודד לאיכרים"),
    ("מארשל", 5, "לוחם ותיק שמאמן חיילים"),
    ("מנהלן", 5, "גובה המס"),
    ("שריף", 5, "אכיפת החוק, מעצרים וחקירות"),
    ("פקח", 5, "שומר על חלק בדומיניון"),
    ("שרת", 5, "משרת או אומן נאמן, בתוספת חדר ולינה"),
]
SPECIALISTS = [
    ("אלכימאי", 1000, "מעתיק שיקוי בחצי זמן ועלות"),
    ("מאלף חיות", 500, "עד שש חיות"),
    ("שריונאי", 100, "שריונאי לכל 50 חיילים"),
    ("נפח", 25, "מתחזק נשק ושריון"),
    ("קוסם", 3000, "3,000+; עבודה זמנית"),
    ("מרגל", 500, "500+ למשימה"),
    ("רב חובל", 250, ""),
    ("נווט", 150, ""),
    ("מלח", 10, ""),
    ("חותר", 2, ""),
]

# Confidence levels, p. 141. The Hebrew edition skips "Healthy" (300-349); "בריא" is our translation.
CONFIDENCE = [
    ("אידיאלי", "450+", "כל ההכנסות +10%. 75% לחשוף כל סוכן של דומיניון אחר. 25% שאסון שנקבע לשנה לא יקרה. "
     "בבדיקה הבאה הרמה לא תרד מתחת ל-400, ומוסיפים לה 25."),
    ("משגשג", "400–449", "כל ההכנסות +10%. 75% לחשוף כל סוכן. 25% שאסון לא יקרה."),
    ("שופע", "350–399", "כל ההכנסות +10%. 25% שאסון לא יקרה. 25% לחשוף כל סוכן."),
    ("בריא", "300–349", "כל ההכנסות +10%. 25% לחשוף כל סוכן."),
    ("יציב", "270–299", "25% לחשוף כל סוכן."),
    ("ממוצע", "230–269", "אין השפעות מיוחדות."),
    ("לא יציב", "200–229", "סיכוי 1 מ-6 שהרמה תרד פתאום ב-10%."),
    ("ממרה", "150–199", "חצי מהאיכרים (2.5 כפול מספר המשפחות) מקימים מיליציה. אין הכנסה ממס. "
     "הכנסה רגילה וממשאבים: חצי לכל היותר, שליש באיזור עם מיליציה. חמולות לא מתערבות."),
    ("מורד", "100–149", "מיליציה, ואין הכנסה ממס. הכנסה רגילה וממשאבים: שליש או רבע. "
     "−5 לרמת האמון בכל חודש שהיא מתחת ל-200."),
    ("לוחמני", "50–99", "אין הכנסה ממס. הכנסה רגילה וממשאבים: רבע או כלום. −10 לרמת האמון בכל חודש. "
     "שודדים תוקפים פקידים ושיירות, כוחות הדומיניון מותקפים בדרך, דמויי-אדם עוינים."),
    ("סוער", "1–49", "כל ההשפעות של לוחמני, כפולות. 95% מהאיכרים במרד גלוי. אין הכנסה אלא בכוח. "
     "הרמה לא תעלה ל-100 עד שהשליט יודח."),
]

VISITORS = [("ברון", 100), ("ויקונט", 150), ("רוזן", 300), ("מרקיז", 400), ("דוכס", 600),
            ("ארכידוכס", 700), ("מלך", 1000), ("קיסר", 1500)]

TROOP_CLASSES = [("0–20", "חסרת אימון"), ("21–35", "נמוכה"), ("36–55", "מתחת לממוצע"), ("56–70", "סבירה"),
                 ("71–80", "ממוצעת"), ("81–100", "טובה"), ("101–125", "מצויינת"), ("126+", "עלית")]

# Battle rating statements a-l, p. 117-118 (letters as in the Hebrew edition).
BR_CONDITIONS = [
    ("א", "20% או יותר מהכוח רכובים"), ("ב", "50% או יותר מהכוח רכובים"),
    ("ג", "20% או יותר יכולים לירות"), ("ד", "20% או יותר יורים לטווח 30 מ׳ או יותר"),
    ("ה", "1% או יותר מצוידים ביכולות קסם"), ("ו", "20% או יותר מצוידים ביכולות קסם"),
    ("ז", "כל הכוח מצויד ביכולות קסם"), ("ח", "5% או יותר יכולים להטיל לחשים"),
    ("ט", "30% או יותר יכולים להטיל לחשים"), ("י", "1% או יותר יכולים לעוף"),
    ("כ", "20% או יותר יכולים לעוף"), ("ל", "תנועה ממוצעת של 30 מ׳ לתור או יותר"),
]

# Combat results, p. 120: difference, casualties W/L, fatigue W/L, location W/L.
# Fatigue: ל not fatigued, ב moderately, מ seriously. Location: ש holds the field, נ retreats.
COMBAT_RESULTS = [
    ("1–8", "0", "10%", "ל", "ל", "ש", "נ"), ("9–15", "0", "20%", "ל", "ל", "ש", "נ"),
    ("16–24", "10%", "20%", "ל", "ב", "ש", "נ"), ("25–30", "10%", "30%", "ל", "ב", "ש", "נ+1"),
    ("31–38", "20%", "40%", "ב", "מ", "נ", "נ"), ("39–50", "0%", "30%", "ל", "מ", "ש", "נ+2"),
    ("51–63", "20%", "50%", "ב", "מ", "ש+1", "נ+3"), ("64–80", "30%", "60%", "ב", "מ", "ש+1", "נ+3"),
    ("81–90", "10%", "50%", "ל", "מ", "ש+3", "נ+2"), ("91–100", "0%", "30%", "ל", "מנוסה", "ש+3", "מנוסה"),
    ("101–120", "20%", "70%", "ל", "מנוסה", "ש+3", "מנוסה"), ("121–150", "10%", "70%", "ל", "מנוסה", "ש+3", "מנוסה"),
    ("151+", "10%", "100%", "ל", "—", "ש+5", "—"),
]


# ---------------------------------------------------------------- helpers

SIGNED = re.compile(r"(?<![\w\u0590-\u05FF])([+\u2212±]\d[\d,.]*%?)")


def signs(html):
    """Wrap +10, −5, +25% etc. in an LTR isolate so the sign stays in front in Hebrew text."""
    return SIGNED.sub(r'<span class="num-ltr">\1</span>', html)


def page(n, total, inner, label, extra=""):
    inner = signs(inner)
    return f"""
  <section class="sheet r-sheet" aria-label="עמוד {n}: {label}"{extra}>
    <div class="page">
{inner}
      <div class="foot"><span>{FOOT}</span><span>עמוד {n} מתוך {total}</span></div>
    </div>
  </section>"""


def inp(key, cls="", kind="text", ph="", extra=""):
    mode = ' inputmode="numeric"' if kind == "num" else ""
    return (f'<input class="fill {cls}" type="text"{mode} data-key="{key}" autocomplete="off"'
            f'{f" placeholder=\"{ph}\"" if ph else ""}{extra}>')


def sel(key, options, cls="", blank=True):
    opts = ('<option value=""></option>' if blank else "") + "".join(f"<option>{o}</option>" for o in options)
    return f'<select class="fill {cls}" data-key="{key}">{opts}</select>'


def chk(key, label="", cls="", on=False):
    return (f'<label class="r-check {cls}"><input type="checkbox" data-key="{key}"{" checked" if on else ""}>'
            f'<i aria-hidden="true"></i>{f"<span>{label}</span>" if label else ""}</label>')


def out(name, cls=""):
    return f'<output class="r-out {cls}" data-out="{name}"></output>'


def field(label, control):
    return f'<label class="field"><span class="label">{label}</span>{control}</label>'


def line(label, value, hint="", cls=""):
    hint = f'<span class="hint">{hint}</span>' if hint else ""
    return f'<div class="r-line {cls}"><span>{label}{hint}</span>{value}</div>'


def header(title, tag, fields):
    return f"""      <header class="r-head">
        <div class="brand"><h1>{title}</h1><span class="class-tag">{tag}</span></div>
        <div class="r-fields">{fields}</div>
      </header>"""


# ---------------------------------------------------------------- dominion

def dominion_page1():
    head = header("דומיניון", "שליטה", "".join([
        field("שם הדומיניון", inp("dom.name", "write")),
        field("השליט", inp("dom.ruler", "write")),
        field("תואר", sel("dom.title", TITLES, "write")),
        field("האדון", inp("dom.liege", "write")),
        field("חודש ושנה", inp("dom.date", "write")),
    ]))
    rows = "".join(
        f"""<tr><td>{inp(f"hex{i}.name")}</td><td>{sel(f"hex{i}.type", HEX_TYPES)}</td><td>{inp(f"hex{i}.terrain")}</td>
          <td class="n">{inp(f"hex{i}.fam", "num", "num")}</td><td class="n">{inp(f"hex{i}.an", "num", "num")}</td>
          <td class="n">{inp(f"hex{i}.veg", "num", "num")}</td><td class="n">{inp(f"hex{i}.min", "num", "num")}</td>
          <td class="o">{out(f"hex{i}.res")}</td></tr>"""
        for i in range(6))
    hexes = f"""      <div class="panel">
        <h2 class="box-title">משושים ואוכלוסייה <span class="hint">משושה = 36 ק״מ. מספר המשאבים מכל סוג בכל משושה (1–4 בסך הכול)</span></h2>
        <table class="r-table">
          <thead><tr><th>משושה</th><th class="w-type">סוג</th><th>פני שטח</th><th class="c">משפחות</th>
            <th class="c">חיות</th><th class="c">צמחים</th><th class="c">מינרלים</th><th class="c">הכנסה ממשאבים</th></tr></thead>
          <tbody>{rows}</tbody>
          <tfoot><tr><td colspan="3">סך הכול</td><td class="n">{out("families")}</td><td colspan="3"></td><td class="o">{out("resInc")}</td></tr></tfoot>
        </table>
        <div class="r-stats">
          <div><span class="label">נפשות</span>{out("people")}<span class="hint">5 לכל משפחה</span></div>
          <div><span class="label">איכרים משרתים</span>{out("servants")}<span class="hint">5% מהאיכרים</span></div>
          <div><span class="label">צבא איכרים</span>{out("muster")}<span class="hint">10% בשעת מלחמה, רמה נמוכה</span></div>
          <div><span class="label">גידול בחודש הבא</span>{out("growth")}<span class="hint">ועוד 1–10 משפחות לכל משושה, לכאן או לכאן</span></div>
        </div>
        <p class="hint r-note">משפחות בתחילה, לכל משושה: מיושב 500–5,000, איזור ספר 200–1,200, מרחבים 10–100.
          הכנסה ממשאבים לכל משפחה, על כל משאב: חיות 2 פ״ז, צמחים 1 פ״ז, מינרלים 3 פ״ז.
          משושה שמכניס יותר מ-15,000 פ״ז ממשאבים צריך שליט מקומי משלו, אחרת חלק נגנב.</p>
      </div>"""
    income = f"""        <div class="panel">
          <h2 class="box-title">הכנסה החודש</h2>
          {line("תעריף מס", inp("dom.tax", "num r-small", "num", "1"), "פ״ז למשפחה, בדרך כלל 1")}
          {line("איכרים שגויסו", inp("dom.musterPct", "num r-small", "num", "0"), "באחוזים; מקטין את כל ההכנסות")}
          <div class="r-sep"></div>
          {line("הכנסה רגילה", out("std"), "שירותים, 10 פ״ז למשפחה; לא מזומן")}
          {line("הכנסה ממס", out("tax"))}
          {line("הכנסה ממשאבים", out("res"))}
          {line("השפעת רמת האמון", out("confEffect"), "", "r-muted")}
          {line("סך ההכנסה", out("income", "r-big"), "", "r-total")}
          {line("נקודות ניסיון לשליט", out("xp"), "מס + משאבים; לדב״ש מחצית")}
        </div>"""
    expenses = f"""        <div class="panel">
          <h2 class="box-title">הוצאות החודש</h2>
          {line(chk("dom.hasLiege", "לאדון, 20%"), out("liegePay"))}
          {line(chk("dom.tithe", "מעשר לשלטון הדת, 10%", on=True), out("tithePay"))}
          {line("יועצים ומומחים", out("staffPay"), "מעמוד 2")}
          {line("חגים", '<span class="r-pair">' + inp("dom.holidays", "num r-small", "num", "0") + out("holidayPay") + "</span>", "מספר החגים; 5 פ״ז למשפחה, מדוכס ומעלה 10")}
          {line("מבקרים", '<span class="r-pair">' + sel("dom.visitor", [v for v, _ in VISITORS], "r-mid") + inp("dom.visitDays", "num r-small", "num", "ימים") + out("visitPay") + "</span>", "האורח הבכיר; +50 ליום לכל אורח נוסף בעל תואר")}
          {line("אורחים נוספים בעלי תואר", inp("dom.visitExtra", "num r-small", "num", "0"))}
          {line("חיילים", inp("dom.troopsPay", "num r-small", "num", "0"))}
          {line("תחרויות ואחר", inp("dom.otherPay", "num r-small", "num", "0"))}
          {line("סך ההוצאות", out("expenses", "r-big"), "", "r-total")}
        </div>"""
    treasury = f"""      <div class="r-strip">
        <div>{field("אוצר בתחילת החודש", inp("dom.treasury", "write num", "num"))}</div>
        <div class="op">+</div><div><span class="label">הכנסה</span>{out("income2")}</div>
        <div class="op">−</div><div><span class="label">הוצאות</span>{out("expenses2")}</div>
        <div class="op">=</div><div><span class="label">אוצר בסוף החודש</span>{out("treasuryEnd", "r-big")}</div>
        <p class="hint">האוצר הוא מזומן וסחורה. רק 20%–50% ממנו זמינים כמזומן בכל חודש.</p>
      </div>"""
    abil = "".join(f'<label class="r-ab"><span class="label">{n}</span>{inp(f"conf.ab{i}", "num", "num")}</label>'
                   for i, n in enumerate(["כוח", "תבונה", "חוכמה", "זריזות", "כושר", "כריזמה"]))
    adj = "".join(f'<div class="r-adj">{inp(f"conf.why{i}", "", "text", "סיבה")}{inp(f"conf.adj{i}", "num", "num", "±")}</div>'
                  for i in range(8))
    conf = f"""      <div class="panel r-conf">
        <h2 class="box-title">רמת האמון <span class="hint">1–500. נקבעת מחדש בתחילת כל שנה; עד ±50 בחודש, ±10 לכל גורם</span></h2>
        <div class="r-conf-grid">
          <div>
            <div class="r-base">
              <label class="r-ab"><span class="label">ק100</span>{inp("conf.roll", "num", "num")}</label>
              <span class="op">+ 150 +</span>{abil}
              <span class="op">=</span><div class="r-ab"><span class="label">בסיס</span>{out("confBase")}</div>
            </div>
            <span class="label">שינויים השנה</span>
            <div class="r-adjs">{adj}</div>
          </div>
          <div class="r-level">
            <span class="label">רמת האמון עכשיו</span>
            {out("conf", "r-huge")}
            <b data-out="confName"></b>
            <p data-out="confText" class="r-conf-text"></p>
          </div>
        </div>
      </div>"""
    return f"""{head}
{hexes}
      <div class="two-up">
{income}
{expenses}
      </div>
{treasury}
{conf}"""


def role_options():
    g1 = "".join(f'<option data-pay="{p}">{n}</option>' for n, p, _ in OFFICIALS)
    g2 = "".join(f'<option data-pay="{p}">{n}</option>' for n, p, _ in SPECIALISTS)
    return f'<option value=""></option><optgroup label="יועצים ופקידים">{g1}</optgroup><optgroup label="מומחים">{g2}</optgroup>'


def dominion_page2():
    rows = "".join(
        f"""<tr><td><select class="fill" data-key="staff{i}.role" data-role>{role_options()}</select></td>
          <td>{inp(f"staff{i}.name")}</td><td>{inp(f"staff{i}.lvl")}</td><td>{inp(f"staff{i}.note")}</td>
          <td class="n">{inp(f"staff{i}.pay", "num", "num")}</td></tr>"""
        for i in range(18))
    ref = "".join(f"<li><b>{n}</b> {d if d[:1].isdigit() else f'{p:,}' + (f' · {d}' if d else '')}</li>"
                  for n, p, d in OFFICIALS + SPECIALISTS)
    return f"""      <header class="hd2">
        <h1>יועצים ומומחים</h1>
        <label class="field"><span class="label">הדומיניון</span><output class="fill write r-echo" data-out="domName"></output></label>
      </header>
      <div class="panel">
        <h2 class="box-title">הסגל בתשלום <span class="hint">בחירת תפקיד ממלאת את המשכורת מהספר; אפשר לשנות</span></h2>
        <table class="r-table r-staff">
          <thead><tr><th class="w-role">תפקיד</th><th>שם</th><th class="w-lvl">מקצוע ודרגה</th><th>פרטים</th><th class="c w-pay">פ״ז לחודש</th></tr></thead>
          <tbody>{rows}</tbody>
          <tfoot><tr><td colspan="4">סך המשכורות (נכנס להוצאות בעמוד 1)</td><td class="o">{out("staffPay2")}</td></tr></tfoot>
        </table>
      </div>
      <div class="panel r-ref">
        <h2 class="box-title">משכורות לפי הספר <span class="hint">פ״ז לחודש. פקיד בלי מחיר מקבל 5 פ״ז. האיכרים משרתים בחינם</span></h2>
        <ul class="r-cols">{ref}</ul>
      </div>"""


def dominion_page3():
    conf = "".join(f'<tr data-band="{i}"><td class="nw"><b>{n}</b></td><td class="c nw">{r}</td><td>{t}</td></tr>'
                   for i, (n, r, t) in enumerate(CONFIDENCE))
    vis = "".join(f"<tr><td>{n}</td><td class=\"c\">{c:,}</td></tr>" for n, c in VISITORS)
    return f"""      <header class="hd2"><h1>עזר לשליט</h1><span></span></header>
      <div class="panel">
        <h2 class="box-title">רמות האמון <span class="hint">השורה המודגשת היא הרמה הנוכחית</span></h2>
        <table class="r-table r-reftable">{conf}</table>
        <p class="hint r-note">אין גלגול בבדיקת אמון: מפעילים את ההשפעות של הרמה הנוכחית. בודקים בתחילת כל שנה,
          כשחגיגה צפויה מבוטלת, אחרי אסון טבע, כשכוח אויב נכנס לדומיניון, או כשהמנחה מחליט.
          את רמת „בריא” (300–349) המהדורה העברית לא מפרטת; השם שלנו.</p>
      </div>
      <div class="two-up">
        <div class="panel">
          <h2 class="box-title">גידול אוכלוסייה בחודש</h2>
          <table class="r-table r-reftable">
            <tr><td>1–100 משפחות</td><td class="c">+25%</td></tr><tr><td>101–200</td><td class="c">+20%</td></tr>
            <tr><td>201–300</td><td class="c">+15%</td></tr><tr><td>301–400</td><td class="c">+10%</td></tr>
            <tr><td>401–500</td><td class="c">+5%</td></tr><tr><td>יותר מ-500</td><td class="c">+1% עד +5%</td></tr>
          </table>
          <h2 class="box-title r-gap">משאבים <span class="hint">ק10</span></h2>
          <table class="r-table r-reftable">
            <tr><td>1: משאב אחד · 2–7: שניים · 8–9: שלושה · 10: ארבעה</td></tr>
            <tr><td><b>חיות</b> (1–3): חלב, דגים, עופות, פרוות, עדרים, דבורים, סוסים, שנהב</td></tr>
            <tr><td><b>צמחים</b> (4–8): גידולי חווה, מזון, שמן, מספוא, עצים, נייר, יין</td></tr>
            <tr><td><b>מינרלים</b> (9–10): מתכות, אבני חן, זפת ונפט, חימר, מחצבות, פחם</td></tr>
          </table>
        </div>
        <div class="panel">
          <h2 class="box-title">מבקרים <span class="hint">פ״ז ליום, כולל משתה אחד ביום</span></h2>
          <table class="r-table r-reftable">{vis}<tr><td>נסיך</td><td class="c">תואר הדומיניון +100</td></tr></table>
          <p class="hint r-note">כל אורח נוסף בעל תואר: +50 פ״ז ליום. מתנות לאורח לא כלולות.</p>
          <h2 class="box-title r-gap">חגים</h2>
          <p class="r-small-text">רוזן ומטה: 1 פ״ז לאיכר (5 למשפחה). דוכס ומעלה: 2 פ״ז לאיכר.
            שלטון הדת מכריז בדרך כלל על שני חגים בשנה, והמלך על אחד.</p>
          <h2 class="box-title r-gap">מלחמה</h2>
          <p class="r-small-text">20% מההכנסה הולכים לאדון, לרוב כחיילים. בשעת מלחמה עשירית מהאיכרים מתגייסים
            (רמה נמוכה); אפשר להכפיל, ואז הרמה חסרת אימון. ההכנסה קטנה באותו אחוז.</p>
        </div>
      </div>"""


# ---------------------------------------------------------------- army

def force_page():
    I = "__I__"
    flags = [("mnt", "רכוב"), ("mis", "ירי"), ("lng", "ירי 30 מ׳+"), ("mag", "קסם"), ("spl", "לחשים"), ("fly", "תעופה"), ("spc", "מיוחד")]
    heads = "".join(f'<th class="c f">{n}</th>' for _, n in flags)
    rows = "".join(
        f"""<tr><td>{inp(f"f{I}.u{r}.name")}</td><td>{sel(f"f{I}.u{r}.role", ["חיילים", "קצינים"], blank=False)}</td>
          <td class="n">{inp(f"f{I}.u{r}.n", "num", "num")}</td><td class="n">{inp(f"f{I}.u{r}.lvl", "num", "num")}</td>
          <td class="n">{inp(f"f{I}.u{r}.mv", "num", "num")}</td>"""
        + "".join(f'<td class="f">{chk(f"f{I}.u{r}.{k}")}</td>' for k, _ in flags) + "</tr>"
        for r in range(8))
    pcts = "".join(f'<td class="f">{out(f"f{I}.pct.{k}", "r-pct")}</td>' for k, _ in flags)
    comp = f"""      <div class="panel">
        <h2 class="box-title">הרכב הכוח <span class="hint">דרגה, או ממוצע קוביות פגיעה למפלצות (לקצינים מפלצות: ועוד 1). תנועה במטרים לתור.
          „מיוחד”: מפלצת עם שתי כוכביות או יותר</span></h2>
        <table class="r-table r-comp">
          <thead><tr><th>יחידה</th><th class="w-role2">תפקיד</th><th class="c">מספר</th><th class="c">דרגה</th><th class="c">תנועה</th>{heads}</tr></thead>
          <tbody>{rows}</tbody>
          <tfoot><tr><td colspan="2">סך הכוח</td><td class="o">{out(f"f{I}.total")}</td><td></td><td class="o">{out(f"f{I}.avgMv")}</td>{pcts}</tr></tfoot>
        </table>
        <div class="r-under">{chk(f"f{I}.elves", "כל הכוח אלפים, או כל הכוח גמדים")}<span class="r-warn" data-out="f{I}.warn"></span></div>
      </div>"""
    leader = f"""        <div class="panel">
          <h2 class="box-title">המנהיג</h2>
          {field("שם", inp(f"f{I}.lead.name", "write"))}
          <div class="r-mini">
            <label><span class="label">דרגה</span>{inp(f"f{I}.lead.lvl", "num", "num")}</label>
            <label><span class="label">תבונה</span>{inp(f"f{I}.lead.int", "num", "num")}</label>
            <label><span class="label">חוכמה</span>{inp(f"f{I}.lead.wis", "num", "num")}</label>
            <label><span class="label">כריזמה</span>{inp(f"f{I}.lead.cha", "num", "num")}</label>
          </div>
          <p class="hint r-note">הבונוסים של תבונה, חוכמה וכריזמה מתווספים לדרגה (עמוד 9).</p>
        </div>"""
    train = f"""        <div class="panel">
          <h2 class="box-title">ניסיון ואימון</h2>
          {line("ניצחונות ב-10 השנים האחרונות", inp(f"f{I}.wins", "num r-small", "num"), "עד 10")}
          {line("תבוסות (מנוסות) באותו זמן", inp(f"f{I}.routs", "num r-small", "num"), "עד 10")}
          {line("שבועות אימון השנה", inp(f"f{I}.weeks", "num r-small", "num"), "עד 20")}
          {line("שבועות אימון עם המנהיג", inp(f"f{I}.lweeks", "num r-small", "num"), "עד 20")}
          {line("חודשים בשירות השנה", inp(f"f{I}.months", "num r-small", "num"), "עד 12")}
        </div>"""
    equip = f"""        <div class="panel">
          <h2 class="box-title">ציוד</h2>
          {line("איכות הנשק", sel(f"f{I}.wq", ["ממוצע", "טוב", "מצויין"], "r-mid", blank=False), "טוב: מחיר כפול, מצויין: משולש")}
          {line(chk(f"f{I}.w2", "נשק שני מאותה איכות"), "")}
          {line(chk(f"f{I}.ac5", "דירוג שריון ממוצע 5 ומטה"), "")}
          <div class="r-sep"></div>
          <span class="label">ציוד ואספקה</span>
          {inp(f"f{I}.gear1", "r-lineinp")}{inp(f"f{I}.gear2", "r-lineinp")}
        </div>"""
    factors = "".join(line(n, out(f"f{I}.{k}"), h) for k, n, h in [
        ("lead", "מנהיגות", "דרגה + בונוסים + 2 לכל 1% בדרגת שם"),
        ("exp", "ניסיון", "קצינים ×3, חיילים ×2, ניצחונות ותבוסות"),
        ("trn", "אימונים", ""), ("eqp", "ציוד", ""), ("spc", "חיילים מיוחדים", "אלפים/גמדים 15, או 2 לכל 1% מיוחד")])
    conds = "".join(f'<li data-out="f{I}.c{i}"><b>{l}</b> {t}</li>' for i, (l, t) in enumerate(BR_CONDITIONS))
    rating = f"""      <div class="panel r-rating">
        <div class="r-factors">
          <h2 class="box-title">דירוג הכוח הבסיסי (דכ״ב)</h2>
          {factors}
          {line("דכ״ב", out(f"f{I}.bfr", "r-big"), "", "r-total")}
          {line("רמת היחידה", f'<b data-out="f{I}.cls"></b>')}
        </div>
        <div class="r-br">
          <h2 class="box-title">דירוג הקרב (ד״ק) <span class="hint">מוסיפים את הבונוס על כל משפט נכון</span></h2>
          <ul class="r-conds">{conds}</ul>
          <div class="r-br-sum">
            <div><span class="label">בונוס</span>{out(f"f{I}.bonus")}<span class="hint">דכ״ב ÷ 10</span></div>
            <div><span class="label">משפטים נכונים</span>{out(f"f{I}.count")}</div>
            <div><span class="label">ד״ק</span>{out(f"f{I}.br", "r-huge")}</div>
          </div>
        </div>
      </div>"""
    cmd_rows = "".join(f"<tr><td>{inp(f'f{I}.c{r}.name')}</td><td>{inp(f'f{I}.c{r}.role')}</td><td>{inp(f'f{I}.c{r}.cls')}</td>"
                       f"<td class=\"n\">{inp(f'f{I}.c{r}.lvl', 'num', 'num')}</td><td>{inp(f'f{I}.c{r}.note')}</td></tr>"
                       for r in range(4))
    cmds = f"""      <div class="panel">
        <h2 class="box-title">פירוט מפקדים</h2>
        <table class="r-table">
          <thead><tr><th>שם</th><th>תפקיד</th><th>מקצוע</th><th class="c w-n">דרגה</th><th>הערות</th></tr></thead>
          <tbody>{cmd_rows}</tbody>
        </table>
      </div>"""
    head = f"""      <header class="r-head">
        <div class="brand"><h1>כוח <span data-out="f{I}.num"></span></h1>
          <button type="button" class="r-del screen-only" data-del-force="{I}">מחיקת הכוח</button>
          <span class="class-tag">מכונת המלחמה</span></div>
        <div class="r-fields r-fields-3">{field("שם הכוח", inp(f"f{I}.name", "write"))}{field("הצבא", inp(f"f{I}.army", "write"))}{field("נאמן ל", inp(f"f{I}.liege", "write"))}</div>
      </header>"""
    return f"""{head}
{comp}
      <div class="r-three">
{leader}
{train}
{equip}
      </div>
{rating}
{cmds}"""


def army_summary():
    pairs = [("1.5", 15), ("2", 30), ("3", 45), ("4", 60), ("5", 70), ("6", 80), ("7", 90), ("8–10", 100),
             ("11–15", 110), ("16–20", 120), ("21–30", 130), ("31–40", 140), ("41–50", 150), ("51–60", 160)]
    ratio = "".join(
        "<tr>" + "".join(f'<td class="c"><span class="num-ltr">{a}:1</span></td><td class="c">+{b}</td>' for a, b in pairs[k:k + 7]) + "</tr>"
        for k in (0, 7))
    crt = "".join(f"<tr><td class=\"c\">{a}</td><td class=\"c\">{b}</td><td class=\"c\">{c}</td><td class=\"c\">{d}</td>"
                  f"<td class=\"c\">{e}</td><td class=\"c\">{f}</td><td class=\"c\">{g}</td></tr>" for a, b, c, d, e, f, g in COMBAT_RESULTS)
    tc = "".join(f"<tr><td class=\"c\">{a}</td><td>{b}</td></tr>" for a, b in TROOP_CLASSES)
    return f"""      <header class="hd2"><h1>הצבא</h1><span></span></header>
      <div class="panel">
        <h2 class="box-title">כל הכוחות <span class="hint">מתמלא לבד מדפי הכוחות</span></h2>
        <table class="r-table r-sum">
          <thead><tr><th class="c w-n">#</th><th>כוח</th><th>מנהיג</th><th class="c">חיילים</th><th class="c">דכ״ב</th><th>רמת היחידה</th><th class="c">ד״ק</th></tr></thead>
          <tbody data-out="summary"></tbody>
          <tfoot><tr><td colspan="3">סך הכול</td><td class="o">{out("sumTroops")}</td><td colspan="3"></td></tr></tfoot>
        </table>
      </div>
      <div class="two-up r-battle">
        <div class="panel">
          <h2 class="box-title">בקרב: מוסיפים לד״ק <span class="hint">ואז כל צד מגלגל ק100 ומוסיף</span></h2>
          <p class="r-small-text"><b>יחס כוחות</b> (רק לצד הגדול, אחד בלבד; 1.01 עד 1.5 נחשב 1.5, וכך הלאה):</p>
          <table class="r-table r-reftable r-ratio">{ratio}</table>
          <p class="r-small-text"><b>מוראל:</b> +10 בדומיניון של האדון; +10 אם הביסו את האויב הזה בעבר;
            +10 אם רמת היחידה גבוהה בשתיים מהאויב; +30 בתקיפת אויב בתנועה; −10 אם כוח מלווה נס.</p>
          <p class="r-small-text"><b>סביבה:</b> ±25 בסביבה ידידותית או עוינת במיוחד; +20 בקרב לילה אם לכל הכוח זיוונות.</p>
          <p class="r-small-text"><b>פני שטח:</b> +20 בגובה רב מהיריב; +20 זוטונים בשדות וביערות; +10 אלפים ביערות;
            +20 גמדים בגבעות ובהרים; −20 לכוח עם רוכבים בהרים, ביערות או במבצר; −20 בבוץ; −10 בשלג או בחול.</p>
          <p class="r-small-text"><b>למגן בלבד:</b> +10 מחזיק במקום; +50 מעבר צר או גשר; +40 התוקף חוצה מים עמוקים;
            +20 הרים, גבעות, שטח קשה או מאחורי חומה; +50 בתוך מבצר. (כשכל התוקפים עפים: בלי; כש-5% עפים: חצי.)</p>
          <p class="r-small-text"><b>חסינות</b> (אחת): +150 חסין להתקפות האויב; +50 אם 1% מהכוח חסין; +50 חסין ל-80% מההתקפות.
            <b>עייפות</b> (אחת): −10 בינונית, −30 גדולה.</p>
          <p class="r-small-text"><b>מצור:</b> המגן מכפיל את חייליו ב-4 ליחס הכוחות, מתעלם מנסיגה ומנוסה, וסופג חצי נפגעים.
            התוקף שמטיל מצור מקבל +5 לכל שבוע.</p>
        </div>
        <div class="panel">
          <h2 class="box-title">תוצאות הקרב <span class="hint">לפי הפער בין התוצאות</span></h2>
          <table class="r-table r-crt">
            <thead><tr><th rowspan="2" class="c">פער</th><th colspan="2" class="c">נפגעים</th><th colspan="2" class="c">עייפות</th><th colspan="2" class="c">מיקום</th></tr>
              <tr><th class="c">מנצח</th><th class="c">מפסיד</th><th class="c">מנצח</th><th class="c">מפסיד</th><th class="c">מנצח</th><th class="c">מפסיד</th></tr></thead>
            <tbody>{crt}</tbody>
          </table>
          <p class="hint r-note">נפגעים: חצי מתים וחצי פצועים; פצועים חוזרים בעוד ק4 חודשים אם הכוח מחזיק בשדה.
            עייפות: ל לא עייף, ב בינונית, מ גדולה (ק4 ימים לכל שלב). מיקום: ש מחזיק בשדה, נ נסוג, +מספר יחידות שטח.
            מנוסה: הכוח מתפרק, והשורדים חוזרים הביתה בעוד ק10 שבועות.</p>
          <h2 class="box-title r-gap">רמות היחידה</h2>
          <table class="r-table r-reftable r-tc">{tc}</table>
        </div>
      </div>"""


# ---------------------------------------------------------------- output

NOTE = ('<a href="../index.html">← חזרה לדפי הדמות</a><br>{what} '
        "הכול נשמר בדפדפן הזה בלבד. "
        '<button type="button" class="clear-all" data-clear-all>ניקוי הדף</button>{extra}<br>'
        "להדפסה: Ctrl+P ← גודל נייר A4, שוליים: ללא.")


def write_pages(out_dir, document):
    dom = "".join([
        page(1, 3, dominion_page1(), "דומיניון"),
        page(2, 3, dominion_page2(), "יועצים ומומחים"),
        page(3, 3, dominion_page3(), "עזר לשליט"),
    ])
    note = NOTE.format(what="ממלאים את השדות והחישובים נעשים לבד: הכנסות, הוצאות, אוצר ורמת האמון.", extra="")
    (out_dir / "dominion.html").write_text(
        document("דף דומיניון", f'<div class="r-doc" data-kind="dominion">{dom}</div>', note, SCRIPT),
        encoding="utf-8", newline="\n")
    tpl = page("__N__", "__T__", force_page(), "כוח", ' data-force="__I__"')
    army = (f'<template id="force-tpl">{tpl}</template><div class="r-forces"></div>'
            + page("__S__", "__T__", army_summary(), "הצבא", ' data-summary'))
    note = NOTE.format(what="דף לכל כוח: ממלאים את ההרכב, וה-דכ״ב, רמת היחידה וה-ד״ק מחושבים לבד.",
                       extra=' <button type="button" class="clear-all" data-add-force>הוספת כוח</button>')
    (out_dir / "army.html").write_text(
        document("דף צבא", f'<div class="r-doc" data-kind="army">{army}</div>', note, SCRIPT),
        encoding="utf-8", newline="\n")
    print("wrote dominion.html, army.html")
    cards = [
        ("dominion.html", "ד", "דומיניון", "Dominion", "האדמה שהדמות שולטת בה: משושים, משפחות, הכנסות והוצאות, אוצר ורמת האמון של העם.",
         ["דומיניון", "יועצים ומומחים", "עזר לשליט"], "3 עמודים"),
        ("army.html", "צ", "צבא", "War Machine", "מכונת המלחמה: הרכב כל כוח, דירוג הכוח הבסיסי, רמת היחידה ודירוג הקרב, ומפקדים.",
         ["דף לכל כוח", "סיכום הצבא", "תוצאות קרב"], "עמוד לכל כוח ועוד אחד"),
    ]
    return "\n".join(f"""    <a class="card" href="sheets/{f}">
      <div class="card-head">
        <span class="badge" aria-hidden="true">{b}</span>
        <div><h2>{n}</h2><span class="en">{en}</span></div>
      </div>
      <p class="tagline">{t}</p>
      <ul class="pages" aria-label="תוכן">{"".join(f"<li>{c}</li>" for c in cs)}</ul>
      <span class="open">פתיחת הדף ({pg})<span class="arrow" aria-hidden="true">←</span></span>
    </a>""" for f, b, n, en, t, cs, pg in cards)
