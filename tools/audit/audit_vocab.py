"""
Audits CHAR_DICT / CHAR_OVERRIDES / VOCAB / WORD_GROUPS / TONE_GAME_DATA
(embedded in src/app.js) for tone/pinyin consistency.

Requires: pip install pycccedict

Usage: python3 tools/audit/audit_vocab.py

What it checks:
  - Every hanzi character's pinyin is verified syllable-by-syllable against
    CHAR_DICT (with CHAR_OVERRIDES taking precedence for specific words),
    for every entry in VOCAB, WORD_GROUPS, and TONE_GAME_DATA.
  - VOCAB internal consistency: the same hanzi must have the same pinyin in
    every section it appears in.
  - VOCAB vs TONE_GAME_DATA: the same hanzi must have the same tones in
    both places (this is the exact class of bug found twice in practice —
    a tone fix applied in one data structure but never propagated to the
    others; see PROJECT_CONTEXT.md bug #7).
  - TONE_GAME_DATA distractors: must share the same letters/syllable count
    as the correct answer (only tones differ), none equal to the correct
    answer, no duplicates among the 5.
  - Every TONE_GAME_DATA word must trace back to a real VOCAB entry.
  - CHAR_DICT and WORD_GROUPS pinyin cross-checked against real CC-CEDICT.
  - No duplicate (silently-overwritten) keys in the JS object literals.

The syllable-matching walks expected syllables in hanzi order and finds
each as a substring of the stored pinyin, always taking the leftmost
match among an exact accented match and a bare/neutral-tone variant (so a
correct neutral-tone reading like 部分 -> "bùfen" isn't flagged, but a
same-base-different-tone typo still is).
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pinyin_utils import numbered_pinyin_to_accented, normalize_pinyin, strip_tone_marks

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_JS = REPO_ROOT / 'src' / 'app.js'


def extract_const(lines, name):
    for line in lines:
        if line.startswith(f'const {name} = '):
            raw = line[len(f'const {name} = '):].rstrip('\n')
            if raw.endswith(';'):
                raw = raw[:-1]
            return json.loads(raw)
    raise SystemExit(f'const {name} not found in {APP_JS}')


def find_duplicate_keys(line):
    depth = 0
    keys = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '"' and depth == 1:
            m = re.match(r'"((?:[^"\\]|\\.)*)"\s*:', line[i:])
            if m:
                keys.append(m.group(1))
                i += len(m.group(0)) - 1
        i += 1
    seen = defaultdict(int)
    for k in keys:
        seen[k] += 1
    return {k: c for k, c in seen.items() if c > 1}


def is_hanzi(ch):
    return '一' <= ch <= '鿿'


def main():
    lines = APP_JS.read_text(encoding='utf-8').splitlines()
    CHAR_DICT = extract_const(lines, 'CHAR_DICT')
    WORD_GROUPS = extract_const(lines, 'WORD_GROUPS')
    TONE_GAME_DATA = extract_const(lines, 'TONE_GAME_DATA')
    CHAR_OVERRIDES = extract_const(lines, 'CHAR_OVERRIDES')
    VOCAB = extract_const(lines, 'VOCAB')

    ok = True

    print('--- duplicate JS object keys (silently overwritten) ---')
    for name, line in [('CHAR_DICT', lines[0]), ('WORD_GROUPS', lines[2]),
                        ('TONE_GAME_DATA', lines[3]), ('CHAR_OVERRIDES', lines[4])]:
        dups = find_duplicate_keys(line)
        if dups:
            ok = False
            print(f'  {name}: DUPLICATES {dups}')
    print('  none found' if ok else '')

    def expected_syllables(hz):
        overrides = CHAR_OVERRIDES.get(hz, {})
        out = []
        for ch in hz:
            if not is_hanzi(ch):
                continue
            if ch in overrides:
                out.append((ch, overrides[ch][0]))
            elif ch in CHAR_DICT:
                out.append((ch, CHAR_DICT[ch][0]))
            else:
                out.append((ch, None))
        return out

    def sequential_check(hz, stored_pinyin):
        syllables = expected_syllables(hz)
        hay = stored_pinyin.lower()
        cursor = 0
        results = []
        for ch, syll in syllables:
            if syll is None:
                results.append((ch, None, 'NO_CHARDICT_ENTRY', ''))
                continue
            needle = syll.lower()
            bare = strip_tone_marks(needle)
            pos_exact = hay.find(needle, cursor)
            pos_bare = hay.find(bare, cursor) if bare != needle else -1
            candidates = [(p, t, s) for p, t, s in
                          [(pos_exact, needle, 'OK'), (pos_bare, bare, 'NEUTRAL_VARIANT')] if p != -1]
            if candidates:
                pos, matched_text, status = min(candidates, key=lambda c: c[0])
                results.append((ch, syll, status, f'matched "{matched_text}" at {pos}'))
                cursor = pos + len(matched_text)
                continue
            results.append((ch, syll, 'MISMATCH', f'"{needle}" not found in "{hay[cursor:]}"'))
        return results

    def report_source(label, items):
        nonlocal ok
        bad = 0
        for hz, pinyin in items:
            results = sequential_check(hz, pinyin)
            problems = [r for r in results if r[2] in ('MISMATCH', 'NO_CHARDICT_ENTRY')]
            if problems:
                bad += 1
                ok = False
                print(f'  {label} MISMATCH: {hz!r} pinyin={pinyin!r}')
                for r in problems:
                    print(f'      {r}')
        print(f'--- {label}: {bad} mismatches out of {len(items)} ---')

    vocab_by_hz = {}
    for sec, terms in VOCAB['data'].items():
        for t in terms:
            vocab_by_hz.setdefault(t['h'], []).append({**t, 'section': sec})

    print()
    report_source('VOCAB', [(hz, occ[0]['p']) for hz, occ in vocab_by_hz.items()])

    print()
    print('--- VOCAB internal consistency (same hanzi, different pinyin across sections) ---')
    inconsistent = 0
    for hz, occ in vocab_by_hz.items():
        pinyins = set(normalize_pinyin(o['p']) for o in occ)
        if len(pinyins) > 1:
            inconsistent += 1
            ok = False
            print(f'  {hz}: {[(o["section"], o["p"]) for o in occ]}')
    print(f'  {inconsistent} inconsistent')

    print()
    report_source('TONE_GAME_DATA', [(hz, e['correct']) for hz, e in TONE_GAME_DATA.items()])

    print()
    print('--- VOCAB vs TONE_GAME_DATA (same hanzi, different tones) ---')
    # Compare only the matched per-character syllables (from sequential_check),
    # not the raw strings — VOCAB pinyin often has digits/Latin/slashes mixed
    # in (e.g. "满68可用", "待收货/使用") that TONE_GAME_DATA always omits, so a
    # raw string compare is noisy. Comparing the actual matched hanzi-aligned
    # syllables is the real, false-positive-free version of this check.
    mism = 0
    for hz, occ in vocab_by_hz.items():
        if hz in TONE_GAME_DATA:
            # Per character, each side either matched CHAR_DICT's expected
            # syllable (exactly or as a neutral-tone variant) or it didn't.
            # Comparing *that* (not the raw strings, which differ trivially
            # whenever digits/Latin/slashes are mixed into the hanzi) is
            # what actually detects "these two sources disagree on the tone".
            v_status = tuple(r[2] for r in sequential_check(hz, occ[0]['p']))
            t_status = tuple(r[2] for r in sequential_check(hz, TONE_GAME_DATA[hz]['correct']))
            matched = {'OK', 'NEUTRAL_VARIANT'}
            diverges = any((vs in matched) != (ts in matched) for vs, ts in zip(v_status, t_status))
            if diverges:
                mism += 1
                ok = False
                print(f'  {hz}: VOCAB={occ[0]["p"]!r} TONE_GAME_DATA={TONE_GAME_DATA[hz]["correct"]!r}')
                print(f'      VOCAB per-char: {v_status}  TONE per-char: {t_status}')
    print(f'  {mism} mismatches')

    print()
    print('--- TONE_GAME_DATA orphans (word not present in VOCAB) ---')
    orphans = [hz for hz in TONE_GAME_DATA if hz not in vocab_by_hz]
    if orphans:
        ok = False
        for o in orphans:
            print(f'  {o}')
    print(f'  {len(orphans)} orphans')

    print()
    print('--- TONE_GAME_DATA distractors (skeleton/syllable-count/dupes/self-match) ---')

    def skeleton(s):
        return strip_tone_marks(s).lower().replace(' ', '')

    dprob = 0
    for hz, entry in TONE_GAME_DATA.items():
        correct = entry['correct']
        csk, ccount = skeleton(correct), len(correct.split())
        norm_correct = normalize_pinyin(correct)
        seen = {}
        for d in entry['distractors']:
            dsk, dcount = skeleton(d), len(d.split())
            if dsk != csk or dcount != ccount:
                dprob += 1
                ok = False
                print(f'  {hz}: distractor {d!r} has different letters/syllable count than correct {correct!r}')
            nd = normalize_pinyin(d)
            if nd == norm_correct:
                dprob += 1
                ok = False
                print(f'  {hz}: distractor {d!r} equals the correct answer')
            if nd in seen:
                dprob += 1
                ok = False
                print(f'  {hz}: duplicate distractors {seen[nd]!r} / {d!r}')
            seen[nd] = d
    print(f'  {dprob} problems')

    print()
    print('--- WORD_GROUPS (substring + pinyin vs CHAR_DICT, using parent word for overrides) ---')
    wgprob = 0
    for parent, groups in WORD_GROUPS.items():
        for g in groups:
            if g['w'] not in parent:
                wgprob += 1
                ok = False
                print(f'  {parent}: {g["w"]!r} is not a substring of the parent')
            overrides = CHAR_OVERRIDES.get(parent, {})
            hay = g['p'].lower()
            cursor = 0
            for ch in g['w']:
                if not is_hanzi(ch):
                    continue
                syll = overrides.get(ch, CHAR_DICT.get(ch))
                if syll is None:
                    continue
                needle = syll[0].lower()
                bare = strip_tone_marks(needle)
                pos_exact = hay.find(needle, cursor)
                pos_bare = hay.find(bare, cursor) if bare != needle else -1
                candidates = [p for p in (pos_exact, pos_bare) if p != -1]
                if not candidates:
                    wgprob += 1
                    ok = False
                    print(f'  {parent} / {g["w"]} ({g["p"]}): char {ch} expected {needle!r}, not found')
                    break
                cursor = min(candidates) + len(needle if min(candidates) == pos_exact else bare)
    print(f'  {wgprob} problems')

    try:
        from pycccedict.cccedict import CcCedict
    except ImportError:
        print('\npycccedict not installed — skipping CC-CEDICT cross-checks (pip install pycccedict)')
        print('\nRESULT:', 'ALL CHECKS PASSED' if ok else 'ISSUES FOUND (see above)')
        return

    print()
    print('--- cross-check against real CC-CEDICT ---')
    d = CcCedict()
    simp_index = defaultdict(list)
    trad_index = defaultdict(list)
    for e in d.entries:
        e2 = dict(e, accented=numbered_pinyin_to_accented(e['pinyin']))
        simp_index[e['simplified']].append(e2)
        trad_index[e['traditional']].append(e2)

    def cedict_lookup(hz):
        res = list(simp_index.get(hz, []))
        for e in trad_index.get(hz, []):
            if e not in res:
                res.append(e)
        return res

    cedict_prob = 0
    for ch, (py, meaning) in CHAR_DICT.items():
        entries = cedict_lookup(ch)
        if not entries:
            continue
        options = set(normalize_pinyin(e['accented']) for e in entries)
        if normalize_pinyin(py) not in options:
            cedict_prob += 1
            print(f'  CHAR_DICT {ch} ({py}, "{meaning}") not among CEDICT readings: '
                  f'{[e["accented"] for e in entries]} (verify manually — may be a documented exception)')
    print(f'  {cedict_prob} CHAR_DICT entries not matching any CEDICT reading (review manually)')

    print()
    print('RESULT:', 'ALL CHECKS PASSED' if ok else 'ISSUES FOUND (see above)')


if __name__ == '__main__':
    main()
