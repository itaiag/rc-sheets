# Rules Cyclopedia in Hebrew: reference and record sheets

A Hebrew web reference for the D&D Rules Cyclopedia (TSR 1071, 1991), plus printable A4 record sheets:
character sheets (cleric, magic-user, thief, dwarf, with level tables up to 36) and dominion and army sheets.

`index.html` is the home page. Every page has the same sidebar: a search box and a menu in the book's chapter order
(chapter names from the Hebrew edition's contents, pp. 2-3): 2 classes, 3 spells, 4 equipment, 6 movement,
9 mass combat (army sheet), 12 strongholds and dominions (dominion sheet), 14 monsters, 16 treasure (magical items), and "דפי רישום" (the book's name for
record sheets, appendix 3) with the character sheets. On phones the menu folds under "תוכן העניינים".

## Search

No Quarto needed: `reference.py` writes `search-index.js` (one row per page, section, spell, weapon, armor and gear
item, monster and magical item (with armor powers, weapon talents and sword powers), plus one row per monster kind such as זאב-אדם: title, English name, kind, link, text), and `search.js` (inlined in every page) searches it in the browser.
Matching is substring over normalised Hebrew: niqqud removed, final letters folded (ם = מ), geresh and gershayim
dropped (נקפ finds נק״פ), hyphens as spaces (אל מתים finds אל-מתים). Title matches rank above English names, which
rank above text matches; text matches show a snippet. Keys: `/` jumps to the box, arrows move, Enter opens, Esc
clears. `?q=…` in the URL fills it.

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

- `monsters.html`: all 187 entries of chapter 14 in Hebrew alphabetical order, with a contents block by letter.
  Each monster has its Hebrew page number, its combat statistics (a list for one kind, a table with one column per
  kind for several, at most four side by side) and a short Hebrew summary. Anchors use the English name
  (`#m-lycanthrope`, `#m-dragon-red`).

- `magic-items.html`: chapter 16's general rules and main table, then potions, scrolls (with the spell scroll
  levels), wands/staves/rods, rings and miscellaneous items: each group's rules, its 1d100 subtable as a compact list
  and a short Hebrew summary per item, with the class limitation and the Hebrew page (`#potions-healing`).
- `magic-weapons.html`: the simple Magical Weapon Generation Table (levels 1-10), then armor and shields, missile
  weapons and missiles, swords (intelligence, alignment, will power, primary and extraordinary powers),
  miscellaneous weapons, and the additional modifiers (opponents and talents). Armor powers, missile talents and
  weapon talents have summaries and anchors (`#wt-flaming`).
- `magic-making.html` (pp. 249-255): artifacts (rules, the Artifacts Table, the Mask of Bachraeus), making
  magical items (requirements, chance of success), magical armor and weapons and miscellaneous items (rules, the
  book's cost summaries and worked examples), magical constructs, huge magical items (buildings and vessels), spell
  research, and experience for all of these. Arithmetic is shown left to right (`⟦…⟧` in `data/enchanting.py`).
  Not included yet: special treasure, cashing treasure and selling magical items (pp. 227, 249).

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
- Monsters: numbers from the English book, names and terms from the Hebrew edition; movement in metres (feet / 3,
  rounded). Summaries are written for this project, like the spell summaries. Where the English book is missing a
  number the Hebrew edition's is used: gargantuan gargoyle AC 1 and ML 11, mountain giant IN 11, every kind of men
  IN 11 (English gives it only for dervishes), manticore AC 4, revener ML 11 (the Hebrew AC 4 is kept as the
  English −4), druj ML 11, wraith ML 11. English printed page 196 is blank in the scan, so the Neanderthal,
  nekrozon and nightshades come from the Hebrew edition (pp. 157, 196, 206). The medium pterosaur's move is fixed
  from 240' (120') to 240' (80'). The elf's XP of 6 is kept as printed in both editions.
- Magical items: numbers from the English book, names from the Hebrew subtables (pp. 228-231). The Hebrew edition
  sorts each group's descriptions alphabetically, so its description pages differ from the English ones; the
  pages shown are the Hebrew ones. Its sword table swaps the rolls of clairaudience and clairvoyance (01-10/11-20);
  the page follows the English. The wand subtable marks every wand (ק), magic-user only, while the text says a
  wand is for a magic-user or an elf; the page keeps the table's mark and says so in the wand rules. The Hebrew
  descriptions head the delusion ring "תעתוע"; the page uses the subtable's "הזיות".
- Making magical items: the book's own examples disagree with its rules in a few places, and the page says so.
  The shield +2 with charm person costs 4,000 gp in the book, without the 5× permanency cost that the dryad example
  and the cost summary add (9,000 gp by the summary; the referee decides). The crystal ball's ESP chance is
  printed 72%; the formula gives 70%. The English wand of polymorph others takes "31 days"; one week plus 14 is 21,
  as the Hebrew edition prints. The dryad sword's 25.2 extra days come out as 32 days in the book, though rounding up
  gives 33. A nonrechargeable item is −20% of the initial enchantment cost in the text, of the total cost in the
  summary box; both are shown. The chain mail's 5,333 gp is not rounded up to tens as the rule says. The minimum
  armor cost (3,000 gp) is applied after multiplying by the bonuses, as in the shield example. The Hebrew
  artifacts table calls the handicap "מגבלה" and the text "נכות"; the page shows "מגבלה (נכות)". The bronze golem
  keeps the monsters chapter's name "גולם ברונזה" (the making text says "ארד"). The 20' cube of dispel magic is 7 m,
  as in the Hebrew edition. XP for spell research is allowed but the book gives no amount.
- Ships list rowing and sailing speeds in separate columns, in the Hebrew edition's km per day.

## Filling in before printing

On screen, the character name, player name, alignment and the six ability scores can be typed in, and the portrait box
takes an uploaded image. The ability bonus is filled in from the score (Rules Cyclopedia p. 9).
Everything else stays blank for pencil. What is typed is saved in the browser's local storage, per sheet,
and "ניקוי הדף" clears it.

## Files

- `make_sheets.py` builds `sheets/*.html`, then calls `reference.py`, which builds `index.html`, `ref/*.html` and
  `search-index.js`. Run `python make_sheets.py` after any change.
- `search.js` is the search box script, inlined into every reference page.
- `data/tables.py` holds XP, hit dice, THAC0, saving throws, spells per day, turn undead and thief abilities,
  transcribed from the book (page numbers in the comments).
- `data/monsters.py` holds the monsters: Hebrew and English names, pages, statistics per kind and the summary.
- `data/magic_items.py` holds chapter 16: main table, subtables with summaries, and the weapon and armor tables.
- `data/enchanting.py` holds artifacts and the making rules (pp. 249-255) as (term, text) rows, cost summaries and
  examples.
- `data/spells.py` holds the cleric and magic-user spell lists with Hebrew names, range and duration.
- `sheet.js` is the fill-in script (fields, ability bonus, portrait upload). It is inlined into every sheet.
- `sheet.css` is the stylesheet of the Basic Fantasy Hebrew sheets (`bfrpg/printable-sheets`), with a few additions at the end.

## Translation

Hebrew terms follow the Hebrew edition of the Rules Cyclopedia ("אוגדן הכללים"): spell names, saving throws,
thief abilities, undead names, attack ranks (ג–מ) and weapon mastery ("שליטה בנשק").
Distances follow that edition too: feet / 3 in meters (120' = 40 m), except 10' = 3 m.
The Hebrew edition's cleric list misprints Create Water as "עצירת מים"; the sheet uses "יצירת מים" from the spell's own heading.

THAC0 is the "Armor Class 0" column of the book's Attack Rolls Table (p. 106).
