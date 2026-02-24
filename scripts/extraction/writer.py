"""
CSV writing functionality for shared lemmas.
"""

import csv


def write_csv(shared_lemmas, MariT_lemmas, IWN_lemmas, file_name):
    """
    Write shared lemmas to a CSV file.
    
    Args:
        shared_lemmas (set): Set of lemmas present in both resources
        MariT_lemmas (dict): MariTerm lemmas with their WORD_MEANING IDs
        IWN_lemmas (dict): ItalWordNet lemmas with their WORD_MEANING IDs
        file_name (str): Output CSV file path
    
    Output CSV format:
        Shared Lemma; IWN_WM_ID; MarT_WM_ID
    """
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Shared Lemma', 'IWN_WM_ID', 'MarT_WM_ID'])
        for lemma in sorted(shared_lemmas, key=lambda x: x.lower()):
            writer.writerow([lemma, IWN_lemmas[lemma], MariT_lemmas[lemma]])
