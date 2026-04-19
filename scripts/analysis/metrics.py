"""
scripts/analysis/metrics.py
============================
Core metric computation for the mt2iwn matching pipeline evaluation.

All metrics are computed via scikit-learn (sklearn.metrics).  The raw
TP / FP / FN / TN counts entered by the user are converted into the
binary prediction arrays that sklearn expects, then passed through
sklearn's own implementations of precision, recall, F-beta, and accuracy.

Why sklearn and not manual formulas
-------------------------------------
sklearn.metrics is the de-facto standard for classification evaluation in
the Python ecosystem.  Using it means:
  • The formulas are tested, versioned, and citable.
  • Edge cases (zero denominators, all-negative predictions, etc.) are
    handled consistently via the zero_division parameter rather than
    custom None-returning helpers.
  • Results are directly comparable to any other sklearn-evaluated system.

Dependency
----------
scikit-learn is already listed in the project's installation requirements:
    pip install pandas scikit-learn

Public API
----------
confusion_matrix(tp, fp, fn, tn)   →  dict  (validated counts + derived totals)
compute_metrics(cm, betas)         →  dict  (all scores via sklearn)
format_report(cm, metrics, meta)   →  str   (human-readable .txt block)

Internal helpers
----------------
_build_arrays(cm)                  →  (y_true, y_pred)  numpy int arrays
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    fbeta_score,
    precision_score,
    recall_score,
)


# ---------------------------------------------------------------------------
# Confusion matrix (validation + derived totals — no sklearn needed here)
# ---------------------------------------------------------------------------

def confusion_matrix(
    tp: int | float,
    fp: int | float,
    fn: int | float,
    tn: int | float,
) -> dict:
    """
    Validate counts and compute derived totals.

    Floats are accepted so that scaled / estimated FN values can be passed
    without prior rounding.  Rounding to integers happens later in
    _build_arrays(), which is the only place sklearn sees the numbers.

    Parameters
    ----------
    tp, fp, fn, tn : non-negative numbers

    Returns
    -------
    dict with keys:
        tp, fp, fn, tn          — original values as floats
        predicted_positive      — tp + fp
        predicted_negative      — fn + tn
        actual_positive         — tp + fn
        actual_negative         — fp + tn
        total                   — tp + fp + fn + tn

    Raises
    ------
    ValueError  if any count is negative or all four are zero.
    """
    for name, val in (("TP", tp), ("FP", fp), ("FN", fn), ("TN", tn)):
        if val < 0:
            raise ValueError(f"{name} must be >= 0, got {val}")
    if tp + fp + fn + tn == 0:
        raise ValueError("All counts are zero — nothing to evaluate.")

    tp, fp, fn, tn = float(tp), float(fp), float(fn), float(tn)

    return {
        "tp":                 tp,
        "fp":                 fp,
        "fn":                 fn,
        "tn":                 tn,
        "predicted_positive": tp + fp,
        "predicted_negative": fn + tn,
        "actual_positive":    tp + fn,
        "actual_negative":    fp + tn,
        "total":              tp + fp + fn + tn,
    }


# ---------------------------------------------------------------------------
# Array construction
# ---------------------------------------------------------------------------

def _build_arrays(cm: dict) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert confusion-matrix counts into the binary label arrays that
    sklearn.metrics functions expect.

    sklearn works on (y_true, y_pred) pairs, not raw TP/FP/FN/TN counts.
    We reconstruct them by tiling the four outcome combinations:

        TP  →  actual=1, predicted=1  (repeated tp times)
        FP  →  actual=0, predicted=1  (repeated fp times)
        FN  →  actual=1, predicted=0  (repeated fn times)
        TN  →  actual=0, predicted=0  (repeated tn times)

    Float counts (e.g. a scaled FN estimate) are rounded to the nearest
    integer before tiling.  Rounding is done here, not at the CLI level,
    so the user sees the original entered value in the report while sklearn
    receives valid integer repetition counts.

    Parameters
    ----------
    cm : dict — output of confusion_matrix()

    Returns
    -------
    (y_true, y_pred) : (np.ndarray, np.ndarray)  dtype=int, shape=(total,)
    """
    tp = round(cm["tp"])
    fp = round(cm["fp"])
    fn = round(cm["fn"])
    tn = round(cm["tn"])

    y_true = np.array(
        [1] * tp + [0] * fp + [1] * fn + [0] * tn,
        dtype=int,
    )
    y_pred = np.array(
        [1] * tp + [1] * fp + [0] * fn + [0] * tn,
        dtype=int,
    )
    return y_true, y_pred


# ---------------------------------------------------------------------------
# Metric computation via sklearn
# ---------------------------------------------------------------------------

def compute_metrics(cm: dict, betas: Sequence[float] = (0.5, 1.0, 2.0)) -> dict:
    """
    Compute all evaluation metrics using scikit-learn.

    Parameters
    ----------
    cm    : dict — output of confusion_matrix()
    betas : sequence of floats — beta values for sklearn.metrics.fbeta_score
              beta < 1  weights precision more heavily
              beta = 1  equivalent to F1 (fbeta_score matches f1_score exactly)
              beta > 1  weights recall more heavily

    Returns
    -------
    dict with keys:

    precision
        sklearn.metrics.precision_score(y_true, y_pred, zero_division=0)
        TP / (TP + FP) — of all pairs the algorithm accepted, what
        fraction were actually correct?

    recall
        sklearn.metrics.recall_score(y_true, y_pred, zero_division=0)
        TP / (TP + FN) — of all truly correct pairs, what fraction
        did the algorithm find?

    accuracy
        sklearn.metrics.accuracy_score(y_true, y_pred)
        (TP + TN) / total — interpret with caution when TN is estimated
        or zero, as is typically the case here.

    error_rate
        1 - precision — fraction of accepted pairs that were wrong.
        Reported alongside precision because the internship report uses
        the "5% error rate" framing.

    f_scores : dict  {beta: float}
        sklearn.metrics.fbeta_score(y_true, y_pred, beta=beta,
                                    zero_division=0)
        for each beta in betas.

    sklearn_version : str
        The installed scikit-learn version, embedded in the report for
        reproducibility.

    Notes on zero_division
    ----------------------
    zero_division=0 tells sklearn to return 0.0 (not raise a warning or
    exception) when the denominator of a metric is zero.  This matches the
    behaviour the rest of the pipeline uses for undefined scores and avoids
    noisy warnings when TN=0 causes certain metrics to be undefined.
    """
    import sklearn

    y_true, y_pred = _build_arrays(cm)

    precision  = float(precision_score(y_true, y_pred, zero_division=0))
    recall     = float(recall_score(   y_true, y_pred, zero_division=0))
    accuracy   = float(accuracy_score( y_true, y_pred))
    error_rate = 1.0 - precision

    f_scores: dict[float, float] = {}
    for beta in betas:
        f_scores[beta] = float(
            fbeta_score(y_true, y_pred, beta=beta, zero_division=0)
        )

    return {
        "precision":       precision,
        "recall":          recall,
        "accuracy":        accuracy,
        "error_rate":      error_rate,
        "f_scores":        f_scores,
        "sklearn_version": sklearn.__version__,
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def _f2(value: float) -> str:
    """Format a 0-1 float to 2 decimal places."""
    return f"{value:.2f}"


def _pct(value: float) -> str:
    """Format a 0-1 float as a percentage string."""
    return f"{value * 100:.2f}%"


def format_report(cm: dict, metrics: dict, meta: dict) -> str:
    """
    Produce a human-readable .txt block for the evaluation report.

    Parameters
    ----------
    cm      : dict — output of confusion_matrix()
    metrics : dict — output of compute_metrics()
    meta    : dict — contextual information added by the CLI:
                     keys: 'timestamp', 'sample_size',
                           'total_candidates', 'total_accepted',
                           'total_rejected', 'fn_estimation_method'

    Returns
    -------
    str — complete report text, ready to write to a .txt file.
    """
    sep  = "=" * 70
    sep2 = "-" * 70
    lines: list[str] = []

    # ---- header ----
    lines += [
        sep,
        "mt2iwn — EVALUATION METRICS REPORT",
        f"Generated      : {meta.get('timestamp', 'N/A')}",
        f"scikit-learn   : {metrics.get('sklearn_version', 'N/A')}",
        sep,
        "",
    ]

    # ---- pipeline context ----
    lines += [
        "PIPELINE CONTEXT",
        sep2,
        f"Total candidates          : {int(meta.get('total_candidates', 0)):>6}",
        f"Accepted by algorithm     : {int(meta.get('total_accepted', 0)):>6}",
        f"Rejected by algorithm     : {int(meta.get('total_rejected', 0)):>6}",
        f"Manually reviewed (sample): {int(meta.get('sample_size', 0)):>6}",
        "",
        f"FN estimation method : {meta.get('fn_estimation_method', 'manual estimate')}",
        "",
    ]


    # ---- confusion matrix ----
    lines += [
        "CONFUSION MATRIX  (entered values — floats rounded to int for sklearn)",
        sep2,
        f"  {'':30}  {'Predicted +':>12}  {'Predicted -':>12}",
        f"  {'Actual Positive (truly correct)':30}  "
        f"{cm['tp']:>12.0f}  {cm['fn']:>12.0f}",
        f"  {'Actual Negative (truly wrong)':30}  "
        f"{cm['fp']:>12.0f}  {cm['tn']:>12.0f}",
        "",
        f"  TP : {cm['tp']:.0f}",
        f"  FP : {cm['fp']:.0f}",
        f"  FN : {cm['fn']:.0f}",
        f"  TN : {cm['tn']:.0f}",
        f"  Total : {cm['total']:.0f}",
        "",
        f"  Predicted positive (accepted)     : {cm['predicted_positive']:.0f}",
        f"  Predicted negative (rejected)     : {cm['predicted_negative']:.0f}",
        f"  Actual positive (true matches)    : {cm['actual_positive']:.0f}",
        f"  Actual negative (true non-matches): {cm['actual_negative']:.0f}",
        "",
    ]

    # ---- sklearn metrics ----
    lines += [
        "METRICS  (computed via scikit-learn)",
        sep2,
        f"  precision_score  : {_f2(metrics['precision'])}  "
        f"[ {_pct(metrics['precision'])} ]",
        f"    → of all accepted pairs, this fraction was correct",
        "",
        f"  recall_score     : {_f2(metrics['recall'])}  "
        f"[ {_pct(metrics['recall'])} ]",
        f"    → of all truly correct pairs, this fraction was found",
        "",
        f"  error_rate       : {_f2(metrics['error_rate'])}  "
        f"[ {_pct(metrics['error_rate'])} ]",
        f"    → 1 - precision; fraction of accepted pairs that were wrong",
        "",
        f"  accuracy_score   : {_f2(metrics['accuracy'])}  "
        f"[ {_pct(metrics['accuracy'])} ]",
        f"    → interpret with caution: TN is estimated, classes are imbalanced",
        "",
    ]

    # ---- F-scores ----
    lines += ["F-SCORES  (sklearn.metrics.fbeta_score, zero_division=0)", sep2]
    for beta, score in sorted(metrics["f_scores"].items()):
        weight_note = (
            "precision-weighted" if beta < 1.0 else
            "balanced"           if beta == 1.0 else
            "recall-weighted"
        )
        lines.append(
            f"  fbeta_score(beta={beta:<4})  ({weight_note:21})  : {_f2(score)}"
        )
    lines += [
        "",
        "  Formula: F_beta = (1 + beta²) × precision × recall",
        "                    ────────────────────────────────",
        "                    beta² × precision + recall",
        "",
        "  F0.5  weights precision — use when incorrect ItalWordNet updates",
        "        are costlier than missing some valid matches.",
        "  F1    balanced — standard publication default.",
        "  F2    weights recall — use when coverage matters most.",
        "",
    ]

    # ---- interpretation ----
    lines += [
        "INTERPRETATION NOTES",
        sep2,
        "  Metrics cover the scoring + threshold stage only (Stage 2 → 3).",
        "  Post-hoc corrections applied in finalize.py are not reflected.",
        "",
        "  FN is an estimate. Re-run with FN ± 10 to gauge recall sensitivity.",
        "",
        "  TN=0 in the default configuration because rejected pairs were not",
        "  exhaustively reviewed. Accuracy will appear inflated if TN is large.",
        "",
        sep,
        "",
    ]

    return "\n".join(lines)
