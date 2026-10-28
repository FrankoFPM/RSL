"""Shared paths, loaders and text-normalisation helpers.

Every analysis script imports from this module so that all figures and tables
are computed from the same files in ``data/`` with the same cleaning rules.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"

# Optimisation families coded per study in corpus_73.csv (0/1 flags).
FAMILIES = {
    "quantization": "Quantization",
    "pruning_sparsity": "Pruning / sparsity",
    "low_rank_peft": "Low-rank (LoRA/PEFT)",
    "distillation": "Knowledge distillation",
}

# Platform classes, ordered from edge to non-edge. Group A = the first two.
PLATFORMS = [
    "NVIDIA Jetson",
    "ARM SoC / Raspberry Pi / NPU",
    "Server FPGA",
    "Desktop/server GPU",
    "No edge platform",
]
EDGE_PLATFORMS = set(PLATFORMS[:2])


def ensure_output_dirs() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- loaders
def load_scopus() -> pd.DataFrame:
    """Original Scopus export (586 records)."""
    return pd.read_csv(DATA / "scopus_raw.csv")


def load_wos() -> pd.DataFrame:
    """Original Web of Science export (138 records)."""
    return pd.read_csv(DATA / "wos_raw.csv")


def load_screening() -> pd.DataFrame:
    """149 records screened by title and abstract, with decision and reason."""
    return pd.read_csv(DATA / "screening_title_abstract.csv")


def load_fulltext_exclusions() -> pd.DataFrame:
    """7 records excluded at the full-text eligibility stage."""
    return pd.read_csv(DATA / "fulltext_exclusions.csv")


def load_corpus() -> pd.DataFrame:
    """Final corpus of 73 studies (data extraction matrix, Annex A)."""
    return pd.read_csv(DATA / "corpus_73.csv")


def load_quality() -> pd.DataFrame:
    """Kitchenham quality assessment of the 73 studies (Annex B)."""
    return pd.read_csv(DATA / "quality_assessment.csv")


# --------------------------------------------------------------------------- helpers
def norm_title(s) -> str:
    """Lower-case ASCII alphanumerics only; used as the de-duplication key."""
    if pd.isna(s):
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


_JOURNAL_ABBR = [
    (r"^IEEE TRANS\.? ", "IEEE TRANSACTIONS ON "),
    (r"\bMOB\.? COMPUT\.?$", "MOBILE COMPUTING"),
    (r"\bCONSUM\.? ELECTRON\.?$", "CONSUMER ELECTRONICS"),
    (r"\bCIRCUITS SYST\.? VIDEO TECHNOL\.?$", "CIRCUITS AND SYSTEMS FOR VIDEO TECHNOLOGY"),
    (r"\bPARALLEL DISTRIB\.? SYST\.?$", "PARALLEL AND DISTRIBUTED SYSTEMS"),
    (r"\bINTELL\.? TRANSP\.? SYST\.?$", "INTELLIGENT TRANSPORTATION SYSTEMS"),
    (r"\bAUTON\.? INTELL\.? SYST\.?\b", "AUTONOMOUS INTELLIGENT SYSTEMS"),
    (r"\bNAT\.? COMMUN\.?\b", "NATURE COMMUNICATIONS"),
    (r"\bCOMPUT\.?\b", "COMPUTING"),
    (r"\bSYST\.?\b", "SYSTEMS"),
    (r"\bAPPL\.?\b", "APPLICATIONS"),
    (r"\bTECHNOL\.?\b", "TECHNOLOGY"),
]


def normalize_journal(s) -> str:
    """Collapse abbreviated journal names (Scopus vs. WoS) to one canonical form."""
    if pd.isna(s):
        return "UNKNOWN"
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"\s+", " ", s.upper().strip()).replace("&", " AND ")
    for pat, rep in _JOURNAL_ABBR:
        s = re.sub(pat, rep, s)
    return re.sub(r"\s+", " ", re.sub(r"[\.,]+$", "", s)).strip()


_KEYWORD_SYNONYMS = {
    "Large language models": {"large language models (llms)", "large language model", "llm", "llms",
                              "large language models"},
    "Quantization": {"quantization (signal)", "quantization", "quantizations", "model quantization"},
    "Computational modeling": {"computational modeling", "computational model", "computational models",
                               "computer simulation"},
    "Edge computing": {"edge computing", "edge-computing"},
    "Knowledge distillation": {"knowledge distillation", "knowledge-distillation", "kd"},
    "Model compression": {"model compression", "model-compression"},
    "Deep learning": {"deep learning", "deep-learning"},
    "Machine learning": {"machine learning", "machine-learning"},
    "Neural networks": {"neural networks", "artificial neural networks", "neural network"},
}


def clean_keyword(kw) -> str:
    """Merge spelling variants of the same author keyword."""
    k = str(kw).strip().lower()
    for canonical, variants in _KEYWORD_SYNONYMS.items():
        if k in variants:
            return canonical
    return str(kw).strip().capitalize()


def split_keywords(cell) -> list[str]:
    """Split a ';'-separated keyword cell into cleaned, non-empty keywords."""
    if pd.isna(cell) or not str(cell).strip():
        return []
    return [clean_keyword(x) for x in str(cell).split(";") if x.strip()]


def write_table(df: pd.DataFrame, stem: str) -> None:
    """Write a table to outputs/tables as both CSV and Markdown."""
    ensure_output_dirs()
    df.to_csv(TABLES / f"{stem}.csv", index=False)
    (TABLES / f"{stem}.md").write_text(to_markdown(df), encoding="utf-8")


def to_markdown(df: pd.DataFrame) -> str:
    """Minimal GitHub-flavoured Markdown table (avoids the optional tabulate dependency)."""
    cells = [[str(c) for c in df.columns]] + [["" if pd.isna(v) else str(v) for v in row]
                                               for row in df.itertuples(index=False)]
    lines = ["| " + " | ".join(r) + " |" for r in cells]
    lines.insert(1, "|" + "|".join("---" for _ in df.columns) + "|")
    return "\n".join(lines) + "\n"
