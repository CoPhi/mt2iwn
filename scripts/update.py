#!/usr/bin/env python3
"""
CLI: Update ItalWordNet with MariTerm entries.

Reads the breakdown CSV, selects candidates via multi-threshold logic,
creates or merges word meanings and relations, and writes the updated IWN XML.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
import scripts.updating as updating
from scripts.updating import (
    read_lemmas_from_csv,
    update_iwn_entries,
    replace_gloss_with_original,
    clean_existing_target_wm_ids,
    remove_duplicate_relations,
)


def main():
    parser = argparse.ArgumentParser(description="Update ItalWordNet with MariTerm entries")
    parser.add_argument('--marit-filtered', default=Paths.FILT_MART, help='Filtered MariTerm XML')
    parser.add_argument('--iwn-filtered', default=Paths.FILT_IWN, help='Filtered IWN XML')
    parser.add_argument('--marit-original', default=Paths.MARIT, help='Original MariTerm XML')
    parser.add_argument('--iwn-original', default=Paths.IWN, help='Original IWN XML')
    parser.add_argument('--breakdown', default=Paths.BREAKDOWN_CSV, help='Breakdown CSV (input)')
    parser.add_argument('--output', default=Paths.UPDATES, help='Updated IWN XML (output)')
    args = parser.parse_args()

    print("=" * 70)
    print("UPDATING IWN")
    print("=" * 70)
    print(f"MariTerm filtered:  {args.marit_filtered}")
    print(f"IWN filtered:       {args.iwn_filtered}")
    print(f"MariTerm original:  {args.marit_original}")
    print(f"IWN original:       {args.iwn_original}")
    print(f"Breakdown CSV:      {args.breakdown}")
    print(f"Output:             {args.output}")
    print()

    # Reset shared mutable state
    updating.replaced_glosses.clear()
    updating.new_word_meanings.clear()
    updating.updated_entries.clear()

    selected_lemmas = read_lemmas_from_csv(args.breakdown)

    mari_root = ET.parse(args.marit_filtered).getroot()
    iwn_root = ET.parse(args.iwn_filtered).getroot()
    original_mari_root = ET.parse(args.marit_original).getroot()
    original_iwn_root = ET.parse(args.iwn_original).getroot()

    updated_entries = updating.updated_entries

    update_iwn_entries(selected_lemmas, mari_root, iwn_root, original_mari_root, original_iwn_root)
    replace_gloss_with_original(iwn_root, original_iwn_root, updated_entries)
    clean_existing_target_wm_ids(iwn_root)
    remove_duplicate_relations(iwn_root)

    ET.ElementTree(iwn_root).write(args.output, encoding='utf-8', xml_declaration=True)

    print(f"\n{'=' * 70}")
    print(f"✓ Updated IWN written to {args.output}")
    print("=" * 70)


if __name__ == '__main__':
    main()