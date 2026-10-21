# -*- coding: utf-8 -*-
"""English, single-column versions of the four manuscript figures (FGCS, twocolumn).

Each figure is drawn at its final printed width (one column, ~3.5 in) so the
font sizes set here are the sizes that appear in the PDF: nothing is scaled
down by LaTeX. Include with  \\includegraphics[width=\\columnwidth]{...}

Outputs (figuras_en/):
    image8.png              PRISMA flow diagram
    image6.png              Strategic thematic map
    grafico_frecuencia.pdf  Adoption frequency of optimisation techniques
    grafico_rq4_matriz.pdf  RQ4: technique x hardware platform matrix
(PNG/PDF twins of each are also written for previewing.)
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
import pandas as pd

from process_rsl import clean_keyword   # same keyword normalisation as the corpus analysis

OUT = 'figuras_en'
os.makedirs(OUT, exist_ok=True)

COL_W = 3.5                     # inches: one column of elsarticle 3p twocolumn
NAVY, ROSE, SLATE, INK, GRID = '#343b4a', '#f43f5e', '#94a3b8', '#1e293b', '#cbd5e1'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 8.5,
    'axes.labelsize': 9,
    'axes.labelweight': 'bold',
    'axes.labelcolor': INK,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'xtick.color': '#475569',
    'ytick.color': '#475569',
    'text.color': INK,
    'pdf.fonttype': 42,          # TrueType, not Type 3 (Elsevier-friendly)
    'ps.fonttype': 42,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.03,
    'savefig.facecolor': 'white',
})


def save(fig, stem, main_ext):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(OUT, f'{stem}.{ext}'))
    plt.close(fig)
    print(f'[ok] {stem}.{main_ext}')


# =================================================================== 1. FREQUENCY
import csv as _csv
_rows = list(_csv.DictReader(open('codificacion_rq4.csv', encoding='utf8')))
_n = lambda c: sum(int(r[c]) for r in _rows)   # conteos desde la codificacion por estudio (n=80)
tec = [('Quantization', _n('cuantizacion')),
       ('Pruning and\nsparsity induction', _n('poda')),
       ('Knowledge\ndistillation', _n('destilacion')),
       ('Low-rank (LoRA/PEFT\nand factorization)', _n('lora_peft'))][::-1]
fig, ax = plt.subplots(figsize=(COL_W, 2.35))
y = list(range(len(tec)))
bars = ax.barh(y, [v for _, v in tec], height=0.62, color=NAVY, zorder=3)
bars[-1].set_color(ROSE)
for i, (_, v) in enumerate(tec):
    ax.text(v + 0.8, i, f'{v} ({v/len(_rows)*100:.0f}%)', va='center', ha='left',
            fontsize=8.5, weight='bold', color=INK)
ax.set_yticks(y)
ax.set_yticklabels([k for k, _ in tec], fontsize=8.5, color=INK)
ax.set_xlabel(f'Number of studies (n = {len(_rows)})', labelpad=5)
ax.set_xlim(0, 60)
ax.set_xticks(range(0, 51, 10))
ax.tick_params(axis='x', colors=SLATE)
ax.tick_params(axis='y', length=0)
ax.grid(axis='x', linestyle='--', alpha=.3, color=SLATE, zorder=0)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(SLATE); ax.spines['bottom'].set_linewidth(.8)
fig.tight_layout()
save(fig, 'grafico_frecuencia', 'pdf')


# =================================================================== 2. PRISMA
# Coordinates are in points (1/72 in) so box sizes follow the text they hold.
W = COL_W * 72
FS, FS_SIDE, LS = 8.4, 7.3, 1.08
GAP, PAD = 7, 4
PH_X, PH_W = 0, 13                 # phase band
MX, MW = 17, 106                   # main column
SX = MX + MW + 8                  # side column
SW = W - SX


def h_of(text, fs):
    return len(text.split('\n')) * fs * LS * 1.12 + 2 * PAD


rows = [  # (phase, main text, side text, main style)
    ('IDENTIFICATION',
     'Records identified\nfrom databases\n(n = 724)\nScopus: n = 586\nWoS: n = 138',
     'No date restriction in the\ninitial search (literature\nsince 2003)', 'normal'),
    ('SCREENING',
     'Records after\nde-duplication and\npreliminary screening\n(n = 149)',
     'Records excluded (n = 575)\nDuplicates: n = 171\n(127 cross-db, 44 internal)\n'
     'Non-primary (EC-4): n = 385\nLanguage (IC-4): n = 5\nSecondary or incomplete\nmetadata: n = 14',
     'normal'),
    ('SCREENING',
     'Records screened by\ntitle and abstract\n(n = 149)',
     'Records excluded (n = 69)\nOff-topic, general AI, or\nsimulation without a real\nphysical constraint\n(fails IC-2 / meets EC-1)',
     'normal'),
    ('SCREENING',
     'Full-text articles\nassessed for\neligibility (n = 80)',
     'Excluded at full text (n = 7)\nDo not optimize or\nevaluate an LLM',
     'normal'),
    ('INCLUDED',
     'Studies included\nin the review\n(n = 73)\n2024: 8 | 2025: 28\n2026: 37',
     None, 'highlight'),
]
note = ('9 of the 73 included studies (12%) report a concrete\nedge platform with physical metrics. The remaining 64\n'
        'use generic descriptors or validate on server GPUs or\nFPGAs outside the edge scope. 33 studies (45%) were coded\n'
        'from the abstract and indexed metadata.')

layout, y = [], 0
for ph, mt, st, style in rows:
    hm, hs = h_of(mt, FS), (h_of(st, FS_SIDE) if st else 0)
    rh = max(hm, hs)
    layout.append((ph, mt, st, style, y, rh, hm, hs))
    y += rh + GAP
hn = h_of(note, FS_SIDE)
H = y + hn + 2

fig = plt.figure(figsize=(COL_W, H / 72))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')


def box(x, ytop, w, h, text, style='normal', fs=FS):
    fc = {'highlight': '#fdf2f4', 'side': '#f8fafc'}.get(style, '#ffffff')
    ax.add_patch(FancyBboxPatch((x, ytop), w, h, boxstyle='round,pad=0,rounding_size=3',
                 linewidth=1.1 if style == 'highlight' else 0.7,
                 edgecolor=ROSE if style == 'highlight' else SLATE, facecolor=fc, zorder=2))
    ax.text(x + w/2, ytop + h/2, text, ha='center', va='center', zorder=3, fontsize=fs,
            color=INK, weight='bold' if style == 'highlight' else 'normal', linespacing=LS)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=5,
                 linewidth=0.8, color=SLATE, zorder=1, shrinkA=0, shrinkB=0))


prev_bottom, phases = None, {}
for ph, mt, st, style, ytop, rh, hm, hs in layout:
    ym = ytop + (rh - hm) / 2
    box(MX, ym, MW, hm, mt, style)
    if st:
        box(SX, ytop + (rh - hs) / 2, SW, hs, st, 'side', FS_SIDE)
        if ph != 'IDENTIFICATION':
            arrow(MX + MW, ytop + rh/2, SX, ytop + rh/2)
    if prev_bottom is not None:
        arrow(MX + MW/2, prev_bottom, MX + MW/2, ym)
    prev_bottom = ym + hm
    p0, p1 = phases.get(ph, (ytop, ytop + rh))
    phases[ph] = (min(p0, ytop), max(p1, ytop + rh))
box(MX, y, W - MX - 0.5, hn, note, 'side', FS_SIDE)

for ph, (p0, p1) in phases.items():
    ax.add_patch(FancyBboxPatch((PH_X, p0), PH_W, p1 - p0, boxstyle='round,pad=0,rounding_size=3',
                 linewidth=0, facecolor='#fde7eb', zorder=1))
    ax.text(PH_X + PH_W/2, (p0 + p1)/2, ph, rotation=90, ha='center', va='center',
            fontsize=7.4, weight='bold', color=ROSE)

save(fig, 'image8', 'png')


# =================================================================== 3. THEMATIC MAP
df = pd.read_excel('ARTICULOS_UNIFICADOS_CRIBADO.xlsx', sheet_name='SELECCIONADOS-FINAL')
df['DE'] = df['DE'].fillna('')
kws_all = []
for s in df['DE']:
    if s:
        kws_all.extend([k for k in (clean_keyword(x) for x in str(s).split(';')) if k])
kw_counts = pd.Series(kws_all).value_counts().reset_index()
kw_counts.columns = ['Keyword', 'Frecuencia']

G = nx.Graph()
for _, r in kw_counts.head(25).iterrows():
    G.add_node(r['Keyword'], size=r['Frecuencia'])
for s in df['DE']:
    if not s:
        continue
    kws = [k for k in set(clean_keyword(x) for x in str(s).split(';') if x.strip()) if k in G.nodes]
    for i in range(len(kws)):
        for j in range(i + 1, len(kws)):
            if G.has_edge(kws[i], kws[j]):
                G[kws[i]][kws[j]]['weight'] += 1
            else:
                G.add_edge(kws[i], kws[j], weight=1)
G.remove_nodes_from(list(nx.isolates(G)))

rows = []
for n in G.nodes:
    c = sum(G[n][m]['weight'] for m in G.neighbors(n))
    nb = list(G.neighbors(n))
    if len(nb) < 2:
        d = 0.0
    else:
        e = G.subgraph(nb).edges(data=True)
        d = sum(x.get('weight', 1.0) for *_, x in e) / len(e) if len(e) else 0.0
    rows.append({'Keyword': n, 'Centrality': float(c), 'Density': float(d), 'Frequency': int(G.nodes[n]['size'])})
th = pd.DataFrame(rows)
th.to_csv(os.path.join(OUT, 'mapa_tematico_datos.csv'), index=False)

fig, ax = plt.subplots(figsize=(COL_W, 3.2))
ax.scatter(th['Centrality'], th['Density'], s=th['Frequency'] * 4.5, color=ROSE, alpha=0.75,
           edgecolors='white', linewidths=0.6, zorder=3)
med_c, med_d = float(th['Centrality'].median()), float(th['Density'].median())
ax.axvline(med_c, color=SLATE, ls='--', lw=0.9, alpha=0.8, zorder=1)
ax.axhline(med_d, color=SLATE, ls='--', lw=0.9, alpha=0.8, zorder=1)
ax.margins(x=0.2, y=0.2)
xl, yl = ax.get_xlim(), ax.get_ylim()
qfs = 6.8
quad = [
    ax.text(xl[1] - (xl[1]-med_c)*.03, yl[1] - (yl[1]-med_d)*.04, 'MOTOR\nTHEMES', ha='right', va='top', fontsize=qfs, weight='bold', color='#16a34a'),
    ax.text(xl[0] + (med_c-xl[0])*.05, yl[1] - (yl[1]-med_d)*.04, 'NICHE\nTHEMES', ha='left', va='top', fontsize=qfs, weight='bold', color='#4f46e5'),
    ax.text(xl[0] + (med_c-xl[0])*.05, yl[0] + (med_d-yl[0])*.04, 'EMERGING OR\nDECLINING', ha='left', va='bottom', fontsize=qfs, weight='bold', color='#dc2626'),
    ax.text(xl[1] - (xl[1]-med_c)*.03, yl[0] + (med_d-yl[0])*.04, 'BASIC AND\nTRANSVERSAL', ha='right', va='bottom', fontsize=qfs, weight='bold', color='#ca8a04'),
]
# Label positions fixed by hand (adjustText crossed leaders over the dense cluster).
# (dx, dy) in data units from the bubble centre, plus alignment.
LAB = {
    'Large language models':  (4, 0.42, 'center', 'bottom'),
    'Computational modeling': (-34, -0.10, 'center', 'top'),
    'Quantization':           (-12, 0.0, 'right', 'center'),
    'Knowledge distillation': (8, 0.0, 'left', 'center'),
    'Model compression':      (27, 0.63, 'left', 'center'),
    'Accuracy':               (17, 0.47, 'left', 'center'),
    'Training':               (17, 0.30, 'left', 'center'),
    'Adaptation models':      (15, 0.02, 'left', 'center'),
    'Optimization':           (-28, -0.60, 'left', 'center'),
    'Edge computing':         (6, 1.30, 'center', 'bottom'),
    'Hardware':               (20, 0.35, 'left', 'center'),
    'Deep learning':          (-6, 0.40, 'center', 'bottom'),
}
ABS = {  # posiciones absolutas de etiqueta (x, y) para evitar cruces
    'Large language models':  (107, 2.62, 'center', 'bottom'),
    'Knowledge distillation': (24, 3.97, 'left', 'center'),
    'Model compression':      (45, 3.62, 'left', 'center'),
    'Accuracy':               (58, 3.33, 'left', 'center'),
    'Training':               (60, 2.98, 'left', 'center'),
    'Adaptation models':      (60, 2.63, 'left', 'center'),
    'Optimization':           (3, 2.68, 'left', 'center'),
    'Edge computing':         (0, 3.5, 'center', 'bottom'),
}
top = th.nlargest(10, 'Frequency')
print(top[['Keyword','Centrality','Density']].to_string())
SHOW = {'Large language models': 'Large language\nmodels', 'Adaptation models': 'Adaptation\nmodels',
        'Edge computing': 'Edge\ncomputing', 'Deep learning': 'Deep\nlearning'}
for _, r in top.iterrows():
    dx, dy, ha, va = LAB.get(r['Keyword'], (3, 0, 'left', 'center'))
    if r['Keyword'] in ABS:
        tx, ty, ha, va = ABS[r['Keyword']]; dx, dy = tx - r['Centrality'], ty - r['Density']
    far = abs(dx) > 3 or abs(dy) > 0.08
    ax.annotate(SHOW.get(r['Keyword'], r['Keyword']), (r['Centrality'], r['Density']),
                xytext=(r['Centrality'] + dx, r['Density'] + dy), ha=ha, va=va,
                fontsize=7, weight='bold', color=NAVY, zorder=5, linespacing=1.0,
                arrowprops=dict(arrowstyle='-', color=SLATE, lw=0.5, shrinkA=1, shrinkB=3) if far else None)
ax.set_xlim(xl); ax.set_ylim(yl)
ax.set_xlabel('Centrality (external relevance)', labelpad=4)
ax.set_ylabel('Density (internal cohesion)', labelpad=4)
ax.grid(True, ls='--', alpha=0.25, color=GRID)
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(length=0)
fig.tight_layout()
save(fig, 'image6', 'png')


# =================================================================== 4. RQ4 MATRIX
# Generada por gen_figura_rq4.py a partir de codificacion_rq4.csv (fuente unica de los conteos).
import subprocess, sys
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen_figura_rq4.py'), 'en'], check=True)
print('[ok] grafico_rq4_matriz.pdf')
