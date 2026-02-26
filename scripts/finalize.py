#!/usr/bin/env python3
"""
CLI: Finalize IWN and MariTerm by adding bidirectional PLUG-IN_LINKS.

Retrieves missing glosses for new synsets, adds plugin links from IWN to
MariTerm and vice versa, removes duplicates, and saves the finalized XML files.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
from scripts.analysis import identify_updates_in_iwn
from scripts.plugin import (
    find_glosses_for_new_synsets,
    display_results,
    update_glosses_in_xml,
    load_csv_data,
    add_plugins,
    sort_plugin_links,
    remove_duplicate_plugins,
    ensure_plugin_links,
    update_plugin_links,
)
from scripts.merging import save_pretty_xml


def main():
    parser = argparse.ArgumentParser(description="Finalize IWN and MariTerm with PLUG-IN_LINKS")
    parser.add_argument('--iwn-original', default=Paths.IWN, help='Original IWN XML')
    parser.add_argument('--iwn-post-mm', default=Paths.IWN_POST_MM, help='Post-merge IWN XML')
    parser.add_argument('--iwn-mm-glosses', default=Paths.IWN_MM_W_GLOSSES, help='IWN with glosses added (intermediate)')
    parser.add_argument('--marit', default=Paths.MARIT, help='Original MariTerm XML')
    parser.add_argument('--marit-filtered', default=Paths.FILT_MART, help='Filtered MariTerm XML')
    parser.add_argument('--breakdown', default=Paths.BREAKDOWN_CSV, help='Breakdown CSV')
    parser.add_argument('--output-iwn', default=Paths.FINALIZED_IWN, help='Finalized IWN XML (output)')
    parser.add_argument('--output-marit', default=Paths.FINALIZED_MARIT, help='Finalized MariTerm XML (output)')
    args = parser.parse_args()

    print("=" * 70)
    print("FINALIZING IWN AND MARIT WITH PLUGIN LINKS")
    print("=" * 70)

    # Step 1: Identify updates in IWN
    print("\n[1/5] Identifying new synsets and newly added relations...")
    updated_synsets, new_synsets, new_wm_info, newly_added_relations_info = identify_updates_in_iwn(
        args.iwn_original, args.iwn_post_mm
    )

    # Build structured_relations from newly_added_relations_info
    structured_relations = []
    for rel_info in newly_added_relations_info:
        rel_type, target_lemma, target_sense, source_lemma, source_sense, target_id, source_synset_id = rel_info
        existing_entry = next((entry for entry in structured_relations if entry['WORD_MEANING_ID'] == source_synset_id), None)
        if existing_entry:
            existing_entry['RELATIONS'].append({
                'RELATION_TYPE': rel_type,
                'TARGET_WM_ID': target_id,
                'TARGET_WM_LEMMA': target_lemma,
                'SENSE': target_sense
            })
        else:
            structured_relations.append({
                'WORD_MEANING_ID': source_synset_id,
                'LITERAL': source_lemma,
                'SENSE': source_sense,
                'RELATIONS': [{
                    'RELATION_TYPE': rel_type,
                    'TARGET_WM_ID': target_id,
                    'TARGET_WM_LEMMA': target_lemma,
                    'SENSE': target_sense
                }]
            })

    # Step 2: Find and update glosses for new synsets
    print("\n[2/5] Updating glosses for new synsets...")
    results = find_glosses_for_new_synsets(args.iwn_post_mm, new_synsets)
    display_results(results)
    update_glosses_in_xml(args.iwn_post_mm, results, args.iwn_mm_glosses)

    # Step 3: Add PLUG-IN_LINKS to IWN synsets
    print("\n[3/5] Adding PLUG-IN_LINKS to IWN synsets...")
    iwn_root = ET.parse(args.iwn_mm_glosses).getroot()
    mariterm_filtered_root = ET.parse(args.marit_filtered).getroot()
    mariterm_original_root = ET.parse(args.marit).getroot()
    reference = load_csv_data(args.breakdown)

    synset_relations_storage, iwn_synsets_with_plugins = add_plugins(
        iwn_root, mariterm_filtered_root, mariterm_original_root, reference, newly_added_relations_info
    )

    for wm in iwn_root.findall('.//WORD_MEANING'):
        plugin_links = wm.find('.//PLUG-IN_LINKS')
        if plugin_links is not None:
            sort_plugin_links(plugin_links)

    remove_duplicate_plugins(iwn_root)
    ensure_plugin_links(iwn_root)

    # Step 4: Save finalized IWN
    print("\n[4/5] Saving finalized IWN...")
    tree = ET.ElementTree(iwn_root)
    tree.write(args.output_iwn, encoding='utf-8', xml_declaration=True)
    save_pretty_xml(tree, args.output_iwn)

    # Step 5: Update MariTerm PLUG-IN_LINKS and save
    print("\n[5/5] Updating MariTerm PLUG-IN_LINKS and saving...")
    update_plugin_links(iwn_root, mariterm_original_root, synset_relations_storage, iwn_synsets_with_plugins, structured_relations)
    m_tree = ET.ElementTree(mariterm_original_root)
    save_pretty_xml(m_tree, args.output_marit)

    print(f"\n{'=' * 70}")
    print(f"✓ Finalized IWN written to    {args.output_iwn}")
    print(f"✓ Finalized MariTerm written to {args.output_marit}")
    print("=" * 70)


if __name__ == '__main__':
    main()