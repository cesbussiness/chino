import re

TONE_MARKS = {
    'a': 'āáǎàa', 'e': 'ēéěèe', 'i': 'īíǐìi', 'o': 'ōóǒòo', 'u': 'ūúǔùu',
    'v': 'ǖǘǚǜü', 'ü': 'ǖǘǚǜü',
}


def numbered_syllable_to_accented(syll):
    """Convert numbered pinyin (CC-CEDICT format) to accented form,
    e.g. 'gou4' -> 'gòu', 'nu:3'/'nv3' -> 'nǚ', 'r5'/'de5' -> neutral tone."""
    m = re.match(r'^([a-zA-Z:]+)([0-9])$', syll)
    if not m:
        return syll
    letters, tone = m.group(1), int(m.group(2))
    letters = letters.replace('u:', 'v').replace('U:', 'V')
    # 'v' is CC-CEDICT's ASCII placeholder for u-umlaut (lv/nv -> lü/nü) —
    # convert it unconditionally, not just for the neutral-tone early return.
    letters = letters.replace('v', 'ü').replace('V', 'Ü')
    if tone == 5 or tone == 0:
        return letters
    lower = letters.lower()
    target = None
    if 'a' in lower:
        target = lower.index('a')
    elif 'e' in lower:
        target = lower.index('e')
    elif 'ou' in lower:
        target = lower.index('o')
    else:
        for i, ch in enumerate(lower):
            if ch in 'iouü':
                target = i
        if 'iu' in lower:
            target = lower.index('iu') + 1
        elif 'ui' in lower:
            target = lower.index('ui') + 1
    if target is None:
        return letters
    ch = letters[target]
    base = ch.lower()
    if base not in TONE_MARKS:
        return letters
    accented_char = TONE_MARKS[base][tone - 1]
    if ch.isupper():
        accented_char = accented_char.upper()
    return letters[:target] + accented_char + letters[target + 1:]


def numbered_pinyin_to_accented(numbered):
    """'gou4 wu4 che1' -> 'gòu wù chē'"""
    parts = numbered.strip().split()
    return ' '.join(numbered_syllable_to_accented(p) for p in parts)


def normalize_pinyin(s):
    """Lowercase, strip whitespace/apostrophes/hyphens, for loose comparison."""
    if s is None:
        return ''
    s = s.lower()
    s = s.replace("'", '').replace(' ', '').replace('-', '')
    return s


def strip_tone_marks(s):
    table = str.maketrans({
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'ü', 'ǘ': 'ü', 'ǚ': 'ü', 'ǜ': 'ü',
    })
    return s.translate(table)
