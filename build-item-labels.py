"""Add the tier (普/扩/精) to weapon and armor base names.

Display only: the base-name strings in item-names.json get a suffix such as
"[精]". The base name is what the game shows on the ground, before and after
identification, for every quality. No item table is changed.

Two steps:

    python build-item-labels.py rules <d2data json/base directory>
        Writes item-label-rules.json from the armor and weapons data of
        blizzhackers/d2data, whose tables match CN build 93854.

    python build-item-labels.py
        Reads the client's original strings from
        .original-build-93854/data/local/lng/strings/item-names.json and writes
        the labelled copy into the mod.

The tier is the column of normcode/ubercode/ultracode that equals the base's
own code.
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
TIERS = {'normcode': '普', 'ubercode': '扩', 'ultracode': '精'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build_rules(source):
    source = Path(source)
    bases = []
    for table in ('armor', 'weapons'):
        bases += json.loads((source / f'{table}.json').read_text(encoding='utf-8')).values()
    rules = {}
    for item in bases:
        key = item.get('namestr')
        tier = next((label for column, label in TIERS.items() if item.get(column) == item['code']), None)
        if not key or tier is None:
            continue
        if rules.get(key, tier) != tier:
            raise ValueError(f'string key {key} is shared by bases of different tiers')
        rules[key] = tier
    RULES.write_text(json.dumps({
        'source': 'https://github.com/blizzhackers/d2data json/base (armor, weapons)',
        'tiers': dict(sorted(rules.items())),
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Wrote {len(rules)} base tiers to {RULES.name}.')


def build_strings():
    source = BASE / STRINGS
    if not source.is_file():
        sys.exit(f'Extract {STRINGS} from the CN 93854 client into {BASE.name}/ first.')
    original = source.read_bytes()
    bom = original.startswith(b'\xef\xbb\xbf')
    entries = json.loads(original.decode('utf-8-sig'))
    tiers = json.loads(RULES.read_text(encoding='utf-8'))['tiers']
    found = set()
    for entry in entries:
        tier = tiers.get(entry.get('Key'))
        if tier is None:
            continue
        name = entry[LANGUAGE]
        assert '[' not in name, f"already labelled: {entry['Key']}"
        entry[LANGUAGE] = f'{name} [{tier}]'
        found.add(entry['Key'])
    missing = sorted(set(tiers) - found)
    assert not missing, f'base names missing from item-names.json: {missing}'
    data = json.dumps(entries, indent=2, ensure_ascii=False) + '\n'
    if b'\r\n' in original:
        data = data.replace('\n', '\r\n')
    data = (b'\xef\xbb\xbf' if bom else b'') + data.encode('utf-8')
    target = MOD / STRINGS
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest = {
        'build': '93854',
        'language': LANGUAGE,
        'labels': list(TIERS.values()),
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
