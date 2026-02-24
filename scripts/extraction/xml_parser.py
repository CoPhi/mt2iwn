"""
XML parsing functionality for MariTerm and ItalWordNet files.
"""

import xml.etree.ElementTree as ET


def extract_lemmas(file_path):
    """
    Extract literal lemmas and their details from an XML file.
    
    Args:
        file_path (str): Path to the XML file (MariTerm or ItalWordNet)
    
    Returns:
        dict: Dictionary mapping literal lemmas to their WORD_MEANING IDs
              Format: {lemma: word_meaning_id}
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    lemmas_with_details = {}

    for word_meaning in root.findall('.//WORD_MEANING'):
        word_meaning_id = word_meaning.get('ID')
        literal = word_meaning.find('.//VARIANTS//LITERAL')
        literal_lemma = literal.get('LEMMA') if literal is not None else None
        if literal_lemma:
            lemmas_with_details[literal_lemma] = word_meaning_id

    return lemmas_with_details
