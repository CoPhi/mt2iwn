# MT2IWN
**MariTerm to ItalWordNet Mapping: Complete Lexical Integration Pipeline**
Modular Python toolkit for extracting, scoring, filtering, and integrating
shared lemmas between MariTerm (maritime terminology) and ItalWordNet (Italian
WordNet). Processes XML-encoded lexical resources through a seven-stage pipeline
from candidate identification to finalized bidirectional plugin links, with
post-pipeline evaluation utilities.

---

## Pipeline Overview

```
Stage 1  candidates.py   MariT.xml + IWN.xml  → candidates.csv
Stage 2  score.py        candidates.csv        → breakdown.csv (747 accepted)
                                                  breakdown_rejected.csv (410 rejected)
                                                  matched_breakdown.txt
                                                  rejected_breakdown.txt
Stage 3  filter.py       breakdown.csv         → MariT_filtered.xml, IWN_filtered.xml
Stage 4  update.py       filtered XMLs         → IWN_updates.xml
Stage 5  merge.py        IWN_updates.xml       → IWN_pre_merge.xml
Stage 6  analyze.py      IWN_pre_merge.xml     → console report
Stage 7  finalize.py     IWN_post_merge.xml    → IWN_final.xml, MariT_final.xml
```

Stage 2 scores all 1,157 candidates, writes accepted and rejected rows to
separate CSVs, and immediately generates the two .txt breakdown reports.
`breakdown.csv` (accepted only) is unchanged for downstream compatibility with
Stage 3; `breakdown_rejected.csv` is a new parallel output.

### Evaluation Utilities

These scripts operate on Stage 2 outputs and are run independently of the
main sequence.

```
audit.py    breakdown.csv + breakdown_rejected.csv  → matched_breakdown.txt,
                                                       rejected_breakdown.txt
metrics.py  manual counts                           → evaluation_metrics.txt
```

`audit.py` reads both Stage 2 CSVs, re-classifies all 1,157 rows with
whatever thresholds you supply, and writes fresh .txt files. Use it for
threshold sensitivity experiments without re-running scoring.

`metrics.py` computes precision, recall, F1 / F-beta and related metrics from
manually entered confusion-matrix counts. Missing values are prompted
interactively if not supplied via flags.

---

## Repository Structure

```
MT2IWN/
├── data/                      XML input files (not in repo)
├── results/
│   ├── breakdown.csv              747 accepted rows (Stage 2)
│   ├── breakdown_rejected.csv     410 rejected rows (Stage 2, new)
│   ├── matched_breakdown.txt      Score report — accepted (Stage 2, new)
│   ├── rejected_breakdown.txt     Score report — rejected (Stage 2, new)
│   └── audit/                     Re-analysis outputs (audit.py, metrics.py)
├── scripts/
│   ├── config.py              Paths, thresholds (GLOSS_HIGH/LOW, REL_SUPPORT),
│   │                          BREAKDOWN_CSV, BREAKDOWN_REJECTED_CSV, AUDIT_OUT_DIR
│   ├── candidates.py          CLI — Stage 1
│   ├── score.py               CLI — Stage 2
│   ├── filter.py              CLI — Stage 3
│   ├── update.py              CLI — Stage 4
│   ├── merge.py               CLI — Stage 5
│   ├── analyze.py             CLI — Stage 6
│   ├── finalize.py            CLI — Stage 7
│   ├── audit.py               CLI — Threshold re-analysis (evaluation utility)
│   ├── metrics.py             CLI — Evaluation metrics (evaluation utility)
│   ├── extraction/            Lemma extraction module
│   ├── similarity/            Normalization and scoring
│   ├── matching/              Word meaning matching
│   │   └── report.py          format_block(), write_breakdown_txts()
│   ├── filtering/             XML filtering and transcription
│   ├── updating/              IWN entry creation and update
│   ├── merging/               File merging and formatting
│   ├── analysis/              Post-hoc checks and evaluation
│   │   ├── audit.py           classify(), build_report_blocks(),
│   │   │                      compute_rejection_stats(), format_entry()
│   │   └── metrics.py         confusion_matrix(), compute_metrics(),
│   │                          format_report()
│   └── plugins/               Plugin link finalization
└── README.md
```

---

## Installation

```bash
git clone https://github.com/yourusername/MT2IWN.git
cd MT2IWN
pip install pandas scikit-learn numpy
```

Python 3.8+ required. No other external dependencies.

---

## Quick Start

Place `MariT_03_24.xml` and `IWN_03_24.xml` in `data/`, then run each stage:

```bash
python scripts/candidates.py
python scripts/score.py
python scripts/filter.py
python scripts/update.py
python scripts/merge.py
python scripts/analyze.py
python scripts/finalize.py
```

All scripts use the default paths from `scripts/config.py`.
Run any script with `--help` to see all options.

### Breakdown reports

`score.py` writes the .txt reports automatically. To re-generate them with
different thresholds (without re-running scoring):

```bash
# Default thresholds — output identical to score.py's
python scripts/audit.py

# Threshold experiment
python scripts/audit.py --gloss-high 0.45 --gloss-low 0.10 --out-dir results/audit_v2

# See all options
python scripts/audit.py --help
```

### Evaluation metrics

```bash
# Fully interactive — prompts for TP, FP, FN, TN with explanations
python scripts/metrics.py

# Fully scripted
python scripts/metrics.py --tp 386 --fp 14 --fn 10 --tn 0 --no-interactive

# Partial flags — missing values are prompted
python scripts/metrics.py --tp 386 --fp 14
```

---

## config.py — Shared Constants

`scripts/config.py` holds all paths and threshold values used across stages.
The evaluation utilities read thresholds from config so the audit reproduces
the same 747 / 410 split as Stage 3.

| Constant                  | Default                          | Used by                        |
|---------------------------|----------------------------------|--------------------------------|
| `GLOSS_HIGH_THRESHOLD`    | 0.43                             | score.py, filter.py, audit.py  |
| `GLOSS_LOW_THRESHOLD`     | 0.13                             | score.py, filter.py, audit.py  |
| `REL_SUPPORT_THRESHOLD`   | 0.09                             | score.py, filter.py, audit.py  |
| `BREAKDOWN_CSV`           | `results/breakdown.csv`          | score.py, filter.py, audit.py  |
| `BREAKDOWN_REJECTED_CSV`  | `results/breakdown_rejected.csv` | score.py, audit.py             |
| `BREAKDOWN_REPORT_DIR`    | `results`                        | score.py                       |
| `AUDIT_OUT_DIR`           | `results/audit`                  | audit.py, metrics.py           |

---

## Module Documentation

Each module has a `README.md` with full API documentation:

- `scripts/extraction/README.md`
- `scripts/similarity/README.md`
- `scripts/matching/README.md`
- `scripts/filtering/README.md`
- `scripts/updating/README.md`
- `scripts/merging/README.md`
- `scripts/analysis/README.md`
- `scripts/plugins/README.md`

---

## Citation

If you use this toolkit in your research, please cite:

### Software Citation
Galiero, L. & Boschetti, F. (2026). *MT2IWN: MariTerm to ItalWordNet Integration Toolkit* (Version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.18788538

**BibTeX:**
```bibtex
@software{galiero2026mt2iwn,
  author = {Galiero, Lucia}, {Boschetti, Federico}
  title = {{MT2IWN}: {MariTerm} to {ItalWordNet} Integration Toolkit},
  year = {2026},
  publisher = {Zenodo},
  version = {1.0.0},
  doi = {https://doi.org/10.5281/zenodo.18788538},
  url = {https://github.com/CoPhi/mt2iwn}
}
```

## License

MIT - See repository for details.

**Last Updated:** April 19th, 2026