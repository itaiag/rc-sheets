# rc-sheets — notes for AI assistants

Printable Hebrew A4 sheets for the D&D **Rules Cyclopedia** (TSR 1071, 1991; Hebrew edition "אוגדן הכללים"),
published at **https://itaiag.github.io/rc-sheets/** from the `main` branch root (GitHub Pages, `.nojekyll`).
Read `README.md` for what exists. This file is how the work is done, so a new session can continue it.

## The people
- The owner (Itai) writes to you in English; everything on the sheets is in **Hebrew**. Code, comments, commit
  messages and this file are in English.
- The owner does not know these rules well. A referee (שופט) in his group plays them and sends requests in Hebrew.
  When a request is rules-heavy, read the rules, decide the sensible reading, build it, and then **list the
  interpretations you made** so the owner can pass them to the referee. Don't stop to ask about every detail.
- Design taste: restrained and editorial — paper, ink, thin rules, one accent colour (`#7b2a1c`). No gradients,
  rounded "cards", pills, emoji or glow. He called the earlier rounded-card index "too much like vibe coding".
- Scope: do what was asked. Fill-in fields were added only to the RC sheets on purpose ("no need for the other
  projects at this stage"); on character sheets only name, player, alignment, abilities (+ auto bonus) and the
  portrait are editable, because everything else changes during play and is written in pencil.

## Sources — the books
Both PDFs sit in the repo root, **git-ignored** (copyrighted; never commit them):
- `אוגדן-הכללים.pdf` — Hebrew edition. Original: `G:\My Drive\Books\RPG\Dungeons & Dragons BECMI Edition\אוגדן הכללים.pdf`.
  PDF index = printed page number (e.g. War Machine 117–120, dominion 138–142).
- `Rules-Cyclopedia.pdf` — English original (archive.org copy). Page index is close to the printed number; check.

Use `tools/book.py` (`find`, `page`, `image`; usage in its docstring). **The Hebrew PDF is reversed OCR**: the
script flips lines back, which reverses digits/Latin inside them, and OCR mixes ם/ס, ו/ן, ה/ח. So:
take **numbers and tables from the English book** (or from a rendered page image of the Hebrew book — use
`image` and look at the PNG), and take **wording from the Hebrew book**. Every table in `data/` and `rulers.py`
carries a page number comment; keep doing that.

## Terminology (the owner cares about this)
1. Hebrew Rules Cyclopedia wording wins, even where it differs from the Basic Fantasy (BFRPG) Hebrew glossary.
2. Only when the Hebrew RC has no term: BFRPG glossaries in `C:\Users\itaiag\git\node\bfrpg\translator\glossary-*.json`,
   the BFRPG Hebrew book `bfrpg\he\*.qmd`, then the campaign vault `C:\Users\itaiag\git\obsidian\snw-campaign\Spells`.
3. When the Hebrew edition is wrong or missing something, fix it and say so in `README.md` (examples there:
   "יצירת מים" misprint, the missing "בריא" confidence band).
4. Distances: feet / 3 in metres (120' → 40 m), 10' → 3 m, 100' → 30 m — as the Hebrew edition does.
Dice are written Hebrew style: `2ק6`, `1ק8+2`.

## Layout and files
| File | Role |
|---|---|
| `make_sheets.py` | Builds `sheets/*.html` and `index.html` (template `INDEX`, rows from `index_item`). Run after any change. |
| `data/tables.py`, `data/spells.py` | Transcribed class tables and spell lists (with page numbers). |
| `rulers.py` / `rulers.js` / `rulers.css` | Dominion and army sheets: HTML builder, live calculations, styles. `write_pages()` returns the index rows. |
| `reference.py` | Builds the web reference `ref/*.html` (classes, equipment); `write_pages()` returns the index rows. Not A4 sheets: screen-first pages with their own inline CSS. |
| `data/equipment.py` | Equipment tables (ch. 4) and the movement/encumbrance table, with page numbers. |
| `bidi.py` | `ltr`, `dice`, `dice_in`, and `fix()` (dice, ranges like `1–2` and signed numbers in Hebrew text). |
| `sheet.css` | Base stylesheet, copied from `bfrpg/printable-sheets` (a sister project with BFRPG sheets), additions at the end. |
| `sheet.js` | Fill-in script for character sheets. |
| `tools/book.py`, `tools/check.py` | Read the books; render/verify the sheets. `tools/out/` is ignored. |

Generated HTML is committed (Pages serves it). Each sheet is **one self-contained file**: CSS and JS are inlined by
`document()`; only Google Fonts (Assistant) is external. Write files with `newline="\n"`.

### How a sheet page is built
- Each printed page is a `<section class="sheet">` (A4). Sizes are **em off a container-relative font size**
  (`1.55cqi`), so the sheet scales on screen and is exactly A4 in print. Don't use px inside a sheet.
- `@page { size: A4; margin: 0 }`; users print with margins "none", double-sided, flip on long edge.
- **Bidi in RTL text** — the most common bug:
  - numbers/Latin that must stay in order: wrap in `ltr()` → `<span class="num-ltr">`;
  - dice: `dice()` / `dice_in()` (otherwise `1ק8` shows as `ק18`);
  - signed numbers (`+10`, `−5`, `+25%`): `rulers.signs()` wraps them automatically in ruler pages. Use the real
    minus `−` (U+2212). Write "+ 150 +" rather than "+150+".
- Screen-only things (buttons, notes, placeholders) get `.screen-only` / hidden under `@media print`.

### Fill-in and calculated sheets
- Inputs carry `data-key="…"`, computed outputs `data-out="…"`. Values are saved in `localStorage` under
  `"rc-sheets:" + file name`, always inside try/catch (storage can be blocked). A "ניקוי הדף" button clears it.
- `rulers.js` recomputes everything on every input from the saved `data` object. Army forces use keys `f{i}.…`
  and are cloned from `<template id="force-tpl">` with `__I__` placeholders; deleting a force shifts the keys down.
- Every rule implemented in JS has a page-number comment. Rules decided by interpretation are listed in `README.md`.

## Verifying (do this before saying something is done)
1. `python make_sheets.py`
2. `python tools/check.py` — reports JS errors per page and writes PNG per page + PDF to `tools/out/`.
   **Open the PNGs/PDF and look**: overflowing boxes, a page spilling onto a second sheet, reversed numbers.
3. For calculations, reproduce the **book's own worked examples** with Playwright (`page.fill('[data-key=…]')`,
   read `[data-out=…]`). Already verified: dominion p.140 example (3,200 gp, 1,200 XP, +40 families);
   War Machine elf-prince force (BFR 86 → troop class טובה, BR 140). Re-run the relevant one after touching the maths.
   Use `wait_until="load"`, not `networkidle` (the font request can hang it).
Playwright runs Edge (`channel="msedge"`); `pymupdf` and `playwright` are installed.

## Publishing
The owner has been happy for each finished feature to be committed and pushed to `main` (that deploys).
Commit messages: plain English summary line. Then confirm it is live:
```
gh api repos/itaiag/rc-sheets/pages/builds/latest --jq '.status+" "+.commit[0:7]'   # wait for "built <sha>"
curl -s https://itaiag.github.io/rc-sheets/ | grep -o "<h1>[^<]*</h1>"
```
Add every new sheet to the index: a row via `index_item(...)` in the right section ("דפי דמות" or
"שליטה ומלחמה"; add a new section if it fits neither), and a back link `← חזרה לרשימת הדפים` in its screen note.
Update `README.md` too.

## Gotchas met so far
- Bash heredocs mangle quotes and `\n` in Python/JS; write scripts and code with the file-writing tool instead.
- A wrapper element inside the centred sheet grid collapsed to zero width → give it `width:100%`.
- Query selectors on the root element itself (`doc.querySelector(".r-doc")` from inside `.r-doc`) return null.
- The sister project `C:\Users\itaiag\git\node\bfrpg` must be rebuilt (`node build-he.js`) before its sheets change
  on its site; the Obsidian vault has its own copy of the BFRPG sheets in `.scripts/character_sheets/`.

## Possible next steps (ideas, not commitments — ask the owner which)
Character sheets for the remaining classes (fighter, elf, halfling, mystic, druid — their tables are in `data/tables.py`), spells in the reference, weapon mastery tracker, stronghold building costs,
spell reference cards, encumbrance/equipment price list, a referee screen (attack, saving throw, turn undead,
reaction and morale tables), monster stat cards.
