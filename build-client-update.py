"""Apply the audited CN 95039 update using extracted current client originals.

37 original resources were compared against CN 93854. Only the version marker,
seven Spanish strings, and councilmember1 texture dependencies changed. The
council model is not overridden by FarmHub. All other existing features retain
their audited assets; the Chinese name labels are rebuilt on the new strings.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    manifest_path = ROOT / 'client-update-assets.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    baseline = ROOT / manifest['baseline']
    for relative, expected in manifest['originalSha256'].items():
        assert sha((baseline / relative).read_bytes()) == expected, relative
    changed = {p for p, h in manifest['originalSha256'].items()
               if h != manifest['previousClientSha256'][p]}
    assert changed == set(manifest['changedClientFiles'])
    assert not (MOD / 'data/hd/character/enemy/councilmember1.json').exists()
    version = (baseline / 'data/global/DataVersionBuild.txt').read_bytes()
    assert version == b'95039'
    subprocess.run([sys.executable, str(ROOT / 'build-item-labels.py')], check=True)
    (MOD / 'data/global/DataVersionBuild.txt').write_bytes(version)
    # Source overrides unrelated to this update must retain their previous bytes.
    previous = manifest['previousCommit']
    for file in MOD.rglob('*'):
        if not file.is_file():
            continue
        relative = file.relative_to(MOD).as_posix()
        if relative in ('data/global/DataVersionBuild.txt', 'data/local/lng/strings/item-names.json'):
            continue
        old = subprocess.check_output(['git', 'show', f'{previous}:mods/FarmHub/FarmHub.mpq/{relative}'], cwd=ROOT)
        assert file.read_bytes() == old, f'Unexpected unrelated override change: {relative}'
    manifest['files'] = {p.relative_to(MOD).as_posix(): sha(p.read_bytes())
                         for p in sorted(MOD.rglob('*')) if p.is_file()}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Audited 37 client originals and preserved all unrelated overrides for CN 95039.')


if __name__ == '__main__':
    build()
