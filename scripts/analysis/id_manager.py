"""
Retrieves the highest numeric WORD_MEANING ID from an IWN XML file.
"""

import xml.etree.ElementTree as ET


def get_last_word_meaning_id(file):
    """
    This function reads an XML file and returns the highest numeric ID of a Word Meaning (WM).
    """
    tree = ET.parse(file)
    root = tree.getroot()

    # Initialize the highest ID variable
    max_id = 0

    # Iterate through all WORD_MEANING elements
    for word_meaning in root.findall('.//WORD_MEANING'):
        wm_id = word_meaning.get('ID')
        if wm_id and '#' in wm_id:
            # Extract the numeric part of the ID
            numeric_id = int(wm_id.split('#')[-1])
            # Update max_id if the current one is higher
            if numeric_id > max_id:
                max_id = numeric_id

    return max_id + 1