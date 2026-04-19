# Scripts Overview

Command-line interface scripts for the MT2IWN pipeline.

This directory contains all CLI wrappers for the seven-stage integration pipeline plus optional analysis utilities. Each script is a thin I/O layer that calls pure functions from the module subdirectories.

---

## Core Pipeline Scripts

### Stage 1: `candidates.py` - Candidate Extraction

Extract shared lemmas between MariTerm and ItalWordNet.

**Input:** 
- `data/MariT_03_24.xml`
- `data/IWN_03_24.xml`

**Output:**
- `results/candidates.csv` - Shared lemma pairs with synset IDs

**Usage:**
```bash
python scripts/candidates.py
python scripts/candidates.py --mariterm data/custom_mariterm.xml --help
```

**Module:** `extraction/`

---

### Stage 2: `score.py` - Similarity Scoring

Score all candidate pairs using TF-IDF and relation similarity.

**Input:** 
- `results/candidates.csv`
- MariTerm and IWN XML files

**Output:**
- `results/breakdown.csv` - All candidates with complete scores

**Key Features:**
- TF-IDF gloss similarity (Jaccard + bidirectional cosine)
- Relation-aware scoring (bonus/malus/no-gloss)
- **Candidate pair constraint**: Only scores (MariTerm ID, IWN ID) pairs from CSV
- **One-to-one enforcement**: Each sense matches at most once

**Usage:**
```bash
python scripts/score.py
python scripts/score.py --candidates results/custom_candidates.csv
```

**Modules:** `similarity/`, `matching/`

**Important:** This stage enforces the candidate pair constraint and one-to-one mapping. The output breakdown.csv contains exactly the candidates from candidates.csv, each scored only once.

---

### Stage 2.5 (Optional): `report.py` - Match Classification

Generate detailed reports showing why each match was accepted or rejected.

**Input:** 
- `results/breakdown.csv`

**Output:**
- `results/reports/accepted_matches.txt` - Accepted pairs with full score breakdowns
- `results/reports/rejected_matches.txt` - Rejected pairs with rejection reasons

**Key Features:**
- Full score component display for every candidate
- Gate-by-gate classification explanation
- Rejection reason for each failed match
- Statistics by classification category

**Usage:**
```bash
python scripts/report.py
python scripts/report.py --gloss-high 0.45 --out-dir results/custom/
python scripts/report.py --help
```

**Module:** `analysis/report.py`

**When to use:**
- Analyzing false positives/negatives
- Tuning threshold parameters
- Documenting matching decisions for papers
- Understanding algorithm behavior

---

### Stage 3: `filter.py` - Threshold Filtering

Apply acceptance gates to scored candidates and extract matched synsets.

**Input:** 
- `results/breakdown.csv`
- MariTerm and IWN XML files

**Output:**
- `results/MariT_filtered.xml` - MariTerm synsets with accepted matches
- `results/IWN_filtered.xml` - IWN synsets with accepted matches

**Key Features:**
- **Two-gate threshold logic**:
  - Gate A: `Gloss S. (WM) >= 0.43` (high gloss alone)
  - Gate B: `Gloss S. (WM) >= 0.13` AND `T. Relation S. >= 0.09` (moderate + relations)
- Extracts only matched synsets to filtered XMLs
- Preserves complete XML structure

**Usage:**
```bash
python scripts/filter.py
python scripts/filter.py --breakdown results/custom_breakdown.csv
```

**Module:** `filtering/`

**Note:** Uses same thresholds as score.py and report.py from `config.py`

---

### Stage 4: `update.py` - IWN Update Generation

Generate ItalWordNet updates from matched MariTerm synsets.

**Input:** 
- `results/MariT_filtered.xml`
- `results/IWN_filtered.xml`

**Output:**
- `results/IWN_updates.xml` - New relations and synsets to add to IWN

**Key Features:**
- Adds missing MariTerm relations to IWN synsets
- Creates new IWN synsets for missing targets
- Handles fallback glosses
- Preserves relation directionality

**Usage:**
```bash
python scripts/update.py
```

**Module:** `updating/`

---

### Stage 5: `merge.py` - XML Merging

Merge IWN updates into the main ItalWordNet resource.

**Input:** 
- `results/IWN_filtered.xml`
- `results/IWN_updates.xml`

**Output:**
- `results/IWN_pre_merge.xml` - Merged but unfinalized IWN

**Usage:**
```bash
python scripts/merge.py
```

**Module:** `merging/`

---

### Stage 6: `analyze.py` - Post-Merge Validation

Validate merged output and report statistics.

**Input:** 
- `results/IWN_pre_merge.xml`

**Output:**
- Console report with statistics and any issues

**Key Features:**
- Synset count verification
- Relation integrity checks
- Gloss completeness validation
- Update summary

**Usage:**
```bash
python scripts/analyze.py
```

**Module:** `analysis/audit.py`, `analysis/identifier.py`

---

### Stage 7: `finalize.py` - Plugin Link Finalization

Generate bidirectional plugin links between MariTerm and ItalWordNet.

**Input:** 
- `results/IWN_pre_merge.xml`
- `results/MariT_filtered.xml`

**Output:**
- `results/IWN_final.xml` - ItalWordNet with plugin links to MariTerm
- `results/MariT_final.xml` - MariTerm with plugin links to IWN

**Key Features:**
- Bidirectional cross-resource links
- Plugin relation encoding (EuroWordNet format)
- Symmetric link verification

**Usage:**
```bash
python scripts/finalize.py
```

**Module:** `plugins/`

---

## Configuration

All scripts read configuration from `config.py`:

### Threshold Constants

```python
# Matching thresholds (used by score.py, filter.py, report.py)
GLOSS_HIGH_THRESHOLD = 0.43    # Gate A: High gloss similarity
GLOSS_LOW_THRESHOLD = 0.13     # Gate B: Minimum gloss
REL_SUPPORT_THRESHOLD = 0.09   # Gate B: Minimum relations
```

**Changing thresholds:**
1. Edit `config.py` constants
2. Re-run affected stages (score.py, filter.py, report.py)

**Or override via CLI:**
```bash
python scripts/report.py --gloss-high 0.50 --gloss-low 0.15
```

### Path Configuration

```python
class Config:
    # Input paths
    DATA_DIR = Path("data")
    MARITERM_XML = DATA_DIR / "MariT_03_24.xml"
    ITALWN_XML = DATA_DIR / "IWN_03_24.xml"
    
    # Output paths
    RESULTS_DIR = Path("results")
    CANDIDATES_CSV = RESULTS_DIR / "candidates.csv"
    BREAKDOWN_CSV = RESULTS_DIR / "breakdown.csv"
    REPORT_OUT_DIR = RESULTS_DIR / "reports"
    
    # ... additional paths
```

**Override via CLI arguments:**
```bash
python scripts/candidates.py --mariterm data/custom.xml --out results/custom/
```

---

## Pipeline Flow

### Complete Pipeline Run

```bash
# Core 7-stage pipeline
python scripts/candidates.py   # Stage 1
python scripts/score.py        # Stage 2
python scripts/filter.py       # Stage 3
python scripts/update.py       # Stage 4
python scripts/merge.py        # Stage 5
python scripts/analyze.py      # Stage 6
python scripts/finalize.py     # Stage 7
```

### With Optional Reporting

```bash
python scripts/candidates.py
python scripts/score.py
python scripts/report.py       # Optional Stage 2.5 - detailed reports
python scripts/filter.py
# ... continue pipeline
```

### Data Flow Diagram

```
MariT.xml ─┐
           ├─→ candidates.py → candidates.csv
IWN.xml ───┘                          ↓
                                 score.py → breakdown.csv
                                      ├─→ [report.py] → reports/*.txt
                                      ↓
                                 filter.py → filtered XMLs
                                      ↓
                                 update.py → IWN_updates.xml
                                      ↓
                                 merge.py → IWN_pre_merge.xml
                                      ↓
                                 analyze.py → [console report]
                                      ↓
                                 finalize.py → IWN_final.xml
                                              MariT_final.xml
```

---

## Common Workflows

### Threshold Tuning

```bash
# Generate baseline reports
python scripts/report.py --out-dir results/baseline/

# Test different thresholds
python scripts/report.py --gloss-high 0.50 --out-dir results/high/
python scripts/report.py --gloss-low 0.15 --out-dir results/strict/

# Compare accepted/rejected counts in each report
```

### Re-Scoring with New Thresholds

```bash
# Edit config.py thresholds
nano scripts/config.py

# Re-run from Stage 2
python scripts/score.py      # Re-score with new thresholds
python scripts/report.py     # Check new classification
python scripts/filter.py     # Continue with new accepted set
# ... rest of pipeline
```

### Validation Only

```bash
# Run just analysis stage on existing merge
python scripts/analyze.py --merged results/IWN_pre_merge.xml
```

### Custom Data Sources

```bash
# Full pipeline with custom inputs
python scripts/candidates.py \
    --mariterm data/MariT_custom.xml \
    --italwn data/IWN_custom.xml \
    --out results/custom/

python scripts/score.py \
    --candidates results/custom/candidates.csv \
    --out results/custom/

# ... continue pipeline with --out results/custom/
```

---

## Constraints and Guarantees

### One-to-One Mapping

**Enforced by:** `score.py` via `matching/matcher.py`

**Guarantee:** Each MariTerm sense matches to AT MOST one IWN sense, and vice versa.

**Verification:**
```bash
python -c "
import pandas as pd
df = pd.read_csv('results/breakdown.csv')
accepted = df[df['Total S.'] >= 0.43]  # Simplified check
print(f'MariTerm IDs unique: {accepted[\"MarT_WM_ID\"].is_unique}')
print(f'IWN IDs unique: {accepted[\"IWN_WM_ID\"].is_unique}')
"
```

### Candidate Pair Constraint

**Enforced by:** `score.py` via `matching/matcher.py`

**Guarantee:** Only (MariTerm ID, IWN ID) pairs from candidates.csv are scored.

**Why:** Prevents spurious matches from cartesian product of all senses.

**Verification:**
```bash
# Count candidates
wc -l results/candidates.csv

# Count scored (should match)
wc -l results/breakdown.csv
```

---

## Module Dependencies

```
candidates.py → extraction/
score.py → extraction/, similarity/, matching/
report.py → analysis/report.py
filter.py → filtering/
update.py → updating/
merge.py → merging/
analyze.py → analysis/audit.py, analysis/identifier.py
finalize.py → plugins/
```

All modules are pure functions (no file I/O). Scripts handle:
- Argument parsing (`argparse`)
- File reading/writing
- Progress reporting
- Error handling

---

## Error Handling

All scripts include:
- Input file validation
- Graceful keyboard interrupt handling
- Detailed error messages
- Stack traces in verbose mode

**Example error:**
```
❌ Error: breakdown.csv not found at results/breakdown.csv
   Run 'python scripts/score.py' first to generate it.
```

---

## Help and Options

Every script supports `--help`:

```bash
python scripts/candidates.py --help
python scripts/score.py --help
python scripts/report.py --help
# ... etc
```

Common options:
- `--help` - Show all options
- `--verbose` - Enable detailed logging
- `--out`, `--out-dir` - Custom output location
- Input file overrides (`--mariterm`, `--italwn`, `--candidates`, etc.)

---

## See Also

- Main `README.md` - Repository overview and quick start
- Module `README.md` files - Detailed API documentation for each module
- `config.py` - Centralized configuration

---

**Last Updated:** April 20th, 2026