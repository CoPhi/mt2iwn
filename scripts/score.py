#!/usr/bin/env python3
"""
CLI: Score shared candidates and produce breakdown CSV.

Reads candidates.csv, computes gloss and relation similarity for each
MariTerm / ItalWordNet pair, and writes the scored results to breakdown.csv.
"""

import argparse
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


def score_candidates(MariT, ItalWN, candidates_file):
    import pandas as pd
    from scripts.config import parse_xml

    mari_term_wms = extract_word_meanings(parse_xml(MariT))
    ital_wn_wms = extract_word_meanings(parse_xml(ItalWN))

    candidate_lemmas = pd.read_csv(candidates_file, delimiter=";")['Shared Lemma'].str.lower().apply(normalize_text).tolist()

    mari_term_wms = [wm for wm in mari_term_wms if any(normalized_lemma in candidate_lemmas for normalized_lemma in wm['normalized_lemmas'])]
    ital_wn_wms = [wm for wm in ital_wn_wms if any(normalized_lemma in candidate_lemmas for normalized_lemma in wm['normalized_lemmas'])]

    results = match_lemmas_with_alternate_senses(mari_term_wms, ital_wn_wms)
    print_and_return_best_match(results)


def main():
    parser = argparse.ArgumentParser(description="Score MariTerm / ItalWordNet candidates")
    parser.add_argument('--marit', default=Paths.MARIT, help='Path to MariTerm XML file')
    parser.add_argument('--iwn', default=Paths.IWN, help='Path to ItalWordNet XML file')
    parser.add_argument('--candidates', default=Paths.CANDIDATES_CSV, help='Candidates CSV (input)')
    parser.add_argument('--output', default=Paths.BREAKDOWN_CSV, help='Breakdown CSV (output)')
    args = parser.parse_args()

    print("=" * 70)
    print("SCORING CANDIDATES")
    print("=" * 70)
    print(f"MariTerm file:   {args.marit}")
    print(f"ItalWordNet file:{args.iwn}")
    print(f"Candidates CSV:  {args.candidates}")
    print(f"Output CSV:      {args.output}")
    print()

    score_candidates(args.marit, args.iwn, args.candidates)

    formatted = format_results(args.marit, args.iwn, args.candidates)
    if formatted:
        print_formatted_results(formatted)
        store_to_csv(formatted, args.output)
        print(f"\n{'=' * 70}")
        print(f"✓ Breakdown written to {args.output}")
        print("=" * 70)
    else:
        print("No results were generated.")


if __name__ == '__main__':
    main()