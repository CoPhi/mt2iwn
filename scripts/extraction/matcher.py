"""
Matching functionality for finding shared lemmas between resources.
"""

from .xml_parser import extract_lemmas


def find_shared(MariT_file, IWN_file):
    """
    Find shared literal lemmas between two resources.
    
    Args:
        MariT_file (str): Path to MariTerm XML file
        IWN_file (str): Path to ItalWordNet XML file
    
    Returns:
        tuple: (shared_lemmas, MariT_lemmas, IWN_lemmas)
            - shared_lemmas (set): Set of lemmas present in both resources
            - MariT_lemmas (dict): All MariTerm lemmas with their IDs
            - IWN_lemmas (dict): All ItalWordNet lemmas with their IDs
    """
    MariT_lemmas = extract_lemmas(MariT_file)
    IWN_lemmas = extract_lemmas(IWN_file)

    shared_lemmas = set(MariT_lemmas.keys()).intersection(set(IWN_lemmas.keys()))
    print(f"Total extracted lemmas: {len(shared_lemmas)}")

    return shared_lemmas, MariT_lemmas, IWN_lemmas
