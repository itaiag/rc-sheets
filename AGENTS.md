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
- The site is for the **whole group, players as well as the referee**. Write pages so a player can use them at the
  table (what my character can do, how far we get, what it costs), and don't pitch features or summaries as
  "for the referee" only. Interpretations still go to the referee, because he rules on them.
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
| `make_sheets.py` | Builds `sheets/*.html`, then calls `reference.write_pages(character_rows, ruler_rows)`. Run after any change. |
| `data/tables.py`, `data/spells.py` | Transcribed class tables and spell lists (with page numbers). |
| `rulers.py` / `rulers.js` / `rulers.css` | Dominion and army sheets: HTML builder, live calculations, styles. `write_pages()` returns the index rows. |
| `reference.py` | Builds the home page `index.html`, the web reference `ref/*.html` (classes, spells, equipment) and `search-index.js`. `MENU` is the sidebar in book chapter order; `home_sections()` the home page; `search_index()` the search rows. Screen-first pages with their own inline CSS, not A4 sheets. |
| `search.js` | Client-side search over `window.RC_INDEX` (normalised Hebrew substring match), inlined into every reference page. |
| `data/equipment.py` | Equipment tables (ch. 4) and the movement/encumbrance table, with page numbers. |
| `data/monsters.py` | Chapter 14: `M = [(English, Hebrew, English page, Hebrew page, kinds, summary)]`, kinds `(en, he, "AC \| HD \| MV \| … \| XP")` with Hebrew values (MV in feet, converted when rendered). Shown on `ref/monsters.html`. |
| `data/magic_items.py` | Chapter 16: `MAIN`, `GROUPS` (potions, scrolls, wands, rings, misc: `(roll, English, Hebrew, class code, Hebrew page, summary)`), armor/weapon roll tables, armor powers, talents, sword powers. Shown on `ref/magic-items.html` and `ref/magic-weapons.html`. The Hebrew edition sorts descriptions alphabetically, so Hebrew pages differ from English ones. |
| `data/enchanting.py` | Chapter 16, pp. 249-255: artifacts and the making rules as `(term, text)` rows (a list as text = bullets), cost summaries and worked examples; text between ⟦ ⟧ is arithmetic shown left to right (`reference.rich()`). Shown on `ref/magic-making.html`. |
| `data/movement.py` | Chapter 6, pp. 87-90: time, distance, overland (terrain effects, `TRAVEL` in English miles per day, converted by `reference.km()`), swimming, ships, the water weather table. Shown on `ref/movement.html`. |
| `data/npcs.py` | Chapter 11, pp. 132-133: retainers (hiring steps, reaction table), `MERCENARIES` (gp/month by race, None = not available), `SPECIALISTS`. Shown on `ref/npcs.html`. Retainer = מלווה, mercenary = שכיר חרב. |
| `data/procedures.py` | Chapter 13, pp. 143-151: ability checks, climbing, doors, listening, thief rolls, `CONDITIONS` `(id, name, bullets)` and a summary, starvation tables, haste, charm (duration table), anti-magic, item damage, aging, alignment, relics, running the game. Shown on `ref/procedures.html` (anchors `#c-<id>`). |
| `data/creation.py` | Chapter 1, pp. 6-12: creation steps, ability, language, Charisma, height/weight and experience-bonus tables, alignment and background as `(term, text)` rows. Shown on `ref/creation.html`. |
| `data/mastery.py` | Chapter 5, pp. 75-86: weapon mastery rules, `GROUPS` (the Weapons Mastery Table: `(English, Hebrew, P, tags, cost, enc, 5 rows of (range in feet, damage, defense, effects))`), special effects and their tables, and `SKILLS` `(English, Hebrew, abilities, summary)`. Shown on `ref/mastery.html` and `ref/skills.html`. |
| `data/treasure.py` | Chapter 16, pp. 224-228, 249-250: dividing, choosing (checklist, example), `LAIR`/`CARRIED` treasure types `{letter: ([5 coins], [gems, jewelry, special, magic])}` with `(chance, amount)` or None, averages, coins, gems, jewelry, special treasure, cashing. Shown on `ref/treasure.html` (rows `#tt-A`, linked from the monsters' treasure types). |
| `data/experience.py` | Chapter 10, pp. 127-131: the five ways, monster XP steps and `XP_TABLE` `(HD, base, bonus per asterisk)`, treasure, exceptional actions, rate, maximum hit points, Immortality paths, high-level characters and magical item prices. Shown on `ref/experience.html`. |
| `data/encounters.py` | Chapter 7, pp. 91-101: checklists, surprise, distances, reactions, dungeon and wilderness tables (English roll order), castle and city subtables, evasion, balancing. Monsters are English keys; `NAMES` maps them to (chapter 14 entry or class page, Hebrew). Shown on `ref/encounters.html`. |
| `data/combat.py` | Chapter 8, pp. 102-115: sequence, initiative, morale, maneuvers, modifiers, missile and cover, striking and wrestling, aerial, naval, underwater. The attack roll tables are computed by `reference.need()` from the row THAC0s, not transcribed. Shown on `ref/combat.html`. |
| `data/spell_notes.py` | Short Hebrew spell summaries (`CLERIC`, `DRUID`, `MU`) keyed by the English names in `data/spells.py`; shown on `ref/spells-*.html`. |
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
Add every new page to `MENU` in `reference.py` under its book chapter (Hebrew chapter names from the
Hebrew edition's contents, pp. 2-3), and to `home_sections()`; character sheets go under "דפי רישום". Sheets keep
a back link `← חזרה לאוגדן הכללים` in their screen note. New searchable things (monsters, magic items) are rows
added in `search_index()`: `[title, English, kind, path from root, text]`, with an anchor id on the page.
Update `README.md` too.

## Gotchas met so far
- Bash heredocs mangle quotes and `\n` in Python/JS; write scripts and code with the file-writing tool instead.
- A wrapper element inside the centred sheet grid collapsed to zero width → give it `width:100%`.
- A `position:fixed; inset:0` element that is a grid child with `align-self:start` sizes to its content, not the
  screen, so `overflow:auto` never scrolls (the mobile menu bug). Give it `align-self:stretch` and `height:100dvh`.
  Test phone menus with a scroll check (`scrollHeight` > `clientHeight`), not only screenshots.
- Query selectors on the root element itself (`doc.querySelector(".r-doc")` from inside `.r-doc`) return null.
- The sister project `C:\Users\itaiag\git\node\bfrpg` must be rebuilt (`node build-he.js`) before its sheets change
  on its site; the Obsidian vault has its own copy of the BFRPG sheets in `.scripts/character_sheets/`.

## Possible next steps (ideas, not commitments — ask the owner which)
Character sheets for the remaining classes (fighter, elf, halfling, mystic, druid — their tables are in `data/tables.py`), weapon mastery tracker, stronghold building costs,
spell reference cards, a printable one-sheet table screen for referee and players (the tables are on `ref/combat.html` and `ref/encounters.html`),
printable monster stat cards, a calculator for magical item cost and chance of success, special treasure.
