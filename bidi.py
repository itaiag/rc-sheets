"""Keep numbers, dice and signs in the right order inside Hebrew (RTL) text. Shared by the sheets and the reference."""
import re


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


# A number range or list such as 1–2, 25/45/70, 60–80, 1,600–2,400: shown reversed in RTL without an LTR isolate.
RANGE = re.compile(r"(?<![\w֐-׿\"=])(\d+(?:[,.]\d+)*(?:\s?[–/×]\s?\d+(?:[,.]\d+)*)+)")
# A signed number: +10, −5, +25%.
SIGNED = re.compile(r"(?<![\w֐-׿])([+−±]\d+(?:[,.]\d+)*%?)")


def fix(text):
    """Dice, ranges and signed numbers in a Hebrew text, each wrapped so it reads correctly."""
    text = dice_in(text)
    text = RANGE.sub(lambda m: ltr(m.group(1)), text)
    return SIGNED.sub(lambda m: ltr(m.group(1)), text)
