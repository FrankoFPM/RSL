# -*- coding: utf-8 -*-
"""Genera grafico_frecuencia.pdf y image8.png (PRISMA) con las cifras corregidas."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, ROSE, SLATE, INK = '#343b4a', '#f43f5e', '#94a3b8', '#1e293b'

# ---------------------------------------------------------------- 1. FRECUENCIA
# Serie unica -> sin leyenda, un solo color, etiquetas directas, ejes recesivos.
import csv as _csv
_rows = list(_csv.DictReader(open('codificacion_rq4.csv', encoding='utf8')))
_n = lambda c: sum(int(r[c]) for r in _rows)   # conteos desde la codificacion por estudio (n=80)
tec = [('Cuantización', _n('cuantizacion')), ('Poda de red e inducción\nde esparsidad (Pruning)', _n('poda')),
       ('Destilación de conocimiento', _n('destilacion')), ('Rango bajo\n(LoRA/PEFT y factorización)', _n('lora_peft'))]
tec = tec[::-1]
fig, ax = plt.subplots(figsize=(9, 4.6))
y = range(len(tec))
bars = ax.barh(list(y), [v for _, v in tec], height=0.62, color=NAVY, zorder=3)
bars[-1].set_color(ROSE)                     # destaca la dominante
for i, (_, v) in enumerate(tec):
    ax.text(v + 0.8, i, f'{v}  ({v/80*100:.0f}%)', va='center', ha='left',
            fontsize=10.5, weight='bold', color=INK)
ax.set_yticks(list(y)); ax.set_yticklabels([k for k, _ in tec], fontsize=10.5, color=INK)
ax.set_xlabel('Número de estudios (n = 80)', fontsize=11, weight='bold', color=INK, labelpad=10)
ax.set_xlim(0, 56)
ax.xaxis.set_ticks(range(0, 51, 10))
ax.tick_params(axis='x', colors=SLATE, labelsize=9.5)
ax.grid(axis='x', linestyle='--', alpha=.25, color=SLATE, zorder=0)
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(SLATE); ax.spines['bottom'].set_linewidth(.8)
plt.tight_layout()
plt.savefig('figuras/grafico_frecuencia.pdf', bbox_inches='tight')
plt.savefig('figuras/grafico_frecuencia.png', dpi=200, bbox_inches='tight')
plt.close()
print('[ok] grafico_frecuencia.pdf / .png')

# ---------------------------------------------------------------- 2. PRISMA
fig, ax = plt.subplots(figsize=(10.5, 12))
ax.set_xlim(0, 100); ax.set_ylim(0, 122); ax.axis('off')

def caja(x, y, w, h, texto, destacar=False, lateral=False):
    fc = '#fdf2f4' if destacar else ('#f8fafc' if lateral else '#ffffff')
    ec = ROSE if destacar else SLATE
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.9",
                 linewidth=1.6 if destacar else 1.1, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w/2, y + h/2, texto, ha='center', va='center', zorder=3,
            fontsize=10 if not lateral else 9.2, color=INK,
            weight='bold' if destacar else 'normal', linespacing=1.5)

def flecha(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=15,
                 linewidth=1.3, color=SLATE, zorder=1))

def fase(y, txt):
    ax.text(1.5, y, txt, rotation=90, ha='center', va='center', fontsize=10.5,
            weight='bold', color=ROSE)

fase(107, 'IDENTIFICACIÓN'); fase(72, 'CRIBADO'); fase(30, 'INCLUSIÓN')

caja(8, 100, 50, 14, 'Registros identificados en bases de datos\n( n = 724 )\n\nScopus: n = 586      Web of Science: n = 138')
caja(66, 100, 30, 14, 'Sin restricción de fecha\nen la búsqueda inicial\n(literatura desde 2003)', lateral=True)

flecha(33, 100, 33, 90)
caja(8, 76, 50, 14, 'Registros tras depuración\ny cribado preliminar\n( n = 149 )')
caja(66, 68, 30, 30, 'Registros excluidos ( n = 575 )\n\nDuplicados: n = 171\n(127 entre bases, 44 internos)\nTipología no primaria (CE-4): n = 385\nIdioma no contemplado (CI-4): n = 5\nLit. secundaria / metadata\nincompleta: n = 14',
     lateral=True)
flecha(58, 83, 66, 83)

flecha(33, 76, 33, 66)
caja(8, 52, 50, 14, 'Registros evaluados por\ntítulo y resumen\n( n = 149 )')
caja(66, 45, 30, 21, 'Registros excluidos ( n = 69 )\n\nDesviación temática, IA\ngeneralizada o simulación sin\nrestricción física real\n(incumple CI-2 / activa CE-1)', lateral=True)
flecha(58, 59, 66, 59)

flecha(33, 52, 33, 42)
caja(8, 24, 50, 18, 'Estudios incluidos en la\nrevisión sistemática\n( n = 80 )\n\n2024: n = 9    2025: n = 31    2026: n = 40', destacar=True)

caja(8, 4, 88, 14, 'De los 80 estudios incluidos, 18 (22 %) declaran una plataforma de hardware perimetral concreta.\n'
     'Los 62 restantes emplean descriptores genéricos o validan sobre GPU fuera del alcance del Edge Computing.\n'
     '36 estudios (45 %) fueron codificados a partir de resumen y metadatos indexados.', lateral=True)

plt.tight_layout()
plt.savefig('figuras/image8.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print('[ok] image8.png (PRISMA)')
