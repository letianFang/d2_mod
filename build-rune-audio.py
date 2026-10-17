"""Merge MDM rune audio into freshly extracted build 93854 client tables."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True, help='MDM.mpq directory')
parser.add_argument('--original', type=Path, default=ROOT / '.original-build-93854')
args = parser.parse_args()
target = ROOT / 'mods/FarmHub/FarmHub.mpq'
assert (args.original / 'data/global/DataVersionBuild.txt').read_bytes() == b'93854'


def read_table(path):
    raw = path.read_bytes()
    lines = raw.decode('latin1').splitlines()
    rows = list(csv.DictReader(io.StringIO(raw.decode('latin1')), delimiter='\t'))
    headers = lines[0].split('\t')
    assert all(None not in row and all(row[h] is not None for h in headers) for row in rows)
    return raw, lines, headers, rows


misc_path = 'data/global/excel/misc.txt'
sound_path = 'data/global/excel/sounds.txt'
misc_raw, misc_lines, misc_headers, misc_rows = read_table(args.original / misc_path)
sound_raw, sound_lines, sound_headers, sound_rows = read_table(args.original / sound_path)
_, _, source_headers, source_rows = read_table(args.source / sound_path)
assert sound_headers == source_headers
source_sounds = {row['Sound']: row for row in source_rows}
next_id = max(int(row['*Index']) for row in sound_rows) + 1
drop_column = misc_headers.index('dropsound')
files = {}
runes = []
audio_info = {}
for number in range(26, 34):
    code = f'r{number:02}'
    sound = f'high_rune_{number}'
    row_index = next(i for i, row in enumerate(misc_rows) if row['code'] == code)
    fields = misc_lines[row_index + 1].split('\t')
    assert fields[drop_column] == 'item_rune'
    fields[drop_column] = sound
    misc_lines[row_index + 1] = '\t'.join(fields)
    new_sound = dict(source_sounds[sound])
    assert new_sound['Loop'] == '0' and new_sound['Redirect'] == ''
    assert new_sound['Channel'] == 'sfx/items_hd'
    assert new_sound['FileName'] == f'item\\{sound}.flac'
    new_sound['*Index'] = str(next_id)
    next_id += 1
    sound_lines.append('\t'.join(new_sound[h] for h in sound_headers))
    audio_relative = f'data/hd/global/sfx/item/{sound}.flac'
    audio = args.source / audio_relative
    data = audio.read_bytes()
    assert data[:4] == b'fLaC' and data[4] & 127 == 0
    assert int.from_bytes(data[5:8], 'big') == 34
    # FLAC STREAMINFO stores sample rate, channels, bit depth, sample count.
    packed = int.from_bytes(data[18:26], 'big')
    rate = packed >> 44
    samples = packed & ((1 << 36) - 1)
    assert rate > 0 and samples > 0
    audio_info[code] = {'sampleRate': rate, 'durationSeconds': round(samples / rate, 3)}
    destination = target / audio_relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(audio, destination)
    files[audio_relative] = hashlib.sha256(data).hexdigest()
    runes.append({'code': code, 'name': misc_rows[row_index]['name'], 'sound': sound})

for relative, lines in [(misc_path, misc_lines), (sound_path, sound_lines)]:
    destination = target / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(('\r\n'.join(lines) + '\r\n').encode('latin1'))
    files[relative] = hashlib.sha256(destination.read_bytes()).hexdigest()

# Verify no changes except the eight drop-sound cells and appended sound rows.
_, _, _, merged_misc = read_table(target / misc_path)
for original, merged in zip(misc_rows, merged_misc):
    expected = dict(original)
    if original['code'] in {r['code'] for r in runes}:
        expected['dropsound'] = f"high_rune_{int(original['code'][1:])}"
    assert expected == merged
_, _, _, merged_sounds = read_table(target / sound_path)
assert merged_sounds[:len(sound_rows)] == sound_rows
assert len(merged_sounds) == len(sound_rows) + 8

manifest = {
    'version': '1.4.0', 'build': '93854', 'source': str(args.source),
    'runes': runes, 'audioInfo': audio_info,
    'miscColumns': len(misc_headers), 'miscRows': len(misc_rows),
    'soundColumns': len(sound_headers), 'soundRows': len(merged_sounds),
    'originalHashes': {misc_path: hashlib.sha256(misc_raw).hexdigest(), sound_path: hashlib.sha256(sound_raw).hexdigest()},
    'files': files,
}
(ROOT / 'rune-audio-assets.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Merged 8 high-rune drop sounds; all other item fields and original sound rows preserved.')
