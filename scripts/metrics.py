"""
scripts/metrics.py
==================
CLI entry point for the mt2iwn evaluation metrics stage.

All computation lives in scripts/analysis/metrics.py.  This script
owns argument parsing, the interactive prompt, file I/O, and the
console summary — nothing else.

Usage modes
-----------
1. Fully non-interactive (CI / reproducible runs):
       python scripts/metrics.py --tp 380 --fp 20 --fn 10 --tn 0

2. Partially specified — missing values are prompted interactively:
       python scripts/metrics.py --tp 380 --fp 20
       # → will ask for FN and TN at the terminal

3. Fully interactive — no flags at all:
       python scripts/metrics.py
       # → walks through every value with explanations

4. Custom F-beta values:
       python scripts/metrics.py --tp 380 --fp 20 --fn 10 --tn 0 \
           --betas 0.5 1.0 2.0 3.0

5. Custom output path:
       python scripts/metrics.py --tp 380 --fp 20 --fn 10 --tn 0 \
           --out results/metrics/evaluation.txt

Default values
--------------
The defaults come from the internship report (post-hoc section):
  TP = 386   (400 reviewed − 14 wrong)
  FP =  14   (10 incorrect alignments + 4 removed as redundant)
  FN =  10   (correctly matched but rejected by scorer)
  TN =   0   (rejected pairs not reviewed in full)

All defaults can be overridden interactively or via flags.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config  # scripts/config.py

from analysis.metrics import (
    confusion_matrix,
    compute_metrics,
    format_report,
)


# ---------------------------------------------------------------------------
# Report defaults (from the internship report, post-hoc section)
# ---------------------------------------------------------------------------
# These are not in config.py because they are dataset-specific empirical
# results, not pipeline parameters.  They live here as named constants so
# the interactive prompt can display them clearly.

_DEFAULT_TP = 386   # 400 reviewed − 14 incorrect alignments/removals
_DEFAULT_FP = 14    # 10 incorrectly aligned + 4 removed as redundant
_DEFAULT_FN = 10    # 10 rejected pairs that were actually correct
_DEFAULT_TN = 0     # rejected pairs were not exhaustively reviewed

_DEFAULT_BETAS = [0.5, 1.0, 2.0]

_DEFAULT_TOTAL_CANDIDATES = 1157
_DEFAULT_TOTAL_ACCEPTED   = 747
_DEFAULT_TOTAL_REJECTED   = 410
_DEFAULT_SAMPLE_SIZE      = 400


# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

def _prompt_int(
    label: str,
    description: str,
    default: int,
    allow_float: bool = False,
) -> float:
    """
    Ask the user for a single confusion-matrix count.

    Displays the label, a one-line description of what the value means
    in this pipeline, and the current default in brackets.  Hitting
    Enter without typing accepts the default.

    Parameters
    ----------
    label        : short name shown in the prompt, e.g. "TP"
    description  : one-sentence explanation of what this count represents
    default      : pre-filled value (from internship report)
    allow_float  : if True, accept decimal values (for scaled FN estimates)
    """
    print()
    print(f"  {label} — {description}")
    print(f"  Default: {default}")

    while True:
        raw = input(f"  Enter {label} [press Enter to use {default}]: ").strip()
        if not raw:
            return float(default)
        try:
            value = float(raw)
            if value < 0:
                print("  Value must be >= 0.  Try again.")
                continue
            if not allow_float and value != int(value):
                print("  Value must be a whole number.  Try again.")
                continue
            return value
        except ValueError:
            print("  Invalid input.  Enter a number.")


def _prompt_notes() -> str:
    """Ask for optional free-text notes to embed in the report."""
    print()
    print("  Notes (optional) — describe your sampling method or")
    print("  any caveats about the FN estimate.  Leave blank to skip.")
    return input("  Notes: ").strip()


def _prompt_fn_method() -> str:
    """Ask how the FN estimate was derived."""
    print()
    print("  FN estimation method — how was the false-negative count determined?")
    print("  Examples:")
    print("    'manual spot-check of 50 rejected pairs, scaled to 410'")
    print("    'direct count from post-hoc review (internship report §3.3)'")
    default = "direct count from post-hoc corrections (internship report §3.3)"
    raw = input(f"  Method [press Enter to use default]: ").strip()
    return raw if raw else default


def _interactive_prompt(args: argparse.Namespace) -> argparse.Namespace:
    """
    Fill in any missing confusion-matrix values interactively.

    If the user already supplied a value via flag, it is shown but not
    re-prompted.  This allows partial pre-filling:
        python scripts/metrics.py --tp 380
    will prompt only for FP, FN, TN.

    The descriptions shown in the prompt are written for this pipeline
    specifically, so users don't need to remember the abstract definition.
    """
    print()
    print("=" * 60)
    print("  mt2iwn — Evaluation Metrics  (interactive input)")
    print("=" * 60)
    print()
    print("  Enter confusion-matrix counts for the scoring stage.")
    print("  Defaults are from the internship report (post-hoc section).")
    print("  Press Enter to accept a default, or type a new value.")

    descriptions = {
        "tp": (
            "pairs accepted by the algorithm AND confirmed correct by "
            "manual review  (True Positives)"
        ),
        "fp": (
            "pairs accepted by the algorithm BUT found wrong by review — "
            "includes incorrectly aligned synsets and redundant entries "
            "removed in post-hoc  (False Positives)"
        ),
        "fn": (
            "pairs rejected by the algorithm that were actually correct — "
            "can be a scaled estimate from a sub-sample of rejected pairs  "
            "(False Negatives)"
        ),
        "tn": (
            "pairs rejected by the algorithm AND confirmed wrong by review — "
            "enter 0 if rejected pairs were not exhaustively reviewed  "
            "(True Negatives)"
        ),
    }
    defaults = {
        "tp": _DEFAULT_TP,
        "fp": _DEFAULT_FP,
        "fn": _DEFAULT_FN,
        "tn": _DEFAULT_TN,
    }

    for field in ("tp", "fp", "fn", "tn"):
        current = getattr(args, field)
        if current is not None:
            # Already supplied via flag — confirm but don't re-prompt
            print()
            print(f"  {field.upper()} already set to {current} (from command-line flag)")
        else:
            value = _prompt_int(
                label=field.upper(),
                description=descriptions[field],
                default=defaults[field],
                allow_float=(field == "fn"),  # FN may be a scaled estimate
            )
            setattr(args, field, value)

    # ---- FN estimation method ----
    if args.fn_method is None:
        args.fn_method = _prompt_fn_method()

    # ---- optional notes ----
    if args.notes is None:
        args.notes = _prompt_notes()

    return args


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    default_out = os.path.join(
        getattr(config, "AUDIT_OUT_DIR", "results"),
        "evaluation_metrics.txt",
    )

    p = argparse.ArgumentParser(
        prog="metrics.py",
        description=(
            "Compute precision, recall, F1 / F-beta and related metrics "
            "for the mt2iwn scoring stage.  Missing values are prompted "
            "interactively if not supplied via flags."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ---- confusion matrix ----
    cm = p.add_argument_group(
        "confusion matrix",
        "Supply any or all counts via flags; missing ones will be prompted.",
    )
    cm.add_argument(
        "--tp", type=float, default=None, metavar="N",
        help="True positives (accepted + confirmed correct)."
    )
    cm.add_argument(
        "--fp", type=float, default=None, metavar="N",
        help="False positives (accepted + confirmed wrong)."
    )
    cm.add_argument(
        "--fn", type=float, default=None, metavar="N",
        help=(
            "False negatives (rejected + actually correct). "
            "Decimals accepted for scaled estimates."
        )
    )
    cm.add_argument(
        "--tn", type=float, default=None, metavar="N",
        help=(
            "True negatives (rejected + confirmed wrong). "
            "Use 0 if rejected pairs were not exhaustively reviewed."
        )
    )

    # ---- F-beta ----
    p.add_argument(
        "--betas", nargs="+", type=float, default=_DEFAULT_BETAS,
        metavar="BETA",
        help=(
            "Beta values for F-beta scores. "
            "beta<1 weights precision, beta>1 weights recall."
        )
    )

    # ---- context / report metadata ----
    ctx = p.add_argument_group(
        "report context",
        "Optional metadata embedded in the output report.",
    )
    ctx.add_argument(
        "--total-candidates", type=int,
        default=_DEFAULT_TOTAL_CANDIDATES, metavar="N",
        help="Total candidate pairs entering Stage 2."
    )
    ctx.add_argument(
        "--total-accepted", type=int,
        default=_DEFAULT_TOTAL_ACCEPTED, metavar="N",
        help="Pairs accepted by Stage 3 threshold filtering."
    )
    ctx.add_argument(
        "--total-rejected", type=int,
        default=_DEFAULT_TOTAL_REJECTED, metavar="N",
        help="Pairs rejected by Stage 3 threshold filtering."
    )
    ctx.add_argument(
        "--sample-size", type=int,
        default=_DEFAULT_SAMPLE_SIZE, metavar="N",
        help="Number of pairs in the manual validation sample."
    )
    ctx.add_argument(
        "--fn-method", type=str, default=None, metavar="TEXT",
        dest="fn_method",
        help="How the FN estimate was derived (embedded in report)."
    )
    ctx.add_argument(
        "--notes", type=str, default=None, metavar="TEXT",
        help="Free-text notes appended to the report (e.g. sampling caveats)."
    )

    # ---- output ----
    p.add_argument(
        "--out", default=default_out, metavar="PATH",
        help="Output .txt file path."
    )
    p.add_argument(
        "--no-interactive", action="store_true",
        help=(
            "Disable the interactive prompt entirely.  Missing values are "
            "filled with the defaults from the internship report instead of "
            "being prompted.  Useful for scripted / CI runs."
        )
    )

    return p


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # ---- fill missing values ----
    any_missing = any(
        getattr(args, f) is None for f in ("tp", "fp", "fn", "tn")
    )

    if any_missing and not args.no_interactive:
        args = _interactive_prompt(args)
    else:
        # Non-interactive: substitute defaults for any still-None values
        for field, default in (
            ("tp", _DEFAULT_TP),
            ("fp", _DEFAULT_FP),
            ("fn", _DEFAULT_FN),
            ("tn", _DEFAULT_TN),
        ):
            if getattr(args, field) is None:
                setattr(args, field, float(default))
        if args.fn_method is None:
            args.fn_method = (
                "direct count from post-hoc corrections (internship report §3.3)"
            )
        if args.notes is None:
            args.notes = ""

    # ---- compute ----
    try:
        cm = confusion_matrix(args.tp, args.fp, args.fn, args.tn)
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    metrics = compute_metrics(cm, betas=args.betas)

    meta = {
        "timestamp":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_candidates":    args.total_candidates,
        "total_accepted":      args.total_accepted,
        "total_rejected":      args.total_rejected,
        "sample_size":         args.sample_size,
        "fn_estimation_method": args.fn_method,
        "notes":               args.notes,
    }

    report = format_report(cm, metrics, meta)

    # ---- write ----
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)

    # ---- console summary ----
    p  = metrics["precision"]
    r  = metrics["recall"]
    f1 = metrics["f_scores"].get(1.0)

    def _fmt(v):
        return f"{v:.2f}" if v is not None else "undefined"

    print()
    print("=" * 50)
    print("  METRICS SUMMARY")
    print("=" * 50)
    print(f"  TP: {cm['tp']:.0f}   FP: {cm['fp']:.0f}   "
          f"FN: {cm['fn']:.0f}   TN: {cm['tn']:.0f}")
    print()
    print(f"  Precision  : {_fmt(p)}")
    print(f"  Recall     : {_fmt(r)}")
    print(f"  Error rate : {_fmt(metrics['error_rate'])}")
    for beta, score in sorted(metrics["f_scores"].items()):
        print(f"  F{beta:<5}    : {_fmt(score)}")
    print()
    print(f"  Report written to: {args.out}")
    print("=" * 50)
    print()


if __name__ == "__main__":
    main()
