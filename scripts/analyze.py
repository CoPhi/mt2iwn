#!/usr/bin/env python3
"""
CLI: Post-hoc analysis of the merged IWN file.

Detects ID conflicts between original and merged IWN, reports the next
available WORD_MEANING ID, and identifies new/updated synsets.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
from scripts.analysis import (
    extract_ids_and_lemmas,
    compare_files,
    get_last_word_meaning_id,
    identify_updates_in_iwn,
)


def main():
    parser = argparse.ArgumentParser(description="Post-hoc analysis of merged IWN")
    parser.add_argument('--iwn-original', default=Paths.IWN, help='Original IWN XML')
    parser.add_argument('--iwn-merged', default=Paths.IWN_PRE_MOD, help='Merged IWN XML')
    parser.add_argument('--iwn-post-mm', default=Paths.IWN_POST_MM, help='Post-merge IWN XML (for ID check)')
    args = parser.parse_args()

    print("=" * 70)
    print("POST-HOC ANALYSIS")
    print("=" * 70)

    print("\n--- ID Conflict Detection ---")
    file1_data = extract_ids_and_lemmas(args.iwn_original)
    file2_data = extract_ids_and_lemmas(args.iwn_merged)
    compare_files(file1_data, file2_data)

    print("\n--- Next Available WORD_MEANING ID ---")
    last_id = get_last_word_meaning_id(args.iwn_post_mm)
    print(f"Next ID to add: {last_id}")

    print("\n--- New and Updated Synsets ---")
    updated_synsets, new_synsets, new_wm_info, newly_added_relations = identify_updates_in_iwn(
        args.iwn_original, args.iwn_post_mm
    )

    print("\nNew Synsets:")
    for lemma, sense in new_wm_info:
        print(f"  Lemma: {lemma}, Sense: {sense}")

    print("\nNewly Added Relations:")
    for rel_type, target_lemma, target_sense, lemma, sense, target_id, synset_id in newly_added_relations:
        print(f"  Type: {rel_type}, Target: {target_lemma} ({target_sense}), "
              f"Source: {lemma} ({sense}), Target ID: {target_id}, Synset ID: {synset_id}")

    print(f"\n{'=' * 70}")
    print("✓ Analysis complete")
    print("=" * 70)


if __name__ == '__main__':
    main()