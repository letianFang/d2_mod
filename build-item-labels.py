"""Add tier and useful socket counts to weapon and armor base names.

Display only: the base-name strings in item-names.json get a suffix such as
"[精华] 4孔". The base name is what the game shows on the ground, before and
after identification, for every quality. No item table is changed.

Two steps:

    python build-item-labels.py rules <d2data json/base directory>
        Writes item-label-rules.json from armor/weapons/itemtypes/runes data
        (blizzhackers/d2data, whose tables match CN build 93854).

    python build-item-labels.py
        Reads the client's original strings from
        .original-build-93854/data/local/lng/strings/item-names.json and writes
        the labelled copy into the mod.

Tier comes from normcode/ubercode/ultracode. "Useful" socket counts are the
rune counts of the runewords in POPULAR_RUNEWORDS that the base can take: its
item type (with parents) matches an itype and no etype, and the count is no
more than min(gemsockets, item type MaxSockets3).
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / '.original-build-93854'
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'
STRINGS = 'data/local/lng/strings/item-names.json'
RULES = ROOT / 'item-label-rules.json'
LANGUAGE = 'zhCN'
TIERS = {'normcode': '普通', 'ubercode': '扩展', 'ultracode': '精华'}

# Edit this list to change which socket counts count as useful, then rerun both steps.
POPULAR_RUNEWORDS = [
    # weapons
    'Spirit', 'Insight', 'Infinity', 'Call to Arms', 'Grief', 'Breath of the Dying', 'Last Wish',
    'Beast', 'Doom', 'Heart of the Oak', 'Faith', 'Fortitude', 'Pride', 'Obedience',
    'Hand of Justice', 'Death', 'Destruction', 'Eternity', 'Silence', 'Phoenix', 'Crescent Moon',
    'Oath', 'Kingslayer', 'Lawbringer', 'Memory', 'White', 'Mosaic',
    # armor
    'Enigma', 'Chains of Honor', 'Treachery', 'Smoke', 'Stealth', 'Duress', 'Bramble', 'Bone',
    'Lionheart',
    # shields
    'Exile', 'Dream', 'Sanctuary', "Ancients' Pledge", 'Rhyme',
    # helms
    'Lore', 'Delirium',
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build_rules(source):
    source = Path(source)
    load = lambda name: json.loads((source / f'{name}.json').read_text(encoding='utf-8'))
    itemtypes, runes = load('itemtypes'), load('runes')
    bases = list(load('armor').values()) + list(load('weapons').values())

    def ancestors(code, seen):
        if code and code in itemtypes and code not in seen:
            seen.add(code)
            for key in ('Equiv1', 'Equiv2'):
                ancestors(itemtypes[code].get(key), seen)
        return seen

    words = []
    for row in runes.values():
        name = row.get('*Rune Name')
        if row.get('complete') != 1 or name not in POPULAR_RUNEWORDS:
            continue
        count = sum(1 for i in range(1, 7) if row.get(f'Rune{i}'))
        allowed = {row.get(f'itype{i}') for i in range(1, 7)} - {None}
        excluded = {row.get(f'etype{i}') for i in range(1, 4)} - {None}
        words.append((name, count, allowed, excluded))
    missing = set(POPULAR_RUNEWORDS) - {w[0] for w in words}
    assert not missing, f'unknown or incomplete runewords: {sorted(missing)}'

    rules = {}
    for item in bases:
        key = item.get('namestr')
        tier = next((label for column, label in TIERS.items() if item.get(column) == item['code']), None)
        if not key or tier is None:
            continue
        types = ancestors(item['type'], set()) | ancestors(item.get('type2'), set())
        limit = min(item.get('gemsockets') or 0, itemtypes[item['type']].get('MaxSockets3') or 0)
        sockets = {}
        for name, count, allowed, excluded in words:
            if count <= limit and types & allowed and not types & excluded:
                sockets.setdefault(count, []).append(name)
        rule = {'code': item['code'], 'tier': tier,
                'sockets': {str(n): sorted(v) for n, v in sorted(sockets.items())}}
        if key in rules and (rules[key]['tier'], rules[key]['sockets']) != (rule['tier'], rule['sockets']):
            raise ValueError(f'string key {key} is shared by bases with different labels')
        rules[key] = rule
    RULES.write_text(json.dumps({
        'source': 'https://github.com/blizzhackers/d2data json/base (armor, weapons, itemtypes, runes)',
        'popularRunewords': POPULAR_RUNEWORDS,
        'rules': dict(sorted(rules.items())),
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Wrote {len(rules)} base rules to {RULES.name}.')


def label(rule):
    text = f"[{rule['tier']}]"
    if rule['sockets']:
        text += ' ' + '/'.join(rule['sockets']) + '孔'
    return text


def build_strings():
    source = BASE / STRINGS
    if not source.is_file():
        sys.exit(f'Extract {STRINGS} from the CN 93854 client into {BASE.name}/ first.')
    original = source.read_bytes()
    bom = original.startswith(b'\xef\xbb\xbf')
    entries = json.loads(original.decode('utf-8-sig'))
    rules = json.loads(RULES.read_text(encoding='utf-8'))['rules']
    found = set()
    for entry in entries:
        rule = rules.get(entry.get('Key'))
        if rule is None:
            continue
        name = entry[LANGUAGE]
        assert '[' not in name, f"already labelled: {entry['Key']}"
        entry[LANGUAGE] = f'{name} {label(rule)}'
        found.add(entry['Key'])
    missing = sorted(set(rules) - found)
    assert not missing, f'base names missing from item-names.json: {missing}'
    data = json.dumps(entries, indent=2, ensure_ascii=False) + '\n'
    data = (b'\xef\xbb\xbf' if bom else b'') + data.encode('utf-8')
    target = MOD / STRINGS
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest = {
        'build': '93854',
        'language': LANGUAGE,
        'labelledBases': len(found),
        'rules': sha(RULES.read_bytes()),
        'originalSha256': {STRINGS: sha(original)},
        'files': {STRINGS: sha(data)},
        'runtimeVerification': 'pending',
    }
    (ROOT / 'item-labels-assets.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Labelled {len(found)} base names in {STRINGS}.')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'rules':
        build_rules(sys.argv[2])
    else:
        build_strings()
