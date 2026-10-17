"""Build FarmHub navigation assets from the pinned local d2r-advanced reference."""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / '.reference-d2r-advanced'
SOURCE = REFERENCE / 'mods/D2rAdvanced/D2rAdvanced.mpq'
TARGET = ROOT / 'mods/FarmHub/FarmHub.mpq'
OUTPUTS = set()


def write(relative, value):
    path = TARGET / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    OUTPUTS.add(relative)


def copy_asset(relative):
    path = SOURCE / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    destination = TARGET / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, destination)
    OUTPUTS.add(relative)


tiles = [
    'act_3_mephisto_down_l', 'act_3_mephisto_down_r',
    'act_5_baal_temple_down_l', 'act_5_baal_temple_down_r',
    'act_5_temple_down', 'act_1_catacombs_down',
    'act_1_crypt_down',
]
beam = 'data/hd/vfx/particles/overlays/object/horadric_light/fx_horadric_light.particles'
prefab = 'data/hd/env/porory/beacon/pf_beacon_downstairs.json'
for tile in tiles:
    relative = f'data/hd/roomtiles/{tile}.json'
    value = json.loads((SOURCE / relative).read_text(encoding='utf-8-sig'))
    original_vfx = next(e for e in value['entities'] if e['name'] == 'entity_vfx1')
    light = copy.deepcopy(original_vfx)
    light['name'] = 'FarmHubEntranceBeam'
    light['id'] = 3900000001
    next(c for c in light['components'] if c['type'] == 'VfxDefinitionComponent')['filename'] = beam
    value['entities'].append(light)
    beacon = next((e for e in value['entities'] if any(c['type'] == 'PrefabPlacementDefinitionComponent' for c in e['components'])), None)
    if beacon is None:
        template = json.loads((SOURCE / 'data/hd/roomtiles/act_5_temple_down.json').read_text())
        beacon = copy.deepcopy(template['entities'][-1])
        value['entities'].append(beacon)
    next(c for c in beacon['components'] if c['type'] == 'PrefabPlacementDefinitionComponent')['prefab'] = prefab
    value['dependencies']['particles'].append({'path': beam})
    value['dependencies']['json'].append({'path': prefab})
    write(relative, value)

# Keep the established beacon dimensions and placement until in-game QA.
value = json.loads(re.sub(r'(?m)^\s*//[^\n]*', '', (SOURCE / prefab).read_text()))
for i, entity in enumerate(value['entities']):
    entity['id'] = 3900000100 + i
texture = 'data/hd/env/porory/beacon/texture/beacon_c03_s07_o100.texture'
value['dependencies']['textures'].append({'path': texture})
write(prefab, value)
# D2R texture references can resolve to separate alpha and RGB resources.
for path in (SOURCE / texture).parent.glob('beacon_c03_s07_o100*.texture'):
    copy_asset(path.relative_to(SOURCE).as_posix())

directions = {'n': '0045', 'e': '0315', 's': '0225', 'w': '0135'}
for direction, angle in directions.items():
    relative = f'data/hd/env/preset/expansion/wildtemple/nihl{direction}.json'
    value = json.loads((SOURCE / relative).read_text())
    used_ids = {e['id'] for e in value['entities'] if 'directionarrows' not in json.dumps(e)}
    arrows = [e for e in value['entities'] if 'directionarrows' in json.dumps(e)]
    assert len(arrows) == 11
    particle = f'data/hd/directionarrows/particles/directionarrows_{angle}.particles'
    for i, entity in enumerate(arrows):
        entity['name'] = f'FarmHubNihlathakArrow{i:02}'
        entity['id'] = 3900000200 + i
        assert entity['id'] not in used_ids
    value['dependencies']['particles'].append({'path': particle})
    write(relative, value)
    copy_asset(particle)
    # Include custom texture references even if they are unused compiled material slots.
    refs = set(re.findall(rb'data/[A-Za-z0-9_./$-]+\.texture', (SOURCE / particle).read_bytes()))
    for ref in refs:
        relative_texture = ref.decode()
        if relative_texture.startswith(('data/hd/directionarrows/', 'data/hd/nickname/')):
            candidates = list((SOURCE / relative_texture).parent.glob(Path(relative_texture).stem + '*.texture'))
            if not candidates:
                # Reference contains stale, unused nickname material slots. Supply
                # a valid fallback texture without altering the binary particle format.
                fallback = SOURCE / 'data/hd/directionarrows/textures/directionarrows_0045.texture'
                destination = TARGET / relative_texture
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(fallback, destination)
                OUTPUTS.add(relative_texture)
                continue
            for candidate in candidates:
                copy_asset(candidate.relative_to(SOURCE).as_posix())

commit = subprocess.check_output(['git', '-C', str(REFERENCE), 'rev-parse', 'HEAD'], text=True).strip()
manifest = {
    'version': '1.3.1',
    'reference': 'https://github.com/lukezord/d2r-advanced',
    'referenceCommit': commit,
    'directionAngles': directions,
    'entranceTiles': tiles,
    'removedFiles': ['data/hd/roomtiles/act_3_travincal_to_mephisto.json'],
    'files': {p: hashlib.sha256((TARGET / p).read_bytes()).hexdigest() for p in sorted(OUTPUTS)},
}
(ROOT / 'navigation-assets.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(f'Built {len(OUTPUTS)} navigation assets from {commit}.')
