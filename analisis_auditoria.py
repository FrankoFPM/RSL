#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_auditoria.py
=====================
Genera las tablas cuantitativas del manuscrito (RQ3, RQ4 y sintesis
bibliometrica) y ejecuta las verificaciones de consistencia del corpus.

Complementa a `process_rsl.py`, que produce las figuras.

Salidas (carpeta ./tablas):
    tabla_rq3.tex             Plataformas de validacion (RQ3)
    tabla_bibliometrica.tex   Sintesis bibliometrica consolidada (RQ1)
    tabla_lotka.tex           Productividad de autores vs. modelo de Lotka
    reporte_consistencia.txt  Verificacion PRISMA + acceso a texto completo

Uso:
    python analisis_auditoria.py
"""
import os
import re
import unicodedata
from collections import Counter

import pandas as pd

EXCEL = 'ARTICULOS_UNIFICADOS_CRIBADO.xlsx'
HOJA_FINAL = 'SELECCIONADOS-FINAL'
OUT = 'tablas'

# --------------------------------------------------------------------
# Normalizacion de denominaciones de revista
# --------------------------------------------------------------------
_ABBR = {
    r'^IEEE TRANS\.? ': 'IEEE TRANSACTIONS ON ',
    r'\bMOB\.? COMPUT\.?$': 'MOBILE COMPUTING',
    r'\bCONSUM\.? ELECTRON\.?$': 'CONSUMER ELECTRONICS',
    r'\bCIRCUITS SYST\.? VIDEO TECHNOL\.?$': 'CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY',
    r'\bPARALLEL DISTRIB\.? SYST\.?$': 'PARALLEL AND DISTRIBUTED SYSTEMS',
    r'\bINTELL\.? TRANSP\.? SYST\.?$': 'INTELLIGENT TRANSPORTATION SYSTEMS',
}


def normalizar_revista(s):
    """Colapsa variantes abreviadas al nombre canonico de la revista."""
    if pd.isna(s):
        return 'DESCONOCIDA'
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    s = re.sub(r'\s+', ' ', s.upper().strip()).replace('&', ' AND ')
    for pat, rep in _ABBR.items():
        s = re.sub(pat, rep, s)
    for pat, rep in [(r'\bAUTON\.? INTELL\.? SYST\.?\b', 'AUTONOMOUS INTELLIGENT SYSTEMS'),
                     (r'\bNAT\.? COMMUN\.?\b', 'NATURE COMMUNICATIONS'),
                     (r'\bCOMPUT\.?\b', 'COMPUTING'), (r'\bSYST\.?\b', 'SYSTEMS'),
                     (r'\bAPPL\.?\b', 'APPLICATIONS'), (r'\bTECHNOL\.?\b', 'TECHNOLOGY')]:
        s = re.sub(pat, rep, s)
    return re.sub(r'\s+', ' ', re.sub(r'[\.,]+$', '', s)).strip()


# --------------------------------------------------------------------
# RQ3 - clasificacion de plataformas declaradas en el Anexo A
# --------------------------------------------------------------------
REGLAS_HW = [
    ("FPGA", r"FPGA|ALVEO|XCU280|U250|XILINX"),
    ("NVIDIA Jetson", r"JETSON"),
    ("Raspberry Pi / SBC", r"RASPBERRY|RADXA|ROCK 5B|SINGLE-BOARD"),
    ("NPU / ASIC / acelerador dedicado", r"\bNPU\b|ASIC|CGRA|AI PROCESSOR"),
    ("SoC movil comercial", r"SNAPDRAGON|APPLE M1|SMARTPHONE"),
    ("CPU ARM / RISC-V", r"\bARM\b|RISC-V"),
    ("GPU escritorio/servidor (fuera de alcance Edge)",
     r"A100|RTX ?40|CONSUMER-GRADE GPU|HIGH-END GPU"),
]
PLATAFORMAS_EDGE = {r[0] for r in REGLAS_HW[:6]}


def clasificar_hardware(hw_por_estudio):
    """Mapea el texto de hardware de cada estudio a categorias de plataforma."""
    return {k: [n for n, p in REGLAS_HW if re.search(p, str(v).upper())]
            for k, v in hw_por_estudio.items()}


def lotka_teorico(k, tope=20):
    return (1 / k ** 2) / sum(1 / i ** 2 for i in range(1, tope + 1)) * 100


def zonas_bradford(conteos, n_total):
    """Particiona las fuentes en tres zonas de Bradford de ~n/3 articulos."""
    objetivo, zonas = n_total / 3, []
    z, n_src, n_art = 1, 0, 0
    for n in conteos:
        n_src, n_art = n_src + 1, n_art + n
        if n_art >= objetivo and z < 3:
            zonas.append((z, n_src, n_art))
            z, n_src, n_art = z + 1, 0, 0
    zonas.append((z, n_src, n_art))
    return zonas


def main():
    os.makedirs(OUT, exist_ok=True)
    xl = pd.ExcelFile(EXCEL)
    fin = pd.read_excel(EXCEL, sheet_name=HOJA_FINAL)
    n = len(fin)
    rep = [f"Corpus: {n} estudios (hoja '{HOJA_FINAL}')", ""]

    # -- consistencia PRISMA -----------------------------------------
    rep.append("== RECONCILIACION PRISMA ==")
    for hoja, esperado, etiqueta in [('ARTICULOS SCOPUS', 586, 'Scopus'),
                                     ('ARTICULOS WoS', 138, 'WoS'),
                                     ('SELECCIONADOS', 149, 'Tras cribado'),
                                     (HOJA_FINAL, 73, 'Corpus final')]:
        if hoja in xl.sheet_names:
            real = len(pd.read_excel(EXCEL, sheet_name=hoja))
            estado = 'OK' if real == esperado else f'DISCREPANCIA (esperado {esperado})'
            rep.append(f"  {etiqueta:14s}: {real:4d}  {estado}")

    # -- acceso a texto completo -------------------------------------
    if 'VERIFICAR-ACCESS' in xl.sheet_names:
        va = pd.read_excel(EXCEL, sheet_name='VERIFICAR-ACCESS')
        if '¿FREE ACCESS?' in va.columns:
            sin = (va['¿FREE ACCESS?'] == 'NO').sum()
            rep += ["", "== ACCESO A TEXTO COMPLETO ==",
                    f"  Sin acceso: {sin}/{len(va)} ({sin/len(va)*100:.0f}%)"]

    # -- bibliometria -------------------------------------------------
    fin['SO_NORM'] = fin['SO'].apply(normalizar_revista)
    vc = fin['SO_NORM'].value_counts()
    zonas = zonas_bradford(vc.values, n)
    mult = [round(zonas[i + 1][1] / zonas[i][1], 2) for i in range(len(zonas) - 1)]
    unicas = int((vc == 1).sum())

    autores = Counter()
    for fila in fin['AU'].dropna():
        for a in str(fila).split(';'):
            a = a.strip().upper().rstrip('.')
            if a:
                autores[a] += 1
    dist, n_au = Counter(autores.values()), len(autores)
    sin_citas = int((fin['TC'].fillna(0) == 0).sum())
    anios = fin['PY'].fillna(0).astype(int).value_counts().sort_index()

    rep += ["", "== BIBLIOMETRIA ==",
            f"  Fuentes normalizadas: {len(vc)}",
            f"  Zonas Bradford: " + "; ".join(f"Z{z}={s} rev/{a} art" for z, s, a in zonas),
            f"  Multiplicadores: {mult}  -> Bradford "
            + ("NO se cumple" if max(mult) / max(min(mult), .01) > 2 else "se aproxima"),
            f"  Fuentes con 1 articulo: {unicas}/{len(vc)} ({unicas/len(vc)*100:.0f}%)",
            f"  Autores unicos: {n_au}; con 1 articulo: {dist[1]} ({dist[1]/n_au*100:.1f}%)",
            f"  Estudios con 0 citas: {sin_citas}/{n} ({sin_citas/n*100:.0f}%)"]

    # -- tabla bibliometrica -----------------------------------------
    nucleo = "; ".join(f"\\emph{{{k.title()}}} ({v})" for k, v in vc.head(3).items())
    filas = [
        ("Evolución de la producción", "; ".join(f"{a}: {c}" for a, c in anios.items())),
        ("Impacto de citación", f"{sin_citas} de {n} estudios ({sin_citas/n*100:.0f}\\%) registran cero citas. "
                                "La métrica no es interpretable en una ventana de tres años y se reporta como dato descriptivo."),
        ("Fuentes de publicación", f"{len(vc)} revistas distintas tras normalización de denominaciones abreviadas."),
        ("Zonas de Bradford", "; ".join(f"Zona {z}: {s} revistas / {a} artículos" for z, s, a in zonas) + "."),
        ("Ajuste a la Ley de Bradford", f"\\textbf{{No se cumple.}} Los multiplicadores entre zonas son {mult[0]} y {mult[1]}, "
                                        "lejos de la constancia que exige la ley."),
        ("Dispersión de fuentes", f"{unicas} de {len(vc)} revistas ({unicas/len(vc)*100:.0f}\\%) aportan un único artículo; "
                                  f"esas fuentes concentran el {unicas/n*100:.0f}\\% del corpus."),
        ("Núcleo editorial", nucleo + "."),
        ("Autores", f"{n_au} autores únicos: {dist[1]} con un artículo ({dist[1]/n_au*100:.1f}\\%), "
                    + ", ".join(f"{dist[k]} con {k}" for k in sorted(dist) if k > 1) + "."),
        ("Ajuste a la Ley de Lotka", f"La proporción de autores con un solo artículo ({dist[1]/n_au*100:.1f}\\%) excede "
                                     f"ampliamente el {lotka_teorico(1):.1f}\\% teórico. La ventana de tres años impide "
                                     "distinguir transitoriedad real de truncamiento del período de observación."),
    ]
    t = [r"\begin{table}[H]", r"\centering",
         rf"\caption{{Síntesis bibliométrica consolidada del corpus (n={n}, 2024--2026).}}",
         r"\label{tab:bibliometria}", r"\small", r"\renewcommand{\arraystretch}{1.35}",
         r"\begin{tabular}{|>{\raggedright\arraybackslash}m{0.30\linewidth}|>{\raggedright\arraybackslash}m{0.60\linewidth}|}",
         r"\hline", r"\textbf{Dimensión} & \textbf{Resultado} \\", r"\hline"]
    for a, b in filas:
        t += [f"{a} & {b} \\\\", r"\hline"]
    t += [r"\end{tabular}", r"\end{table}"]
    open(f'{OUT}/tabla_bibliometrica.tex', 'w', encoding='utf-8').write("\n".join(t))

    # -- tabla de Lotka ----------------------------------------------
    t = [r"\begin{table}[H]", r"\centering",
         r"\caption{Distribución de la productividad de autores frente al modelo teórico de Lotka.}",
         r"\label{tab:lotka}", r"\small", r"\renewcommand{\arraystretch}{1.3}",
         r"\begin{tabular}{|c|c|c|c|}", r"\hline",
         r"\textbf{Artículos por autor} & \textbf{Autores} & \textbf{\% observado} & \textbf{\% teórico (Lotka)} \\",
         r"\hline"]
    for k in sorted(dist):
        t += [f"{k} & {dist[k]} & {dist[k]/n_au*100:.1f}\\% & {lotka_teorico(k):.1f}\\% \\\\", r"\hline"]
    t += [rf"\multicolumn{{4}}{{|l|}}{{\footnotesize Total: {n_au} autores únicos sobre {n} estudios primarios.}} \\",
          r"\hline", r"\end{tabular}", r"\end{table}"]
    open(f'{OUT}/tabla_lotka.tex', 'w', encoding='utf-8').write("\n".join(t))

    # -- RQ3 ----------------------------------------------------------
    try:
        from anexoA_hardware import HARDWARE
    except ImportError:
        rep += ["", "[aviso] falta anexoA_hardware.py; se omite la tabla RQ3."]
        HARDWARE = None

    if HARDWARE:
        cat = clasificar_hardware(dict(HARDWARE))
        c = Counter(x for v in cat.values() for x in v)
        con_edge = [k for k, v in cat.items() if set(v) & PLATAFORMAS_EDGE]
        sin_plat = [k for k, v in cat.items() if not v]
        total = len(cat)

        t = [r"\begin{table}[H]", r"\centering",
             rf"\caption{{Plataformas de validación empírica declaradas en el corpus (n={total}). "
             r"Un estudio puede declarar más de una plataforma.}",
             r"\label{tab:rq3_plataformas}", r"\small", r"\renewcommand{\arraystretch}{1.3}",
             r"\begin{tabular}{|>{\raggedright\arraybackslash}m{0.44\linewidth}|c|c|}", r"\hline",
             r"\textbf{Plataforma de validación} & \textbf{Estudios} & \textbf{\% del corpus} \\", r"\hline"]
        for nombre, _ in REGLAS_HW:
            etq = nombre.replace("SoC movil comercial", "SoC móvil comercial (Snapdragon, Apple M1)")
            etq = etq.replace("(fuera de alcance Edge)", r"\textit{(fuera de alcance Edge)}")
            t += [f"{etq} & {c[nombre]} & {c[nombre]/total*100:.1f}\\% \\\\", r"\hline"]
        t += [rf"\textbf{{Sin plataforma física identificable}} & \textbf{{{len(sin_plat)}}} & "
              rf"\textbf{{{len(sin_plat)/total*100:.1f}\%}} \\", r"\hline",
              r"\multicolumn{3}{|l|}{\footnotesize Estudios con validación verificable en hardware "
              rf"\emph{{Edge}} concreto: \textbf{{{len(con_edge)}/{total} ({len(con_edge)/total*100:.0f}\%)}}}} \\",
              r"\hline", r"\end{tabular}", r"\end{table}"]
        open(f'{OUT}/tabla_rq3.tex', 'w', encoding='utf-8').write("\n".join(t))

        rep += ["", "== RQ3 - PLATAFORMAS ==",
                f"  Con hardware Edge concreto : {len(con_edge)}/{total} ({len(con_edge)/total*100:.0f}%)",
                f"  Sin plataforma identificable: {len(sin_plat)}/{total} ({len(sin_plat)/total*100:.0f}%)",
                f"  FPGA={c['FPGA']}  Jetson={c['NVIDIA Jetson']}"]

    open(f'{OUT}/reporte_consistencia.txt', 'w', encoding='utf-8').write("\n".join(rep))
    print("\n".join(rep))
    print(f"\nTablas escritas en ./{OUT}/")


if __name__ == '__main__':
    main()
