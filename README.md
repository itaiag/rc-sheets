# Rules Cyclopedia in Hebrew: reference and record sheets

A Hebrew web reference for the D&D Rules Cyclopedia (TSR 1071, 1991), plus printable A4 record sheets:
character sheets (cleric, magic-user, thief, dwarf, with level tables up to 36) and dominion and army sheets.

`index.html` is the home page. Every page has the same sidebar: a search box and a menu in the book's chapter order
(chapter names from the Hebrew edition's contents, pp. 2-3): 1 character creation, 2 classes, 3 spells, 4 equipment, 5 other character abilities (weapon mastery,
general skills), 6 movement,
7 encounters and evasion, 8 combat, 9 mass combat (army sheet), 10 experience, 11 retainers, mercenaries and
specialists, 12 strongholds and dominions (building strongholds, dominion sheet), 13 DM procedures (checks, special conditions), 14 monsters (how to read an entry, the monster list), 16 treasure (treasure types, magical items), and "דפי רישום" (the book's name for
record sheets, appendix 3) with the character sheets. On phones the menu folds under "תוכן העניינים".
On wide screens (84rem and up) a second menu, "בדף זה", sits on the left with the current page's sections and
marks the one being read; on narrower screens those sections stay nested under the page in the right-hand menu.

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

- `creation.html` (chapter 1, pp. 6-12): the twelve steps of character creation, abilities and the bonus table, class
  requirements, adjusting scores, hit dice, money, armor class, attack rolls and saving throws, Intelligence and
  languages, Charisma, alignment, name and background, heights and weights, and experience bonuses.
- `classes.html`: all eight classes at a glance, and how to read the tables.
- One page per class (fighter, cleric with the druid, magic-user, thief, dwarf, elf, halfling, mystic): requirements,
  experience table with hit dice, THAC0 and spells per day (demihuman attack ranks included), saving throws,
  special abilities, and the class's own tables (turn undead, thief skills, mystic abilities, traveling fighters).
- `equipment.html`: money, weapons (Hebrew edition's note letters, with the legend), ammunition, armor,
  adventuring gear, riding animals and land gear, ships, encumbrance and movement.
- `weapons-armor.html` (chapter 4, pp. 63-68): the Weapon Special Effects Table (עילפון, הימום, עיכוב, סיבוך,
  האטה), every weapon description in Hebrew alphabetical order (`#w-bola`, `#w-lance` …), nets with the net size
  table, polearms and their kinds, shield weapons with the breakage roll, using a one-handed weapon with two hands,
  armor descriptions (`#a-chain` …), suit armor, and barding (the barding and barding encumbrance tables, barding
  for other creatures). Weapon and armor names on `equipment.html` link to their descriptions.
  The Hebrew edition's griffon barding example prints the cost as 200 gp; it is 400 × 5 = 2,000 gp (English
  p. 67), and the page shows 2,000. Mounts' movement is feet / 3 like the rest of the site (riding horse 80 m
  (27 m)), where the Hebrew barding table rounds the round speed to 25 m. The misprint is also noted on the page,
  under the example.
- `spells-cleric.html` (56), `spells-druid.html` (28), `spells-magic-user.html` (117): every spell by level with
  range, duration, a reversible mark, and a one- or two-line Hebrew summary. A contents block at the top lists
  them all; each spell has its own anchor (`#s-fireball`).

- `monster-rules.html` (chapter 14 opening, pp. 152-156): what each line of a monster entry means (asterisks,
  sizes, number appearing in dungeon and lair, save-as letters, morale, treasure in parentheses), the description
  lines (monster type and rarity, diet words, terrain words, load, barding multiplier), abbreviated listings with
  the Hebrew edition's example, the special attacks (`#sa-energy-drain`, `#sa-swallow` …), special defenses, the
  monster types (`#mt-undead` …), and the Type of Human and NPC Reasons for Appearing checklists. Links go to the
  spells, conditions, morale, treasure and monsters it names.
- `monster-variants.html` (end of chapter 14, pp. 214-218): the eight ways to vary monsters with the book's
  examples, the Monster Intelligence Table, size modifiers with the gorgon example and the XP rule, age,
  environmental variations, monster spellcasters (shamans and wokani: rules, the Maximum Spellcaster Ability Table
  linked to the monsters, notes a-g, and the shaman and wokan spell lists linked to the spell pages), lycanthrope
  and undead spellcasters, and undead lieges and pawns: limits, procedure, the Undead Attempts to Control Other
  Undead Table, benefits to a liege, the War Machine factors for an undead army, turning pawns, duration of
  control and energy drainers. Interpretations and corrections: the control table is computed from its diagonal
  (3-5-7-9-11) and matches the English table; the Hebrew edition swaps the wight (נקזן) and wraith (רפא) rows of
  that table, the page follows the English book and the Hebrew text ("a spectre could control up to 12 wights")
  and says so; the Hebrew edition leaves out note [a] for the greater efreeti, the page has it; range of control
  is 40 km per Hit Die, as the Hebrew edition gives 24 miles.
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
- `treasure.html` (chapter 16, pp. 224-228 and 249-250): dividing and choosing treasure, the random treasure
  checklist and the rocs example, the treasure types tables (in lairs A-O, carried P-V; each type has an anchor,
  `#tt-H`, and the treasure types on `monsters.html` link to it), average values, coins, gems (values, variable
  size and quality, damaged gems), jewelry (values, types and definitions), special treasure, and cashing treasure.
- `experience.html` (chapter 10, pp. 127-131): the five ways to gain XP, the Experience Points for Monsters
  table and the asterisk rules, XP for treasure and for selling magical items, rate of gain, maximum hit points,
  paths to Immortality, and creating high-level characters (the twelve steps, magical item prices).
- `mastery.html` (chapter 5, pp. 75-81): weapon choices by level, levels of mastery and attack bonuses, training
  time, cost and chance of success, the whole Weapons Mastery Table (every weapon at the five levels: range,
  damage, defense, special effects), the special effects and the three special effects tables, other polearms,
  the despair effect, weapon-using monsters and retroactive mastery.
- `skills.html` (chapter 5, pp. 81-86): skill slots, skill rolls, improving and learning skills, the sample skills
  by ability, a short description of every skill, the optional language rule, vessel types, and the DM's rules
  (modifiers, time, using skills together and against each other).
- `movement.html` (chapter 6, pp. 87-90): game time, distances and maps, movement rates and encumbrance,
  overland movement (terrain effects, km per day by terrain and mount, resting, getting lost, food), swimming and
  drowning, ships and aerial travel, and the optional water movement (weather) table.
- `npcs.html` (chapter 11, pp. 132-133): retainers (hiring step by step, the Retainer Reaction Table, morale,
  treasure and experience), the Mercenaries Table by race, and specialists with their monthly pay and skills.
- `strongholds.html` (chapter 12, pp. 134-139): who may build a stronghold and how, by class; independent
  strongholds and the Ruler Reactions Table; noble and royal titles and forms of address; the construction process
  (clearing the area, plans, costs, time, engineers); the Fortifications Table with finishing details, footnotes
  and notes on each detail; stronghold retainers by class; the stronghold staff (servitors, peasants, the advisors
  and officials with pay and who they answer to, squires and ladies-in-waiting); and after the stronghold is built.
  The dominion rules that follow (pp. 139-142) are on the dominion sheet.
- `procedures.html` (chapter 13, pp. 143-151, for players as much as for the referee): ability checks, climbing,
  doors and secret doors, listening, how thief abilities are rolled; the special conditions (blindness, deafness,
  invisible foes, paralysis, prone, sleep, stunning) with a summary table, starvation and dehydration; haste and
  other speed effects, charm person and the Duration of Charm Table, anti-magic, damage to magical items; aging and
  maximum ages, alignment changes, creating, retiring and transferring characters, the magic-user's first spells
  and lost spell books; demihuman clan relics; and the DM's advice (arguments, clues, mapping, records). Each
  condition has an anchor (`#c-paralysis`) and a search row.
- `encounters.html` (chapter 7, pp. 91-101): the encounter, game turn and game day checklists, chance of encounter,
  surprise and encounter distances, monster reactions, the dungeon tables (levels 1-10), the wilderness table with
  subtables 1-9 (each monster linked to its entry on `monsters.html`), castle encounters and reactions, city
  encounters, evasion and pursuit (with ships), and balancing encounters.
- `combat.html` (chapter 8, pp. 102-115): the round and combat sequence, initiative, morale, movement, combat
  maneuvers, the attack roll checklist and modifiers, the attack roll tables for characters and monsters (AC 19 to
  −20, computed from the book's rule), missile fire and cover, magic and saving throws, two-weapon combat, striking
  and wrestling with their mastery tables, and aerial, naval and underwater combat. Siege combat links to
  `siege.html`.
- `siege.html` (pp. 72-74, 115-116, 120, 122-126): siege weapons and miscellaneous siege equipment with their tables
  and descriptions (the Hebrew edition's metric ranges, sizes and per-30-cm costs), pitch shot, siege specialists,
  structural damage (attack and target kinds, the Special Attacks Checklist, special damage types), fire and fire
  fighting, the War Machine's simple siege rules, and the Siege Machine: attacker and defender options, preparations,
  order of events, results by tactic, casualties, BR bonuses of siege equipment, ammunition, payroll and sustenance
  with the Clerics and the Create Food Spell Table, concealed information, special squads, field construction,
  post-siege damage and attacks on part of a fortification. Linked from `equipment.html`, `combat.html` and the
  army sheet. The book prints 215 for a 12th level cleric's maximum on the create food table (2 × 108 = 216); the
  page keeps 215 and notes it.

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
- Encounters: the Hebrew edition sorts every wilderness subtable alphabetically in Hebrew, so its d12 rolls differ
  from the English book's (same odds); the page keeps the English order. The city subtable has no numbers, so it
  keeps the Hebrew edition's own order. The Hebrew wilderness table reads "חיה" for roll 8 in the barren column;
  the page follows the English Dragon. Its castle subtable sorts the demihumans as elf, dwarf, halfling; the page
  follows the English (1-2 dwarf 12th, 3-4 elf 10th, 5-6 halfling 8th). Scouts lower the evasion chance by 15% in
  the table and 10% in the text; the page shows the table's number and says so. Ship speeds and the closing rate
  are in metres (30' a round = 10 m), outdoor yards as metres, as the Hebrew edition does. "Dervish" is shown as
  the subtable's "בדואי"; merchant and trader are both "סוחר" in the Hebrew edition.
- Combat: the attack roll tables are generated from the rule on p. 105 (20 and 30 hold for five steps, 2 for raw
  2 to −2, then 1, then extra damage with † or *, 10† holding for five steps), checked against the printed
  tables. The demihuman attack ranks use the Hebrew letters (א–מ). Encounter, wrestling and naval distances
  are feet / 3.
- Character creation: the height and weight table is the Hebrew edition's own metric one (metres, weights in
  coins). The druid's experience bonus is the cleric's (Wisdom), as in the English table. The druid's maximum is
  30th level, reached only after the special challenge (Hebrew p. 12).
- Weapon mastery: the table's numbers are from the English book's page images; weapon names are the equipment
  page's (the Hebrew mastery table sometimes uses others: גרזן קרב, פטיש מלחמה, תלת קלשון). Ranges are feet / 3
  rounded, 5' = 1.5 m; the Hebrew mastery table rounds a few differently (35' as 11 m). The book marks some damage
  values with ✱ (the legend's "melee weapon, may be thrown") without saying what it means there; the page keeps
  the mark and says so (ask the referee). Typos fixed: tusked shield and normal sword encumbrance printed in gp
  (275, 60) are cn. Whip and net costs are per 30 cm and about per m². In the Hebrew edition's other-polearm list
  the bill and gisarme are כילף and מנקור.
- General skills: English printed page 84 is blank in the scan, so Hunting to Persuasion are summarised from the
  Hebrew edition (pp. 83-85). The Hebrew term is "מיומנויות כלליות"; the combat and encounter pages now use it.
  Skill penalties are written as the book does, "+1" to the roll is worse (roll under the ability).
- Treasure: numbers from the English book's page images, gem, jewelry and special treasure names from the Hebrew
  edition (brooch is its "פריפה"). The book prints each treasure table in two parts and merges rows ("L,N,O",
  "J,K"); the page shows every letter on its own row. Special treasure prices are per square metre as in the
  Hebrew edition (the English book: square yard).
- Experience: the Hebrew edition says a human's maximum hit points come from eight Hit Dice; the English book
  (and its own table) says nine, and the page says nine. The book gives the mystic fighter hit points and a
  maximum of 113, but the mystic's class table rolls 1d6 (+2 a level after 9th), which gives 95; the page shows
  both (ask the referee). Rods are "קנה" as on the magical items page (the chapter 10 price table says "שרביט").
- Movement: travel distances are the English miles × 1.6, rounded to 5 km. The Hebrew table gives the ox 10 and
  5 km a day in mountains and desert; the English 8 and 6 miles make 15 and 10 km, and the page uses those. The
  overland rule is written as "the speed in metres a turn is about the km a day in open terrain" (40 m → 40 km).
  The English loaded-on-foot rows of the travel table do not match its own speed ÷ 5 rule; the page keeps the
  table. Flying travel is 120 km (mount) and 190 km (fast flyer) a day.
- NPCs: the Hebrew edition calls a retainer "מלווה" (and also "שכיר") and a mercenary "שכיר חרב"; the page uses
  both as it does. The mercenaries table is read from the English page image (– = not available for that race).
- Strongholds: the Fortifications Table is read from the English page image, with the Hebrew edition's names.
  Sizes are feet / 3. The Hebrew table writes the buildings' 120' of walls as 120 m for the stone building (40 m for
  wood), the wooden wall's BR bonus per 3 m instead of 7 m (20'), the exterior door 2 × 2.5 m instead of 2 × 1.5;
  the page uses 40 m, 7 m and 2 × 1.5. The book gives the keep as 60' a side and 80' high in the text but
  80' × 60' × 60' in the table; the page shows the table and notes the text. The map hex is the Hebrew edition's
  12 km and patrols reach 40 km. Staff titles are the dominion sheet's.
- DM procedures: both editions print the starvation table's movement for 75%-99% hit points lost as ×3/4, after
  ×3/4 and ×1/2; the page shows ×1/4 and says so (the referee decides). Distances are feet / 3: falling 1d6 per
  3 m, a secret door search covers 3 × 3 m a turn (the Hebrew edition says "3 square metres"), the relic's turning
  range is 120 m and drops 1.5 m a use, the lightship and the moonlight fabric fly 120 m a turn (the Hebrew
  edition says a round; the English book says a turn). The Hebrew edition turns the relic oils' ounces into grams
  at 2 g an ounce; the page says ounces (about 28 g). Cure serious wounds keeps the spell list's "ריפוי פצעים
  קשים", thief abilities the thief page's names.
- Ships list rowing and sailing speeds in separate columns, in the Hebrew edition's km per day.

## Filling in before printing

On screen, the character name, player name, alignment, the six ability scores and the description
(age, hair, eyes, height, weight) and the experience adjustment (התאמת נק״נ, e.g. 10%, from a high prime
requisite) can be typed in, and the portrait box
takes an uploaded image. The ability bonus is filled in from the score (Rules Cyclopedia p. 9).
The character name is copied to the name line at the top of every later page.
Everything else stays blank for pencil. What is typed is saved in the browser's local storage, per sheet,
and "ניקוי הדף" clears it.

## Files

- `make_sheets.py` builds `sheets/*.html`, then calls `reference.py`, which builds `index.html`, `ref/*.html` and
  `search-index.js`. Run `python make_sheets.py` after any change.
- `search.js` is the search box script, inlined into every reference page.
- `data/tables.py` holds XP, hit dice, THAC0, saving throws, spells per day, turn undead and thief abilities,
  transcribed from the book (page numbers in the comments).
- `data/siege.py` holds the siege chapters (pp. 72-74, 115-116, 120, 122-126) as tables and (term, text) rows.
- `data/weapons_armor.py` holds the chapter 4 descriptions (pp. 63-68) as (id, term, text) rows and small tables.
- `data/monster_variants.py` holds the end of chapter 14 (pp. 214-218).
- `data/monster_rules.py` holds the chapter 14 opening (pp. 152-156) as (term, text) rows; «label|key» marks a link.
- `data/monsters.py` holds the monsters: Hebrew and English names, pages, statistics per kind and the summary.
- `data/magic_items.py` holds chapter 16: main table, subtables with summaries, and the weapon and armor tables.
- `data/enchanting.py` holds artifacts and the making rules (pp. 249-255) as (term, text) rows, cost summaries and
  examples.
- `data/mastery.py` holds chapter 5 (weapon mastery rules and table, special effects, general skills).
- `data/treasure.py` and `data/experience.py` hold the rest of chapter 16 (treasure types, gems, jewelry, special
  treasure, cashing) and chapter 10 (experience).
- `data/movement.py` and `data/npcs.py` hold chapters 6 (time, travel, terrain, water) and 11 (retainers,
  mercenaries, specialists).
- `data/strongholds.py` holds chapter 12 up to p. 139 (authorities, titles, Fortifications Table, retainers,
  staff).
- `data/procedures.py` holds chapter 13 (checks, conditions, starvation, magic, the character over time, relics,
  running the game).
- `data/creation.py` holds chapter 1 (steps, ability tables, alignment, heights and weights, experience bonuses).
- `data/encounters.py` and `data/combat.py` hold chapters 7 and 8 (tables, checklists and rules as (term, text)
  rows).
- `data/spells.py` holds the cleric and magic-user spell lists with Hebrew names, range and duration.
- `sheet.js` is the fill-in script (fields, ability bonus, portrait upload). It is inlined into every sheet.
- `sheet.css` is the stylesheet of the Basic Fantasy Hebrew sheets (`bfrpg/printable-sheets`), with a few additions at the end.

## Translation

Hebrew terms follow the Hebrew edition of the Rules Cyclopedia ("אוגדן הכללים"): spell names, saving throws,
thief abilities, undead names, attack ranks (ג–מ) and weapon mastery ("שליטה בנשק").
Distances follow that edition too: feet / 3 in meters (120' = 40 m), except 10' = 3 m.
The Hebrew edition's cleric list misprints Create Water as "עצירת מים"; the sheet uses "יצירת מים" from the spell's own heading.

THAC0 is the "Armor Class 0" column of the book's Attack Rolls Table (p. 106). Page 1 has a row of boxes for
armor class −5 to 9 that the player fills in by hand, THAC0 under 0; the how-to note reminds that the book holds
20 for five armor classes before 21.
