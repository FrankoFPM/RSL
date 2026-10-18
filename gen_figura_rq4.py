# -*- coding: utf-8 -*-
"""Figura 3 (RQ4): familia de optimización x plataforma de hardware declarada.

Lee codificacion_rq4.csv (una fila por estudio del corpus, n=80). Para cambiar la
codificación, edite el CSV y vuelva a ejecutar: python gen_figura_rq4.py
Uso: python gen_figura_rq4.py [en|es]   (en por defecto)
Salida: figuras_en/ (en) o figuras/ (es) grafico_rq4_matriz.pdf (y .png de vista previa).
"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, ROSE, SLATE, INK, GRID = '#343b4a', '#f43f5e', '#94a3b8', '#1e293b', '#cbd5e1'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans', 'Arial'],
                     'font.size': 8.5, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'savefig.dpi': 600,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03, 'savefig.facecolor': 'white'})

import sys
LANG = sys.argv[1] if len(sys.argv) > 1 else 'en'   # 'en' (por defecto, como el resto de figuras) o 'es'
T = {
 'en': {'fam': ['Quanti-\nzation', 'Pruning /\nsparsity', 'Low-rank\n(LoRA/PEFT)', 'Distil-\nlation'],
        'plat': ['Jetson', 'ARM SoC / RPi', 'Server FPGA', 'Desktop/server GPU', 'No edge platform'],
        'edge': 'Edge (Group A) \u2191'},
 'es': {'fam': ['Cuanti-\nzación', 'Poda /\nesparsidad', 'Rango bajo\n(LoRA/PEFT)', 'Destila-\nción'],
        'plat': ['Jetson', 'SoC ARM / RPi', 'FPGA de servidor', 'GPU de escritorio/servidor', 'Sin plataforma perimetral'],
        'edge': 'Edge (Grupo A) \u2191'},
}[LANG]
OUT = os.path.join(HERE, 'figuras_en' if LANG == 'en' else 'figuras'); os.makedirs(OUT, exist_ok=True)
FAM = list(zip(['cuantizacion', 'poda', 'lora_peft', 'destilacion'], T['fam']))
PLAT = ['Jetson', 'SoC ARM / RPi / NPU', 'FPGA de servidor', 'GPU de escritorio/servidor', 'Sin plataforma perimetral']
EDGE = {'Jetson', 'SoC ARM / RPi / NPU'}

rows = list(csv.DictReader(open(os.path.join(HERE, 'codificacion_rq4.csv'), encoding='utf8')))
M = {p: {f: 0 for f, _ in FAM} for p in PLAT}
for r in rows:
    for f, _ in FAM:
        M[r['plataforma']][f] += int(r[f])

fig, ax = plt.subplots(figsize=(4.0, 2.9))
nP = len(PLAT)
for xi, (f, _) in enumerate(FAM):
    for pi, p in enumerate(PLAT):
        v = M[p][f]
        if not v:
            continue
        y = nP - 1 - pi
        col = NAVY if p in EDGE else SLATE
        ax.scatter(xi, y, s=60 + v * 32, color=col, edgecolors='white', linewidths=0.6, zorder=3)
        ax.text(xi, y, str(v), ha='center', va='center', fontsize=7.3, weight='bold', color='white', zorder=4)
ax.axhline(nP - 2.5, color=ROSE, ls='--', lw=0.8)
ax.text(len(FAM) - 0.45, nP - 2.45, T['edge'], ha='right', va='bottom', fontsize=6.6, style='italic', color=ROSE)
ax.set_xticks(range(len(FAM))); ax.set_xticklabels([l for _, l in FAM], fontsize=7.2, color=INK)
ax.set_yticks(range(nP)); ax.set_yticklabels(T['plat'][::-1], fontsize=7.2, color=INK)
ax.set_xlim(-0.55, len(FAM) - 0.45); ax.set_ylim(-0.6, nP - 0.4)
ax.grid(True, ls='--', alpha=0.35, color=GRID, zorder=0); ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout()
for ext in ('pdf', 'png'):
    fig.savefig(os.path.join(OUT, f'grafico_rq4_matriz.{ext}'))
for p in PLAT:
    print(f'{p:28s}', ' '.join(f'{M[p][f]:3d}' for f, _ in FAM))
print('totales', {f: sum(M[p][f] for p in PLAT) for f, _ in FAM})
