"""
Entry saving and CSV export for matched MariTerm / ItalWordNet results.
"""

import pandas as pd
from scripts.config import parse_xml
from scripts.similarity import normalize_text
from .extractor import extract_word_meanings
from .matcher import match_lemmas_with_alternate_senses


def save_entries(MariT, ItalWN, breakdown_csv):
    mari_term_wms = extract_word_meanings(parse_xml(MariT))
    ital_wn_wms = extract_word_meanings(parse_xml(ItalWN))

    candidate_lemmas = set(pd.read_csv(breakdown_csv, delimiter=';')['Shared Lemma'].str.lower().apply(normalize_text))

    mari_term_wms = [wm for wm in mari_term_wms if any(normalized_lemma in candidate_lemmas for normalized_lemma in wm['normalized_lemmas'])]
    ital_wn_wms = [wm for wm in ital_wn_wms if any(normalized_lemma in candidate_lemmas for normalized_lemma in wm['normalized_lemmas'])]

    results = match_lemmas_with_alternate_senses(mari_term_wms, ital_wn_wms)

    mari_term_id_to_ital_wn_ids = {}
    ital_wn_id_counts = {}

    for best_match, matched_senses in results:
        mari_term_id = best_match.get('Mariterm ID')
        ital_wn_id = best_match.get('ItalWN ID')

        if mari_term_id not in mari_term_id_to_ital_wn_ids:
            mari_term_id_to_ital_wn_ids[mari_term_id] = [ital_wn_id]
        else:
            mari_term_id_to_ital_wn_ids[mari_term_id].append(ital_wn_id)

        if ital_wn_id in ital_wn_id_counts:
            ital_wn_id_counts[ital_wn_id] += 1
        else:
            ital_wn_id_counts[ital_wn_id] = 1

    unique_entries = []

    for best_match, matched_senses in results:
        mari_term_id = best_match.get('Mariterm ID')
        ital_wn_id = best_match.get('ItalWN ID')

        if len(mari_term_id_to_ital_wn_ids[mari_term_id]) == 1 and ital_wn_id_counts[ital_wn_id] == 1:
            gloss = best_match.get("Mariterm Gloss", 'No Gloss Available')
            if "[FALLBACK]" in gloss:
                gloss = ''  # Remove the gloss entirely if it contains "[FALLBACK]"

            entry = {
                "Literal Lemma": best_match.get("Literal Lemma", 'N/A'),
                "IWN ID": ital_wn_id,
                "Mariterm ID": mari_term_id,
                "Total S.": best_match.get("Total S.", 0.00),
                "Gloss S. (WM)": best_match.get("Gloss S. (WM)", 0.00),
                "T. Relation S.": best_match.get("T. Relation S.", 0.00),
                "Malus": best_match.get('malus', 0.00),
                "Bonus": best_match.get('bonus', 0.00),
                "Mariterm Gloss": gloss,
                "MariT sense": best_match.get("MariT sense", 'N/A'),
                "IWN sense": best_match.get("IWN sense", 'N/A'),
                "MariTerm Relations": best_match.get("MariTerm Relations", []),
                "ItalWN Relations": best_match.get("ItalWN Relations", []),
            }
            unique_entries.append(entry)

    print(f"Unique Entries: {len(unique_entries)} entries generated.")

    return unique_entries


def store_to_csv(formatted_results, breakdown_csv):
    # Entries with "[FALLBACK]" glosses have already had the gloss removed during the formatting step
    df = pd.DataFrame(formatted_results)

    if 'Gloss S. (WM)' in df.columns:
        df['Gloss S. (WM)'] = pd.to_numeric(df['Gloss S. (WM)'], errors='coerce')
    else:
        print("Warning: 'Gloss S. (WM)' column is missing!")

    df['Malus'] = pd.to_numeric(df['Malus'], errors='coerce')
    df['Bonus'] = pd.to_numeric(df['Bonus'], errors='coerce')

    required_columns = ['Literal Lemma', 'IWN ID', 'MariTerm ID', 'IWN sense', 'MariT sense', 'Gloss S. (WM)', 'Total S.', 'T. Relation S.', 'Malus', 'Bonus', 'MariTerm Gloss']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df.to_csv(breakdown_csv, sep=';', encoding='utf-8', index=False, float_format='%.2f')