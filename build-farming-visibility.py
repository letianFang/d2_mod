"""Build minimal corpse/panel overrides from the local CN build 93854."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / '.original-build-93854'
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    state_path = 'data/global/excel/states.txt'
    original = (BASE / state_path).read_bytes()
    # Keep every original byte except the one selected TSV cell.
    lines = original.decode('utf-8-sig').splitlines(keepends=True)
    columns = lines[0].rstrip('\r\n').split('\t')
    state_col, hide_col = columns.index('state'), columns.index('hide')
    changed = 0
    for index, line in enumerate(lines[1:], 1):
        ending = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
        cells = line.rstrip('\r\n').split('\t')
        if cells[state_col] == 'corpse_noselect':
            assert cells[columns.index('*ID')] == '118'
            assert cells[hide_col] == ''
            cells[hide_col] = '1'
            lines[index] = '\t'.join(cells) + ending
            changed += 1
    assert changed == 1
    states = ''.join(lines).encode('utf-8')
    assert not original.startswith(b'\xef\xbb\xbf')
    (MOD / state_path).write_bytes(states)

    panel_path = 'data/global/ui/layouts/panelborderspanelhd.json'
    panel_original = (BASE / panel_path).read_bytes()
    # Preserve anchor widgets because BordersPanel may address them by name.
    # Remove both the decorative images and their invisible click catchers.
    panel = {
        'type': 'BordersPanel', 'name': 'PanelBordersPanel',
        'fields': {'fitToParent': True, 'priority': -1},
        'children': [
            {'type': 'Panel', 'name': 'LeftAnchor',
             'fields': {'anchor': {'x': 0.0}}, 'children': []},
            {'type': 'Panel', 'name': 'RightAnchor',
             'fields': {'anchor': {'x': 1.0}}, 'children': []},
        ],
    }
    (MOD / panel_path).write_text(json.dumps(panel, indent=4) + '\n', encoding='utf-8')
    manifest = {
        'build': '93854',
        'launchArguments': '-mod FarmHub -txt -assettestmode 1',
        'corpseScope': 'all areas; used corpses only',
        'stateChange': {'state': 'corpse_noselect', 'id': 118, 'column': 'hide', 'before': '', 'after': '1'},
        'originalSha256': {state_path: sha(original), panel_path: sha(panel_original)},
        'files': {name: sha((MOD / name).read_bytes()) for name in (state_path, panel_path)},
        'runtimeVerification': 'confirmed by user 2026-10-30',
        'parameterReference': 'https://github.com/jcymeow/jcy#使用',
    }
    (ROOT / 'farming-visibility-assets.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Built used-corpse visibility and borderless mouse/keyboard panels for CN 93854.')


if __name__ == '__main__':
    build()
