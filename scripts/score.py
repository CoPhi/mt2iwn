#!/usr/bin/env python3
"""
CLI: Score shared candidates and produce breakdown CSV.

Reads candidates.csv, computes gloss and relation similarity for each
MariTerm / ItalWordNet pair, and writes the scored results to breakdown.csv.

Outputs (Stage 2)
-----------------
breakdown.csv              — 747 accepted rows (unchanged, feeds filter.py)
breakdown_rejected.csv     — 410 rejected rows (NEW, same column layout)
matched_breakdown.txt      — full score blocks for accepted pairs (NEW)
rejected_breakdown.txt     — full score blocks for rejected pairs (NEW)
"""

import argparse
import csv                          # NEW
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths, parse_xml
from scripts.similarity import normalize_text
from scripts.matching import (
    extract_word_meanings,
    match_lemmas_with_alternate_senses,
    print_and_return_best_match,
    format_results,
    print_formatted_results,
    save_entries,
    store_to_csv,
)
from scripts.matching.report import write_breakdown_txts   # NEW


# ---------------------------------------------------------------------------
# NEW: write breakdown_rejected.csv
# ---------------------------------------------------------------------------

def _store_rejected_to_csv(rejected_rows: list[dict], path: str) -> None:
    """
    Write the rejected candidate pairs to a CSV in the same column layout as
    breakdown.csv so that audit.py and report.py can treat both files uniformly.

    Parameters
    ----------
    rejected_rows : list[dict]
        Raw current_match dicts from matcher.py that failed all three gates.
    path : str
        Output file path (parent directory created if absent).
    """
    if not rejected_rows:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rejected_rows[0].keys(),
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected_rows)


# ---------------------------------------------------------------------------
# Scoring (modified to also return rejected rows)
# ---------------------------------------------------------------------------

def score_candidates(MariT, ItalWN, candidates_file):
    """
    Score all candidates and print the accepted matches to the terminal.

    Returns
    -------
    rejected : list[dict]
        Raw current_match dicts for pairs that failed all threshold gates.
        Used by main() to write breakdown_rejected.csv and the .txt files.
    """
    import pandas as pd

    mari_term_wms = extract_word_meanings(parse_xml(MariT))
    ital_wn_wms = extract_word_meanings(parse_xml(ItalWN))

    candidate_lemmas = (
        pd.read_csv(candidates_file, delimiter=";")['Shared Lemma']
        .str.lower()
        .apply(normalize_text)
        .tolist()
    )

    mari_term_wms = [
        wm for wm in mari_term_wms
        if any(nl in candidate_lemmas for nl in wm['normalized_lemmas'])
    ]
    ital_wn_wms = [
        wm for wm in ital_wn_wms
        if any(nl in candidate_lemmas for nl in wm['normalized_lemmas'])
    ]

    # NEW: pass return_rejected=True to capture pairs that failed the gates
    results, rejected_tuples = match_lemmas_with_alternate_senses(
        mari_term_wms, ital_wn_wms,
        return_rejected=True,
    )

    print_and_return_best_match(results)   # unchanged — prints accepted to terminal

    # Unwrap (match_dict, []) tuples → plain dicts for CSV / report writing
    rejected = [match for match, _ in rejected_tuples]   # NEW
    return rejected                                       # NEW


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Score MariTerm / ItalWordNet candidates"
    )
    parser.add_argument('--marit',      default=Paths.MARIT,
                        help='Path to MariTerm XML file')
    parser.add_argument('--iwn',        default=Paths.IWN,
                        help='Path to ItalWordNet XML file')
    parser.add_argument('--candidates', default=Paths.CANDIDATES_CSV,
                        help='Candidates CSV (input)')
    parser.add_argument('--output',     default=Paths.BREAKDOWN_CSV,
                        help='Breakdown CSV (output, accepted pairs)')
    # NEW argument ↓
    parser.add_argument('--rejected-output', default=Paths.BREAKDOWN_REJECTED_CSV,
                        help='Breakdown CSV for rejected pairs (output)')
    # NEW argument ↓
    parser.add_argument('--report-dir', default=Paths.BREAKDOWN_REPORT_DIR,
                        help='Directory for matched_breakdown.txt / rejected_breakdown.txt')
    args = parser.parse_args()

    print("=" * 70)
    print("SCORING CANDIDATES")
    print("=" * 70)
    print(f"MariTerm file:      {args.marit}")
    print(f"ItalWordNet file:   {args.iwn}")
    print(f"Candidates CSV:     {args.candidates}")
    print(f"Output CSV:         {args.output}")
    print(f"Rejected CSV:       {args.rejected_output}")   # NEW
    print(f"Report directory:   {args.report_dir}")        # NEW
    print()

    # score_candidates now also returns the rejected rows
    rejected = score_candidates(args.marit, args.iwn, args.candidates)   # MODIFIED

    formatted = format_results(args.marit, args.iwn, args.candidates)
    if formatted:
        print_formatted_results(formatted)
        store_to_csv(formatted, args.output)   # unchanged — writes breakdown.csv
        print(f"\n{'=' * 70}")
        print(f"✓ Breakdown written to {args.output}")

        # NEW: write rejected CSV
        _store_rejected_to_csv(rejected, args.rejected_output)
        print(f"✓ Rejected breakdown written to {args.rejected_output}")

        # NEW: write .txt score-block reports
        # accepted_rows: unwrap from format_results' dict list (already plain dicts)
        # rejected_rows: plain dicts from score_candidates()
        matched_txt, rejected_txt = write_breakdown_txts(
            accepted_rows=formatted,
            rejected_rows=rejected,
            out_dir=args.report_dir,
        )
        print(f"✓ Matched report:  {matched_txt}")
        print(f"✓ Rejected report: {rejected_txt}")
        print("=" * 70)
    else:
        print("No results were generated.")


if __name__ == '__main__':
    main()