"""Descriptive statistics of the 73-study corpus (RQ1, RQ2, RQ4 counts,
Bradford, Lotka and quality-assessment summaries).

Every number quoted in the "Descriptive characterisation of the corpus" and in
the RQ1/RQ2/RQ4 tables of the manuscript is recomputed here from
``data/corpus_73.csv`` and ``data/quality_assessment.csv``.

Outputs (outputs/tables/, each as .csv and .md):
    corpus_summary              headline indicators
    annual_distribution         studies per publication year
    technique_frequency         RQ1: studies per optimisation family
    platform_distribution       RQ2: studies per validation platform class
    technique_platform_matrix   RQ4: family x platform cross-tabulation
    journals                    studies per (normalised) journal
    bradford_zones              Bradford zones and multipliers
    lotka                       author productivity vs. Lotka's law
    quality_summary             QA1-QA3 score distribution

Usage: python scripts/bibliometrics.py
"""
from __future__ import annotations

from collections import Counter

import pandas as pd

from common import (FAMILIES, PLATFORMS, load_corpus, load_quality, normalize_journal,
                    write_table)

# Headline figures reported in the manuscript; the script fails if they drift.
EXPECTED = {
    "studies": 73, "journals": 54, "single_article_journals": 47,
    "unique_authors": 371, "single_article_authors": 355, "uncited_studies": 40,
    "edge_group_a": 9, "no_edge_platform": 53,
    "quantization": 42, "pruning_sparsity": 19, "low_rank_peft": 15, "distillation": 14,
    "qa1_full": 17, "qa1_partial": 54, "qa1_none": 2,
}


def lotka_expected(k: int, kmax: int = 20) -> float:
    """Share (%) of authors with k papers under Lotka's inverse-square law."""
    return (1 / k ** 2) / sum(1 / i ** 2 for i in range(1, kmax + 1)) * 100


def bradford_zones(counts, n_articles: int):
    """Split journals (sorted by productivity) into three zones of ~n/3 articles."""
    target, zones = n_articles / 3, []
    z, n_src, n_art = 1, 0, 0
    for n in counts:
        n_src, n_art = n_src + 1, n_art + n
        if n_art >= target and z < 3:
            zones.append((z, n_src, n_art))
            z, n_src, n_art = z + 1, 0, 0
    zones.append((z, n_src, n_art))
    return zones


def main() -> None:
    df = load_corpus()
    qa = load_quality()
    n = len(df)
    got = {"studies": n}

    # ---- publication years
    years = df["year"].value_counts().sort_index()
    write_table(pd.DataFrame({"year": years.index, "studies": years.values}), "annual_distribution")

    # ---- RQ1: optimisation families (a study can use more than one)
    fam = pd.DataFrame([{"family": label, "studies": int(df[col].sum()),
                         "percent_of_corpus": round(df[col].sum() / n * 100, 1)}
                        for col, label in FAMILIES.items()])
    write_table(fam, "technique_frequency")
    got.update({col: int(df[col].sum()) for col in FAMILIES})

    # ---- RQ2: validation platform class (one class per study)
    plat = df["platform_class"].value_counts().reindex(PLATFORMS, fill_value=0)
    pdist = pd.DataFrame({"platform_class": plat.index, "studies": plat.values,
                          "percent_of_corpus": (plat.values / n * 100).round(1),
                          "edge_group_a": [p in PLATFORMS[:2] for p in plat.index]})
    write_table(pdist, "platform_distribution")
    got["edge_group_a"] = int(df["edge_group_a"].sum())
    got["no_edge_platform"] = int(plat["No edge platform"])

    # ---- RQ4: family x platform matrix
    mat = df.groupby("platform_class")[list(FAMILIES)].sum().reindex(PLATFORMS, fill_value=0)
    mat.columns = list(FAMILIES.values())
    write_table(mat.reset_index(), "technique_platform_matrix")

    # ---- journals and Bradford's law
    df["journal"] = df["source"].map(normalize_journal)
    # Sort by frequency, then alphabetically, so ties are ordered identically
    # across pandas versions.
    vc = df["journal"].value_counts()
    vc = vc.loc[sorted(vc.index, key=lambda j: (-vc[j], j))]
    write_table(pd.DataFrame({"journal": vc.index, "studies": vc.values}), "journals")
    zones = bradford_zones(vc.values, n)
    mult = [round(zones[i + 1][1] / zones[i][1], 2) for i in range(len(zones) - 1)]
    write_table(pd.DataFrame([{"zone": z, "journals": s, "articles": a} for z, s, a in zones]),
                "bradford_zones")
    got["journals"] = len(vc)
    got["single_article_journals"] = int((vc == 1).sum())

    # ---- authors and Lotka's law
    authors = Counter(a.strip().upper().rstrip(".")
                      for cell in df["authors"].dropna() for a in str(cell).split(";") if a.strip())
    dist = Counter(authors.values())
    write_table(pd.DataFrame([{"papers_per_author": k, "authors": dist[k],
                               "observed_percent": round(dist[k] / len(authors) * 100, 1),
                               "lotka_expected_percent": round(lotka_expected(k), 1)}
                              for k in sorted(dist)]), "lotka")
    got["unique_authors"] = len(authors)
    got["single_article_authors"] = dist[1]
    got["uncited_studies"] = int((df["times_cited"] == 0).sum())

    # ---- quality assessment (descriptive only, not used as a filter)
    qrows = []
    for col in ("QA1_hardware", "QA2_method", "QA3_metrics"):
        c = qa[col].value_counts()
        qrows.append({"question": col, "score_1.0": int(c.get(1.0, 0)),
                      "score_0.5": int(c.get(0.5, 0)), "score_0.0": int(c.get(0.0, 0)),
                      "mean": round(qa[col].mean(), 2)})
    write_table(pd.DataFrame(qrows), "quality_summary")
    got["qa1_full"], got["qa1_partial"], got["qa1_none"] = (qrows[0]["score_1.0"],
                                                            qrows[0]["score_0.5"], qrows[0]["score_0.0"])

    # ---- headline summary
    summary = [
        ("Studies in corpus", n),
        ("Publication years", "; ".join(f"{y}: {c}" for y, c in years.items())),
        ("Distinct journals", got["journals"]),
        ("Journals with a single article", f"{got['single_article_journals']} "
                                           f"({got['single_article_journals'] / got['journals'] * 100:.0f}%)"),
        ("Top journals", "; ".join(f"{j.title().replace('Ieee', 'IEEE')} ({c})" for j, c in vc.head(3).items())),
        ("Bradford zones (journals/articles)", "; ".join(f"Z{z}: {s}/{a}" for z, s, a in zones)),
        ("Bradford multipliers", ", ".join(map(str, mult))),
        ("Unique authors", got["unique_authors"]),
        ("Authors with a single article", f"{dist[1]} ({dist[1] / len(authors) * 100:.1f}%)"),
        ("Studies with zero citations", f"{got['uncited_studies']} ({got['uncited_studies'] / n * 100:.0f}%)"),
        ("Edge platform with physical metrics (Group A)", f"{got['edge_group_a']} ({got['edge_group_a'] / n * 100:.1f}%)"),
        ("No edge platform identified", f"{got['no_edge_platform']} ({got['no_edge_platform'] / n * 100:.1f}%)"),
    ]
    sdf = pd.DataFrame(summary, columns=["indicator", "value"])
    write_table(sdf, "corpus_summary")
    for k, v in summary:
        print(f"  {k:48s} {v}")

    bad = {k: (got[k], v) for k, v in EXPECTED.items() if got[k] != v}
    if bad:
        raise SystemExit(f"[FAIL] values differ from the manuscript: {bad}")
    print("\n[OK] All corpus statistics match the manuscript.")


if __name__ == "__main__":
    main()
