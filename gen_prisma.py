"""Diagrama PRISMA 2020 (estilo plantilla oficial) para el manuscrito.
Salida: figuras_en/prisma.pdf (vector) y figuras_en/prisma.png (600 dpi).
Uso: python gen_prisma.py [carpeta_salida]"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else 'figuras_en'
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42, 'ps.fonttype': 42})

COL_W = 3.5                    # ancho de columna elsarticle 3p (pulgadas)
W = COL_W * 72                 # coordenadas en puntos
FS, FS_S, LS, PAD, GAP = 7.0, 6.4, 1.15, 4, 9
PH_X, PH_W = 0, 11             # banda de fase
MX, MW = 16, 108               # columna principal
SX = MX + MW + 10              # columna lateral
SW = W - SX - 0.5
INK, LINE = '#111111', '#222222'
ORANGE, BLUE, BLUE_E = '#F2A51A', '#C9DAF0', '#7A9CC8'

def h_of(t, fs):
    return len(t.split('\n')) * fs * LS * 1.12 + 2 * PAD

rows = [
    ('Identification',
     'Records identified from\ndatabases (n = 724)\nScopus (n = 586)\nWeb of Science (n = 138)\nNo date restriction',
     'Records removed before screening\n(n = 575)\nDuplicates (n = 171; 127 cross-\ndatabase, 44 internal)\n'
     'Non-primary type, EC-4 (n = 385)\nLanguage, IC-4 (n = 5)\nSecondary literature or incomplete\nmetadata (n = 14)'),
    ('Screening',
     'Records screened by\ntitle and abstract\n(n = 149)',
     'Records excluded (n = 69)\nOff-topic, general AI, or no real\nphysical constraint (IC-2 / EC-1)'),
    ('Screening',
     'Full-text articles\nassessed for eligibility\n(n = 80)',
     'Excluded at full text (n = 7)\nDo not optimize or evaluate\nan LLM'),
    ('Included',
     'Studies included in the\nreview (n = 73)\n2024: n = 8 | 2025: n = 28\n2026: n = 37',
     None),
]
note = ('9 of the 73 included studies (12%) report a concrete edge platform\n'
        'with physical metrics. The remaining 64 use generic descriptors or\n'
        'validate on server GPUs or FPGAs outside the edge scope.')

HEAD = 16
y = HEAD + GAP
lay = []
for ph, mt, st in rows:
    hm = h_of(mt, FS); hs = h_of(st, FS_S) if st else 0
    rh = max(hm, hs)
    lay.append((ph, mt, st, y, rh, hm, hs)); y += rh + GAP
hn = h_of(note, FS_S)
H = y + hn + 1

fig = plt.figure(figsize=(COL_W, H / 72))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

def box(x, yt, w, h, t, fs=FS, fc='white', ec=LINE, lw=0.7, color=INK, r=0):
    ax.add_patch(FancyBboxPatch((x, yt), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                 linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w/2, yt + h/2, t, ha='center', va='center', fontsize=fs, color=color,
            linespacing=LS, zorder=3)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=6,
                 linewidth=0.7, color=LINE, zorder=1, shrinkA=0, shrinkB=0))

# cabecera
box(MX, 0, W - MX - 0.5, HEAD, 'Identification of studies via databases and registers',
    fs=7.2, fc=ORANGE, ec=ORANGE, color='white', r=3)

prev = None; phases = {}
for ph, mt, st, yt, rh, hm, hs in lay:
    ym = yt + (rh - hm) / 2
    box(MX, ym, MW, hm, mt)
    if st:
        ys = yt + (rh - hs) / 2
        box(SX, ys, SW, hs, st, fs=FS_S)
        arrow(MX + MW, ym + hm/2, SX, ym + hm/2)
    if prev is not None:
        arrow(MX + MW/2, prev, MX + MW/2, ym)
    prev = ym + hm
    p0, p1 = phases.get(ph, (yt, yt + rh)); phases[ph] = (min(p0, yt), max(p1, yt + rh))
box(MX, y, W - MX - 0.5, hn, note, fs=FS_S)

for ph, (p0, p1) in phases.items():
    ax.add_patch(FancyBboxPatch((PH_X, p0), PH_W, p1 - p0, boxstyle='round,pad=0,rounding_size=3',
                 linewidth=0.6, edgecolor=BLUE_E, facecolor=BLUE, zorder=1))
    ax.text(PH_X + PH_W/2, (p0 + p1)/2, ph, rotation=90, ha='center', va='center',
            fontsize=6.6, color=INK, weight='bold')

for ext in ('pdf', 'png'):
    fig.savefig(os.path.join(OUT, f'prisma.{ext}'), dpi=1100 if ext == 'png' else None,
                bbox_inches='tight', pad_inches=0.02, facecolor='white')
print('ok', round(H/72, 2), 'in')
