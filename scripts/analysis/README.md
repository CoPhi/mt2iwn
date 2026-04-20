# Analysis Module

Post-pipeline analysis, validation, and reporting utilities for the MT2IWN toolkit.

This module provides functions for validating pipeline outputs, classifying match results, computing evaluation metrics, and generating detailed human-readable reports. All functions are pure (no file I/O) - CLI scripts handle I/O.

---

## Module Files

### `metrics.py` - Evaluation Metrics Computation

**NEW in v1.0.0** - Core metric computation for matching pipeline evaluation using scikit-learn.

All metrics are computed via `sklearn.metrics` rather than manual formulas. This ensures tested, versioned, citable implementations with consistent edge-case handling.

#### Why sklearn and not manual formulas

- ✅ `sklearn.metrics` is the de-facto standard for classification evaluation in Python
- ✅ Formulas are tested, versioned, and citable
- ✅ Edge cases (zero denominators, all-negative predictions) handled consistently via `zero_division` parameter
- ✅ Results directly comparable to any other sklearn-evaluated system

#### Functions

##### `confusion_matrix(tp, fp, fn, tn)`

Validate counts and compute derived totals.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tp` | int or float | True positives (correctly accepted matches) |
| `fp` | int or float | False positives (incorrectly accepted matches) |
| `fn` | int or float | False negatives (missed valid matches) |
| `tn` | int or float | True negatives (correctly rejected non-matches) |

**Why floats accepted:** FN is often an estimate from sampling rejected pairs (e.g., "~45 based on reviewing 50 rejected"). Floats are accepted so scaled estimates can be passed without prior rounding. Rounding to integers happens internally in `_build_arrays()`.

**Returns:** `dict` with keys:
```python
{
    'tp': float,                  # Original value
    'fp': float,
    'fn': float,
    'tn': float,
    'predicted_positive': float,  # tp + fp
    'predicted_negative': float,  # fn + tn
    'actual_positive': float,     # tp + fn
    'actual_negative': float,     # fp + tn
    'total': float                # tp + fp + fn + tn
}
```

**Raises:** `ValueError` if any count is negative or all four are zero.

**Example:**
```python
from analysis.metrics import confusion_matrix

# From validation: 380 correct, 20 incorrect in 400-sample
# Extrapolated to 730 accepted total: ~694 TP, ~36 FP
# Estimated 45 FN from examining rejected pairs
cm = confusion_matrix(tp=694, fp=36, fn=45, tn=382)

print(f"Total evaluated: {cm['total']}")
print(f"Precision denominator: {cm['predicted_positive']}")  # 694 + 36 = 730
```

---

##### `compute_metrics(cm, betas=(0.5, 1.0, 2.0))`

Compute all evaluation metrics using scikit-learn.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cm` | dict | - | Output from `confusion_matrix()` |
| `betas` | Sequence[float] | (0.5, 1.0, 2.0) | Beta values for F-beta scores |

**Beta interpretation:**
- `beta < 1.0` - Weights precision more (e.g., F0.5: incorrect updates costlier than missing matches)
- `beta = 1.0` - Balanced F1-score (standard publication default)
- `beta > 1.0` - Weights recall more (e.g., F2: coverage matters most)

**Returns:** `dict` with keys:

```python
{
    'precision': float,        # sklearn.metrics.precision_score
                               # TP / (TP + FP) - fraction of accepted that were correct
    
    'recall': float,           # sklearn.metrics.recall_score  
                               # TP / (TP + FN) - fraction of true matches found
    
    'accuracy': float,         # sklearn.metrics.accuracy_score
                               # (TP + TN) / total - interpret with caution when TN estimated
    
    'error_rate': float,       # 1 - precision
                               # Fraction of accepted pairs that were wrong
    
    'f_scores': dict,          # {beta: fbeta_score}
                               # sklearn.metrics.fbeta_score for each beta
    
    'sklearn_version': str     # Installed sklearn version for reproducibility
}
```

**Note on zero_division:** All sklearn calls use `zero_division=0`, which returns `0.0` (not raise warnings) when denominators are zero. Matches pipeline's undefined score handling.

**Example:**
```python
from analysis.metrics import confusion_matrix, compute_metrics

cm = confusion_matrix(tp=694, fp=36, fn=45, tn=382)
metrics = compute_metrics(cm, betas=[0.5, 1.0, 2.0])

print(f"Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
print(f"Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
print(f"F1-score:  {metrics['f_scores'][1.0]:.4f}")
print(f"\nComputed with sklearn {metrics['sklearn_version']}")

# Check all F-beta scores
for beta, score in metrics['f_scores'].items():
    weight = 'precision' if beta < 1 else 'balanced' if beta == 1 else 'recall'
    print(f"F{beta} ({weight}): {score:.4f}")
```

---

##### `format_report(cm, metrics, meta)`

Produce human-readable .txt block for evaluation report.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cm` | dict | Output from `confusion_matrix()` |
| `metrics` | dict | Output from `compute_metrics()` |
| `meta` | dict | Contextual info added by CLI (timestamp, sample_size, etc.) |

**Meta dict keys:**
- `'timestamp'` - Report generation time
- `'sample_size'` - Validation sample size (e.g., 400)
- `'total_candidates'` - Total pairs evaluated (e.g., 1157)
- `'total_accepted'` - Total accepted by algorithm (e.g., 730)
- `'total_rejected'` - Total rejected by algorithm (e.g., 427)
- `'fn_estimation_method'` - How FN was estimated (e.g., "manual review of 50 rejected pairs")

**Returns:** `str` - Complete report text ready to write to file.

**Report Structure:**
```
======================================================================
mt2iwn — EVALUATION METRICS REPORT
Generated      : 2026-04-20 15:30:00
scikit-learn   : 1.3.0
======================================================================

PIPELINE CONTEXT
----------------------------------------------------------------------
Total candidates          :   1157
Accepted by algorithm     :    730
Rejected by algorithm     :    427
Manually reviewed (sample):    400

FN estimation method : manual review of 50 rejected pairs

CONFUSION MATRIX  (entered values — floats rounded to int for sklearn)
----------------------------------------------------------------------
  [... matrix table ...]

METRICS  (computed via scikit-learn)
----------------------------------------------------------------------
  precision_score  : 0.95  [ 95.00% ]
    → of all accepted pairs, this fraction was correct

  recall_score     : 0.94  [ 94.00% ]
    → of all truly correct pairs, this fraction was found

  error_rate       : 0.05  [ 5.00% ]
    → 1 - precision; fraction of accepted pairs that were wrong

  accuracy_score   : 0.93  [ 93.00% ]
    → interpret with caution: TN is estimated, classes are imbalanced

F-SCORES  (sklearn.metrics.fbeta_score, zero_division=0)
----------------------------------------------------------------------
  fbeta_score(beta=0.5 )  (precision-weighted    )  : 0.95
  fbeta_score(beta=1.0 )  (balanced              )  : 0.94
  fbeta_score(beta=2.0 )  (recall-weighted       )  : 0.94

  [... formula and interpretation notes ...]

INTERPRETATION NOTES
----------------------------------------------------------------------
  Metrics cover the scoring + threshold stage only (Stage 2 → 3).
  Post-hoc corrections applied in finalize.py are not reflected.

  FN is an estimate. Re-run with FN ± 10 to gauge recall sensitivity.
  [... additional notes ...]
```

**Example:**
```python
from analysis.metrics import confusion_matrix, compute_metrics, format_report
from datetime import datetime

cm = confusion_matrix(tp=694, fp=36, fn=45, tn=382)
metrics = compute_metrics(cm)

meta = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'sample_size': 400,
    'total_candidates': 1157,
    'total_accepted': 730,
    'total_rejected': 427,
    'fn_estimation_method': 'manual review of 50 rejected pairs'
}

report_text = format_report(cm, metrics, meta)

# Write to file
with open('results/evaluation_report.txt', 'w') as f:
    f.write(report_text)

print("Report saved to results/evaluation_report.txt")
```

---

#### Internal Helpers

##### `_build_arrays(cm)`

Convert confusion matrix counts into binary label arrays for sklearn.

**Why needed:** `sklearn.metrics` functions expect `(y_true, y_pred)` arrays, not raw TP/FP/FN/TN counts. This function reconstructs them by tiling:
- TP → `actual=1, predicted=1` (repeated tp times)
- FP → `actual=0, predicted=1` (repeated fp times)
- FN → `actual=1, predicted=0` (repeated fn times)
- TN → `actual=0, predicted=0` (repeated tn times)

**Rounding:** Float counts (e.g., FN=45.2 from scaling) are rounded to nearest integer before tiling. Rounding happens here (not at CLI) so user sees original value in report while sklearn receives valid integer arrays.

**Returns:** `(y_true, y_pred)` - numpy arrays with dtype=int

---

### `report.py` - Match Classification and Formatting

Functions for classifying scored synset matches into accepted/rejected categories and generating detailed formatted reports.

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

---

##### `build_report_blocks(df, gloss_high=0.43, gloss_low=0.13, rel_support=0.09)`

Build formatted text blocks for all matches, separated by acceptance.

**Returns:** `Tuple[List[str], List[str], Dict[str, int]]`
- `accepted_blocks`: List of formatted strings for accepted matches
- `rejected_blocks`: List of formatted strings for rejected matches
- `stats`: Classification counts by reason

---

##### `compute_classification_stats(df, gloss_high=0.43, gloss_low=0.13, rel_support=0.09)`

Compute classification statistics without building full text blocks.

Lightweight version of `build_report_blocks()` for quick analysis.

---

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

### Compute Evaluation Metrics

```python
from analysis.metrics import confusion_matrix, compute_metrics, format_report
from datetime import datetime

# From your validation data:
# - Reviewed 400 accepted pairs: 380 correct, 20 incorrect
# - Algorithm accepted 730 total
# - Estimated 45 FN from examining rejected pairs
# - Rejected 427 total

# Extrapolate FP from sample to full accepted set
fp_rate = 20 / 400  # 5% error rate in sample
fp_full = int(730 * fp_rate)  # ~37 false positives
tp_full = 730 - fp_full  # ~693 true positives

# True negatives (estimated)
tn_full = 427 - 45  # rejected - false negatives = 382

# Build confusion matrix
cm = confusion_matrix(tp=tp_full, fp=fp_full, fn=45, tn=tn_full)

# Compute metrics
metrics = compute_metrics(cm, betas=[0.5, 1.0, 2.0])

print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1-score:  {metrics['f_scores'][1.0]:.4f}")

# Generate full report
meta = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'sample_size': 400,
    'total_candidates': 1157,
    'total_accepted': 730,
    'total_rejected': 427,
    'fn_estimation_method': 'manual review of 50 rejected pairs'
}

report = format_report(cm, metrics, meta)

# Save report
with open('results/evaluation_metrics.txt', 'w') as f:
    f.write(report)
```

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

### Threshold Consistency

All analysis functions use the same threshold defaults as `scripts/config.py`:
- `GLOSS_HIGH_THRESHOLD = 0.43`
- `GLOSS_LOW_THRESHOLD = 0.13`
- `REL_SUPPORT_THRESHOLD = 0.09`

This ensures classification in reports matches the actual pipeline decisions.

### sklearn Dependency

`metrics.py` requires scikit-learn, already in project requirements:
```bash
pip install pandas scikit-learn numpy
```

---

## CLI Scripts

The analysis module is called by these CLI scripts:

- **`scripts/metrics.py`** - Computes evaluation metrics
  - Uses: `confusion_matrix()`, `compute_metrics()`, `format_report()`
  
- **`scripts/report.py`** - Generates detailed match classification reports
  - Uses: `classify_match()`, `format_match_entry()`, `build_report_blocks()`
  
- **`scripts/analyze.py`** - Post-merge validation and analysis
  - Uses: `validate_merged_xml()`, `identify_updates_in_iwn()`

---

## Output Formats

### Metrics Report Format

See `format_report()` documentation above for complete structure.

### Classification Report Format

See `report.py` documentation above for complete structure.

---

## Changelog

### Version 1.0.0 (2026-04-20)
- ✅ Added `metrics.py` module with sklearn-based metric computation
- ✅ `confusion_matrix()` - Validation and derived totals
- ✅ `compute_metrics()` - Precision, recall, F-beta via sklearn
- ✅ `format_report()` - Human-readable metric reports
- ✅ Added `report.py` module with classification functions
- ✅ `classify_match()` - Two-gate threshold logic
- ✅ `format_match_entry()` - Detailed score formatting
- ✅ `build_report_blocks()` - Batch processing for reports
- ✅ `compute_classification_stats()` - Quick statistics
- ✅ Existing `identifier.py` modules

---

## See Also

- `scripts/metrics.py` - CLI wrapper for computing metrics
- `scripts/report.py` - CLI wrapper for generating reports
- `scripts/analyze.py` - CLI wrapper for post-merge validation
- `scripts/matching/matcher.py` - Core matching algorithm
- `scripts/config.py` - Threshold configuration