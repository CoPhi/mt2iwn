# MT2IWN

**MariTerm to ItalWordNet Mapping: Complete Lexical Integration Pipeline**

Modular Python toolkit for extracting, scoring, filtering, and integrating
shared lemmas between MariTerm (maritime terminology) and ItalWordNet (Italian
WordNet). Processes XML-encoded lexical resources through a seven-stage pipeline
from candidate identification to finalized bidirectional plugin links.

---

## Pipeline Overview

```
Stage 1  candidates.py   MariT.xml + IWN.xml → candidates.csv
Stage 2  score.py        candidates.csv       → breakdown.csv
Stage 3  filter.py       breakdown.csv        → MariT_filtered.xml, IWN_filtered.xml
Stage 4  update.py       filtered XMLs        → IWN_updates.xml
Stage 5  merge.py        IWN_updates.xml      → IWN_pre_merge.xml
Stage 6  analyze.py      IWN_pre_merge.xml    → console report
Stage 7  finalize.py     IWN_post_merge.xml   → IWN_final.xml, MariT_final.xml
```

---

## Repository Structure

```
MT2IWN/
├── data/                      XML input files (not in repo)
├── results/                   Generated outputs (not in repo)
├── scripts/
│   ├── config.py              Paths, Config, parse_xml
│   ├── candidates.py          CLI — Stage 1
│   ├── score.py               CLI — Stage 2
│   ├── filter.py              CLI — Stage 3
│   ├── update.py              CLI — Stage 4
│   ├── merge.py               CLI — Stage 5
│   ├── analyze.py             CLI — Stage 6
│   ├── finalize.py            CLI — Stage 7
│   ├── extraction/            Lemma extraction module
│   ├── similarity/            Normalization and scoring
│   ├── matching/              Word meaning matching
│   ├── filtering/             XML filtering and transcription
│   ├── updating/              IWN entry creation and update
│   ├── merging/               File merging and formatting
│   ├── analysis/              Post-hoc checks
│   └── plugins/               Plugin link finalization
└── README.md
```

---

## Installation

```bash
git clone https://github.com/yourusername/MT2IWN.git
cd MT2IWN
pip install pandas scikit-learn
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

Lucia Galiero (2026). MT2IWN: MariTerm to ItalWordNet Integration Toolkit 
(Version 1.0.0) [GitHub Repository]. https://github.com/CoPhi/mt2iwn

BibTeX:
```bibtex
@software{lgaliero2026mt2iwn,
  author = {[Lucia Galiero]},
  title = {MT2IWN: MariTerm to ItalWordNet Integration Toolkit},
  year = {2026},
  url = {https://github.com/CoPhi/mt2iwn},
  version = {1.0.0}
}
```

## License

MIT - See repository for details.

**Last Updated:** February 26th, 2026
