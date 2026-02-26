"""
ID conflict detection between two IWN XML files.
"""

import xml.etree.ElementTree as ET


def extract_ids_and_lemmas(xml_file):
    """Extracts IDs and LEMMA values from the XML file."""
    data = {}

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Iterate through each WORD_MEANING element
    for word_meaning in root.findall('.//WORD_MEANING'):
        # Extract the numerical ID and LEMMA
        word_id = word_meaning.get('ID').split('#')[1]  # Extract the numerical part
        lemma = word_meaning.find('.//VARIANTS/LITERAL').get('LEMMA')

        # Store in dictionary with ID as key and lemma as value (store as a list for handling multiple lemmas)
        if word_id not in data:
            data[word_id] = []
        data[word_id].append(lemma)

    return data


def compare_files(file1_data, file2_data):
    """Compares IDs and LEMMAs between two files and prints pairs where ID matches but lemmas differ."""
    # Combine data from both files
    all_data = {**file1_data, **file2_data}

    # Check for matching IDs with different LEMMAs
    for word_id, lemmas in all_data.items():
        if len(lemmas) > 1:  # Only consider IDs with more than one lemma
            lemmas_set = set(lemmas)  # Use set to remove duplicates
            if len(lemmas_set) > 1:  # If there are different lemmas for the same ID
                print(f"{word_id}, {lemmas[0]} | {word_id}, {', '.join(lemmas_set - {lemmas[0]})} ")