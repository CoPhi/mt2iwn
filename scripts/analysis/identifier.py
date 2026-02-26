"""
Identifies new synsets and newly added relations between the original
and finalized IWN XML files.
"""

import xml.etree.ElementTree as ET
from scripts.config import Config


def extract_internal_links(wm):
    """Extract all relations in INTERNAL_LINKS."""
    return {(rel.get('TYPE'), rel.find('.//TARGET_WM').get('LEMMA'), rel.find('.//TARGET_WM').get('SENSE'), rel.find('.//TARGET_WM').get('ID')): rel
            for rel in wm.findall('.//INTERNAL_LINKS//RELATION')}


def identify_updates_in_iwn(ItalWN, plug_att):
    updated_synsets = []
    new_synsets = []
    new_word_meanings_info = []
    newly_added_relations_info = []

    # Parsing the XML files
    original_tree = ET.parse(ItalWN)
    original_root = original_tree.getroot()

    finalized_tree = ET.parse(plug_att)
    finalized_root = finalized_tree.getroot()

    # Dictionary of original word meanings
    original_word_meanings = {
        (wm.find('.//LITERAL').get('LEMMA'), wm.find('.//LITERAL').get('SENSE')): wm
        for wm in original_root.findall('.//WORD_MEANING')
    }

    # Iterating through finalized word meanings
    for finalized_wm in finalized_root.findall('.//WORD_MEANING'):
        lemma = finalized_wm.find('.//LITERAL').get('LEMMA')
        sense = finalized_wm.find('.//LITERAL').get('SENSE')
        synset_id = finalized_wm.get('ID')  # Get the ID of the current synset

        if (lemma, sense) not in original_word_meanings:
            new_synsets.append({
            'LEMMA': lemma,
            'SENSE': sense,
            'ID': synset_id,
            })
            new_word_meanings_info.append((lemma, sense))
        else:
            original_wm = original_word_meanings[(lemma, sense)]

            original_internal_links = extract_internal_links(original_wm)
            finalized_internal_links = extract_internal_links(finalized_wm)

            # Identify new relations that are present in the finalized version but not in the original
            new_relations = {
                key: finalized_internal_links[key]
                for key in finalized_internal_links
                if key not in original_internal_links and key[0] in Config.ALLOWED_RELATION_TYPES
            }

            if new_relations:
                updated_synsets.append({
                    'LEMMA': lemma,
                    'SENSE': sense,
                    'ID': synset_id,
                    'NEW_RELATIONS': new_relations  # Store relations as a dictionary
                })
                for rel_key in new_relations.keys():
                    target_id = rel_key[3]  # This is the ID of the TARGET_WM
                    newly_added_relations_info.append((rel_key[0], rel_key[1], rel_key[2], lemma, sense, target_id, synset_id))

    return updated_synsets, new_synsets, new_word_meanings_info, newly_added_relations_info