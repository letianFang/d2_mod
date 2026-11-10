"""Port MDM3C Skill/HP icons onto extracted build 95039 overlays (stdlib only)."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / '.original-build-95039'
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'
SOURCE_HASHES = {
    'data/hd/overlays/common/battlecommand.json': '0f14e94e4209cfc34494fa72bdd757e6a7559165705e184e659d9167bf87edc1',
    'data/hd/overlays/common/battleorders.json': '3f322dc22bb7267fa9878eab77984005c28456603baf568c0029c2b513fb5a39',
    'data/hd/directionarrows/particles/buff_skill.particles': '23ffe0591ee8493170ad777b968a0d727fa907f83464c2b446e35f4f4c00adc2',
    'data/hd/directionarrows/particles/buff_hp.particles': '432225fb7b1aab797c51c45347626b0aa7910c2f1943f06e2171d3385556b22c',
    'data/hd/directionarrows/textures/buff_skillup_0000000.texture': '3267049777be210082931625f0c03afab6cae18876d025bf4dd0597820fbdacb',
    'data/hd/directionarrows/textures/buff_hpup_0000000000.texture': '6c6c3037b0cac336db2418d3d0bd5234337ae896552c7fa2146e0eeba1a2f1d4',
}
LABELS = {
    'battlecommand': ('Skill ↑', 'buff_skill', 'buff_skillup_0000000'),
    'battleorders': ('HP ↑', 'buff_hp', 'buff_hpup_0000000000'),
}
REMOVED = [f'data/hd/directionarrows/{folder}/{stem}.{extension}'
           for folder, extension in [('particles', 'particles'), ('textures', 'texture')]
           for stem in ['farmhub_bc_skilltext', 'farmhub_bo_life_text']]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(value):
    return json.dumps(value, separators=(',', ':')).encode('utf-8')


def build(source_root):
    sources = {p.relative_to(source_root).as_posix().lower(): p.read_bytes()
               for p in source_root.rglob('*') if p.is_file()
               and p.relative_to(source_root).as_posix().lower() in SOURCE_HASHES}
    for path, expected in SOURCE_HASHES.items():
        assert path in sources, f'Missing MDM3C source: {path}'
        assert sha(sources[path]) == expected, f'MDM3C source changed: {path}'
    outputs = {p: data for p, data in sources.items() if not p.endswith('.json')}
    originals, labels = {}, {}
    for state, (text, particle_stem, texture_stem) in LABELS.items():
        path = f'data/hd/overlays/common/{state}.json'
        original = (BASE / path).read_bytes()
        vanilla, source = json.loads(original), json.loads(sources[path])
        assert vanilla['type'] == source['type'] == 'OverlayDefinition'
        assert vanilla['name'] == source['name'] == state
        assert vanilla['dependencies'] == source['dependencies']
        assert len(vanilla['entities']) == len(source['entities']) == 1
        particle = f'data/hd/directionarrows/particles/{particle_stem}.particles'
        texture = f'data/hd/directionarrows/textures/{texture_stem}.texture'
        components = source['entities'][0]['components']
        vfx, transform = components
        assert vfx['type'] == 'VfxDefinitionComponent'
        assert vfx['filename'] == particle and vfx['hardKillOnDestroy'] is True
        assert transform['type'] == 'TransformDefinitionComponent'
        assert transform['position'] == {'x': 122, 'y': 95, 'z': 116}
        assert transform['scale'] == {'x': 1.0, 'y': 1.0, 'z': 1.0}
        assert transform['inheritOnlyPosition'] is True
        # Other texture strings are unused editor metadata, as in the existing
        # direction arrows. This is the particle's only active sampler.
        assert sources[particle].count(b'__sampler_0=' + texture.encode()) == 1
        assert sources[particle].count(b'__sampler_') == 1
        old_components = compact(vanilla['entities'][0]['components'])
        assert original.count(old_components) == 1
        output = original.replace(old_components, compact(components))
        dependency = compact(vanilla['dependencies']['particles'])
        assert output.count(dependency) == 1
        new_dependency = compact([{'path': particle}])
        output = output.replace(dependency, new_dependency)
        textures = vanilla['dependencies']['textures']
        old_textures = compact(textures)
        new_textures = textures + [{'path': texture}]
        assert output.count(old_textures) == 1
        output = output.replace(old_textures, compact(new_textures))
        expected = copy.deepcopy(vanilla)
        expected['entities'][0]['components'] = components
        expected['dependencies']['particles'] = [{'path': particle}]
        expected['dependencies']['textures'] = new_textures
        assert json.loads(output) == expected
        # Retain all unrelated original bytes and the current client's entity ID.
        restored = output.replace(compact(components), old_components)
        restored = restored.replace(new_dependency, dependency)
        restored = restored.replace(compact(new_textures), old_textures)
        assert restored == original
        outputs[path], originals[path] = output, sha(original)
        labels[state] = {'text': text, 'overlay': path, 'particle': particle,
                         'texture': texture, 'transform': transform}
    for relative, data in outputs.items():
        target = MOD / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for relative in REMOVED:
        (MOD / relative).unlink(missing_ok=True)
    manifest = {
        'build': '95039', 'source': 'MDM3C.7z (author 暗黑2阿檬), local copy',
        'sourceSha256': SOURCE_HASHES, 'originalSha256': originals,
        'labels': labels, 'tablesChanged': [], 'removedFiles': REMOVED,
        'files': {p: sha(data) for p, data in sorted(outputs.items())},
        'runtimeVerification': 'pending',
    }
    (ROOT / 'buff-labels-assets.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print('Ported MDM3C Skill/HP icons; original particles, textures and transforms retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    build(parser.parse_args().source_root)
