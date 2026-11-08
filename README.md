# Rules Cyclopedia character sheets (Hebrew)

Printable A4 character sheets in Hebrew for the D&D Rules Cyclopedia (TSR 1071, 1991):
dwarf, cleric, magic-user and thief, with level tables up to level 36 (dwarf: 12 plus attack ranks C–M).

Open `index.html`, pick a class, and print with Ctrl+P (A4, no margins).

## Pages

| Class | Pages |
|---|---|
| Dwarf | sheet, level table, inventory |
| Cleric | sheet, level table, turn undead, inventory, 2 spell pages |
| Magic-user | sheet, level table, inventory, 4 spellbook pages |
| Thief | sheet, level table, thief abilities, inventory |

## Ruler sheets

Two more sheets for high-level characters, with automatic calculations as you type (`rulers.py`, `rulers.js`, `rulers.css`):

- **Dominion** (`sheets/dominion.html`, 3 pages): hexes, families and resources; standard, tax and resource income;
  liege share, tithe, staff pay, holidays and visitors; treasury; confidence level from d% + 150 + the ruler's
  six ability scores, with the level's effects applied to income. Page 2 lists staff and specialists with the
  book's pay, page 3 is a reference (confidence levels, population growth, resources, visitors).
  Rules: Hebrew Rules Cyclopedia pp. 133 and 138-142.
- **Army** (`sheets/army.html`): one War Machine page per force (add or delete forces on screen) that works out
  the basic force rating, troop class and battle rating from the force's make-up, leader, training and gear;
  plus a summary page with every force, the battle modifiers and the combat results table. Rules: pp. 117-120.

Notes: the Hebrew edition leaves out the "Healthy" confidence level (300-349); the sheet calls it "בריא".
Distances use the Hebrew edition's 30 m for the book's 100'. Percentages of a force count the officers and troops,
not the leader, and fractions are rounded up, as in the book's examples.

## Reference (ספר עזר)

Web pages for reading on screen (they also print), in `ref/`, built by `reference.py`:

- `classes.html`: all eight classes at a glance, and how to read the tables.
- One page per class (fighter, cleric with the druid, magic-user, thief, dwarf, elf, halfling, mystic): requirements,
  experience table with hit dice, THAC0 and spells per day (demihuman attack ranks included), saving throws,
  special abilities, and the class's own tables (turn undead, thief skills, mystic abilities, traveling fighters).
- `equipment.html`: money, weapons (Hebrew edition's note letters, with the legend), ammunition, armor,
  adventuring gear, riding animals and land gear, ships, encumbrance and movement.
- `spells-cleric.html` (56), `spells-druid.html` (28), `spells-magic-user.html` (117): every spell by level with
  range, duration, a reversible mark, and a one- or two-line Hebrew summary. A contents block at the top lists
  them all; each spell has its own anchor (`#s-fireball`).

Data: `data/tables.py` (classes), `data/equipment.py` (chapter 4 and p. 88), `data/spells.py` (lists, range,
duration) and `data/spell_notes.py` (the summaries).

About the spell summaries: they are written for this project from the English descriptions, using the Hebrew
edition's terms, and are reminders at the table, not the rules; the book wins. They are not the Hebrew edition's
text. Saving throws are vs. spells unless named. Outdoor yards are written as metres, as the Hebrew edition does
(pass plant, weather control). Where the Hebrew edition has no term the summaries use plain Hebrew
("סימולקרום", "יציר (קונסטרוקט)"). Armor classes of created walls drop the book's second number in brackets. Pages are screen-first, with a
contents sidebar; tables wider than a phone scroll inside their own box.

Decisions and corrections (worth telling the referee):
- Weapon ranges use the Hebrew edition's own metres (long bow 25/45/70). Exception: the Hebrew bola reads 5/15/20;
  the English 20/40/60' is the spear's range, so the page uses the spear's 7/15/20.
- The Hebrew net note converts badly (1 sp per m², a 2×2 m net at 3.6 gp); the page says a medium 2×2 m net costs
  3.6 gp and 36 cn, about 1 gp and 10 cn per m². Rafts: the Hebrew 1 gp per m² and 6×6 m sections are fixed to
  100 gp per 3×3 m section (the book's 1 gp per square foot, 10'×10').
- Encounter speeds are feet / 3 (13, 10, 7, 3, 2 m per round); the Hebrew table prints 15 and 5 for some rows while
  its text says 13.
- Elf hit points at 10th level: +2 (Hebrew summary and English class details), not the +1 of the English summary.
- The druid's tables equal the cleric's from 9th level, so the druid is a section of the cleric page.
- Ships list rowing and sailing speeds in separate columns, in the Hebrew edition's km per day.

## Filling in before printing

On screen, the character name, player name, alignment and the six ability scores can be typed in, and the portrait box
takes an uploaded image. The ability bonus is filled in from the score (Rules Cyclopedia p. 9).
Everything else stays blank for pencil. What is typed is saved in the browser's local storage, per sheet,
and "ניקוי הדף" clears it.

## Files

- `make_sheets.py` builds `sheets/*.html` and `index.html`. Run `python make_sheets.py` after any change.
- `data/tables.py` holds XP, hit dice, THAC0, saving throws, spells per day, turn undead and thief abilities,
  transcribed from the book (page numbers in the comments).
- `data/spells.py` holds the cleric and magic-user spell lists with Hebrew names, range and duration.
- `sheet.js` is the fill-in script (fields, ability bonus, portrait upload). It is inlined into every sheet.
- `sheet.css` is the stylesheet of the Basic Fantasy Hebrew sheets (`bfrpg/printable-sheets`), with a few additions at the end.

## Translation

Hebrew terms follow the Hebrew edition of the Rules Cyclopedia ("אוגדן הכללים"): spell names, saving throws,
thief abilities, undead names, attack ranks (ג–מ) and weapon mastery ("שליטה בנשק").
Distances follow that edition too: feet / 3 in meters (120' = 40 m), except 10' = 3 m.
The Hebrew edition's cleric list misprints Create Water as "עצירת מים"; the sheet uses "יצירת מים" from the spell's own heading.

THAC0 is the "Armor Class 0" column of the book's Attack Rolls Table (p. 106).
