"""Generate printable Hebrew character sheets (A4, RTL) for the D&D Rules Cyclopedia.

Writes into sheets/:
    dwarf.html, cleric.html, magic-user.html, thief.html
and index.html, a page that links to them.

Class tables live in data/tables.py and spells in data/spells.py, both transcribed from the
Rules Cyclopedia. Hebrew terms follow the Basic Fantasy Hebrew glossary (bfrpg/translator).
Layout and styles (sheet.css) come from the Basic Fantasy Hebrew sheets in bfrpg/printable-sheets.

Usage:
    python make_sheets.py
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "data"))
import spells as SP  # noqa: E402
import tables as T  # noqa: E402

OUT = HERE / "sheets"
CSS = (HERE / "sheet.css").read_text(encoding="utf-8")
FOOT = "חוקי המבוכים והדרקונים (Rules Cyclopedia), דף דמות בעברית"


# ---------------------------------------------------------------- small helpers

def ltr(v):
    return f'<span class="num-ltr">{v}</span>'


def dice(v):
    """Hebrew dice notation, e.g. '9ק8+2': an RTL container with LTR number atoms (see bfrpg dice-he.lua).

    Inside a plain LTR span the strong-RTL letter ק makes the bidi algorithm show '1ק8' as 'ק18'.
    """
    m = re.fullmatch(r"(\d*)ק(\d+)(?:([+-])(\d+))?", v.strip())
    if not m:
        return ltr(v)
    count, sides, sign, mod = m.groups()
    atom = '<span dir="ltr">{}</span>'.format
    parts = ([atom(count)] if count else []) + ["ק", atom(sides)]
    if sign:
        parts += [f'<span class="mod" dir="ltr">{sign}</span>', atom(mod)]
    return '<span class="dice">' + "".join(parts) + "</span>"


def dice_in(text):
    """Wrap every dice expression inside a longer Hebrew text."""
    return re.sub(r"\d*ק\d+(?:[+-]\d+)?", lambda m: dice(m.group(0)), text)


def xp(n):
    return f"{n:,}"


def cells(n, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<td{c}></td>" for _ in range(n))


def hit_dice(level, die, extra):
    """'Nק<die>' up to level 9, then '9ק<die>+X' with `extra` hit points per level after 9th."""
    return f"{level}ק{die}" if level <= 9 else f"9ק{die}+{extra * (level - 9)}"


# ---------------------------------------------------------------- class data

def human_levels(xp_table, die, extra, thac0, saves, spells=None):
    rows = []
    for lv in range(1, 37):
        rows.append(dict(level=str(lv), xp=xp(xp_table[lv - 1]), hd=hit_dice(lv, die, extra),
                         thac0=T.by_range(thac0, lv), saves=T.by_range(saves, lv),
                         spells=(spells or {}).get(lv)))
    return rows


def dwarf_levels():
    rows = []
    for lv in range(1, 12):
        rows.append(dict(level=str(lv), rank="", xp=xp(T.DWARF_XP[lv - 1]), hd=hit_dice(lv, 8, 3),
                         thac0=T.by_range(T.THAC0_FIGHTER, lv), saves=T.by_range(T.DWARF_SAVES, lv)))
    for i, (rank, need) in enumerate(T.DWARF_RANKS):
        rows.append(dict(level="12" if i == 0 else "", rank=T.RANK_HE[rank], xp=xp(need), hd=hit_dice(12, 8, 3),
                         thac0=T.THAC0_RANK[rank], saves=T.by_range(T.DWARF_SAVES, 12), is_rank=i > 0))
    return rows


BOOK_HINT = ("<b>בספר:</b> סמנו בעט כל לחש שכתוב בספר הלחשים שלכם. "
             "<b>שיננתי:</b> בכל בוקר סמנו בעיפרון את הלחשים שבחרתם להיום, רק מתוך הלחשים שבספר, "
             "ולפי מספר הלחשים ליום בטבלה. לחש שהוטל נשכח, אז מוחקים את הסימון.")

CLASSES = {
    "dwarf": dict(
        name="גמד", file="dwarf.html", max_level="12, ואחריה דרגות התקפה",
        hd="ק8; מדרגה 10: <span class=\"num-ltr\">+3</span> נק״פ",
        prime="כוח (וכושר 9 לפחות)", armor="כל שריון ומגן",
        weapons="נשק קטן או בינוני; קשת קצרה ורובה קשת, לא קשת ארוכה",
        levels=dwarf_levels(),
        about=[
            "<b>זיוונות:</b> רואה חום בחושך עד 20 מ׳. לא עובדת ליד אור רגיל או קסום, ולא מספיקה כדי לקרוא.",
            "<b>גילוי:</b> מחפש מלכודות בבנייה, קירות זזים, מעברים משופעים ובנייה חדשה. המנחה מגלגלת ק6, הצלחה ב-1–2.",
            "<b>שפות:</b> מדוברת, שפת הנטייה, ועוד גמדים, נומים, גובלינים וקובולדים.",
            "<b>תמרוני לוחם:</b> תקיפה ברומח, וכיוון חנית כנגד הסתערות. ב-660,000 נק״נ: אפשרויות הקרב של הלוחם (שתי התקפות בסיבוב), ב-2,200,000 נק״נ: שלוש.",
            "<b>אחרי דרגה 12:</b> הגמד לא עולה בדרגה, אבל צובר <b>דרגות התקפה</b> (ג עד מ) שמשפרות את ה-THAC0.",
            "<b>ב-1,400,000 נק״נ:</b> חצי נזק מלחשים ומיכולות דמויות לחש (רבע נזק בגלגול הצלה מוצלח). לא כולל נשיפת דרקון.",
            "<b>דרישה ראשית:</b> כוח 13–15 נותן <span class=\"num-ltr\">+5%</span> נק״נ, כוח 16–18 נותן <span class=\"num-ltr\">+10%</span>.",
        ],
    ),
    "cleric": dict(
        name="כוהן", file="cleric.html", max_level="36",
        hd="ק6; מדרגה 10: <span class=\"num-ltr\">+1</span> נק״פ",
        prime="חוכמה", armor="כל שריון ומגן",
        weapons="נשק קהה בלבד: בלי להב ובלי חוד (גם לא חצים)",
        levels=human_levels(T.CLERIC_XP, 6, 1, T.THAC0_CTD, T.CLERIC_SAVES, T.CLERIC_SPELLS),
        spell_levels=7, spells=SP.CLERIC,
        spell_mode="prepared", spell_title="הלחשים שלי",
        custom=("מתנות מהאל", "לחש מיוחד שהאל העניק רק לך"),
        spell_hint=("לכוהן אין ספר לחשים: אחרי שינה טובה הוא מתפלל שעה ומקבל את לחשיו, החל מדרגה 2. "
                    "<b>הכנתי היום:</b> סמנו בעיפרון את הלחשים שבחרתם להיום, לפי מספר הלחשים ליום בטבלה. "
                    "לחש שהוטל נעלם, אז מוחקים את הסימון. לחש הפיך אפשר להטיל הפוך."),
        about=[
            "<b>לחשים:</b> מדרגה 2. כמה לחשים מכל עוצמה ביום, לפי הטבלה. הכוהן יכול לבחור כל לחש כוהנים שהוא מספיק מנוסה להטיל.",
            "<b>לחש הפיך</b> (מסומן ברשימה): מטילים אותו הפוך. כוהני סדר עושים זאת רק בסכנת חיים.",
            "<b>גירוש אל-מתים:</b> במקום לתקוף. מצליבים את הדרגה עם סוג האל-מת בטבלה בעמוד 3.",
            "<b>דרגה 9:</b> הכוהן נקרא פטריארך או מטריארך, ויכול לבנות מבצר. כוהן ניטרלי יכול להפוך לדרואיד.",
            "<b>דרישה ראשית:</b> חוכמה 13–15 נותנת <span class=\"num-ltr\">+5%</span> נק״נ, חוכמה 16–18 נותנת <span class=\"num-ltr\">+10%</span>.",
        ],
    ),
    "mu": dict(
        name="קוסם", file="magic-user.html", max_level="36",
        hd="ק4; מדרגה 10: <span class=\"num-ltr\">+1</span> נק״פ",
        prime="תבונה", armor="אסור שריון ואסור מגן", weapons="פגיון בלבד",
        levels=human_levels(T.MU_XP, 4, 1, T.THAC0_MU, T.MU_SAVES, T.MU_SPELLS),
        spell_levels=9, spells=SP.MU,
        spell_mode="book", spell_title="ספר הלחשים",
        custom=("לחשים מיוחדים", "לחש שהקוסם חקר בעצמו, או מצא במגילה או בספר עתיק"),
        spell_hint=BOOK_HINT,
        about=[
            "<b>ספר הלחשים:</b> המורה נותן ספר עם 2 לחשים מעוצמה 1. בדרגה 2 הוא מוסיף לחש מעוצמה 1, בדרגה 3 לחש מעוצמה 2, ובדרגה 4 עוד לחש מעוצמה 2. מכאן מחפשים לחשים לבד.",
            "<b>לחשים ביום:</b> לפי הטבלה. כל לחש שמוטל נשכח, עד שלומדים אותו שוב מהספר אחרי שינה טובה.",
            "<b>נשקים:</b> פגיון בלבד. באישור המנחה גם מטה, צינור נשיפה, שמן בוער, מים קדושים, רשת, אבן, קלע ושוט.",
            "<b>בלי שריון ובלי מגן.</b> הקוסם הכי חלש בקרב, ויש לו הכי מעט נקודות פגיעה.",
            "<b>דרישה ראשית:</b> תבונה 13–15 נותנת <span class=\"num-ltr\">+5%</span> נק״נ, תבונה 16–18 נותנת <span class=\"num-ltr\">+10%</span>.",
        ],
    ),
    "thief": dict(
        name="גנב", file="thief.html", max_level="36",
        hd="ק4; מדרגה 10: <span class=\"num-ltr\">+2</span> נק״פ",
        prime="זריזות", armor="שריון עור בלבד, בלי מגן", weapons="כל כלי ירייה, וכל נשק ביד אחת",
        levels=human_levels(T.THIEF_XP, 4, 2, T.THAC0_CTD, T.THIEF_SAVES),
        about=[
            "<b>מיומנויות גנב:</b> מגלגלים ק100 (שתי קוביות ק10). הצלחה אם התוצאה שווה לאחוז או נמוכה ממנו. אחוזים בעמוד 3.",
            "<b>מעל 100%:</b> במשימה קשה המנחה מורידה מחסר מהאחוז. אם נשאר 100% או יותר, מצליחים.",
            "<b>דקירה מאחור:</b> מתגנבים אל יריב שלא שם לב, עם נשק ביד אחת לקרב פנים אל פנים: <span class=\"num-ltr\">+4</span> להתקפה ונזק כפול.",
            "<b>דרגה 4:</b> קריאת כל כתב או שפה רגילים (לא כתב קסום) בסיכוי 80%. נכשלתם? מנסים שוב רק בדרגה הבאה.",
            "<b>דרגה 10:</b> הטלת לחשי קוסם ממגילה. בסיכוי 10% הלחש משתבש.",
            "<b>דרישה ראשית:</b> זריזות 13–15 נותנת <span class=\"num-ltr\">+5%</span> נק״נ, זריזות 16–18 נותנת <span class=\"num-ltr\">+10%</span>.",
        ],
    ),
}


# ---------------------------------------------------------------- page parts

def field(label, value=None):
    inner = f'<div class="filled">{value}</div>' if value else '<div class="write"></div>'
    return f'<div class="field"><span class="label">{label}</span>{inner}</div>'


def page(n, total, inner, label):
    return f"""
  <section class="sheet" aria-label="עמוד {n}: {label}">
    <div class="page">
{inner}
      <div class="foot"><span>{FOOT}</span><span>עמוד {n} מתוך {total}</span></div>
    </div>
  </section>"""


def abilities_panel():
    rows = [
        ("כוח", "פגיעה ונזק בקרב פנים אל פנים"),
        ("תבונה", "שפות; התכונה של הקוסם"),
        ("חוכמה", "הצלה נגד לחשים; התכונה של הכוהן"),
        ("זריזות", "ירי, דירוג שריון ויוזמה"),
        ("כושר", "נקודות פגיעה"),
        ("כריזמה", "איך אחרים מגיבים אליך"),
    ]
    abs_ = "".join(
        f'<div class="ab"><div class="ab-name">{n}<span class="hint">{h}</span></div><div class="cell score"></div><div class="mod"></div></div>'
        for n, h in rows)
    return f"""<div class="panel">
            <h2 class="box-title">תכונות</h2>
            <div class="ab-head label"><span></span><span>ערך</span><span>בונוס</span></div>
            <div class="abilities">{abs_}</div>
          </div>"""


def saves_panel():
    rows = "".join(f'<div class="row"><span>{n}</span><div class="cell"></div></div>' for n in T.SAVE_NAMES)
    return f"""<div class="panel saves">
            <h2 class="box-title">גלגולי הצלה <span class="hint">ק20, שווה או יותר. הערכים בעמוד 2</span></h2>
            {rows}
            <div class="note"><span class="label">בונוס חוכמה נגד לחשים קסומים</span><div class="write"></div></div>
          </div>"""


def combat_strip():
    return """<div class="combat">
            <div class="stat">
              <span class="label">דירוג שריון</span>
              <div class="shield" aria-hidden="true">
                <svg viewBox="0 0 46 50"><path d="M23 2 L43 8 V24 C43 36 34 44 23 48 C12 44 3 36 3 24 V8 Z" fill="#fff" stroke="#221c18" stroke-width="2.2" stroke-linejoin="round"/></svg>
              </div>
            </div>
            <div class="stat">
              <span class="label">נקודות פגיעה</span>
              <div class="hp">
                <div class="field"><div class="cell"></div><span class="hint">מרבי</span></div>
                <div class="field"><div class="cell"></div><span class="hint">עכשיו (בעיפרון)</span></div>
              </div>
            </div>
            <div class="stat"><span class="label">THAC0</span><div class="cell big"></div></div>
            <div class="stat"><span class="label">תנועה</span><div class="cell big"></div></div>
          </div>"""


HOWTO = """<p class="howto"><b>איך תוקפים?</b> THAC0 הוא המספר שצריך לגלגל כדי לפגוע ביריב עם דירוג שריון 0.
מגלגלים ק20 ומוסיפים בונוס <b>כוח</b> בקרב פנים אל פנים או בונוס <b>זריזות</b> בירי.
פגעתם אם התוצאה שווה ל-THAC0 פחות דירוג השריון של היריב, או גבוהה ממנו. בקרב פנים אל פנים מוסיפים את בונוס הכוח גם לנזק.</p>"""


def weapons_panel(rows=4):
    body = "".join(f"<tr>{cells(8)}</tr>" for _ in range(rows))
    return f"""<div class="panel">
            <h2 class="box-title">נשקים</h2>
            <table class="weapons">
              <thead>
                <tr>
                  <th rowspan="2">נשק</th>
                  <th class="c" rowspan="2" style="width:4.4em">רמת<br>שליטה</th>
                  <th class="c" rowspan="2" style="width:4em">פגיעה</th>
                  <th class="c" rowspan="2" style="width:4.4em">נזק</th>
                  <th class="c" colspan="3">טווח (מ׳)</th>
                  <th rowspan="2" style="width:6em">הערות</th>
                </tr>
                <tr class="sub">
                  <th class="c" style="width:2.8em">קצר</th>
                  <th class="c" style="width:2.8em">בינוני</th>
                  <th class="c" style="width:2.8em">ארוך</th>
                </tr>
              </thead>
              <tbody>{body}</tbody>
            </table>
          </div>"""


def lined_panel(title, extra="", grow=False):
    style = "display:flex; flex-direction:column" + ("; flex:1; min-height:0" if grow else "")
    return f"""<div class="panel" style="{style}">
              <h2 class="box-title">{title}</h2>
              <div class="lined-box"><div class="lines"></div></div>
              {extra}
            </div>"""


def spells_day_panel(levels, extra="", hint="לפי עוצמת לחש"):
    lv = "".join(f'<span class="lvl">{i}</span>' for i in range(1, levels + 1))
    boxes = '<div class="cell"></div>' * levels
    return f"""<div class="panel">
                <h2 class="box-title">לחשים ליום <span class="hint">{hint}</span></h2>
                <div class="spells-day" style="grid-template-columns: repeat({levels}, 1fr)">{lv}{boxes}</div>
                {extra}
              </div>"""


def class_box(key, cfg):
    """Right-hand column at the bottom of page 1."""
    if key == "dwarf":
        return """<div class="panel">
                <h2 class="box-title">דרגת התקפה <span class="hint">אחרי דרגה 12, לפי עמוד 2</span></h2>
                <div class="write" style="height:1.6em"></div>
              </div>
              <div class="note-box"><b>זיוונות</b> עד 20 מ׳. <b>גילוי</b> מלכודות ובנייה: 1–2 בק6 (המנחה מגלגלת).</div>
              <div class="note-box"><b>שפות:</b> גמדים, נומים, גובלינים, קובולדים.</div>""" + lined_panel("אויבים שהבסתי", grow=True)
    if key == "thief":
        rows = "".join(f'<div class="row"><span>{s}</span><div class="cell"></div></div>' for s in T.THIEF_SKILL_NAMES)
        return f"""<div class="panel skills">
                <h2 class="box-title">מיומנויות גנב <span class="hint">האחוזים בעמוד 3</span></h2>
                {rows}
              </div>
              <div class="note-box"><b>דקירה מאחור:</b> מאחורי יריב שלא שם לב,
                <span class="num-ltr">+4</span> להתקפה ונזק כפול.</div>"""
    if key == "cleric":
        return spells_day_panel(
            7, '<div class="turn"><span class="label">האל או האמונה שלי</span><div class="write"></div></div>',
            "מדרגה 2, לפי עמוד 2") + f"""<div class="note-box"><b>גירוש אל-מתים:</b> מגלגלים 2ק6
                ובודקים בטבלה בעמוד 3.</div>
              <div class="note-box"><b>רשימת הלחשים</b> נמצאת {cfg['spell_where']}.</div>"""
    if key == "mu":
        return spells_day_panel(
            9, '<div class="turn"><span class="label">המורה שלי</span><div class="write"></div></div>',
            "לפי עמוד 2") + f"""<div class="note-box"><b>ספר הלחשים</b> נמצא {cfg['spell_where']}.
                בלי שריון ובלי מגן!</div>"""
    raise KeyError(key)


def page_one(cfg, total):
    key, name = cfg["key"], cfg["name"]
    id_row = field("שם השחקן") + field("נטייה") + field("מקצוע", name) + field("דרגה")
    inner = f"""      <header class="hd">
        <div class="hd-main">
          <div class="brand"><h1>דף דמות</h1><span class="class-tag">{name}</span></div>
          <div class="field name"><span class="label">שם הדמות</span><div class="write"></div></div>
          <div class="id-grid">{id_row}</div>
          <div class="id-grid two">{field("נקודות ניסיון")}{field("נקודות ניסיון לדרגה הבאה")}</div>
        </div>
        <div class="portrait"><span class="hint">ציירו כאן את הדמות</span></div>
      </header>
      <div class="strip">
        <div><span class="label">קוביית פגיעה</span><b>{dice_in(cfg['hd'])}</b></div>
        <div><span class="label">דרישה ראשית</span><b>{cfg['prime']}</b></div>
        <div><span class="label">שריון</span><b>{cfg['armor']}</b></div>
        <div><span class="label">נשקים</span><b>{cfg['weapons']}</b></div>
      </div>
      <div class="body">
        <div class="col">
          {abilities_panel()}
          {saves_panel()}
        </div>
        <div class="col">
          {combat_strip()}
          {HOWTO}
          {weapons_panel()}
          <div class="two-up" style="flex:1; min-height:0">
            {lined_panel("יכולות ומיומנויות כלליות", '<div class="field" style="margin-top:.4em"><span class="label">שפות</span><div class="write"></div></div>')}
            <div class="col" style="gap:.9em">
              {class_box(key, cfg)}
            </div>
          </div>
        </div>
      </div>"""
    return page(1, total, inner, "דף דמות")


# ---------------------------------------------------------------- reference pages

def progression_table(cfg):
    levels = cfg["levels"]
    n_sp = cfg.get("spell_levels", 0)
    rank = cfg["key"] == "dwarf"
    head1 = ("<tr><th rowspan=2>דרגה</th>" + ("<th rowspan=2>דרגת<br>התקפה</th>" if rank else "")
             + "<th rowspan=2>נקודות ניסיון</th><th rowspan=2>קוביות<br>פגיעה</th><th rowspan=2>THAC0</th>"
             + '<th class="grp sep" colspan=5>גלגולי הצלה</th>'
             + (f'<th class="grp sep" colspan={n_sp}>לחשים ביום, לפי עוצמה</th>' if n_sp else "") + "</tr>")
    head2 = ("<tr>" + "".join(f'<th{" class=sep" if i == 0 else ""}>{n}</th>' for i, n in enumerate(T.SAVE_SHORT))
             + "".join(f'<th{" class=sep" if i == 0 else ""}>{i + 1}</th>' for i in range(n_sp)) + "</tr>")
    body = ""
    for r in levels:
        sp = r.get("spells") or []
        sp_cells = "".join(f'<td{" class=sep" if i == 0 else ""}>{sp[i] if i < len(sp) else "–"}</td>' for i in range(n_sp))
        cls = ' class="rank"' if r.get("is_rank") else ""
        body += (f'<tr{cls}><td class="lv">{r["level"]}</td>' + (f'<td class="lv">{r["rank"]}</td>' if rank else "")
                 + f'<td>{r["xp"]}</td><td>{dice(r["hd"])}</td><td>{r["thac0"]}</td>'
                 + "".join(f'<td{" class=sep" if i == 0 else ""}>{s}</td>' for i, s in enumerate(r["saves"]))
                 + sp_cells + "</tr>")
    return f"<table><thead>{head1}{head2}</thead><tbody>{body}</tbody></table>"


def thief_skills_table():
    head = "<tr><th>דרגה</th>" + "".join(f"<th>{s}</th>" for s in T.THIEF_SKILL_NAMES) + "</tr>"
    body = "".join(f'<tr><td class="lv">{lv}</td>' + "".join(f"<td>{v}%</td>" for v in T.THIEF_SKILLS[lv]) + "</tr>"
                   for lv in range(1, 37))
    return f"<table><thead>{head}</thead><tbody>{body}</tbody></table>"


TURN_HE = {"T": "ג", "D": "ה", "D+": "ה+", "D#": "ה#"}


def turn_table():
    head = ("<tr><th>אל-מת</th>" + "".join(f"<th>{lv}</th>" for lv in T.TURN_LEVELS) + "</tr>")
    body = ""
    for u in T.TURN_UNDEAD:
        body += f'<tr><td class="txt"><b>{u}</b></td>' + "".join(
            f"<td>{TURN_HE.get(v, v)}</td>" for v in T.TURN[u]) + "</tr>"
    return f'<table class="turn-table"><thead>{head}</thead><tbody>{body}</tbody></table>'


TURN_LEGEND = ("<b>מספר</b> = מגלגלים 2ק6, ומצליחים בתוצאה שווה או גבוהה יותר. "
               "<b>ג</b> = גירוש בלי לגלגל. <b>ה</b> = השמדה בלי לגלגל. <b>–</b> = אי אפשר לגרש. "
               "<br>בהצלחה המנחה מגלגלת 2ק6: כמה קוביות פגיעה של אל-מתים בורחים (תמיד לפחות אחד). "
               "<b>ה</b> = הם מושמדים במקום לברוח. <b>ה+</b> = השמדה של 3ק6 קוביות פגיעה. <b>ה#</b> = השמדה של 4ק6. "
               "נכשלתם מול אל-מת מסוים? אי אפשר לנסות שוב לגרש אותו באותו קרב.")


def page_ref(cfg, total):
    about = "".join(f"<li>{a}</li>" for a in cfg["about"])
    hint = "דרגות 1–12 ודרגות התקפה" if cfg["key"] == "dwarf" else "דרגות 1–36"
    inner = f"""      <header class="hd2">
        <h1>טבלת ה{cfg['name']}</h1>
        <p class="find-row" style="margin:0">מוצאים את השורה של <b>הדרגה שלכם</b> ומעתיקים את המספרים לעמוד 1. כשעולים דרגה, חוזרים לכאן.</p>
      </header>
      <div class="panel"><h2 class="box-title">מה ה{cfg['name']} יודע לעשות <span class="hint">דרגה מרבית: {cfg['max_level']}</span></h2><ul class="bullets">{about}</ul></div>
      <div class="panel ref dense"><h2 class="box-title">עלייה בדרגה <span class="hint">{hint}</span></h2>{progression_table(cfg)}</div>"""
    return page(2, total, inner, f"טבלת ה{cfg['name']}")


def page_second(cfg, n, total):
    if cfg["key"] == "thief":
        title, box, table, legend = "מיומנויות גנב", "אחוזי הצלחה לפי דרגה", thief_skills_table(), (
            "מגלגלים ק100. הצלחה אם התוצאה שווה לאחוז או נמוכה ממנו. "
            "את מציאת מלכודות, תנועה חרישית, התחבאות בצללים ושמיעת רחשים המנחה מגלגלת בסוד.")
    else:
        title, box, table, legend = "גירוש אל-מתים", "לפי דרגת הכוהן; מגלגלים 2ק6", turn_table(), TURN_LEGEND
    inner = f"""      <header class="hd2">
        <h1>{title}</h1>
        {field("שם הדמות")}
      </header>
      <div class="panel ref dense"><h2 class="box-title">{title} <span class="hint">{dice_in(box)}</span></h2>{table}
        <p class="legend">{dice_in(legend)}</p></div>
      {lined_panel("הערות", grow=True)}"""
    return page(n, total, inner, title)


# ---------------------------------------------------------------- inventory + spells

def page_inventory(n, total):
    def rows(k):
        return "".join('<tr><td></td><td></td><td class="wt"></td><td></td></tr>' for _ in range(k))
    inner = f"""      <header class="hd2">
        <h1>ציוד ומטען</h1>
        {field("שם הדמות")}
      </header>
      <div class="inv-wrap">
        <div class="panel" style="display:flex; flex-direction:column">
          <table class="inv">
            <thead><tr><th>פריט</th><th class="c num">כמות</th><th class="c wt">עומס (מט׳)</th><th class="notes">הערות</th></tr></thead>
            <tbody>
              {rows(30)}
              <tr class="group"><td colspan="4">על החיה או בעגלה</td></tr>{rows(4)}
            </tbody>
            <tfoot><tr><td colspan="2">סה״כ עומס שהדמות נושאת</td><td class="wt"></td><td></td></tr></tfoot>
          </table>
        </div>
        <div class="col">
          <div class="panel armor-rows">
            <h2 class="box-title">שריון ומגן</h2>
            <div class="row head"><span>פריט</span><span>דירוג</span><span>עומס</span></div>
            <div class="row"><div class="write"></div><div class="write"></div><div class="write"></div></div>
            <div class="row"><div class="write"></div><div class="write"></div><div class="write"></div></div>
          </div>
          <div class="panel">
            <h2 class="box-title">מטבעות</h2>
            <div class="coins">
              <div class="coin"><div class="disc">פ״פ</div><div class="cell"></div><span class="hint">פלטינה</span></div>
              <div class="coin"><div class="disc">פ״ז</div><div class="cell"></div><span class="hint">זהב</span></div>
              <div class="coin"><div class="disc">פ״א</div><div class="cell"></div><span class="hint">אלקטרום</span></div>
              <div class="coin"><div class="disc">פ״כ</div><div class="cell"></div><span class="hint">כסף</span></div>
              <div class="coin"><div class="disc">פ״נ</div><div class="cell"></div><span class="hint">נחושת</span></div>
            </div>
          </div>
          <div class="panel">
            <h2 class="box-title">עומס <span class="hint">ביחידות מט׳ (מטבעות)</span></h2>
            <div class="field"><span class="label">תנועה עם העומס</span><div class="write"></div></div>
          </div>
          <div class="panel" style="display:flex; flex-direction:column; flex:1; min-height:0">
            <h2 class="box-title">הערות <span class="hint">חפצים קסומים: מטענים, מילות הפעלה, מה החפץ עושה</span></h2>
            <div class="lined-box"><div class="lines"></div></div>
          </div>
        </div>
      </div>"""
    return page(n, total, inner, "ציוד")


def spellbook_chunks(spells, capacity=44, reserve=0):
    """Split spell levels into pages; a level never breaks across pages. Each level costs its rows + a header row."""
    pages, cur, used = [], [], 0
    for lv in sorted(spells):
        cost = len(spells[lv]) + 1
        if cur and used + cost > capacity:
            pages.append(cur)
            cur, used = [], 0
        cur.append(lv)
        used += cost
    if cur:
        pages.append(cur)
    # The last page also holds the custom-spells panel; move its last level to a new page if they don't fit.
    if len(pages[-1]) > 1 and used + reserve > capacity:
        pages.append([pages[-1].pop()])
    return pages


def spell_heads(book):
    if book:
        return '<th class="c" style="width:3.2em">בספר</th><th class="c" style="width:3.6em">שיננתי</th>'
    return '<th class="c" style="width:4.6em">הכנתי היום</th>'


def page_spell_list(n, total, cfg, levels, first, last, custom_rows):
    book = cfg["spell_mode"] == "book"
    ncols = 5 if book else 4
    rows = ""
    for lv in levels:
        rows += f'<tr class="group"><td colspan="{ncols}">לחשים מעוצמה {lv}</td></tr>'
        for s in sorted(cfg["spells"][lv], key=lambda s: s["he"]):
            tags = ' <span class="tag light">הפיך</span>' if s["reversible"] else ""
            boxes = '<td class="chk"><i></i></td>' * (2 if book else 1)
            rows += (f'<tr>{boxes}<td class="sname">{s["he"]}{tags}</td>'
                     f'<td>{dice_in(s["range"])}</td><td>{dice_in(s["duration"])}</td></tr>')
    hint = f'<p class="howto">{cfg["spell_hint"]}</p>' if first else ""
    custom = custom_spells_panel(cfg, custom_rows) if last else ""
    inner = f"""      <header class="hd2">
        <h1>{cfg['spell_title']}</h1>
        {field("שם הדמות")}
      </header>
      {hint}
      <div class="panel">
        <table class="spell-list">
          <thead><tr>
            {spell_heads(book)}
            <th>שם הלחש</th>
            <th style="width:10em">טווח</th>
            <th style="width:12em">משך</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>{custom}"""
    return page(n, total, inner, cfg["spell_title"])


def custom_spells_panel(cfg, n_rows):
    book = cfg["spell_mode"] == "book"
    title, hint = cfg["custom"]
    boxes = '<td class="chk"><i></i></td>' * (2 if book else 1)
    body = "".join(f"<tr>{boxes}<td></td><td></td><td></td><td></td></tr>" for _ in range(n_rows))
    return f"""
      <div class="panel custom-spells">
        <h2 class="box-title">{title} <span class="hint">{hint}</span></h2>
        <table class="spell-list">
          <thead><tr>
            {spell_heads(book)}
            <th class="c" style="width:3.6em">עוצמה</th>
            <th>שם הלחש ומה הוא עושה</th>
            <th style="width:8em">טווח</th>
            <th style="width:8em">משך</th>
          </tr></thead>
          <tbody>{body}</tbody>
        </table>
      </div>"""


# ---------------------------------------------------------------- assemble

def sheet_pages(key):
    cfg = dict(CLASSES[key], key=key)
    second = key in ("thief", "cleric")
    n_inv = 4 if second else 3
    custom_rows = 6 if key == "mu" else 10
    chunks = spellbook_chunks(cfg["spells"], reserve=custom_rows + 4) if cfg.get("spells") else []
    total = n_inv + len(chunks)
    if chunks:
        first = n_inv + 1
        cfg["spell_where"] = f"בעמודים {first}–{total}" if len(chunks) > 1 else f"בעמוד {first}"
    pages = [page_one(cfg, total), page_ref(cfg, total)]
    if second:
        pages.append(page_second(cfg, 3, total))
    pages.append(page_inventory(n_inv, total))
    pages += [page_spell_list(n_inv + 1 + i, total, cfg, lv, i == 0, i == len(chunks) - 1, custom_rows)
              for i, lv in enumerate(chunks)]
    return pages


def document(title, body, note):
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700;900&family=Assistant:wght@400;600;700&display=swap">
<style>
{CSS}
</style>
</head>
<body>
<div class="desk" dir="rtl" lang="he">
  <p class="screen-note">{note}</p>
{body}
</div>
</body>
</html>
"""


def print_note(pages):
    return (f'<a href="../index.html">← חזרה לדפי הדמות</a><br>'
            f"{pages} עמודים בגודל A4. להדפסה: Ctrl+P ← גודל נייר A4, שוליים: ללא. "
            "להדפסה דו-צדדית: הפכו לאורך הצד הארוך.")


INDEX = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>דפי דמות לאוגדן הכללים</title>
<meta name="description" content="דפי דמות להדפסה בעברית לחוקי המבוכים והדרקונים (Rules Cyclopedia): גמד, כוהן, קוסם וגנב.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700;900&family=Assistant:wght@400;600;700&display=swap">
<style>
:root {
  --ink:#221c18; --muted:#6b5d50; --paper:#f6f0e4; --card:#fffdf8; --line:#e2d7c5;
  --accent:#7a2a1c; --accent-ink:#fffdf8; --tint:#f1e4d6; --shadow:0 1px 2px rgba(60,40,20,.06), 0 6px 18px rgba(60,40,20,.08);
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --ink:#efe6d8; --muted:#b5a796; --paper:#171411; --card:#221d19; --line:#3a312a;
  --accent:#e08a6e; --accent-ink:#1d1916; --tint:#2e2520; --shadow:0 1px 2px rgba(0,0,0,.3), 0 6px 18px rgba(0,0,0,.35);
} }
:root[data-theme="dark"] {
  --ink:#efe6d8; --muted:#b5a796; --paper:#171411; --card:#221d19; --line:#3a312a;
  --accent:#e08a6e; --accent-ink:#1d1916; --tint:#2e2520; --shadow:0 1px 2px rgba(0,0,0,.3), 0 6px 18px rgba(0,0,0,.35);
}
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:Assistant, sans-serif; line-height:1.55; }
.num-ltr { direction:ltr; unicode-bidi:isolate; }
main { max-width:52rem; margin:0 auto; padding:3rem 1rem 2rem; }
header { text-align:center; margin-bottom:2.5rem; }
.eyebrow { color:var(--accent); font-weight:700; letter-spacing:.04em; font-size:.95rem; margin:0 0 .4rem; }
h1 { font-family:"Frank Ruhl Libre", serif; font-weight:900; font-size:clamp(2rem, 6vw, 3.1rem); line-height:1.1; margin:0 0 .8rem; }
.lead { color:var(--muted); font-size:1.1rem; max-width:34rem; margin:0 auto; }
.rule { width:5rem; height:3px; background:var(--accent); border:0; margin:1.6rem auto 0; border-radius:2px; }
.grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:1.1rem; }
@media (max-width:40rem) { .grid { grid-template-columns:1fr; } }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px; box-shadow:var(--shadow);
  padding:1.4rem 1.3rem 1.2rem; display:flex; flex-direction:column; gap:.9rem; color:inherit; text-decoration:none;
  transition:transform .15s ease, border-color .15s ease; }
.card:hover, .card:focus-visible { transform:translateY(-3px); border-color:var(--accent); outline:none; }
.card-head { display:flex; align-items:center; gap:.85rem; }
.badge { flex:none; width:3.1rem; height:3.1rem; border-radius:50%; display:grid; place-items:center;
  background:var(--tint); color:var(--accent); font-family:"Frank Ruhl Libre", serif; font-weight:900; font-size:1.6rem; }
.card h2 { font-family:"Frank Ruhl Libre", serif; font-weight:900; font-size:1.7rem; margin:0; line-height:1.1; }
.card .en { color:var(--muted); font-size:.85rem; direction:ltr; unicode-bidi:isolate; }
.tagline { margin:0; color:var(--muted); }
dl { margin:0; display:grid; grid-template-columns:auto 1fr; gap:.25rem .8rem; font-size:.95rem; }
dt { color:var(--muted); }
dd { margin:0; font-weight:600; }
.pages { display:flex; flex-wrap:wrap; gap:.35rem; margin:0; padding:0; list-style:none; }
.pages li { background:var(--tint); border-radius:999px; padding:.1rem .65rem; font-size:.82rem; }
.open { margin-top:auto; display:flex; justify-content:space-between; align-items:center;
  border-top:1px solid var(--line); padding-top:.8rem; font-weight:700; color:var(--accent); }
.open .arrow { transition:transform .15s ease; }
.card:hover .arrow { transform:translateX(-4px); }
.howto { margin-top:2.5rem; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1.3rem 1.4rem; }
.howto h3 { font-family:"Frank Ruhl Libre", serif; font-size:1.3rem; margin:0 0 .6rem; }
.howto ol { margin:0; padding-inline-start:1.3rem; display:grid; gap:.3rem; }
footer { text-align:center; color:var(--muted); font-size:.9rem; margin-top:2.5rem; }
footer a { color:var(--accent); }
@media (max-width:30rem) { main { padding-top:2rem; } .card { padding:1.2rem 1rem 1rem; } }
@media (prefers-reduced-motion:reduce) { .card, .arrow { transition:none; } }
</style>
</head>
<body>
<main>
  <header>
    <p class="eyebrow">חוקי המבוכים והדרקונים · Rules Cyclopedia</p>
    <h1>דפי דמות לאוגדן הכללים</h1>
    <p class="lead">דפי דמות בעברית להדפסה על A4, עם טבלאות התקדמות עד דרגה 36, גלגולי הצלה, THAC0 ורשימות לחשים.</p>
    <hr class="rule">
  </header>
  <div class="grid">
CARDS
  </div>
  <section class="howto">
    <h3>איך מדפיסים</h3>
    <ol>
      <li>פותחים את דף הדמות של המקצוע.</li>
      <li>לוחצים <b class="num-ltr">Ctrl+P</b> (במק: <b class="num-ltr">⌘P</b>).</li>
      <li>בוחרים נייר A4, שוליים <b>ללא</b>, ובוחרים הדפסה דו-צדדית עם היפוך לאורך הצד הארוך.</li>
    </ol>
  </section>
  <footer>
    המונחים לקוחים מהמהדורה העברית של אוגדן הכללים ·
    <a href="https://github.com/itaiag/rc-sheets">קוד המקור ב-GitHub</a>
  </footer>
</main>
</body>
</html>
"""

INDEX_INFO = {
    "dwarf": ("Dwarf", "לוחם עיקש מתחת להרים. רואה בחושך, מגלה מלכודות, וממשיך להשתפר בדרגות התקפה אחרי דרגה 12.",
              ["דף דמות", "טבלת דרגות", "ציוד"]),
    "cleric": ("Cleric", "משרת האל: לוחם בנשק קהה, מרפא, ומגרש אל-מתים בכוח האמונה.",
               ["דף דמות", "טבלת דרגות", "גירוש אל-מתים", "ציוד", "לחשים"]),
    "mu": ("Magic-User", "חלש בקרב, אבל ספר הלחשים שלו הופך אותו לדמות החזקה ביותר בדרגות הגבוהות.",
           ["דף דמות", "טבלת דרגות", "ציוד", "ספר לחשים"]),
    "thief": ("Thief", "פותח מנעולים, מפרק מלכודות, מטפס על קירות ודוקר מאחור.",
              ["דף דמות", "טבלת דרגות", "מיומנויות גנב", "ציוד"]),
}


def index_card(key, n_pages):
    cfg = CLASSES[key]
    en, tagline, contents = INDEX_INFO[key]
    pages = "".join(f"<li>{c}</li>" for c in contents)
    return f"""    <a class="card" href="sheets/{cfg['file']}">
      <div class="card-head">
        <span class="badge" aria-hidden="true">{cfg['name'][0]}</span>
        <div><h2>{cfg['name']}</h2><span class="en">{en}</span></div>
      </div>
      <p class="tagline">{tagline}</p>
      <dl>
        <dt>קוביית פגיעה</dt><dd>{cfg['hd'].split(';')[0]}</dd>
        <dt>דרישה ראשית</dt><dd>{cfg['prime']}</dd>
        <dt>דרגות</dt><dd>{cfg['max_level']}</dd>
      </dl>
      <ul class="pages" aria-label="תוכן">{pages}</ul>
      <span class="open">פתיחת הדף ({n_pages} עמודים)<span class="arrow" aria-hidden="true">←</span></span>
    </a>"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    links = []
    for key in ["dwarf", "cleric", "mu", "thief"]:
        cfg = CLASSES[key]
        pages = sheet_pages(key)
        (OUT / cfg["file"]).write_text(
            document(f"דף דמות {cfg['name']}", "".join(pages), print_note(len(pages))),
            encoding="utf-8", newline="\n")
        links.append(index_card(key, len(pages)))
        print("wrote", cfg["file"], len(pages), "pages")
    (HERE / "index.html").write_text(INDEX.replace("CARDS", "\n".join(links)), encoding="utf-8", newline="\n")
    print("wrote index.html")


if __name__ == "__main__":
    main()
