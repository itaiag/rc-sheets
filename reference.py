"""Hebrew web reference ("ספר עזר") for the Rules Cyclopedia: the character classes and the equipment tables.

Screen-first pages that also print on A4, built from data/tables.py and data/equipment.py. Writes into ref/:
    classes.html (overview), one page per class (fighter.html ... mystic.html), equipment.html,
    spells-cleric.html, spells-druid.html, spells-magic-user.html (lists from data/spells.py, notes from data/spell_notes.py).
Rules and page numbers: Hebrew Rules Cyclopedia ch. 2 (classes, pp. 13-31), ch. 4 (equipment, pp. 62-71),
movement p. 88, attack rolls p. 106. Wording follows the Hebrew edition; numbers the English one.
"""
import html
import pathlib
import re

import equipment as E
import spell_notes as SN
import spells as SP
import tables as T
from bidi import dice, fix, ltr

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "ref"


# ---------------------------------------------------------------- small helpers

def num(v):
    """A table cell value: dice, signed and ranged numbers kept in order in RTL."""
    if isinstance(v, int):
        return ltr(f"−{-v}") if v < 0 else f"{v:,}"
    s = str(v)
    if re.fullmatch(r"\d*ק\d+(?:[+-]\d+)?", s):
        return dice(s)
    if s.startswith("−") or re.fullmatch(r"[+±]\d.*", s):
        return ltr(s)
    return fix(s)


def table(head, rows, cls="", cols=None):
    """head: list of header cells (HTML); rows: list of lists of cell HTML, or ('group', title) / ('cls', css, cells)."""
    cols = cols or [""] * len(head)
    th = "".join(f'<th class="{c}">{h}</th>' if c else f"<th>{h}</th>" for h, c in zip(head, cols))
    body = []
    for r in rows:
        tr_cls = ""
        if isinstance(r, tuple) and r[0] == "group":
            body.append(f'<tr class="group"><th colspan="{len(head)}" scope="rowgroup">{r[1]}</th></tr>')
            continue
        if isinstance(r, tuple):
            _, tr_cls, r = r
        tds = "".join(f'<td class="{c}">{v}</td>' if c else f"<td>{v}</td>" for v, c in zip(r, cols))
        body.append(f'<tr class="{tr_cls}">{tds}</tr>' if tr_cls else f"<tr>{tds}</tr>")
    return (f'<div class="tbl"><table class="{cls}"><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def facts(rows):
    return '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{fix(v)}</dd>" for k, v in rows) + "</dl>"


def bullets(items):
    return '<ul class="bullets">' + "".join(f"<li>{fix(i)}</li>" for i in items) + "</ul>"


def note(text):
    return f'<p class="note">{fix(text)}</p>'


def hit_dice(level, die, extra, cap=9):
    """'Nק<die>' up to level `cap`, then 'capק<die>+X' with `extra` hit points per level after it."""
    return f"{level}ק{die}" if level <= cap else f"{cap}ק{die}+{extra * (level - cap)}"


def span(first, last):
    return str(first) if first == last else f"{first}–{last}"


# ---------------------------------------------------------------- shared tables

def level_rows(xp, die, extra, thac0, spells=None, n_spells=0, ranks=None, cap=9, extra_cols=None):
    """Rows for the experience table. Demihumans: `ranks` continue after the last level; the first rank
    comes with the last level (same row), like the book's tables."""
    rows = []
    last = len(xp)
    for lv in range(1, last + 1):
        row = [str(lv), num(xp[lv - 1]), dice(hit_dice(lv, die, extra, cap)), str(T.by_range(thac0, lv))]
        if ranks is not None:
            row.insert(1, T.RANK_HE[ranks[0][0]] if lv == last else "")
        if n_spells:
            got = (spells or {}).get(lv, [])
            row += [str(got[i]) if i < len(got) and got[i] else "–" for i in range(n_spells)]
        if extra_cols:
            row += extra_cols(lv)
        rows.append(row)
    for rank, need in (ranks or [])[1:]:
        row = ["", T.RANK_HE[rank], num(need), dice(hit_dice(last, die, extra, cap)), str(T.THAC0_RANK[rank])]
        if n_spells:
            got = spells[last]
            row += [str(g) for g in got] + ["–"] * (n_spells - len(got))
        rows.append(("row", "rank", row))
    return rows


def level_table(xp, die, extra, thac0, spells=None, n_spells=0, ranks=None, cap=9, extra_head=(), extra_cols=None):
    head = ["דרגה"] + (["דרגת<br>התקפה"] if ranks else []) + ["נק״נ", "קוביות<br>פגיעה", "THAC0"]
    head += [f'<span class="sp">{i}</span>' for i in range(1, n_spells + 1)] + list(extra_head)
    cols = ["n"] * len(head)
    rows = level_rows(xp, die, extra, thac0, spells, n_spells, ranks, cap, extra_cols)
    out = ""
    if n_spells:
        out += f'<p class="cap">לחשים ליום לפי עוצמת לחש: עמודות {ltr(f"1–{n_spells}")}</p>'
    return out + table(head, rows, "levels", cols)


def saves_table(groups, first_row=None, last_note=None):
    head = ["דרגה"] + T.SAVE_NAMES
    rows = [[first_row[0]] + [str(v) for v in first_row[1]]] if first_row else []
    rows += [[ltr(span(a, b))] + [str(v) for v in vals] for a, b, vals in groups]
    out = table(head, rows, "saves", ["n"] * 6)
    return out + (note(last_note) if last_note else "")


SAVES_HOW = "מגלגלים ק20. מצליחים אם התוצאה שווה למספר בטבלה או גבוהה ממנו."
THAC0_HOW = ("THAC0 הוא המספר שצריך לגלגל בק20 כדי לפגוע ביריב עם דירוג שריון 0. "
             "כדי לפגוע בדירוג שריון אחר מחסירים אותו: מול דרג״ש 4 צריך THAC0 פחות 4, מול דרג״ש −2 צריך THAC0 ועוד 2. "
             "מוסיפים לגלגול בונוס כוח בקרב פנים אל פנים ובונוס זריזות בירי (טבלת ההתקפות, עמ׳ 106).")


# ---------------------------------------------------------------- the classes

def turn_table():
    TURN_HE = {"T": "ג", "D": "ה", "D+": "ה+", "D#": "ה#"}
    head = ["אל-מת"] + [ltr(lv) for lv in T.TURN_LEVELS]
    rows = [[f"<b>{u}</b>"] + [TURN_HE.get(v, v) for v in T.TURN[u]] for u in T.TURN_UNDEAD]
    return table(head, rows, "turn", [""] + ["n"] * len(T.TURN_LEVELS))


TURN_LEGEND = ("<b>מספר:</b> מגלגלים 2ק6, ומצליחים בתוצאה שווה או גבוהה יותר. <b>ג:</b> גירוש בלי לגלגל. "
               "<b>ה:</b> השמדה בלי לגלגל. <b>–:</b> אי אפשר לגרש. "
               "בהצלחה המנחה מגלגלת 2ק6: כמה קוביות פגיעה של אל-מתים בורחים (תמיד לפחות אחד). "
               "<b>ה</b> – הם מושמדים במקום לברוח; <b>ה+</b> – השמדה של 3ק6 קוביות פגיעה; <b>ה#</b> – של 4ק6. "
               "מי שנכשל מול אל-מת מסוים לא יכול לנסות לגרש אותו שוב באותו קרב.")


def thief_table():
    head = ["דרגה"] + [n.replace(" ", "<br>", 1) for n in T.THIEF_SKILL_NAMES]
    rows = [[str(lv)] + [f"{v}%" for v in T.THIEF_SKILLS[lv]] for lv in range(1, 37)]
    return table(head, rows, "skills", ["n"] * 9)


def mystic_cols(lv):
    ac, mv, at, dmg, ability = T.MYSTIC_TABLE[lv]
    return [num(ac), str(mv), str(at), dice(dmg), ability]


FIGHTER = dict(
    key="fighter", file="fighter.html", name="לוחם", en="Fighter", pages="16–18",
    lead="מי שהלחימה היא דרכו בחיים. הכי טוב בקרב, עם הכי הרבה נקודות פגיעה, ויכול להשתמש בכל נשק ובכל שריון.",
    facts=[("דרישה ראשית", "כוח"), ("בונוס ניסיון", "+5% לכוח 13–15, +10% לכוח 16–18"),
           ("קוביות פגיעה", "1ק8 לכל דרגה עד דרגה 9. מדרגה 10: +2 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "36"), ("שריון", "כל סוג; מותר מגן"), ("נשק", "כל סוג")],
    abilities=[
        "<b>תמרוני קרב:</b> תקיפה ברומח, וכיוון חנית כנגד הסתערות (פרק 8).",
        "<b>דרגה 9 – אפשרויות הקרב של הלוחם:</b> מכה, הדיפה ופירוק מנשק (עמ׳ 104–105).",
        "<b>התקפות מרובות:</b> אם מספיק לו לגלגל 2 (עם כל הבונוסים) כדי לפגוע ביריב, הלוחם תוקף אותו פעמיים בסיבוב "
        "מדרגה 12, שלוש פעמים מדרגה 24 וארבע פעמים מדרגה 36.",
        "<b>דרגה 9 (דרגת השם):</b> הלוחם נקרא אדון או גבירה ובוחר דרך: <b>לוחם בעל אדמות</b>, שמקבל אדמה מהשליטים "
        "ובונה עליה טירה על חשבונו (ברון ומעלה, ראו דף הדומיניון), או <b>לוחם נודד</b> – למטה.",
    ],
)

TRAVELING = [
    ("פאלאדין", "לוחם נודד שנוטה לסדר", [
        "נשבע אמונים למסדר כוהנים של סדר, ועושה מה שמנהיגיו מבקשים כל עוד זה בשירות הטוב.",
        "מגלה רוע (כמו לחש הכוהנים) פעם בסיבוב, עד 40 מ׳, בריכוז. לא תוקף באותו סיבוב.",
        "עם חוכמה 13 ומעלה מטיל לחשי כוהן כמו כוהן בשליש מדרגתו (מעגלים למטה): בדרגה 9 – כמו כוהן בדרגה 3.",
        "מגרש אל-מתים כמו כוהן בשליש מדרגתו.",
        "שכירים: לא יותר מדרגת הכוהן שלו.",
        "חייב לעזור לכל מי שמבקש עזרה – בשירות, לא בכסף – חוץ מרשעים. במשימה מטעם אדונו מספיקה עזרה קטנה והסבר.",
    ]),
    ("אביר", "לוחם נודד נייטרלי, או לוחם של סדר או תוהו שלא הפך לפאלאדין או לנוקם", [
        "נשבע אמונים לנסיך, למלך או לקיסר. כשהאדון קורא לו, הוא מתייצב ומשרת.",
        "מסרב לאדונו או נשבע לאחר: מאבד 3 דרגות ניסיון, ואולי גם את חייו ואת שמו הטוב.",
        "רשאי לבקש מקלט בכל טירה: עד 3 ימים, עם אוכל ושתייה.",
        "חייב להיענות לקריאה לנשק שנשמעת באזור שבו הוא עובר, וזכאי למתנה על השירות.",
    ]),
    ("נוקם", "לוחם נודד שנוטה לתוהו", [
        "כורת ברית עם מסדר כוהנים של תוהו ומציית למנהיגיו. מסרב – מאבד את יכולות הנוקם.",
        "מגלה רוע כמו הפאלאדין.",
        "עם חוכמה 13 ומעלה מטיל לחשי כוהן בשליש מדרגתו, תמורת תשלום למסדר (מומלץ: 10,000 פ״ז לכל עוצמת לחש).",
        "מגרש אל-מתים בשליש מדרגתו. בתוצאה של גירוש או השמדה הוא יכול במקום זה לשלוט בהם: תור לכל דרגה.",
        "אין לו שכירים בני אדם או בני-אדם-למחצה; רק מפלצות של תוהו שהוא משכנע להצטרף.",
    ]),
]

CLERIC = dict(
    key="cleric", file="cleric.html", name="כוהן", en="Cleric", pages="13–15", also="ודרואיד",
    lead="משרת האל: נלחם בנשק קהה, מרפא בלחשים ומגרש אל-מתים בכוח האמונה.",
    facts=[("דרישה ראשית", "חוכמה"), ("בונוס ניסיון", "+5% לחוכמה 13–15, +10% לחוכמה 16–18"),
           ("קוביות פגיעה", "1ק6 לכל דרגה עד דרגה 9. מדרגה 10: +1 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "36"), ("שריון", "כל סוג; מותר מגן"),
           ("נשק", "נשק קהה בלבד, בלי להב ובלי חוד (מסומן כ בטבלת הנשק)")],
    abilities=[
        "<b>לחשים:</b> מדרגה 2, לפי הטבלה. אחרי שינה טובה הכוהן מתפלל שעה ומקבל את לחשיו. אין לו ספר לחשים: "
        "הוא יכול לבקש כל לחש כוהנים מעוצמה שהוא מספיק מנוסה להטיל.",
        "<b>לחש הפיך:</b> אפשר להטיל אותו הפוך. כוהני סדר עושים זאת רק בסכנת חיים.",
        "<b>גירוש אל-מתים:</b> במקום לתקוף. מצליבים את הדרגה עם סוג האל-מת בטבלה למטה.",
        "<b>דרגה 9:</b> הכוהן נקרא פטריארך או מטריארך. <b>כוהן בעל אדמות</b> בונה מבצר בחסות המסדר "
        "(המסדר יכול לממן חלק, בדרך כלל 50%, ו-1ק6 כוהנים בדרגות נמוכות באים לעזור), או <b>כוהן נודד</b>.",
        "<b>דרואיד:</b> כוהן נייטרלי בדרגות 9–29 יכול להפוך לדרואיד – למטה.",
    ],
)

DRUID = [
    ("איך", "כוהן נייטרלי בדרגות 9–29 גר ביער ומתבודד 1ק4 חודשים. דרואיד בדרגה גבוהה (בדרך כלל 25 ומעלה) "
            "בוחן ומלמד אותו."),
    ("טבלאות", "כמו של הכוהן: נק״נ, קוביות פגיעה, לחשים ליום וגלגולי הצלה מדרגה 9 ומעלה."),
    ("שריון", "שריון עור בלבד; מגן רק מעץ ומעור. בלי שום פריט מתכת."),
    ("נשק", "כמו הכוהן, אבל בלי חלקי מתכת. נשק מעץ בלבד עולה 50% יותר."),
    ("לחשים", "לחשי כוהנים – חוץ מלחשים שקשורים בטוב ורע, כגון הגנה מרוע – ובנוסף לחשי דרואידים."),
    ("הגבלות", "לא מגרש אל-מתים. גר בסביבה טבעית ולא בעיר. שומר על היער שלו ומעניש מי שהורס אותו בכוונה. "
               "דרואיד שמשנה נטייה מאבד את כל יכולות הדרואיד."),
    ("דרגות 30–36", "יש רק 9 דרואידים בדרגה 30, 7 בדרגה 31, 5 ב-32, 4 ב-33, 3 ב-34, 2 ב-35 ודרואיד גדול אחד ב-36. "
                    "כדי לעלות, מנצחים דרואיד מהדרגה החדשה בקסם ובקרב בלי נשק. המפסיד נשאר נקודה אחת לפני הדרגה."),
]

MU = dict(
    key="mu", file="magic-user.html", name="קוסם", en="Magic-User", pages="18–20",
    lead="חלש בקרב, אבל ספר הלחשים שלו הופך אותו לדמות החזקה ביותר בדרגות הגבוהות.",
    facts=[("דרישה ראשית", "תבונה"), ("בונוס ניסיון", "+5% לתבונה 13–15, +10% לתבונה 16–18"),
           ("קוביות פגיעה", "1ק4 לכל דרגה עד דרגה 9. מדרגה 10: +1 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "36"), ("שריון", "אסור שריון ואסור מגן"),
           ("נשק", "פגיון בלבד. באישור המנחה גם מטה, קנה נשיפה, שמן בוער, מים קדושים, רשת, אבן, קלע ושוט "
                   "(מסומנים ל בטבלת הנשק)")],
    abilities=[
        "<b>ספר הלחשים:</b> המורה נותן ספר עם 2 לחשים מעוצמה 1. בדרגה 2 הוא מוסיף לחש מעוצמה 1, בדרגה 3 לחש מעוצמה 2, "
        "ובדרגה 4 עוד לחש מעוצמה 2. מכאן מחפשים לחשים לבד: במגילות, בספרים ובמחקר.",
        "<b>לחשים ביום:</b> לפי הטבלה. כל לחש שמוטל נשכח, עד שלומדים אותו שוב מהספר אחרי שינה טובה.",
        "<b>בלי שריון ובלי מגן:</b> הקוסם הכי חלש בקרב, ויש לו הכי מעט נקודות פגיעה.",
    ],
)

THIEF = dict(
    key="thief", file="thief.html", name="גנב", en="Thief", pages="21–23",
    lead="פותח מנעולים, מפרק מלכודות, מטפס על קירות ודוקר מאחור.",
    facts=[("דרישה ראשית", "זריזות"), ("בונוס ניסיון", "+5% לזריזות 13–15, +10% לזריזות 16–18"),
           ("קוביות פגיעה", "1ק4 לכל דרגה עד דרגה 9. מדרגה 10: +2 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "36"), ("שריון", "שריון עור בלבד; בלי מגן"),
           ("נשק", "כל כלי ירייה, וכל נשק ביד אחת לקרב פנים אל פנים")],
    abilities=[
        "<b>מיומנויות גנב:</b> מגלגלים ק100. הצלחה אם התוצאה שווה לאחוז או נמוכה ממנו (טבלה למטה). "
        "מציאת מלכודות, תנועה חרישית, התחבאות בצללים ושמיעת רחשים – המנחה מגלגלת בסוד.",
        "<b>מעל 100%:</b> במשימה קשה המנחה מורידה מחסר מהאחוז. אם נשאר 100% או יותר, מצליחים.",
        "<b>דקירה מאחור:</b> מתגנבים אל יריב שלא שם לב, עם נשק ביד אחת לקרב פנים אל פנים: +4 להתקפה ונזק כפול.",
        "<b>דרגה 4:</b> קריאת כל כתב או שפה רגילים (לא כתב קסום) בסיכוי 80%. נכשלתם? מנסים שוב רק בדרגה הבאה.",
        "<b>דרגה 10:</b> הטלת לחשי קוסם ממגילה. בסיכוי 10% הלחש משתבש.",
    ],
)

DWARF = dict(
    key="dwarf", file="dwarf.html", name="גמד", en="Dwarf", pages="23–24",
    lead="לוחם עיקש מתחת להרים. רואה בחושך, מגלה מלכודות, וממשיך להשתפר בדרגות התקפה אחרי דרגה 12.",
    facts=[("דרישה ראשית", "כוח"), ("דרישות נוספות", "כושר 9 ומעלה"),
           ("בונוס ניסיון", "+5% לכוח 13–15, +10% לכוח 16–18"),
           ("קוביות פגיעה", "1ק8 לכל דרגה עד דרגה 9. מדרגה 10: +3 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "12, ואחריה דרגות התקפה ג–מ"), ("שריון", "כל סוג; מותר מגן"),
           ("נשק", "כל נשק קטן או בינוני לקרב פנים אל פנים; קשת קצרה ורובי-קשת. לא קשת ארוכה")],
    abilities=[
        "<b>זיוונות:</b> רואה חום בחושך עד 20 מ׳. לא עובדת ליד אור רגיל או קסום, ולא מספיקה כדי לקרוא.",
        "<b>גילוי:</b> מחפש מלכודות, קירות זזים, מעברים משופעים ובנייה חדשה. המנחה מגלגלת ק6, הצלחה ב-1–2.",
        "<b>שפות:</b> מדוברת, שפת הנטייה, ועוד גמדית, נומית, גובלינית וקובולדית.",
        "<b>תמרוני לוחם:</b> תקיפה ברומח, וכיוון חנית כנגד הסתערות. ב-660,000 נק״נ: אפשרויות הקרב של הלוחם "
        "ושתי התקפות בסיבוב; ב-2,200,000 נק״נ: שלוש.",
        "<b>אחרי דרגה 12:</b> הגמד לא עולה בדרגה, אבל צובר <b>דרגות התקפה</b> (ג עד מ) שמשפרות את ה-THAC0. "
        "קוביות הפגיעה וגלגולי ההצלה נשארים כמו בדרגה 12.",
        "<b>ב-1,400,000 נק״נ:</b> חצי נזק מלחשים ומיכולות דמויות לחש (רבע נזק בגלגול הצלה מוצלח). לא כולל נשיפת דרקון.",
    ],
)

ELF = dict(
    key="elf", file="elf.html", name="אלף", en="Elf", pages="24–26",
    lead="לוחם וקוסם בגוף אחד: לובש שריון, נלחם בכל נשק ומטיל לחשי קוסם. מגיע רק לדרגה 10, ואחריה דרגות התקפה.",
    facts=[("דרישות ראשיות", "כוח ותבונה"), ("דרישות נוספות", "תבונה 9 ומעלה"),
           ("בונוס ניסיון", "+5% לכוח 13 ומעלה ותבונה 13–15; +10% לכוח 13 ומעלה ותבונה 16–18"),
           ("קוביות פגיעה", "1ק6 לכל דרגה עד דרגה 9. בדרגה 10: +2 נק״פ, בלי התאמת כושר"),
           ("דרגה מרבית", "10, ואחריה דרגות התקפה ד–מ"), ("שריון", "כל סוג; מותר מגן"), ("נשק", "כל סוג")],
    abilities=[
        "<b>לחשים:</b> לחשי קוסם, עם ספר לחשים כמו של הקוסם, לפי הטבלה. אחרי דרגה 10 מספר הלחשים לא עולה.",
        "<b>זיוונות:</b> כמו הגמד – רואה חום בחושך עד 20 מ׳.",
        "<b>שפות:</b> מדוברת, שפת הנטייה, ועוד אלפית, נולית, הובגובלינית ואורקית.",
        "<b>גילוי:</b> מוצא דלתות סודיות ונחבאות בסיכוי 1 מ-3 – רק כשאומרים למנחה שמחפשים.",
        "<b>חסין לשיתוק של גועל.</b> שיתוק אחר (כמו של זחל נבלות) פועל עליו כרגיל.",
        "<b>תמרוני לוחם:</b> תקיפה ברומח, וכיוון חנית כנגד הסתערות.",
        "<b>ב-850,000 נק״נ:</b> אפשרויות הקרב של הלוחם – מכה, הדיפה ופירוק מנשק – ושתי התקפות בסיבוב. "
        "ב-2,600,000 נק״נ: שלוש התקפות. אף פעם לא ארבע.",
        "<b>ב-1,600,000 נק״נ:</b> חצי נזק מכל נשיפה, רבע נזק בגלגול הצלה מוצלח (תמיד לפחות נקודה אחת).",
        "<b>דרגה 9:</b> נקרא אדון קוסם או גבירה קוסמת, ויכול לבנות מבצר ביער שמשתלב בטבע. חיות היער עד 8 ק״מ "
        "מסביב נעשות ידידותיות: מזהירות מזרים ומעבירות הודעות.",
    ],
)

HALFLING = dict(
    key="halfling", file="halfling.html", name="זוטון", en="Halfling", pages="26–27",
    lead="קטן, אוהב בית ונוחות, וקשה מאוד לראות אותו ביער. נלחם כמו לוחם ושורד כמו גמד.",
    facts=[("דרישות ראשיות", "כוח וזריזות"), ("דרישות נוספות", "זריזות 9 ומעלה וכושר 9 ומעלה"),
           ("בונוס ניסיון", "+5% אם כוח או זריזות 13 ומעלה; +10% אם שניהם 13 ומעלה"),
           ("קוביות פגיעה", "1ק6 לכל דרגה עד דרגה 8"),
           ("דרגה מרבית", "8, ואחריה דרגות התקפה א–כ"),
           ("שריון", "כל סוג ומותר מגן, אבל רק בגודל של זוטון"),
           ("נשק", "כל נשק קטן לקרב פנים אל פנים; קשת קצרה ורובה-קשת קל")],
    abilities=[
        "<b>בונוסים בקרב:</b> −2 לדירוג השריון מול יצורים גדולים מאדם (דרג״ש 6 נעשה 4); +1 להתקפה עם כלי קליעים; "
        "+1 ליוזמה אישית. גדול מאדם: ענק או עצום בתיאור, חיה גדולה מאדם, או יצור לא דמוי-אדם עם 4 ק״פ ומעלה.",
        "<b>הסתתרות:</b> בלי לזוז. ביער ובסבך 90%; בתוך מבנה, בצל או מאחורי מחסה, 33%. המנחה מגלגלת ק100. "
        "אור חזק, או אור שהזוטון עצמו נושא, מבטלים את הסיכוי.",
        "<b>תמרון לוחם:</b> כיוון חנית כנגד הסתערות. קטן מדי לתקיפה ברומח.",
        "<b>ב-300,000 נק״נ:</b> חצי נזק מלחשים ומיכולות דמויות לחש (רבע בגלגול הצלה מוצלח).",
        "<b>ב-900,000 נק״נ:</b> אפשרויות הקרב של הלוחם ושתי התקפות בסיבוב. פירוק מנשק לא עובד מול יריב בגודל ענק. "
        "ב-3,000,000 נק״נ: שלוש התקפות.",
        "<b>ב-2,100,000 נק״נ:</b> חצי נזק מכל נשיפה (רבע בגלגול הצלה מוצלח).",
        "<b>מבצר:</b> בכל דרגה, כשיש כסף. בדרגה 8 הזוטון נקרא שריף.",
    ],
)

MYSTIC = dict(
    key="mystic", file="mystic.html", name="מיסטיקן", en="Mystic", pages="29–31", optional=True,
    lead="נזיר ממנזר שנלחם בידיים חשופות, בלי שריון. ככל שהוא עולה בדרגה הוא מהיר יותר, קשה לפגוע בו, ותוקף יותר פעמים.",
    facts=[("דרישות ראשיות", "כוח וזריזות"), ("דרישות נוספות", "חוכמה 13 ומעלה וזריזות 13 ומעלה"),
           ("בונוס ניסיון", "+5% לכוח 13–15, +10% לכוח 16–18. מיסטיקן אקרובט: −20%"),
           ("קוביות פגיעה", "1ק6 לכל דרגה עד דרגה 9. מדרגה 10: +2 נק״פ לדרגה, בלי התאמת כושר"),
           ("דרגה מרבית", "16"),
           ("שריון", "אסור שריון ואסור מגן, וגם חפצי קסם מגוננים (טבעות, גלימות וכדומה)"),
           ("נשק", "כל סוג; רבים מעדיפים ידיים חשופות או מקל הליכה")],
    abilities=[
        "<b>בטבלה:</b> דירוג השריון, התנועה (מ׳ לתור), מספר ההתקפות בסיבוב (בידיים או בנשק לקרב פנים אל פנים "
        "ונשק מוטל, לא בכלי קליעים) והנזק בידיים חשופות. מוסיפים בונוס כוח לנזק.",
        "<b>יכולות גנב:</b> כמו גנב באותה דרגה – מציאת מלכודות, פירוק מלכודות, תנועה חרישית, טיפוס על קירות "
        "והתחבאות בצללים.",
        "<b>תמרוני לוחם:</b> כיוון חנית כנגד הסתערות (לא תקיפה ברומח). בדרגה 9: מכה, הדיפה ופירוק מנשק – "
        "בלי התקפות מרובות, בנשק או בידיים.",
        "<b>אקרובטיקה</b> (לא לכל מיסטיקן): קפיצות, גלגולים, תפיסות, תנופות ושיווי משקל. הסיכוי באחוזים: "
        "פי 3 מהזריזות ועוד פי 2 מהדרגה. בהצלחה חוצה שטח קשה בלי להאט, או חוצה שורת אויבים. מחיר: −20% לנק״נ.",
        "<b>אורח חיים:</b> מקבל נק״נ על אוצר רק אם תרם אותו לנזקקים, ונותן 10% למנזר. כל רכושו שייך למנזר. "
        "מפר שבועה – מגורש מהמנזר.",
        "<b>דרגות גבוהות:</b> בדרגה 9 נקרא מורה או מורה. רק 7 מיסטיקנים בכל דרגה 10–12, 5 בכל דרגה 13–15 ו-3 בדרגה 16: "
        "כדי לעלות מנצחים אחד מהם בקרב בלי נשק.",
    ],
)

MYSTIC_ABILITIES = [
    ("מודעות", 2, "מופתע רק ב-1 בק6."),
    ("ריפוי עצמי", 4, "פעם ביום: מתרכז סיבוב אחד ומרפא לעצמו נקודת פגיעה אחת לכל דרגה."),
    ("דיבור עם חיות", 6, "מדבר עם כל חיה רגילה או ענקית, כמה שרוצה. החיה לא חייבת לענות."),
    ("עמידות", 8, "חצי נזק מכל לחש ונשיפה שגורמים נזק, רבע בגלגול הצלה מוצלח (מעגלים למטה, לפחות 1)."),
    ("דיבור עם כל אחד", 10, "מדבר עם כל יצור חי שיש לו שפה, כמה שרוצה."),
    ("מחסום מוח", 12, "חסין לתע״ח, עצירה והאטה, להקסמה, למשימה ולפיקוד."),
    ("היעלמות", 14, "פעם ביום: מתרכז סיבוב, ואף יצור חי או אל-מת לא רואה אותו – סיבוב לכל דרגה, או עד שהוא תוקף."),
    ("מגע עדין", 16, "פעם ביום, בגלגול פגיעה: הקסמה, ריפוי כל, מוות, משימה או שיתוק. בלי גלגול הצלה; 24 שעות "
                     "(המוות לתמיד). לא עובד על יצור עם יותר קוביות פגיעה מדרגת המיסטיקן."),
]

CLASSES = [FIGHTER, CLERIC, MU, THIEF, DWARF, ELF, HALFLING, MYSTIC]


def class_sections(c):
    """(id, title, html) for a class page."""
    k = c["key"]
    s = [("about", "בקצרה", facts(c["facts"] + [("בספר", f"עמודים {c['pages']}")]))]
    if k == "fighter":
        lv = level_table(T.FIGHTER_XP, 8, 2, T.THAC0_FIGHTER)
        sv = saves_table(T.FIGHTER_SAVES, ("אדם רגיל", T.NORMAL_MAN_SAVES), SAVES_HOW + " אדם רגיל: מי שאינו הרפתקן.")
    elif k == "cleric":
        lv = level_table(T.CLERIC_XP, 6, 1, T.THAC0_CTD, T.CLERIC_SPELLS, 7)
        sv = saves_table(T.CLERIC_SAVES, last_note=SAVES_HOW)
    elif k == "mu":
        lv = level_table(T.MU_XP, 4, 1, T.THAC0_MU, T.MU_SPELLS, 9)
        sv = saves_table(T.MU_SAVES, last_note=SAVES_HOW)
    elif k == "thief":
        lv = level_table(T.THIEF_XP, 4, 2, T.THAC0_CTD)
        sv = saves_table(T.THIEF_SAVES, last_note=SAVES_HOW)
    elif k == "dwarf":
        lv = level_table(T.DWARF_XP, 8, 3, T.THAC0_FIGHTER, ranks=T.DWARF_RANKS)
        sv = saves_table(T.DWARF_SAVES, last_note=SAVES_HOW + " אחרי דרגה 12 – כמו בדרגה 12.")
    elif k == "elf":
        lv = level_table(T.ELF_XP, 6, 2, T.THAC0_FIGHTER, T.ELF_SPELLS, 5, ranks=T.ELF_RANKS)
        sv = saves_table(T.ELF_SAVES, last_note=SAVES_HOW + " אחרי דרגה 10 – כמו בדרגה 10.")
    elif k == "halfling":
        lv = level_table(T.HALFLING_XP, 6, 0, T.THAC0_FIGHTER, ranks=T.HALFLING_RANKS, cap=8)
        sv = saves_table(T.HALFLING_SAVES, last_note=SAVES_HOW + " אחרי דרגה 8 – כמו בדרגה 8.")
    elif k == "mystic":
        lv = level_table(T.MYSTIC_XP, 6, 2, T.THAC0_FIGHTER,
                         extra_head=["דרג״ש", "תנועה<br>(מ׳)", "התקפות", "נזק<br>בידיים", "יכולת חדשה"],
                         extra_cols=mystic_cols)
        sv = saves_table(T.MYSTIC_SAVES, last_note=SAVES_HOW)
    ranks_note = (" <b>דרגות התקפה</b> (אחרי הדרגה המרבית): צוברים נק״נ כרגיל, וכל דרגת התקפה משפרת את ה-THAC0."
                  if k in ("dwarf", "elf", "halfling") else "")
    s.append(("levels", "עלייה בדרגה", lv + note(THAC0_HOW) + (f'<p class="note">{ranks_note}</p>' if ranks_note else "")))
    s.append(("saves", "גלגולי הצלה", sv))
    s.append(("abilities", "יכולות", bullets(c["abilities"])))
    if k == "fighter":
        body = "".join(f'<h3>{n} <span class="sub">{w}</span></h3>' + bullets(items) for n, w, items in TRAVELING)
        s.append(("traveling", "לוחמים נודדים", note("בדרגה 9 ומעלה, לוחם שלא לקח אדמה יכול להפוך לאחד מאלה. "
                                                      "היכולות לא באות לבד: צריך לעמוד בתנאים.") + body))
    if k == "cleric":
        s.append(("turn", "גירוש אל-מתים", turn_table() + note(TURN_LEGEND)))
        s.append(("druid", "דרואיד (אופציונלי)", facts(DRUID)))
    if k == "thief":
        s.append(("skills", "מיומנויות גנב", thief_table()))
    if k == "mystic":
        body = facts([(f"{n} <span class=\"lv\">דרגה {lv}</span>", t) for n, lv, t in MYSTIC_ABILITIES])
        s.append(("mystic-abilities", "יכולות מיסטיקן", body))
        rows = [[str(lv), w] for lv, w in T.MYSTIC_UNARMED]
        s.append(("unarmed", "התקפה בידיים חשופות",
                  note("מדרגה 2 הידיים של המיסטיקן פוגעות ביצורים שרק נשק מיוחד פוגע בהם, כאילו היה זה הנשק בטבלה – "
                       "בלי הבונוסים שלו להתקפה ולנזק. מיסטיקן בדרגה 5 פוגע בגרגויל.")
                  + table(["מדרגה", "פוגע כמו"], rows, "narrow", ["n", ""])))
    return s


# ---------------------------------------------------------------- overview and equipment

def overview_sections():
    rows = []
    for c in CLASSES:
        f = dict(c["facts"])
        prime = f.get("דרישה ראשית") or f.get("דרישות ראשיות")
        hd = f["קוביות פגיעה"].split(" ")[0].removeprefix("1")
        rows.append([f'<a href="{c["file"]}">{c["name"]}</a>' + (" *" if c.get("optional") else ""),
                     prime, dice(hd), fix(f["דרגה מרבית"].split(",")[0]), fix(f["שריון"]), fix(f["נשק"].split(".")[0])])
    s = [("compare", "המקצועות במבט אחד",
          table(["מקצוע", "דרישה ראשית", "קוביית<br>פגיעה", "דרגה<br>מרבית", "שריון", "נשק"], rows, "compare",
                ["", "", "n", "n", "", ""])
          + note("* מקצוע אופציונלי: המנחה מחליטה אם הוא קיים במשחק. דרואיד הוא כוהן נייטרלי מדרגה 9 ומעלה – "
                 "ראו בדף הכוהן."))]
    s.append(("read", "איך קוראים את הטבלאות", bullets([
        "<b>נק״נ:</b> נקודות הניסיון שצריך כדי להגיע לדרגה.",
        "<b>קוביות פגיעה:</b> בכל דרגה מגלגלים קובייה ומוסיפים את בונוס הכושר. אחרי דרגה 9 מוסיפים מספר קבוע "
        "של נקודות, בלי בונוס.",
        "<b>THAC0:</b> " + THAC0_HOW,
        "<b>גלגולי הצלה:</b> " + SAVES_HOW,
        "<b>בונוס ניסיון:</b> ערך גבוה בדרישה הראשית מוסיף אחוזים לכל נק״נ שהדמות מרוויחה.",
        "<b>בני אדם וחצאי-אדם:</b> גמד, אלף וזוטון מגיעים לדרגה מרבית נמוכה, ואחריה צוברים <b>דרגות התקפה</b> "
        "(א–מ) שמשפרות רק את ה-THAC0.",
    ])))
    return s


def weapons_table():
    head = ["נשק", "נזק", "טווח<br>קצר", "טווח<br>בינוני", "טווח<br>ארוך", "מחיר<br>(פ״ז)", "עומס<br>(מט׳)", "גודל", "הערות"]
    rows = []
    for group, items in E.WEAPONS:
        rows.append(("group", group))
        for name, dmg, rng, cost, enc, notes, size in items:
            r = rng or ("", "", "")
            letters = ", ".join(ltr(x) if x[0].isdigit() else x for x in (E.NOTE_LETTERS[n] for n in notes.split()))
            rows.append([name, num(dmg) if dmg != "אין" else "אין", *(str(x) for x in r), num(cost), num(enc),
                         E.SIZES[size], letters])
    out = table(head, rows, "weapons", ["", "n", "n", "n", "n", "n", "n", "", ""])
    legend = "".join(f"<dt>{ltr(k) if k[0].isdigit() else k}</dt><dd>{fix(v)}</dd>" for k, v in E.NOTE_TEXT)
    return out + ('<p class="note">הטווח במטרים. בטווח קצר +1 להתקפה, בטווח ארוך −1; מעבר לטווח הארוך אי אפשר לפגוע. '
                  'בחוץ הטווחים פי שלושה.</p>'
                  f'<dl class="legend">{legend}</dl>')


def equipment_sections():
    coins = table(["", *[f'{a}<br><span class="sub">{n}</span>' for a, n, _ in E.COINS]],
                  [[f'<b class="nw">1 {a}</b>'] + [num(v1 // v2) if v1 >= v2 else "–" for _, _, v2 in E.COINS]
                   for a, _, v1 in E.COINS], "coins", ["", "n", "n", "n", "n", "n"])
    s = [("money", "כסף", note("כל דמות חדשה מתחילה עם 3ק6 × 10 פ״ז, ושניים-שלושה זוגות בגדים פשוטים, נעליים, "
                               "חגורה ופאוץ׳.") + coins
          + note("כמה שווה מטבע אחד מהשורה, במטבעות של העמודה. מטבע אחד שוקל עומס של 1 מט׳."))]
    s.append(("weapons", "כלי נשק", weapons_table()))
    ammo = table(["נשק", "תחמושת", "כמות<br>רגילה", "מחיר<br>(פ״ז)", "יריות<br>למט׳"],
                 [[w, a, str(n), str(c), str(e)] for w, a, n, c, e in E.AMMO], "narrow", ["", "", "n", "n", "n"])
    s.append(("ammo", "תחמושת", ammo + note("המחיר כולל אשפה או נרתיק פשוטים. אותה תחמושת לקשת קצרה וארוכה, "
                                            "ולקנה נשיפה קצר וארוך.")))
    armor = table(["דרג״ש", "שריון", "מחיר (פ״ז)", "עומס (מט׳)", "הערות"],
                  [[num(ac), n, str(c), num(e), w] for ac, n, c, e, w in E.ARMOR], "", ["n", "", "n", "n", ""])
    s.append(("armor", "שריון", armor + bullets([
        "<b>מגן:</b> מוריד 1 מדירוג השריון, בכל גודל.",
        "<b>אחרי כל שריון בא גם כובע מתאים.</b> שריון של גזע אחר לא מתאים: אלף בשריון גמד מאט, זוטון בשריון אדם "
        "מועד, וגמד לא נכנס לשריון זוטון.",
        "<b>חליפת שריון:</b> דרג״ש 0 (−1 עם מגן). מורידה נקודה אחת לכל קוביית נזק מאש, קור, גז, חומצה ונשיפה "
        "(לפחות 1 לקובייה), ו-+2 לגלגול ההצלה מהם. רועשת (נשמעת עד 40 מ׳), תנועה 10 מ׳ לתור, −5 לירי (חוץ "
        "מרובה-קשת), ולבד −1 להפתעה. נתפרת למידות של לובש אחד; לובשים אותה שני תורים.",
    ])))
    gear = table(["פריט", "תיאור", "מחיר", "עומס (מט׳)"],
                 [[n, fix(d), fix(c), e] for n, d, c, e in E.GEAR], "gear", ["", "", "n", "n"])
    s.append(("gear", "ציוד הרפתקנות", gear + note(
        "* העומס כשהוא ריק; מלא – מוסיפים את עומס התכולה (פאוץ׳ חגורה מלא: 55 מט׳). "
        "** העומס כשהוא ארוז; בגדים שלובשים לא נחשבים. "
        "*** אשפה ריקה; מלאה (20 חיצים או 30 קליעים) – 10 מט׳ בסך הכול.")))
    animals = table(["חיה", "מחיר (פ״ז)"], [[n, num(c)] for n, c in E.RIDING_ANIMALS], "narrow", ["", "n"])
    land = table(["פריט", "מחיר (פ״ז)", "תכולה (מט׳)", "הערה"],
                 [[n, num(c), fix(cap), x] for n, c, cap, x in E.LAND_GEAR], "", ["", "n", "n", "n"])
    s.append(("land", "תחבורה ביבשה", animals + land + note(
        "א – העומס שהפריט עצמו מוסיף למשא של הסוס: שק אוכף מלא הוא 900 מט׳. "
        "ב – התכולה עם סוס עבודה אחד / עם שניים; שתי פרדות במקום סוס אחד. מריצה ועגלה לא עוברות מדבר, יער, הרים או ביצה "
        "בלי דרך, ומעל 20 מ׳ לתור הן עלולות להישבר או להתהפך.")))
    ships = []
    for n, cost, row, sail, mar, cap, km, mr, hull, ac in E.SHIPS:
        ships.append([n, fix(cost), row, sail, mar, num(cap), num(km[0] or "—"), num(km[1] or "—"),
                      num(mr[0] or "—"), num(mr[1] or "—"), fix(hull), ac])
    s.append(("water", "תחבורה במים", table(
        ["כלי שיט", "מחיר<br>(פ״ז)", "חותרים", "מלחים", "נחתים", "תכולה<br>(מט׳)", "ק״מ ליום<br>בחתירה",
         "ק״מ ליום<br>במפרש", "מ׳ לסיבוב<br>בחתירה", "מ׳ לסיבוב<br>במפרש", "נקודות<br>גוף", "דרג״ש"],
        ships, "ships", ["", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n"]) + note(
        "התכולה היא מעבר לצוות: סירת נהר נושאת 8 אנשים ועוד 40,000 מט׳ מטען. בלי רוח, או ברוח נגדית, "
        "כלי שיט בלי חותרים לא זז. רב החובל לא כלול בצוות. "
        "† באוניה ארוכה המלחים הם גם החותרים והנחתים. "
        "†† לכל קטע של 3×3 מ׳ (100 פ״ז לקטע מקצועי). "
        "‡ בספינת מפרש אין נחתים; ספינה שהוסבה למעבורת כוחות נושאת את מספר הנחתים הזה ועולה 1/3 יותר.")))
    move = table(["עומס (מט׳)", "מהירות רגילה<br>(מ׳ לתור)", "מהירות היתקלות<br>(מ׳ לסיבוב)",
                  "מהירות ריצה<br>(מ׳ לסיבוב)"],
                 [[fix(e), str(a), str(b), str(c)] for e, a, b, c in E.MOVEMENT], "narrow", ["n", "n", "n", "n"])
    s.append(("encumbrance", "עומס ותנועה", move + note(
        "מחברים את העומס של כל מה שהדמות נושאת: נשק, שריון, ציוד ומטבעות. 10 מט׳ הם בערך חצי ק״ג. "
        "בחוץ המרחקים פי שלושה. רצים לכל היותר 30 סיבובים, ואז נחים 3 תורים. "
        "קבוצה זזה במהירות של האיטי שבה (עמ׳ 88).")))
    return s


# ---------------------------------------------------------------- page shell

# ---------------------------------------------------------------- spells (ch. 3, pp. 33-61)

def slug(en):
    return "s-" + re.sub(r"[^a-z0-9]+", "-", en.lower()).strip("-")


def spell_entry(s, notes):
    rev = ' <span class="rev">הפיך</span>' if s["reversible"] else ""
    return (f'<div class="spell" id="{slug(s["en"])}">'
            f'<h3>{s["he"]} <span class="sub" lang="en" dir="ltr">{html.escape(s["en"])}</span>{rev}</h3>'
            f'<p class="meta"><span>טווח: {num(s["range"])}</span><span>משך: {num(s["duration"])}</span></p>'
            f'<p>{fix(notes[s["en"]])}</p></div>')


def spell_sections(spells, notes, intro):
    """One contents block with every spell by level, then a section per level."""
    index = "".join(
        f'<div><h3><a href="#l{lv}">עוצמה {lv}</a></h3><ol>'
        + "".join(f'<li><a href="#{slug(s["en"])}">{s["he"]}</a>{"*" if s["reversible"] else ""}</li>' for s in ss)
        + "</ol></div>"
        for lv, ss in spells.items())
    out = [("list", "כל הלחשים", note(intro) + f'<div class="spell-index">{index}</div>')]
    for lv, ss in spells.items():
        out.append((f"l{lv}", f"לחשים מעוצמה {lv}", "".join(spell_entry(s, notes) for s in ss)))
    return out


SPELL_NOTE = ("סיכום קצר לשימוש ליד השולחן; התיאור המלא בספר גובר. כוכבית (*) מסמנת לחש הפיך – לחש שאפשר להטיל גם "
              "בצורה ההפוכה, וזו מתוארת בסוף הסיכום אחרי \"הפוך:\". גלגולי ההצלה הם מפני לחשים, אלא אם כתוב אחרת. "
              "המרחקים במטרים, כמו במהדורה העברית (רגל חלקי 3).")

SPELL_PAGES = [
    ("spells-cleric.html", "לחשי כוהנים", "Clerical Spells",
     "כל 56 לחשי הכוהן, מעוצמה 1 עד 7: טווח, משך וסיכום קצר של מה שהלחש עושה.",
     SP.CLERIC, SN.CLERIC,
     SPELL_NOTE + " הדרואיד מטיל גם את הלחשים האלה, חוץ מאלה שקשורים בטוב ורע (כגון הגנה מרוע)."),
    ("spells-druid.html", "לחשי דרואידים", "Druidic Spells",
     "28 הלחשים שרק הדרואיד מטיל, מעוצמה 1 עד 7, נוסף על לחשי הכוהן.",
     SP.DRUID, SN.DRUID, SPELL_NOTE),
    ("spells-magic-user.html", "לחשי קוסמים", "Magical Spells",
     "כל 117 לחשי הקוסם (וגם העלף), מעוצמה 1 עד 9: טווח, משך וסיכום קצר של מה שהלחש עושה.",
     SP.MU, SN.MU, SPELL_NOTE + " העלף מטיל את לחשי הקוסם עד עוצמה 5."),
]


CSS = """
:root { --ink:#1b1b1b; --muted:#5f5f5f; --paper:#fdfdfb; --line:#dcdcd6; --rule:#1b1b1b; --accent:#7b2a1c; --hover:#f3f2ee; --band:#f6f5f1; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --ink:#ececea; --muted:#a3a3a0; --paper:#141414; --line:#323230; --rule:#8a8a86; --accent:#e0937c; --hover:#1d1d1c; --band:#1a1a19;
} }
:root[data-theme="dark"] { --ink:#ececea; --muted:#a3a3a0; --paper:#141414; --line:#323230; --rule:#8a8a86; --accent:#e0937c; --hover:#1d1d1c; --band:#1a1a19; }
* { box-sizing:border-box; }
html { scroll-padding-top:1rem; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:Assistant, "Segoe UI", Arial, sans-serif; line-height:1.55; font-size:1.02rem; }
a { color:var(--accent); }
.num-ltr { direction:ltr; unicode-bidi:isolate; }
.dice { direction:rtl; unicode-bidi:isolate; white-space:nowrap; }
.layout { display:grid; grid-template-columns:13.5rem minmax(0, 1fr); gap:3rem; max-width:76rem; margin:0 auto; padding:2.6rem 1.25rem 4rem; }
.toc { position:sticky; top:1.4rem; align-self:start; max-height:calc(100vh - 2.8rem); overflow:auto; font-size:.95rem; padding-inline-end:.4rem; }
.toc .back { display:inline-block; font-weight:700; text-decoration:none; margin-bottom:1.4rem; }
.toc .back:hover { text-decoration:underline; }
.toc h2 { font-size:.78rem; letter-spacing:.06em; color:var(--muted); font-weight:700; margin:1.1rem 0 .35rem; }
.toc ol { list-style:none; margin:0; padding:0; }
.toc li a { display:block; color:var(--ink); text-decoration:none; padding:.16rem 0; }
.toc li a:hover { color:var(--accent); }
.toc li a[aria-current="page"] { color:var(--accent); font-weight:800; }
.toc ol.here { margin:.1rem 0 .4rem; padding-inline-start:.8rem; border-inline-start:1.5px solid var(--line); }
.toc ol.here a { color:var(--muted); font-size:.9rem; padding:.1rem 0; }
.toc ol.here a:hover { color:var(--accent); }
main { min-width:0; max-width:56rem; }
header { border-bottom:4px solid var(--rule); padding-bottom:1rem; margin-bottom:.6rem; }
.eyebrow { color:var(--accent); font-weight:700; font-size:.9rem; margin:0 0 .3rem; }
h1 { font-weight:800; font-size:clamp(2.1rem, 6vw, 3.1rem); line-height:1.05; margin:0 0 .7rem; }
h1 .en { font-weight:400; font-size:1rem; color:var(--muted); margin-inline-start:.6rem; direction:ltr; unicode-bidi:isolate; }
.lead { color:var(--muted); font-size:1.08rem; max-width:42rem; margin:0; }
section { margin-top:2.4rem; }
section > h2 { font-weight:800; font-size:1.35rem; margin:0 0 .6rem; padding-bottom:.3rem; border-bottom:1.5px solid var(--rule); }
h3 { font-size:1.1rem; font-weight:800; margin:1.3rem 0 .2rem; }
h3 .sub { font-weight:400; color:var(--muted); font-size:.92rem; margin-inline-start:.4rem; }
.facts { display:grid; grid-template-columns:minmax(8rem, 11rem) 1fr; margin:0; }
.facts dt, .facts dd { margin:0; padding:.42rem 0; border-bottom:1px solid var(--line); }
.facts dt { font-weight:700; padding-inline-end:1rem; }
.facts dt .lv { display:block; font-weight:400; color:var(--muted); font-size:.85rem; }
.bullets { margin:0; padding-inline-start:1.1rem; display:grid; gap:.4rem; }
.bullets li::marker { color:var(--accent); }
.note { color:var(--muted); font-size:.92rem; margin:.6rem 0 0; max-width:48rem; }
.note b { color:var(--ink); }
.cap { color:var(--muted); font-size:.88rem; margin:0 0 .2rem; }
.tbl { overflow-x:auto; margin:.3rem 0 0; }
table { border-collapse:collapse; width:100%; font-variant-numeric:tabular-nums; font-size:.95rem; }
th { text-align:start; font-weight:700; vertical-align:bottom; padding:.35rem .45rem; border-bottom:1.5px solid var(--rule); line-height:1.2; }
td { padding:.24rem .45rem; border-bottom:1px solid var(--line); vertical-align:top; }
th.n, td.n { text-align:center; white-space:nowrap; }
tbody tr:hover td { background:var(--hover); }
tr.group th { font-weight:800; font-size:1rem; color:var(--accent); padding-top:1rem; border-bottom:1px solid var(--line); }
tr.rank td { color:var(--muted); }
tr.rank td:nth-child(2) { color:var(--ink); font-weight:700; }
.sp { display:inline-block; min-width:1.2em; }
table.levels td.n:first-child { font-weight:700; }
table.narrow { width:auto; min-width:22rem; }
table.turn td, table.turn th { padding-inline:.3rem; }
table.compare td:first-child a { font-weight:800; font-size:1.05rem; text-decoration:none; }
table.compare td:first-child a:hover { text-decoration:underline; }
table.weapons td:last-child { white-space:nowrap; }
.sub { font-weight:400; color:var(--muted); font-size:.85em; }
.nw { white-space:nowrap; }
.legend { display:grid; grid-template-columns:2.2rem 1fr; gap:.15rem .4rem; margin:.8rem 0 0; font-size:.92rem; color:var(--muted); max-width:48rem; }
.legend dt { font-weight:800; color:var(--ink); margin:0; }
.legend dd { margin:0; }
.spell-index { display:grid; grid-template-columns:repeat(auto-fill, minmax(11.5rem, 1fr)); gap:.2rem 1.6rem; margin-top:.4rem; }
.spell-index h3 { font-size:.95rem; margin:.9rem 0 .25rem; padding-bottom:.15rem; border-bottom:1px solid var(--line); }
.spell-index h3 a { color:var(--accent); text-decoration:none; }
.spell-index ol { list-style:none; margin:0; padding:0; font-size:.95rem; }
.spell-index li a { color:var(--ink); text-decoration:none; }
.spell-index li a:hover { color:var(--accent); text-decoration:underline; }
.spell { padding:.75rem 0 .8rem; border-bottom:1px solid var(--line); max-width:48rem; }
.spell h3 { margin:0; font-size:1.12rem; }
.spell h3 .sub { margin-inline-start:.35rem; }
.spell .rev { font-size:.8rem; font-weight:700; color:var(--accent); margin-inline-start:.5rem; }
.spell .meta { display:flex; flex-wrap:wrap; gap:.1rem 1.4rem; color:var(--muted); font-size:.9rem; margin:.1rem 0 .3rem; }
.spell p { margin:0; }
.spell:target h3 { color:var(--accent); }
footer { color:var(--muted); font-size:.85rem; margin-top:3rem; border-top:1px solid var(--line); padding-top:.8rem; }
@media (max-width:56rem) {
  .layout { grid-template-columns:1fr; gap:1.6rem; padding-top:1.6rem; }
  .toc { position:static; max-height:none; overflow:visible; border-bottom:1.5px solid var(--rule); padding-bottom:1rem; }
  .toc ol { display:flex; flex-wrap:wrap; gap:.1rem 1rem; }
  .toc ol.here { display:none; }
  .toc h2 { margin-top:.7rem; }
  .toc .back { margin-bottom:.4rem; }
}
@media (max-width:34rem) {
  .facts { grid-template-columns:1fr; }
  .facts dt { border-bottom:0; padding-bottom:0; }
  table.narrow { min-width:0; width:100%; }
}
@media print {
  :root, :root[data-theme="dark"] { --ink:#000; --muted:#444; --paper:#fff; --line:#bbb; --rule:#000; --accent:#7b2a1c; --hover:transparent; }
  @page { size:A4; margin:14mm 12mm; }
  body { font-size:10pt; }
  .toc, footer { display:none; }
  .layout { display:block; padding:0; max-width:none; }
  main { max-width:none; }
  .tbl { overflow:visible; }
  table { font-size:8.5pt; }
  td { padding:.1rem .3rem; }
  tr, .facts dd, .facts dt { break-inside:avoid; }
  section > h2, h3 { break-after:avoid; }
  a { color:inherit; text-decoration:none; }
}
"""


def nav(current, sections):
    def item(href, label):
        cur = ' aria-current="page"' if href == current else ""
        sub = ""
        if href == current and sections:
            sub = '<ol class="here">' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t, _ in sections) + "</ol>"
        return f'<li><a href="{href}"{cur}>{label}</a>{sub}</li>'
    classes = [item("classes.html", "במבט אחד")] + [item(c["file"], c["name"]) for c in CLASSES]
    return f"""<nav class="toc" aria-label="ספר עזר">
    <a class="back" href="../index.html">← חזרה לרשימת הדפים</a>
    <h2>מקצועות</h2>
    <ol>{"".join(classes)}</ol>
    <h2>לחשים</h2>
    <ol>{"".join(item(p[0], p[1]) for p in SPELL_PAGES)}</ol>
    <h2>ציוד</h2>
    <ol>{item("equipment.html", "ציוד ומחירים")}</ol>
  </nav>"""


def document(file, title, en, eyebrow, lead, sections):
    body = "".join(f'<section id="{i}"><h2>{t}</h2>{h}</section>' for i, t, h in sections)
    en_html = f' <span class="en" lang="en">{html.escape(en)}</span>' if en else ""
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · ספר עזר</title>
<meta name="description" content="{html.escape(lead)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;700;800&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="layout">
  {nav(file, sections)}
  <main>
    <header>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}{en_html}</h1>
      <p class="lead">{fix(lead)}</p>
    </header>
    {body}
    <footer>מתוך אוגדן הכללים (Rules Cyclopedia), בעברית. המספרים מהספר; עמודים לפי המהדורה העברית.</footer>
  </main>
</div>
</body>
</html>
"""


def write_pages():
    OUT.mkdir(exist_ok=True)
    pages = [("classes.html", "המקצועות", "Character Classes", "ספר עזר · מקצועות",
              "שמונה מקצועות של אוגדן הכללים: הדרישות, טבלת הדרגות, גלגולי ההצלה והיכולות של כל אחד.",
              overview_sections())]
    for c in CLASSES:
        title = c["name"] + (f" {c['also']}" if c.get("also") else "")
        eyebrow = "ספר עזר · מקצועות" + (" · אופציונלי" if c.get("optional") else "")
        pages.append((c["file"], title, c["en"], eyebrow, c["lead"], class_sections(c)))
    pages.append(("equipment.html", "ציוד ומחירים", "Equipment", "ספר עזר · ציוד",
                  "כסף, כלי נשק ותחמושת, שריון, ציוד הרפתקנות, תחבורה ועומס.", equipment_sections()))
    for file, title, en, lead, spells, notes, intro in SPELL_PAGES:
        pages.append((file, title, en, "ספר עזר · לחשים", lead, spell_sections(spells, notes, intro)))
    for p in pages:
        (OUT / p[0]).write_text(document(*p), encoding="utf-8", newline="\n")
    print("wrote ref/:", ", ".join(p[0] for p in pages))
    # (href, name, English name, description, contents line, link label) for the index list
    return [
        ("ref/classes.html", "מקצועות", "Character Classes",
         "כל שמונת המקצועות: דרישות, טבלת דרגות עם THAC0 ולחשים ליום, גלגולי הצלה ויכולות.",
         " · ".join(c["name"] for c in CLASSES) + " · דרואיד", "דף לכל מקצוע"),
        ("ref/equipment.html", "ציוד", "Equipment",
         "כסף, כלי נשק ותחמושת, שריון, ציוד הרפתקנות, בעלי חיים, כלי רכב וכלי שיט, ועומס ותנועה.",
         "מחירים · נזק וטווח · דירוג שריון · עומס", "דף אחד"),
        ("ref/spells-cleric.html", "לחשים", "Spells",
         "כל לחשי הכוהן, הדרואיד והקוסם לפי עוצמה: טווח, משך, הפיך או לא, וסיכום קצר בעברית של כל לחש.",
         "כוהנים 56 · דרואידים 28 · קוסמים 117", "שלושה דפים"),
    ]
