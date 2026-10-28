# Data dictionary

All files are UTF-8 CSV with a header row. They are derived from
`screening_workbook.xlsx`, the working file in which the authors recorded every
selection decision. Abstracts, cited references, funding texts and e-mail
addresses were removed from all files before publication; every other field
is as exported or as coded by the authors.

| File | Rows | PRISMA stage | Content |
|---|---:|---|---|
| `scopus_raw.csv` | 586 | Identification | Scopus CSV export (native Scopus column names). |
| `wos_raw.csv` | 138 | Identification | Web of Science Core Collection export as a field-tag table (`AU`, `TI`, `SO`, `DT`, `LA`, `PY`, `DI`, ...; bibliometrix format). |
| `screening_title_abstract.csv` | 149 | Screening | Records that survived de-duplication and type/language filters, with the title/abstract decision. |
| `fulltext_exclusions.csv` | 7 | Eligibility | Records excluded after full-text reading, with the reason. |
| `corpus_73.csv` | 73 | Included | **Data extraction matrix (Annex A)**: one row per included study. |
| `quality_assessment.csv` | 73 | Included | **Quality assessment (Annex B)**: QA1-QA3 scores. |
| `keyword_corrections_log.csv` | 180 | -- | Audit log of author/index keyword cells re-aligned by DOI against the raw exports (October 2026). |
| `screening_workbook.xlsx` | -- | All | Original working workbook (one sheet per stage), kept for provenance. |

## `screening_title_abstract.csv`

Uses the WoS field tags for bibliographic columns (`BASE` = database the
metadata were taken from, `DI` = DOI, `AU` = authors, `TI` = title, `SO` =
source, `DT` = document type, `PY` = year, `LA` = language, `DE` = author
keywords, `ID` = index keywords, `C1` = affiliations, `RP` = reprint address,
`TC` = times cited, `WC` = WoS categories), plus:

| Column | Values | Meaning |
|---|---|---|
| `TA_DECISION` | `include` / `exclude` | Title and abstract screening decision (80 / 69). |
| `TA_REASON_ES` | free text (Spanish) | Reviewer's justification, as recorded during screening. |

## `fulltext_exclusions.csv`

Same columns as above, plus `FT_EXCLUSION_REASON_ES` (Spanish): why the study
was excluded after full-text reading. All seven do not optimise or evaluate an
LLM.

## `corpus_73.csv` (Annex A)

| Column | Type | Description |
|---|---|---|
| `cite_key` | text | BibTeX key used in the manuscript and supplementary material. |
| `doi` | text | DOI (lower case). Join key with every other file. |
| `authors`, `title`, `year`, `source`, `document_type`, `language` | text / int | Bibliographic metadata. |
| `database` | `WOS` / `SCOPUS` | Database the metadata come from (WoS preferred when the record is in both). |
| `times_cited` | int | Citation count at export time. |
| `author_keywords`, `index_keywords` | text, `;`-separated | Used for the thematic map. |
| `affiliations`, `wos_categories` | text | As exported. |
| `open_access` | `yes` / `no` | Whether the full text is freely available. |
| `technique` | text | Optimisation technique(s) as declared by the study. |
| `hardware` | text | Hardware exactly as declared by the study (not completed with assumptions). |
| `platform_class` | category | `NVIDIA Jetson`, `ARM SoC / Raspberry Pi / NPU`, `Server FPGA`, `Desktop/server GPU`, `No edge platform`. One class per study. |
| `edge_group_a` | 0/1 | 1 = concrete edge platform with physical metrics measured on it (Group A, n = 9). |
| `quantization`, `pruning_sparsity`, `low_rank_peft`, `distillation` | 0/1 | Optimisation families (non-exclusive). |
| `main_result_es` | text (Spanish) | Main quantitative result, as reported in Annex A of the supplementary material. |
| `inclusion_rationale_es` | text (Spanish) | Reviewer's inclusion justification at screening. |

Rows follow the order of the screening workbook. `scripts/generate_charts.py`
uses this order to break frequency ties in the thematic map, so do not
re-sort the file if you want to reproduce Figure 2 exactly.

## `quality_assessment.csv` (Annex B)

| Column | Values | Question |
|---|---|---|
| `QA1_hardware` | 1.0 / 0.5 / 0.0 | Does the study explicitly specify the hardware and physical deployment environment? 1.0 = concrete device named; 0.5 = generic descriptor only; 0.0 = not declared. |
| `QA2_method` | 1.0 / 0.5 / 0.0 | Is the optimisation method reproducible? |
| `QA3_metrics` | 1.0 / 0.5 / 0.0 | Are quantitative metrics compared against established reference models? |
| `total_score` | 0-3 | Sum of the three scores. |

The assessment is descriptive: no study was excluded or down-weighted because
of its score.
