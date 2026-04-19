# Analysis Module

Post-pipeline analysis, validation, and reporting utilities for the MT2IWN toolkit.

This module provides functions for validating pipeline outputs, classifying match results, and generating detailed human-readable reports. All functions are pure (no file I/O) - CLI scripts handle I/O.

---

## Module Files

### `report.py` - Match Classification and Formatting

**NEW in v1.0.0** - Functions for classifying scored synset matches into accepted/rejected categories and generating detailed formatted reports.

#### Functions

##### `classify_match(gloss_score, relation_score, gloss_high=0.43, gloss_low=0.13, rel_support=0.09)`

Classify a synset match as accepted or rejected based on threshold gates.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gloss_score` | float | - | Gloss similarity score (weighted mean) |
| `relation_score` | float | - | Total relation similarity score |
| `gloss_high` | float | 0.43 | High gloss threshold for Gate A |
| `gloss_low` | float | 0.13 | Low gloss threshold for Gate B |
| `rel_support` | float | 0.09 | Relation support threshold for Gate B |

**Returns:** `Tuple[bool, str]`
- `is_accepted`: True if match passes either gate
- `reason`: Explanation of classification decision

**Gate Logic:**
```python
# Gate A: High gloss similarity alone
if gloss_score >= gloss_high:
    return True, "Gate A: High gloss similarity"

# Gate B: Moderate gloss + relation support
if gloss_score >= gloss_low and relation_score >= rel_support:
    return True, "Gate B: Moderate gloss + strong relations"

# Otherwise rejected (specify which threshold failed)
if gloss_score < gloss_low:
    return False, f"Rejected: Gloss {gloss_score:.2f} < {gloss_low}"
else:
    return False, f"Rejected: Relations {relation_score:.2f} < {rel_support}"
```

**Example:**
```python
is_accepted, reason = classify_match(0.50, 0.05)
# → (True, "Gate A: High gloss similarity (≥0.43)")

is_accepted, reason = classify_match(0.20, 0.12)
# → (True, "Gate B: Moderate gloss + strong relations")

is_accepted, reason = classify_match(0.10, 0.05)
# → (False, "Rejected: Gloss 0.10 < 0.13 (min threshold)")
```

---

##### `format_match_entry(row, include_rejection_reason=False)`

Format a single match row into a detailed score breakdown block.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `row` | Dict | - | Match data from breakdown.csv row |
| `include_rejection_reason` | bool | False | Include reason line if rejected |

**Returns:** `str` - Formatted text block with all score details

**Output Format:**
```
MariTerm Lemma: bitta
ItalWN Lemma: bitta
POS: N

Gloss S. (WM): 0.4512
T. Relation S.: 0.1200

  Gloss S. (J): 0.3500
  Gloss S. (MT): 0.5000
  Gloss S. (IWN): 0.4800

  Bonus Relations (2): has_hyperonym, has_meronym
  Bonus Score: 0.1500

  Missing Relations (0): None
  Malus Score: 0.0000

  No-Gloss Relations (0): None
  No-Gloss Malus: 0.0000

  MariTerm Relations (2): has_hyperonym, has_meronym
  ItalWN Relations (1): has_hyperonym

[Reason: Gate A: High gloss similarity]  # If include_rejection_reason=True
```

**Example:**
```python
import pandas as pd
df = pd.read_csv('results/breakdown.csv')

# Format first match
entry_text = format_match_entry(df.iloc[0], include_rejection_reason=False)
print(entry_text)

# Format with rejection reason
rejected_df = df[df['Gloss S. (WM)'] < 0.13]
entry_text = format_match_entry(rejected_df.iloc[0], include_rejection_reason=True)
print(entry_text)
```

---

##### `build_report_blocks(df, gloss_high=0.43, gloss_low=0.13, rel_support=0.09)`

Build formatted text blocks for all matches, separated by acceptance.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | DataFrame | - | All scored candidates from breakdown.csv |
| `gloss_high` | float | 0.43 | High gloss threshold |
| `gloss_low` | float | 0.13 | Low gloss threshold |
| `rel_support` | float | 0.09 | Relation support threshold |

**Returns:** `Tuple[List[str], List[str], Dict[str, int]]`
- `accepted_blocks`: List of formatted strings for accepted matches
- `rejected_blocks`: List of formatted strings for rejected matches
- `stats`: Classification counts by reason

**Stats Dictionary:**
```python
{
    'total': 1157,
    'accepted_gate_a': 600,
    'accepted_gate_b': 147,
    'rejected_low_gloss': 300,
    'rejected_weak_relations': 110
}
```

**Example:**
```python
import pandas as pd
from analysis.report import build_report_blocks

df = pd.read_csv('results/breakdown.csv')

accepted_blocks, rejected_blocks, stats = build_report_blocks(df)

print(f"Total: {stats['total']}")
print(f"Accepted via Gate A: {stats['accepted_gate_a']}")
print(f"Accepted via Gate B: {stats['accepted_gate_b']}")
print(f"Rejected (low gloss): {stats['rejected_low_gloss']}")
print(f"Rejected (weak relations): {stats['rejected_weak_relations']}")

# Write to file
with open('accepted.txt', 'w') as f:
    for block in accepted_blocks:
        f.write(block + '\n\n' + '-'*80 + '\n\n')
```

---

##### `compute_classification_stats(df, gloss_high=0.43, gloss_low=0.13, rel_support=0.09)`

Compute classification statistics without building full text blocks.

Lightweight version of `build_report_blocks()` for quick analysis.

**Parameters:** Same as `build_report_blocks()`

**Returns:** `Dict[str, int]` - Classification counts

**Additional Keys:**
```python
{
    'total': 1157,
    'accepted': 747,
    'rejected': 410,
    'accepted_gate_a': 600,
    'accepted_gate_b': 147,
    'rejected_low_gloss': 300,
    'rejected_weak_relations': 110
}
```

**Example:**
```python
from analysis.report import compute_classification_stats

stats = compute_classification_stats(df)

print(f"Acceptance rate: {stats['accepted']/stats['total']:.1%}")
print(f"Gate A rate: {stats['accepted_gate_a']/stats['accepted']:.1%}")
print(f"Gate B rate: {stats['accepted_gate_b']/stats['accepted']:.1%}")
```

---

### `audit.py` - Post-Merge Validation

Functions for validating the final merged XML output and identifying inconsistencies.

#### Functions

##### `validate_merged_xml(xml_path)`

Validate the merged ItalWordNet XML for structural and semantic consistency.

**Checks:**
- XML well-formedness
- Synset ID uniqueness
- Gloss completeness
- Relation target validity
- Plugin link integrity

**Returns:** `Dict[str, List]` - Validation results by category

---

##### `identify_inconsistencies(merged_xml, original_xml)`

Compare merged output against original to identify changes and potential errors.

**Returns:** `List[Dict]` - Inconsistencies with severity levels

---

### `identifier.py` - Update Identification

Functions for identifying which synsets were modified during the integration pipeline.

#### Functions

##### `extract_internal_links(xml_tree)`

Extract all internal semantic relation links from an XML tree.

**Returns:** `Dict[str, List[str]]` - Synset ID → list of related synset IDs

---

##### `identify_updates_in_iwn(original_xml, merged_xml)`

Identify which ItalWordNet synsets were modified during integration.

**Returns:** `Dict[str, str]` - Synset ID → update type (added, modified, unchanged)

---

## Usage Examples

### Generate Classification Report

```python
import pandas as pd
from analysis.report import build_report_blocks

# Load scored candidates
df = pd.read_csv('results/breakdown.csv')

# Build report blocks
accepted_blocks, rejected_blocks, stats = build_report_blocks(
    df,
    gloss_high=0.43,
    gloss_low=0.13,
    rel_support=0.09
)

# Print statistics
print(f"\nClassification Summary:")
print(f"  Total candidates: {stats['total']}")
print(f"  Accepted: {len(accepted_blocks)}")
print(f"    Via Gate A (high gloss): {stats['accepted_gate_a']}")
print(f"    Via Gate B (moderate + relations): {stats['accepted_gate_b']}")
print(f"  Rejected: {len(rejected_blocks)}")
print(f"    Due to low gloss: {stats['rejected_low_gloss']}")
print(f"    Due to weak relations: {stats['rejected_weak_relations']}")

# Write reports to files
with open('results/accepted_report.txt', 'w') as f:
    for i, block in enumerate(accepted_blocks, 1):
        f.write(f"--- Entry {i} ---\n\n{block}\n\n{'-'*80}\n\n")

with open('results/rejected_report.txt', 'w') as f:
    for i, block in enumerate(rejected_blocks, 1):
        f.write(f"--- Entry {i} ---\n\n{block}\n\n{'-'*80}\n\n")
```

### Quick Statistics Check

```python
from analysis.report import compute_classification_stats

# Fast stats without building full reports
stats = compute_classification_stats(df)

print(f"Acceptance rate: {stats['accepted']/stats['total']:.1%}")
print(f"Rejection rate: {stats['rejected']/stats['total']:.1%}")

# Analyze gate usage
total_accepted = stats['accepted']
print(f"\nGate A usage: {stats['accepted_gate_a']/total_accepted:.1%}")
print(f"Gate B usage: {stats['accepted_gate_b']/total_accepted:.1%}")
```

### Validate Pipeline Output

```python
from analysis.audit import validate_merged_xml
from analysis.identifier import identify_updates_in_iwn

# Validate merged XML
issues = validate_merged_xml('results/IWN_merged.xml')

if issues:
    print("⚠ Validation issues found:")
    for category, items in issues.items():
        print(f"  {category}: {len(items)} issues")
else:
    print("✓ Validation passed")

# Identify updates
updates = identify_updates_in_iwn(
    'data/IWN_03_24.xml',
    'results/IWN_merged.xml'
)

print(f"\nUpdate summary:")
print(f"  Added: {sum(1 for v in updates.values() if v == 'added')}")
print(f"  Modified: {sum(1 for v in updates.values() if v == 'modified')}")
print(f"  Unchanged: {sum(1 for v in updates.values() if v == 'unchanged')}")
```

---

## Implementation Notes

### Shared Helpers

Both `report.py` and `audit.py` use shared helper functions for parsing list fields from CSV:

```python
def _parse_list_field(field_value):
    """
    Parse list fields that may be in repr format or pipe-separated.
    
    Handles:
    - Python repr: "['rel1', 'rel2']"
    - Pipe-separated: "rel1|rel2"
    - Empty values: '[]', '', 'nan'
    """
    if not field_value or str(field_value) in ['[]', '', 'nan']:
        return []
    
    s = str(field_value)
    if s.startswith('['):
        import ast
        return ast.literal_eval(s)
    else:
        return [x.strip() for x in s.split('|') if x.strip()]
```

### Threshold Consistency

All analysis functions use the same threshold defaults as `scripts/config.py`:
- `GLOSS_HIGH_THRESHOLD = 0.43`
- `GLOSS_LOW_THRESHOLD = 0.13`
- `REL_SUPPORT_THRESHOLD = 0.09`

This ensures classification in reports matches the actual pipeline decisions.

---

## CLI Scripts

The analysis module is called by these CLI scripts:

- **`scripts/report.py`** - Generates detailed match classification reports
  - Uses: `classify_match()`, `format_match_entry()`, `build_report_blocks()`
  
- **`scripts/analyze.py`** - Post-merge validation and analysis
  - Uses: `validate_merged_xml()`, `identify_updates_in_iwn()`

---

## Output Formats

### Classification Report Format

```
================================================================================
ACCEPTED MATCHES - DETAILED BREAKDOWN
Total: 747 synset pairs
================================================================================

STATISTICS
--------------------------------------------------------------------------------
Total accepted: 747
Via Gate A (high gloss): 600
Via Gate B (moderate gloss + relations): 147

================================================================================

--- Entry 1 ---

MariTerm Lemma: ancora
ItalWN Lemma: ancora
POS: N

Gloss S. (WM): 0.5234
T. Relation S.: 0.0800

  Gloss S. (J): 0.4500
  Gloss S. (MT): 0.5600
  Gloss S. (IWN): 0.5600

  Bonus Relations (1): has_hyperonym
  Bonus Score: 0.1200

  [... full breakdown ...]

--------------------------------------------------------------------------------

--- Entry 2 ---

[... next match ...]
```

---

## Changelog

### Version 1.0.0 (2026-04-20)
-  Added `report.py` module with classification functions
- `classify_match()` - Two-gate threshold logic
- `format_match_entry()` - Detailed score formatting
- `build_report_blocks()` - Batch processing for reports
- `compute_classification_stats()` - Quick statistics
- Existing `audit.py` and `identifier.py` modules

---

## See Also

- `scripts/report.py` - CLI wrapper for generating reports
- `scripts/analyze.py` - CLI wrapper for post-merge validation
- `scripts/matching/matcher.py` - Core matching algorithm
- `scripts/config.py` - Threshold configuration