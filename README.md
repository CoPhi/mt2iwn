# MT2IWN

**MariTerm to ItalWordNet Mapping: Complete Lexical Integration Pipeline**

Modular Python toolkit for extracting, scoring, filtering, and integrating shared lemmas between MariTerm (maritime terminology) and ItalWordNet (Italian WordNet). Processes XML-encoded lexical resources through a seven-stage pipeline from candidate identification to finalized bidirectional plugin links, with optional analysis and reporting utilities.

---

## Pipeline Overview

### Core Pipeline Stages

```
Stage 1  candidates.py   MariT.xml + IWN.xml → candidates.csv
Stage 2  score.py        candidates.csv       → breakdown.csv
Stage 3  filter.py       breakdown.csv        → MariT_filtered.xml, IWN_filtered.xml
Stage 4  update.py       filtered XMLs        → IWN_updates.xml
Stage 5  merge.py        IWN_updates.xml      → IWN_pre_merge.xml
Stage 6  analyze.py      IWN_pre_merge.xml    → console report
Stage 7  finalize.py     IWN_post_merge.xml   → IWN_final.xml, MariT_final.xml
```

### Optional Analysis Stage

**Stage 2.5 (Optional): `report.py`** - Match Classification Reports

Generates detailed breakdowns showing why each match was accepted or rejected. Does not affect pipeline output - pure analysis/reporting tool.

```bash
python scripts/report.py
```

**Input:** `results/breakdown.csv` (from score.py)  
**Output:** 
- `results/reports/accepted_matches.txt` - Detailed breakdown of accepted pairs with full score components
- `results/reports/rejected_matches.txt` - Detailed breakdown of rejected pairs with rejection reasons

**Use cases:**
- Understanding matching algorithm behavior
- Identifying false positive/negative patterns
- Threshold tuning and validation
- Documentation for papers and reports

---

## Repository Structure

```
MT2IWN/
├── data/                      XML input files (not in repo)
├── results/                   Generated outputs (not in repo)
│   ├── candidates.csv
│   ├── breakdown.csv
│   ├── reports/               Match classification reports (optional)
│   │   ├── accepted_matches.txt
│   │   └── rejected_matches.txt
├── scripts/
│   ├── config.py              Paths, Config, parse_xml, threshold constants
│   ├── candidates.py          CLI — Stage 1
│   ├── score.py               CLI — Stage 2
│   ├── report.py              CLI — Optional Stage 2.5 (NEW)
│   ├── filter.py              CLI — Stage 3
│   ├── update.py              CLI — Stage 4
│   ├── merge.py               CLI — Stage 5
│   ├── analyze.py             CLI — Stage 6
│   ├── finalize.py            CLI — Stage 7
│   ├── extraction/            Lemma extraction module
│   ├── similarity/            Normalization and scoring
│   ├── matching/              Word meaning matching
│   │   ├── matcher.py         Core matching algorithm
│   │   ├── normalizer.py      Gloss preprocessing
│   │   └── writer.py          Output formatting
│   ├── filtering/             XML filtering and transcription
│   ├── updating/              IWN entry creation and update
│   ├── merging/               File merging and formatting
│   ├── analysis/              Post-hoc checks and reporting
│   │   ├── audit.py           Post-merge validation
│   │   ├── identifier.py      Update identification
│   │   └── report.py          Match classification and formatting (NEW)
│   └── plugins/               Plugin link finalization
└── README.md
```

---

## Installation

```bash
git clone https://github.com/CoPhi/mt2iwn.git
cd mt2iwn
pip install pandas scikit-learn numpy
```

Python 3.8+ required. No other external dependencies.

---

## Configuration

All threshold values and paths are defined in `scripts/config.py`:

| Constant | Default | Used By | Purpose |
|----------|---------|---------|---------|
| `GLOSS_HIGH_THRESHOLD` | 0.43 | score.py, filter.py, report.py | Gate A: Accept on high gloss similarity alone |
| `GLOSS_LOW_THRESHOLD` | 0.13 | score.py, filter.py, report.py | Gate B: Minimum gloss with relation support |
| `REL_SUPPORT_THRESHOLD` | 0.09 | score.py, filter.py, report.py | Gate B: Minimum relation score |
| `REPORT_OUT_DIR` | results/reports/ | report.py | Report output location |

**Matching constraints:**
- **One-to-one mapping**: Each MariTerm sense matches to at most one IWN sense, and vice versa
- **Two-gate threshold logic**: Matches pass via high gloss similarity (Gate A) OR moderate gloss + strong relation support (Gate B)

To change thresholds, edit these values in `config.py` - all relevant stages will use the updated values automatically.

---

## Quick Start

Place `MariT_03_24.xml` and `IWN_03_24.xml` in `data/`, then run each stage:

### Core Pipeline
```bash
python scripts/candidates.py
python scripts/score.py
python scripts/filter.py
python scripts/update.py
python scripts/merge.py
python scripts/analyze.py
python scripts/finalize.py
```

### Optional: Generate Match Reports

```bash
# Generate detailed acceptance/rejection reports
python scripts/report.py

# Use custom thresholds
python scripts/report.py --gloss-high 0.45 --out-dir results/custom_reports/

# See all options
python scripts/report.py --help
```

All scripts use the default paths from `scripts/config.py`.
Run any script with `--help` to see all options.

---

## Module Documentation

Each module has a `README.md` with full API documentation:

- `scripts/extraction/README.md` - Lemma extraction from XML
- `scripts/similarity/README.md` - Normalization and TF-IDF scoring
- `scripts/matching/README.md` - One-to-one sense matching
- `scripts/filtering/README.md` - XML filtering and transcription
- `scripts/updating/README.md` - IWN entry creation
- `scripts/merging/README.md` - File merging and formatting
- `scripts/analysis/README.md` - Post-hoc validation and reporting
- `scripts/plugins/README.md` - Plugin link finalization

---

## Key Features

### Matching Algorithm
- **TF-IDF-based gloss similarity** with weighted mean scoring
- **Relation-aware scoring** with configurable bonus/malus weights
- **One-to-one constraint enforcement** - no duplicate matches
- **Two-gate threshold logic** for balanced precision/recall

### Quality Controls
- **Multi-stage validation**: Scoring → filtering → updating → merging → analysis
- **One-to-one mapping verification**: Each sense matches at most once
- **Manual validation support**: Post-hoc inspection of merged XML
- **Detailed reporting**: Full score breakdowns for all candidates

### Output Formats
- **Enhanced XML resources** with bidirectional plugin links
- **CSV breakdowns** with complete scoring details
- **Text reports** with human-readable match classifications
- **Console summaries** for quick pipeline monitoring

---

## Citation

If you use this toolkit in your research, please cite:

### Software Citation

Galiero, L. & Boschetti, F. (2026). *MT2IWN: MariTerm to ItalWordNet Integration Toolkit* (Version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.18788538

**BibTeX:**
```bibtex
@software{galiero2026mt2iwn,
  author = {Galiero, Lucia and Boschetti, Federico},
  title = {{MT2IWN}: {MariTerm} to {ItalWordNet} Integration Toolkit},
  year = {2026},
  publisher = {Zenodo},
  version = {1.0.0},
  doi = {10.5281/zenodo.18788538},
  url = {https://github.com/CoPhi/mt2iwn}
}
```

### Associated Publication

Galiero, L., Boschetti, F., Del Gratta, R., Del Grosso, A. M., & Monachini, M. (2026). Reviving Legacy WordNet-like Resources: MariTerm and ItalWordNet Renewal through Mutual Expansion and Plug-in Links. *Journal of Open Humanities Data*.

---

## License

MIT - See LICENSE file for details.

---

## Contributing

This toolkit was developed as part of a research project at CNR-ILC. For bug reports, feature requests, or contributions, please open an issue or pull request on GitHub.

---

## Changelog

### Version 1.0.0 (2026-04-20)
- Initial release
- Seven-stage integration pipeline
- Optional reporting utilities
- Configurable threshold system

---

**Last Updated:** April 20th, 2026