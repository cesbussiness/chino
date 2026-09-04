"""
Builds CHAR_RADICALS (character -> radical/component breakdown) for every
character in CHAR_DICT, used by the "Practicar escritura" mode to show a
character's radical(s) while writing it — requested by the user after
seeing this in a reference dictionary app.

Requires: pip install pycccedict
Downloads (and caches next to this script): Make Me a Hanzi's dictionary.txt
(~2.5 MB, MIT-compatible / Arphic Public License data, same project as the
stroke data in src/hanzi-data.js) — not committed to the repo since it's an
easily re-fetched external source file.

Usage: python3 tools/audit/build_char_radicals.py
Prints the resulting CHAR_RADICALS object as JSON to stdout — paste it into
src/hanzi-data.js (as `const CHAR_RADICALS = ...;`) replacing the existing
one if regenerating.

Method: for each character, parses Make Me a Hanzi's `decomposition` field
(an IDS string like "⿰纟娄") to get its component characters, and looks up
each component's own pinyin/meaning — preferring CHAR_DICT (if that
component is itself one of our 456 words, for consistency with the rest of
the app), then CC-CEDICT (preferring a common-word reading over a bare
surname entry, e.g. 戈 -> "dagger-axe" not "surname Ge"), then falling back
to Make Me a Hanzi's own English gloss for pure radical forms that aren't
CEDICT words (纟, 亻, 氵...). The component matching `radical` in the source
data is flagged for the UI to highlight.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

from pycccedict.cccedict import CcCedict

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_JS = REPO_ROOT / 'src' / 'app.js'
DICT_URL = 'https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt'
DICT_CACHE = Path(__file__).parent / '_makemeahanzi_dictionary.txt'

sys.path.insert(0, str(Path(__file__).parent))
from pinyin_utils import numbered_pinyin_to_accented

IDS_OPS = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻')


def is_component_char(c):
    if c in IDS_OPS or c == '？':
        return False
    cp = ord(c)
    return (0x2E80 <= cp <= 0x2EFF or 0x2F00 <= cp <= 0x2FDF or
            0x3400 <= cp <= 0x4DBF or 0x4E00 <= cp <= 0x9FFF)


def load_mmh_dict():
    if not DICT_CACHE.exists():
        print(f'Downloading {DICT_URL} ...', file=sys.stderr)
        urllib.request.urlretrieve(DICT_URL, DICT_CACHE)
    out = {}
    for line in DICT_CACHE.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        out[e['character']] = e
    return out


def main():
    lines = APP_JS.read_text(encoding='utf-8').splitlines()
    CHAR_DICT = json.loads(lines[0][len('const CHAR_DICT = '):-1])
    chars = list(CHAR_DICT.keys())
    mmh = load_mmh_dict()

    print('Loading CC-CEDICT...', file=sys.stderr)
    d = CcCedict()
    simp_index = {}
    for e in d.entries:
        simp_index.setdefault(e['simplified'], []).append(e)
        simp_index.setdefault(e['traditional'], []).append(e)

    def resolve_component(c):
        if c in CHAR_DICT:
            py, meaning = CHAR_DICT[c]
            return py, meaning
        m = mmh.get(c) or {}
        mmh_def = m.get('definition', '')
        mmh_py = (m.get('pinyin') or [''])[0]
        if c in simp_index:
            candidates = simp_index[c]
            common = [e for e in candidates if e['pinyin'][:1].islower()]
            if common:
                e = common[0]
                return numbered_pinyin_to_accented(e['pinyin']), '; '.join(e['definitions'][:1])
            if mmh_def and not mmh_def.lower().startswith('surname'):
                return mmh_py, mmh_def
            e = candidates[0]
            return numbered_pinyin_to_accented(e['pinyin']), '; '.join(e['definitions'][:1])
        return mmh_py, mmh_def

    out = {}
    for ch in chars:
        e = mmh.get(ch)
        if not e:
            continue
        seen = []
        for c in e.get('decomposition', ''):
            if is_component_char(c) and c not in seen and c != ch:
                seen.append(c)
        if not seen:
            continue
        radical = e.get('radical')
        components = []
        for c in seen[:4]:
            py, meaning = resolve_component(c)
            if not py and not meaning:
                continue
            meaning = re.split(r' \(Kangxi radical', meaning)[0]
            if len(meaning) > 55:
                meaning = meaning[:52].rsplit(' ', 1)[0] + '…'
            components.append({'c': c, 'p': py, 'e': meaning, 'radical': c == radical})
        if components:
            out[ch] = components

    print(f'{len(out)}/{len(chars)} characters got a component breakdown', file=sys.stderr)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
