"""Generate the manuscript figures (English, single-column FGCS layout).

Each figure is drawn at its final printed width (one column, 3.5 in), so the
font sizes set here are the sizes that appear in the PDF.

Outputs (outputs/figures/, vector PDF + 600-dpi PNG):
    fig1_prisma_flow           PRISMA 2020 flow diagram (counts from prisma_flow.py)
    fig2_thematic_map          Strategic thematic map of author keywords
    fig3_rq4_matrix            RQ4: optimisation family x hardware platform
    figS1_technique_frequency  RQ1: studies per optimisation family (supplementary)
    + thematic_map_data.csv    centrality/density values behind fig2

Usage: python scripts/generate_charts.py
"""
from __future__ import annotations

from collections import Counter

import matplotlib

matplotlib.use("Agg")  # headless backend: no display needed
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import prisma_flow
from common import (EDGE_PLATFORMS, FAMILIES, FIGURES, PLATFORMS, ensure_output_dirs,
                    load_corpus, split_keywords)

COL_W = 3.5  # inches: one column of elsarticle 3p twocolumn
NAVY, ROSE, SLATE, INK, GRID = "#343b4a", "#f43f5e", "#94a3b8", "#1e293b", "#cbd5e1"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 8.5,
    "axes.labelsize": 9,
    "axes.labelweight": "bold",
    "axes.labelcolor": INK,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "xtick.color": "#475569",
    "ytick.color": "#475569",
    "text.color": INK,
    "pdf.fonttype": 42,  # embed TrueType fonts (Elsevier requirement), not Type 3
    "ps.fonttype": 42,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
    "savefig.facecolor": "white",
})


def save(fig, stem: str) -> None:
    for ext in ("pdf", "png"):
        fig.savefig(FIGURES / f"{stem}.{ext}")
    plt.close(fig)
    print(f"[ok] outputs/figures/{stem}.pdf|png")


# =========================================================================== Fig. 1
def prisma_figure() -> None:
    """PRISMA 2020 diagram in the style of the official template."""
    c = prisma_flow.compute()
    removed_before = c["identified"] - c["screened"]
    corpus = load_corpus()
    yr = corpus["year"].value_counts().sort_index()
    group_a = int(corpus["edge_group_a"].sum())

    W = COL_W * 72  # work in points so box heights follow the text they hold
    FS, FS_S, LS, PAD, GAP = 7.0, 6.4, 1.15, 4, 9
    PH_X, PH_W = 0, 11            # phase band
    MX, MW = 16, 108              # main column
    SX = MX + MW + 10             # side column
    SW = W - SX - 0.5
    ORANGE, BLUE, BLUE_E, LINE = "#F2A51A", "#C9DAF0", "#7A9CC8", "#222222"

    def h_of(t, fs):
        return len(t.split("\n")) * fs * LS * 1.12 + 2 * PAD

    rows = [
        ("Identification",
         f"Records identified from\ndatabases (n = {c['identified']})\nScopus (n = {c['scopus']})\n"
         f"Web of Science (n = {c['wos']})\nNo date restriction",
         f"Records removed before screening\n(n = {removed_before})\n"
         f"Duplicates (n = {c['duplicates']}; {c['duplicates_cross']} cross-\n"
         f"database, {c['duplicates_internal']} internal)\n"
         f"Non-primary type, EC-4 (n = {c['non_primary']})\nLanguage, IC-4 (n = {c['language']})\n"
         f"Secondary literature or incomplete\nmetadata (n = {c['secondary_or_incomplete']})"),
        ("Screening",
         f"Records screened by\ntitle and abstract\n(n = {c['screened']})",
         f"Records excluded (n = {c['excluded_title_abstract']})\nOff-topic, general AI, or no real\n"
         "physical constraint (IC-2 / EC-1)"),
        ("Screening",
         f"Full-text articles\nassessed for eligibility\n(n = {c['fulltext_assessed']})",
         f"Excluded at full text (n = {c['excluded_fulltext']})\nDo not optimize or evaluate\nan LLM"),
        ("Included",
         f"Studies included in the\nreview (n = {c['included']})\n"
         + " | ".join(f"{y}: n = {v}" for y, v in list(yr.items())[:2]) + "\n"
         + " | ".join(f"{y}: n = {v}" for y, v in list(yr.items())[2:]),
         None),
    ]
    note = (f"{group_a} of the {c['included']} included studies ({group_a / c['included'] * 100:.0f}%) "
            "report a concrete edge platform\nwith physical metrics. The remaining "
            f"{c['included'] - group_a} use generic descriptors or\n"
            "validate on server GPUs or FPGAs outside the edge scope.")

    HEAD = 16
    y = HEAD + GAP
    lay = []
    for ph, mt, st in rows:
        hm = h_of(mt, FS)
        hs = h_of(st, FS_S) if st else 0
        rh = max(hm, hs)
        lay.append((ph, mt, st, y, rh, hm, hs))
        y += rh + GAP
    hn = h_of(note, FS_S)
    H = y + hn + 1

    fig = plt.figure(figsize=(COL_W, H / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

    def box(x, yt, w, h, t, fs=FS, fc="white", ec=LINE, color=INK, r=0):
        ax.add_patch(FancyBboxPatch((x, yt), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    linewidth=0.7, edgecolor=ec, facecolor=fc, zorder=2))
        ax.text(x + w / 2, yt + h / 2, t, ha="center", va="center", fontsize=fs, color=color,
                linespacing=LS, zorder=3)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6,
                                     linewidth=0.7, color=LINE, zorder=1, shrinkA=0, shrinkB=0))

    box(MX, 0, W - MX - 0.5, HEAD, "Identification of studies via databases and registers",
        fs=7.2, fc=ORANGE, ec=ORANGE, color="white", r=3)
    prev, phases = None, {}
    for ph, mt, st, yt, rh, hm, hs in lay:
        ym = yt + (rh - hm) / 2
        box(MX, ym, MW, hm, mt)
        if st:
            box(SX, yt + (rh - hs) / 2, SW, hs, st, fs=FS_S)
            arrow(MX + MW, ym + hm / 2, SX, ym + hm / 2)
        if prev is not None:
            arrow(MX + MW / 2, prev, MX + MW / 2, ym)
        prev = ym + hm
        p0, p1 = phases.get(ph, (yt, yt + rh))
        phases[ph] = (min(p0, yt), max(p1, yt + rh))
    box(MX, y, W - MX - 0.5, hn, note, fs=FS_S)
    for ph, (p0, p1) in phases.items():
        ax.add_patch(FancyBboxPatch((PH_X, p0), PH_W, p1 - p0, boxstyle="round,pad=0,rounding_size=3",
                                    linewidth=0.6, edgecolor=BLUE_E, facecolor=BLUE, zorder=1))
        ax.text(PH_X + PH_W / 2, (p0 + p1) / 2, ph, rotation=90, ha="center", va="center",
                fontsize=6.6, color=INK, weight="bold")
    for ext in ("pdf", "png"):
        fig.savefig(FIGURES / f"fig1_prisma_flow.{ext}", dpi=1100 if ext == "png" else None,
                    bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    print("[ok] outputs/figures/fig1_prisma_flow.pdf|png")


# =========================================================================== Fig. 2
def thematic_map() -> None:
    """Callon-style strategic map: centrality vs. density of the top-25 author keywords."""
    df = load_corpus()
    kw_lists = [split_keywords(s) for s in df["author_keywords"]]
    # Frequency ranking. Ties are broken by first appearance in corpus_73.csv
    # (Counter keeps insertion order and sorted() is stable), so the selected
    # top-25 set is identical across pandas versions.
    counts = Counter(k for ks in kw_lists for k in ks)
    freq = dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    # Co-occurrence network among the 25 most frequent keywords.
    G = nx.Graph()
    for kw, f in list(freq.items())[:25]:
        G.add_node(kw, size=int(f))
    for ks in kw_lists:
        ks = [k for k in set(ks) if k in G]
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                w = G[ks[i]][ks[j]]["weight"] + 1 if G.has_edge(ks[i], ks[j]) else 1
                G.add_edge(ks[i], ks[j], weight=w)
    G.remove_nodes_from(list(nx.isolates(G)))

    # Centrality = total link strength; density = mean link weight among neighbours.
    rows = []
    for node in G.nodes:
        nb = list(G.neighbors(node))
        cen = sum(G[node][m]["weight"] for m in nb)
        e = G.subgraph(nb).edges(data=True) if len(nb) >= 2 else []
        den = sum(d.get("weight", 1.0) for *_, d in e) / len(e) if len(e) else 0.0
        rows.append({"Keyword": node, "Centrality": float(cen), "Density": float(den),
                     "Frequency": G.nodes[node]["size"]})
    th = pd.DataFrame(rows).sort_values("Frequency", ascending=False)
    th.to_csv(FIGURES / "thematic_map_data.csv", index=False)

    fig, ax = plt.subplots(figsize=(COL_W, 3.2))
    ax.scatter(th["Centrality"], th["Density"], s=th["Frequency"] * 4.5, color=ROSE, alpha=0.75,
               edgecolors="white", linewidths=0.6, zorder=3)
    med_c, med_d = float(th["Centrality"].median()), float(th["Density"].median())
    ax.axvline(med_c, color=SLATE, ls="--", lw=0.9, alpha=0.8, zorder=1)
    ax.axhline(med_d, color=SLATE, ls="--", lw=0.9, alpha=0.8, zorder=1)
    ax.margins(x=0.2, y=0.2)
    xl, yl = ax.get_xlim(), ax.get_ylim()
    for x, y, txt, ha, va, col in [
        (xl[1] - (xl[1] - med_c) * .03, yl[1] - (yl[1] - med_d) * .04, "MOTOR\nTHEMES", "right", "top", "#16a34a"),
        (xl[0] + (med_c - xl[0]) * .05, yl[1] - (yl[1] - med_d) * .04, "NICHE\nTHEMES", "left", "top", "#4f46e5"),
        (xl[0] + (med_c - xl[0]) * .05, yl[0] + (med_d - yl[0]) * .04, "EMERGING OR\nDECLINING", "left", "bottom", "#dc2626"),
        (xl[1] - (xl[1] - med_c) * .03, yl[0] + (med_d - yl[0]) * .04, "BASIC AND\nTRANSVERSAL", "right", "bottom", "#ca8a04"),
    ]:
        ax.text(x, y, txt, ha=ha, va=va, fontsize=6.8, weight="bold", color=col)

    # Labels for the 10 most frequent keywords. Positions (data coordinates) were
    # set by hand so that leader lines do not cross the dense central cluster;
    # any other keyword falls back to a label just right of its bubble.
    POS = {
        "Large language models": (113, 3.75, "center", "bottom", "Large language\nmodels"),
        "Computational modeling": (86, 2.55, "center", "bottom", "Computational\nmodeling"),
        "Quantization": (70, 2.13, "center", "top", None),
        "Knowledge distillation": (21, 3.97, "left", "center", None),
        "Model compression": (36, 3.47, "left", "center", None),
        "Accuracy": (52, 3.27, "left", "center", None),
        "Training": (57, 3.02, "left", "center", None),
        "Adaptation models": (41, 2.42, "center", "top", "Adaptation\nmodels"),
        "Edge computing": (-5, 3.05, "center", "top", "Edge\ncomputing"),
        "Optimization": (22, 2.62, "center", "top", None),
    }
    for _, r in th.nlargest(10, "Frequency").iterrows():
        k, cx, cy = r["Keyword"], r["Centrality"], r["Density"]
        tx, ty, ha, va, txt = POS.get(k, (cx + 3, cy, "left", "center", None))
        far = abs(tx - cx) > 3 or abs(ty - cy) > 0.08
        ax.annotate(txt or k, (cx, cy), xytext=(tx, ty), ha=ha, va=va, fontsize=7,
                    weight="bold", color=NAVY, zorder=5, linespacing=1.0,
                    arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.5, shrinkA=1, shrinkB=3) if far else None)
    ax.set_xlim(xl); ax.set_ylim(yl)
    ax.set_xlabel("Centrality (external relevance)", labelpad=4)
    ax.set_ylabel("Density (internal cohesion)", labelpad=4)
    ax.grid(True, ls="--", alpha=0.25, color=GRID)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout()
    save(fig, "fig2_thematic_map")


# =========================================================================== Fig. 3
def rq4_matrix() -> None:
    """Bubble matrix: optimisation family (x) vs. declared hardware platform (y)."""
    df = load_corpus()
    labels_x = ["Quanti-\nzation", "Pruning /\nsparsity", "Low-rank\n(LoRA/PEFT)", "Distil-\nlation"]
    labels_y = ["Jetson", "ARM SoC / RPi", "Server FPGA", "Desktop/server GPU", "No edge platform"]
    M = df.groupby("platform_class")[list(FAMILIES)].sum().reindex(PLATFORMS, fill_value=0)

    fig, ax = plt.subplots(figsize=(4.0, 2.9))
    nP = len(PLATFORMS)
    for xi, fam in enumerate(FAMILIES):
        for pi, plat in enumerate(PLATFORMS):
            v = int(M.loc[plat, fam])
            if not v:
                continue
            yy = nP - 1 - pi
            ax.scatter(xi, yy, s=60 + v * 32, color=NAVY if plat in EDGE_PLATFORMS else SLATE,
                       edgecolors="white", linewidths=0.6, zorder=3)
            ax.text(xi, yy, str(v), ha="center", va="center", fontsize=7.3, weight="bold",
                    color="white", zorder=4)
    ax.axhline(nP - 2.5, color=ROSE, ls="--", lw=0.8)  # separates edge (Group A) rows
    ax.text(len(FAMILIES) - 0.45, nP - 2.45, "Edge (Group A) ↑", ha="right", va="bottom",
            fontsize=6.6, style="italic", color=ROSE)
    ax.set_xticks(range(len(FAMILIES))); ax.set_xticklabels(labels_x, fontsize=7.2, color=INK)
    ax.set_yticks(range(nP)); ax.set_yticklabels(labels_y[::-1], fontsize=7.2, color=INK)
    ax.set_xlim(-0.55, len(FAMILIES) - 0.45); ax.set_ylim(-0.6, nP - 0.4)
    ax.set_xlabel(""); ax.grid(True, ls="--", alpha=0.35, color=GRID, zorder=0)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    save(fig, "fig3_rq4_matrix")


# =========================================================================== Fig. S1
def technique_frequency() -> None:
    """Horizontal bars: number of studies per optimisation family (RQ1)."""
    df = load_corpus()
    n = len(df)
    order = ["low_rank_peft", "distillation", "pruning_sparsity", "quantization"]  # bottom -> top
    names = {"quantization": "Quantization", "pruning_sparsity": "Pruning and\nsparsity induction",
             "distillation": "Knowledge\ndistillation", "low_rank_peft": "Low-rank (LoRA/PEFT\nand factorization)"}
    vals = [int(df[c].sum()) for c in order]

    fig, ax = plt.subplots(figsize=(COL_W, 2.35))
    bars = ax.barh(range(len(order)), vals, height=0.62, color=NAVY, zorder=3)
    bars[-1].set_color(ROSE)  # highlight the most frequent family
    for i, v in enumerate(vals):
        ax.text(v + 0.8, i, f"{v} ({v / n * 100:.0f}%)", va="center", ha="left",
                fontsize=8.5, weight="bold", color=INK)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([names[c] for c in order], fontsize=8.5, color=INK)
    ax.set_xlabel(f"Number of studies (n = {n})", labelpad=5)
    ax.set_xlim(0, 60); ax.set_xticks(range(0, 51, 10))
    ax.tick_params(axis="x", colors=SLATE); ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", linestyle="--", alpha=.3, color=SLATE, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(SLATE)
    fig.tight_layout()
    save(fig, "figS1_technique_frequency")


def main() -> None:
    ensure_output_dirs()
    prisma_figure()
    thematic_map()
    rq4_matrix()
    technique_frequency()


if __name__ == "__main__":
    main()
