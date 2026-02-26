"""
Lemma matching by first literal lemma and sense number from CSV entries.
"""


def match_lemmas(mari_term_wms, ital_wn_wms, csv_entries):
    matched_pairs = []
    for entry in csv_entries:
        csv_lemma = entry['literal_lemma'].lower()
        mari_t_sense = entry['mari_t_sense']
        iwn_sense = entry['iwn_sense']

        # Find the correct word meanings based on both the lemma and the sense numbers
        mari_match = next((wm for wm in mari_term_wms if wm["first_literal_lemma"].lower() == csv_lemma and wm["first_literal_sense"] == mari_t_sense), None)
        iwn_match = next((wm for wm in ital_wn_wms if wm["first_literal_lemma"].lower() == csv_lemma and wm["first_literal_sense"] == iwn_sense), None)

        if mari_match and iwn_match:
            matched_pairs.append((mari_match["original_element"], iwn_match["original_element"]))
        else:
            print(f"Skipped: Could not find matching sense for {csv_lemma} (MariTerm sense {mari_t_sense}, IWN sense {iwn_sense})")

    return matched_pairs