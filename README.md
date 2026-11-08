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

## Files

- `make_sheets.py` builds `sheets/*.html` and `index.html`. Run `python make_sheets.py` after any change.
- `data/tables.py` holds XP, hit dice, THAC0, saving throws, spells per day, turn undead and thief abilities,
  transcribed from the book (page numbers in the comments).
- `data/spells.py` holds the cleric and magic-user spell lists with Hebrew names, range and duration.
- `sheet.css` is the stylesheet of the Basic Fantasy Hebrew sheets (`bfrpg/printable-sheets`), with a few additions at the end.

## Translation

Hebrew terms follow the Hebrew edition of the Rules Cyclopedia ("אוגדן הכללים"): spell names, saving throws,
thief abilities, undead names, attack ranks (ג–מ) and weapon mastery ("שליטה בנשק").
Distances follow that edition too: feet / 3 in meters (120' = 40 m), except 10' = 3 m.
The Hebrew edition's cleric list misprints Create Water as "עצירת מים"; the sheet uses "יצירת מים" from the spell's own heading.

THAC0 is the "Armor Class 0" column of the book's Attack Rolls Table (p. 106).
