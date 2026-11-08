"""Search or dump the two Rules Cyclopedia PDFs kept (untracked) in the repo root.

    python tools/book.py find  he "מכונת המלחמה" "דירוג קרב"   # page indexes + lines containing the words
    python tools/book.py find  en "War Machine" "Battle Rating"
    python tools/book.py page  he 117 118                       # full text of those pages
    python tools/book.py image he 117 [zoom]                    # render to tools/out/he-117.png, then look at it

`he` = אוגדן-הכללים.pdf (Hebrew edition), `en` = Rules-Cyclopedia.pdf (TSR 1071).
Page arguments are 0-based PDF indexes. In the Hebrew PDF the index equals the printed page number
(index 141 shows "141" in the footer); check the footer on the rendered image when it matters.

The Hebrew PDF is OCR stored in visual order: every line comes out reversed. This script flips each line back,
which fixes the Hebrew but also reverses digits and Latin text inside it ("051" may be 150). The OCR also
confuses ם/ס, ו/ן, ה/ח. Before copying a number or table from the Hebrew book, render the page image and read it,
or take the number from the English book.
"""
import pathlib
import re
import sys

import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)  # the English PDF spams harmless content-stream errors
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOKS = {"he": ROOT / "אוגדן-הכללים.pdf", "en": ROOT / "Rules-Cyclopedia.pdf"}


def lines(doc, lang, i):
    out = [l.strip() for l in doc[i].get_text().splitlines() if l.strip()]
    return [l[::-1] for l in out] if lang == "he" else out


def main(cmd, lang, *args):
    doc = pymupdf.open(BOOKS[lang])
    if cmd == "find":
        for i in range(len(doc)):
            for l in lines(doc, lang, i):
                if any(k.lower() in l.lower() for k in args):
                    print(f"{i:3} | {l}")
    elif cmd == "page":
        for a in args:
            text = "\n".join(lines(doc, lang, int(a)))
            if lang == "en":
                text = re.sub(r"-\n", "", text)
            print(f"===== {lang} {a}\n{text}")
    elif cmd == "image":
        out = ROOT / "tools" / "out"
        out.mkdir(exist_ok=True)
        zoom = float(args[1]) if len(args) > 1 else 2
        path = out / f"{lang}-{args[0]}.png"
        doc[int(args[0])].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(path)
        print(path)


if __name__ == "__main__":
    main(*sys.argv[1:])
