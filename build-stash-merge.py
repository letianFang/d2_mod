"""Build the merged rune/gem/material stash tab from a local MDM mod copy (CN build 93854)."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / '.reference-mdm/MDM.mpq'
TARGET = ROOT / 'mods/FarmHub/FarmHub.mpq'
TAB_LABEL = '材料'
TRANSMUTE_INTERVAL = 0.9  # The looping timer adds up to 0.1s, giving about one transmute per second.
LAYOUT = 'data/global/ui/layouts/bankexpansionlayouthd.json'
TIMER_START = 'data/global/ui/layouts/CALL/mymodConvertAutoStarthd.json'
TIMER_STEP = 'data/global/ui/layouts/CALL/mymodConverthd.json'
BACKGROUNDS = [
    'data/hd/global/ui/panel/stash/additionalstash/panel_bg_craft.sprite',
    'data/hd/global/ui/panel/stash/additionalstash/panel_bg_craft.lowend.sprite',
]
# MDM draws these five frames on a single row; its widget offsets overlap by 8px.
ALIGNED_SLOTS = {'ua1': 330, 'ua2': 430, 'ua3': 530, 'ua4': 630, 'ua5': 730}
# Earlier Horadric Stash resources: they resize the panel and must not survive an upgrade.
RETIRED = [
    'data/global/ui/layouts/bankoriginallayouthd.json',
] + [
    f'data/hd/global/ui/panel/stash/{name}{suffix}'
    for name in ('stashpanel_bg_personal', 'stashpanel_bg_shared', 'stash_rightarrow',
                 'additionalstash/panel_additionalstash_gems', 'additionalstash/stashnotification')
    for suffix in ('.sprite', '.lowend.sprite')
]


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def source_path(relative):
    """MDM mixes path case, so resolve each part without relying on the host filesystem."""
    path = SOURCE
    for part in Path(relative).parts:
        match = [child for child in path.iterdir() if child.name.lower() == part.lower()]
        assert len(match) == 1, (path, part)
        path = match[0]
    return path


def load_jsonc(data):
    text = re.sub(r'//[^\n]*', '', data.decode('utf-8-sig'))
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', text))


def find_widget(node, name):
    if node.get('name') == name:
        return node
    for child in node.get('children', []):
        found = find_widget(child, name)
        if found:
            return found
    return None


def stackable_codes():
    with open(TARGET / 'data/global/excel/misc.txt', encoding='utf-8', newline='') as table:
        return {row['code'] for row in csv.DictReader(table, delimiter='\t')
                if row['AdvancedStashStackable'] == '1'}


def build_layout(layout):
    find_widget(layout, 'BankTabs')['fields']['textStrings'][2] = TAB_LABEL

    # Keep MDM's merged page and auto-transmute; drop its unrelated gold and page-arrow extras.
    for name in ('basicstash_container', 'SharedStashTabContainer', 'StashNavigation'):
        container = find_widget(layout, name)
        container['children'] = [
            child for child in container['children']
            if not child['name'].startswith(('custom_', 'StashTab'))
        ]

    # MDM repeats r07/r08 under the cube for its own recipes, without a background frame.
    gems = find_widget(layout, 'advancedstash_gems')
    slots, seen = [], set()
    for slot in gems['children']:
        code = slot['fields']['itemCode']
        if code not in seen:
            seen.add(code)
            if code in ALIGNED_SLOTS:
                slot['fields']['rect']['x'] = ALIGNED_SLOTS[code]
            slots.append(slot)
    gems['children'] = slots
    assert seen == stackable_codes()
    assert not find_widget(layout, 'advancedstash_materials')['children']
    assert not find_widget(layout, 'advancedstash_runes')['children']

    # The game may look this widget up by name, so park it off-screen instead of deleting it.
    find_widget(layout, 'withdraw_button')['fields']['rect']['x'] = -10000
    find_widget(layout, 'auto_convert_toggle')['fields']['tooltipString'] = '自动重塑：勾选后约每秒执行一次重塑，取消勾选后停止'
    return len(slots)


def write_json(relative, value):
    path = TARGET / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=4) + '\n', encoding='utf-8')


def build():
    originals = {name: source_path(name).read_bytes() for name in [LAYOUT, TIMER_START, TIMER_STEP] + BACKGROUNDS}

    layout = load_jsonc(originals[LAYOUT])
    slot_count = build_layout(layout)
    write_json(LAYOUT, layout)

    write_json(TIMER_START, load_jsonc(originals[TIMER_START]))
    step = load_jsonc(originals[TIMER_STEP])
    for timer in step['children']:
        timer['fields']['time'] = TRANSMUTE_INTERVAL
    write_json(TIMER_STEP, step)

    for name in BACKGROUNDS:
        destination = TARGET / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(originals[name])
    for name in RETIRED:
        (TARGET / name).unlink(missing_ok=True)

    manifest = {
        'version': '1.5.0',
        'build': '93854',
        'source': 'MDM mod (author 暗黑2阿檬), local copy; no license file found',
        'tabLabel': TAB_LABEL,
        'slotCount': slot_count,
        'transmuteIntervalSeconds': TRANSMUTE_INTERVAL,
        'runtimeVerification': 'confirmed by user 2026-10-30',
        'removedFiles': RETIRED,
        'originalSha256': {name: sha(data) for name, data in sorted(originals.items())},
        'files': {name: sha((TARGET / name).read_bytes())
                  for name in sorted([LAYOUT, TIMER_START, TIMER_STEP] + BACKGROUNDS)},
    }
    (ROOT / 'stash-merge-assets.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Built merged stash tab with {slot_count} slots and auto transmute.')


if __name__ == '__main__':
    build()
