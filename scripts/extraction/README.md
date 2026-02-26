## Module: Extraction (`scripts/extraction/`)

Extracts shared lemma candidates between MariTerm and ItalWordNet XML files.

---

### Overview

This module parses XML-encoded lexical resources (MariTerm and ItalWordNet) to identify lemmas that appear in both resources. It extracts WORD_MEANING IDs for each shared lemma, enabling downstream alignment and mapping tasks.

**Core functionality:**
- Parse MariTerm and ItalWordNet XML files
- Extract literal lemmas with their WORD_MEANING IDs
- Find intersection of lemmas between resources
- Export results to CSV format

---

### Module Structure

```
extraction/
├── __init__.py       # Module exports
├── xml_parser.py     # XML parsing (extract_lemmas)
├── matcher.py        # Lemma matching (find_shared)
├── writer.py         # CSV output (write_csv)
└── README.md
```

---

### Functions

#### `extract_lemmas(file_path)`
**Purpose:** Extract literal lemmas and WORD_MEANING IDs from XML file

**Args:**
- `file_path` (str): Path to MariTerm or ItalWordNet XML file

**Returns:**
- dict: `{lemma: word_meaning_id}`

**Example:**
```python
from extraction import extract_lemmas

lemmas = extract_lemmas('data/MariT_03_24.xml')
# Returns: {'ancora': 'WM_001', 'barca': 'WM_002', ...}
```

---

#### `find_shared(MariT_file, IWN_file)`
**Purpose:** Find lemmas present in both MariTerm and ItalWordNet

**Args:**
- `MariT_file` (str): Path to MariTerm XML file
- `IWN_file` (str): Path to ItalWordNet XML file

**Returns:**
- tuple: `(shared_lemmas, MariT_lemmas, IWN_lemmas)`
  - `shared_lemmas` (set): Lemmas in both resources
  - `MariT_lemmas` (dict): All MariTerm lemmas
  - `IWN_lemmas` (dict): All ItalWordNet lemmas

**Output:**
Prints count of shared lemmas to console

**Example:**
```python
from extraction import find_shared

shared, marit, iwn = find_shared('MariT.xml', 'IWN.xml')
# Output: "Total extracted lemmas: 1195"
# Returns: ({'ancora', 'barca', ...}, {...}, {...})
```

---

#### `write_csv(shared_lemmas, MariT_lemmas, IWN_lemmas, file_name)`
**Purpose:** Write shared lemmas to CSV with IDs from both resources

**Args:**
- `shared_lemmas` (set): Shared lemmas from `find_shared()`
- `MariT_lemmas` (dict): MariTerm lemmas from `find_shared()`
- `IWN_lemmas` (dict): ItalWordNet lemmas from `find_shared()`
- `file_name` (str): Output CSV path

**CSV Format:**
```
Shared Lemma;IWN_WM_ID;MarT_WM_ID
ancora;IWN_12345;MT_67890
barca;IWN_23456;MT_78901
```

**Example:**
```python
from extraction import write_csv

write_csv(shared, marit, iwn, 'candidates.csv')
```

---

### Usage

**As Python module:**
```python
from extraction import find_shared, write_csv

# Find shared lemmas
shared, marit, iwn = find_shared('MariT.xml', 'IWN.xml')

# Export to CSV
write_csv(shared, marit, iwn, 'candidates.csv')
```

**Via CLI (recommended):**
```bash
python scripts/candidates.py \
    --marit data/MariT_03_24.xml \
    --iwn data/IWN_03_24.xml \
    --output candidates.csv
```

See `scripts/README.md` for CLI documentation.

---

### XML Structure Requirements

**Expected XML structure:**
```xml
<ROOT>
  <WORD_MEANING ID="WM_12345">
    <VARIANTS>
      <LITERAL LEMMA="ancora"/>
    </VARIANTS>
  </WORD_MEANING>
</ROOT>
```

**Required elements:**
- `WORD_MEANING` with `ID` attribute
- `VARIANTS/LITERAL` with `LEMMA` attribute

**Processing:**
- Extracts only entries with both `WORD_MEANING[@ID]` and `LITERAL[@LEMMA]`
- Skips entries missing either element
- Case-sensitive lemma matching

---

### Output

**Console output:**
```
Total extracted lemmas: 1195
```

**CSV output (semicolon-delimited):**
- Header: `Shared Lemma;IWN_WM_ID;MarT_WM_ID`
- Sorted alphabetically (case-insensitive)
- UTF-8 encoding

---

### Error Handling

**File not found:**
```python
FileNotFoundError: [Errno 2] No such file or directory: 'MariT.xml'
```

**Invalid XML:**
```python
xml.etree.ElementTree.ParseError: mismatched tag
```

**No shared lemmas:**
```
Total extracted lemmas: 0
```
Creates empty CSV with header only.

---

### Dependencies

- `xml.etree.ElementTree` (Python standard library)
- `csv` (Python standard library)

**No external dependencies required.**

---

**Last Updated:** February 24, 2026
