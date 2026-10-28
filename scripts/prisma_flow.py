"""Reproduce the PRISMA 2020 selection cascade reported in the manuscript.

The script rebuilds every count of the flow diagram directly from the raw
database exports in ``data/`` and checks it against the published figures:

    724 identified (Scopus 586 + WoS 138)
    -171 duplicates (title-based; see note below)         -> 553
    -385 non-primary document types (EC-4)                 -> 168
    -  5 language not covered (IC-4)                       -> 163
    - 14 untyped secondary literature / incomplete metadata -> 149 screened
    - 69 excluded on title and abstract                    ->  80 full text
    -  7 excluded at full text (do not evaluate an LLM)    ->  73 included

Note on duplicates: de-duplication uses the normalised title. Under that rule
126 removed records overlap across databases and 45 are internal Scopus
redundancies (171 in total). Matching on DOI instead finds 127 WoS records in
Scopus, which is where an earlier 127/44 split came from; the total of 171 and
every downstream count are identical under the title rule used here.

Outputs: outputs/tables/prisma_flow.{csv,md}
Usage:   python scripts/prisma_flow.py
"""
from __future__ import annotations

from collections import Counter

import pandas as pd

from common import (load_corpus, load_fulltext_exclusions, load_screening, load_scopus,
                    load_wos, norm_title, write_table)

# Document types kept as primary journal research (criterion EC-4).
PRIMARY_TYPES = {"Article", "ARTICLE", "ARTICLE; EARLY ACCESS"}

# Figures reported in the manuscript; the script fails if the data disagree.
EXPECTED = {
    "identified": 724, "scopus": 586, "wos": 138,
    "duplicates": 171,
    "non_primary": 385, "language": 5, "secondary_or_incomplete": 14,
    "screened": 149, "excluded_title_abstract": 69, "fulltext_assessed": 80,
    "excluded_fulltext": 7, "included": 73,
}


def _records() -> list[dict]:
    """One dict per identified record, harmonising Scopus and WoS field names."""
    recs = []
    for _, r in load_scopus().iterrows():
        recs.append(dict(db="SCOPUS", key=norm_title(r["Title"]),
                         dtype=str(r["Document Type"]),
                         lang=str(r["Language of Original Document"])))
    for _, r in load_wos().iterrows():
        recs.append(dict(db="WOS", key=norm_title(r["TI"]), dtype=str(r["DT"]), lang=str(r["LA"])))
    return recs


def compute() -> dict:
    """Return every count of the PRISMA cascade as a dict."""
    recs = _records()
    c = {"identified": len(recs),
         "scopus": sum(r["db"] == "SCOPUS" for r in recs),
         "wos": sum(r["db"] == "WOS" for r in recs)}

    # 1) De-duplication by normalised title. WoS metadata are kept when a record
    #    appears in both databases (richer indexed fields, e.g. cited references).
    unique = {}
    for r in sorted(recs, key=lambda r: 0 if r["db"] == "WOS" else 1):
        unique.setdefault(r["key"], r)
    unique = list(unique.values())
    c["duplicates"] = len(recs) - len(unique)

    # Split duplicates into within-database redundancy and cross-database overlap.
    internal = sum(n - 1 for db in ("SCOPUS", "WOS")
                   for n in Counter(r["key"] for r in recs if r["db"] == db).values())
    c["duplicates_internal"] = internal
    c["duplicates_cross"] = c["duplicates"] - internal

    # 2) EC-4: keep primary journal articles only.
    primary = [r for r in unique if r["dtype"] in PRIMARY_TYPES]
    c["non_primary"] = len(unique) - len(primary)
    c["non_primary_breakdown"] = Counter(r["dtype"] for r in unique if r["dtype"] not in PRIMARY_TYPES)

    # 3) IC-4: English or Spanish (blank language fields are kept).
    lang_ok = [r for r in primary if r["lang"].strip().lower() in ("english", "spanish", "", "nan")]
    c["language"] = len(primary) - len(lang_ok)

    # 4) Manual clean-up: untyped reviews/surveys and records with incomplete metadata.
    screened_keys = set(load_screening()["TI"].map(norm_title))
    c["secondary_or_incomplete"] = sum(r["key"] not in screened_keys for r in lang_ok)

    # 5) Title/abstract screening and full-text eligibility.
    scr = load_screening()
    c["screened"] = len(scr)
    c["excluded_title_abstract"] = int((scr["TA_DECISION"] == "exclude").sum())
    c["fulltext_assessed"] = int((scr["TA_DECISION"] == "include").sum())
    c["excluded_fulltext"] = len(load_fulltext_exclusions())
    c["included"] = len(load_corpus())
    return c


def main() -> None:
    c = compute()
    rows = [
        ("Identification", "Records identified (Scopus + WoS)", None, c["identified"]),
        ("Identification", "Duplicates removed", c["duplicates"], c["identified"] - c["duplicates"]),
        ("Identification", "Non-primary document type (EC-4)", c["non_primary"], None),
        ("Identification", "Language not covered (IC-4)", c["language"], None),
        ("Identification", "Secondary literature or incomplete metadata", c["secondary_or_incomplete"], c["screened"]),
        ("Screening", "Excluded on title and abstract", c["excluded_title_abstract"], c["fulltext_assessed"]),
        ("Eligibility", "Excluded at full text (no LLM evaluated)", c["excluded_fulltext"], c["included"]),
        ("Included", "Studies included in the synthesis", None, c["included"]),
    ]
    remaining = c["identified"]
    table = []
    for phase, step, removed, _ in rows:
        if removed:
            remaining -= removed
        table.append({"phase": phase, "step": step, "removed": removed if removed else "",
                      "remaining": remaining})
    write_table(pd.DataFrame(table), "prisma_flow")

    print("PRISMA cascade")
    for t in table:
        print(f"  {t['step']:48s} {str(t['removed']):>5s} -> {t['remaining']:4d}")
    print(f"  (duplicates: {c['duplicates_cross']} cross-database, {c['duplicates_internal']} internal)")
    print("  Non-primary document types:")
    for k, v in c["non_primary_breakdown"].most_common():
        print(f"    {k:34s} {v:4d}")

    bad = {k: (c[k], v) for k, v in EXPECTED.items() if c[k] != v}
    if bad:
        raise SystemExit(f"[FAIL] counts differ from the manuscript: {bad}")
    print("\n[OK] All PRISMA counts match the manuscript.")


if __name__ == "__main__":
    main()
