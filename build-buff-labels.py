"""Build the Battle Orders / Battle Command text labels for FarmHub.

The vanilla persistent overlays of the two warcry states are replaced in HD:
states.txt gives state `battleorders` overlay `battleorders` and state
`battlecommand` overlay `battlecommand`; overlay.txt puts both in Character
`common`, so D2R reads data/hd/overlays/common/<overlay>.json. No data table is
changed. Every unit holding the state (player, mercenary, monsters) shows the
label for as long as the state lasts. The words sit right of the billboard
centre, so they appear beside the body at waist height instead of on it.

The label is a camera-facing billboard: a byte copy of the Nihlathak direction
arrow particle with only its texture path changed (same length), plus a BC3
texture rendered here. SKILL sits in the upper half of its texture and LIFE in
the lower half, so with both buffs active the words stack instead of overlapping.
Standard library only.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD = ROOT / 'mods/FarmHub/FarmHub.mpq'

TEMPLATE_PARTICLE = 'data/hd/directionarrows/particles/directionarrows_0045.particles'
TEMPLATE_TEXTURE = 'data/hd/directionarrows/textures/directionarrows_0045.texture'
TEMPLATE_SAMPLER = TEMPLATE_TEXTURE.encode('ascii')

# Height above the unit's feet and billboard scale. Tune these after in-game checks.
# 2026-11-07 test: height 1.0 / scale 0.5 drew the words at the feet with a good size.
# A character is about 3 units tall (preset walls are 3.8-7.6), so the waist is about 1.6.
LABEL_HEIGHT = 1.6
LABEL_SCALE = 1.0

SIZE = 1024
GLYPH_HEIGHT = 75  # 150 px at scale 0.5 had a good size; keep the same size in the world
TEXT_LEFT = 0.62  # left edge of the words; the billboard centre (0.5) is on the unit, so this is beside the body
STROKE = 0.17  # stroke width as a fraction of glyph height

LABELS = {
    # overlay name: (text, RGB, vertical centre in the texture as a fraction of its height, file stem)
    'battlecommand': ('SKILL', (255, 205, 60), 0.448, 'farmhub_bc_skilltext'),
    'battleorders': ('LIFE', (255, 85, 85), 0.552, 'farmhub_bo_life_text'),
}

# Glyphs as polylines in a box of width w and height 1 (y grows downwards).
GLYPH_WIDTH = {'S': 0.62, 'K': 0.62, 'I': 0.0, 'L': 0.52, 'F': 0.52, 'E': 0.55}


def s_curve(w):
    """Two elliptical bowls: the upper one counter-clockwise from 20 to 270 degrees,
    the lower one clockwise from 90 to -160 degrees (screen y grows downwards)."""
    points = []
    for k in range(25):
        a = math.radians(20 + k * 250 / 24)
        points.append((w / 2 + w / 2 * math.cos(a), 0.25 - 0.25 * math.sin(a)))
    for k in range(1, 25):
        a = math.radians(90 - k * 250 / 24)
        points.append((w / 2 + w / 2 * math.cos(a), 0.75 - 0.25 * math.sin(a)))
    return [points]


def glyph(letter):
    w = GLYPH_WIDTH[letter]
    return {
        'S': s_curve(w),
        'K': [[(0, 0), (0, 1)], [(w, 0), (0, 0.6)], [(0.22 * w, 0.44), (w, 1)]],
        'I': [[(0, 0), (0, 1)]],
        'L': [[(0, 0), (0, 1), (w, 1)]],
        'F': [[(w, 0), (0, 0), (0, 1)], [(0, 0.5), (0.8 * w, 0.5)]],
        'E': [[(w, 0), (0, 0), (0, 1), (w, 1)], [(0, 0.5), (0.8 * w, 0.5)]],
    }[letter]


def segment_distance(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length))
    x, y = ax + t * dx - px, ay + t * dy - py
    return math.sqrt(x * x + y * y)


def render(text, colour, centre):
    """Additive label: black is invisible, so the RGB carries the anti-aliased text."""
    h = GLYPH_HEIGHT
    stroke = STROKE * h
    gap = 0.32 * h
    widths = [GLYPH_WIDTH[c] * h + stroke for c in text]
    total = sum(widths) + gap * (len(text) - 1)
    left = TEXT_LEFT * SIZE + stroke / 2
    assert left + total < SIZE - stroke, 'label runs off the texture'
    top = centre * SIZE - h / 2
    segments = []
    x = left
    for c, width in zip(text, widths):
        for line in glyph(c):
            pts = [(x + px * h, top + py * h) for px, py in line]
            segments.extend((a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:]))
        x += width + gap
    coverage = bytearray(SIZE * SIZE)
    radius = stroke / 2
    x0, x1 = int(left - stroke), int(left + total + stroke)
    y0, y1 = int(top - stroke), int(top + h + stroke)
    for py in range(y0, y1 + 1):
        for px in range(x0, x1 + 1):
            cx, cy = px + 0.5, py + 0.5
            d = min(segment_distance(cx, cy, *s) for s in segments)
            alpha = max(0.0, min(1.0, radius - d + 0.5))
            if alpha:
                coverage[py * SIZE + px] = round(alpha * 255)
    r, g, b = colour
    return [(r * a // 255, g * a // 255, b * a // 255) for a in coverage]


def downsample(pixels, size):
    half = size // 2
    out = []
    for y in range(half):
        for x in range(half):
            quad = [pixels[(2 * y + dy) * size + 2 * x + dx] for dy in (0, 1) for dx in (0, 1)]
            out.append(tuple((sum(p[i] for p in quad) + 2) // 4 for i in range(3)))
    return out


def rgb565(c):
    return (c[0] * 31 + 127) // 255 << 11 | (c[1] * 63 + 127) // 255 << 5 | (c[2] * 31 + 127) // 255


def expand565(v):
    return ((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31


OPAQUE_ALPHA = bytes((255, 255, 0, 0, 0, 0, 0, 0))  # matches the template: alpha 255 everywhere


def bc3(pixels, size):
    out = bytearray()
    for by in range(0, size, 4):
        for bx in range(0, size, 4):
            block = [pixels[(by + y) * size + bx + x] for y in range(4) for x in range(4)]
            bright = max(block, key=sum)
            dark = min(block, key=sum)
            c0, c1 = rgb565(bright), rgb565(dark)
            if c0 < c1:
                c0, c1 = c1, c0
            if c0 == c1:
                out += OPAQUE_ALPHA + struct.pack('<HHI', c0, c1, 0)
                continue
            p0, p1 = expand565(c0), expand565(c1)
            palette = [p0, p1,
                       tuple((2 * a + b) // 3 for a, b in zip(p0, p1)),
                       tuple((a + 2 * b) // 3 for a, b in zip(p0, p1))]
            indices = 0
            for i, p in enumerate(block):
                best = min(range(4), key=lambda k: sum((p[j] - palette[k][j]) ** 2 for j in range(3)))
                indices |= best << (2 * i)
            out += OPAQUE_ALPHA + struct.pack('<HHI', c0, c1, indices)
    return out


def texture(pixels):
    """Reuse the template header: same format (BC3), 1024x1024 and the same 8-level mip table."""
    template = (MOD / TEMPLATE_TEXTURE).read_bytes()
    header = template[:0x64]
    assert header[:4] == b'<DE(' and struct.unpack_from('<HII', header, 4)[0] == 61
    assert struct.unpack_from('<II', header, 8) == (SIZE, SIZE)
    levels = struct.unpack_from('<I', header, 0x1c)[0]
    data = bytearray(header)
    size = SIZE
    for level in range(levels):
        expected, _ = struct.unpack_from('<II', header, 0x24 + level * 8)
        encoded = bc3(pixels, size)
        assert len(encoded) == expected
        data += encoded
        if level + 1 < levels:
            pixels = downsample(pixels, size)
            size //= 2
    assert len(data) == len(template)
    return bytes(data)


def overlay_json(name, particle, texture_path, entity_id):
    return {
        'dependencies': {
            'particles': [{'path': particle}],
            'models': [],
            'skeletons': [],
            'animations': [],
            'textures': [
                {'path': texture_path},
                {'path': 'data/hd/vfx/Library/PopcornFXCore/Materials/DefaultTextures/White.texture'},
            ],
            'physics': [],
            'json': [],
            'variantdata': [],
            'objecteffects': [],
            'other': [],
        },
        'type': 'OverlayDefinition',
        'name': name,
        'entities': [{
            'type': 'Entity',
            'name': 'entity_root',
            'id': entity_id,
            'components': [
                {
                    'type': 'VfxDefinitionComponent',
                    'name': 'component_vfx',
                    'filename': particle,
                    'hardKillOnDestroy': True,
                },
                {
                    'type': 'TransformDefinitionComponent',
                    'name': 'entity_root_TransformDefinition',
                    'position': {'x': 0.0, 'y': LABEL_HEIGHT, 'z': 0.0},
                    'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
                    'scale': {'x': LABEL_SCALE, 'y': LABEL_SCALE, 'z': LABEL_SCALE},
                    'inheritOnlyPosition': True,
                },
            ],
        }],
    }


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    particle_template = (MOD / TEMPLATE_PARTICLE).read_bytes()
    assert particle_template.count(TEMPLATE_SAMPLER) == 1
    files = {}
    labels = {}
    for index, (overlay, (text, colour, centre, stem)) in enumerate(LABELS.items()):
        texture_path = f'data/hd/directionarrows/textures/{stem}.texture'
        particle_path = f'data/hd/directionarrows/particles/{stem}.particles'
        assert len(texture_path) == len(TEMPLATE_TEXTURE)
        outputs = {
            texture_path: texture(render(text, colour, centre)),
            particle_path: particle_template.replace(TEMPLATE_SAMPLER, texture_path.encode('ascii')),
            f'data/hd/overlays/common/{overlay}.json': (json.dumps(
                overlay_json(overlay, particle_path, texture_path, 3900000300 + index), indent=4) + '\n').encode('utf-8'),
        }
        for relative, data in outputs.items():
            path = MOD / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            files[relative] = sha(data)
        labels[overlay] = {'text': text, 'rgb': list(colour), 'textureCentre': centre,
                           'overlay': f'data/hd/overlays/common/{overlay}.json'}
    manifest = {
        'build': '93854',
        'labels': labels,
        'labelHeight': LABEL_HEIGHT,
        'labelScale': LABEL_SCALE,
        'textLeft': TEXT_LEFT,
        'template': {'particle': TEMPLATE_PARTICLE, 'texture': TEMPLATE_TEXTURE,
                     'particleSha256': sha(particle_template)},
        'tablesChanged': [],
        'files': files,
        'runtimeVerification': 'pending',
    }
    (ROOT / 'buff-labels-assets.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Built SKILL/LIFE labels for Battle Command and Battle Orders.')


if __name__ == '__main__':
    build()
