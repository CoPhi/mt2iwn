# scripts/analysis/

Post-hoc checks and evaluation for the mt2iwn pipeline.

This module is called by two CLI entry points:

| CLI script           | Module file   | What it does                                                         |
|----------------------|---------------|----------------------------------------------------------------------|
| `scripts/audit.py`   | `audit.py`    | Reads breakdown.csv + breakdown_rejected.csv, re-classifies all 1,157 rows with supplied thresholds, writes .txt reports |
| `scripts/metrics.py` | `metrics.py`  | Computes precision, recall, F-scores from manually entered confusion-matrix counts |

Both files contain only pure functions — no file I/O, no argparse. All of
that belongs to the CLI scripts, following the same pattern as every other
module / CLI pair in the repo.

---

## audit.py

Re-applies the Stage 3 gate logic (Gate A / Gate B) to the full breakdown
CSV and produces formatted text blocks for both accepted and rejected pairs.

### Functions

---

#### `classify(row, cfg) → (decision, reason)`

Decide whether a single candidate row passes the acceptance thresholds.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `row` | `dict` | One row from the full breakdown CSV |
| `cfg` | `dict` | Must contain `GLOSS_HIGH_THRESHOLD`, `GLOSS_LOW_THRESHOLD`, `REL_SUPPORT_THRESHOLD` |

**Returns** `(str, str)` — `decision` is `'ACCEPTED'` or `'REJECTED'`;
`reason` is a human-readable string naming the gate that passed or failed.

**Gate logic**

```
Gate A  Gloss S. (WM) >= GLOSS_HIGH_THRESHOLD          → ACCEPTED
Gate B  Gloss S. (WM) >= GLOSS_LOW_THRESHOLD
        AND T. Relation S. >= REL_SUPPORT_THRESHOLD     → ACCEPTED
otherwise                                               → REJECTED
```

The thresholds are read from `cfg` (not imported from `config.py` directly)
so the function can be tested with arbitrary values without touching global
state.

---

#### `format_entry(row, decision, reason) → str`

Produce a text block for one candidate pair in the same layout that
`display.py` writes to the terminal, extended with the audit verdict.

All float values are rounded to 2 decimal places. Absent glosses are
rendered as `[NO GLOSS]` rather than blank so they are visually distinct.
The block ends with a separator line and a blank line so blocks can be
concatenated directly.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `row` | `dict` | One row from the full breakdown CSV |
| `decision` | `str` | `'ACCEPTED'` or `'REJECTED'` |
| `reason` | `str` | From `classify()` |

**Returns** `str`

---

#### `compute_rejection_stats(rows, cfg) → dict`

Count rejected rows by failure category.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `rows` | `list[dict]` | All rows from the full breakdown CSV |
| `cfg` | `dict` | Same threshold dict as `classify()` |

**Returns** `dict` with keys:

| Key | Description |
|-----|-------------|
| `total` | All rows |
| `accepted` | Rows passing either gate |
| `rejected` | Rows failing both gates |
| `no_gloss_both` | Both glosses absent — scorer had nothing to compare |
| `gloss_below_gate_b` | Gloss S. below Gate B floor regardless of relations |
| `gloss_in_range_rel_weak` | Gloss in `[low, high)` but relation support insufficient |

`no_gloss_both` pairs are the most likely false negatives: the low score
reflects missing data, not semantic divergence.

---

#### `build_report_blocks(rows, cfg) → (matched_blocks, rejected_blocks)`

Classify every row and return two lists of formatted text blocks.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `rows` | `list[dict]` | All rows from the full breakdown CSV |
| `cfg` | `dict` | Threshold dict |

**Returns** `(list[str], list[str])` — one element per candidate pair.
The caller joins and writes; this function produces no output itself.

---

### Internal helpers

| Function | Purpose |
|----------|---------|
| `_safe_float(value, default)` | `float(value)` with fallback for empty/None CSV fields |
| `_parse_list_field(raw)` | Recover a Python list from a CSV field stored as repr or pipe-joined string |

---

## metrics.py

Computes precision, recall, F1 / F-beta and related metrics from manually
entered TP / FP / FN / TN counts using **scikit-learn** (`sklearn.metrics`).
Floats are accepted for FN so scaled estimates can be passed directly; they
are rounded to integers internally before sklearn sees them.

### Functions

---

#### `confusion_matrix(tp, fp, fn, tn) → dict`

Validate counts and compute derived totals.

**Parameters** — all non-negative numbers; floats accepted for scaled
estimates (FN in particular is often derived by scaling a sub-sample).

**Returns** `dict`:

| Key | Formula |
|-----|---------|
| `tp`, `fp`, `fn`, `tn` | Input values, cast to float |
| `predicted_positive` | `tp + fp` |
| `predicted_negative` | `fn + tn` |
| `actual_positive` | `tp + fn` |
| `actual_negative` | `fp + tn` |
| `total` | `tp + fp + fn + tn` |

**Raises** `ValueError` if any count is negative or all four are zero.

---

#### `compute_metrics(cm, betas=(0.5, 1.0, 2.0)) → dict`

Compute all evaluation metrics from a validated confusion matrix.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `cm` | `dict` | Output of `confusion_matrix()` |
| `betas` | `Sequence[float]` | Beta values for F-beta scores |

**Returns** `dict`:

| Key | sklearn function | Notes |
|-----|-----------------|-------|
| `precision` | `precision_score(zero_division=0)` | 0.0 if no pairs were accepted |
| `recall` | `recall_score(zero_division=0)` | 0.0 if no actual positives |
| `accuracy` | `accuracy_score()` | Misleading when TN is estimated or zero |
| `error_rate` | `1 - precision` | Complement of precision |
| `f_scores` | `{beta: fbeta_score(beta=beta, zero_division=0)}` | One entry per beta |
| `sklearn_version` | `sklearn.__version__` | Embedded in report for reproducibility |

`zero_division=0` instructs sklearn to return 0.0 (not raise a warning)
when a denominator is zero — consistent with how the rest of the pipeline
handles undefined scores.

**F-beta formula** (as implemented by `sklearn.metrics.fbeta_score`)

```
F_beta = (1 + beta²) × precision × recall
         ─────────────────────────────────
         beta² × precision + recall

beta < 1  →  precision-weighted  (penalises false positives more)
beta = 1  →  balanced F1
beta > 1  →  recall-weighted     (penalises false negatives more)
```

For this pipeline: use **F0.5** if incorrect ItalWordNet updates are the
primary concern; **F2** if maximising coverage of valid matches matters
most; **F1** for the neutral / publication-default case.

---

#### `format_report(cm, metrics, meta) → str`

Produce a human-readable .txt report.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `cm` | `dict` | Output of `confusion_matrix()` |
| `metrics` | `dict` | Output of `compute_metrics()` |
| `meta` | `dict` | Contextual fields added by the CLI (see below) |

**`meta` keys**

| Key | Description |
|-----|-------------|
| `timestamp` | ISO datetime string |
| `total_candidates` | All pairs entering Stage 2 |
| `total_accepted` | Pairs accepted by Stage 3 |
| `total_rejected` | Pairs rejected by Stage 3 |
| `sample_size` | Size of the manual validation sample |
| `fn_estimation_method` | How the FN count was derived |
| `notes` | Free-text caveats or sampling description |

**Returns** `str` — complete report text, ready to write to a .txt file.

---

### Default values (from the internship report)

These are pre-filled in `scripts/metrics.py` and shown in the interactive
prompt. They come from the post-hoc corrections section of the internship
report and should not be changed here without updating that reference.

| Count | Value | Source |
|-------|-------|--------|
| TP | 386 | 400 reviewed − 14 wrong (10 incorrect + 4 redundant) |
| FP | 14  | 10 incorrectly aligned + 4 removed as redundant |
| FN | 10  | 10 below-threshold pairs confirmed correct in post-hoc |
| TN | 0   | Rejected pairs not exhaustively reviewed |

---

### Internal helpers

| Function | Purpose |
|----------|---------|
| `_build_arrays(cm)` | Reconstruct `(y_true, y_pred)` numpy arrays from TP/FP/FN/TN counts for sklearn; floats rounded to int here |
| `_f2(value)` | Format float to 2 decimal places for the report |
| `_pct(value)` | Format float as percentage string for the report |

---

## Shared internal helper

`audit.py` uses `_safe_float()` and `_parse_list_field()` as local helpers.
`metrics.py` delegates edge-case handling to sklearn's `zero_division`
parameter instead.  If a third analysis file needs either helper, move it
to `scripts/analysis/utils.py` and import from there.