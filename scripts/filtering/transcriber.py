"""
Transcription of matched MariTerm / ItalWordNet pairs to filtered XML files.
"""

import csv
import xml.etree.ElementTree as ET

from .validator import validate_xml
from .filter import filter_wm
from .matcher import match_lemmas


def transcribe_matched_pairs(matched_pairs, filt_mart, filt_iwn):
    mari_term_root = ET.Element("WN")
    ital_wn_root = ET.Element("WN")

    for mari_element, ital_element in matched_pairs:
        mari_term_root.append(mari_element)
        ital_wn_root.append(ital_element)

    mari_term_tree = ET.ElementTree(mari_term_root)
    mari_term_tree.write(filt_mart, encoding="utf-8", xml_declaration=True)

    ital_wn_tree = ET.ElementTree(ital_wn_root)
    ital_wn_tree.write(filt_iwn, encoding="utf-8", xml_declaration=True)


def transcribe_candidates(MariT, ItalWN, candidates_file, filt_mart, filt_iwn):
    if not validate_xml(MariT) or not validate_xml(ItalWN):
        return

    mari_term_wms = filter_wm(ET.parse(MariT).getroot())
    ital_wn_wms = filter_wm(ET.parse(ItalWN).getroot())

    # Read the CSV file to extract the lemmas and their corresponding senses
    csv_entries = []
    with open(candidates_file, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            csv_entries.append({
                'literal_lemma': row['Literal Lemma'],
                'mari_t_sense': row.get('MariT sense', 'N/A'),
                'iwn_sense': row.get('IWN sense', 'N/A')
            })

    matched_pairs = match_lemmas(mari_term_wms, ital_wn_wms, csv_entries)
    transcribe_matched_pairs(matched_pairs, filt_mart, filt_iwn)
    print(f"Total matched pairs transcribed: {len(matched_pairs)}")