# scripts

All pipeline code lives here. Each stage is a self-contained module with
its own `README.md`, plus a CLI tool that wraps it.

## Module Map

```
scripts/
├── config.py              Paths, Config (allowed relation types), parse_xml
│
├── extraction/            Stage 1 — shared lemma candidate extraction
├── similarity/            Core — normalization and scoring functions
├── matching/              Stage 2 — word meaning matching and CSV export
├── filtering/             Stage 3 — filtered XML pair generation
├── updating/              Stage 4 — IWN word meaning creation and update
├── merging/               Stage 5 — merge updated entries into full IWN
├── analysis/              Stage 6 — post-hoc conflict and ID checks
└── plugins/               Stage 7 — bidirectional PLUG-IN_LINKS finalization
```

## CLI Tools

| Script | Stage | Description |
|--------|-------|-------------|
| `candidates.py` | 1 | Extract shared lemma candidates → `candidates.csv` |
| `score.py` | 2 | Score candidates → `breakdown.csv` |
| `filter.py` | 3 | Filter pairs → `MariT_filtered.xml`, `IWN_filtered.xml` |
| `update.py` | 4 | Update IWN → `IWN_updates.xml` |
| `merge.py` | 5 | Merge IWN files → `IWN_pre_merge.xml` |
| `analyze.py` | 6 | Detect conflicts, report IDs |
| `finalize.py` | 7 | Add plugin links → `IWN_final.xml`, `MariT_final.xml` |

## Quick Pipeline

```bash
python scripts/candidates.py --marit data/MariT.xml --iwn data/IWN.xml --output results/candidates.csv

python scripts/score.py --candidates results/candidates.csv --output results/breakdown.csv

python scripts/filter.py --breakdown results/breakdown.csv \
    --output-marit results/MariT_filtered.xml --output-iwn results/IWN_filtered.xml

python scripts/update.py --breakdown results/breakdown.csv --output results/IWN_updates.xml

python scripts/merge.py --iwn-updates results/IWN_updates.xml --output results/IWN_pre_merge.xml

python scripts/analyze.py --iwn-merged results/IWN_pre_merge.xml

python scripts/finalize.py --output-iwn results/IWN_final.xml --output-marit results/MariT_final.xml
```

All scripts accept `--help` for full argument documentation.
Default paths are read from `scripts/config.py` (`Paths` class).

## Module READMEs

Each module folder contains a `README.md` with full API documentation:
`extraction/`, `similarity/`, `matching/`, `filtering/`,
`updating/`, `merging/`, `analysis/`, `plugins/`.
