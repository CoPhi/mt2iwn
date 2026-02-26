"""
Word meaning creation and merging for ItalWordNet update.
"""

import xml.etree.ElementTree as ET

from .retriever import find_word_meaning_in_root, get_new_id
from .cleaner import clean_target_wm_id
import scripts.updating as state  # shared mutable state


def determine_inverse_relation(rel_type):
    inverse_map = {
        "has_hyperonym": "has_hyponym",
        "has_hyponym": "has_hyperonym",
        "near_synonym": "near_synonym",
        "has_xpos_hyperonym": "has_xpos_hyponym",
        "has_xpos_hyponym": "has_xpos_hyperonym",
        "xpos_near_synonym": "xpos_near_synonym"
    }
    return inverse_map.get(rel_type, rel_type)


def extract_eq_links_and_top_onto(root):
    eq_links, top_onto = {}, {}
    for word in root.findall('.//WORD_MEANING'):
        key = (word.find('.//LITERAL').get('LEMMA'), word.find('.//LITERAL').get('SENSE'))

        # Explicitly check if the elements exist
        eq_link_elem = word.find('.//EQ_LINKS')
        top_onto_elem = word.find('.//TOP_ONTO')

        eq_links[key] = eq_link_elem if eq_link_elem is not None else ET.Element('EQ_LINKS')
        top_onto[key] = top_onto_elem if top_onto_elem is not None else ET.Element('TOP_ONTO')

    return eq_links, top_onto


def merge_sections(existing_section, new_section):
    existing_relations = {ET.tostring(rel) for rel in existing_section.findall('.//RELATION')}
    for new_rel in new_section.findall('.//RELATION'):
        if ET.tostring(new_rel) not in existing_relations:
            # Clean the IDs in the TARGET_WM elements
            for target_wm in new_rel.findall('.//TARGET_WM'):
                clean_target_wm_id(target_wm)
            existing_section.append(new_rel)


def create_or_merge_word_meaning(lemma, sense, existing_ids, mari_eq_links, mari_top_onto, iwn_root, back_references=[], relation_ids=None, gloss="", add_lfeatures_due_to_hyponym=False, add_lfeatures_due_to_non_compliance=False, original_iwn_root=None):
    state.updated_entries.add((lemma, sense))
    word_meaning = find_word_meaning_in_root(iwn_root, lemma, sense)
    if word_meaning is None:
        word_meaning = find_word_meaning_in_root(original_iwn_root, lemma, sense)

    if word_meaning is not None:
        word_meaning_id = word_meaning.get('ID')
        gloss_element = word_meaning.find('.//GLOSS')
        original_gloss = gloss_element.text.strip() if gloss_element is not None and gloss_element.text else ''

        if original_gloss != gloss:
            if gloss_element is None:
                gloss_element = ET.SubElement(word_meaning, 'GLOSS')
            gloss_element.text = gloss
        return word_meaning, word_meaning_id

    pos_prefix = back_references[0]['part_of_speech'] if back_references else "N"
    new_id = get_new_id(existing_ids)
    word_meaning_id = f"{pos_prefix}#{new_id}"
    existing_ids.add(word_meaning_id)

    word_meaning = ET.Element('WORD_MEANING', ID=word_meaning_id, PART_OF_SPEECH=pos_prefix)
    gloss_element = ET.SubElement(word_meaning, 'GLOSS')
    gloss_element.text = gloss

    variants = ET.SubElement(word_meaning, 'VARIANTS')
    literal_node = ET.SubElement(variants, 'LITERAL', LEMMA=lemma, SENSE=str(sense))

    if add_lfeatures_due_to_hyponym or add_lfeatures_due_to_non_compliance:
        ET.SubElement(literal_node, 'LFEATURES', SUBLANGUAGE="mar")

    internal_links = ET.SubElement(word_meaning, 'INTERNAL_LINKS')
    eq_links_section = ET.SubElement(word_meaning, 'EQ_LINKS')
    top_onto_section = ET.SubElement(word_meaning, 'TOP_ONTO')

    iwn_root.append(word_meaning)
    state.new_word_meanings.append(lemma)

    key = (lemma, sense)
    if key in mari_eq_links:
        merge_sections(eq_links_section, mari_eq_links[key])
    if key in mari_top_onto:
        merge_sections(top_onto_section, mari_top_onto[key])

    for ref in back_references:
        rel_type, target_lemma = ref['inverse_relation'], ref['lemma']
        section = internal_links if not rel_type.startswith('eq_') else eq_links_section
        existing_relations = {
            (rel.get('TYPE'), rel.find('.//TARGET_WM').get('LEMMA')): rel
            for rel in section.findall('.//RELATION')
        }

        if (rel_type, target_lemma) not in existing_relations:
            rel_id, inv_id = relation_ids.get(rel_type, {}).get('ID', 'UNKNOWN'), relation_ids.get(rel_type, {}).get('INV_ID', 'UNKNOWN')
            new_rel = ET.SubElement(section, 'RELATION', TYPE=rel_type, ID=rel_id, INV_ID=inv_id)

            target_wm = ET.SubElement(new_rel, 'TARGET_WM', ID=ref['id'], PART_OF_SPEECH=ref['part_of_speech'], LEMMA=ref['lemma'], SENSE=ref['sense'])
            clean_target_wm_id(target_wm)  # Ensure the ID is cleaned

            if ref.get('gloss'):
                target_wm.set('GLOSS', ref['gloss'])

    return word_meaning, word_meaning_id