"""
XML retrieval utilities — word meanings, IDs, glosses, and relation IDs.
"""

import xml.etree.ElementTree as ET


def retrieve_wm(root):
    return {(word.find('.//LITERAL').get('LEMMA'), word.find('.//LITERAL').get('SENSE')): word for word in root.findall('.//WORD_MEANING')}


def find_word_meaning_in_root(root, lemma, sense):
    """
    Utility function to find a word meaning in a given XML root by lemma and sense.
    """
    for wm in root.findall('.//WORD_MEANING'):
        for literal in wm.findall('.//LITERAL'):
            if literal.get('LEMMA') == lemma and literal.get('SENSE') == sense:
                return wm
    return None


def get_new_id(existing_ids):
    numeric_ids = [int(id.split('#')[1]) for id in existing_ids if '#' in id and id.split('#')[1].isdigit()]
    return max(numeric_ids, default=0) + 1


def get_gloss_from_italwn(lemma, sense, root, pos=None):
    for word in root.findall('.//WORD_MEANING'):
        literal = word.find('.//LITERAL')
        word_pos = word.get('PART_OF_SPEECH')
        if literal is not None and literal.get('LEMMA') == lemma and literal.get('SENSE') == sense and (pos is None or word_pos == pos):
            gloss_element = word.find('.//GLOSS')
            if gloss_element is not None and gloss_element.text:
                return gloss_element.text.strip()
    return None


def extract_target_ids(root):
    return {(word.find('.//LITERAL').get('LEMMA'), word.find('.//LITERAL').get('SENSE')): word.get('ID') for word in root.findall('.//WORD_MEANING')}


def retrieve_relation_ids(iwn_root):
    return {
        rel.get('TYPE'): {'ID': rel.get('ID'), 'INV_ID': rel.get('INV_ID')}
        for rel in iwn_root.findall('.//RELATION') if rel.get('ID') and rel.get('INV_ID')
    }