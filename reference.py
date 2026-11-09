"""Hebrew web reference ("ספר עזר") for the Rules Cyclopedia: the character classes and the equipment tables.

Screen-first pages that also print on A4, built from data/tables.py and data/equipment.py. Writes into ref/:
    classes.html (overview), one page per class (fighter.html ... mystic.html), equipment.html,
    spells-cleric.html, spells-druid.html, spells-magic-user.html (lists from data/spells.py, notes from data/spell_notes.py).
Rules and page numbers: Hebrew Rules Cyclopedia ch. 2 (classes, pp. 13-31), ch. 4 (equipment, pp. 62-71),
movement p. 88, attack rolls p. 106. Wording follows the Hebrew edition; numbers the English one.
"""
import html
import json
import pathlib
import re

import combat as CB
import enchanting as EN
import encounters as ENC
import equipment as E
import magic_items as MI
import monsters as MO
import spell_notes as SN
import spells as SP
import tables as T
from bidi import dice, dice_in, fix, ltr

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

CLASSES = [CLERIC, FIGHTER, MU, THIEF, DWARF, ELF, HALFLING, MYSTIC]  # book order (ch. 2)


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


# ---------------------------------------------------------------- monsters (chapter 14, data/monsters.py)

STAT_LABELS = ["דירוג שריון", "קוביות פגיעה", "תנועה", "התקפות", "נזק", "מספר מופיעים", "ניצל כמו", "מוראל",
               "סוג אוצר", "תבונה", "נטייה", "ערך נק״נ"]
MOVE_KINDS = {"Fl": "תעופה:", "Sw": "שחייה:", "Bu": "חפירה:", "Cl": "טיפוס:", "Wb": "ברשת:"}
HEBREW = re.compile(r"[֐-׿]")


def metres(feet):
    """Feet in metres as the Hebrew edition does: feet / 3, rounded (120' -> 40, 40' -> 13)."""
    m = int(feet.replace(",", "")) / 3
    return f"{m:.1f}" if 0 < m < 1 else f"{round(m):,}"


def move(v):
    v = re.sub(r"\b(Fl|Sw|Bu|Cl|Wb) ", lambda m: MOVE_KINDS[m.group(1)] + " ", v)
    return re.sub(r"(\d[\d,]*)'", lambda m: metres(m.group(1)) + " מ׳", v)


def stat_value(i, v):
    if i == 2:
        v = move(v)
    v = html.escape(v, quote=False)
    return fix(v) if HEBREW.search(v) else ltr(v)


def mslug(en):
    return "m-" + re.sub(r"[^a-z0-9]+", "-", en.lower()).strip("-")


def plain_name(he):
    """Hebrew name without the asterisk, for sorting and search titles."""
    return he.replace("*", "").strip()


def monster_stats(kinds):
    if not kinds:
        return ""
    if len(kinds) == 1 and not kinds[0][0]:
        vals = [x.strip() for x in kinds[0][2].split("|")]
        return '<dl class="stats">' + "".join(
            f"<div><dt>{l}</dt><dd>{stat_value(i, v)}</dd></div>" for i, (l, v) in enumerate(zip(STAT_LABELS, vals))) + "</dl>"
    out = []
    for c in range(0, len(kinds), 4):           # at most four kinds side by side, as the book does
        chunk = kinds[c:c + 4]
        vals = [[x.strip() for x in k[2].split("|")] for k in chunk]
        rows = [[f"<b>{l}</b>"] + [stat_value(i, v[i]) for v in vals] for i, l in enumerate(STAT_LABELS)]
        out.append(table([""] + [k[1] for k in chunk], rows, "mstats"))
    return "".join(out)


def monster_entry(m):
    en, he, en_page, he_page, kinds, summary = m
    return (f'<div class="monster" id="{mslug(en)}">'
            f'<h3>{he} <span class="sub" lang="en" dir="ltr">{html.escape(en)}</span>'
            f'<span class="pg">עמ׳ {he_page}</span></h3>'
            f'{monster_stats(kinds)}<p>{fix(html.escape(summary, quote=False))}</p></div>')


def sorted_monsters():
    return sorted(MO.M, key=lambda m: plain_name(m[1]))


MONSTER_LEAD = "כל המפלצות של אוגדן הכללים לפי סדר האלף-בית: נתוני הקרב של כל סוג וסיכום קצר לשימוש ליד השולחן."
MONSTER_INTRO = ("הנתונים מהספר האנגלי, השמות והמונחים מהמהדורה העברית, והסיכום הקצר נכתב לשימוש ליד השולחן – "
                 "התיאור המלא בספר גובר. המרחקים במטרים (רגל חלקי 3), כמו במהדורה העברית.")
MONSTER_LEGEND = [
    ("*", "אחרי שם המפלצת: רק נשק קסום או מיוחד פוגע בה. אחרי קוביות הפגיעה: יכולת מיוחדת, שמוסיפה לערך הנק״נ."),
    ("ק ב ג", "גודל: קטן, בינוני (בגודל אדם), גדול."),
    ("( )", "בתנועה: המהירות בסיבוב קרב. במספר מופיעים: במאורה או במרחבים."),
    ("ניצל", "ל לוחם, כ כוהן, ק קוסם, גנ גנב, ג גמד, א אלף, נ זוטון; המספר הוא הדרגה."),
]


def monster_sections():
    ms = sorted_monsters()
    letters = []
    for m in ms:
        first = plain_name(m[1])[0]
        if not letters or letters[-1][0] != first:
            letters.append((first, []))
        letters[-1][1].append(m)
    index = "".join(f'<div><h3><a href="#ml{n}">{l}</a></h3><ol>'
                    + "".join(f'<li><a href="#{mslug(m[0])}">{m[1]}</a></li>' for m in group) + "</ol></div>"
                    for n, (l, group) in enumerate(letters))
    legend = '<dl class="legend">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in MONSTER_LEGEND) + "</dl>"
    out = [("list", "כל המפלצות", note(MONSTER_INTRO) + legend + f'<div class="spell-index">{index}</div>')]
    for n, (l, group) in enumerate(letters):
        out.append((f"ml{n}", l, "".join(monster_entry(m) for m in group)))
    return out


def monster_rows():
    rows = []
    for en, he, _ep, hp, kinds, summary in MO.M:
        path = f"ref/monsters.html#{mslug(en)}"
        names = " · ".join(k[1] for k in kinds if k[1])
        rows.append([plain_name(he), en, "מפלצת", path, (names + ". " if names else "") + summary])
        if len(kinds) > 1:
            base = re.sub(r"\s*\(.*?\)", "", plain_name(he))
            for k_en, k_he, _ in kinds:
                k = plain_name(k_he)
                title = k if "-" in k else f"{base} {k}"
                rows.append([title, k_en, f"מפלצת · {plain_name(he)}", path, summary])
    return rows


# ---------------------------------------------------------------- magic items (chapter 16, data/magic_items.py)

CLASS_WORDS = {"כ": "כוהן", "ד": "דרואיד", "ג": "גמד", "א": "אלף", "ל": "לוחם", "ז": "זוטון", "ק": "קוסם",
               "גנ": "גנב", "למ": "לא־מטיל לחשים", "מ": "מטיל לחשים"}
D100 = dice("1ק100")
ITEMS_PAGE, WEAPONS_PAGE = "ref/magic-items.html", "ref/magic-weapons.html"
MI_TITLE, MW_TITLE = "חפצי קסם", "נשק ושריון קסומים"
MI_LEAD = ("שיקויים, מגילות, בדידים, מטות וקנים, טבעות וחפצי קסם שונים: טבלאות הגלגול ומה כל חפץ עושה, "
           "בקיצור.")
MW_LEAD = ("שריון, כלי קליעים, חרבות וכלי נשק שונים: טבלאות היצירה, הבונוסים, הכוחות המיוחדים והכשרונות.")
MI_NOTE = ("סיכום קצר לשימוש ליד השולחן, לא נוסח הספר – התיאור המלא בספר גובר. המספרים מהספר האנגלי, השמות "
           "מהמהדורה העברית, המרחקים במטרים (רגל חלקי 3). עמוד = העמוד של התיאור במהדורה העברית, שבה התיאורים "
           "של כל קבוצה מסודרים לפי האלף-בית.")


def mi_id(prefix, en):
    return prefix + "-" + re.sub(r"[^a-z0-9]+", "-", en.lower()).strip("-")


def who(code):
    return " או ".join(CLASS_WORDS[c.strip()] for c in code.split(",")) + " בלבד" if code else ""


def rich(text):
    """Escaped Hebrew text made bidi-safe; arithmetic between ⟦ ⟧ is shown left to right as one piece."""
    parts = re.split(r"⟦(.*?)⟧", html.escape(text, quote=False))
    return "".join(ltr(dice_in(p)) if i % 2 else fix(p) for i, p in enumerate(parts))


def rules(rows):
    """(term, text) rows as a definition list; a list as the text becomes bullets."""
    def dd(v):
        return ('<ul class="bullets">' + "".join(f"<li>{rich(i)}</li>" for i in v) + "</ul>"
                if isinstance(v, list) else rich(v))
    return '<dl class="rules">' + "".join(f"<dt>{k}</dt><dd>{dd(v)}</dd>" for k, v in rows) + "</dl>"


def roll_index(prefix, items):
    """Compact 1d100 list in columns, each name linking to its entry."""
    return '<ol class="rolls">' + "".join(
        f'<li><span class="roll">{ltr(it[0])}</span><a href="#{mi_id(prefix, it[1])}">{fix(it[2])}</a>'
        + (f' <span class="code">({it[3]})</span>' if len(it) > 5 and it[3] else "") + "</li>"
        for it in items) + "</ol>"


def item_entry(prefix, it):
    roll, en, he, code, page, summary = it
    meta = [f"{D100}: {ltr(roll)}"] + ([who(code)] if code else []) + [f"עמ׳ {page}"]
    return (f'<div class="spell" id="{mi_id(prefix, en)}">'
            f'<h3>{fix(he)} <span class="sub" lang="en" dir="ltr">{html.escape(en)}</span></h3>'
            f'<p class="meta">{"".join(f"<span>{m}</span>" for m in meta)}</p>'
            f'<p>{fix(html.escape(summary, quote=False))}</p></div>')


def roll_table(head, rows, cls="rolltbl"):
    """Small roll table: every cell made bidi-safe (ranges, dice, signs)."""
    def cell(v):
        v = html.escape(str(v), quote=False)
        return fix(v) if HEBREW.search(v) else ltr(v)
    return table(head, [[cell(v) for v in r] for r in rows], cls)


def described(prefix, rows, page_col=True):
    """Table of (roll, English, Hebrew, [page,] description) with an anchor per row."""
    body = []
    for r in rows:
        roll, en, he = r[:3]
        page, desc = (r[3], r[4]) if page_col else ("", r[3])
        name = f'<b>{fix(he)}</b> <span class="sub" lang="en" dir="ltr">{html.escape(en)}</span>'
        pg = f'<td class="pg">{page}</td>' if page_col else ""
        body.append(f'<tr id="{mi_id(prefix, en)}"><td class="r">{ltr(roll)}</td><td>{name}</td>'
                    f'<td>{fix(html.escape(desc, quote=False))}</td>{pg}</tr>')
    head = f"<th>{D100}</th><th>שם</th><th>מה זה עושה</th>" + ("<th>עמ׳</th>" if page_col else "")
    return (f'<div class="tbl"><table class="desc"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def magic_item_sections():
    here = {g["id"]: "#" + g["id"] for g in MI.GROUPS}
    rows = []
    for roll, he, gid in MI.MAIN:
        href = here.get(gid, "magic-weapons.html#" + gid)
        rows.append([ltr(roll), f'<a href="{href}">{he}</a>'])
    main = table([D100, "סוג החפץ"], rows, "rolltbl")
    codes = '<dl class="legend">' + "".join(f"<dt>({k})</dt><dd>{v}</dd>" for k, v in MI.CODES) + "</dl>"
    out = [("rules", "כללים", note(MI_NOTE) + rules(MI.GENERAL)
            + f"<h3>טבלה ראשית לחפצי קסם</h3>{main}<h3>הגבלות בטבלאות המשנה</h3>{codes}")]
    for g in MI.GROUPS:
        body = rules(g["rules"])
        if g["id"] == "scrolls":
            body += "<h3>מגילות לחשים: עוצמת כל לחש</h3>" + roll_table(
                ["עוצמה", "כוהן או דרואיד", "קוסם"], [(lv, c or "–", m) for lv, c, m in MI.SPELL_SCROLL_LEVELS])
        body += f'<h3>טבלת משנה ({D100}), עמ׳ {g["table_page"]}</h3>' + roll_index(g["id"], g["items"])
        body += "".join(item_entry(g["id"], it) for it in g["items"])
        out.append((g["id"], g["he"], body))
    return out


def magic_weapon_sections():
    gen = '<div class="gen">' + "".join(
        f"<div><h3>{t}</h3>{roll_table([D100, 'כלי'], rows)}</div>"
        for t, rows in [("כלי קליעים וקליעים", MI.GEN_MISSILES), ("חרבות", MI.GEN_SWORDS),
                        ("כלי נשק שונים", MI.GEN_MISC)]) + "</div>"
    gen_note = note("השיטה הפשוטה, מומלצת לדמויות בדרגות 1–10: בוחרים או מגלגלים 1ק6 – 1–2 כלי קליעים, 3–4 חרב, "
                    "5–6 כלי נשק שונה – ואז 1ק100 בטור. לדרגות גבוהות יותר – טבלאות המשנה בהמשך.")
    ac_rows = [[n, str(b)] + [str(b - k) for k in range(1, 6)] for n, b in MI.ARMOR_BASE]
    ac_rows.append(["מגן", "−1"] + [f"−{k + 1}" for k in range(1, 6)])
    armor = (rules(MI.ARMOR_RULES)
             + '<div class="gen">'
             + f"<div><h3>גודל</h3>{roll_table([D100, 'גודל'], MI.ARMOR_SIZE)}</div>"
             + f"<div><h3>סוג</h3>{roll_table([D100, 'סוג'], MI.ARMOR_TYPE)}</div></div>"
             + "<h3>שינוי הדרג״ש וסיכוי לכוח מיוחד</h3>"
             + roll_table(["בונוס", "רצועות, קשקשים או עור", "שרשראות", "לוחות או חליפת שריון", "מגן",
                           "סיכוי לכוח מיוחד"], MI.ARMOR_BONUS)
             + "<h3>דרג״ש סופי</h3>"
             + note("הדרג״ש של השריון אחרי הבונוס; למגן – כמה הוא מוריד מהדרג״ש. שריון שרשראות +3 עם מגן +2: "
                    "2 − 3 = −1.")
             + roll_table(["", "רגיל", "+1", "+2", "+3", "+4", "+5"], ac_rows)
             + "<h3>כוחות מיוחדים</h3>" + described("ap", MI.ARMOR_POWERS))
    missiles = (rules(MI.MISSILE_RULES)
                + roll_table([D100, "פריט", "סוג הכלי"], MI.MISSILE_ITEMS)
                + '<div class="gen">'
                + f"<div><h3>כלי קליעים (סוג ד׳)</h3>"
                + roll_table(["בונוס", D100, "סיכוי להתאמה נוספת"], [(b, r, c) for b, r, c in MI.MISSILE_WEAPON_BONUS])
                + roll_table(["1ק4 + בונוס", "מכפלת טווח"], MI.MISSILE_RANGE) + "</div>"
                + f"<div><h3>קליעים (סוג א׳)</h3>"
                + roll_table(["בונוס", D100, "מספר שנמצא", "סיכוי לכשרון"], MI.MISSILE_BONUS) + "</div></div>"
                + "<h3>כשרונות קליעים</h3>" + described("mt", MI.MISSILE_TALENTS))
    swords = (rules(MI.SWORD_RULES)
              + '<div class="gen">'
              + f"<div><h3>סוג</h3>{roll_table([D100, 'סוג', 'סוג הכלי'], MI.SWORD_TYPES)}</div>"
              + f"<div><h3>בונוס</h3>{roll_table(['בונוס', 'סוג ג׳', 'סוג ד׳', 'סיכוי להתאמה נוספת'], MI.SWORD_BONUS)}"
              + "</div></div>"
              + "<h3>תבונת החרב</h3>"
              + roll_table([D100, "תבונה", "תקשורת", "שפות", "כוחות"], MI.SWORD_INT)
              + note("ר – כוח ראשוני; ח – כוח חריג; קק – קורא קסם על־פי פקודה.")
              + "<h3>כוחות ראשוניים</h3>" + described("pp", MI.PRIMARY_POWERS, page_col=False)
              + "<h3>כוחות חריגים</h3>" + described("ep", MI.EXTRA_POWERS, page_col=False))
    weapons = (rules(MI.WEAPON_RULES)
               + roll_table([D100, "כלי הנשק", "סוג הכלי"], MI.MISC_WEAPONS)
               + "<h3>בונוסים קסומים והתאמות</h3>"
               + roll_table(["בונוס", "סוג ב׳", "סוג ג׳", "סוג ד׳", "סיכוי להתאמה נוספת"], MI.WEAPON_BONUS)
               + note("* בהצלחה – טבלת ההתאמות הנוספות, בונוס נגד יריב. ** בהצלחה – ישר לכשרונות."))
    mods = (rules(MI.MODIFIER_RULES)
            + roll_table(["חרבות", "כלי נשק שונים", "התאמה נוספת"], MI.EXTRA_MODIFIERS)
            + "<h3>יריבים</h3>" + described("op", MI.OPPONENTS, page_col=False)
            + "<h3>כשרונות</h3>" + described("wt", MI.TALENTS))
    return [("generation", "טבלת יצירת כלי־נשק קסומים", gen_note + gen),
            ("armor", "שריון ומגינים", armor),
            ("missiles", "כלי קליעים וקליעים", missiles),
            ("swords", "חרבות", swords),
            ("weapons", "כלי נשק שונים", weapons),
            ("modifiers", "התאמות נוספות לכלי נשק", mods)]


def magic_rows():
    rows = []
    for g in MI.GROUPS:
        for roll, en, he, code, page, summary in g["items"]:
            rows.append([he, en, f"חפץ קסם · {g['he']}", f"{ITEMS_PAGE}#{mi_id(g['id'], en)}", summary])
    for prefix, kind, lst in [("ap", "כוח מיוחד של שריון", MI.ARMOR_POWERS),
                              ("mt", "כשרון של קליעים", MI.MISSILE_TALENTS),
                              ("wt", "כשרון של כלי נשק", MI.TALENTS)]:
        for roll, en, he, page, desc in lst:
            rows.append([he, en, kind, f"{WEAPONS_PAGE}#{mi_id(prefix, en)}", desc])
    for prefix, kind, lst in [("pp", "כוח ראשוני של חרב", MI.PRIMARY_POWERS),
                              ("ep", "כוח חריג של חרב", MI.EXTRA_POWERS)]:
        for roll, en, he, desc in lst:
            if desc and not he.startswith("גלגל"):
                rows.append([he, en, kind, f"{WEAPONS_PAGE}#{mi_id(prefix, en)}", desc])
    return rows


MAKING_PAGE, MAKING_TITLE = "ref/magic-making.html", "עתקים ויצירת קסם"
MAKING_LEAD = ("עתקים של בני האלמוות, ואיך דמויות יוצרות חפצי קסם, שריון ונשק קסומים, קונסטרוקטים, חפצים ענקיים "
               "ולחשים חדשים: הדרישות, העלויות, הזמן וסיכויי ההצלחה.")
MAKING_NOTE = ("סיכום לשימוש ליד השולחן, לא נוסח הספר – הספר גובר. המספרים מהספר האנגלי, המונחים מהמהדורה העברית; "
               "שני הספרים באותם עמודים (249–255).")


def formula(text, after=""):
    return f'<p class="formula">{rich(text)}</p>' + (note(after) if after else "")


def example(text):
    return f'<p class="example"><b>דוגמה:</b> {rich(text)}</p>'


def making_sections():
    art_head = ["", "פחות", "משני", "חזק", "עיקרי"]
    art_rows = [r if r[0] == "group" else [r[0]] + [str(v) for v in r[1:]] for r in EN.ARTIFACT_TABLE]
    artifacts = (note(MAKING_NOTE) + rules(EN.ARTIFACT_RULES)
                 + "<h3>טבלת עתקים</h3>" + table(art_head, art_rows, "rolltbl")
                 + note("השורה הראשונה – כמה כוחות יש לעתק בסך הכול; השורות הבאות – כמה מכל סוג לכל היותר.")
                 + '<h3 id="mask">עתק לדוגמה: מסכת בקראוס <span class="sub">(עתק פחות: אנטרופיה, רוע)</span></h3>'
                 + rules(EN.MASK))
    making = (rules(EN.MAKING_RULES) + "<h3>הנוסחה</h3>" + formula(EN.CHANCE, EN.CHANCE_NOTE)
              + example(EN.CHANCE_EXAMPLE))
    arms = (rules(EN.ARMS_RULES)
            + "<h3>סיכום העלויות</h3>" + table(["רכיב", "חישוב"], [[k, rich(v)] for k, v in EN.ARMS_COSTS], "rolltbl")
            + "<h3>דוגמאות מהספר</h3>" + rules(EN.ARMS_EXAMPLES)
            + '<p class="note">' + rich("בדוגמת המגן הספר לא מוסיף עלות קביעות להקסמת איש, אבל בדוגמת הדריאדות "
                                        "ובסיכום העלויות היא נוספת. לפי הסיכום המגן עולה "
                                        "⟦3,000 + 1,000 + 5,000 = 9,000⟧ פ״ז – החלטת השופט.") + "</p>")
    misc = (rules(EN.MISC_RULES)
            + "<h3>סיכום העלויות</h3>" + table(["רכיב", "חישוב"], [[k, rich(v)] for k, v in EN.MISC_COSTS], "rolltbl")
            + "<h3>דוגמאות מהספר</h3>" + rules(EN.MISC_EXAMPLES))
    constructs = (rules(EN.CONSTRUCT_RULES) + example(EN.CONSTRUCT_EXAMPLE)
                  + "<h3>הנחיות לקונסטרוקטים חדשים</h3>" + rules(EN.CONSTRUCT_GUIDES))
    return [("artifacts", "עתקים", artifacts),
            ("making", "יצירת חפצי קסם", making),
            ("arms", "שריון וכלי נשק קסומים", arms),
            ("misc", "חפצי קסם שונים", misc),
            ("constructs", "קונסטרוקטים קסומים", constructs),
            ("huge", "חפצי קסם ענקיים", rules(EN.HUGE_RULES) + example(EN.HUGE_EXAMPLE)),
            ("research", "מחקר לחשים", rules(EN.RESEARCH_RULES) + example(EN.RESEARCH_EXAMPLE)),
            ("xp", "ניסיון מיצירה ומחקר", rules(EN.XP_RULES))]


# ---------------------------------------------------------------- referee screen: chapters 7 and 8

ENC_PAGE, ENC_TITLE = "ref/encounters.html", "היתקלויות והתחמקות"
ENC_LEAD = ("נוהלי התור, היום וההיתקלות, הפתעה, מרחק ותגובה, טבלאות המפלצות המשוטטות במבוך, במרחבים, בטירה ובעיר, "
            "התחמקות ומרדף, ואיזון היתקלויות.")
COMBAT_PAGE, COMBAT_TITLE = "ref/combat.html", "קרב"
COMBAT_LEAD = ("סדר הקרב, יוזמה, מוראל, תמרונים, טבלאות גלגולי ההתקפה של הדמויות והמפלצות, קליעים ומחסה, לחשים, "
               "קרב בלתי חמוש (הכאה והיאבקות), וקרב באוויר, בים ומתחת למים.")
REF_NOTE = ("סיכום לשימוש ליד השולחן, לא נוסח הספר – הספר גובר. המספרים מהספר האנגלי, המונחים מהמהדורה העברית; "
            "העמודים זהים בשני הספרים. מרחקים במטרים, כמו במהדורה העברית.")
_MONSTER_NAMES = {m[0] for m in MO.M}


def steps(items):
    return '<ol class="steps">' + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ol>"


def notes(items):
    return "".join(f'<p class="note">{rich(t)}</p>' for t in items)


def mlink(key):
    """A monster from the encounter tables, in Hebrew, linked to its chapter 14 entry (or a class page)."""
    link, he = ENC.NAMES[key]
    if link is None:
        return fix(he)
    if not link.endswith(".html"):
        assert link in _MONSTER_NAMES, link
        link = "monsters.html#" + mslug(link)
    return f'<a href="{link}">{fix(he)}</a>'


def cells(row):
    return [rich(v) for v in row]


def encounter_sections():
    checklist = (note(REF_NOTE) + steps(ENC.ENCOUNTER_STEPS)
                 + "<h3>נוהל תור המשחק (במבוך ובשטח מסוכן)</h3>" + steps(ENC.TURN_STEPS)
                 + "<h3>נוהל יום המשחק (במסע)</h3>" + steps(ENC.DAY_STEPS)
                 + "<h3>מפלצות משוטטות</h3>" + rules(ENC.WANDERING_RULES))
    chance = (table(["סוג ההיתקלות", "איך מגלגלים", "היתקלות ב־"], [cells(r) for r in ENC.CHANCE], "rolltbl")
              + notes(ENC.CHANCE_NOTES))
    surprise = (rules(ENC.SURPRISE) + "<h3>טבלת מרחקי ההיתקלויות</h3><p class=\"cap\">כשאף צד לא מופתע.</p>"
                + table(["סביבה", "ראות", "היתקלות", "מרחק"], [cells(r) for r in ENC.DISTANCES], "rolltbl")
                + notes(ENC.DISTANCE_NOTES))
    reactions = (table(["2ק6", "תגובת המפלצת"], [[ltr(a), rich(b)] for a, b in ENC.REACTIONS], "rolltbl")
                 + rules(ENC.REACTION_RULES))
    levels = "".join(
        f'<div><h3>{lv}</h3>' + table(["1ק20", "מפלצת", "מספר"], [
            [ltr(r), mlink(k) + (f' <span class="sub">({fix(n)})</span>' if n else ""), num(c)]
            for r, k, n, c in rows], "rolltbl") + "</div>" for lv, rows in ENC.DUNGEON)
    dungeon = rules(ENC.DUNGEON_RULES) + f'<div class="gen">{levels}</div>' + note(ENC.DUNGEON_NOTE)

    def sub_link(kind):
        if kind in ENC.SUBTABLE_OF:
            return f'<a href="#sub{ENC.SUBTABLE_OF[kind]}">{kind}</a>'
        return f'<a href="#{"castle" if kind.startswith("טירה") else "city"}">{kind}</a>'
    main = table(["1ק8"] + ENC.TERRAINS,
                 [[ltr(str(i + 1))] + [sub_link(col[i]) for col in ENC.WILDERNESS] for i in range(8)], "rolltbl wild")
    subs = ""
    for n, title, heads, cols in ENC.SUBTABLES:
        die = "1ק12*" if n == 6 else "1ק12"
        subs += (f'<h3 id="sub{n}">תת־טבלה {n}. {title}</h3>'
                 + table([die] + heads, [[ltr(str(i + 1))] + [mlink(c[i]) for c in cols] for i in range(12)],
                         "rolltbl wild")
                 + (note(ENC.SUBTABLE_NOTES[n]) if n in ENC.SUBTABLE_NOTES else ""))
    wilderness = (rules(ENC.WILDERNESS_RULES) + "<h3>טבלת ההיתקלויות במרחבים</h3>" + main
                  + notes(ENC.WILDERNESS_NOTES) + subs)
    castle = (rules(ENC.CASTLE_RULES) + '<div class="gen"><div><h3>תת־טבלה 10. היתקלויות טירה</h3>'
              + table(["1ק6", "בעל הטירה", "דרגה"], [cells(r) for r in ENC.CASTLE_OWNER], "rolltbl")
              + "</div><div><h3>נטיית בעל הטירה</h3>"
              + table(["1ק6", "נטייה"], [cells(r) for r in ENC.CASTLE_ALIGNMENT], "rolltbl") + "</div></div>"
              + "<h3>טבלת תגובות הטירה</h3>"
              + table(["בעל הטירה", "סוג וגודל הפטרול", "רדיפה", "התעלמות", "ידידות"],
                      [cells(r) for r in ENC.CASTLE_REACTIONS], "rolltbl"))
    city = rules(ENC.CITY_RULES)
    for start in (0, 4):
        city += table(["1ק20"] + [f"חלק {start + j + 1}" for j in range(4)],
                      [[ltr(str(i + 1))] + [fix(ENC.CITY[start + j][i]) for j in range(4)] for i in range(20)],
                      "rolltbl wild")
    ev_rows = []
    for party, rows in ENC.EVASION:
        for i, (mon, pct) in enumerate(rows):
            ev_rows.append([ltr(party) if i == 0 else "", ltr(mon), ltr(pct)])
    evasion = (steps(ENC.EVASION_STEPS) + '<div class="gen"><div><h3>טבלת סיכויי ההתחמקות</h3>'
               + table(["גודל החבורה", "מספר המפלצות", "הסיכוי"], ev_rows, "rolltbl") + "</div><div><h3>התאמות</h3>"
               + table(["מצב", "שינוי בסיכוי"], [cells(r) for r in ENC.EVASION_MODS], "rolltbl")
               + note("בטקסט הספר הגששים הם −10%; בטבלה −15%.") + "</div></div>"
               + rules(ENC.EVASION_RULES) + '<h3 id="ships">התחמקות ספינות</h3>'
               + table(["מהירות המתחמקת לעומת הרודפת", "הסיכוי"], [cells(r) for r in ENC.SHIP_EVASION], "rolltbl")
               + rules(ENC.SHIP_RULES))
    balance = (note("חוק אפשרי, לשימוש בהיתקלויות מתוכננות.") + steps(ENC.BALANCE_STEPS) + rules(ENC.BALANCE_RULES)
               + "<h3>טבלת אתגרי ההיתקלויות</h3>"
               + table(["אחוז האתגר", "ההיתקלות", "מה זה אומר"], [cells(r) for r in ENC.CHALLENGE], "rolltbl"))
    return [("checklist", "נוהל ההיתקלות", checklist),
            ("chance", "סיכויי היתקלות", chance),
            ("surprise", "הפתעה ומרחק", surprise),
            ("reactions", "תגובת המפלצות", reactions),
            ("dungeon", "היתקלויות במבוך", dungeon),
            ("wilderness", "היתקלויות במרחבים", wilderness),
            ("castle", "היתקלויות טירה", castle),
            ("city", "היתקלויות עירוניות", city),
            ("evasion", "התחמקות ומרדף", evasion),
            ("balance", "איזון היתקלויות", balance)]


def need(raw, mark):
    """Roll needed on the Attack Rolls Tables (pp. 106-107) for raw = THAC0 - AC: 20 and 30 hold five times,
    2 holds for raw 2 to -2, then 1, then extra damage with a dagger (or * for monsters), 10 holding five times."""
    if raw >= 3:
        return str(raw if raw <= 19 else 20 if raw <= 24 else raw - 4 if raw <= 33 else 30 if raw <= 38 else raw - 8)
    if raw >= -2:
        return "2"
    if raw == -3:
        return "1"
    d = -raw - 4
    return f"{d if d < 10 else 10 if d <= 14 else d - 4}{mark}"


def ac(v):
    return ltr(f"−{-v}") if v < 0 else str(v)


def attack_tables(rows, mark, head):
    """rows: (raw THAC0, label); split into AC 19..0 and -1..-20, as the book prints them."""
    out = ""
    for acs in (range(19, -1, -1), range(-1, -21, -1)):
        out += table([head] + [ac(a) for a in acs],
                     [[fix(label)] + [need(raw - a, mark) for a in acs] for raw, label in rows], "atk")
    return out


def combat_sections():
    round_ = note(REF_NOTE) + rules(CB.ROUND) + "<h3>נוהל סדר הקרב</h3>" + rules(CB.SEQUENCE)
    morale = (rules(CB.MORALE) + "<h3>טבלת ערכי המוראל</h3>"
              + table(["סוג האישיות", "ערך המוראל"], [cells(r) for r in CB.MORALE_SCORES], "rolltbl narrow")
              + note(CB.MORALE_NOTE))
    maneuvers = (table(["תמרון הקרב", "מתי מבוצע", "מי יכול לבצע"], [cells(r) for r in CB.MANEUVERS], "rolltbl")
                 + note(CB.MANEUVERS_NOTE) + rules(CB.MANEUVER_RULES))
    attack = (steps(CB.ATTACK_STEPS) + rules(CB.THAC0_RULES) + "<h3>טבלת הגורמים המשפיעים על גלגולי התקפה</h3>"
              + table(["גורם", "התאמה לגלגול"], [cells(r) for r in CB.MODIFIERS], "rolltbl narrow")
              + note(CB.MODIFIERS_NOTE))
    who = table(["לוחם", "כוהן, גנב, דרואיד", "קוסם", "דרגת התקפה", "תלד0"],
                [[fix(f), fix(c), fix(m), fix(r), need(raw, "†")] for raw, f, c, m, r in CB.CHAR_ROWS], "rolltbl")
    chars = (who + note(CB.CHAR_NOTE) + "<h3>המספר הדרוש לפגיעה, לפי דרג״ש המטרה</h3>"
             + attack_tables([(raw, " · ".join(x for x in (f, r) if x)) for raw, f, c, m, r in CB.CHAR_ROWS],
                             "†", "לוחם · ד״ה")
             + note("השורות לפי דרגת הלוחם או דרגת ההתקפה; כוהן, גנב, דרואיד וקוסם – באותה שורה בטבלה שלמעלה. "
                    "† – נזק נוסף (אפשרי)."))
    monsters = (attack_tables(CB.MONSTER_ROWS, "*", "קוביות פגיעה")
                + note("* – נזק נוסף (אפשרי). מפלצת עם תוספת לקוביות הפגיעה (⟦3+1⟧) – בשורה של \"3+ עד 4\"."))
    missile = (rules(CB.MISSILE) + '<div class="gen"><div><h3>טבלת מחסה המטרה</h3>'
               + table(["המטרה מוסתרת", "מחסה רך", "מחסה נוקשה"], [cells(r) for r in CB.COVER], "rolltbl")
               + note(CB.COVER_NOTE) + "</div><div><h3>מטרות חלקיות</h3>"
               + table(["שניות חשיפה", "תוספת הגנה"], [[str(s), ltr(f"+{b}")] for s, b in CB.PARTIAL], "rolltbl")
               + note(CB.PARTIAL_NOTE) + "</div></div>")
    unarmed = (rules(CB.UNARMED) + '<h3 id="striking">הכאה (אפשרי)</h3>' + steps(CB.STRIKE_STEPS)
               + rules(CB.STRIKE_RULES) + "<h3>איגרוף: טבלת שליטה בקרב בלתי חמוש</h3>"
               + table(["רמה", "נזק", "השפעה מיוחדת"], [cells(r) for r in CB.BOXING], "rolltbl")
               + note(CB.MASTERY_NOTE))
    wrestling = (rules(CB.WRESTLE_RULES) + "<h3>היאבקות: טבלת שליטה בקרב בלתי חמוש</h3>"
                 + table(["רמה", "נזק", "הגנה", "השפעה מיוחדת"], [cells(r) for r in CB.WRESTLING], "rolltbl"))
    naval = (rules(CB.NAVAL) + "<h3>טבלת התקפות ניגוח</h3>"
             + table(["הספינה המנגחת", "נגד ספינה (נקודות גוף)", "נגד יצור"], [cells(r) for r in CB.RAM], "rolltbl"))
    return [("round", "סיבוב הקרב", round_),
            ("initiative", "יוזמה", rules(CB.INITIATIVE)),
            ("morale", "מוראל", morale),
            ("movement", "תנועה בקרב", rules(CB.MOVEMENT)),
            ("maneuvers", "תמרוני קרב", maneuvers),
            ("attack", "גלגול ההתקפה", attack),
            ("attack-characters", "טבלת גלגולי ההתקפה: כל הדמויות", chars),
            ("attack-monsters", "טבלת גלגולי ההתקפה: כל המפלצות", monsters),
            ("missile", "קרב קליעים", missile),
            ("magic", "קסם וגלגולי הצלה", rules(CB.MAGIC)),
            ("melee", "קפא״פ ולחימה בשני כלי נשק", rules(CB.MELEE)),
            ("unarmed", "קרב בלתי חמוש והכאה", unarmed),
            ("wrestling", "היאבקות (אפשרי)", wrestling),
            ("aerial", "קרב אווירי", rules(CB.AERIAL)),
            ("naval", "קרב ימי", naval),
            ("underwater", "קרב תת־מימי", rules(CB.UNDERWATER))]


CSS = """
:root { color-scheme:light; --ink:#1b1b1b; --muted:#5f5f5f; --paper:#fdfdfb; --line:#dcdcd6; --rule:#1b1b1b; --accent:#7b2a1c; --hover:#f3f2ee; --band:#f6f5f1; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  color-scheme:dark; --ink:#ececea; --muted:#a3a3a0; --paper:#141414; --line:#323230; --rule:#8a8a86; --accent:#e0937c; --hover:#1d1d1c; --band:#1a1a19;
} }
:root[data-theme="dark"] { color-scheme:dark; --ink:#ececea; --muted:#a3a3a0; --paper:#141414; --line:#323230; --rule:#8a8a86; --accent:#e0937c; --hover:#1d1d1c; --band:#1a1a19; }
* { box-sizing:border-box; }
html { scroll-padding-top:1rem; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:Assistant, "Segoe UI", Arial, sans-serif; line-height:1.55; font-size:1.02rem; }
a { color:var(--accent); }
.num-ltr { direction:ltr; unicode-bidi:isolate; }
.dice { direction:rtl; unicode-bidi:isolate; white-space:nowrap; }
.layout { display:grid; grid-template-columns:15rem minmax(0, 1fr); gap:3rem; max-width:76rem; margin:0 auto; padding:2.6rem 1.25rem 4rem; }
.toc { position:sticky; top:1.4rem; align-self:start; max-height:calc(100vh - 2.8rem); overflow:auto; font-size:.95rem;
  padding-inline-end:1.4rem; border-inline-end:1px solid var(--line);
  scrollbar-width:thin; scrollbar-color:transparent transparent; scrollbar-gutter:stable; }
.toc:hover, .toc:focus-within { scrollbar-color:var(--line) transparent; }
.toc::-webkit-scrollbar { width:6px; }
.toc::-webkit-scrollbar-thumb { background:transparent; border-radius:3px; }
.toc:hover::-webkit-scrollbar-thumb { background:var(--line); }
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
.monster { padding:.9rem 0 1rem; border-bottom:1px solid var(--line); max-width:52rem; }
.monster h3 { margin:0 0 .35rem; font-size:1.15rem; display:flex; flex-wrap:wrap; align-items:baseline; gap:0 .4rem; }
.monster h3 .pg { margin-inline-start:auto; font-weight:400; font-size:.82rem; color:var(--muted); }
.monster:target h3 { color:var(--accent); }
.monster p { margin:.45rem 0 0; }
.stats { display:grid; grid-template-columns:repeat(auto-fill, minmax(15rem, 1fr)); gap:0 1.4rem; margin:0; font-size:.93rem; }
.stats div { display:flex; gap:.6rem; border-bottom:1px solid var(--line); padding:.14rem 0; }
.stats dt { color:var(--muted); min-width:6.6rem; flex:none; }
.stats dd { margin:0; }
table.mstats { font-size:.9rem; }
table.mstats th:not(:first-child) { color:var(--accent); }
table.mstats td:first-child { white-space:nowrap; width:7rem; }
table.mstats td:first-child b { font-weight:400; color:var(--muted); }
table.mstats + .tbl, .tbl + .tbl { margin-top:.6rem; }
@media (max-width:38rem) { table.mstats td:not(:first-child) { min-width:7.5rem; } }
.rules { display:grid; grid-template-columns:max-content 1fr; gap:.3rem 1rem; margin:.4rem 0 1rem; max-width:52rem; font-size:.95rem; }
.rules dt { font-weight:700; margin:0; }
.rules dd { margin:0; }
.rolls { list-style:none; margin:.3rem 0 1rem; padding:0; columns:13rem; column-gap:1.6rem; font-size:.93rem; }
.rolls li { break-inside:avoid; display:flex; gap:.6rem; padding:.08rem 0; }
.rolls .roll { color:var(--muted); min-width:3.2rem; flex:none; font-variant-numeric:tabular-nums; }
.rolls a { color:var(--ink); text-decoration:none; }
.rolls a:hover { color:var(--accent); text-decoration:underline; }
.rolls .code { color:var(--muted); }
.gen { display:grid; grid-template-columns:repeat(auto-fit, minmax(16rem, 1fr)); gap:0 1.6rem; align-items:start; }
table.rolltbl, table.desc { font-size:.92rem; }
table.desc td.r { white-space:nowrap; color:var(--muted); width:3.6rem; }
table.desc td.pg { color:var(--muted); width:2.4rem; }
table.desc .sub { display:block; font-size:.8rem; color:var(--muted); font-weight:400; }
table.desc tr:target td { background:var(--band); }
table.desc tr:target b { color:var(--accent); }
.formula { margin:.4rem 0 .2rem; padding:.55rem .9rem; border-inline-start:3px solid var(--accent); background:var(--band); font-weight:700; max-width:48rem; }
.example { margin:.7rem 0 1rem; max-width:52rem; font-size:.95rem; }
.example b { color:var(--accent); }
.steps { margin:.4rem 0 1rem; padding-inline-start:1.4rem; display:grid; gap:.35rem; max-width:52rem; font-size:.95rem; }
.steps li::marker { color:var(--accent); font-weight:700; }
table.wild { font-size:.88rem; }
table.wild th:not(:first-child), table.wild td:not(:first-child) { min-width:4.6rem; }
table.wild td:first-child, table.atk td:first-child { color:var(--muted); white-space:nowrap; }
table.wild a, #dungeon table a { color:var(--ink); text-decoration:none; }
table.wild a:hover, #dungeon table a:hover { color:var(--accent); text-decoration:underline; }
table.atk { font-size:.84rem; }
table.atk th, table.atk td { padding:.2rem .3rem; text-align:center; white-space:nowrap; }
table.atk th:first-child, table.atk td:first-child { text-align:start; position:sticky; inset-inline-start:0; background:var(--paper); }
table.atk + .tbl, .tbl + .tbl { margin-top:.6rem; }
h3[id^="sub"] { scroll-margin-top:1rem; }
@media (max-width:38rem) { .rules { grid-template-columns:1fr; gap:0 0; } .rules dd { margin-bottom:.4rem; }
  table.desc td:nth-child(3) { min-width:13rem; } }
.toc .brand { display:block; color:var(--ink); text-decoration:none; font-weight:800; font-size:1.15rem; line-height:1.15; }
.toc .brand span { display:block; color:var(--muted); font-weight:400; font-size:.8rem; }
.toc .brand:hover { color:var(--accent); }
.search { margin:1rem 0 .4rem; }
.search input { width:100%; font:inherit; font-size:.95rem; color:var(--ink); background:var(--paper); border:0;
  border-bottom:1.5px solid var(--rule); padding:.35rem .1rem; border-radius:0; }
.search input:focus { outline:none; border-bottom-color:var(--accent); }
.search input::placeholder { color:var(--muted); }
.results { list-style:none; margin:.4rem 0 0; padding:0; }
.results li a { display:block; padding:.4rem .3rem; border-bottom:1px solid var(--line); color:var(--ink); text-decoration:none; }
.results li a:hover, .results li a.on { background:var(--hover); }
.results .t { font-weight:700; }
.results .k { display:block; color:var(--muted); font-size:.78rem; }
.results .x { display:block; color:var(--muted); font-size:.84rem; line-height:1.35; margin-top:.1rem; }
.results mark { background:none; color:var(--accent); font-weight:700; }
.results .none { color:var(--muted); font-size:.9rem; padding:.4rem 0; }
.searching .menu { display:none; }
section:target > h2, h3:target { color:var(--accent); }
.list { list-style:none; margin:0; padding:0; }
.item { display:grid; grid-template-columns:10rem 1fr auto; gap:.25rem 1.4rem; align-items:baseline;
  padding:.9rem .2rem; border-bottom:1px solid var(--line); color:inherit; text-decoration:none; }
.item:hover, .item:focus-visible { background:var(--hover); outline:none; }
.item:focus-visible { box-shadow:inset 0 0 0 2px var(--accent); }
.item .name { font-weight:800; font-size:1.3rem; line-height:1.15; }
.item .name .en { display:block; font-weight:400; font-size:.78rem; color:var(--muted); direction:ltr; unicode-bidi:isolate; text-align:right; }
.item .desc { margin:0; }
.item .meta { grid-column:2; margin:0; color:var(--muted); font-size:.88rem; }
.item .meta b { color:var(--ink); font-weight:600; }
.item .go { grid-row:1 / span 2; grid-column:3; align-self:center; color:var(--accent); font-weight:700; white-space:nowrap; font-size:.92rem; }
.howto { margin-top:1.2rem; }
.howto h3 { margin-top:0; }
.howto ol { margin:0; padding-inline-start:1.2rem; color:var(--muted); display:grid; gap:.2rem; }
.howto b { color:var(--ink); }
footer { color:var(--muted); font-size:.85rem; margin-top:3rem; border-top:1px solid var(--line); padding-top:.8rem; }
footer a { color:var(--accent); }
.icon-btn { display:none; }
@media (max-width:56rem) {
  .layout { grid-template-columns:1fr; gap:1.4rem; padding-top:0; }
  .toc { position:sticky; top:0; z-index:10; max-height:none; overflow:visible; background:var(--paper);
    margin:0 -1.25rem; padding:.55rem 1.25rem; border-inline-end:0; border-bottom:1px solid var(--line); }
  .bar { display:flex; align-items:center; gap:.2rem; }
  .bar .brand { flex:1; font-size:1.05rem; }
  .bar .brand span { font-size:.74rem; }
  .icon-btn { display:inline-grid; place-items:center; width:2.6rem; height:2.6rem; padding:0; border:0;
    background:none; color:var(--ink); cursor:pointer; }
  .icon-btn:hover, .icon-btn:focus-visible { color:var(--accent); outline:none; }
  .icon-btn:focus-visible { box-shadow:inset 0 0 0 1.5px var(--accent); }
  .menu-btn .i-close, .toc.open .menu-btn .i-menu { display:none; }
  .toc.open .menu-btn .i-close { display:block; }
  .toc.open .search-btn { visibility:hidden; }
  .drawer { display:none; }
  /* align-self:start (from the grid) would size a fixed grid child to its content, so set the height outright */
  .toc.open { position:fixed; inset:0; align-self:stretch; height:100vh; height:100dvh; margin:0; overflow-y:auto;
    -webkit-overflow-scrolling:touch; border:0; overscroll-behavior:contain; }
  .toc.open .bar { border-bottom:1.5px solid var(--rule); padding-bottom:.55rem; }
  .toc.open .drawer { display:block; padding-bottom:3rem; }
  .toc li a { padding:.42rem 0; font-size:1.05rem; }
  .toc ol.here a { font-size:.95rem; padding:.3rem 0; }
  .toc h2 { margin-top:1.3rem; }
  body.locked { overflow:hidden; }
  header { padding-top:.4rem; }
}
@media (max-width:38rem) {
  .item { grid-template-columns:1fr auto; gap:.2rem 1rem; }
  .item .name { grid-column:1; }
  .item .go { grid-row:1; grid-column:2; align-self:baseline; }
  .item .desc, .item .meta { grid-column:1 / -1; }
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


# ---------------------------------------------------------------- site: menu in book order, search, home page
# All paths below are from the site root; rel() turns them into links from a page in ref/ or in the root.

CLASS_LINKS = [("ref/classes.html", "במבט אחד")] + [("ref/" + c["file"], c["name"]) for c in CLASSES[:7]] + [
    ("ref/cleric.html#druid", "דרואיד"), ("ref/mystic.html", "מיסטיקן")]   # book order, druid p. 28 before mystic

# Character sheets (built by make_sheets.py), book order of the classes.
CHARACTER_SHEETS = [("sheets/cleric.html", "כוהן"), ("sheets/magic-user.html", "קוסם"),
                    ("sheets/thief.html", "גנב"), ("sheets/dwarf.html", "גמד")]

# (id, heading, [(path, label)]); chapter names from the Hebrew edition's contents, pp. 2-3.
MENU = [
    ("ch2", "פרק 2 · סוגי דמויות", CLASS_LINKS),
    ("ch3", "פרק 3 · לחשים", [("ref/" + p[0], p[1]) for p in SPELL_PAGES]),
    ("ch4", "פרק 4 · ציוד", [("ref/equipment.html", "ציוד ומחירים")]),
    ("ch6", "פרק 6 · תנועה", [("ref/equipment.html#encumbrance", "עומס ותנועה")]),
    ("ch7", "פרק 7 · היתקלות והתחמקות", [(ENC_PAGE, ENC_TITLE)]),
    ("ch8", "פרק 8 · קרב", [(COMBAT_PAGE, COMBAT_TITLE)]),
    ("ch9", "פרק 9 · קרב המוני", [("sheets/army.html", "מכונת המלחמה")]),
    ("ch12", "פרק 12 · מבצרים ושליטה", [("sheets/dominion.html", "דומיניון")]),
    ("ch14", "פרק 14 · מפלצות", [("ref/monsters.html", "מפלצות")]),
    ("ch16", "פרק 16 · אוצר", [(ITEMS_PAGE, MI_TITLE), (WEAPONS_PAGE, MW_TITLE), (MAKING_PAGE, MAKING_TITLE)]),
    ("sheets", "דפי רישום", [(p, "דף דמות – " + n) for p, n in CHARACTER_SHEETS]),
]


def rel(path, here):
    """A link to `path` (from the site root) from the page at `here` (also from the root)."""
    return path[len("ref/"):] if here.startswith("ref/") and path.startswith("ref/") else (
        "../" + path if here.startswith("ref/") else path)


def nav(here, sections):
    def item(path, label):
        cur = ' aria-current="page"' if path == here else ""
        sub = ""
        if path == here and sections:
            sub = '<ol class="here">' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t, _ in sections) + "</ol>"
        return f'<li><a href="{rel(path, here)}"{cur}>{label}</a>{sub}</li>'
    groups = "".join(f'<h2>{head}</h2><ol>{"".join(item(p, l) for p, l in links)}</ol>' for _, head, links in MENU)
    root = "../" if here.startswith("ref/") else ""
    return f"""<nav class="toc" id="toc" aria-label="תוכן">
    <div class="bar">
      <a class="brand" href="{rel("index.html", here)}">אוגדן הכללים<span>ספר עזר ודפי רישום בעברית</span></a>
      <button class="icon-btn search-btn" type="button" aria-label="חיפוש">{ICON_SEARCH}</button>
      <button class="icon-btn menu-btn" type="button" aria-label="תפריט" aria-expanded="false" aria-controls="drawer">{ICON_MENU}{ICON_CLOSE}</button>
    </div>
    <div class="drawer" id="drawer">
      <div class="search" role="search">
        <input id="q" type="search" data-root="{root}" placeholder="חיפוש: לחש, מפלצת, נשק…" aria-label="חיפוש באתר" autocomplete="off" spellcheck="false">
        <ol id="results" class="results" hidden></ol>
      </div>
      <div class="menu">{groups}</div>
    </div>
  </nav>"""


_SVG = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="{}">{}</svg>'
ICON_MENU = _SVG.format("i-menu", '<path d="M4 7h16M4 12h16M4 17h16"/>')
ICON_CLOSE = _SVG.format("i-close", '<path d="M6 6l12 12M18 6L6 18"/>')
ICON_SEARCH = _SVG.format("i-search", '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>')


SEARCH_JS = (HERE / "search.js").read_text(encoding="utf-8")


def document(here, title, en, eyebrow, lead, sections, menu_sections=True):
    body = "".join(f'<section id="{i}"><h2>{t}</h2>{h}</section>' for i, t, h in sections)
    en_html = f' <span class="en" lang="en">{html.escape(en)}</span>' if en else ""
    root = "../" if here.startswith("ref/") else ""
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · אוגדן הכללים</title>
<meta name="description" content="{html.escape(re.sub("<[^>]+>", "", lead))}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;700;800&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="layout">
  {nav(here, sections if menu_sections else None)}
  <main>
    <header>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}{en_html}</h1>
      <p class="lead">{fix(lead)}</p>
    </header>
    {body}
    <footer>מתוך אוגדן הכללים (Rules Cyclopedia), בעברית. המספרים מהספר; עמודים לפי המהדורה העברית ·
      <a href="https://github.com/itaiag/rc-sheets">קוד המקור</a></footer>
  </main>
</div>
<script src="{root}search-index.js"></script>
<script>{SEARCH_JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- search index

def plain(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def search_index(pages, extra):
    """Rows [title, English, kind, path, text]: every page, every section, every spell and equipment item."""
    rows = []
    for here, title, en, eyebrow, lead, sections in pages:
        kind = eyebrow.split(" · ")[-1] if " · " in eyebrow else eyebrow
        rows.append([title, en, "דף · " + kind, here, plain(lead)])
        for sid, head, body in sections:
            rows.append([head, "", title, f"{here}#{sid}", plain(body)[:300]])
    for file, title, _en, _lead, spells, notes, _intro in SPELL_PAGES:
        for lv, ss in spells.items():
            for s in ss:
                rows.append([s["he"], s["en"], f"{title} · עוצמה {lv}", f"ref/{file}#{slug(s['en'])}", notes[s["en"]]])
    for group, items in E.WEAPONS:
        for it in items:
            rows.append([it[0], "", f"כלי נשק · {group}", "ref/equipment.html#weapons",
                         f"נזק {it[1]}, מחיר {it[3]} פ״ז, עומס {it[4]} מט׳"])
    for ac, name, cost, enc, notes in E.ARMOR:
        rows.append([name, "", "שריון", "ref/equipment.html#armor", f"דרג״ש {ac}, מחיר {cost} פ״ז, עומס {enc} מט׳. {notes}"])
    for name, desc, cost, enc in E.GEAR:
        rows.append([name, "", "ציוד הרפתקנות", "ref/equipment.html#gear", f"{desc} מחיר {cost}".strip()])
    rows += monster_rows()
    rows += magic_rows()
    for n, title, *_ in ENC.SUBTABLES:
        rows.append([f"תת־טבלה {n}. {title}", "", "היתקלויות במרחבים", f"{ENC_PAGE}#sub{n}",
                     f"טבלת היתקלויות אקראיות במרחבים: {title}"])
    for tid, title, text in [("ships", "התחמקות ספינות", "סיכויי התחמקות ומרדף בים"),
                             ("striking", "הכאה", "הימום ונוק־אאוט בקרב בלתי חמוש, איגרוף")]:
        rows.append([title, "", "דף · " + (ENC_TITLE if tid == "ships" else COMBAT_TITLE),
                     f"{ENC_PAGE if tid == 'ships' else COMBAT_PAGE}#{tid}", text])
    rows.append(["מסכת בקראוס", "Mask of Bachraeus", "עתק לדוגמה", f"{MAKING_PAGE}#mask", EN.MASK[0][1]])
    rows += extra
    return rows


# ---------------------------------------------------------------- home page

def index_item(path, name, en, desc, meta, label, here="index.html"):
    return (f'<li><a class="item" href="{rel(path, here)}"><span class="name">{name}<span class="en">{en}</span></span>'
            f'<p class="desc">{desc}</p><p class="meta">{meta}</p><span class="go">{label} ←</span></a></li>')


HOWTO = """<div class="howto"><h3>איך מדפיסים דף רישום</h3><ol>
<li>פותחים את הדף וממלאים מה שרוצים. מה שמוקלד נשמר בדפדפן הזה.</li>
<li>לוחצים <b class="num-ltr">Ctrl+P</b> (במק: <b class="num-ltr">⌘P</b>).</li>
<li>נייר A4, שוליים <b>ללא</b>, והדפסה דו-צדדית עם היפוך לאורך הצד הארוך.</li></ol></div>"""


def home_sections(character_rows, ruler_rows):
    rulers = {r[0]: r for r in ruler_rows}
    def lst(items):
        return '<ul class="list">' + "".join(index_item(*it) for it in items) + "</ul>"
    classes = ("ref/classes.html", "מקצועות", "Character Classes",
               "כל שמונת המקצועות והדרואיד: דרישות, טבלת דרגות עם THAC0 ולחשים ליום, גלגולי הצלה ויכולות.",
               " · ".join(c["name"] for c in CLASSES) + " · דרואיד", "דף לכל מקצוע")
    spells = [("ref/" + f, t, en, lead, "טווח · משך · הפיך · סיכום", "דף אחד")
              for f, t, en, lead, *_ in SPELL_PAGES]
    equipment = ("ref/equipment.html", "ציוד", "Equipment",
                 "כסף, כלי נשק ותחמושת, שריון, ציוד הרפתקנות, בעלי חיים, כלי רכב וכלי שיט.",
                 "מחירים · נזק וטווח · דירוג שריון · עומס", "דף אחד")
    movement = ("ref/equipment.html#encumbrance", "עומס ותנועה", "Encumbrance",
                "כמה הדמות סוחבת וכמה מהר היא זזה: בסיור, במפגש ובריצה.", "טבלת עומס ומהירות", "בדף הציוד")
    monsters = ("ref/monsters.html", "מפלצות", "Monsters",
                MONSTER_LEAD, f"{len(MO.M)} ערכים · נתוני קרב · סיכום קצר", "דף אחד")
    n_items = sum(len(g["items"]) for g in MI.GROUPS)
    magic = (ITEMS_PAGE, MI_TITLE, "Magical Items", MI_LEAD,
             f"{n_items} חפצים · טבלאות גלגול · סיכום קצר", "דף אחד")
    weapons = (WEAPONS_PAGE, MW_TITLE, "Magical Weapons and Armor", MW_LEAD,
               "טבלאות יצירה · כוחות מיוחדים · כשרונות · חרבות תבוניות", "דף אחד")
    encounters = (ENC_PAGE, ENC_TITLE, "Encounters and Evasion", ENC_LEAD,
                  "הפתעה · תגובה · מפלצות משוטטות במבוך, במרחבים, בטירה ובעיר · מרדף", "דף אחד")
    combat = (COMBAT_PAGE, COMBAT_TITLE, "Combat", COMBAT_LEAD,
              "יוזמה · מוראל · תמרונים · גלגולי התקפה · מחסה · הכאה והיאבקות", "דף אחד")
    making = (MAKING_PAGE, MAKING_TITLE, "Artifacts and Making Magical Items", MAKING_LEAD,
              "עתקים · עלויות וזמן · סיכויי הצלחה · קונסטרוקטים · מחקר לחשים", "דף אחד")
    return [
        ("ch2", "פרק 2 · סוגי דמויות", lst([classes])),
        ("ch3", "פרק 3 · לחשים והטלת לחשים", lst(spells)),
        ("ch4", "פרק 4 · ציוד", lst([equipment])),
        ("ch6", "פרק 6 · תנועה", lst([movement])),
        ("ch7", "פרק 7 · היתקלות והתחמקות", lst([encounters])),
        ("ch8", "פרק 8 · קרב", lst([combat])),
        ("ch9", "פרק 9 · קרב המוני", note("דף מחושב: הדירוגים מתעדכנים תוך כדי הקלדה.") + lst([rulers["sheets/army.html"]])),
        ("ch12", "פרק 12 · מבצרים ושליטה",
         note("דף מחושב: ההכנסות ורמת האמון מתעדכנות תוך כדי הקלדה.") + lst([rulers["sheets/dominion.html"]])),
        ("ch14", "פרק 14 · מפלצות", lst([monsters])),
        ("ch16", "פרק 16 · אוצר", lst([magic, weapons, making])),
        ("sheets", "דפי רישום",
         note("דפי דמות להדפסה על A4, עם טבלת הדרגות של המקצוע עד דרגה 36. אפשר למלא שם, נטייה ותכונות במחשב, "
              "והשאר בעיפרון ליד השולחן.") + lst(character_rows) + HOWTO),
    ]


def write_pages(character_rows, ruler_rows):
    """Write ref/*.html, index.html and search-index.js. Rows: (path from root, name, English, description,
    contents line, link label) for the character sheets and the ruler sheets."""
    OUT.mkdir(exist_ok=True)
    pages = [("ref/classes.html", "המקצועות", "Character Classes", "פרק 2 · סוגי דמויות",
              "שמונה מקצועות של אוגדן הכללים: הדרישות, טבלת הדרגות, גלגולי ההצלה והיכולות של כל אחד.",
              overview_sections())]
    for c in CLASSES:
        title = c["name"] + (f" {c['also']}" if c.get("also") else "")
        eyebrow = "פרק 2 · סוגי דמויות" + (" · אופציונלי" if c.get("optional") else "")
        pages.append(("ref/" + c["file"], title, c["en"], eyebrow, c["lead"], class_sections(c)))
    for file, title, en, lead, spells, notes, intro in SPELL_PAGES:
        pages.append(("ref/" + file, title, en, "פרק 3 · לחשים", lead, spell_sections(spells, notes, intro)))
    pages.append(("ref/equipment.html", "ציוד ומחירים", "Equipment", "פרק 4 · ציוד",
                  "כסף, כלי נשק ותחמושת, שריון, ציוד הרפתקנות, תחבורה ועומס.", equipment_sections()))
    pages.append((ENC_PAGE, ENC_TITLE, "Encounters and Evasion", "פרק 7 · היתקלות והתחמקות", ENC_LEAD,
                  encounter_sections()))
    pages.append((COMBAT_PAGE, COMBAT_TITLE, "Combat", "פרק 8 · קרב", COMBAT_LEAD, combat_sections()))
    pages.append(("ref/monsters.html", "מפלצות", "Monsters", "פרק 14 · מפלצות", MONSTER_LEAD, monster_sections()))
    pages.append((ITEMS_PAGE, MI_TITLE, "Magical Items", "פרק 16 · אוצר", MI_LEAD, magic_item_sections()))
    pages.append((WEAPONS_PAGE, MW_TITLE, "Magical Weapons and Armor", "פרק 16 · אוצר", MW_LEAD,
                  magic_weapon_sections()))
    pages.append((MAKING_PAGE, MAKING_TITLE, "Artifacts and Making Magical Items", "פרק 16 · אוצר", MAKING_LEAD,
                  making_sections()))
    for p in pages:
        (HERE / p[0]).write_text(document(*p), encoding="utf-8", newline="\n")
    home = ("index.html", "אוגדן הכללים", "Rules Cyclopedia", "חוקי המבוכים והדרקונים · ספר עזר בעברית",
            "הטבלאות החשובות של אוגדן הכללים בעברית, לפי סדר הפרקים בספר, ודפי רישום להדפסה. "
            "החיפוש מוצא כל לחש, מפלצת, חפץ קסם, מקצוע ופריט ציוד; המקש / קופץ אליו.", home_sections(character_rows, ruler_rows))
    (HERE / "index.html").write_text(document(*home, menu_sections=False), encoding="utf-8", newline="\n")
    extra = [[n, en, "דף רישום", p, d] for p, n, en, d, *_ in character_rows + ruler_rows]
    rows = search_index(pages, extra)
    js = "window.RC_INDEX=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (HERE / "search-index.js").write_text(js, encoding="utf-8", newline="\n")
    print("wrote ref/:", ", ".join(p[0][4:] for p in pages))
    print(f"wrote index.html, search-index.js ({len(rows)} entries, {len(js) // 1024} KB)")
