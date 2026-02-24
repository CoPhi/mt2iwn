# MT2IWN

**MariTerm to ItalWordNet Mapping: Complete Lexical Integration Pipeline**

Modular Python toolkit for extracting, scoring, filtering, and integrating shared lemmas between MariTerm (maritime terminology database) and ItalWordNet (Italian WordNet). Processes XML-encoded lexical resources through a multi-stage pipeline from candidate identification to final integration with bidirectional plugin links.

---

## Overview

**Problem:** Integrating domain-specific terminological resources (MariTerm) with general-purpose lexical databases (ItalWordNet) requires: (1) identifying shared lexical entries, (2) scoring semantic similarity across glosses and relations, (3) filtering candidates, (4) merging resources while preserving structure, and (5) establishing bidirectional links.

**Solution:** This toolkit automates the complete integration pipeline through modular components handling extraction, similarity scoring, filtering, updating, merging, and plugin link creation.

**Use Case:** Lexical resource integration, terminology alignment, WordNet extension, cross-resource semantic linking.

---

## Features

**Candidate Extraction** (Notebook 1):
- Automated lemma extraction from XML-encoded lexical resources
- Intersection detection between MariTerm and ItalWordNet
- WORD_MEANING ID mapping for both resources
- CSV export with semicolon-delimited format

**Similarity Scoring & Filtering** (Notebook 2, Part 1):
- TF-IDF-based gloss similarity calculation
- Weighted semantic relation comparison
- Multi-threshold candidate filtering
- Comprehensive metadata breakdown (similarity scores, bonuses, penalties)

**Resource Integration** (Notebook 2, Part 2):
- Filtered XML generation for matched pairs
- ItalWordNet updates with MariTerm entries
- Gloss replacement and fallback handling
- Bidirectional PLUG-IN_LINKS creation
- Duplicate relation removal and XML formatting

**Architecture:**
- Modular design with clear separation of concerns
- Zero external dependencies for core extraction (stdlib only)
- Scientific stack (sklearn, pandas) for advanced scoring

---

## Repository Structure

```
MT2IWN/
├── data/                      # XML input files (not in repo)
│   ├── MariT_03_24.xml       # MariTerm data
│   └── IWN_03_24.xml         # ItalWordNet data
│
├── scripts/                   # All code here
│   ├── extraction/           # Extraction module
│   │   ├── __init__.py
│   │   ├── xml_parser.py     # XML parsing (extract_lemmas)
│   │   ├── matcher.py        # Lemma matching (find_shared)
│   │   ├── writer.py         # CSV output (write_csv)
│   │   └── README.md
│   │
│   ├── candidates.py         # CLI: Extract shared candidates
│   └── README.md
│
├── results/                   # Generated outputs (not in repo)
│   └── candidates.csv        # Shared lemmas with IDs
│
└── README.md
```

---

## Installation

**Requirements:**
- Python 3.8+
- No external dependencies (uses standard library only)

**Setup:**

```bash
# Clone repository
git clone https://github.com/yourusername/MT2IWN.git
cd MT2IWN

# No additional installation needed - uses Python standard library
```

**Note:** All modules are in the `scripts/` directory.

---

## Quick Start

**1. Obtain XML data files:**
- Place MariTerm XML file in `data/MariT_03_24.xml`
- Place ItalWordNet XML file in `data/IWN_03_24.xml`

**2. Extract shared lemma candidates:**
```bash
python scripts/candidates.py \
    --marit data/MariT_03_24.xml \
    --iwn data/IWN_03_24.xml \
    --output results/candidates.csv
```

**3. View results:**
```bash
head -n 5 results/candidates.csv
```

**Output:**
```
Shared Lemma;IWN_WM_ID;MarT_WM_ID
abbandonare;IWN_12345;MT_67890
abbassare;IWN_23456;MT_78901
abboccare;IWN_34567;MT_89012
```

---

## Usage

### Command Line Interface

**Extract shared candidates:**
```bash
python scripts/candidates.py \
    --marit PATH_TO_MARIT_XML \
    --iwn PATH_TO_IWN_XML \
    --output OUTPUT_CSV
```

**Required arguments:**
- `--marit`: Path to MariTerm XML file
- `--iwn`: Path to ItalWordNet XML file
- `--output`: Output CSV file path

**Example:**
```bash
python scripts/candidates.py \
    --marit data/MariT_03_24.xml \
    --iwn data/IWN_03_24.xml \
    --output results/candidates_2024.csv
```

**Console output:**
```
======================================================================
EXTRACTING SHARED LEMMA CANDIDATES
======================================================================
MariTerm file: data/MariT_03_24.xml
ItalWordNet file: data/IWN_03_24.xml
Output file: results/candidates.csv

Finding shared lemmas...
Total extracted lemmas: 1195
Writing 1195 shared lemmas to CSV...

======================================================================
✓ Shared lemmas written to results/candidates.csv
======================================================================
```

---

### Python API

**As module:**
```python
from scripts.extraction import find_shared, write_csv

# Find shared lemmas
shared, marit, iwn = find_shared(
    'data/MariT_03_24.xml',
    'data/IWN_03_24.xml'
)
# Output: "Total extracted lemmas: 1195"

# Export to CSV
write_csv(shared, marit, iwn, 'results/candidates.csv')
```

**Individual functions:**
```python
from scripts.extraction import extract_lemmas

# Extract lemmas from single resource
marit_lemmas = extract_lemmas('data/MariT_03_24.xml')
# Returns: {'ancora': 'MT_12345', 'barca': 'MT_23456', ...}

iwn_lemmas = extract_lemmas('data/IWN_03_24.xml')
# Returns: {'ancora': 'IWN_67890', 'mare': 'IWN_78901', ...}

# Find intersection
shared = set(marit_lemmas.keys()).intersection(set(iwn_lemmas.keys()))
# Returns: {'ancora', ...}
```

See `scripts/extraction/README.md` for detailed API documentation.

---

## Output Format

**CSV Structure (semicolon-delimited, UTF-8):**
```
Shared Lemma;IWN_WM_ID;MarT_WM_ID
abbandonare;IWN_00012345;MT_00067890
abbassare;IWN_00023456;MT_00078901
abboccare;IWN_00034567;MT_00089012
```

**Properties:**
- Header row: `Shared Lemma;IWN_WM_ID;MarT_WM_ID`
- Delimiter: semicolon (`;`)
- Encoding: UTF-8
- Sorting: Alphabetical by lemma (case-insensitive)

---

## XML Structure

**Expected XML format for both MariTerm and ItalWordNet:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ROOT>
  <WORD_MEANING ID="WM_12345">
    <VARIANTS>
      <LITERAL LEMMA="ancora"/>
    </VARIANTS>
  </WORD_MEANING>
  <WORD_MEANING ID="WM_23456">
    <VARIANTS>
      <LITERAL LEMMA="barca"/>
    </VARIANTS>
  </WORD_MEANING>
</ROOT>
```

**Required elements:**
- `WORD_MEANING` with `ID` attribute → WORD_MEANING identifier
- `VARIANTS/LITERAL` with `LEMMA` attribute → Literal lemma form

**Processing notes:**
- Extracts only entries with both required elements
- Skips entries missing `ID` or `LEMMA`
- Case-sensitive lemma matching
- Preserves original WORD_MEANING IDs

---

## Example Results

**Typical extraction from MariTerm and ItalWordNet (March 2024 versions):**

```
Total extracted lemmas: 1195
```

**Breakdown:**
- MariTerm entries: ~5,000 WORD_MEANING elements
- ItalWordNet entries: ~70,000 WORD_MEANING elements
- Shared lemmas: 1,195 (24% of MariTerm coverage)

**Common shared lemmas:**
- Maritime general terms: ancora, barca, nave, porto
- Maritime actions: navigare, ancorare, affondare
- Maritime features: costa, baia, rada

---

## Dependencies

**Python Standard Library Only:**
- `xml.etree.ElementTree` - XML parsing
- `csv` - CSV writing
- `argparse` - CLI argument parsing
- `pathlib` - File path handling

**No external dependencies required.**

Install with:
```bash
# No installation needed - Python 3.8+ includes all required modules
python --version  # Verify Python 3.8+
```

---

## Error Handling

**Missing input files:**
```
Error: MariTerm file not found: data/MariT.xml
```

**Invalid XML structure:**
```
xml.etree.ElementTree.ParseError: mismatched tag: line 42, column 8
```

**No shared lemmas:**
```
Total extracted lemmas: 0
✓ Shared lemmas written to results/candidates.csv
```
Creates CSV with header only.

---

## License

This code is released under an open source license.

---

## Contact

For questions or issues, please open a GitHub issue.

---

**Last Updated:** February 24th, 2026
