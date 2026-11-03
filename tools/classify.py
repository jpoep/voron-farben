"""Turn the raw OCCT export of the official Voron 2.4r2 CAD into a viewer-ready GLB.

- removes overlapping alternative variants (Fusion keeps them hidden, STEP exports all)
- assigns role materials by CAD colour + assembly path:
  1_first_color (dark printed), 2_second_color (red printed), 3_chains, 4_frame, panels
- gives the remaining (hardware) materials sensible PBR values
Geometry (BIN chunk) is left untouched; unused data is pruned later by gltf-transform.
"""
import json, re, struct, sys, collections

src, dst = sys.argv[1], sys.argv[2]
b = open(src, 'rb').read()
jl = struct.unpack_from('<I', b, 12)[0]
g = json.loads(b[20:20 + jl])
binchunk = b[20 + jl:]
N, M = g['nodes'], g['materials']

def hexcol(mi):
    c = M[mi].get('pbrMetallicRoughness', {}).get('baseColorFactor', [1, 1, 1, 1])
    return '#%02x%02x%02x' % tuple(round(x * 255) for x in c[:3])

def base(name):
    return re.sub(r'( \(\d+\))+$', '', name or '')

# --- 1. variants to drop (matched against the "/"-joined base-name path) -----------------
DROP = [
    r'/ Skirt / .* / (300|350)$',                       # keep 250 skirts, matches the 370 mm frame
    r'/ Controllers / (?!Octopus)[^/]+$',               # keep one controller board
    r'/ Left_Power_Inlet / Filtered$',
    r'/ IEC-GS / For_1\.2mm_Mounting_Tabs$',
    r'/ Z Tensioner 6mm$',
    r'/ D2F Microswitch Pod$',
    r'/ Cable_Cover_For_PCB$',
    r'/ Panasonic GX-H15A$',
    r'/ Chain_Anchor_3_Hole[^/]*$',
    r'/ XY Cable Chain Bridge - 3 Hole$',
    r'/ Front_Skirt_Logo$',                             # alternative to the Mini12864 display (same spot)
]
DROP = [re.compile(p) for p in DROP]
dropped = collections.Counter()

def prune(i, path):
    n = N[i]
    keep = []
    for c in n.get('children', []):
        p = path + ' / ' + base(N[c].get('name'))
        hit = next((d for d in DROP if d.search(p)), None)
        if hit:
            dropped[hit.pattern] += 1
            continue
        keep.append(c)
        prune(c, p)
    if 'children' in n:
        n['children'] = keep

for r in g['scenes'][0]['nodes']:
    prune(r, base(N[r].get('name')))

# --- 2. classification ---------------------------------------------------------------
DARK = {'#0d0d0d', '#101010', '#111111', '#121212', '#141414', '#131313', '#080808', '#0b0b0b'}
RED = {'#8d0905', '#b80704', '#8e0000', '#ab0100'}
NOT_PRINTED = re.compile(
    r'Fan|turbine|NEMA|Stepper|LDO-36|pcb|PCB|VHB|Raspberry Pi|Switch|Fuse|IEC GS|Jog|Screen|KW10|'
    r'Microswitch|V7_wo_fan|Needle_Bearings|asxl345|LRS-200-24 / COMPOUND|c-3-1609115|8008:|8009:|'
    r'BSP Bowden|1X4_CONN|VORONDESIGN_XY-Endstop|Heatsink|Foam Tape|Filter Element|Rubber Foot|Magnet|'
    r'MGN|PRODUCT_NAME|Bed heater')
PANEL_SHEET = re.compile(r'Transparent Panels / (Side Panel|Top Panel|Front Door (Left|Right)) / SOLID$')
CHAIN = re.compile(r'X_Cable_Chain|Y Cable Chain|IGUS Z Chain')

def classify(path, col):
    if re.search(r'/ HFSB5-[^/]*( / (SOLID|COMPOUND))?$', path):
        return '4_frame'
    if re.search(r'/ 10in Bed / (10in MIC6 Plate|Magnet Sheet|Flex Sheet)$', path):
        return '4_frame'                                # build plate follows the frame colour
    if PANEL_SHEET.search(path):
        return 'panels'
    if CHAIN.search(path) and col in DARK:
        return '3_chains'
    if NOT_PRINTED.search(path):
        return None
    if col in RED:
        return '2_second_color'
    if col in DARK:
        return '1_first_color'
    return None

role_mat = {}
# Distinct defaults (preset "Graphit") so gltf-transform's dedup can't merge the role materials,
# which it would if they were identical (it ignores names).
ROLE_DEFAULT = {
    '1_first_color':  ('#2b2e33', 1.0, 0.0, 0.62),
    '2_second_color': ('#f2707a', 1.0, 0.0, 0.62),
    '3_chains':       ('#ac96c6', 1.0, 0.0, 0.62),
    '4_frame':        ('#222324', 1.0, 0.35, 0.45),
    'panels':         ('#2a2f31', 0.45, 0.0, 0.08),
}
def srgb_to_linear(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
def role_index(role):
    if role not in role_mat:
        col, alpha, metal, rough = ROLE_DEFAULT[role]
        mat = {'name': role, 'pbrMetallicRoughness': {'baseColorFactor': srgb_to_linear(col) + [alpha],
                                                      'metallicFactor': metal, 'roughnessFactor': rough}}
        if alpha < 1:
            mat['alphaMode'] = 'BLEND'
        M.append(mat)
        role_mat[role] = len(M) - 1
    return role_mat[role]

stats = collections.Counter()
mesh_variant = {}   # (mesh idx, tuple(materials)) -> new mesh idx, so shared meshes stay shared when possible

def walk(i, path):
    n = N[i]
    p = path + ' / ' + base(n.get('name'))
    if 'mesh' in n:
        mesh = g['meshes'][n['mesh']]
        mats = []
        for pr in mesh['primitives']:
            role = classify(p, hexcol(pr['material']))
            stats[role] += 1
            mats.append(role_index(role) if role else pr['material'])
        key = (n['mesh'], tuple(mats))
        if key not in mesh_variant:
            if all(pr['material'] == m for pr, m in zip(mesh['primitives'], mats)):
                mesh_variant[key] = n['mesh']
            else:
                new = json.loads(json.dumps(mesh))
                for pr, m in zip(new['primitives'], mats):
                    pr['material'] = m
                g['meshes'].append(new)
                mesh_variant[key] = len(g['meshes']) - 1
        n['mesh'] = mesh_variant[key]
    for c in n.get('children', []):
        walk(c, p)

for r in g['scenes'][0]['nodes']:
    walk(r, '')

# --- 3. PBR for the hardware that keeps its CAD colour -------------------------------
METAL = {'#5a5a5a', '#e9e9eb', '#989898', '#e59833', '#83807d', '#8d8e8d', '#727272', '#737373',
         '#e9e9e9', '#afabab', '#a6a6a6', '#8d8d8d', '#9a9a9a', '#868686', '#8b8b8b', '#2c2c2c', '#bc0000'}
for i, m in enumerate(M):
    if m.get('name') in role_mat:
        continue
    pbr = m.setdefault('pbrMetallicRoughness', {})
    metal = hexcol(i) in METAL
    pbr['metallicFactor'] = 0.85 if metal else 0.0
    pbr['roughnessFactor'] = 0.35 if metal else 0.6

g.setdefault('asset', {})['copyright'] = 'Voron Design, GPL-3.0 (github.com/VoronDesign/Voron-2)'

js = json.dumps(g, separators=(',', ':')).encode()
js += b' ' * (-len(js) % 4)
out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + len(binchunk)) + struct.pack('<II', len(js), 0x4E4F534A) + js + binchunk
open(dst, 'wb').write(out)
print('dropped:', dict(dropped))
print('primitives per role:', dict(stats))
