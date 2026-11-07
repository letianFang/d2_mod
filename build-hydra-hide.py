"""Hide hydras and their fire bolts in HD. Display only.

Monster behavior and damage are untouched: no data table is changed. The
hydras still spawn and still hit; they are just not drawn in HD.

* data/hd/missiles/missiles.json maps the `hydra` missile to the shared
  `firebolt` model. Only that one entry becomes "null", the value vanilla uses
  for invisible missiles (88 entries already). Fire Bolt, skeleton mages and
  traps keep `firebolt`.
* data/hd/character/enemy/hydra1-3.json keep only `entity_root` (unit root,
  skeleton, variant, preload, transform). The body model, the four to six
  attached fire particles and the ground decal entities are removed, so
  nothing of the hydra is drawn. The dependency (preload) lists stay as they
  are, since the state machine may still refer to them.

The hit flash (`fireexplode`, shared with Fire Bolt and Fire Arrow) is left
alone. hydra1-3 are also the Sorceress's Hydra summons, so those disappear in
HD too.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / '.original-build-93854'
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'
MISSILES = 'data/hd/missiles/missiles.json'
HYDRAS = [f'data/hd/character/enemy/hydra{i}.json' for i in (1, 2, 3)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(relative):
    raw = (BASE / relative).read_bytes()
    value = json.loads(raw.decode('utf-8-sig'))
    # The client files are compact JSON; prove the writer reproduces them exactly.
    assert dump(value, raw) == raw, f'cannot reproduce original formatting: {relative}'
    return raw, value


def dump(value, original):
    text = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    prefix = b'\xef\xbb\xbf' if original.startswith(b'\xef\xbb\xbf') else b''
    return prefix + text.encode('utf-8')


def write(relative, data):
    path = MOD / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def build():
    originals, files = {}, {}

    raw, missiles = load(MISSILES)
    assert missiles['hydra'] == 'firebolt'
    missiles['hydra'] = 'null'
    files[MISSILES] = dump(missiles, raw)
    originals[MISSILES] = raw

    removed = {}
    for relative in HYDRAS:
        raw, unit = load(relative)
        root = [e for e in unit['entities'] if e['name'] == 'entity_root']
        assert len(root) == 1
        removed[relative] = [e['name'] for e in unit['entities'] if e['name'] != 'entity_root']
        assert 'entity_torso' in removed[relative]
        unit['entities'] = root
        files[relative] = dump(unit, raw)
        originals[relative] = raw

    for relative, data in files.items():
        write(relative, data)
    manifest = {
        'build': '93854',
        'missile': {'hydra': {'before': 'firebolt', 'after': 'null'}},
        'removedEntities': removed,
        'notHidden': 'fireexplode hit flash (shared with Fire Bolt and Fire Arrow)',
        'tablesChanged': [],
        'originalSha256': {k: sha(v) for k, v in originals.items()},
        'files': {k: sha(v) for k, v in files.items()},
        'runtimeVerification': 'pending',
    }
    (ROOT / 'hydra-hide-assets.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Hid hydras and their fire bolts in HD.')


if __name__ == '__main__':
    build()
